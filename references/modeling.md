# Model and analysis decisions

## Establish conditions, not software trivia

If the user supplies a model and explicit changes, inspect and implement those
changes. For an underspecified comparison, ask together about medium/oxygen,
source limits, objective and growth constraints. Explain any proposed conditions
and obtain agreement before treating them as experimental assumptions. Existing
model defaults can be retained when appropriate, but identify them as inherited.

Use model annotations and upstream documentation to identify exchange, biomass,
gene and product IDs. Check GPR rules when evaluating a knockout: deleting one
gene need not block all associated reactions. Adding a pathway requires explicit
metabolites, compartments, stoichiometry, bounds and any intended GPRs. Check
available formula/charge balance and document incomplete annotations; do not
invent cofactors or add a biochemical route merely to make growth feasible.

Each comparison must state its basis: identical source capacities, equivalent
allowed carbon input, fixed growth, measured uptake, or another user-defined
basis. These are different questions. Opening two sources does not force both
to be consumed. Read actual exchange fluxes with their stoichiometric sign;
negative reaction flux is not a universal uptake convention for every model.

## Select and preserve models

Use the supplied model, or search [BiGG](https://bigg.ucsd.edu/) and official
model repositories for the requested organism/strain. Compare coverage of the
requested substrates, product and modifications, provenance, documented model
quality and annotations. A classic model may suit the task better than a newer
one. If strain differences matter, put that decision to the user rather than
silently substituting organisms.

Record source URL, version/commit when available, license and SHA256. A missing
license is unknown, not evidence of permission to redistribute. Downloaded model
files remain external data; do not bundle them into this skill. The project's
same-folder `source.json` is suitable for a source record when supported.

COBRApy can read supported MAT, JSON, SBML and YAML model files. MAT here is a
data format, not a MATLAB runtime requirement. Do not assume every arbitrary
YAML file uses COBRApy's format. Preserve companion model annotations for step-2
structure discovery. SMILES are not required for step-1 export.

## Use the requested scientific objective

FBA returns an objective solution; pFBA first retains an objective optimum and
then minimizes total absolute flux. For pFBA report the biological objective
separately from its minimized flux sum. Equivalent optima and solver differences
can change the selected active reactions. Explain which representative was used.

Do not replace a user's objective with biomass or impose half-maximal growth
unless that choice is requested or scientifically agreed. Do not convert the
publication's engineered strains into universal model-setup defaults.

This version uses static single-source or simultaneous mixed-source conditions.
Source-label order is computational, not physical feeding time. FVA, sampling,
dynamic feeding and community simulations are outside the implemented scope.

Consult official documentation for the installed COBRApy version when needed:

- [Model building](https://cobrapy.readthedocs.io/en/latest/building_model.html)
- [FBA and pFBA](https://cobrapy.readthedocs.io/en/latest/simulating.html)
- [Growth media](https://cobrapy.readthedocs.io/en/latest/media.html)

Inspect the installed API when documentation describes a newer release.
