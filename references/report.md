# Report outline

Write one short English `reports/preparation_report.md` for the analysis. Use compact tables or
paragraphs and observed values; omit irrelevant sections rather than leaving
unfilled placeholders.

- **Purpose and comparison:** question, conditions and the comparison basis.
- **Model provenance:** organism/strain, model source URL or user-supplied origin,
  version/commit when known, license status, original file and SHA256. Identify
  inherited medium settings and unavailable provenance explicitly.
- **Setup:** sources, uptake capacities and units, oxygen/medium, modifications
  with meaningful IDs, objective, growth/other constraints and assumptions.
- **Results:** FBA/pFBA method and reason, solver/version and status, biological
  objective, separately labelled total absolute flux, actual source uptake,
  unused declared sources, nonzero reaction count and validation outcome.
- **Handoff:** script, plan and workbooks, reproduction command and exact next
  step-2 command from the project root.
- **Limits:** one calculated representative, missing structures delegated to
  step 2, unsupported requests or unresolved provenance. Do not infer carbon
  propagation, isotope abundance or experimental confirmation from step 1.

For a failed run, state which condition failed and why, whether any files were
written, and that no successful batch plan is available. Do not invent numerical
results or silently relax culture conditions to produce a report.

Keep solver logs, research downloads, draft scripts and validation JSON under the
project's .cache/ai/setup/<run>/. Preserve the final runnable preparation script,
analysis plan and original model provenance outside cache so clearing temporary
work does not prevent reproduction.
