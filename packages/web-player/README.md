# Resonant web player

## 2026-10-02 — Shared-library web edition preview

Web edition runs on port 4174 with layout 3, 187 verified fully analyzed MP3s, a single mix with transition timestamps, and brief white guide cards. Local edition stays on 4173 with layouts 1 and 3. Owner-only APIs are blocked in web mode. A live PlaylistIQ request and main-player playback passed; 95 tests pass. Same private repository, separate edition/config/build; no cloud deployment or audio upload performed. [Architecture, catalog gate, tests and next launch steps](docs/WEB_EDITION.md).

## 2026-10-01 — M4A normalization and storage recovery

New uploads convert M4A to MP3 locally; Analysis includes a provisional bulk conversion button. Closed storage reconnects once, then pauses analysis on persistent failure. Originals are preserved; converted audio needs fresh analysis. 90 web tests pass. Chrome currently has zero persisted track rows after reload; recovery is unresolved, not completed. See [implementation and evidence](docs/MP3_IMPORT.md).

## 2026-10-01 — 120 character probes; audio embeddings reused

The replacement bank and all 120 text embeddings are ready. Analyze Tracks refreshes stale description scores from compatible cached audio vectors without audio inference. The current feature version is `selected-estimators-v3-character120`; the eleven estimators and playlist ranking remain unchanged. The new Musical character view groups results by dimension. Two cached-track matching tests passed with exact vector preservation; broader analysis remains a manual owner action. [Concepts, implementation, evidence and limits](../prompt-to-playlist/docs/CHARACTER_BANK_120.md). This supersedes earlier fixed-32/bundled-matching descriptions.

## 2026-10-01 — Selected estimators are the Analyze Tracks default

The owner requested one default pipeline with selected replacements, retained unreplaced features, added instruments, and both Music2Emo and previous EffNet moods. The web bridge now requires all eleven stages under `selected-estimators-v2`. Old DEAM/key/vocal results remain readable; those replaced estimators no longer execute in ordinary analysis. MusiCNN danceability stays an optional experiment because EffNet remains the selected head. [Implementation, safety behavior and verification](../prompt-to-playlist/docs/DEFAULT_ANALYSIS_PIPELINE.md). This supersedes earlier standard-bulk/optional-specialists descriptions. Whole-library and new-album analysis remains the owner’s next manual action.

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


Live spectrogram correction (2026-09-13): supersedes the static accent. Option 2 now renders actual playing local/demo audio as a perspective 3D dotted frequency-history surface, using Web Audio FFT and Canvas. Static SVG removed. Local mode only until provider CORS/audio routing is verified.

Spectrum accent (2026-09-13): Option 2 now has a faint static dotted spectrum below Add music, inspired by the supplied image. SVG only; no live audio analysis, animation, invented telemetry or dependencies. Hidden at widths <=700px; Option 1 preserved.

Navigation refinement (2026-09-13): top navigation now contains Your library and Playlists in both options. Playlists opens a contained directory with saved playlist links, track counts and Create playlist. Favorites/demo data and existing routes remain available; no playback/provider changes.

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


**0.1.1 — reference-led gray design:** locally bundled Geist Mono, light display
type, a compact masthead and ruled listening workspace. [Design](docs/DESIGN.md),
[verification](docs/VERIFICATION.md) and [staged checkpoint](docs/REDESIGN_PLAN.md).
The [fast cloud plan](../../docs/cloud-library/FAST_CLOUD_LAUNCH.md) favors
R2/Workers/D1/Access with stable connections for the private trial; setup remains later work.


A local listening application with a portable static build and a replaceable
cloud-library adapter. Hosting, storage, authentication and uploads are for
later service integration. No cloud service has been deployed.

Resonant's D058 product direction is larger than this local release: one DJ
workspace for manual and AI-assisted playlists, continuous playback of the
whole set sequence and an optional whole-playlist file download. The goal is to
remove the friction of jumping among local files, SoundCloud, Spotify and other
apps merely to hear one planned set, wherever official source capabilities
allow in-app playback.

## Run locally

Requires Node 22 or newer; no npm dependencies or install step.

```sh
cd projects/dj-collection-set-builder/packages/web-player
npm run dev
```

Open **http://127.0.0.1:4173**. On macOS, double-click
`Open Resonant Player.command` to start the same loopback server. Stop with
Ctrl+C. Use `npm run dev -- --port 4174` if the default port is occupied.
Saved browser data belongs to the exact origin/port, so use the same address.

```sh
npm run check
npm test
npm run build
npm run preview
```

Preview serves `dist/` on the same port; stop development preview first.
Run `node scripts/verify-preview.mjs` to check HTTP asset delivery and headers.

## Features and data

- Six clearly labeled generated ambient demos; fictional titles/artists.
- Add/drop local audio, saved as browser-local copies in IndexedDB. Original
  files are untouched. Imports probe playback metadata, not acoustic models.
- Search/sort, favorites, named playlists, playlist order, inspectable JSON
  export/download, track details and evidence provenance.
- Play/pause/seek, previous/next, repeat all/one, shuffle, volume/mute, play next,
  append/reorder/remove queue entries and clear queue. Navigation does not stop
  playback. Space toggles playback, arrows seek 5s, M mutes, / focuses search.
- Responsive desktop/mobile controls and optional browser Media Session actions.

Local audio, favorites/playlists and volume survive reload; the queue does not
autoplay or resume after reload. Browser storage is **not a backup**: private
mode, quota limits, clearing site data or changing origin may remove/hide it.
Each import creates a separate entry; filename/size/mtime is not content identity.
No hash-based deduplication is claimed. Keep original files separately.

Up to 500 files/batch and 512 MiB/file; unsupported/corrupt/oversized/quota failures
are reported. MP3/PCM WAV are practical initial targets; codecs vary by browser.
Embedded ID3/cover extraction, acoustic descriptors, crossfade, gapless playback,
normalization, upload management, AI and service workers are outside this release.
Unknown artists and musical descriptors remain unknown.

The current “Download” action exports playlist metadata as JSON; it does **not**
download audio. A future cloud service should add **Download playlist files**
to the playlist ellipsis / More options menu, package eligible tracks in order
with an M3U/JSON manifest, and identify tracks it cannot include. This secondary
placement keeps frequent Play/Edit/Add actions prominent. Connected-provider
playback never implies permission to download, copy or rehost that provider's
audio.

## Later deployment

Only deploy `dist/`, after service/hosting decisions. It has no private audio,
Python runtime, dependencies, credentials or vendor SDK. `build-manifest.json`
records SHA-256 for every shipped app file. Relative assets and hash navigation
support path-prefix hosting without SPA rewrites.

Default [config](public/config.json) is local. The HTTP adapter activates only
through explicit configuration and never silently substitutes demos for service
errors. Read [API.md](docs/API.md) and [DEPLOYMENT.md](docs/DEPLOYMENT.md).
HTTP playlists/favorites are session-only pending authenticated account scoping.

[AGENTS.md](AGENTS.md), [PLAN.md](PLAN.md), [WORK_LOG.md](WORK_LOG.md) and
[verification](docs/VERIFICATION.md) preserve stage/status/failure/continuation
evidence. Parent D054/E042 owns authorization/results. Python packages remain
independent.

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

The page source is web-player/public/app-status.json; builds generate docs/APP_STATUS.md. Relevant future changes must update this snapshot and the project logs. Implementation evidence: web-player/WORK_LOG.md.

## 2026-09-15 — Smooth low-frequency visualization

Owner reported squared shelves below 315 Hz, especially 40–80 Hz. Cause: 2048-point FFT spacing (~21.5–23.4 Hz) plus repeated floor/ceil peak-bin groups. Shared visualizer now uses 8192 points (~5.4–5.9 Hz), interpolates narrow log-frequency columns in dB, and retains wider-band peaks with continuous boundaries. Axis endpoints align with sampled column centers. Window length is now ~171–186 ms; 50 ms display cadence, dBFS scale, point size and history depth remain unchanged. This trades some transient sharpness for bass detail.

Verification and changed behavior are recorded in web-player/WORK_LOG.md and its maintained App status snapshot.

## V0 listening lab

PlaylistIQ now contains ten varied test prompts and a saved review notebook. Use prompt, Find tracks, listen, add a verdict and notes, then export review JSON. [Review protocol and all ten prompts](docs/V0_LISTENING_REVIEW.md). App status uses an asymmetric responsive dashboard while retaining the maintained JSON/Markdown content contract.

## Library filters and ordering

Your Library and Analysis share a Filter sheet with manual BPM range, searchable genres, key, analysis status and favorites. Apply filters to update the list; selected genres match any top-six label, other criteria combine. Order by offers nine fields with an adjacent ascending/descending arrow. Missing values sort last. Filters and ordering last for the current page session; playback controls use the displayed tracks. PlaylistIQ and saved playlists retain their own selection/order.


## 2026-09-22 — Local DJ mix delivery

DJ mixes now renders saved/imported manual plans through the existing local DJ engine and provides progressive AAC playback, lossless/downloadable completion, cache reuse, seeking and cancellation. Owner explicitly authorized this implementation after research. See [implementation and evidence](../../docs/MIX_DELIVERY.md). 77 web tests, syntax/build checks, live HTTP integrity/cancellation/ranges and browser playback/seek pass; 390px document width is 390px. Human listening, remote hosting and automatic MixPlan generation remain separate. Existing library state stays on its original browser origin.
