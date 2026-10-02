# Web player takeover

## 2026-10-02 — Shared-library web edition preview

Web edition runs on port 4174 with layout 3, 187 verified fully analyzed MP3s, a single mix with transition timestamps, and brief white guide cards. Local edition stays on 4173 with layouts 1 and 3. Owner-only APIs are blocked in web mode. A live PlaylistIQ request and main-player playback passed; 95 tests pass. Same private repository, separate edition/config/build; no cloud deployment or audio upload performed. [Architecture, catalog gate, tests and next launch steps](docs/WEB_EDITION.md).

## 2026-10-01 — Recovery scope expanded

Restore saved batch now includes nested test_music/new_albums and uncached audio: 255 unique originals found, 59 with saved analysis. The former 54-file limitation came from a cached-only three-folder scan. The owner restored 54; another manual run can add 201. No automatic import/inference was performed. 92 tests pass. [Evidence](docs/LIBRARY_RECOVERY.md).

## 2026-10-01 — M4A normalization and storage recovery

New uploads convert M4A to MP3 locally; Analysis includes a provisional bulk conversion button. Closed storage reconnects once, then pauses analysis on persistent failure. Originals are preserved; converted audio needs fresh analysis. 90 web tests pass. Chrome currently has zero persisted track rows after reload; recovery is unresolved, not completed. See [implementation and evidence](docs/MP3_IMPORT.md).

## 2026-10-01 — 120 character probes; audio embeddings reused

The replacement bank and all 120 text embeddings are ready. Analyze Tracks refreshes stale description scores from compatible cached audio vectors without audio inference. The current feature version is `selected-estimators-v3-character120`; the eleven estimators and playlist ranking remain unchanged. The new Musical character view groups results by dimension. Two cached-track matching tests passed with exact vector preservation; broader analysis remains a manual owner action. [Concepts, implementation, evidence and limits](../prompt-to-playlist/docs/CHARACTER_BANK_120.md). This supersedes earlier fixed-32/bundled-matching descriptions.

## 2026-10-01 — Selected estimators are the Analyze Tracks default

The owner requested one default pipeline with selected replacements, retained unreplaced features, added instruments, and both Music2Emo and previous EffNet moods. The web bridge now requires all eleven stages under `selected-estimators-v2`. Old DEAM/key/vocal results remain readable; those replaced estimators no longer execute in ordinary analysis. MusiCNN danceability stays an optional experiment because EffNet remains the selected head. [Implementation, safety behavior and verification](../prompt-to-playlist/docs/DEFAULT_ANALYSIS_PIPELINE.md). This supersedes earlier standard-bulk/optional-specialists descriptions. Whole-library and new-album analysis remains the owner’s next manual action.

## 2026-10-01 — Test music relocated; local server restarted

The owner moved the three existing test corpora into `test_music/` and created `test_music/new_albums/`. Runtime recovery and bounded smoke/attachment scripts now use the new parent; current README commands are updated. Historical analysis files retain their recorded paths and hashes. The DJ engine resolves a missing legacy corpus folder to its existing `test_music` location without changing archived evidence; existing folders always take precedence. Source-output protection includes the new music parent, and Git excludes the whole local music tree.

Server uses the existing `http://127.0.0.1:4173` origin. Models, profiles, weights and analysis behavior are unchanged. The owner will manually import new albums and launch analysis; the agent did not import or analyze music. Bulk Analyze Tracks remains the standard pipeline; Details → Upgrade selected specialists runs the newer selected models. `new_albums` is not silently included in Restore saved batch.

## 2026-09-25 — Quality-selected estimators implemented

Quality-first non-genre research and the selected available specialists are delivered locally. The web default selects Music2Emo theme/VA, MusiCNN vocals, VGGish aggression and independent PaSST OpenMIC instrument evidence, retaining EffNet happy/sad/relaxed/danceability. SheetSage2 supplies selected key evidence. MAEST, MuQ and planner weights remain unchanged. Two authorized sources passed 8/8 new stages; retries execute zero stages. Richer nuanced-emotion prediction and listening superiority remain unresolved; do not present encoder-only releases or the same 56 tags as solving that objective.

Read the [research, implementation, measured results and continuation](../prompt-to-playlist/docs/TOP_ESTIMATORS_IMPLEMENTATION.md). This checkpoint supersedes the older next-work and reference-default descriptions below. Broader corpus, cloud and source-preservation boundaries remain.

## 2026-09-25 — Selectable supervised feature estimators

Music2Emo (MERT-95M + BTC/chord/key + J_all, corrected mode) and MusiCNN danceability are implemented as optional direct-feature challengers. The specialist reference remains default; MAEST top-six, MuQ and ranking weights are preserved. Complete compatible catalog coverage is required per challenger; otherwise everyone retains the reference. Two authorized sources passed six matched-window stages and zero-inference retries. Final checks: 481 Python tests, 80 web tests, 45 JS syntax modules, 28-file build, 40 exact fixed-query replays and one final successful live replay. One prior live intent proposal was rejected; no new listening judgments or superiority claim.

Exactly two local cache records have both challengers. Original Chrome was observed at 109 unique tracks; its final updated display was not confirmed because native interaction was interrupted by active use. The new reload migration attaches richer same-hash optional caches to completed reference records. Isolated browser acceptance verified real values, retry, profile/scope, saved-result reopening, App Status and 390/320px controls. No batch/new-corpus inference, audio upload, cloud work, commit or format migration.

Read [research, commands, failures, coverage and continuation](../prompt-to-playlist/docs/SUPERVISED_ESTIMATORS.md). Historical sections/publication cutoffs below remain evidence for their original dates.


## 2026-09-22 — Local mix delivery current checkpoint

Owner-authorized research and implementation are complete locally: progressive mix playback, one-pass WAV/AAC rendering, headroom/peak checks, cache reuse and web controls for existing manual MixPlans. This supersedes the earlier rendering/planning-only hold for this scope. See [implementation, benchmark and limits](../../docs/MIX_DELIVERY.md). First-web-release listening and remote rollout acceptance remain open.

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


## 2026-09-17 — Library and Analysis filters / ordering

Owner authorized manual BPM, genre, key and additional filters plus both sort directions, with themed design discretion. Added a numbered modal filter sheet with BPM interval validation, searchable genre multi-selection (OR across the existing top six), harmonic key, analysis status and favorites. Different fields combine with AND; missing requested values are excluded. Live preview, active-filter count, clear/apply and empty-result recovery included. Existing search combines with the filters. Sorts cover date added, title, artist, duration, BPM, numeric Camelot key, top genre, LUFS and arousal; missing values stay last in both directions and ties are deterministic.

Filters and browse order are shared in memory by Library/Analysis for the current page session. They are not written to saved playlists or applied to PlaylistIQ/analysis processing. Play all and Shuffle use the displayed subset. No data/schema migration or source audio changes. App status and generated Markdown updated.

Validation: 45 tests, 29 syntax checks and production build verification pass. New tests cover inclusive bounds, combined filters, genre OR/top-six policy, status/favorites, failed-stage exclusion, numeric key ordering, descending BPM, unknown-last and nonmutation. Browser checks confirm BPM error, apply/active count, BPM order and shared Library/Analysis state. Desktop and 390px filter-sheet layouts checked; no document overflow at 390px. No inference or provider requests.


## 2026-09-15 — Shared compact banner and full-width status

Owner requested the Analysis banner across all other tabs except Your Library; the shared Radio compact banner now follows that rule, including individual playlists. Analysis moves the existing toolbar DOM between its title and Analyze Tracks action, restoring it on other routes. On narrow screens it wraps below the title/action. App Status removes the empty secondary header, uses all available width, and adds varied metric shapes, 4/8-column modules, model tiles and a wider query flow. Snapshot/Markdown refreshed.

Validation: 27 syntax checks and production build verification pass. Browser desktop Analysis title/controls/action align in one row; compact banner is 121px versus unchanged 202px Your Library banner. Status uses all 1240px available at a 1280px viewport; blank header is hidden. Status and Analysis have no document overflow at 390px; route switching restores the library toolbar. No playback, inference or cloud requests executed.


## 2026-09-15 — Playful App status and V0 listening lab

Owner requested a more expressive status page and ten varied PlaylistIQ tests with commentary capture to close local V0 before cloud work. Status now uses staggered metrics, asymmetric cards, large typography, a numbered query flow and contrasting next steps, with compact transport and responsive stacking. Maintained snapshot remains the content source.

PlaylistIQ now includes ten loadable prompts and a persistent per-attempt notebook: exact prompt, candidate identities/hashes, full query/result/error, timing, verdict and notes. Repeated tests remain separate. Export provides a Download JSON link and copyable JSON fallback. See web-player/docs/V0_LISTENING_REVIEW.md for the suite, interpretation categories and proposed closure checklist. User listening/comments and interpretation are pending; V0 is not marked complete. Cloud is the subsequent milestone; no provider execution performed.

Validation: 42 tests, 27 syntax checks and production manifest verification pass. Browser checks confirm status content, mobile width 390 with no document overflow, prompt loading and JSON export fallback. No OpenAI test calls or user verdicts generated.


## 2026-09-15 — Restore dots without extra increment

Owner removed the recent 10% dot increase. All four views restore pointScale=1.60 (from 1.76), the prior size with zero additional increment. Split 8192/2048 FFT resolution at 350 Hz, interpolation and metadata display remain unchanged. App status and generated Markdown updated. Validation: 25 syntax checks and 20-file build verification pass. No new tests or browser acceptance run for this scalar-only adjustment.


## 2026-09-15 — Split FFT resolution and embedded track names

Owner requested 5–6 Hz below 350 Hz and approximately 20 Hz above, plus a title/artist audit of the currently loaded browser library. Shared visualization now uses parallel 8192/2048 FFTs, selecting at 350 Hz, retaining interpolation and 1.76× dots. Upper spacing is 21.5–23.4 Hz at common sample rates. No audio crossover/filter is applied.

Local imports and one-time existing-library refresh read bounded ID3v2.2/2.3/2.4 and ID3v1 tags, plus existing analysis metadata. Embedded title/artist/album supersede fallback display values with evidence; missing fields retain fallbacks. Other formats currently depend on analysis metadata. IDs, audio, playlist references and features are preserved. App status shows live title/artist/both/neither coverage. Snapshot and generated Markdown updated.

Validation: 41 tests, 25 syntax checks and 20-file production build verification pass, including UTF-8 tags, legacy tags, fallback/provenance and FFT crossover selection.


## 2026-09-15 — Ten-percent dot increase

Owner replaced the 50% dot enlargement with a 10% increase over the earlier 1.60× size. Shared point scale is now 1.76× baseline in all four views; 8192-point FFT (5–6 Hz) and interpolation remain unchanged. App status and generated Markdown updated. Validation: 23 syntax checks and 19-file production build verification pass. No new tests or browser acceptance run for this scalar-only adjustment.


## 2026-09-15 — Restore bass resolution and enlarge dots

Owner rolled back the approximately 10 Hz trial and requested 50% larger dots. Shared FFT restored to 8192 samples (~5.4–5.9 Hz at common sample rates; 171–186 ms window). Interpolation retained. Point dimensions increased from 1.60× to 2.40× baseline across Isometric, Front, Mountain and Falling. History and amplitude span unchanged. App status JSON and generated Markdown updated. Validation: 38 tests, 23 syntax checks and 19-file build verification pass; no new listening/browser acceptance run. No saved analysis or corpus changes.


## 2026-09-15 — Approximately 10 Hz visualization trial

Owner requested 10 Hz resolution. Changed shared live FFT from 8192 to 4096 samples: 10.77 Hz at 44.1 kHz or 11.72 Hz at 48 kHz (nearest practical power-of-two setting). Retained dB interpolation and continuous peak-band boundaries. Window now 85–93 ms. Supersedes the prior 5–6 Hz trial. App status and generated Markdown updated. 38 tests, 23 syntax checks and 19-file build verification pass; no real-track browser acceptance run. No saved analysis changes.


## 2026-09-15 — Smooth low-frequency visualization

Owner reported squared shelves below 315 Hz, especially 40–80 Hz. Cause: 2048-point FFT spacing (~21.5–23.4 Hz) plus repeated floor/ceil peak-bin groups. Shared visualizer now uses 8192 points (~5.4–5.9 Hz), interpolates narrow log-frequency columns in dB, and retains wider-band peaks with continuous boundaries. Axis endpoints align with sampled column centers. Window length is now ~171–186 ms; 50 ms display cadence, dBFS scale, point size and history depth remain unchanged. This trades some transient sharpness for bass detail.


## 2026-09-15 — dBFS axes and maintained App status

Added App status navigation with live library counts and a maintained overview of capabilities, analysis models, prompt restructuring, deterministic matching, storage, limitations and next steps. Shared visualizations now use 11px axis labels, denser logarithmic Hz ticks and floating-point FFT magnitude from −90 to 0 dBFS. Removed artistic magnitude taper; the scale describes windowed FFT bins, not LUFS or a sample-peak meter. This supersedes the earlier relative-amplitude axis.

**Required maintenance:** When capabilities, models, prompt/query matching, storage, limits or next steps change, update [public/app-status.json](public/app-status.json). Run the player build to regenerate [docs/APP_STATUS.md](docs/APP_STATUS.md), and record the user steer, changes and verification in the corresponding plans and logs. The tab’s live counts remain separate from its maintained snapshot.


## 2026-09-15 — Analysis workspace and fresh-export repair

Analyze tracks and PlaylistIQ now sit in the top controls. Feature columns toggle in the track list; the Analysis tab uses the full width with sticky track names and headers, horizontal scrolling, genre scores, tempo/key/loudness/arousal, mood/danceability/vocal scores and missing-stage details. Option 2 uses compact transport in Analysis. PlaylistIQ is a themed page with analyzed-track count, prompt form and inline results/save action; the earlier technical introductory copy is removed.

Fresh MAEST export NameError fixed; persistent checkpoints and invalid-worker-output recovery added. See the player WORK_LOG and PlaylistIQ WEB_INTEGRATION for evidence and retry instructions.


## 2026-09-15 — MAEST top-six and local player integration

Owner-authorized `maest-top6-v1` now replaces legacy genre estimation: match the top six, display three expandable to six, retain all 519 scores, and apply no probability threshold or human review overrides. Historical outputs remain preserved. The low-priority board card `PIQ-GENRE-TOP6-REVISIT` is Later / could; further genre experimentation is not a launch blocker.

The local web player now provides **Analyze tracks** and **Create with PlaylistIQ**. Its loopback Node job service invokes the existing Python environment; analysis persists by source hash and in IndexedDB, and prompt results save into normal playable playlists. Restart the player server on the same origin/port to retain the browser library. This explicit integration authorization supersedes older local bridge/Python-edit holds; cloud deployment, remote audio processing and automatic MixPlans remain deferred.

See [integration contract](../prompt-to-playlist/docs/WEB_INTEGRATION.md).

Spectrogram motion update (2026-09-14): pause fall shortened to 2.8 seconds; Play starts fresh audio-driven points with a 1.6-second eased rise from below the canvas. Applies to all four modes.

Pause descent (2026-09-14): all four spectrogram modes now let retained points fall and fade for four seconds on pause/end, then clear and stop rendering. Resume cancels descent and starts fresh live history.

Falling spectrogram (2026-09-13): fourth view extends Mountain history from 48 to 62 planes (round(48×1.3)). Oldest 30% accelerate downward and fade smoothly into reserved lower space. First three projections retain 48 visible planes.

Spectrogram modes (2026-09-13): Isometric restores the first unpadded projection; Front retains zero elevation; Mountain adds reference-inspired dense grain and shaped audio history. Inline 16px buttons switch without resetting playback/history; preference saved locally.

Zero-elevation front view (2026-09-13): removes the remaining time-dependent vertical offset. Every history slice shares the same baseline and frequency positions; age changes opacity only. Supersedes the previous stacked frontal interpretation.

Frontal spectrogram (2026-09-13): rolled back the 10% axis padding. Live history now uses aligned frequency columns and constant amplitude scale, with vertical time offsets and fading instead of perspective skew or foreshortening.

Spectrogram axis padding (2026-09-13): both time and frequency have zero-height ground extending 10% of the original span at each end (120% total). Measured samples are unchanged; expanded surface fits the existing canvas.

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


**Product direction — D058 (2026-09-12):** Resonant is now planned as the
cohesive DJ workspace around this player: native/manual and PlaylistIQ-assisted
playlists, continuous in-app playback of a full set playlist and a rights-aware
whole-playlist file download. The download is a low-frequency playlist action
inside the ellipsis / More options menu, not a primary button. The current
0.1.1 player already creates/reorders playlists and exports JSON; cloud account
sync, cross-source playback and audio archive generation remain unimplemented
and unauthorized. Provider playback does not imply download permission.

**Current revision — D057/E045 (2026-09-12):** Player0.1.1 uses the requested
sustainit.space-inspired gray brutalist design and locally hosted Geist Mono.
All R2 stages complete; read [docs/REDESIGN_PLAN.md](docs/REDESIGN_PLAN.md),
[docs/VERIFICATION.md](docs/VERIFICATION.md), then WORK_LOG.
30 tests,13syntax modules,15HTTP checks and desktop/390/320 acceptance pass.
Build13files/227407bytes, SHA22e618b77c25de82b5fe0f3011e29fd702ff1c76662db7bcde4085f4debedaa7.
The [cloud launch plan](../../docs/cloud-library/FAST_CLOUD_LAUNCH.md) recommends
R2/Workers/D1/Access for private1→3→10 with stable connections; no execution
approved. Provider/budget/scope acceptance then a revised R2 packet is next.
This task leaves its production preview on4175 running for review;4173 was
already occupied and untouched. Earlier baseline below remains0.1.0 evidence.

Read `../../AGENTS.md` and `../../docs/cloud-library/AGENTS.md`, then this file.
This package is the independent browser player for Resonant. Do not infer
status from chat. `PLAN.md` owns staged completion and `WORK_LOG.md` owns the
append-only implementation/verification trail.

## Authorization — D054, 2026-09-12

User explicitly requests a complete local web player ready for later deployment
once hosting/storage/services are resolved. This supersedes the blanket local
player build hold in D042/D043/D045; it does not choose a provider or authorize
deployment, accounts, source uploads, remote audio processing, model requests,
automatic MixPlans, rendering or commits. Existing corpus rules still apply.
The follow-up explicitly requests stages and frequent continuation checkpoints
so another chat can resume after token/usage limits.

## Current checkpoint — all five local build stages complete

- Package 0.1.0 implements browser-local imports/persistence, labeled generated
  demos, library search/sort, playlists/favorites/JSON export, editable queue,
  transport, evidence details, responsive UI and a future HTTP service adapter.
- Final tests: 30/30 pass in 130.086583 ms; 13 JS modules syntax checked;
  12 production HTTP checks pass. Exact static build: ten files, 88,376 bytes
  plus manifest. See docs/verification.json for SHA-256 identity.
- Browser: native generated audio play/pause/12s seek/next; generated WAV import
  and play after reload; corrupt fixture rejection; preferences and playlist
  persistence/order; queue order; M shortcut; empty search; desktop and 390/320px
  layouts. No final warning/error console logs.
- Export JSON payload/order/privacy and download anchor verified. Actual filesystem
  download completion was not observed by the browser tool; copyable JSON is
  provided. Real Safari/Firefox/mobile hardware, 200% text, scale/quota/eviction
  and provider range/auth/CORS/expiry remain untested; read VERIFICATION.md.
- No original corpus access, acoustic analysis, uploads, provider accounts,
  credentials, remote services, model requests, renders, deployment or commits.
- Production preview was verified at http://127.0.0.1:4173; do not assume a
  retained terminal session survives into the next task. Launcher/commands below
  are authoritative. Keep the same origin/port to reuse browser-local data.
- Shared documentation validated: 58 sources, 94 relative links, registry IDs,
  original unrun cloud protocols, unchanged readiness/cost invariants; zero errors.
  Git diff whitespace checks passed. Unrelated concurrent work was preserved.

## Continue next

1. To use/review: `npm run dev` in this package, then open the printed URL.
   macOS launcher: `Open Resonant Player.command`. No install required (Node ≥22).
2. To inspect release: `npm run check && npm test && npm run build`, then
   `node scripts/verify-build.mjs`. `npm run preview` serves dist; use
   `node scripts/verify-preview.mjs` to check it. Stop dev before preview (same port).
3. The next implementation boundary is chosen hosting/auth/storage/catalog and
   playback services. Read docs/API.md, docs/DEPLOYMENT.md and cloud D055 owner
   packet; obtain any missing actual service execution authority before doing
   external work. Current request deliberately deferred deployment/services.
4. Connect using explicit HTTP config only after server contracts/auth/CSP exist.
   HTTP collection preferences remain session-only until account scoping/sync.
5. Update PLAN/AGENTS/WORK_LOG and parent records for any subsequent work. Do not
   repeat the already completed local build or re-run music analysis for context.
6. For the D058 service slice, keep playlist-file download distinct from JSON
   export and rendered mixes. Preflight eligible/omitted items, ordered count,
   total bytes and expiry; use only owned or download-authorized audio.

## Ownership and integration

Root owns package edits. Research subagent reviewed contracts/source and
reproduced state defects without writing files. Player records: D054/E042 and
cloud CD017/CE015/T028/EX008/F010. The parallel readiness task owns D055/E043
and CD014–CD016/CE010–CE014/T027. Do not duplicate these IDs; re-read shared
files before editing. Existing cloud provider gates remain unpassed. Do not
implement a speculative backend, absorb PlaylistIQ, or modify Python packages.

## Data contract boundaries

Local mode uses IndexedDB for selected File blobs and track metadata. Favorites,
playlists and volume use namespaced localStorage. Browser storage is not a
backup. Original files are untouched. Local imports probe playback metadata
only, not audio analysis. HTTP preferences are session-only, not stored across
accounts. Demo titles/artists are fictional and marked as such.

HTTP mode is an adapter for a future same-origin authenticated API. It reads
versioned catalog pages and requests expiring playback sessions. No server is
implemented. Playback capabilities live only in memory; no credentials or
object keys appear in configuration. Cloud source attributes are estimates or
unknown according to supplied evidence, never fabricated from titles/BPM.

## Required checkpoint discipline

After every stage and meaningful failure: update PLAN, this takeover and
WORK_LOG. Keep details append-only; correct summary state explicitly. Before
ending, record checks run, unresolved failures, changed files and next commands.
Never claim unrun tests, cloud compatibility or browser/device coverage.

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

## 2026-09-19 — Iteration 1 integration checkpoint (in progress)

Intent compiler, MAEST-weighted ranking, genre alternatives/taxonomy, directional preferences and web/CLI/native clarification are implemented. Twenty listening prompts preserve P01–P10 and add P11–P20. Focused checks pass; initial live validation failures are preserved and corrected with explicit prompt examples. Final regression/browser checks and documentation remain in progress. See [implementation checkpoint](../prompt-to-playlist/docs/ITERATION_1.md).


## 2026-09-22 — Local DJ mix delivery

DJ mixes now renders saved/imported manual plans through the existing local DJ engine and provides progressive AAC playback, lossless/downloadable completion, cache reuse, seeking and cancellation. Owner explicitly authorized this implementation after research. See [implementation and evidence](../../docs/MIX_DELIVERY.md). 77 web tests, syntax/build checks, live HTTP integrity/cancellation/ranges and browser playback/seek pass; 390px document width is 390px. Human listening, remote hosting and automatic MixPlan generation remain separate. Existing library state stays on its original browser origin.
