# Next work: quality-first feature estimators for PlaylistIQ

Recorded from Manuel's voice instructions on 2026-09-25.
Status: activated by “go now”; research reports delivered and the available specialist selection implemented and validated locally. See [research](research/TOP_ESTIMATORS_2026-09-25.md), [reader report](research/TOP_ESTIMATORS_DIGEST_2026-09-25.md) and [implementation checkpoint](TOP_ESTIMATORS_IMPLEMENTATION.md).

## Purpose and priority

Manuel finds the present feature estimates insufficient for PlaylistIQ. He considers the current prompt interpretation and planning approach acceptable for now; better musical evidence is the priority. This is owner feedback, not a measured diagnosis of every model.

Produce a defensible shortlist of the strongest available estimators for each feature, not an exhaustive model inventory. Estimation quality, credible performance evidence and musical usefulness carry the greatest weight. Start from the strongest candidates rather than the easiest models to install. Existing Music2Emo and MusiCNN experiments are comparison infrastructure, not predetermined winners or proof that this objective is complete.

Local operation on Manuel's Mac is the present implementation target, but CPU speed, Apple compatibility and convenience are secondary considerations. Do not remove a leading model from the research shortlist simply because it is costly or difficult to run locally. Separate the quality ranking from implementation feasibility. Licensing has zero weight in this proof-of-concept selection; do not spend this task on licensing research or commercial-readiness screening.

## Task 1: research and two reports

Inventory the actual feature pipeline, catalog and scoring inputs first. Cover every directly estimated non-genre feature, including mood/emotion and musical character, valence, arousal, energy/intensity, danceability/rhythmic movement, vocal presence and instruments. Include tempo/beats/downbeats, key/harmony and loudness or other existing direct descriptors discovered in the audit. For signal measurements such as loudness, identify the appropriate measurement method instead of inventing a need for a learned model. Mark any retained estimator with a substantive comparison-based reason.

Preserve MAEST genre estimation and its top-six matching policy. The owner's satisfaction with MAEST explains this exclusion; it is not a universal state-of-the-art claim. Preserve the current MuQ retrieval branch and planner approach; supervised estimator research must not turn into a retrieval or planner redesign.

For each feature, identify the leading serious candidates using current papers, official benchmark results, implementations and released weights. Establish their exact prediction targets, meaningful label vocabulary, scales, temporal resolution, training/evaluation data, matched metrics, generalization evidence and limitations. Distinguish perceived versus induced emotion and emotional labels versus contextual themes. More labels alone do not prove better recognition; unchanged vocabulary does not rule out more accurate estimates.

Rank where the evidence supports ranking. Where datasets or targets differ, explicitly state which comparisons are inconclusive instead of constructing a false universal leaderboard. Identify richer emotion models and strong quality contenders beyond the current 56 Jamendo tags. Explain why each recommended specialist or combination is preferable to the current baseline. Distinguish published performance, engineering judgment, local measurements and human judgments.

Deliver two versions of the research:

1. An implementation-ready technical report for a future Codex agent: source-linked evidence tables, recommendations per feature, exact model/checkpoint identities, target and preprocessing contracts, inference availability, dependencies, integration plan, validation plan and unresolved questions.
2. A concise reader report for Manuel: the strongest candidates, selected choices and reasons, expected practical improvements, meaningful new outputs and remaining uncertainty.

The reports must precede implementation decisions. They are not an extra approval gate: the user has requested both research and subsequent implementation.

## Task 2: implement the highest-ranked available choices

Starting from the quality-ranked shortlist, implement the highest-ranked model with usable weights and a workable inference path for each feature, or a justified specialist combination. “First available” means first in the evidence-based ranking, not the first search result or easiest installation. Attempt reasonable local adaptation before falling back for engineering convenience. If the strongest candidate cannot actually run on the current machine, preserve its research ranking, explain the concrete blocker and identify the strongest viable local option separately. Do not silently redefine the best model as the cheapest model.

Complete the local path: reproducible acquisition, inference, bounded workers, caching/retries, continuous outputs and sampling provenance, typed descriptors, catalog and capability projection, auditable preference mappings and ranking contributions, app display and upgrade/migration behavior, source/playlist preservation, tests, real-model checks and maintained documentation. Preserve existing weights and hard constraints unless a directly necessary, explained integration change requires otherwise.

Keep engineering validation separate from musical-quality evidence. Use matched settings and held-out judgments where available; no fabricated listening results, calibration or superiority claims. Retain reversible baselines when local superiority remains uncertain. Report actual end-to-end coverage and quality gaps.

## Carry-forward boundaries and completion

This instruction records the next two work phases; it does not start separate Codex tasks or a scheduled run. New research and implementation remain pending. Existing audio/corpus boundaries carry forward: agent-run checks on one or two already authorized tracks, no implied whole-library reanalysis or new corpus. A stronger research ranking does not authorize cloud execution, remote audio uploads, spending, new accounts or commits. Resource limits are real execution constraints, not a reason to hide stronger candidates from the report.

Completion requires the two research reports plus fully integrated selected estimators and honest validation evidence. A working alternative alone is not completion of the quality-first selection objective. Existing September 22 and 25 reports remain historical evidence and starting references, not final answers to this revised brief.
