# PlaylistIQ estimator update — reader summary

**Implemented, with the reference still default.** Music2Emo can now supply direct mood/theme, valence and arousal estimates. A MusiCNN danceability alternative is independently selectable. MAEST genre matching and MuQ similarity are preserved.

Music2Emo was selected as the most practical supervised emotion challenger found in this investigation: official usable weights, relevant multi-dataset results and feasible CPU inference. It predicts the same 56 Jamendo tags as the current theme head, plus VA; this is a new estimator, not 56 newly added emotions. Published results justify testing it, not declaring it universally better. Newer graph/distributional alternatives lack a verified suitable local-file deployment path under this task's constraints.

Two authorized tracks passed six matched-window model stages, preserving audio hashes and the source inventory. Music2Emo took 11–16 seconds per track and peaked near 2.1 GiB process-tree RAM. All four profiles passed 40 frozen-query replays. The Python suite passed 481 tests; the web suite passed 80 tests, syntax and build. One live intimate-evening plan was rejected by the existing intent validator; it was preserved as a failure, not counted as a successful playlist. The final energetic/danceable live request succeeded with both challengers and passed exact replay.

**Accuracy is still unproven.** MusiCNN danceability scores both examples very highly and currently offers no persuasive reason to replace EffNet. More elaborate emotion estimates still cannot prove beach, picnic or intimate-evening suitability. Manuel and Grecia's earlier feedback remains intact; no new listening judgments were invented.

In Analysis, open a track's Details to inspect or compare its estimators. In PlaylistIQ, choose **Compared tracks only** to use the same two-track development set across profiles. Choose Reference, Music2Emo, MusiCNN danceability or Both challengers. With incomplete compatible coverage, everyone keeps the reference. The default all-library/reference path is unchanged.

Next: use the prepared independent, blinded listening sheets as a development exercise, then authorize a separate held-out evaluation set before making a quality claim or upgrading the library. Broader analysis has not been started.

[Full technical report](SUPERVISED_ESTIMATORS_2026-09-25.md) · [Commands, final acceptance and checkpoint](../SUPERVISED_ESTIMATORS.md) · [Reusable comparison evidence](../../output/supervised-estimators/comparison-v1/manifest.json)
