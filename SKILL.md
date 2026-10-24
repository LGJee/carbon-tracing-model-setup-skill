---
name: carbon-tracing-model-setup-skill
description: >-
  Prepare existing metabolic models for carbon-source tracing: clarify culture
  conditions, find or load models, apply COBRApy modifications, run FBA or pFBA,
  and deliver validated step-2 workbooks, an analysis plan, and a concise report.
  Use for model setup and condition comparisons, not genome reconstruction or
  atom-mapping review.
---

# Carbon Tracing Model Setup

Turn a biological question into a readable, reproducible step-1 analysis for
[atom-mapped-carbon-tracing](https://github.com/LGJee/atom-mapped-carbon-tracing).
Deliver actual input workbooks and a generated plan, not just proposed code.
Use the user's language in conversation; write distributable files in English.

## Project context and responsibility

Atom-mapped-carbon-tracing connects a defined metabolic flux solution to reaction
atom correspondences and downstream carbon-source analysis. This skill prepares
the biological conditions and flux solution that determine which reactions and
directions enter that analysis. Its deliverables are step-2 input workbooks and
their analysis plan; preparing them does not establish carbon origins.

The publication's non-IUPD/IUPD comparison is one reference application. New
species, carbon mixtures, engineering strategies and objectives require their
own stated assumptions. A model with missing molecular structures can still
support flux calculation; downstream structure and mapping gaps must remain
visible rather than being treated as biological impossibility.

## Resolve the analysis

Inspect the supplied model and materials before asking questions. Establish the
organism/strain, comparisons, carbon sources and uptake limits, oxygen/medium,
requested modifications, objective, growth constraints, and FBA versus pFBA.
Ask only about missing conditions that change the calculation or interpretation;
bundle related questions and offer a justified proposal when useful. Do not
reconfirm explicit instructions or ask users to manage JSON or internal modules.
Do not inherit the publication's IUPD engineering or squalene settings as defaults.

Prefer a supplied model and preserve it. Otherwise find a suitable model through
BiGG or an official model repository; justify strain/purpose compatibility rather
than selecting solely by recency. Verify the source and record version/commit,
license, download source and SHA256. Keep its companion annotations together in
`data/<model>/`; do not invent missing identifiers or licensing information.
Read [modeling decisions](references/modeling.md) when selecting models,
interpreting uptake or planning modifications.

Support static single-source and simultaneous mixed-source FBA/pFBA analyses.
Choose FBA for a requested objective solution, or pFBA when a parsimonious
representative is appropriate; explain the choice. Do not run FVA, sampling,
dynamic cultivation or community analyses in this version. For other requests,
describe the required extension without claiming it is implemented.

## Disposable AI work and final files

Use `<project>/.cache/ai/<stage>/<run>/` for disposable AI process files:
research downloads, extracted inputs, proposals, staging workbooks, retry reports,
logs, validation output and continuation JSON. Stages may be workflow, setup,
review, structures or enzymatic-mapping. Reuse the orchestrator's supplied run
folder when available. Do not put these process files in the results root.

Keep final workbooks in the selected case output directory and readable final
reports under its `Ai_reports/` subfolder. Preserve reproducible preparation scripts
and analysis plans with the case. Downloaded models, adopted AI/manual chemistry
CSVs and immutable evidence supporting adopted records remain in `data/`; they
are not disposable cache. Do not move the only copy of a prior final delivery or
its scientific evidence into cache. A brief same-filesystem temporary file for
atomic final publication is allowed and must be cleaned up.

Users can remove `.cache/ai/` after its runs have stopped. This loses temporary
progress and downloaded research pages, not formal results or adopted evidence.
Do not automatically delete active runs, clear shared scientific tables, relocate
old case files or change the computation project's own caches as a side effect.
For standalone use without a project, use `.cache/ai/` under the chosen work folder.

## Prepare and execute

Locate the user's actual project and inspect its interface before generating
code. Prefer their selected local checkout over a public copy; never replace it
with an older download. If it is missing, help locate or obtain it. Read the
project's `docs/interfaces.md`, exporter, example and step-2 input checks, then
read [the handoff contract](references/project-interface.md).

Keep the publication-reference step-1 script and existing results unchanged.
Create a separate `results/results_by_AI/<analysis-name>/` directory, sharing installed
environments and raw model data. For a new request choose an unused directory;
for an authorized rerun use the existing analysis directory. Put its script,
plan and input workbooks directly there, final reports under Ai_reports/, and
disposable process files under .cache/ai/setup/. Do not add a results subfolder.
Shared original models and adopted scientific records remain under data/.

Adapt [the readable example](assets/step1_prepare_inputs.py), or the installed
project's compatible example. This asset is a runnable glucose/xylose example,
not universal biological defaults. Copy it into the analysis directory and edit
its explicit model blocks. Each condition should visibly load its own model,
declare sources, set medium/modifications and constraints, choose its objective,
calculate its solution, and register export. Use direct COBRApy operations and
short comments explaining reaction/gene IDs. Avoid hiding biological settings in
generic configuration engines or a proliferation of helper functions.

Use the project's preparation interpreter and shared export/plan helpers. Do not
duplicate the exporter or refactor the shared project as part of a case. Missing
SMILES belongs to step 2, not a new lookup implementation here.

Run the script. Validate solver status, finite fluxes, steady state, bounds,
source identity and output schema. Export one concrete, jointly feasible solution
per condition; never splice reactions from different solutions. Record actual
source uptake and warn when permitted sources are unused. Uptake capacities do
not force co-utilization. Do not silently change an infeasible model's biology.

Check the real exporter limits. Some versions require a positive biological
objective and retain `pFBA` in filenames even for FBA. Report an unsupported valid
request rather than fabricating fluxes/objectives, replacing solver status,
monkey-patching checks or claiming a new interface is available.

## Deliver

Produce the analysis script, per-condition input workbooks, generated analysis
plan and a short English `Ai_reports/preparation_report.md`. Follow
[the report outline](references/report.md), replacing example descriptions with
verified case-specific findings. Record the method explicitly: a legacy filename
does not identify the method.

Verify the plan and input hashes with the installed project's loader, without
calling mappers. Provide the exact next command from the project root, e.g.:

```bash
python3 step2_atom_mapping.py --plan results/results_by_AI/my_analysis/analysis_plan.json
```

Stop after step 1 unless the user separately requests later stages. Atom mapping,
AI review and EMU carbon-source analysis belong to the separate project orchestrator;
this skill does not call the existing mapping-review skills by default.

On failure, report the actual blocker and which artifacts, if any, are valid.
Do not present stale outputs as new successes. A calculated representative is
not all feasible pathways, an isotope measurement or a carbon-propagation result.

The current downstream step3 is EMU-only. Preparation does not configure rounds
or enumeration and does not claim source fractions have been calculated. Keep
this skill's standard step-2 inputs unchanged; inspect the selected project's
interface when another checkout exposes a different analysis version.
