# Staged web-player build

## 2026-10-17 — Album artwork, local only

[Artwork checkpoint](../../docs/ALBUM_ARTWORK.md): embedded-first extraction, conservative MusicBrainz/CAA fallback, album/negative caches, provenance, 500/96px derivatives, post-storage local import hook and resumable backfill are implemented. Only compact library/result/minimized-player thumbnails; both spectrograms preserved. No deployment. Personal cloud upload lifecycle, private derivative delivery and physical iPhone acceptance remain pending. Transition, analysis and ranking work is unchanged.

## 2026-10-06 — Individual accounts and spectrum motion

[Account release](docs/ACCOUNTS_RELEASE.md) replaces shared hosted state with email/username/password accounts, private playlists/PlaylistIQ results/listening counters, owner-only bounded analytics and a full-spectrum motion override. Google sign-in/linking is implemented but activation and real-provider acceptance await a Google web client ID. Owner authorized deployment, a test user, live-history reset and Git push. Current rollout receipt and limitations are maintained in the linked checkpoint; audio, saved analysis and planner policy are preserved.

## 2026-10-04 — History and native spectrum published

The owner-authorized release is live on resonant.lat and CloudFront: green PlaylistIQ tab (+15%), 1.6-second mini-spectrum pause easing, permanent Liked Songs, playable prompt history, prior sheet/UI refinements and real native-playback spectra. API/worker aliases 4/4, admissions enabled; audio/model/password unchanged. 168 web / 22 API / 5 infrastructure checks plus cloud auth, ranges, spectrum protection and profile persistence pass. [Production checkpoint](../../docs/cloud-library/first-release/serverless/HISTORY_SPECTRUM_RELEASE.md). Physical iPhone acceptance remains.


## 2026-10-04 — History, likes, sheet motion and real native spectrum

Local 4174 now includes permanent Liked Songs, revised navigation/footer/cards, slower rounded sheets and playable saved prompt results with new explanation snapshots. Replaced iPhone progress-grid fallback with audio-derived frequency files while preserving native playback. **168 web / 22 API tests; 85 syntax modules; 47-file build pass. Not deployed or pushed.** Read [current changes, evidence and publication handoff](docs/WEB_HISTORY_SPECTRUM_REFINEMENT.md). Three existing production prompts retain their ten saved tracks; no history reset. Physical iPhone acceptance remains.


## 2026-10-03 — Discovery and third player refinement

Local 4174: 1.25× taller spectrum, centered title/artist spacing, larger icon-only controls, stable seeking UI, 75%-height queue, two-row mobile navigation, stacked card actions and immediate top-five cosines. Each reload randomizes the library and selects two of 50 examples across ten writing styles. More habits derive from existing profile counters. **165 web tests / 81 syntax modules / 44-file build pass. Not deployed.** [Current behavior and evidence](docs/WEB_DISCOVERY_REFINEMENT.md). Physical iPhone acceptance remains.

## 2026-10-03 — Shared listener profile and second UI polish ready locally

4174 now saves likes/playlists and PlaylistIQ prompt/listening history through a durable local profile, with the matching authenticated cloud API prepared using the existing DynamoDB table. Slower sheets, smaller spectrum, Love/Add controls, themed sort, compact character features and main-player DJ mix are implemented. **Not deployed; local review hold remains.** 156 web / 21 API-edge / 4 infrastructure checks pass; 79 syntax modules and 43-file build. Read [profile behavior, cost, tests and deployment handoff](docs/SINGLE_USER_PROFILE.md). Deployment now needs API/routes/IAM as well as frontend; earlier frontend-only handoff is superseded.

## 2026-10-03 — Full-screen mobile refinement ready locally

The 4174 web preview now has edge-to-edge expanded playback, pull-down dismissal, animated title swipes, a mini spectrum, whole-card playback with musical facts, a current-first queue and shorter PlaylistIQ explanations. **Not deployed; the local-review hold remains.** 143 tests, 72 syntax modules and a 38-file build pass. In-app browser checks cover 320/393px, desktop, mouse drags and synthetic IQ presentation. Real iPhone touch/background acceptance remains; iOS still uses native playback progress instead of FFT. [Current changes and evidence](docs/WEB_REFRESH_2026-10-03.md).

## 2026-10-03 — Web refresh ready for local review

The simplified web UI, 186 distinct recordings, PlaylistIQ deduplication, mobile mini/expanded player and iOS native-audio fix are implemented locally on 4174. Replacement password is privately staged. **Not deployed: owner confirmation required by the current request.** 135 tests, 70 syntax modules and 37-file web build pass; Chrome responsive and transition-seek checks pass. Real iPhone background/lock-screen acceptance remains. [Changes, evidence, limitations and deployment handoff](docs/WEB_REFRESH_2026-10-03.md).


## 2026-10-02 — Serverless candidate implemented locally (D072/E060)

[Current implementation checkpoint](../../docs/cloud-library/first-release/serverless/IMPLEMENTATION.md) supersedes the earlier plan-only status. Lambda worker, durable jobs/login, static playback transport, allowlisted export and five infrastructure templates are implemented locally. 123 player / 16 API-edge / 24 Python tests pass; offline Linux preserves all 60 planner cases. A separate preview on 4176 loaded 187 tracks and played/seeked audio with the API deliberately unavailable. Original release/model policy and 4173/4174 servers preserved.

One no-cost AWS quota request is now PENDING: concurrency 1,001 because AWS rejected 200 as below its standard default 1,000, despite the effective account limit of 10. App reservations remain worker=1/API=5. No compute/storage/subscription resource created, upload or paid model call. Final self-contained image export needs more disk (20 GiB free before build). CloudFront Free subscription is explicit in IaC; zero existing subscriptions observed, actual eligibility unproven. Hosted-key choice, alert email, real cloud benchmark/auth/ranges/rollback remain pending. Use the checkpoint and serverless runbook, not the historical VM provisioner. T034 remains in progress.

## 2026-10-02 — Separate production cloud runtime prepared

The immutable 187-track release, production server and frozen planner are ready
locally; Linux execution and cloud publication remain pending. The existing
local/preview servers and UI were not restarted or redesigned. AWS profile
`manueldev` / IAM `manuel-web` is selected. Read the
[current preparation checkpoint](../../docs/cloud-library/first-release/PREPARATION.md)
and [deployment operator guide](../../deploy/first-release/README.md).

## 2026-10-02 — Shared-library web edition preview

Web edition runs on port 4174 with layout 3, 187 verified fully analyzed MP3s, a single mix with transition timestamps, and brief white guide cards. Local edition stays on 4173 with layouts 1 and 3. Owner-only APIs are blocked in web mode. A live PlaylistIQ request and main-player playback passed; 95 tests pass. Same private repository, separate edition/config/build; no cloud deployment or audio upload performed. [Architecture, catalog gate, tests and next launch steps](docs/WEB_EDITION.md).

## 2026-10-01 — M4A normalization and storage recovery

New uploads convert M4A to MP3 locally; Analysis includes a provisional bulk conversion button. Closed storage reconnects once, then pauses analysis on persistent failure. Originals are preserved; converted audio needs fresh analysis. 90 web tests pass. Chrome currently has zero persisted track rows after reload; recovery is unresolved, not completed. See [implementation and evidence](docs/MP3_IMPORT.md).

## 2026-10-01 — Test music relocated; local server restarted

The owner moved the three existing test corpora into `test_music/` and created `test_music/new_albums/`. Runtime recovery and bounded smoke/attachment scripts now use the new parent; current README commands are updated. Historical analysis files retain their recorded paths and hashes. The DJ engine resolves a missing legacy corpus folder to its existing `test_music` location without changing archived evidence; existing folders always take precedence. Source-output protection includes the new music parent, and Git excludes the whole local music tree.

Server uses the existing `http://127.0.0.1:4173` origin. Models, profiles, weights and analysis behavior are unchanged. The owner will manually import new albums and launch analysis; the agent did not import or analyze music. Bulk Analyze Tracks remains the standard pipeline; Details → Upgrade selected specialists runs the newer selected models. `new_albums` is not silently included in Restore saved batch.

## Current — 2026-09-25 quality-selected estimators

Research reports and the selected available specialists are implemented and validated on two authorized sources. [Checkpoint](../prompt-to-playlist/docs/TOP_ESTIMATORS_IMPLEMENTATION.md). Richer emotion heads and listening-quality acceptance remain open. This supersedes the older next-task-only entry below.

## 2026-09-25 — Selectable supervised feature estimators

Music2Emo (MERT-95M + BTC/chord/key + J_all, corrected mode) and MusiCNN danceability are implemented as optional direct-feature challengers. The specialist reference remains default; MAEST top-six, MuQ and ranking weights are preserved. Complete compatible catalog coverage is required per challenger; otherwise everyone retains the reference. Two authorized sources passed six matched-window stages and zero-inference retries. Final checks: 481 Python tests, 80 web tests, 45 JS syntax modules, 28-file build, 40 exact fixed-query replays and one final successful live replay. One prior live intent proposal was rejected; no new listening judgments or superiority claim.

Exactly two local cache records have both challengers. Original Chrome was observed at 109 unique tracks; its final updated display was not confirmed because native interaction was interrupted by active use. The new reload migration attaches richer same-hash optional caches to completed reference records. Isolated browser acceptance verified real values, retry, profile/scope, saved-result reopening, App Status and 390/320px controls. No batch/new-corpus inference, audio upload, cloud work, commit or format migration.

Read [research, commands, failures, coverage and continuation](../prompt-to-playlist/docs/SUPERVISED_ESTIMATORS.md). Historical sections/publication cutoffs below remain evidence for their original dates.


## 2026-09-22 — PlaylistIQ estimator upgrade

The selected local hybrid is implemented and integrated: MuQ-MuLan musical-character retrieval, 56 mood/theme and 40 instrument outputs, exposed valence, versioned catalog/query/replay, fair coverage fallback and app explanations. Two authorized tracks are upgraded in Chrome; the rest retain their existing analysis until an explicit upgrade. Final validation: 442 Python / 77 web tests, 45 syntax modules, verified 28-file build. Listening superiority remains unproven; the semantic intimacy comparison was a negative finding.

See [research](../prompt-to-playlist/docs/research/ESTIMATOR_UPGRADE_2026-09-22.md), [digest](../prompt-to-playlist/docs/research/ESTIMATOR_UPGRADE_DIGEST_2026-09-22.md) and [implementation evidence / continuation](../prompt-to-playlist/docs/ESTIMATOR_UPGRADE.md). New checkpoint supersedes older pending descriptor-bridge descriptions. Cloud, corpus and render boundaries remain in force.

## 2026-09-19 — Prompt-to-scene explanations and listener counterexample

Why this track now connects the exact request and saved planner scene to conditional listening roles for recorded audio evidence, before the numeric explanation. It makes scene assumptions and limits explicit: broad mood agreement does not establish that a track belongs in a setting. The notebook can reopen exact saved results without regeneration. Chrome verified the original 65.62-point Listen Over the Ocean result for “un dia en la playa”; Manuel/Grecia feedback was saved to that attempt, without assigning a whole-playlist verdict or changing ranking. 69 web tests pass. See [scene-fit case](docs/SCENE_FIT_FEEDBACK.md) and [explanation contract](docs/TRACK_EXPLANATIONS.md).


## 2026-09-19 — Natural-language PlaylistIQ score explanations

Every result now explains musical fit, strongest contributors, the main score gap, qualification and rank. Expandable per-objective details translate recorded evidence, preference direction, explicit/inferred origin, priorities, weights and earned points into plain language with 0–100 arithmetic. Missing evidence, genre alternatives/families, tempo ordering and rounding are explicit; raw engine notes remain available. Deterministic presentation adds no explanation LLM calls or ranking changes. See [explanation contract and example](docs/TRACK_EXPLANATIONS.md). 64 web tests pass; current Chrome beach-day request inspected.


## 2026-09-19 — Chrome batch recovery, unique Analysis and result playback

Recovered 54 exact-hash originals with complete saved analysis into the existing Chrome profile at `127.0.0.1:4173`: the older 37-track batch (including ten house tracks) plus 17 cached pool tracks. Chrome now has 115 library records / 109 unique Analysis tracks (83 complete, nine partial, 17 without analysis); PlaylistIQ has 88 genre-backed candidates. Six duplicate Analysis entries are collapsed by content hash, retaining stored audio/IDs and playlist references. Every PlaylistIQ result can play through the main player. Restore saved batch is repeatable and limited to the three established source folders; regular imports reattach matching cache data. No new audio inference.

57 web tests, 35 syntax checks, 24-file build verification and local HTTP checks pass. Chrome playback advanced on the selected second result, then was paused. Repeat recovery confirmed zero added / 54 already present. Human listening acceptance remains pending. See [recovery workflow and evidence](docs/LIBRARY_RECOVERY.md).


## 2026-09-19 — PlaylistIQ Iteration 1 delivered

Python 0.4.0 / player 0.3.0 now integrate `playlist-intent-v1.3` (configured low reasoning), `intent-compiler-v1.1`, `maest-intent-v1` ranking and `discogs-parents-v1`. Required genres use MAEST support; creative prompts use directional soft priorities. Genre OR/family matching, original-request clarification, per-track contributions and twenty-prompt review evidence are available. New result/catalog/translation/run writes use schema 0.2.0 and read historical 0.1.0.

422 Python tests and 50 web tests pass. Final compiler replay passes all 20 intent/constraint checks; live revision failures are preserved, and final optional/HTTP checks pass. Human listening acceptance remains pending. No new audio analysis or cloud work; YAML is still a consideration task.

See [implementation, prompt, contracts and verification](../prompt-to-playlist/docs/ITERATION_1.md). This current checkpoint supersedes older descriptions of v3-only translation, flat genre ties and missing parent matching; dated older sections remain historical evidence.


**0.2.1 — D062/E050:** Always-visible Option1/Option2 header buttons;
Radio is predominantly black/dark gray. Live switching preserves generated
playback; desktop/390/320 checks pass. Library information and exact0.1.2 snapshot
retained.13syntax/15HTTP checks pass; no provider scope changes in this revision.


**Current0.2.0 — D060/E049:** Two frontend options: Studio(default) and
Radio(`?front=radio`). Switch in Library information. Exact0.1.2 preserved in
checkpoints/option-1-0.1.2 (34verified hashes). Read
[options](docs/FRONTEND_OPTIONS.md) and [R4 checkpoint](docs/FRONTEND_OPTIONS_PLAN.md).
30tests/13syntax modules/15HTTP checks plus Radio entry/CSS200 pass. Browser
layout/switching QA unrun under current workflow; prior browser evidence below
is historical. Local-only; no source audio or cloud scope changed.


**Current player — 0.1.2, D059/E048 (2026-09-13):** Removed filler copy;
visible text is at least16px, titles larger. Added collection Shuffle and fixed
shell/list-only scrolling; Library information retained.30tests/15HTTP checks
and desktop/390/320 checks pass. Read [R3 checkpoint](docs/UX_REFINEMENT_PLAN.md)
and WORK_LOG. Earlier0.1.1/0.1.0 evidence below is historical.


Authority: 2026-09-12 user request, D054. Deliver a complete local player and
portable static deployment output; connect hosting/storage/services later.
Latest checkpoint: **Original five stages and R2 design/plan stages complete;
current0.1.1 has30tests and15HTTP checks.** See [R2 plan](docs/REDESIGN_PLAN.md).

## Broader product direction — D058

This package began as a listening surface for the local/cloud library adapter.
It now sits inside a broader Resonant DJ workflow: build and edit playlists in
the app, audition the whole ordered set without switching among source apps,
download eligible playlist files for later DJ use, and separately request a
deterministic continuous mix when that workflow is authorized.

Current0.1.1 already supports manual playlist creation, ordering, continuous
queue playback and JSON export in local mode. The future cloud slice adds
account persistence, supported connected-source playback and an asynchronous
audio archive. Put **Download playlist files** inside the existing playlist
ellipsis / More options menu; do not promote it to the primary toolbar. Show a
preflight with ordered track count, eligible/unavailable entries, bytes and
archive contents. A provider track may be streamable but not downloadable.
No cloud/backend/provider implementation is authorized by this direction.

| Stage | Deliverable / exit criterion | Status |
|---|---|---|
| 1. Scope and boundary | Read handoffs; isolated package; local/cloud adapter boundary; preservation rules | Complete |
| 2. Listening application | Responsive UI, local file imports, demo audio, library, transport, queue, favorites, playlists, error/empty states | Complete: local application and responsive UI authored; browser acceptance is stage 4 |
| 3. Reliability | Build/check scripts, meaningful state/adapter tests; fix actual failures | Complete: 30 tests, syntax, static build and 12 HTTP checks |
| 4. Browser acceptance | Desktop/mobile visual QA; playback/seek/queue/import/persistence/errors using generated audio | Complete within documented browser coverage; real-device/provider tests remain later work |
| 5. Deployment handoff | Static dist, service contract/configuration, hosting acceptance checklist, docs/registers reconciled | Complete locally; no deployment executed |

## Product decisions

- Name: Resonant, matching repository/project identity; PlaylistIQ remains its
  independent prompt-to-playlist product.
- Visual direction (D057 supersedes original lime): gray brutalist workspace,
  Geist Mono200/400, masthead and ruled listening rail; actual listening
  controls in the first viewport. No marketing page or invented track art.
- Standard HTML audio owns playback; keep one audio element, native accessible
  range inputs, browser media controls where supported, no DSP or mixing.
- Local import copies chosen audio to IndexedDB for later browser sessions.
  Display names come from filenames; unknown artists/semantic descriptors stay
  unknown. No source-folder auto-import, processing or upload.
- Pure ES modules and Node standard-library tooling: static output, zero npm
  runtime dependencies, independent of both Python packages and hosting vendor.
- Playlist/favorites storage is persistent locally; HTTP mode is session-only
  pending an authenticated account namespace. No claim of account synchronization or AI playlist integration.
- Playlist-level audio download is a future service job, separate from the
  existing JSON export and from DJ mix rendering. It stays in More options and
  can include only owned or otherwise download-authorized files.
- Future HTTP adapter validates catalog/pages and short-lived capability
  envelopes; cookie/session establishment and storage are future services.

## Required checks before calling complete

- Syntax/static references, deterministic build contents, no private audio,
  credentials or source paths in deployment artifacts.
- State tests: rapid track changes; late play resolution after pause/clear;
  queue identity while moving/removing; next/previous/repeat/shuffle; bounded
  expiry recovery; safe error presentation; input/URL/catalog validation.
- Browser: actual demo play/pause/seek/next, local generated-file import and
  reload, favorites/playlists/reordering/export/remove, search empty state,
  narrow layout, keyboard/focus, clear library/service failures.
- Document what was measured separately from open provider/device tests.

## Later deployment dependencies (not this build)

Select host/storage/auth, implement/verify authenticated catalog and capability
API, enforce tenant/source authorization, private object storage and range
semantics, configure CSP/CORS, verify expiry and deletion, test actual intended
browsers/devices, then explicitly deploy. Existing research gates remain open.

## Continuation rule

Read AGENTS + WORK_LOG before editing. Advance one stage, record outputs and
evidence, then continue. Leave this table accurate even when work stops mid-stage.

## Navigation refinement — 2026-09-13

Plan: replace top Favorites/Demo collection with a Playlists directory, preserve existing data and both frontend options, then verify the build. Implementation in progress.

Completed: directory and route handling implemented. 13 syntax modules, 30 tests and exact 14-file build verification pass. Browser interaction QA was not run for this patch.

## Spectrum accent — 2026-09-13

1. Reference/layout review complete: Option 2 left column below Add music.
2. Implement a subtle static dotted spectrum SVG, without simulated measurements or audio processing. Hide on narrow layouts where the empty column disappears; preserve Option 1.
3. Pending: build and visual verification, then durable checkpoint.

Spectrum stages 2–3 complete: SVG, scoped layout, production build and desktop preview checked. Narrow-screen hiding verified by CSS inspection only; no new device checks.

## Live spectrogram correction — 2026-09-13

User clarified actual playing audio must drive a 3D spectrogram. Supersedes static accent interpretation. Stage 1: implement lazy Web Audio analyser and bounded frequency-history canvas in existing Option 2 position. Stage 2: verify generated playback, pause and switching; checkpoint limitations. No corpus batch analysis or provider implementation.

Live spectrogram stages complete: actual FFT history rendered and browser-inspected during generated playback, pause and Option 1/2 switching. 14 syntax modules, 30 regressions and final build integrity pass. Provider integration remains deferred.

## Spectrogram axis padding — 2026-09-13

Plan: extend both projected axes with zero-height ground equal to 10% of the original span at each end. Preserve all measured samples; fit the 120% surface inside the existing canvas. Verify syntax/build and checkpoint.

Axis-padding stage complete: exact endpoints -0.1/1.1 normalized to the canvas, 10 extra columns and 5 extra rows per side. 14 syntax modules and 15-file build integrity pass. No new browser QA or audio-path changes.

## Frontal spectrogram — 2026-09-13

Plan: roll back only the last axis-padding change, then replace perspective projection with frontal aligned ridges. Preserve FFT/history/playback. Verify syntax/build and document.

Completed frontal projection and padding rollback. 14 syntax modules and 15-file build verification pass. No audio-path changes; browser visual review not rerun.

## Zero-elevation correction — 2026-09-13

User clarified a direct front view. Remove time-dependent vertical offset; all history shares one baseline, with age conveyed only by opacity. Implementation complete; syntax/build verification next.

Zero-elevation verification complete: 14 syntax modules and 15-file build integrity pass. No browser or unit-test rerun for the single projection correction.

## Spectrogram modes — 2026-09-13

Plan: add Isometric / Front / Mountain controls. Restore original unpadded isometric formulas; preserve zero-elevation Front. Mountain uses denser interpolated, smoothed/tapered actual audio history to echo reference grain without fake telemetry. Verify build and browser modes.

Modes implemented and checked: initial desktop playback continued through Front → Isometric → Mountain; final 14-module syntax and 15-file build validation pass. Final spacing/quiet-point refinement source checked; no final desktop screenshot after viewport became narrow.

## Falling spectrogram — 2026-09-13

Plan: fourth mode based on Mountain, 48 × 1.3 rounded to 62 visible history planes; oldest 30% descend and fade into reserved lower canvas space. Preserve first three modes and shared audio history.

Falling implemented; 14 syntax modules and 15-file build integrity pass. Projection inspected in source; browser visual QA not run for this revision.

## Pause descent — 2026-09-14

Plan: all four views gently drop/fade their retained points over four seconds on pause, without reading new FFT frames. Cancel on resume/seek/track change; stop animation after completion and while hidden.

Pause descent complete: bounded four-second animation, no paused FFT reads, lifecycle reset paths inspected. 14 syntax modules, 30 regressions and build integrity pass. Browser visual acceptance not rerun.

## Faster fall / playback rise — 2026-09-14

Plan: reduce pause descent from 4s to 2.8s; add 1.6s eased rise from canvas bottom on playback across all modes. Keep real FFT input and bounded rendering.

Motion update complete: 14 syntax modules and 15-file build integrity pass. Browser animation acceptance not rerun.

## 2026-09-15 — MAEST top-six and local player integration

Owner-authorized `maest-top6-v1` now replaces legacy genre estimation: match the top six, display three expandable to six, retain all 519 scores, and apply no probability threshold or human review overrides. Historical outputs remain preserved. The low-priority board card `PIQ-GENRE-TOP6-REVISIT` is Later / could; further genre experimentation is not a launch blocker.

The local web player now provides **Analyze tracks** and **Create with PlaylistIQ**. Its loopback Node job service invokes the existing Python environment; analysis persists by source hash and in IndexedDB, and prompt results save into normal playable playlists. Restart the player server on the same origin/port to retain the browser library. This explicit integration authorization supersedes older local bridge/Python-edit holds; cloud deployment, remote audio processing and automatic MixPlans remain deferred.

See [integration contract](../prompt-to-playlist/docs/WEB_INTEGRATION.md).

## 2026-09-15 — Analysis workspace and fresh-export repair

Analyze tracks and PlaylistIQ now sit in the top controls. Feature columns toggle in the track list; the Analysis tab uses the full width with sticky track names and headers, horizontal scrolling, genre scores, tempo/key/loudness/arousal, mood/danceability/vocal scores and missing-stage details. Option 2 uses compact transport in Analysis. PlaylistIQ is a themed page with analyzed-track count, prompt form and inline results/save action; the earlier technical introductory copy is removed.

Fresh MAEST export NameError fixed; persistent checkpoints and invalid-worker-output recovery added. See the player WORK_LOG and PlaylistIQ WEB_INTEGRATION for evidence and retry instructions.

## 2026-09-15 — Analysis action and batch duplicate review

Removed shared Analyze tracks / PlaylistIQ buttons; Analysis has a larger dedicated Analyze tracks action. Imports now compare SHA-256 content and normalized filenames, including earlier files in the batch. Unique files are added first; one end-of-import dialog lists duplicates with Omit (default), Keep both and Replace, applied together. Closing the dialog omits pending duplicates. Replacement atomically updates the saved audio and track while preserving its ID, playlist/favorite references and added date; analysis survives only for identical bytes. Changed audio loses stale features. Replacing the current item reloads it paused while preserving the queue. Import and analysis cannot overlap. Original files are never modified.

Evidence: web-player WORK_LOG, 35 passing tests.

## 2026-09-15 — Option 3 visualization layout

Option 3 (`?front=radio-wide#library`) inherits Option 2. Only Your Library above 700px changes: the left visualization/right list grid uses 1.15:1 instead of 0.7:2, moving the list right and allowing the visualization to grow vertically. All other routes and narrow layouts retain Radio behavior; storage, playback and analysis are shared. The masthead and Library information expose all three options.

Validation: 35 player tests, 18 JS syntax checks and production manifest verification pass. Browser switching at 1280px confirms list width changes from 868px (Option 2) to 545px (Option 3), with visual review. No audio processing, provider calls or corpus edits. Reload the existing player origin and choose Option 3.

## 2026-09-15 — Denser, stronger spectrogram display

All four modes now draw points 25% larger and use 64 time slices (formerly 48); Falling retains 83 (formerly 62). Vertical amplitude display gain is 1.15 in every projection. Sampling cadence, frequency bins, audio signal, pause descent and rise timing are unchanged. This affects the shared visualizer in Options 2 and 3.

Validation: 35 tests, 18 JS syntax modules and production build verification pass. No new listening/browser acceptance or acoustic analysis run. Reload the player to load the rebuilt visualizer.

## 2026-09-15 — Visualization controls and amplitude refinement

On desktop Radio/Option 3 Your Library, Add music sits at the bottom-left of the library area; visualization selectors follow the canvas below-right. Shared visualizer points now use 1.60× baseline size (formerly 1.25×), and vertical amplitude is 1.30× baseline (formerly 1.15×). Time slices remain 64/83; audio and analysis are unchanged. Syntax (18 modules) and build verification pass; desktop Option 3 placement visually verified. Reload the existing player origin.

## 2026-09-15 — Taller visualizer with reference axes

Desktop Radio/Option 3 Your Library hides its visible heading while retaining its accessible heading, allowing the canvas to occupy the freed height. All spectrogram modes add themed 16px logarithmic frequency references (40/100/1k/10k Hz where space permits) and relative display-amplitude ticks referenced to the newest slice. Amplitude labels are not calibrated dB; shaping and gain remain visual. Canvas reserves label margins and clips points to the plot area. Syntax/build checks pass; desktop layout and non-clipping reference labels visually verified. No audio processing or corpus changes.

## 2026-09-15 — dBFS axes and maintained App status

Added App status navigation with live library counts and a maintained overview of capabilities, analysis models, prompt restructuring, deterministic matching, storage, limitations and next steps. Shared visualizations now use 11px axis labels, denser logarithmic Hz ticks and floating-point FFT magnitude from −90 to 0 dBFS. Removed artistic magnitude taper; the scale describes windowed FFT bins, not LUFS or a sample-peak meter. This supersedes the earlier relative-amplitude axis.

Validation: 36 player tests pass (including local/demo counts and content escaping), 21 JS syntax modules pass, and the 18-file production build verifies (SHA-256 5164bca7e411e1a169911ca97ac74dbeeb5b15060402098875e1b86d38a0c756). Option 3 desktop status layout and ten frequency labels visually checked. No corpus inference or provider calls. Reload the existing browser origin to retain its library.

## 2026-09-15 — Smooth low-frequency visualization

Owner reported squared shelves below 315 Hz, especially 40–80 Hz. Cause: 2048-point FFT spacing (~21.5–23.4 Hz) plus repeated floor/ceil peak-bin groups. Shared visualizer now uses 8192 points (~5.4–5.9 Hz), interpolates narrow log-frequency columns in dB, and retains wider-band peaks with continuous boundaries. Axis endpoints align with sampled column centers. Window length is now ~171–186 ms; 50 ms display cadence, dBFS scale, point size and history depth remain unchanged. This trades some transient sharpness for bass detail.

Validation: 38 tests pass, including bass interpolation, silence and peak preservation; 23 JS syntax checks and 19-file build verification pass. Manifest SHA-256 c976bfc4f59fd2cf642a3a44e90d4d40e9e335635baec8e5e804f75d7fedb3f4. No real-track listening/browser acceptance run for this revision. App status JSON and generated Markdown updated. No saved analysis or corpus changes.

## 2026-09-15 — Approximately 10 Hz visualization trial

Owner requested 10 Hz resolution. Changed shared live FFT from 8192 to 4096 samples: 10.77 Hz at 44.1 kHz or 11.72 Hz at 48 kHz (nearest practical power-of-two setting). Retained dB interpolation and continuous peak-band boundaries. Window now 85–93 ms. Supersedes the prior 5–6 Hz trial. App status and generated Markdown updated. 38 tests, 23 syntax checks and 19-file build verification pass; no real-track browser acceptance run. No saved analysis changes.

## 2026-09-15 — Restore bass resolution and enlarge dots

Owner rolled back the approximately 10 Hz trial and requested 50% larger dots. Shared FFT restored to 8192 samples (~5.4–5.9 Hz at common sample rates; 171–186 ms window). Interpolation retained. Point dimensions increased from 1.60× to 2.40× baseline across Isometric, Front, Mountain and Falling. History and amplitude span unchanged. App status JSON and generated Markdown updated. Validation: 38 tests, 23 syntax checks and 19-file build verification pass; no new listening/browser acceptance run. No saved analysis or corpus changes.

## 2026-09-15 — Ten-percent dot increase

Owner replaced the 50% dot enlargement with a 10% increase over the earlier 1.60× size. Shared point scale is now 1.76× baseline in all four views; 8192-point FFT (5–6 Hz) and interpolation remain unchanged. App status and generated Markdown updated. Validation: 23 syntax checks and 19-file production build verification pass. No new tests or browser acceptance run for this scalar-only adjustment.

## 2026-09-15 — Split FFT resolution and embedded track names

Owner requested 5–6 Hz below 350 Hz and approximately 20 Hz above, plus a title/artist audit of the currently loaded browser library. Shared visualization now uses parallel 8192/2048 FFTs, selecting at 350 Hz, retaining interpolation and 1.76× dots. Upper spacing is 21.5–23.4 Hz at common sample rates. No audio crossover/filter is applied.

Local imports and one-time existing-library refresh read bounded ID3v2.2/2.3/2.4 and ID3v1 tags, plus existing analysis metadata. Embedded title/artist/album supersede fallback display values with evidence; missing fields retain fallbacks. Other formats currently depend on analysis metadata. IDs, audio, playlist references and features are preserved. App status shows live title/artist/both/neither coverage. Snapshot and generated Markdown updated.

Validation: 41 tests, 25 syntax checks and 20-file production build verification pass, including UTF-8 tags, legacy tags, fallback/provenance and FFT crossover selection.

## 2026-09-15 — Restore dots without extra increment

Owner removed the recent 10% dot increase. All four views restore pointScale=1.60 (from 1.76), the prior size with zero additional increment. Split 8192/2048 FFT resolution at 350 Hz, interpolation and metadata display remain unchanged. App status and generated Markdown updated. Validation: 25 syntax checks and 20-file build verification pass. No new tests or browser acceptance run for this scalar-only adjustment.

## 2026-09-15 — Playful App status and V0 listening lab

Owner requested a more expressive status page and ten varied PlaylistIQ tests with commentary capture to close local V0 before cloud work. Status now uses staggered metrics, asymmetric cards, large typography, a numbered query flow and contrasting next steps, with compact transport and responsive stacking. Maintained snapshot remains the content source.

PlaylistIQ now includes ten loadable prompts and a persistent per-attempt notebook: exact prompt, candidate identities/hashes, full query/result/error, timing, verdict and notes. Repeated tests remain separate. Export provides a Download JSON link and copyable JSON fallback. See web-player/docs/V0_LISTENING_REVIEW.md for the suite, interpretation categories and proposed closure checklist. User listening/comments and interpretation are pending; V0 is not marked complete. Cloud is the subsequent milestone; no provider execution performed.

Validation: 42 tests, 27 syntax checks and production manifest verification pass. Browser checks confirm status content, mobile width 390 with no document overflow, prompt loading and JSON export fallback. No OpenAI test calls or user verdicts generated.

## 2026-09-15 — Shared compact banner and full-width status

Owner requested the Analysis banner across all other tabs except Your Library; the shared Radio compact banner now follows that rule, including individual playlists. Analysis moves the existing toolbar DOM between its title and Analyze Tracks action, restoring it on other routes. On narrow screens it wraps below the title/action. App Status removes the empty secondary header, uses all available width, and adds varied metric shapes, 4/8-column modules, model tiles and a wider query flow. Snapshot/Markdown refreshed.

Validation: 27 syntax checks and production build verification pass. Browser desktop Analysis title/controls/action align in one row; compact banner is 121px versus unchanged 202px Your Library banner. Status uses all 1240px available at a 1280px viewport; blank header is hidden. Status and Analysis have no document overflow at 390px; route switching restores the library toolbar. No playback, inference or cloud requests executed.

## 2026-09-17 — Library and Analysis filters / ordering

Owner authorized manual BPM, genre, key and additional filters plus both sort directions, with themed design discretion. Added a numbered modal filter sheet with BPM interval validation, searchable genre multi-selection (OR across the existing top six), harmonic key, analysis status and favorites. Different fields combine with AND; missing requested values are excluded. Live preview, active-filter count, clear/apply and empty-result recovery included. Existing search combines with the filters. Sorts cover date added, title, artist, duration, BPM, numeric Camelot key, top genre, LUFS and arousal; missing values stay last in both directions and ties are deterministic.

Filters and browse order are shared in memory by Library/Analysis for the current page session. They are not written to saved playlists or applied to PlaylistIQ/analysis processing. Play all and Shuffle use the displayed subset. No data/schema migration or source audio changes. App status and generated Markdown updated.

Validation: 45 tests, 29 syntax checks and production build verification pass. New tests cover inclusive bounds, combined filters, genre OR/top-six policy, status/favorites, failed-stage exclusion, numeric key ordering, descending BPM, unknown-last and nonmutation. Browser checks confirm BPM error, apply/active count, BPM order and shared Library/Analysis state. Desktop and 390px filter-sheet layouts checked; no document overflow at 390px. No inference or provider requests.

## 2026-09-19 — Iteration 1 integration checkpoint (in progress)

Intent compiler, MAEST-weighted ranking, genre alternatives/taxonomy, directional preferences and web/CLI/native clarification are implemented. Twenty listening prompts preserve P01–P10 and add P11–P20. Focused checks pass; initial live validation failures are preserved and corrected with explicit prompt examples. Final regression/browser checks and documentation remain in progress. See [implementation checkpoint](../prompt-to-playlist/docs/ITERATION_1.md).


## 2026-09-22 — Local DJ mix delivery

DJ mixes now renders saved/imported manual plans through the existing local DJ engine and provides progressive AAC playback, lossless/downloadable completion, cache reuse, seeking and cancellation. Owner explicitly authorized this implementation after research. See [implementation and evidence](../../docs/MIX_DELIVERY.md). 77 web tests, syntax/build checks, live HTTP integrity/cancellation/ranges and browser playback/seek pass; 390px document width is 390px. Human listening, remote hosting and automatic MixPlan generation remain separate. Existing library state stays on its original browser origin.


## 2026-09-25 — Quality-first estimator research and implementation

Quality-first non-genre research and the selected available specialists are delivered locally. The web default selects Music2Emo theme/VA, MusiCNN vocals, VGGish aggression and independent PaSST OpenMIC instrument evidence, retaining EffNet happy/sad/relaxed/danceability. SheetSage2 supplies selected key evidence. MAEST, MuQ and planner weights remain unchanged. Two authorized sources passed 8/8 new stages; retries execute zero stages. Richer nuanced-emotion prediction and listening superiority remain unresolved; do not present encoder-only releases or the same 56 tags as solving that objective.

[Implementation, two research reports, setup, model contracts and verification](../prompt-to-playlist/docs/TOP_ESTIMATORS_IMPLEMENTATION.md). Final validation: 502 Python tests, 83 web tests, 45 syntax modules, 28-file build, eight successful final audio stages and 26 exact fixed-query replays. No new provider calls or listener judgments. The new optional specialist stages and quality/openmic vocabulary identity preserve reference records and saved-profile replay.
