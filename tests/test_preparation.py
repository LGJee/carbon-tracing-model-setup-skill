"""Run isolated real FBA/pFBA handoff tests against a compatible local project."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest

import pandas as pd

ASSET = Path(__file__).resolve().parents[1] / "assets/step1_prepare_inputs.py"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class PreparationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(cls.project))
        from carbon_flow_tools.cli import load_analysis_plan

        cls.load_plan = staticmethod(load_analysis_plan)
        cls.model = cls.project / "data/Escherichia_coli/iML1515.json"
        if not cls.model.is_file():
            raise unittest.SkipTest("The real iML1515 JSON model is required.")
        files = [cls.project / "step1_prepare_carbon_tracing_inputs.py", cls.model]
        plan = cls.project / "data/analysis_plan.json"
        if plan.exists():
            files.append(plan)
        files.extend((cls.project / "results").glob("*.xlsx"))
        cls.original = {path: sha256(path) for path in files}

    @classmethod
    def tearDownClass(cls):
        changed = [
            str(path) for path, digest in cls.original.items() if sha256(path) != digest
        ]
        if changed:
            raise AssertionError("Original project artifacts changed: " + str(changed))

    def run_case(self, name, method, transform=None):
        directory = self.output / name
        directory.mkdir(parents=True, exist_ok=True)
        script = directory / "step1_prepare_inputs.py"
        text = ASSET.read_text(encoding="utf-8").replace(
            'ANALYSIS_METHOD = "pFBA"', 'ANALYSIS_METHOD = "{}"'.format(method)
        )
        script.write_text(transform(text) if transform else text, encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(script)],
            cwd=self.project,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        (directory / "execution.log").write_text(result.stdout, encoding="utf-8")
        return directory, result

    def valid_case(self, name, method, transform=None):
        directory, result = self.run_case(name, method, transform)
        self.assertEqual(result.returncode, 0, result.stdout)
        plan = directory / "analysis_plan.json"
        data = json.loads(plan.read_text())
        _, jobs = self.load_plan(plan, "map", {})
        self.assertEqual(len(jobs), 2)
        self.assertGreater((directory / "Ai_reports" / "preparation_report.md").stat().st_size, 0)
        for name, entry in data["models"].items():
            workbook = self.project / entry["input_file"]
            self.assertEqual(sha256(workbook), entry["input_sha256"])
            self.assertEqual(entry["preparation"]["analysis_method"], method)
            self.assertEqual(
                entry["preparation_script"]["sha256"],
                sha256(directory / "step1_prepare_inputs.py"),
            )
            reactions = pd.read_excel(workbook, sheet_name="Nonzero")
            metabolites = pd.read_excel(workbook, sheet_name="Metabolites")
            self.assertTrue(
                {"ReactionID", "ReactionName", "Flux", "Equation"}
                <= set(reactions.columns)
            )
            self.assertTrue(
                {"MetaboliteID", "MetaboliteName"} <= set(metabolites.columns)
            )
            self.assertFalse(
                any("smiles" in column.lower() for column in metabolites.columns)
            )
            self.assertTrue(
                set(entry["carbon_sources"]) <= set(metabolites.MetaboliteName)
            )
            self.assertTrue(reactions.Flux.ne(0).all())
            self.assertEqual(entry["source_model"]["sha256"], self.original[self.model])
        return directory, data

    def test_fba_and_pfba_real_mixed_sources_without_smiles(self):
        for method in ("FBA", "pFBA"):
            _, data = self.valid_case(method.lower(), method)
            single = data["models"]["Escherichia_coli_glucose"]["preparation"]
            mixed = data["models"]["Escherichia_coli_glucose_xylose"]["preparation"]
            self.assertAlmostEqual(
                single["source_uptake"]["D-glucose[e]"]["net_import"], 10, places=6
            )
            self.assertAlmostEqual(
                mixed["source_uptake"]["D-glucose[e]"]["net_import"], 5, places=6
            )
            self.assertAlmostEqual(
                mixed["source_uptake"]["D-Xylose[e]"]["net_import"], 6, places=6
            )
            self.assertAlmostEqual(single["objective_value"], 0.876997214, places=6)
            self.assertAlmostEqual(mixed["objective_value"], 0.871354700, places=6)

    def test_user_supplied_model_and_explicit_knockout(self):
        def modify(text):
            text = text.replace(
                "labels = metabolite_labels(model)",
                'model.genes.get_by_id("b0002").knock_out()  # thrA knockout.\n'
                "    labels = metabolite_labels(model)",
            )
            return text.replace(
                "No gene or pathway engineering is applied.",
                "The specified thrA gene knockout is applied.",
            )

        _, data = self.valid_case("supplied_model_knockout", "FBA", modify)
        for entry in data["models"].values():
            self.assertIn("b0002", entry["preparation"]["knocked_out_genes"])

    def test_unused_declared_source_is_retained(self):
        def modify(text):
            return text.replace(
                'get_by_id("EX_xyl__D_e").lower_bound = -6',
                'get_by_id("EX_xyl__D_e").lower_bound = 0',
            )

        _, data = self.valid_case("unused_source", "pFBA", modify)
        mixed = data["models"]["Escherichia_coli_glucose_xylose"]
        self.assertEqual(
            mixed["preparation"]["source_uptake"]["D-Xylose[e]"]["net_import"], 0
        )
        self.assertIn("D-Xylose[e]", mixed["carbon_sources"])

    def test_infeasible_rerun_invalidates_plan_and_report(self):
        directory, data = self.valid_case("failed_rerun", "FBA")
        originals = {
            self.project / entry["input_file"]: entry["input_sha256"]
            for entry in data["models"].values()
        }

        def modify(text):
            return text.replace(
                'model.objective_direction = "max"',
                'model.objective_direction = "max"\n'
                '    model.reactions.get_by_id("BIOMASS_Ec_iML1515_core_75p37M").bounds = (1000, 1000)',
            )

        _, result = self.run_case("failed_rerun", "FBA", modify)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((directory / "analysis_plan.json").exists())
        self.assertFalse((directory / "Ai_reports" / "preparation_report.md").exists())
        self.assertTrue(
            all(sha256(path) == digest for path, digest in originals.items())
        )

    def test_zero_objective_reports_current_interface_limit(self):
        def modify(text):
            return text.replace(
                'model.objective = "BIOMASS_Ec_iML1515_core_75p37M"',
                "model.objective = {}",
            )

        directory, result = self.run_case("zero_objective", "FBA", modify)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("biological objective must have positive flux", result.stdout)
        self.assertFalse((directory / "analysis_plan.json").exists())
        self.assertFalse((directory / "Ai_reports" / "preparation_report.md").exists())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="Isolated validation folder inside the project",
    )
    args = parser.parse_args()
    PreparationTests.project = args.project.resolve()
    PreparationTests.output = args.output.resolve()
    PreparationTests.output.relative_to(PreparationTests.project)
    if PreparationTests.output.exists():
        raise SystemExit(
            "Choose a new validation output directory; do not overwrite earlier tests."
        )
    PreparationTests.output.mkdir(parents=True)
    unittest.main(argv=[sys.argv[0]], verbosity=2)
