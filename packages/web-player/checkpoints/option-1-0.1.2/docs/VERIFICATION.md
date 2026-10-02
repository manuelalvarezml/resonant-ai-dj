# Current local verification — 0.1.1, 2026-09-12

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
