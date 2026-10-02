# Changelog

## 2026-09-25 — Selectable supervised feature estimators

Music2Emo (MERT-95M + BTC/chord/key + J_all, corrected mode) and MusiCNN danceability are implemented as optional direct-feature challengers. The specialist reference remains default; MAEST top-six, MuQ and ranking weights are preserved. Complete compatible catalog coverage is required per challenger; otherwise everyone retains the reference. Two authorized sources passed six matched-window stages and zero-inference retries. Final checks: 481 Python tests, 80 web tests, 45 JS syntax modules, 28-file build, 40 exact fixed-query replays and one final successful live replay. One prior live intent proposal was rejected; no new listening judgments or superiority claim.

Exactly two local cache records have both challengers. Original Chrome was observed at 109 unique tracks; its final updated display was not confirmed because native interaction was interrupted by active use. The new reload migration attaches richer same-hash optional caches to completed reference records. Isolated browser acceptance verified real values, retry, profile/scope, saved-result reopening, App Status and 390/320px controls. No batch/new-corpus inference, audio upload, cloud work, commit or format migration.

Read [research, commands, failures, coverage and continuation](SUPERVISED_ESTIMATORS.md). Historical sections/publication cutoffs below remain evidence for their original dates.


## 2026-09-22 — Hybrid estimator upgrade implemented

MuQ-MuLan-large now supplies local, segmented audio/text similarity; shared Discogs-EffNet supplies all 56 mood/theme and 40 instrument scores. Existing specialist estimators remain. Planner `playlist-intent-v1.6`, compiler `intent-compiler-v1.2`, schema 0.3.0 and `hybrid-semantic-v1` integrate this evidence with replayable contributions. Only descriptors with available evidence enter the planner's soft-preference enum. Historical records remain readable.

Two authorized tracks passed expanded-head and MuQ inference, source preservation and zero-inference retries. Both are attached to the existing Chrome library. Final checks: **442 Python tests, 77 web tests, 45 JS syntax modules and 28-file production build verification passed**. Seven live planner requests exposed and then corrected language/unsupported-field failures; the final affected case passed exact replay. Semantic-only intimacy ranking remains a negative quality finding, not a solved listener case.

The selected implementation is complete; the library-wide upgrade and listening acceptance are pending. Semantic fusion requires complete compatible coverage of eligible tracks. Expanded theme/instrument/valence objectives with incomplete eligible coverage are omitted for every candidate. Use the explicit Analyze Tracks / one-track upgrade actions; do not automatically rerun the whole corpus. No cloud/audio upload, rendered mix, new corpus, commit or YAML migration.

See [implementation log](ESTIMATOR_UPGRADE.md). Package release numbers remain 0.4.0 / player 0.3.0; schema and feature-policy versions identify this working-tree upgrade.

## 2026-09-17 — Creative-intent planner research and YAML evaluation

- Added full and digest planner research under `docs/research/`, including source
  evidence, opinions, a proposed prompt/contract and an ablation-based evaluation.
- P019 records probability-aware genre ranking and creative-intent planning as the
  proposed next direction; no runtime or schema changes in this pass.
- Added PIQ-020 and a Later action for the requested YAML/JSON comparison.

## Playlist-building pattern learning planned — 2026-09-16

- P018 adds a future private personalization path based primarily on repeated
  track co-grouping in the user's manually built playlists.
- Playlist names are retained only as weak optional context; they cannot create
  catalog facts or outweigh grouping evidence.
- Learned ranking remains downstream of explicit prompt/rights constraints and
  must be auditable, versioned, resettable and protected by minimum-support,
  provenance and provider-policy checks.
- Added the corresponding Later board card and implementation/evaluation steps.
  No data collection, model training, schema, dependency or runtime changed.

## Resonant product-direction integration — 2026-09-12

P016/D058 records PlaylistIQ's role inside the broader Resonant DJ workspace.
The host may turn auditable candidates into editable playlists, but owns saved
state, source capabilities, continuous playback, rights-aware playlist-file
download and mix workflows. No code, schema, dependency, catalog, model request
or audio scope changed.

## Complete diverse-37 descriptor run — 2026-09-11

- Audited the user's 37-track run: 222/222 stages, zero failures, 60 verified
  reuses, 162 new executions, 222 compatible checkpoints and exact sources.
- Complete projection: 970.231 stage-wall seconds for 170.920 audio minutes,
  43.704 serial minutes/100 tracks, 1,415.031 MB peak RSS and 1.866 GB/worker
  with headroom.
- The command span was 48.966 minutes versus 11.677 minutes of new worker-stage
  time; future run-phase telemetry must explain the 37.289-minute gap before VM
  elapsed-cost projection.
- Genre top-1 collapsed to electronic for 24/37 and danceability was at least
  0.95 for 28/37. Keep them soft/deferred; mood and raw arousal are stronger
  first catalog-bridge candidates pending human review.

## Diverse-37 verified checkpoint reuse — 2026-09-11

- Recorded the explicitly authorized 37-track, 418,398,951-byte cross-genre
  pre-analysis manifest: 37 unique hashes, ten exact baseline overlaps and 27
  new tracks. No new track was decoded or analyzed during preparation.
- Added repeatable `--reuse-from` with prior source-gate validation and
  per-stage source/pipeline/tool/model/CPU identity checks. Compatible results
  are copied into the separate new output; prior reports remain unchanged.
- Verified all 60 expected baseline checkpoints and prepared a resumable user
  command expected to execute only the 162 new stages.
- Focused pipeline/CLI tests pass 33/33; the full package passes 383 tests, the
  parent retains 54, and the 0.3.0 artifacts build. P-E009 retains exact
  evidence and `docs/DIVERSE_37_MANIFEST.md` is the canonical pre-analysis
  inventory.

## Completed ten-track descriptor baseline — 2026-09-11

- The user's repaired resume reused 50 checkpoints and ran ten Beat This rhythm
  stages in 95.964 seconds. Final result: 60/60 stages, zero failures, 60
  checkpoints, and unchanged source hashes/inventory.
- Complete pipeline: 269.609 stage-wall seconds for 62.984 audio minutes, 4.281
  wall minutes/audio hour, 44.935 projected serial minutes/100 same-length
  tracks, 1,400.047 MB peak RSS and 1.846 GB/worker with 35% headroom.
- Beat This BPM and grids exactly reproduce the earlier DJ artifact for all ten
  tracks. One atypical downbeat ratio remains documented and does not enter
  PlaylistIQ retrieval. P-E008 is the canonical experiment record.
- This accepts runtime integration/capacity evidence only. Semantic thresholds,
  catalog migration, diverse-folder accuracy and prompt fit remain open.

## 0.3.0 operational decoder repair — 2026-09-11

- Audited the user's full ten-track output: 50/60 stages passed, ten Beat This
  rhythm stages failed, and both source-preservation gates passed.
- Confirmed Torchaudio 2.11 required absent TorchCodec and Beat This could not
  reach its missing SoundFile fallback. Added and locked SoundFile 0.14.0 as an
  explicit optional-analysis dependency and preflight requirement.
- Verified real-MP3 rhythm extraction on one track: 9.81 seconds, 220.2% CPU,
  1,053.0 MB peak RSS, 130.43 BPM, 738 beats and 185 downbeats; source unchanged.
- Added legacy checkpoint migration so the user's repair command reuses 50
  successful checkpoints and reruns only the ten failed rhythm stages.
- Excluded failed attempts from capacity projections and require every requested
  stage to pass before a track contributes to the combined projection.
- Expanded the package suite to 381 passing tests. P-E007 retains exact partial
  numbers, failure text, outputs, hashes, fix validation and the resume command.

## 0.3.0 — no-All-In-One descriptor pipeline — 2026-09-10

- Added a variable-folder `analyze-folder` command. It defaults to one track;
  processing every discovered track requires explicit `--all-tracks`.
- Added sequential subprocess stages for FFprobe metadata, FFmpeg loudness,
  Essentia key, Beat This rhythm, shared Discogs-EffNet genre/mood/
  danceability/vocal inference, and MusiCNN/DEAM arousal. All-In-One MLX is not
  installed or invoked.
- Added pinned/hash-verified model caching, strict source/output separation,
  source hashes and inventory gates, time/RSS/available-RAM bounds, resumable
  stage checkpoints, controlled descriptor documents and strict descriptor-run
  schema 0.1.0.
- Added measured wall/CPU/RSS/VMS/thread/swap/I/O/RTF telemetry and per-stage,
  combined-pipeline, 100-track, audio-hour and 8/16/32 GB planning projections
  in JSON and Markdown.
- Resolved Python 3.12/Apple Silicon compatibility with the optional analysis
  environment. Added TensorFlow and PyTorch thread requests while retaining
  observed CPU as authoritative.
- P-E006 ran exactly two of the ten house tracks: 12/12 stages, zero failures,
  source unchanged, 84.23 seconds summed stage wall time for 684.58 seconds of
  audio, 1,311.4 MB maximum stage RSS, and a 70.19-minute serial estimate per
  100 same-length tracks. The full ten-track run remains for the user.
- Expanded the suite to 377 passing tests; the parent engine retained 54. Built
  and isolated-validated the 0.3.0 wheel/source distribution. The current UI
  catalog remains metadata-only; descriptor-to-catalog matching is the next
  separate contract.

## Auditability and next-build brief — 2026-09-10

- P011 makes “lets us audit why each track matched” a core structured-retrieval
  property and records the exact evidence needed to preserve it.
- The active next build is a fully tested, variable-folder, no-All-In-One
  descriptor pipeline with a versioned durable output for later matching.
- CLAP audio–text retrieval, TF-IDF/BM25 descriptor documents, lightweight text
  embeddings, and hybrid retrieval are explicit later comparisons.
- Commercial licensing remains a future viability note, not a blocker for the
  private local feasibility playground.
- No runtime, dependency, catalog, audio, provider request, or schema changed.

## PlaylistIQ local evaluation resumed — 2026-09-10

- P009/D046 name the product PlaylistIQ while retaining the existing package,
  CLI, import, and `prompt-playlist/*` schema identifiers.
- Reverified 363 package tests, 54 parent tests, package build, CLI help, project
  profile, catalog, and non-disclosing credential availability (P-E004/E033).
- Added `Open PlaylistIQ.command` and updated the native window branding.
- P010 documents the no-All-In-One first-web feature priorities, candidate
  semantic models, license gate, deferred fields, and the required diverse-
  folder experiment.
- No audio was analyzed, no live OpenAI request was made, and no catalog or
  serialized schema changed.

## Paused — 2026-09-08

Recorded P008: V0.2 and the natural-language UI follow-up remain implemented,
but further playlist development is paused. Reviewed semantic annotations and
broader prompt evaluation stay in the backlog. Parent D042's future cloud
library phase does not authorize hosting or integration changes in this
package. No code, schema, catalog, dependency or test claim changed.

## 0.2.0 follow-up — 2026-09-07

Corrected a user-visible offline launch failure: the desktop now requires
OpenAI, selects the explicit/current-directory/editable-checkout profile and
rejects rules mode. Generic CLI prompt defaults to OpenAI; offline examples
require `--provider rules`. P007 supersedes the earlier default below.

Revised the translation policy to `playlist-query-v3` for short natural
descriptions: a direct single genre is required, mood/energy is preferred
unless mandatory, and “DJ set” alone is context rather than a render command.
The user’s “house dj set energetic” regression is recorded in P-E003: eight
house-tagged matches with unknown energy, all six live cases passing, 363 package
tests and a successful 0.2.0 wheel/source rebuild. Native Tk state/geometry
checks passed without additional API calls; screenshot QA was unavailable.

Refreshed the desktop with a light, modern Tk interface, plain-language
criteria, artist/BPM results, visible missing-preference evidence and detailed
provenance on demand. No new dependency or serialized schema was introduced.

## 0.2.0 — 2026-09-07

Added a read-only local MP3 metadata/hash importer with FFprobe/version capture,
source-preservation gates, provenance, duplicate aliases and coverage. Imported
the authorized 120-file pool; 62 tracks have exactly mapped genre labels and 22
have positive embedded BPM. Added the project-only pool vocabulary.

Added explicit TOML project configuration, safe named-key loading from environment
or a literal shell-file assignment, and `Open Playlist.command`. The configured
desktop/CLI flow now uses OpenAI and the real pool. The generic library remains
offline by default. Desktop shows available catalog evidence and a usable prompt.

The first live check exposed a count interpretation error. `playlist-query-v2`
fixes the instruction; the corrected request and all five live smoke cases pass.
Added the explicit live-check command/report. No engine runtime, audio analyzer,
source audio or `.zshrc` changes.

## 0.1.0 — 2026-09-07

Added the standalone prompt-to-playlist foundation: strict contracts, editable
vocabulary, evidence-aware deterministic tools, offline grammar, bounded OpenAI
adapter, JSON/DJ adapters, CLI, optional local desktop form, synthetic examples,
independent lockfile and tests. Documented architecture, schemas, decisions,
validation and the parallel roadmap. Parent DJ behavior and runtime unchanged.

Review fixed public-boundary handling of caller-mutated catalogs/vocabularies;
duplicate IDs and ambiguous aliases are revalidated before lookup/provider use.
All API tests use mocked HTTP; no live language-quality claim is made.
## 2026-09-08 — Parent cloud research cross-reference

Parent D043 publishes cloud discovery and proposed host contracts. Package
handoff/README/PLAN now point to that research while retaining the pause.
No runtime, schema, catalog, model call, build or test result changed.

## 2026-09-13 — MAEST Discogs519

Added opt-in `genre_maest` with all 519 mean sigmoid scores in the existing
algorithm values and a separate `prompt-playlist/genre-review` 0.1.0
`genre-top10.json`. It retains failed tracks and source-preservation gates.
No catalog integration or replacement of existing genre evidence.
See [MAEST setup, aggregation and command](MAEST_DISCOGS519.md).

## 2026-09-13 — MAEST listening-review checkpoint

The user-run MAEST diverse-37 output has 33 genre results and four RAM-limit
failures; fresh source hashes all match. A standalone `listening-review.html`
is now beside those outputs. See the DJ project’s `tools/genre-review/README.md`
for regeneration, review semantics and verification limits. No audio analysis
was rerun. The earlier “full run not executed” checkpoint is superseded by
this audit; no genre-quality acceptance or model replacement is implied.

## 2026-09-15 — MAEST top-six and local player integration

Owner-authorized `maest-top6-v1` now replaces legacy genre estimation: match the top six, display three expandable to six, retain all 519 scores, and apply no probability threshold or human review overrides. Historical outputs remain preserved. The low-priority board card `PIQ-GENRE-TOP6-REVISIT` is Later / could; further genre experimentation is not a launch blocker.

The local web player now provides **Analyze tracks** and **Create with PlaylistIQ**. Its loopback Node job service invokes the existing Python environment; analysis persists by source hash and in IndexedDB, and prompt results save into normal playable playlists. Restart the player server on the same origin/port to retain the browser library. This explicit integration authorization supersedes older local bridge/Python-edit holds; cloud deployment, remote audio processing and automatic MixPlans remain deferred.

See [integration contract](WEB_INTEGRATION.md).

## 2026-09-15 — Analysis workspace and fresh-export repair

Analyze tracks and PlaylistIQ now sit in the top controls. Feature columns toggle in the track list; the Analysis tab uses the full width with sticky track names and headers, horizontal scrolling, genre scores, tempo/key/loudness/arousal, mood/danceability/vocal scores and missing-stage details. Option 2 uses compact transport in Analysis. PlaylistIQ is a themed page with analyzed-track count, prompt form and inline results/save action; the earlier technical introductory copy is removed.

Fresh MAEST export NameError fixed; persistent checkpoints and invalid-worker-output recovery added. See the player WORK_LOG and PlaylistIQ WEB_INTEGRATION for evidence and retry instructions.

## 2026-09-19 — PlaylistIQ Iteration 1 delivered

Python 0.4.0 / player 0.3.0 now integrate `playlist-intent-v1.3` (configured low reasoning), `intent-compiler-v1.1`, `maest-intent-v1` ranking and `discogs-parents-v1`. Required genres use MAEST support; creative prompts use directional soft priorities. Genre OR/family matching, original-request clarification, per-track contributions and twenty-prompt review evidence are available. New result/catalog/translation/run writes use schema 0.2.0 and read historical 0.1.0.

422 Python tests and 50 web tests pass. Final compiler replay passes all 20 intent/constraint checks; live revision failures are preserved, and final optional/HTTP checks pass. Human listening acceptance remains pending. No new audio analysis or cloud work; YAML is still a consideration task.

See [implementation, prompt, contracts and verification](ITERATION_1.md). This current checkpoint supersedes older descriptions of v3-only translation, flat genre ties and missing parent matching; dated older sections remain historical evidence.


## 2026-09-25 — Quality-first estimator research and implementation

Quality-first non-genre research and the selected available specialists are delivered locally. The web default selects Music2Emo theme/VA, MusiCNN vocals, VGGish aggression and independent PaSST OpenMIC instrument evidence, retaining EffNet happy/sad/relaxed/danceability. SheetSage2 supplies selected key evidence. MAEST, MuQ and planner weights remain unchanged. Two authorized sources passed 8/8 new stages; retries execute zero stages. Richer nuanced-emotion prediction and listening superiority remain unresolved; do not present encoder-only releases or the same 56 tags as solving that objective.

[Implementation, two research reports, setup, model contracts and verification](TOP_ESTIMATORS_IMPLEMENTATION.md). Final validation: 502 Python tests, 83 web tests, 45 syntax modules, 28-file build, eight successful final audio stages and 26 exact fixed-query replays. No new provider calls or listener judgments. The new optional specialist stages and quality/openmic vocabulary identity preserve reference records and saved-profile replay.

## 2026-10-01 — Unified default analysis delivered and verified

Owner requested selected model replacements in ordinary Analyze Tracks, retained unreplaced/additional features and both Music2Emo/EffNet moods. Implemented `selected-estimators-v2` with eleven sequential guarded stages, isolated stage failures, missing-only retry, current-cache precedence, updated primary columns and explicit comparison labels. Fresh two-track test passed 22/22 stages in 129.19/182.31 seconds; peak worker RSS 3680.4/3064.3 MiB, minimum host available RAM 2532.7/2546.3 MiB. Both retries and real HTTP analysis requests executed zero stages. Hashes/inventories unchanged. Prior cache history and retired results preserved. 505 Python + 84 web tests, 45 syntax checks and 28-file build pass. One migration test fixture needed the new version; no real inference failure. Chrome Analysis verified and left ready with 109 unique tracks. No whole-library/new-album inference, cloud activity or commit. Two-track success does not guarantee every future file; whole-machine swap increased during the test.

See the maintained default-pipeline document for exact lineup, evidence paths and limitations.

## 2026-10-01 — 120-description bank ready

Owner authorized 120 concepts, precomputed text embeddings and replacement matching that reuses audio embeddings. Delivered `musical-character-v2-120` (30 emotion / 25 groove / 25 texture / 20 intensity / 20 arrangement), independent audio cache, bank-content and audio-fingerprint score invalidation, a model-free matching path, and current-version upgrade detection. UI groups two matches per dimension and spells out seconds sampled. Playlist ranking unchanged.

All 120 text embeddings prepared in 34.38 s, peak worker RSS 1574.8 MiB. Two existing acceptance tracks refreshed in ~42 ms each; exact audio vectors and other stages unchanged, no inference, repeated requests no-op. Real HTTP route accepted current records. 516 Python / 85 web tests pass. No whole-library inference or matching was launched. See CHARACTER_BANK_120.md for full concepts, artifact paths and unvalidated listening-quality limits.
