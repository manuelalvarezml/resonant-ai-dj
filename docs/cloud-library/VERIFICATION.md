# Research and artifact verification

As of 2026-09-08. Scope: local research documents, planning registers and the cost workbook.

## Actual checks

- The 45-source inventory and all current-state/event JSON parse successfully.
- Record IDs, gate/task dependencies, experiment references and relative document links are checked by validate.py; machine results are in verification.json.
- The cost workbook was recalculated using the bundled spreadsheet engine. All three cases update the same model. A changed storage driver changes the result; zero revenue gives an unavailable margin; an unselected blank does not affect the active case, while selecting that blank exposes unavailable input.
- Formula error scan returned zero matches after restoring the final inputs.
- Every workbook sheet was visually inspected through rendered ranges, including all common assumptions and rates. B2's five-decimal rate precision and retained WAV-master costs were corrected before delivery.
- Independent arithmetic and saved workbook formula/cached-value checks are recorded in verification.json.
- The preserved workbook builder is economics/build.mjs. It generates only documentation economics artifacts and requires the bundled @oai/artifact-tool runtime.
- No engine or playlist tests were rerun because no runtime/dependency/live-schema changes were made.

## Interpretation limits

These are document/workbook checks, not cloud acceptance tests. No provider performance, security penetration test, backup recovery, customer interview, legal opinion, actual cost invoice or new audio-quality evidence was collected. No native Excel application recalculation was performed; workbook calculations were verified in the bundled engine and saved-file structure.

No source audio was accessed, hashed, analyzed, rendered or uploaded. No cloud resources, accounts, hosted UI, provider purchases, customer/vendor messages, model calls or commits were created. Historical 54-engine/363-playlist test counts and source-preservation observations remain the earlier logs' evidence.

Research gaps include selected-region S3 pricing, dynamic Lexicon plan amounts, commercial license applicability and unmeasured customer/worker behavior. The gate register remains not_passed throughout.

## Repeating checks

Run validate.py with a Python 3 standard-library environment. It checks local documents/registers and the economics artifact without network or audio access. For workbook regeneration, copy economics/build.mjs into a temporary directory with access to the bundled node_modules, then pass the absolute cloud-library directory as its first argument. Use the spreadsheet skill's prescribed runtime and creation/edit marker workflow. Never install dependencies into the engine or playlist environment to rebuild this artifact.

Preserve accepted inputs/output revisions before publishing a new scenario. See MAINTENANCE.md.
