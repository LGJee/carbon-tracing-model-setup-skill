# Carbon Tracing Model Setup Skill

Prepare existing metabolic models for carbon tracing through concise questions,
readable COBRApy modifications, FBA/pFBA, and validated step-2 inputs.

Install this repository as `carbon-tracing-model-setup-skill` in your Codex skills
directory, then invoke `$carbon-tracing-model-setup-skill`. For example:

> Compare E. coli growth on glucose alone with simultaneous glucose and xylose
> supply. Use my carbon-tracing project and help clarify the missing conditions.

The skill creates a separate analysis script, workbooks, generated plan and a
short English report. It shares the installed
[carbon-tracing project](https://github.com/LGJee/atom-mapped-carbon-tracing)
environments and exporter; it does not replace the publication's step-1 script.
Inspect your installed project's interface: the latest local development version
may provide features not yet available in the public project release.

- [Skill instructions](SKILL.md)
- [Project interface and known limits](references/project-interface.md)
- [Readable glucose/xylose example](assets/step1_prepare_inputs.py)
- [Validation evidence](VALIDATION.md)

The example must be copied into an analysis folder inside a compatible project
before execution. Its uptake capacities are illustrative, not universal defaults.
Original models and third-party data are not bundled.

This skill stops after input preparation. It does not run FVA, sampling, dynamic
or community analysis, atom mapping, AI mapping review, or carbon propagation.
The separate `carbon-tracing-ai-review-skill` and
`enzymatic-atom-mapping-skill` handle reaction mapping review.
