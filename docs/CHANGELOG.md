# Documentation and Plan Changelog

This file records changes to project direction and documentation. Decisions
belong in `../DECISION_LOG.md`; commands, results, failures, and empirical
learnings belong in `../EXPERIMENT_LOG.md`.

## 2026-09-08 — Full cloud discovery research and agent planning package

- D043 activates research/planning and publishes
  [cloud-library/README.md](cloud-library/README.md) with cited reports,
  proposed contracts, storage comparison, rights/security review packet,
  formula cost model, operations and conditional build plan.
- Added machine-readable source/current-state registers and append-only
  events for decisions, gates, risks, open questions, experiments, rejected
  paths and actual research limitations. Maintenance templates preserve
  motives and reopening conditions.
- Reconciled workspace/project/package handoffs, plans and registry. Playlist
  implementation remains paused and cloud implementation remains unauthorized.
- No engine/package runtime code, audio, live schema or dependency changes.
  No cloud resources, remote processing, outreach or model requests. Artifact
  validation is recorded in E030; historical audio/test results are unchanged.

## 2026-09-08 — Cloud music-library discovery phase

- Registered D042 and added an ordered future product phase for a portable,
  listenable cloud library aimed first at DJs and second at personal digital-
  music collectors.
- Recorded the candidate product surface: descriptor browsing, prompt-built
  playlists, deterministic prompt-built DJ mixes and downloadable renders.
- Made storage-provider cost/integration/retrieval research the first to-do,
  followed by demand, MVP, architecture/development cycle, upload/sync,
  playback, descriptor, AI-boundary, security/privacy/rights, economics,
  reliability and build/no-build work.
- Recorded the adoption risks around a limited digital-library market and the
  initial large upload, with a dedicated streaming-style app deferred.
- Paused further prompt-to-playlist work while preserving its implemented
  V0.2 progress. The local engine's headroom and larger-manual-set milestone
  remains active.
- No source code, audio, cloud resources, schema contracts or corpus policy
  changed. Cloud implementation and automatic MixPlan generation remain
  unauthorized.

## 2026-08-31 — Documentation baseline for DJ Engine V1

### Added

- `README.md` as the project entry point and document map.
- `V1_ENGINE_PLAN.md` as the three-step implementation source of truth.
- `DECISION_LOG.md` for append-only decisions and supersessions.
- `EXPERIMENT_LOG.md` for append-only inspections, experiments, failures, and
  learnings.
- `docs/CORPUS.md` with the authorized 10-track manifest and no-substitution
  policy.
- `docs/SCHEMAS.md` with authority vocabulary, analysis objects, planner tool
  contracts, `MixBrief`, `MixPlan`, and `RenderManifest`.
- This changelog.

### Changed

- Reframed `PLAN.md` as the product north star and mapped the original two
  phases to three V1 steps.
- Recorded that the 10-track house corpus is now populated and ready for an
  approved Step 1 run.
- Recorded that Git is initialized and an existing `uv` scaffold is present,
  while package/import compatibility remains unverified.
- Changed the next build action from “create the environment” to “audit the
  existing scaffold.”
- Standardized authority vocabulary on:
  - `encoded_fact`
  - `standardized_measurement`
  - `deterministic_measurement`
  - `benchmark_estimate`
  - `user_verified`
  - `llm_proposal`
  - `executed_action`
- Split harmonic, tempo, and combined transition scoring into separate planned
  tools.
- Added an explicit section-to-loop derivation policy.
- Added initial EQ bass-handoff, loop, time-stretch, and intermediate-audio
  policies while leaving untested numerical limits open.
- Added the LLM-facing tool-discovery and deterministic scoring interfaces.
- Updated the broad tooling report's corpus note to distinguish the ready
  10-track V1 corpus from the later 120-track corpus.
- Updated the parent project registry from idea status to documentation
  complete / awaiting build approval.

### Deferred

- All implementation, package installation, environment mutation, and audio
  analysis pending user approval.
- Stem separation.
- Semantic genre, mood, energy, danceability, and embedding features.
- LLM provider selection.
- Time-stretch engine decision.
- Exact EQ/gain limits and crossover frequencies.
- Final export format.

### Corrected inconsistencies

- Empty test folder → 10 MP3s confirmed by direct inspection.
- No repository → local Git repository exists, with no confirmed commits.
- Create `uv` project → scaffold and lockfile already exist and must be audited.
- Competing authority terms → one canonical vocabulary.
- Original two-phase plan vs. current three-step plan → explicit mapping.
- Broad 120-track research context vs. V1 10-track test target → explicit
  corpus policy.

### Approval boundary

Documentation work does not authorize build work. The next implementation
milestone begins only after explicit user approval.

## 2026-09-03 — Step 1 build started after explicit approval

### Changed

- Build authorization: user approved implementation. Step 1 is in progress.
- Essentia pin: `2.1b6.dev1389` after latest PyPI wheel failed on CPython 3.12.
- FFmpeg runtime recorded as 8.0.1 rather than the report's 9.0.1.
- Loudness LRA independent-check tolerance set to 0.5 LU; integrated stays 0.1.
- CLI is `dj-analyze FOLDER --out FILE`.
- Analysis artifacts go to `output/`, not the music folder.
- Parent registry, README, PLAN, and V1 engine plan statuses updated.

### Added

- Step 1 package: ingest, loudness, key, rhythm, engines, collection analyzer,
  tests.
- `dj-analyze` console script.

### 2026-09-03 later — 10-track run paused

- Isolated subprocess run saved 6/10 complete tracks then stopped after
  disk-full (ENOSPC), a worker SIGKILL (`-9`), and a laptop hard restart
  from RAM exhaustion (E016, E017). Love State's partial record was later
  dropped by a killed `--retry-failed` run.
- Deleted leftover `output/.dj-engine-work/` (~563 MB). Did not resume
  All-In-One.

### 2026-09-03 — one-track staged pipeline

- Each track is now ingest → All-In-One → Beat This in separate processes.
- Default `--max-tracks 1` with live RAM telemetry on stderr (D029 / E018).
- Remaining four corpus files are intended as four Cursor runs, not a batch.

### 2026-09-04 — staged resume (E019)

- `--resume --max-tracks 4` analyzed the four remaining files.
- Ingest and Beat This succeeded on all four. All-In-One succeeded only on
  Life Is Trippy. Love State, Dj Yellow, and Lemon8 were killed during
  HTDemucs when wired Metal RAM dropped reclaimable below ~768 MB.
- Source MP3 hashes unchanged. JSON now contains 10 track objects.

### 2026-09-04 — spectrogram RSS cap (E020 / D030)

- Retry with ~10 GB reclaimable survived HTDemucs demix, then died at
  spectrogram extraction when RSS hit 4.8–5.0 GB (cap was 4096 MB).
- Default RSS cap raised to 7168 MB. Failed-track retries reuse ingest and
  Beat This and only re-run All-In-One.

### 2026-09-04 — 10-track corpus complete (E021)

- Love State, Dj Yellow, and Lemon8 All-In-One finished under the 7168 MB
  RSS cap (peaks 4689 / 4671 / 4731 MB). Ingest and Beat This were reused.
- Stale collection-level failure records from earlier kills were pruned so
  the JSON matches current track state (0 track failures).
- Step 2 remains deferred pending explicit approval.

### 2026-09-04 — Step 1 shortcomings and Step 2A

- Recorded All-In-One RAM backlog (D031): single Harmonix fold, internal
  demix changes, different model, or Amazon VM. No analyzer swap yet.
- Implemented Step 2A scoring and `dj-score` (D032, D033, E022).
- Step 2B render/EQ/stretch still deferred.

### 2026-09-04 — Step 2B clip renders

- Implemented planner lookups (`get_track_summary`, `get_transition_windows`)
  and FFmpeg clip tools (`dj-render`) under D034 / E023.
- Initial gain/EQ/loop/crossfade bounds and `atempo` stretch are recorded
  as pending listening tests.
- `render_set`, volume envelopes, and Step 3 remain deferred.
- Cleared leftover current-status text that still described the pre-Step-1
  approval checkpoint and unresolved scaffold/Essentia blockers.

### 2026-09-04 — Agent takeover pack

- Added `AGENTS.md` as the live operating brief for a new agent (hard
  stops, corpus table, RAM history, tool status, next slice) (D035).
- Workspace `AGENTS.md` and `.cursor/rules/dj-engine.mdc` point at that
  file.
- Marked `AUDIO_ANALYSIS_TOOLING_REPORT.md` as a frozen research registry
  so v1 is not driven back to FFmpeg 9.0.1 or the 120-track folder.
- Parent `LOG.md` / `PROJECTS.md` / `README.md` updated for the handoff.

### Still deferred

- MixPlan `render_set` and Step 3 LLM planning.
- Stem separation.
- Rubber Band stretch comparison, volume envelopes, final export format,
  LLM provider.

## 2026-09-04 — Manual MixPlan set-render vertical slice

### Added

- Strict manual `MixPlan` models with downbeat-indexed track segments and
  4/8/16-bar transitions.
- `set_renderer.py` validation, source resolution/hash checks, atomic set
  rendering, final measurement, and `RenderManifest` generation.
- `dj-render set --analysis ... --plan ... --out ...`.
- `examples/mvp-three-track-plan.json`, validated but not rendered.
- Synthetic end-to-end and safety/failure-path tests.

### Changed

- `render_set` is now implemented for manual plans; automatic/LLM planning
  remains deferred.
- Direct render CLI operations protect their source parent by default.
- Output safety checks run before creating directories.
- Collection checkpoints and render manifests are written atomically.
- Resume rejects a collection created for a different source folder.
- Current collection-level worker failures are retained until a later resume.
- Unknown MP3 bitrate mode is no longer populated with FFmpeg sample format.
- Test baseline increased from 43 to 50 passing tests.

### Not run

- No real-corpus set render.
- No batch render.
- No stretch/EQ listening experiment.
- No Step 3 planner.

## 2026-09-05 — Downbeat-aligned house-transition revision

### Listening evidence

- The user rendered and heard the D036 v1 three-track plan.
- Both eight-bar overlaps were only 14.44 seconds and felt too quick.
- Opposing whole-track volume fades were not an adequate house transition.
- Incoming downbeats sounded unsynchronized with outgoing downbeats.

### Added

- Exact detected-downbeat-span transition timing and a 70 ms adjacent-grid
  drift gate.
- `house_eq_v1`: 180 Hz band split, midpoint bass handoff, and broad
  high-band entry/exit envelopes.
- `dj-render downbeat-clicks`, producing one centered click-overlay excerpt
  per track selected by a MixPlan.
- `examples/mvp-three-track-plan-v2.json` with two 16-bar, 29.090-second
  transitions and the original transition start positions.
- Synthetic coverage for exact-grid timing, the house transition, and the
  three-output click command.

### Changed

- Test baseline increased from 50 to 54 passing tests.
- The next checkpoint is to hear the three diagnostic clips, then explicitly
  render/listen to v2.

### Not run

- No real v2 set render.
- No real downbeat-click diagnostic render.
- No corpus re-analysis or source modification.
- No Step 3 planner.

## 2026-09-05 — First user-accepted listening checkpoint

### Registered

- The user rendered `mvp-three-track-set-v2.wav` and described it as much
  better than v1.
- Both 29.090-second transition durations and their downbeat alignment are
  accepted for the first version.
- The primary downbeat click diagnostic was also reported great.
- The v2 manifest records 609.100 seconds, −13.81 LUFS, 3.1 LU loudness range,
  +1.04 dBTP, and unchanged hashes for all three source tracks.
- All three primary diagnostic WAVs are exactly 30.000 seconds.

### Status change

- `house_eq_v1` with 16-bar exact-grid timing is now the first user-accepted
  house-transition baseline for these two heard pairs.
- This bounded listening success does not promote all stored rhythm grids or
  other corpus tracks from `benchmark_estimate`.
- Final-bus headroom/limiting becomes the smallest delivery-quality gap because
  the accepted render exceeds 0 dBTP.

## 2026-09-07 — Independent prompt-to-playlist track

### Scope and documentation

- Registered D039 authorizing reusable candidate-selection work in parallel
  with the engine. Automatic MixPlan generation and render integration remain
  deferred; D038/E026 listening evidence and headroom requirements are retained.
- Added a separately installable package boundary at
  `packages/prompt-to-playlist/` with independent runtime, lockfile, tests, and
  documentation. E027 records the implemented and independently tested first
  slice, including a native desktop prompt form, CLI, strict translation,
  deterministic retrieval, and a JSON-only DJ catalog adapter.
- Reconciled takeover brief, product/implementation plans, schemas, corpus
  policy, workspace registry, and Spotify plan crosslinks around that boundary.
- Kept detailed playlist contracts in package documentation; the parent
  schema reference records only the JSON adapter and future integration edge.
- Documented that the real ten-track analysis has no semantic annotations and
  that synthetic labeled fixtures do not supply evidence for the real songs.
- Verified the actual form returned three demo matches, standalone source/wheel
  builds succeeded, real-catalog import preserved all ten BPM estimates and
  produced no semantic tags, and source/analysis hashes remained unchanged.
- Kept the engine baseline at 54 passing tests. The independent playlist
  suite passed 190 tests (E027); its top-level result uses the versioned
  `prompt-playlist/run` 0.1.0 envelope.
- Review closed catalog/vocabulary mutation paths that could bypass initial
  validation and added regression coverage.
- Split next actions between engine delivery quality and reviewed playlist
  tag evidence/live prompt evaluation. Live model quality is not yet validated.

## 2026-09-07 — Larger playlist pool and project OpenAI setup

- Recorded D040 and the user's explicit authorization to use the larger local
  pool and their project OpenAI key for playlist requests. Superseded active
  blanket no-pool rules with a read-only hashing/ffprobe metadata-import scope.
  Heavy acoustic analysis, rendering, automatic MixPlans, and publication
  remain deferred; source audio stays immutable.
- Added project configuration and a desktop launcher for the real catalog and
  OpenAI translation. The configured model is the editable snapshot
  `gpt-5.4-mini-2026-03-17`; reusable no-config operation stays offline.
- Documented credential resolution through `AUTODJ_OPENAI_API_DEV_KEY` and an
  explicit literal-assignment fallback in `~/.zshrc`. No shell execution,
  secret copying, or unrelated-key fallback is part of loading credentials.
- Kept catalog/audio data local. OpenAI sees the request, vocabulary, and
  query contract. Interpretation remains `llm_proposal`, followed by the
  existing deterministic validation/retrieval boundary.
- Extended corpus/schema documentation for local metadata, hash identities,
  source-preservation and coverage manifests, and unreviewed embedded-tag
  provenance. Unavailable labels and unknown tag coverage remain explicit.
- Reconciled parent/workspace handoffs, README, product/implementation plans,
  registry, and editor rules. E028 records the observed import, live API,
  validation, source-preservation results, and remaining evidence gaps.
- Preserved all E027 test/build claims and earlier engine listening/RAM
  findings as historical records. Larger-pool catalog use does not change the
  engine's ten-track corpus or its next headroom/manual-set checkpoint.
- E028 confirms 120 imported tracks, 62 with recognized embedded genre labels
  and 22 with BPM metadata; all 120 pool and ten original source hashes match.
  Raw metadata presence remains separate from normalized semantic coverage.
- Recorded the first live count-interpretation failure, the
  `playlist-query-v2` correction, and five passing live cases. Setup made
  seven live requests in total; the configured desktop smoke check reused a
  saved translation and displayed five real matches without another API call.
- Final standalone suite: 346 passed; engine suite: 54 passed. Version 0.2.0
  source/wheel builds succeeded. Detailed outcomes, elapsed times, artifact
  paths/hashes, and remaining quality gaps are retained in E028.

## 2026-09-07 — Natural-language playlist and interface correction

- D041 supersedes the old implicit offline UI/CLI default after the user’s
  “house dj set energetic” request reached a stale offline window.
- Desktop now requires OpenAI and selects explicit/current-directory/editable-
  checkout configuration; generic CLI prompt defaults to OpenAI, with explicit
  `--provider rules` for offline development. No provider-error fallback.
- `playlist-query-v3` requires a directly requested single genre, prefers
  ordinary mood/energy, and treats “DJ set” alone as playlist context.
- Refreshed the standard-library Tk interface with light styling, simple
  criteria, artists/BPM, visible evidence gaps and optional provenance. No
  dependency, query schema, source-catalog or DJ engine change.
- E029 and package P-E003 retain the reported failure and actual verification
  outcomes: six live cases, 363 package tests, a successful 0.2.0 build and real
  Tk state/geometry checks with no extra API calls. Screenshot QA was unavailable.
  These observations are separate from the earlier small E028 evaluation.
# 2026-09-09 — Private repository baseline

- Added `VERSIONING.md` with the reasons for preserving history, tracked and
  excluded artifacts, independent version namespaces, checkpoint tags, working
  practice, and recovery procedure.
- Added D044/E031 and the `checkpoint-2026-09-09` baseline.
- Preserved compact engine, playlist, and research evidence in Git while
  excluding source music, rendered audio, credentials, environments, caches,
  and disposable analyzer work.
- No engine, playlist, schema, cloud implementation, or audio behavior changed.
