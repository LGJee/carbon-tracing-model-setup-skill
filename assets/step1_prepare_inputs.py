"""Copy into results/results_by_AI/<name>/ and adapt the explicit COBRApy model blocks."""

from pathlib import Path
import hashlib
import importlib.util
import json
import os
import sys

CASE_DIR = Path(__file__).resolve().parent
ROOT = next(
    (
        parent
        for parent in CASE_DIR.parents
        if (parent / "carbon_flow_tools/model_preparation.py").is_file()
    ),
    None,
)
if ROOT is None:
    raise SystemExit(
        "Place this script inside the carbon-tracing project, under results/results_by_AI/<name>/."
    )
sys.path.insert(0, str(ROOT))

# Shared execution settings; biological settings stay with their model blocks.
ANALYSIS_METHOD = "pFBA"  # "FBA" or "pFBA".
SOLVER = "glpk"
NONZERO_TOLERANCE = 1e-8
PREPARATION_PYTHON = ".envs/preparation/bin/python"
PURPOSE = "Compare growth with glucose alone and simultaneous glucose/xylose supply."


def prepare_models():
    from cobra.flux_analysis import pfba
    from carbon_flow_tools.model_preparation import (
        close_other_carbon_uptake,
        metabolite_labels,
        read_model,
    )

    models = {}

    # 1. E. coli, glucose only. Capacities below are illustrative, not measured.
    model_file = ROOT / "data/Escherichia_coli/iML1515.json"
    model = read_model(model_file, SOLVER)
    labels = metabolite_labels(model)
    carbon_sources = [labels["glc__D_e"]]  # Extracellular D-glucose.
    close_other_carbon_uptake(model, "EX_glc__D_e")
    model.reactions.get_by_id("EX_glc__D_e").lower_bound = -10  # Glucose exchange.
    # Inherit oxygen and other inorganic nutrient bounds from the supplied model.
    model.objective = "BIOMASS_Ec_iML1515_core_75p37M"  # Core biomass synthesis.
    model.objective_direction = "max"
    if ANALYSIS_METHOD == "FBA":
        solution = model.optimize()
    else:
        solution = pfba(model, fraction_of_optimum=1.0)
    models["Escherichia_coli_glucose"] = (model, solution, carbon_sources)

    # 2. E. coli, simultaneous supply. Reload so conditions remain independent.
    model_file = ROOT / "data/Escherichia_coli/iML1515.json"
    model = read_model(model_file, SOLVER)
    labels = metabolite_labels(model)
    carbon_sources = [labels["glc__D_e"], labels["xyl__D_e"]]
    close_other_carbon_uptake(model, ["EX_glc__D_e", "EX_xyl__D_e"])
    # Equal allowed carbon input: 5*6 + 6*5 = 10*6 mmol carbon/gDW/h.
    model.reactions.get_by_id("EX_glc__D_e").lower_bound = -5  # Glucose exchange.
    model.reactions.get_by_id("EX_xyl__D_e").lower_bound = -6  # D-xylose exchange.
    model.objective = "BIOMASS_Ec_iML1515_core_75p37M"  # Core biomass synthesis.
    model.objective_direction = "max"
    if ANALYSIS_METHOD == "FBA":
        solution = model.optimize()
    else:
        solution = pfba(model, fraction_of_optimum=1.0)
    models["Escherichia_coli_glucose_xylose"] = (model, solution, carbon_sources)
    return models


def write_report(entries, models, plan):
    """Summarize measured outputs of this run, not a future carbon-flow result."""
    import cobra

    lines = [
        "# Model preparation report",
        "",
        PURPOSE,
        "",
        "Runtime: Python {}; COBRApy {}.".format(
            sys.version.split()[0], cobra.__version__
        ),
        "",
        "## Setup",
        "",
        "This example maximizes growth with illustrative uptake capacities. "
        "Other carbon uptake is closed; oxygen and inorganic nutrient bounds "
        "are inherited. No gene or pathway engineering is applied. "
        "Both sources are supplied simultaneously; consumption is not forced.",
        "",
        "Method: {}. FBA selects an objective solution; pFBA additionally "
        "minimizes total absolute flux. The biological objective is reported "
        "separately below. These uptake flux units are mmol/gDW/h for iML1515.".format(
            ANALYSIS_METHOD
        ),
        "",
    ]
    for name, entry in entries.items():
        model, solution, _ = models[name]
        info = entry["preparation"]
        source = entry.get("source_model", {})
        record_path = source.get("source_record", {}).get("path")
        record = (
            json.loads((ROOT / record_path).read_text(encoding="utf-8"))
            if record_path
            else {}
        )
        lines.extend(
            [
                "## " + name,
                "",
                "- Solver status: " + solution.status,
                "- Solver: " + info["solver"],
                "- Source model: `{}`; SHA256: `{}`.".format(
                    source.get("path", "unknown"), source.get("sha256", "unknown")
                ),
                "- Source URL: {}.".format(
                    record.get("source", "User-supplied; URL not recorded")
                ),
                "- Model ID: {}. Version/commit: {}. License: {}.".format(
                    model.id,
                    record.get(
                        "version",
                        record.get(
                            "commit", model.annotation.get("source_version", "unknown")
                        ),
                    ),
                    record.get(
                        "license",
                        "unknown; inspect upstream terms before redistribution",
                    ),
                ),
                "- Source record: `{}`.".format(
                    source.get("source_record", {}).get("path", "not recorded")
                ),
                "- Biological objective: `{}` ({}); value: {:.9g}.".format(
                    info["objective_reactions"],
                    info["objective_direction"],
                    info["objective_value"],
                ),
                "- Total absolute flux: {:.9g}.".format(info["total_absolute_flux"]),
                "- Nonzero reactions: {}.".format(
                    int((solution.fluxes.abs() > NONZERO_TOLERANCE).sum())
                ),
                "- Knocked-out genes: {}. Added reactions: {}.".format(
                    info["knocked_out_genes"], info.get("added_reactions", [])
                ),
                "- Workbook: `{}`.".format(entry["input_file"]),
                "",
                "| Carbon source | Exchange | Bounds | Actual net import |",
                "|---|---|---|---|",
            ]
        )
        for source_name, uptake in info["source_uptake"].items():
            for reaction, flux in uptake["exchange_imports"].items():
                exchange = info["exchange_conditions"][reaction]
                lines.append(
                    "| {} | {} | [{:g}, {:g}] | {:g} |".format(
                        source_name,
                        reaction,
                        exchange["lower_bound"],
                        exchange["upper_bound"],
                        flux,
                    )
                )
            if (
                uptake["net_import"] is not None
                and uptake["net_import"] <= NONZERO_TOLERANCE
            ):
                lines.append(
                    "\nDeclared source `{}` has no net uptake.".format(source_name)
                )
        oxygen = model.reactions.get_by_id(
            "EX_o2_e"
        )  # Oxygen exchange in this example model.
        lines.extend(
            ["", "Oxygen exchange bounds: [{:g}, {:g}].".format(*oxygen.bounds), ""]
        )
    relative_script = Path(__file__).resolve().relative_to(ROOT).as_posix()
    relative_plan = plan.relative_to(ROOT).as_posix()
    lines.extend(
        [
            "## Validation and handoff",
            "",
            "Exporter checks passed for optimal status, finite fluxes, steady state "
            "and bounds. Input hashes, workbook headers and the plan loader were checked.",
            "",
            "From the project root:",
            "",
            "```bash",
            "python3 " + relative_script,
            "python3 step2_atom_mapping.py --plan " + relative_plan,
            "```",
            "",
            "These are selected computational solutions, not all feasible pathways "
            "or experimental measurements. Missing SMILES is left to step 2. "
            "No atom mapping or carbon propagation was run. "
            "Legacy workbook names containing pFBA do not determine the analysis method.",
            "",
        ]
    )
    report_dir = CASE_DIR / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / "preparation_report.md").write_text("\n".join(lines), encoding="utf-8")


def main():
    if ANALYSIS_METHOD not in ("FBA", "pFBA"):
        raise ValueError("ANALYSIS_METHOD must be FBA or pFBA.")
    python = ROOT / PREPARATION_PYTHON
    if python.is_file() and python.resolve() != Path(sys.executable).resolve():
        os.execv(
            str(python), [str(python), str(Path(__file__).resolve())] + sys.argv[1:]
        )
    if importlib.util.find_spec("cobra") is None:
        raise SystemExit(
            "COBRApy is unavailable. Use the project's preparation environment."
        )
    import pandas as pd
    from carbon_flow_tools.cli import load_analysis_plan
    from carbon_flow_tools.model_preparation import (
        export_model,
        invalidate_plan,
        save_plan,
    )

    target = invalidate_plan(ROOT, CASE_DIR / "analysis_plan.json")
    # An old report must not survive a failed rerun as an apparent new success.
    report = CASE_DIR / "reports" / "preparation_report.md"
    if report.exists():
        report.unlink()
    models = prepare_models()
    entries = {}
    output_dir = CASE_DIR.relative_to(ROOT).as_posix()
    for name, (model, solution, sources) in models.items():
        entry = export_model(
            model, solution, name, sources, ROOT, output_dir, NONZERO_TOLERANCE
        )
        entry["preparation"]["analysis_method"] = ANALYSIS_METHOD
        with pd.ExcelFile(ROOT / entry["input_file"], engine="openpyxl") as excel:
            if not {"ReactionID", "ReactionName", "Flux", "Equation"} <= set(
                pd.read_excel(excel, "Nonzero").columns
            ):
                raise ValueError(
                    "Exported reaction headers are incompatible with step 2."
                )
            if not {"MetaboliteID", "MetaboliteName"} <= set(
                pd.read_excel(excel, "Metabolites").columns
            ):
                raise ValueError(
                    "Exported metabolite headers are incompatible with step 2."
                )
        if (
            hashlib.sha256((ROOT / entry["input_file"]).read_bytes()).hexdigest()
            != entry["input_sha256"]
        ):
            raise ValueError("Exported input hash changed: " + name)
        entries[name] = entry
    save_plan(ROOT, entries, output_dir, target, script_file=__file__)
    try:
        load_analysis_plan(target, "map", {})
        write_report(entries, models, target)
    except Exception:
        invalidate_plan(ROOT, target)
        raise
    print("Report saved: " + str(report))
    print(
        "Next: python3 step2_atom_mapping.py --plan "
        + target.relative_to(ROOT).as_posix()
    )


if __name__ == "__main__":
    main()
