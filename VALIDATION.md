## EMU-only compatibility check (2026-10-24)

All five existing real-model preparation/handoff tests passed against the current
local EMU-only development project. The step-1 export schema and asset remain
unchanged. Official skill metadata validation passed. The following earlier
validation record describes its original checks, not new independent agent tests.
No full-network source analysis or fresh environment installation was performed.

# Validation

Validated on 2026-10-15 against the local Python development implementation of
atom-mapped-carbon-tracing on Linux/WSL x86_64. Its base commit was `af68a40` with
the newer, uncommitted Python preparation and analysis-plan interfaces. This
does not certify an older public project release. No shared project code was
changed for this skill.

## Executed checks

- The official skill-creator validator passed for the installed skill and the
  publication copy. Python syntax/unused-code lint and formatting checks passed.
- Five automated integration tests passed using actual iML1515, COBRApy 0.30.0,
  GLPK 5.0, Python 3.11.17, NumPy 1.26.4, pandas 2.2.3 and openpyxl 3.1.5.
- FBA and pFBA both generated glucose-only and simultaneous glucose/xylose input
  workbooks, valid version-3 plans and English reports. Input workbooks contained
  no SMILES columns and were accepted by the project's read-only plan loader.
- An explicitly requested `thrA` (`b0002`) knockout was executed and recorded.
- An unused declared xylose source was retained with zero actual uptake.
- An infeasible rerun invalidated its plan and old success report while keeping
  previously exported workbooks unchanged. A zero-objective request correctly
  failed the current exporter's positive-objective requirement.
- Hash checks confirmed the original model, publication step-1 script, default
  analysis plan and existing root-level result workbooks were unchanged.
- An independent read-only forward test handled a species-only glucose/xylose
  request by asking about strain, medium/oxygen, comparison basis and objective,
  without inventing uptake values, downloading data or starting calculations.
- An independent supplied-model forward test adapted the skill to baseline
  versus `thrA` knockout FBA, producing two workbooks, a plan and a concise
  case-specific report in isolation. Both solutions had biomass objective
  0.876997214426967, glucose import 10, 432 nonzero reactions and 438 metabolites.
  The knockout was nonfunctional, but alternative GPR genes retained the relevant
  reaction activities; equal predicted growth was reported rather than treated
  as a failed knockout. Workbook hashes, numerical checks and loader acceptance
  passed without SMILES or any downstream calculation.

The real example's observed biological objectives were approximately
0.876997214 for glucose alone and 0.871354700 for simultaneous glucose/xylose
supply. Actual uptake was 10 glucose, or 5 glucose plus 6 xylose, respectively,
in mmol/gDW/h. These are illustrative growth conditions, not measured culture
data or carbon-propagation results.

The test suite requires the project's existing preparation environment and
`data/Escherichia_coli/iML1515.json`; it downloads nothing. From this repository, run with
absolute paths and choose a new output folder inside the target project:

```bash
PROJECT=/path/to/atom-mapped-carbon-tracing
"$PROJECT/.envs/preparation/bin/python" tests/test_preparation.py \
  --project "$PROJECT" \
  --output "$PROJECT/.cache/ai/setup/model_setup_skill_test"
```

## Limits

No real mapper or carbon-propagation run was performed. Model downloading,
genome reconstruction, FVA, sampling, dynamic/community analysis, and platforms
outside the project's tested Linux/WSL environments are not validated here.
The current shared exporter still requires a positive biological objective and
uses legacy filenames containing pFBA. The skill documents these limits instead
of bypassing them. Other models and more complex introduced pathways require
case-specific checks.

The installed skill contains instructions, references, metadata and the runnable
asset. Repository-only integration tests and this validation record are not
runtime dependencies. Model files, environments, private results and credentials
are not included in the repository.
