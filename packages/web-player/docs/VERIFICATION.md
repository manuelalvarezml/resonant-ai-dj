# Current local verification — 0.1.1, 2026-09-12

**0.2.1 — D062/E050:** Always-visible Option1/Option2 header buttons;
Radio is predominantly black/dark gray. Live switching preserves generated
playback; desktop/390/320 checks pass. Library information and exact0.1.2 snapshot
retained.13syntax/15HTTP checks pass; no provider scope changes in this revision.


## Current0.2.0 — D060/E049

14files246439bytes, manifest
`2c37e5d74a7f56d7abf224f3a815e75a482c8c71d5ea5fc6ec6379414612fa32`.
30tests/13syntax modules/15HTTP checks pass; Radio entry and stylesheet return200.
34hashes preserve exact0.1.2. Current verification.json records this release;
verification-0.1.2.json preserves prior evidence. No browser QA performed for
Radio/switching (current Sites skill requires explicit request). No source audio.


## Current0.1.2 — D059/E048, 2026-09-13

30tests/13syntax modules/15HTTP checks pass.13files232122bytes; manifest
`11762b548184b32e686c498c67956bd21f82e17475c17d5f130c00565d219291`.
Visible text16px minimum; track titles18px. Desktop/mobile list scrolling leaves
page scroll at0 (list moves161px/116px respectively).320×740 list viewport133px;
390×844 viewport237px, page widths match. Six-track shuffle plays generated
audio; filter-to-orbit queues only Slow orbit; empty results disable Shuffle.
Pause and Library information verified. Final viewport restored. Prior import,
favorites/persistence and export evidence below was not rerun for this change.
Current JSON: verification.json; prior exact release: verification-0.1.1.json.
Only generated demo audio used; no source corpus, hosting or real mobile hardware.


D057 / E045 / EX009. The reference-led gray redesign is complete. No cloud
execution or new source-corpus evidence follows from this local verification.

| Check | Observed |
|---|---|
| Syntax/config | 13 modules pass; release remains local mode |
| Existing regression suite | 30 pass / 0 fail, 135.965458 ms; playback/adapter logic unchanged |
| Exact build | 13 files, 227,407 bytes plus manifest; fonts/OFL included |
| Manifest SHA-256 | `22e618b77c25de82b5fe0f3011e29fd702ff1c76662db7bcde4085f4debedaa7` |
| Artifact audit | Hashes/imports/CSS font references/license and private-material checks pass |
| Production HTTP | 15 checks pass, including both font MIME responses and license |
| Viewports | 1280 desktop, 390×844 and320×740; final document widths1280/390/320 |
| Playback | Actual generated24s demo plays and pauses; keyboard seek moves to0.2s while paused; next selection works |
| Collection interactions | Search filters six→one; favorite toggles; playlist created, track added and persisted after reload; dialogs/queue usable |

Desktop heading measured56.32px/weight200/Geist Mono. Fonts are self-hosted;
regular font served as font/ttf,71160bytes. Initial desktop demo banner delayed
track rows; removed it. Mobile title placement and320px nav overflow repaired.
The final desktop first row fits above the fixed player. Viewport override
reset after checks. No real mobile hardware or alternate browser engine tested.

Current JSON is [verification.json](verification.json). Original full local-import,
corrupt-file and export evidence remains below and in
[verification-0.1.0.json](verification-0.1.0.json); those workflows were not rerun
in this visual revision. Existing filesystem-download and provider limitations
remain. Browser fixtures created on this preview origin: one demo-only playlist
“Concrete sessions” and one demo favorite; no original audio.

Preview for this task uses127.0.0.1:4175 because4173 was occupied. No process on
4173 was changed. The4175 production preview is left running for user review;
restart with `npm run preview -- --port 4175` if it stops. This is not hosting.

---

# Preserved 0.1.0 verification — 2026-09-12

Package 0.1.0, decision D054, experiment E042 / local EX008. Generated audio
only. No provider, source-corpus, model, analysis or rendering experiment.

## Automated and artifact checks

| Check | Observed result |
|---|---|
| Node environment | v24.2.0, npm 11.3.0 on macOS |
| Syntax/config | 13 JavaScript modules passed; checked-in mode local |
| Unit/regression tests | 30 passed, 0 failed, 130.086583 ms final run |
| Production artifact | 10 static app files, 88,376 bytes plus build manifest |
| Manifest | `ebbcb2d8d2ff29ab5d122441cea1b193742f3e5ccd17dd4f799ecece2935c3ac` SHA-256 |
| Build audit | Exact file membership/hash/import references passed; only HTML/CSS/JS/JSON/SVG, no private audio/paths/credentials |
| Production HTTP preview | 12 checks passed: assets, content types, security headers, private-file denial, unsupported method |

Tests exercise selection races, late callbacks/clear, pause during loading,
paused current removal, stale seek reset, duplicate queue occurrences, ordering,
repeat/shuffle/end, bounded capability recovery and later reset, expired paused
seek, blocked-play retry, safe API errors, catalog pagination/revision/IDs,
unsafe URL rejection, exact source identity, unknown evidence, malformed stored
preferences and export privacy. Audio transport tests use an EventTarget fake;
they do not replace browser/provider verification.

## Browser observations

Codex in-app browser, desktop and viewport overrides (not actual mobile hardware):

- Full desktop app inspected at 1280×720 and 1280×800; readable track controls,
  persistent footer/queue. Mobile inspected at 390×844 and checked at 320×740.
  Final document width equals viewport at 390 and 320; navigation intentionally
  scrolls horizontally when narrow. Queue artwork size and topbar overflow fixed.
- Native demo playback had duration 24s, readyState 4, paused=false; pause, seek
  to 12s, next-track selection and final production-build play/pause passed.
- Generated 32s WAV imported and played after reload. Deliberately corrupt WAV
  rejected with a per-file decoder error: 1 saved / 1 failed. Files were generated
  under `/tmp/resonant-player-qa`; original music folders never selected.
- Favorites and named playlist survived reload. Add-to-playlist, track order,
  queue order/current identity, empty search/clear and M mute shortcut verified.
- Export preview inspected: correct ordered IDs/public fields, no audio/URLs/
  private paths; real anchor `download=resonant-playlist.json` verified. The
  browser tool's download-event wait timed out on the initial automatic export.
  Actual filesystem download completion remains unverified; copyable JSON is
  available directly as a tested fallback. Do not call this a downloaded file.
- Final production preview reported no browser warning/error console entries.

## Failures and fixes

Full trail in WORK_LOG W003–W006. Initial dev source assets returned 404 because
directory trailing slash broke a containment test; fixed normalized root and
added HTTP checks. Independent review reproduced four playback/keyboard state
bugs and an HTTP cross-account preference risk; patched and tested. Mobile
topbar overflow and artwork sizing fixed. CUA selector ambiguity/timeouts are
recorded separately from application failures. A docs patch initially attempted
delete/add of the same path and was rejected atomically; corrected to update.

## Remaining coverage

No real MP3/FLAC/AIFF library import, Safari/Firefox/device tests, iOS volume/
background behavior, browser eviction/quota pressure, 500-file batch performance,
200% text enlargement, provider ranges/expiry/CORS/auth/multi-tenant/logout tests,
actual deployment or cloud upload performed. Local generated playback is not a
cloud evidence gate. Backend auth and HTTP collection sync remain intentionally
unimplemented. Test removal/clear boundaries are automated; no original audio
or user-authored playlists were deleted in browser QA. Follow DEPLOYMENT.md.

### Navigation refinement — 2026-09-13

13 syntax modules, 30 tests and 14-file build validation pass. Current build is 249371 bytes; manifest SHA-256 e3e827800797287df00e45149916a144eb2446c6f8d2a2b4dd1dc10a4c5c291c. Browser/HTTP navigation acceptance not rerun; prior visual evidence is historical.

### Spectrum accent — 2026-09-13

13 syntax modules and final 15-file build integrity check pass (346852 bytes). Desktop 1280×720 preview inspected; static decorative SVG loads beneath Add music. Narrow hiding inspected in CSS only. Unit tests not rerun; previous navigation suite remains historical.

### Live spectrogram correction — 2026-09-13

Static visual is superseded by audio-driven Canvas FFT history. 14 syntax modules, 30 tests and 15-file build pass; 253708 bytes, SHA f4977d8e9deccd04d813fc486c804ce51644b6f600228d2ad1500436906286f9. Desktop generated playback changing surface, pause freeze and front switching inspected. Remote CORS, real devices and human audibility not tested.

### Axis padding — 2026-09-13

Projection-only patch: 14 syntax modules and build integrity pass. 15 files / 254283 bytes; SHA 4b7f1b78483d634ebbd355758a365dd86357104c3a1d20c26cf2e7a8de2fc4d4. No new browser or unit-test run; prior live playback evidence is historical.

### Frontal projection — 2026-09-13

Padding reverted; frontal projection implemented. 14 syntax modules/build integrity pass: 15 files, 253664 bytes, SHA 9c0f2c47b846e6aaeb1aec923065a04228c6620fd93d5f4268cbe05d49ddb96f. Browser and unit tests not rerun.

### Zero-elevation correction — 2026-09-13

14 syntax modules and build integrity pass: 15 files / 253649 bytes, SHA 563ff6d082d09b39cb43932a18474becea77ef8cab07899c0ef99f69226db044. Projection source verified: time affects opacity only. Browser/unit tests not rerun.

### Spectrogram modes — 2026-09-13

14 syntax modules and final build integrity pass (15 files / 256388 bytes, SHA cabdf19e2754b9dd16d52d5693a53015e5147699a85a5727c972fbf29c78324f). Desktop mode switching during generated playback inspected before final spacing/quiet-point refinement; final narrow reload confirms responsive hiding. No new unit/device tests.

### Falling mode — 2026-09-13

14 syntax modules / build integrity pass: 15 files, 256836 bytes, SHA 683f303d8c5bb66591792978b3914a1a96e1c9c4e60b67bbaedbc7abb431eddf. 62-plane history and fall/fade bounds inspected in source. Browser/unit tests not rerun.

### Pause descent — 2026-09-14

14 syntax modules, 30 tests and build integrity pass: 15 files, 257510 bytes, SHA 4f88c34d7c1e7b7ff53dfa52c3fcfb7573721814af305671eda8eb1318832150. Source lifecycle checked; browser visual acceptance not rerun.

### Fall/rise timing — 2026-09-14

14 syntax modules and build integrity pass: 15 files / 257763 bytes; SHA 16d1f77629013b3a78d9f12421ff4f90e66531ba4036cb900b77cc96b41612db. Animation source reviewed; no new browser or unit-test run.

## 2026-09-19 — PlaylistIQ Iteration 1 delivered

Python 0.4.0 / player 0.3.0 now integrate `playlist-intent-v1.3` (configured low reasoning), `intent-compiler-v1.1`, `maest-intent-v1` ranking and `discogs-parents-v1`. Required genres use MAEST support; creative prompts use directional soft priorities. Genre OR/family matching, original-request clarification, per-track contributions and twenty-prompt review evidence are available. New result/catalog/translation/run writes use schema 0.2.0 and read historical 0.1.0.

422 Python tests and 50 web tests pass. Final compiler replay passes all 20 intent/constraint checks; live revision failures are preserved, and final optional/HTTP checks pass. Human listening acceptance remains pending. No new audio analysis or cloud work; YAML is still a consideration task.

See [implementation, prompt, contracts and verification](../../prompt-to-playlist/docs/ITERATION_1.md). This current checkpoint supersedes older descriptions of v3-only translation, flat genre ties and missing parent matching; dated older sections remain historical evidence.

