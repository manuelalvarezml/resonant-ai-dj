# Supervised estimator implementation checkpoint

Started 2026-09-25. This task revisits direct feature estimation; it preserves MAEST/top-six and MuQ embeddings, inspection bank and prompt similarity. The 2026-09-22 report remains historical evidence.

## Predeclared comparison (before new inference)

- Production reference: existing EffNet mood/theme, four binary mood heads, danceability/voice, MusiCNN-DEAM arousal/valence. No blend or priority weight tuning.
- Primary challenger: official Music2Emo MERT-95M + BTC chord/key + multitask head. Retain continuous 56-label output and both regression coordinates. Audit the released checkpoint/training targets before selecting a regression head. No cosine substitution.
- Danceability challenger: official MusiCNN danceability head, same 306-track binary training task as EffNet. Its published normalized accuracy (0.95 versus 0.97) does not support automatic promotion. Test runtime and output disagreement, not accuracy, on our two sources.
- Sources only: Listen Over the Ocean (`b23cf7fc573254db349ab179fdcc406c5da159186b04b1fe914ff913d83e4ae2`) and My Paradise - Edit (`c4fa9722112e74661c9a4da26fa386d9a65564da8a3cef25048df25168f31bae`). Existing broader outputs may be audited read-only.
- Sampling: at most three non-overlapping 30-second excerpts distributed across each source; shorter tracks use their available duration. Compare baseline and challengers on identical excerpt audio. Preserve times, per-window outputs, means, ranges, sampled seconds and coverage. Also show historical full-track baseline separately; never call it a matched-window comparison.
- Runtime gates: finite outputs, exact labels/order, raw units, verified weights, unchanged source hashes, sequential CPU workers, existing memory/timeout guards, exact retry reuse. These establish engineering feasibility only.
- Quality gate: no new labels or listener judgments are inferred. Keep production reference default and expose experimental selection with complete eligible coverage or visible reference fallback. Selection is reversible and recorded in catalog/replay evidence.
- Held-out review: calm beach, energetic beach, intimate evening, picnic, heartbreak, celebration, dance party. Separate perceived valence, arousal, movement and scene suitability. Manuel and Grecia judge independently, blind to estimator. Reserve artist/release-disjoint examples for final evaluation; the two smoke sources are development examples and cannot establish superiority. No threshold/calibration/weight fitting in this task.

## Completed checkpoint — 2026-09-25

Research, implementation, model acquisition, two-source inference, catalog/ranking integration, UI, comparison workflow and maintained documentation are complete. Reference remains default; musical superiority and held-out listening acceptance are unproven. The final coverage gate is deliberately stricter than the initial eligible-coverage proposal: every catalog candidate must have compatible challenger evidence.

- Six real stages passed, and all six final retries reused verified checkpoints without inference. Ocean browser retry reused all ten base/optional stages with zero executed.
- 481 Python tests, 80 web tests, 45 JavaScript syntax checks and the 28-file production build pass. Generated-signal official MERT parity is exact across all 13 hidden states.
- Four profiles × ten fixed/recorded queries = 40 exact offline replays. The final successful live result also replays exactly.
- Two live provider calls in isolated browser acceptance: intimate-evening proposal rejected by existing local validation; energetic/danceable request matched using both challengers and two candidates. Scores: Paradise 0.825136, Ocean 0.570411. No new listener ratings.
- Real columns, single-track retry, profile/scope selection, saved-result reopening, App Status and 390/320px control containment verified in the in-app browser. One existing generated playback fixture and its saved playlist were retained; the two authorized files were imported locally for acceptance. No actual-audio quality judgment or playback acceptance is inferred from this.
- Original Chrome library was observed at 109 unique tracks before the update; maintained prior snapshot is 115 records, 83 complete / 9 partial / 17 unanalyzed and 88 PlaylistIQ candidates. Native Chrome interaction was interrupted by active use; a final updated Chrome display is **not claimed**. The normal reload path now attaches richer same-hash optional caches even to already complete reference records. This migration has a passing regression test and preserves stored IDs/audio.
- Local backend cache audit: 113 records, 101 complete / 12 partial, 109 with genres; exactly **two** have complete optional estimators. These counts are distinct from the loaded Chrome library. In-app acceptance library: 3 tracks, 2 complete, 2 compared, 1 existing saved playlist.

[Full research/implementation report](research/SUPERVISED_ESTIMATORS_2026-09-25.md) · [Reader digest](research/SUPERVISED_ESTIMATORS_DIGEST_2026-09-25.md).

## Setup and operation

From `packages/prompt-to-playlist`:

```sh
uv sync --frozen --extra analysis --extra semantic --extra supervised
.venv/bin/python scripts/setup_supervised.py
```

The manifest pins official source/model URLs, sizes and SHA-256. Setup may download about 406 MB of inference assets; ordinary analysis does not download them. `PLAYLISTIQ_SUPERVISED_MODELS` optionally chooses the model directory. Original upstream training requirements are not installed wholesale.

For the already authorized two-source smoke only:

```sh
.venv/bin/python scripts/smoke_supervised.py --run-name matched-v2
.venv/bin/python scripts/integrate_supervised.py
.venv/bin/python scripts/compare_supervised.py
```

The first command resumes and validates source/config identity; it is hard-coded to the two authorized filenames and hashes. Do not generalize this to a new folder or whole-library run without scope. The second validates the successful model outputs and preserves a historical cache snapshot before appending optional stages. The third reads saved values/queries only and produces comparison results and blank blind rating sheets.

In the player, reload to receive code/cache upgrades. Details → Compare feature estimators runs one explicit track, sequentially; a failed stage is visible and successful older values survive. A retry reuses successful compatible stages. All-library base Analyze Tracks does not imply optional experimental stages. PlaylistIQ → Candidate set → Compared tracks only gives the two-track development comparison; select the same candidate set for each estimator profile. More analyzed reference tracks remain available under the default All analyzed tracks scope.

Rollback is **select Reference**, with All analyzed tracks if desired. This changes only the next catalog projection; it does not delete challenger evidence, replace the baseline, erase playlists or change stored audio. Historical cache snapshots remain in `output/web-features/history/<sha256>/`. Do not blindly restore a whole old cache over newer evidence; select the profile or inspect a snapshot first.

Missing assets: rerun setup and verify the pinned manifest. Dependency errors: use the frozen extras above. Memory/timeout failure: leave the failure visible, close unrelated heavy applications and retry only the selected track; do not increase concurrency or weaken guards. Host telemetry needs normal macOS process permissions. Failed provider plan: no playlist is accepted; the two-stage feature cache is independent. Do not silently relax the intent validator.

## Evidence map and continuation

- `src/prompt_to_playlist/supervised_assets.json`: exact official acquisition identities.
- `output/supervised-estimators/matched-v1/`: retained initial strict-load failure.
- `output/supervised-estimators/matched-v2/<ocean|paradise>/<stage>/descriptor-run.json`: measurements, windows, full scores, dependency versions and source preservation; retries retain original execution timing and mark reused.
- `output/supervised-estimators/integration.json`: unchanged baseline/MuQ verification.
- `output/supervised-estimators/mert-parity.json`: generated-signal comparison, audited source hashes.
- `output/supervised-estimators/comparison-v1/`: frozen catalogs/vocabulary/results, matched vs historical measurements, separate blank Manuel/Grecia sheets, organizer key and checksums. Script reruns overwrite generated blank development sheets; copy completed ratings elsewhere before regenerating.
- `output/supervised-estimators/browser-acceptance.json`, `live-success.json`, `live-success-inputs.json`: two-attempt acceptance record and exact final replay inputs.
- `output/supervised-estimators/python-tests-final.txt`, `web-tests.txt`, `retry.txt`: mechanical verification.

Use the [listening instructions](evaluations/SUPERVISED_LISTENING.md) and blank reviewer sheets for the prepared development comparison.

Next work is explicit held-out listening evaluation, not automatic corpus expansion. The seven-scene protocol in the report separates perceived VA, movement, scene relevance and personal response, keeps Manuel/Grecia independent, and reserves artist/release-disjoint final examples. Revisit promotion only after judgments; preserve the reference and hand-set ranking weights until that decision.

## Failures and findings

- Initial workspace-root `git status` failed because the repository is the DJ project subdirectory. Its extensive pre-existing modified/untracked work is preserved.
- Sandboxed public GitHub download failed DNS resolution. Approved network fetch succeeded; no source audio was transmitted.
- Music2Emo official source pinned at `c5f7984f78d9928b841f25bd05a47377c12c58ca`. Wrapper thresholds scores, deletes fixed `temp_out`/`output` directories, permits unrestricted checkpoint unpickling and unpinned MERT loading. Integration must not call this wrapper unchanged.
- Verified machine: macOS 26.5.1, ARM64, 16 GiB RAM, 10 logical CPUs; installed Torch 2.13.0, Transformers 4.57.6, NumPy 2.5.3. Original upstream requirements target Python 3.10/Torch 2.3.1/NumPy 1.26.4; install only required inference dependencies and preserve the working environment.
- Published Essentia DEAM metadata contains an arousal R² value of `589`; treat it as a metadata error, not a usable benchmark or silently corrected result.

Final build verification: 28 static files, 389001 bytes; manifest SHA-256 `a71f0c4ee6fad1b678e003b03ee70c18db8374614c0f0da36b25bdce6b34e0c5`. All manifest content hashes match the build and no source audio/model weights are included. No commit made.
