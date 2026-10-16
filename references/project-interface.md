# Step-1 to step-2 handoff

Use the installed project's documentation and functions as the authority. The
interface below was tested against the Python development implementation; an
older public checkout may not provide it. Do not claim compatibility without
inspecting or testing that checkout.

## Shared implementation

Read `carbon_flow_tools/model_preparation.py`, especially:

```python
read_model(path, solver="glpk", variable_name=None)
metabolite_labels(model)
export_model(model, solution, name, sources, project,
             output_dir="results", tolerance=1e-8)
invalidate_plan(project, plan_file="data/analysis_plan.json")
save_plan(project, models, output_dir,
          plan_file="data/analysis_plan.json", script_file=None)
```

Use `read_model` to retain source provenance and later structure discovery.
Derive exact compartment-qualified source names with `metabolite_labels`.
Use a letter followed by letters, digits or underscores for each analysis name.
Model paths can point to shared `data/<model>/` files. Generated plans and outputs
stay inside the project. Paths inside plans are project-root-relative, not
relative to the plan folder or terminal working directory.

The asset discovers its project through an ancestor containing the shared
exporter. Place it at `results/results_by_AI/<analysis-name>/step1_prepare_inputs.py` before
running it. Use the existing `.envs/preparation/bin/python`; do not create an
environment per analysis. If the user installed environments elsewhere, adapt
that path to their actual project. Leave shared scripts untouched.

## Workbooks

Each model gets one workbook with `Nonzero` and `Metabolites` sheets. Current
exporters use `<model>_1_pFBA_nonzero_reactions.xlsx`, including when given an FBA
solution. Preserve the actual filename returned by the exporter; do not infer
the method from it.

| Sheet | Required columns |
|---|---|
| Nonzero | ReactionID, ReactionName, Flux, Equation |
| Metabolites | MetaboliteID, MetaboliteName |

Fluxes must be finite and nonzero for included reactions. Equation sides and
signed flux jointly determine direction. Metabolite names include compartments
and match the equation/source names exactly. Preserve formulas, charges and
identifiers supplied by the exporter. Missing SMILES is valid here; step 2
enriches structures without changing these inputs.

Some coefficients may not be supported by the mapper stage, such as fractional
stoichiometry; retain the correct chemistry and report the existing unmappable
status rather than rounding coefficients to manufacture support.

## Plan and validation

The tested plan has exactly three top-level fields:

```json
{"version": 3, "models": {}, "output_dir": "results/results_by_AI/my_analysis"}
```

Let `save_plan` populate it. Each model records input_file, input_sha256 and
ordered carbon_sources, with optional source_model, preparation_script and
preparation metadata. Add method-specific metadata under the model entry,
not as a new top-level field. Record `preparation.analysis_method` explicitly.

Invalidate only this analysis's old plan before recalculating; save a valid plan
only after every intended export succeeds. Do not treat existing workbooks as
new outputs after failed preparation. Use the installed loader for a read-only
handoff check, not the step-2 command itself:

```python
from carbon_flow_tools.cli import load_analysis_plan
load_analysis_plan(plan_path, "map", {})
```

Also verify input file hashes and workbook headers. The loader validates plan
structure, not every numerical or workbook property.

The tested exporter checks optimal status, finite fluxes, steady-state residuals,
bounds and a positive current biological objective. Consequently some legitimate
zero/negative-objective or minimization requests may be blocked. Report that
limitation rather than editing the shared checks or pretending it is solved.

## Deliverable and next stage

```text
results/results_by_AI/my_analysis/
    step1_prepare_inputs.py
    analysis_plan.json
    report.md
    <model>_1_pFBA_nonzero_reactions.xlsx
```

From the project root, the next command is:

```bash
python3 step2_atom_mapping.py --plan results/results_by_AI/my_analysis/analysis_plan.json
```

Step 2 and later stages are a separate task. No mapper, AI-review or propagation
call is required to validate this handoff. See the project's own interfaces for
optional reviewed copies and later stage behavior.
