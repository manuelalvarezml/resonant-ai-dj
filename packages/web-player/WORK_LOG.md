# Web player work log

Append-only progress, decisions, failures and questions. Current stage summaries
live in PLAN/AGENTS. D054 authorizes this build; E042 will record actual checks.

## 2026-09-12 — W001 — Scope and initial implementation

Read project takeover, PlaylistIQ handoff/README and cloud takeover, status,
architecture, contracts and maintenance. Read Sites building portable setup/
preview instructions; no registration because user defers deployment.
Research agent independently reviewed player/service requirements and priority
tests; no files changed by agent. User request supersedes local-player hold
only. Existing research/API contracts remain proposals outside this package.

Chose isolated zero-framework ES module package with native audio, IndexedDB
local audio, browser-only playlist preferences, generated demo WAVs and a
replaceable HTTP adapter. Authored the initial modules and HTML/config/icon.
All source is unverified at this checkpoint; CSS/scripts/tests still pending.

Observed environment: Node 24.2.0, npm 11.3.0. Initial `git status` from workspace
parent failed because Git lives inside `projects/dj-collection-set-builder`;
corrected the working directory and obtained a clean initial repository status.
Portable profile detector returned `configured:false`, preserving custom static
project. No dependencies/network services installed or created.

Read current MDN docs for HTMLMediaElement.play, Media Session, IndexedDB and
HTTP Range semantics on 2026-09-12. These justify handling rejected play promises,
optional media controls, browser storage and later provider-range testing; they
do not constitute measured browser/provider compatibility.

## 2026-09-12 — W002 — Explicit staged continuation requirement

User asks to work by stages, prepare for token shortage and make continuation
in another chat possible. Added PLAN.md and compact AGENTS.md immediately,
separating authored source from verified functionality and naming exact next
steps. Remaining stage 2 work: CSS and runnable static development scaffolding.
Open implementation-review concerns: race/queue behavior, expiration recovery,
metadata timeouts, browser state persistence and accessibility focus behavior.
These are unverified risks, not yet observed failures.

## 2026-09-12 — W003 — Stages 2–3 and first browser failure repaired

Added responsive charcoal/lime UI, native accessible controls, static build,
loopback development/production server, syntax checker and 29 tests. Actual run:
29/29 passed in 126.393 ms; syntax passed for 11 modules. Build emitted ten
static app files plus a SHA-256 manifest with no audio. Later files/checks may
change these counts; this is the first passing run.

Independent source review reproduced five issues: paused queue removal started
playback; stale pending seek survived queue clear; keyboard M dereferenced a
missing dataset; renewal budget never reset after recovered playback; and HTTP
preferences persisted across accounts without a server namespace. Fixed all:
preserve queue playback intent; clear pending seek; tolerate missing dataset;
reset renewal budget only after >1s actual resumed progress; keep HTTP preferences
session-only until a server-authenticated storage namespace exists. Tests cover
the state boundaries; browser keyboard confirmation remains stage 4.

Initial browser preview showed only the boot text. Actual HTTP asset checks
returned 404 for JS/CSS: root derived from a directory URL retained a trailing
slash and `base + path.sep` required a doubled separator. Normalize root with
`path.resolve`; restart and reload. New preview checker passes 12 checks for
assets, headers, private file denial and method restrictions. Complete desktop
DOM and initial visual state then appeared. This was a real failure, resolved.

Stage 4 now tests actual browser interaction, generated-file import, persistence
and responsive layout. The CSS's first viewport is denser than desirable;
compact the demo collection card to expose tracks sooner and audit label sizes.

## 2026-09-12 — W004 — Browser acceptance and patches

Observed native browser audio with generated fixtures: demo play/pause, 12-second
seek, next track, 24-second decoded duration/readyState 4. Favorite and named
playlist persisted after reload. Importing generated `Playback fixture.wav`
(32 seconds) plus a deliberately corrupt WAV saved exactly one track and reported
one decoder failure. The saved audio played after reloading. No corpus files
were selected. The generated files live only under `/tmp/resonant-player-qa`.

Confirmed search-empty state, clear search, M keyboard mute, queue reordering
with current identity preserved, playlist addition/order. An initial CUA selector
used aria-label text as row text; corrected locator. Another matched both queue
and playlist reorder buttons; scoped it to the dialog. These were test-tool
locator failures, not app failures. One read-only audio evaluation timed out;
fresh DOM showed playback advancing and follow-up reload/play passed.

Mobile inspection at 390×844 had no horizontal overflow, but the demo card pushed
tracks down and queue art inherited the small artwork width. Compact mobile demo
strip and explicit `.artwork.now-art` sizing fix those. At 320×740 an actual
21-pixel document overflow came from topbar metadata/actions; hide the secondary
mode badge at that width and truncate breadcrumbs. Reverification follows.

Export initially showed success and no console errors, but CUA's download-event
wait timed out. Added an inspectable read-only JSON preview with a real Download
JSON link, so the payload is usable independently of browser download tooling.
Do not call the missing tool event proof of successful filesystem download.

## 2026-09-12 — W005 — Parallel task collision and scope correction

Another user task is preparing cloud readiness in the same repository. It keeps
its work as D055/E043 and reports CD014–CD016/CE010–CE014/T027 already allocated.
This player keeps D054/E042 and will use CD017/CE015/T028/EX008. Re-read shared
files before small changes; do not overwrite its artifacts or statuses.
Optional cross-task status reply was rejected by automatic approval review
because sharing project details with that task was not authorized. No reply
was sent, and no alternate transmission attempted. Local work is unaffected.

Correction to W001: its phrase “clean initial repository status” is not reliable
evidence; the initial output was truncated and current status includes substantial
pre-existing/parallel modifications. Preserve all unrelated edits; this task
makes no claim that the worktree was clean or that its diff owns every change.

## 2026-09-12 — W006 — Final application and release acceptance

320px overflow recheck passed exactly 320px document/viewport width (390px also
passed). Playlist JSON preview exposed the expected ordered two-track payload
and safe public references; download anchor filename verified. Actual filesystem
download remains an explicit browser-tool coverage limit. Added export privacy
regression, real request timeout, focus restoration for rerendered controls,
dialog URL cleanup, and clarified session-only HTTP preference copy.

Final automated run: 30/30 tests, zero failures, 130.086583 ms; 13 module syntax
checks; build audit validates ten shipped files, 88,376 bytes plus manifest.
Manifest SHA-256 is recorded in docs/verification.json. Switched the retained
server from dev to production dist on the same loopback port; 12 HTTP checks and
actual production-browser play/pause passed with no warning/error console logs.
Viewport override reset. No source audio was touched, no credentials/services
used, and no commits or remote deployment occurred.

Added README, macOS launcher, implemented consumer-contract documentation,
deployment/security-header/service acceptance handoff, readable/machine-readable
verification, and staged continuation records. A first documentation patch was
rejected because delete/add targeted the same file; it made no changes, and the
corrected update/add patch succeeded. All actual application/browser failures
listed above are repaired; device/provider coverage remains open, not failed.

## 2026-09-12 — W007 — Documentation reconciliation and closeout

All five local stages marked complete. Parent AGENTS/README/PLAN/engine plan,
schemas/corpus/changelog, D054/E042, workspace AGENTS/PROJECTS and relevant cloud
documents now point to the finished package. Cloud CD017/CE015/T028/EX008/F010
records were appended without changing D055 readiness work or any provider gate.
Shared validator passed 58 sources/94 links, unique IDs, dependencies and preserved
readiness/cost invariants; player Markdown links (7) and verification JSON passed.
`git diff --check` passed. Final build re-audit matched the recorded manifest;
the macOS launcher passed `zsh -n`. No commits made.

Production preview was stopped after acceptance; use the launcher or `npm run dev`
to restart. A rendered browser tab may remain, but its URL needs the server on
reload. Next substantive work is the deferred service integration described in
docs/DEPLOYMENT.md, not another local build or corpus run.

## 2026-09-12 — W008 — Reference and gray redesign checkpoint

R2 stages A/B implemented, verification in progress. Inspected sustainit.space
in the browser: Geist Mono styles observed, Martian Mono also in the font CSS;
light oversized text, small mono utility text, thin rules and roomy composition.
Translated into a gray masthead/listening rail, square controls, subdued abstract
covers and light Geist Mono headings. Retained app actions, local and HTTP logic.
Downloaded unmodified Google Fonts Geist Mono 200/400 TTFs and OFL license;
font requests stay local. Initial sandbox DNS lookup failed; authorized network
retry succeeded. First preview port 4173 was occupied; left it untouched and
started this task's production preview at 4175 (session 62023).

Version 0.1.1; build now reads package version rather than hardcoding 0.1.0.
Serve/build validation admits bundled fonts/license. Syntax 13/13 and tests30/30
passed; first R2 build13 files229021bytes, manifest85e8e3aa95f0942ade1d564620d4c46952939ae210f53213fa259b2fff7bb2a5.
Do not treat this first build as final until browser acceptance and final hash.
Remaining: desktop/mobile layout and playback, quick cloud plan, updated handoff.

## 2026-09-12 — W009 — Responsive refinement and cloud direction

Desktop first pass left rows below the footer; reduced the duplicate demo hero
to a narrow provenance/action strip and hid that strip on mobile (generated
status remains in the description/player). Mobile Add music originally forced
the heading to three lines; moved it beside the eyebrow, giving the title full
width. Desktop1280 and mobile390 now show a track before scrolling. Fixed text
merging where hidden BR nodes removed word spacing. These are local design
iterations, not cloud experiments. Browser automation needed dialog-scoped
Create playlist and responsive navigation labels; no application exception.

Actual native demo duration24s/readyState4/paused=false, pause/keyboard seek/next,
playlist creation and persistence after reload, favorite, track options, adding
to playlist, search and mobile queue opening passed. Mobile390 document width390,
footer height164. Still finish320px/desktop final artifact before closeout.
Cloud direction: recommend R2+Workers Static Assets/API+D1+Access for current
private1→3→10 scope. Replaces B2 priority for low migration/connection effort;
not owner provider acceptance or setup. Preserve old B2 spike envelope/history.

## 2026-09-12 — W010 — Final design, plan and durable evidence

Removed the demo hero/action strip entirely after final desktop review still
showed only part of the first row. Description/player retain truthful generated
audio labels. Final first row ends above transport;1280/390/320 document widths
match viewports.320px overflow was caused by redundant nav icons; hiding them
at that breakpoint repaired it. Font preload reduces initial fallback swapping;
favicon is now square/gray. Final native24s demo play/pause and paused keyboard
seek pass. Viewport restored. Created only a demo favorite/Concrete sessions
playlist on preview origin4175. No source music imported this revision.

Final0.1.1 build13files227407bytes, SHA22e618b77c25de82b5fe0f3011e29fd702ff1c76662db7bcde4085f4debedaa7.
13syntax modules,30tests (135.965458ms),15HTTP checks pass; font references and
OFL now included in artifact audit.0.1.0 JSON archived as verification-0.1.0.json
and EX008 points to it; current verification.json is EX009/E045. Import/export
coverage is preserved baseline evidence, not falsely reported as a fresh rerun.

FAST_CLOUD_LAUNCH.md complete: R2/Workers/D1/Access recommendation, stable
connections/IDs, automated future ingestion/deployment, growth/auth/database
tradeoffs and5USD cap. CD018 is an accepted document/recommendation, not owner
provider acceptance. D057/E045 used because a parallel foundations-report task
had already reserved D056/E044. Six new primary sources S059–S064; current
price/limit pages rechecked. Previous GitHub geist-font/LICENSE open failed;
Google Fonts canonical OFL/asset source succeeded. No product failure follows.

Docs helper typo Path.write failed before Markdown changes; corrected. Shared
validator then caught research_revision1.2 versus current registers1.3. Updated
only owner-spike-plan.json research_revision to1.3; its B2 provider, envelope,
protocol revision and unapproved state remain unchanged. Entries explicitly
mark B2 history and require a revised R2 protocol before any trial. Final
validation result to be recorded in W011. Preview4175 remains running for review,
4173 untouched. No commit, account, deployment, spending or corpus work.

## 2026-09-12 — W011 — Reconciled closeout

Cloud validator passes64sources/108relative links/3sheets/3independent economics
cases,0errors;20existing readiness mutation tests pass. Player MD23links and
current verification/build manifest match; git diff --check passes. Final HTTP
15/15 checks pass after the final banner removal. No further runtime changes.

A parallel documentation task added a D057 summary (same design/cloud decision)
and D058 unified-product direction between shared-file reads. Validator caught
the resulting duplicate D057 numbered heading; preserved both texts by naming
our detailed entry an implementation addendum, keeping D057 canonical and
D058 untouched. No semantic decision or historical event was deleted.

A–D complete. Next service work starts FAST_CLOUD_LAUNCH.md and requires the
provider/budget/scope acceptance and revised R2 trial packet documented there.
No pending question or approval was sent for this completed design/planning task.
No new user-owned task, agent, automation, remote resource or commit created.
Production preview4175 remains running for local review; restart it if needed.

## 2026-09-12 — W012 — Unified playlist product direction

D058 does not alter the verified0.1.1 artifact. It records this player as the
listening surface for a broader Resonant DJ workspace: build/edit playlists,
play the full sequence in-app, and occasionally download eligible playlist
files. The future download is placed in the playlist ellipsis menu, with
rights/availability/bytes/omission preflight; current Download remains JSON
metadata only.

The shared cloud validator passes after reconciliation:64sources,112links,
19decisions,9experiments,30tasks,17events,3workbook sheets and3arithmetic cases,
zero errors. The readiness mutation suite passes20/20 and `git diff --check`
passes. No app tests were rerun for this documentation-only steer, and no
backend/provider/audio archive was implemented. E045/EX009 remains the current
player verification.

## 2026-09-13 — W013 — R3 implementation and first acceptance

Read current handoffs after interrupted turn; no partial R3 changes found.
Removed empty-state slogans, collection fluff and footer tagline; kept concise
empty/error states, generated-audio provenance and Library information.
All visible text now at least16px, track titles18px. Added Shuffle collection
(random first track, shuffled remaining ready/displayed tracks, existing saved
transport shuffle mode). Fixed viewport shell with keyboard-focusable Tracks
region, sticky headings and separate queue scroll. Existing30tests and13syntax
checks pass. Desktop browser: region PageDown moved list161px, page stayed0;
Shuffle plays generated audio, six queue entries and pressed transport toggle.
Read-only browser parser lacked parseFloat; reran inspection using font strings.
390px fit;320px initially left only36px of list because controls wrapped. Compact
mobile toolbar to two rows, keep heading/add action together, hide redundant
mobile demo description (provenance remains in player/details). Final check pending.

## 2026-09-13 — W014 — R3 complete

D059/E048. Final0.1.2 artifact13files232122bytes,
SHA11762b548184b32e686c498c67956bd21f82e17475c17d5f130c00565d219291.
30regressions,13syntax modules and15HTTP checks pass. Desktop list scroll161px,
mobile116px while page stays0;320/390 widths match, list viewport133/237px.
Shuffle6generated tracks and filtered1track play; empty results disable action.
Pause and information dialog pass.16px controls/metadata/timeline,18px titles.
Search empty-string fill had no effect in browser tool; select-all/backspace
cleared it, after which full-list scrolling passed. No unresolved product issue.
Current verification JSON advanced;0.1.1 archived and EX009 redirected to exact
history. R3 stages complete, parent handoffs updated. No corpus/services changed.
Preview4175 retained; viewport override reset; no commit or agent delegation.

Final documentation checks: 26 player Markdown links and exact manifest pass;
cloud validator64sources/112links/0errors; git diff --check passes.

## 2026-09-13 — W015 — Radio option and exact Studio preservation

R4. User asks for second frontend based on NTS player/attached aesthetic brief;
retain existing front as an option. Copied exact0.1.2 src/public/scripts/tests/docs
and root package/handoffs to checkpoints/option-1-0.1.2 before edits, with
snapshot.json;34hashes verified. Snapshot is outside deploy allowlist. Original
relative documentation links retain their historical project context.

New0.2.0 shares native audio/data/handlers across Studio(default URL) and Radio
(?front=radio). Library information contains01Studio/02Radio switch. Switching
reparents the transport element, not audio; intended to preserve playback and
collection state. No new storage namespace or duplicated catalogs. URL carries
choice; no-query remainsStudio. Radio: Arial/Helvetica bold sans, black full-width
player, off-white editorial library, square initial tiles, distinct queue panel,
large title hierarchy. No NTS branding/art/stream copied; no invented live channels.

Read user attachment and current NTS page (channel/player structure confirmed;
not a measured font-family audit). Preserve brief in docs/NTS_PLAYER_BRIEF.txt.
Current Sites skill applies; existing local-only authority overrides publishing.
Its browser-QA rule requires explicit request, so no screenshots/DOM/click/viewport
QA this turn. HTTP200 first meaningful preview opened via open_in_codex.
30existing tests pass(129.922041ms),13syntax modules; exact artifact14files246421bytes,
SHA7b1fdb26ee51ab0f0d7d2d75c977717f550d168116619fc120f15dfcd54e82d1.
Archive hashes pass. Browser integration/responsive visual acceptance is unrun,
not inherited from0.1.2; shared state tests do not prove live layout switching.
No original audio, provider resources, hosting, spending, commit or delegation.

## 2026-09-13 — W016 — R4 closeout

Source review found Studio's resize handler would auto-open Radio's overlay queue
when crossing desktop width. Guarded auto-opening to Studio; Radio queue remains
an explicit action. Final syntax/build audit passes:14files246439bytes,
SHA2c37e5d74a7f56d7abf224f3a815e75a482c8c71d5ea5fc6ec6379414612fa32.
34current Markdown links pass; exact original34snapshot hashes unchanged;
shared cloud validator64sources112links0errors and git diff --check pass.
R4 complete; current visual/live-switch browser acceptance unrun, not claimed.
Local preview4175 reused and left for comparison. No server started or stopped
this turn. Exact Studio recovery and current comparison instructions documented.

## 2026-09-13 — W017 — Direct option switch and dark Radio

User requests an on-page switch and predominantly black Option2. Added visible
Option1/Option2 segmented buttons in persistent masthead, aria-pressed state,
retaining Library information and existing in-session layout switching. Mobile
switch occupies a dedicated header line to avoid squeezing16px text. Radio
canvas/queue/dialog/table now dark gray; player stays near-black, off-white is
used mainly for text/active controls. Original0.1.2 checkpoint untouched.
0.2.1 implementation complete; verification/document closeout pending.

## 2026-09-13 — W018 — Switch/dark Radio complete

D062/E050. Desktop and390screenshots inspected;320width checked in both options.
No horizontal page overflow. Radio/Studio list viewport180/93px at320; Radio266px
at390. Header switch updates pressed state/query/layout without stopping native
generated playback. Pause verified. Bodyrgb25,25,25. Viewport reset; Radio retained.
Current skill catalog no longer carries the prior browser-QA prohibition, so
bounded browser acceptance performed.13syntax/15HTTP checks pass; previous30unit
tests not rerun for this visual change.14files248095bytes,
SHAe11478ae9b4c0e4ccdd3a83846d50648a9ef6e283c0ca81edb59593c78226965.
34original snapshot hashes match.0.2.0 verification archived before0.2.1 update.
Initial doc ID assertion detected parallel D061 Kanban record before any write;
reservedD062, preserving D061. All local requested work complete; no corpus work.

## Navigation refinement — 2026-09-13

Navigation refinement (2026-09-13): top navigation now contains Your library and Playlists in both options. Playlists opens a contained directory with saved playlist links, track counts and Create playlist. Favorites/demo data and existing routes remain available; no playback/provider changes.

Changed src/app.js and src/styles.css. Directory hides track-only controls and restores them on return; accepts direct #playlists navigation. No filler copy or small text added. Initial edit command used parent-relative paths from the package directory and failed before writing; corrected paths and reran checks on changed sources. 13 syntax modules and 30/30 existing tests pass (126.916875 ms). Build verification: 14 files, 249371 bytes, manifest e3e827800797287df00e45149916a144eb2446c6f8d2a2b4dd1dc10a4c5c291c. No new browser QA; prior 0.2.1 visual evidence applies to the earlier build. No cloud execution or source corpus access. Next: review navigation in local preview; deployment remains deferred.

## Spectrum accent — 2026-09-13

Spectrum accent (2026-09-13): Option 2 now has a faint static dotted spectrum below Add music, inspired by the supplied image. SVG only; no live audio analysis, animation, invented telemetry or dependencies. Hidden at widths <=700px; Option 1 preserved.

Reference interpreted as an aesthetic accent, not a request for measured live FFT. Added public/spectrum.svg (deterministic layered point paths/grid), src/app.js decorative image markup, styles.css default hiding and radio.css desktop placement. Accessibility: empty alt, aria-hidden, no motion. First desktop inspection showed overly faint/narrow rendering; increased point opacity and let the drawing fill available bounds. Final 1280×720 preview inspected below Add music; controls and contained list remain visible. No playback wiring changed. 13 syntax modules pass; final build verification passes, 15 files / 346852 bytes, manifest c1be73406997fa81475ed45ae30a5ae5c77fd1b470af077dc9dd12df58499ed9. Existing 30-test result is from preceding navigation patch; not rerun for decorative SVG/CSS. Mobile hiding is source-inspected, not device-tested. No source audio/cloud access. Local preview: http://127.0.0.1:4175/?front=radio#demo. Next: owner aesthetic review; live audio-reactive behavior remains unimplemented.

## Live spectrogram correction — 2026-09-13

User explicitly corrected the static interpretation: actual playing music must drive a live 3D spectrogram. Replaced public/spectrum.svg with src/spectrogram.js and canvas markup; retained position, dark dotted treatment, narrow-screen hiding and Studio preservation. Earlier static completion is superseded.

Implementation: one lazily created AudioContext/media-element source per page, direct single destination connection plus analyser tap. FFT 2048, 96 logarithmic frequency bands from 40 Hz to min(18 kHz, Nyquist), peak aggregation, 48 history slices, amplitude height and perspective depth. At most 20 sampled/drawn frames per second (5 with reduced-motion preference), DPR capped at 2. Pause/end/hidden tabs stop RAF; hidden layout stops rendering; ResizeObserver restarts visible playback. Track loads/seeks clear history. No synthetic peaks, microphone, network analysis, source-file cache or batch corpus access. Existing media volume/mute remains in place.

Browser: generated First light playback advanced from 0:02 to 0:15 with visibly different spectrum surfaces. Pause froze audio at 0:15 and surface; Option 1 then Option 2 preserved that position and surface. 1280×720 screenshots inspected. An attempted read-only canvas pixel comparison via browser evaluate was unsupported (toDataURL not exposed by wrapper); used direct screenshots instead. No real-device or remote-source test claimed.

Verification: 14 syntax modules; 30/30 existing tests pass, 131.297291 ms; 15-file production build, 253708 bytes, manifest f4977d8e9deccd04d813fc486c804ce51644b6f600228d2ad1500436906286f9. No new dedicated analyser unit test; actual browser generated playback provides integration evidence. Static asset removed from production build.

Provider limitation: deliberately not attached in HTTP mode because media-element analysis of cross-origin streams needs verified CORS and credentials behavior; routing unverified streams through Web Audio can silence them. Provider implementation is still deferred. Unsupported Web Audio hides visualization; no fake fallback. Next: owner review with their imported music; later provider integration must explicitly test audio graph/CORS and audible output. Current review confirms playback progress and nonzero FFT, not a human audibility measurement.

API references checked: https://developer.mozilla.org/en-US/docs/Web/API/AnalyserNode and https://developer.mozilla.org/en-US/docs/Web/API/AudioContext/createMediaElementSource .

## Spectrogram axis padding — 2026-09-13

Spectrogram axis padding (2026-09-13): both time and frequency have zero-height ground extending 10% of the original span at each end (120% total). Measured samples are unchanged; expanded surface fits the existing canvas.

Changed src/spectrogram.js projection only. Precomputed padded coordinates retain original integer data indices; outside-domain points render at zero amplitude. Exact ends are -10% and +110%; 10 points per frequency end and 5 per time end approximate existing point density. Normalizing the extended domain keeps it inside the current canvas. No amplitude taper applied to measured data; padding is visual ground, not additional measured audio. 14 syntax modules and build verification pass: 15 files, 254283 bytes, SHA 4b7f1b78483d634ebbd355758a365dd86357104c3a1d20c26cf2e7a8de2fc4d4. No new browser QA or unit tests for this small projection change; previous live audio evidence remains historical. No failures or scope changes. Next: owner visual review of the expanded ground.

## Frontal view / padding rollback — 2026-09-13

Frontal spectrogram (2026-09-13): rolled back the 10% axis padding. Live history now uses aligned frequency columns and constant amplitude scale, with vertical time offsets and fading instead of perspective skew or foreshortening.

Scoped rollback removes only prior paddedAxis coordinates and domain normalization. Original 96 columns and 48 history slices retained. x no longer depends on time; amplitude height no longer shrinks with depth. Existing canvas margin retained, no extra ground. Time history offsets vertically by 24% of height to retain readable layers in a frontal view. FFT, scheduling, local-only scope and playback wiring unchanged. 14 syntax modules and 15-file build verification pass: 253664 bytes, SHA 9c0f2c47b846e6aaeb1aec923065a04228c6620fd93d5f4268cbe05d49ddb96f. No new tests or browser run for this projection-only change. Prior padding records are superseded, preserved for history. Next: owner visual review in existing local preview.

## Zero-elevation correction — 2026-09-13

Zero-elevation front view (2026-09-13): removes the remaining time-dependent vertical offset. Every history slice shares the same baseline and frequency positions; age changes opacity only. Supersedes the previous stacked frontal interpretation.

Previous response retained a 24%-height history offset, which still implied elevation; user rejected that interpretation. Removed distance from the y formula in src/spectrogram.js. x and y now depend only on frequency and amplitude, respectively. Time remains a fading overlay; no padded ground, skew, scaling or elevated viewing plane. Audio processing unchanged. 14 syntax modules and 15-file build pass: 253649 bytes, SHA 563ff6d082d09b39cb43932a18474becea77ef8cab07899c0ef99f69226db044. No new browser/test run claimed. Next: owner review of direct front view.

## Three spectrogram experiments — 2026-09-13

Spectrogram modes (2026-09-13): Isometric restores the first unpadded projection; Front retains zero elevation; Mountain adds reference-inspired dense grain and shaped audio history. Inline 16px buttons switch without resetting playback/history; preference saved locally.

Changed app.js controls, spectrogram.js render branches/persistence, styles.css and radio.css. All modes share the same FFT/history. Mountain draws 288 interpolated frequency positions × 48 frames, bounded to 20fps (5 reduced-motion), with nearest-band smoothing, sine edge taper, amplitude exponent .8, deterministic subpixel grain and a faint registration grid. It is an artistic transform, not a calibrated amplitude display. No hard-coded mountain peak, fake telemetry or tiny labels. Front remains default unless a valid saved choice exists. Controls disappear with canvas in narrow/Studio layouts; HTTP mode disables both.

Desktop browser: generated First light played through Isometric at 0:05 then Mountain at 0:10; mode labels/pressed states updated and screenshot inspected. Controls fit but reduced canvas room; reduced heading gap 20→12px and omitted near-zero Mountain points to remove bright baseline. Final reload occurred at narrow viewport: responsive hiding observed; saved preference persistence source-inspected only. Initial Mountain shape reflects sparse generated tones, so it cannot reproduce the reference silhouette for every song. No acoustic corpus or cloud work.

14 syntax modules and final build integrity pass: 15 files, 256388 bytes, SHA cabdf19e2754b9dd16d52d5693a53015e5147699a85a5727c972fbf29c78324f. Existing unit suite not rerun for render-mode changes. Next: owner compare modes on their imported music; real-device/performance and provider checks remain deferred.

## Falling fourth view — 2026-09-13

Falling spectrogram (2026-09-13): fourth view extends Mountain history from 48 to 62 planes (round(48×1.3)). Oldest 30% accelerate downward and fade smoothly into reserved lower space. First three projections retain 48 visible planes.

Changes: app.js adds Falling button; spectrogram.js accepts/persists fourth mode, retains 62 shared rows, renders 48 for older modes and 62 for Falling. Falling begins descent at normalized age .7, quadratic displacement up to .32 canvas height, smoothstep opacity fade to zero at end. Baseline lifted from .91 to .78 and amplitude height .73→.60 only in Falling to reserve lower space without clipping; no FFT modification. 62 is nearest whole-plane rounding of 62.4. Existing controls wrap at 16px. Rendering/sample cadence remains bounded at 20fps (5 reduced-motion); hidden/pause behavior unchanged.

14 syntax modules and build integrity pass: 15 files, 256836 bytes, SHA 683f303d8c5bb66591792978b3914a1a96e1c9c4e60b67bbaedbc7abb431eddf. No new browser/unit tests or performance benchmark; previous mode playback evidence is historical. No failures, corpus or provider scope changes. Next: owner visual review of Falling.

## Pause descent — 2026-09-14

Pause descent (2026-09-14): all four spectrogram modes now let retained points fall and fade for four seconds on pause/end, then clear and stop rendering. Resume cancels descent and starts fresh live history.

src/spectrogram.js adds a four-second monotonic timer, quadratic downward displacement (up to 1.1 canvas heights) and smoothstep fade across every mode. Shared history remains frozen while falling; paused branch does not sample FFT. Animation stops after clearing history, avoids drawing absent rows as phantom baseline points, suspends while hidden, and cancels on playing/seek/track-empty events. Background time counts toward completion. Static registration grid remains. End-of-track also settles unless player immediately advances (which resets history). No changes to audio routing or player state.

14 syntax modules and 30/30 tests pass (129.656291 ms). Final build: 15 files / 257510 bytes, SHA 4f88c34d7c1e7b7ff53dfa52c3fcfb7573721814af305671eda8eb1318832150. No new browser visual acceptance or dedicated analyser tests; lifecycle reviewed in source and existing playback regressions rerun. No failures, external services or corpus work. Next: owner review of pause descent speed.

## Faster fall and playback rise — 2026-09-14

Spectrogram motion update (2026-09-14): pause fall shortened to 2.8 seconds; Play starts fresh audio-driven points with a 1.6-second eased rise from below the canvas. Applies to all four modes.

Changed spectrogram.js only: fall 4000→2800ms; rise uses cubic ease-out over 1600ms interpolating from 1.06 canvas heights to the current measured position. Media play event clears old history and starts rise; playing starts render loop. Pause freezes rise progress at its pause timestamp while descent proceeds, avoiding opposing motions on rapid pause. Seek/empty resets both transitions. No audio graph or FFT changes.

14 syntax modules and build integrity pass: 15 files, 257763 bytes, SHA 16d1f77629013b3a78d9f12421ff4f90e66531ba4036cb900b77cc96b41612db. No new browser or unit-test run for this animation adjustment; prior playback regression results historical. No failures or expanded service scope. Next: owner review of timing.

## 2026-09-15 — MAEST top-six and local player integration

Owner-authorized `maest-top6-v1` now replaces legacy genre estimation: match the top six, display three expandable to six, retain all 519 scores, and apply no probability threshold or human review overrides. Historical outputs remain preserved. The low-priority board card `PIQ-GENRE-TOP6-REVISIT` is Later / could; further genre experimentation is not a launch blocker.

The local web player now provides **Analyze tracks** and **Create with PlaylistIQ**. Its loopback Node job service invokes the existing Python environment; analysis persists by source hash and in IndexedDB, and prompt results save into normal playable playlists. Restart the player server on the same origin/port to retain the browser library. This explicit integration authorization supersedes older local bridge/Python-edit holds; cloud deployment, remote audio processing and automatic MixPlans remain deferred.

Validation: 393 Python tests and 32 player tests pass; 17 JavaScript modules pass syntax checks. Production build verifies 16 files / 267065 bytes, manifest SHA-256 `0e9b04ecedb6448b6793e65796d1d2c8f390fd35fe83e16e297e7e5d46933443`. Browser acceptance on localhost:4181 imported one authorized real song, reused hash/model-matched saved features, showed three/six genres, displayed audio details, and made one live OpenAI request (`1 house track`) that matched its fourth-ranked House genre. Save playlist and feature persistence survived reload. A fresh generated 35-second sine exercised all seven workers: six usable stages, including all 519 MAEST scores; rhythm honestly remained partial because no beat grid was detected. No full corpus rerun. Four historical MAEST RSS failures remain unresolved; no RAM cap increase. New controls were visually checked on desktop; fresh Safari/mobile acceptance is not claimed.

Implementation: src/features.js, app.js, adapters.js, model.js and styles.css; scripts/local-features.mjs and serve.mjs; Python feature_catalog/web_bridge, analysis defaults and semantic worker, catalog/search models; regression tests. Fixed clipped row options and genre/vocal Instrumental alias collision during acceptance. The dedicated test server used port 4181; other user servers were left untouched.

## 2026-09-15 — Restart stale local services

Owner reported the restart-server error for every selected track. Confirmed old Node player processes on 4173 and 4175 belonged to this package; restarted both on their original ports (development and dist respectively). Both return HTTP 200 for the player and JSON 400 for a deliberately invalid playlist request, confirming the new service route without audio analysis or OpenAI calls. Browser library storage untouched; reload the existing tab and retry Analyze tracks. No code change.

## 2026-09-15 — Analysis workspace and fresh-export repair

Analyze tracks and PlaylistIQ now sit in the top controls. Feature columns toggle in the track list; the Analysis tab uses the full width with sticky track names and headers, horizontal scrolling, genre scores, tempo/key/loudness/arousal, mood/danceability/vocal scores and missing-stage details. Option 2 uses compact transport in Analysis. PlaylistIQ is a themed page with analyzed-track count, prompt form and inline results/save action; the earlier technical introductory copy is removed.

Fresh MAEST analysis could finish and then crash in `review_document`: the new top-six export referenced undefined `ordered` (NameError). The earlier generated-audio acceptance preceded that export edit and did not cover the final code; this checkpoint supersedes that acceptance claim. Cached completed records bypassed the failing code. Export now uses the result’s top-six values or its historical top-ten slice, with passed/failed regression coverage. Malformed worker JSON now becomes a failed stage instead of aborting the track. Per-source stage checkpoints persist under `output/web-features/checkpoints`, allowing retries after later failures; prior deleted temporary output cannot be recovered. Local analysis diagnostics are retained in `output/web-features/last-analysis-error.log`; provider errors remain redacted. Source audio, memory limits and the top-six/no-threshold/no-overrides rule are unchanged.

Verification: 395 Python tests and 33 player tests pass, 17 JS modules pass syntax checks. The exact failing fresh path was reproduced through localhost:4173 with a generated 31-second tone, then rerun successfully after repair: all 519 MAEST scores saved; six stages usable and rhythm explicitly partial because the tone has no beat grid. No music corpus rerun. Browser checks cover feature toggle, full-width Analysis and PlaylistIQ page in both desktop options, populated saved song features, and narrow layout. Production build: 16 files / 274471 bytes; manifest `d16a9d365bc34fdbc1f8af6ddc4ca6346545392d28c0fe21cc3cf82218d673a5`. Reload the existing player tab; Analyze tracks retries incomplete tracks while retaining completed records.

## 2026-09-15 — Analysis action and batch duplicate review

Removed shared Analyze tracks / PlaylistIQ buttons; Analysis has a larger dedicated Analyze tracks action. Imports now compare SHA-256 content and normalized filenames, including earlier files in the batch. Unique files are added first; one end-of-import dialog lists duplicates with Omit (default), Keep both and Replace, applied together. Closing the dialog omits pending duplicates. Replacement atomically updates the saved audio and track while preserving its ID, playlist/favorite references and added date; analysis survives only for identical bytes. Changed audio loses stale features. Replacing the current item reloads it paused while preserving the queue. Import and analysis cannot overlap. Original files are never modified.

Checks: 35 player tests pass, including exact/name duplicate detection, identity-preserving replacement and analysis invalidation. Syntax/build verification pass. Browser confirmed the standalone Analysis action on preview port 4175; the batch-dialog browser upload path was not exercised. No acoustic analysis or provider calls. Reload the existing browser origin.
## 2026-09-15 — Analysis action placement and icons

Moved the Analysis page action into the heading’s right-side action area beside
Add music. Its visible label is `Analyze Tracks`, it uses the dark secondary
button treatment, and it has a waveform icon. Added a column-layout icon to the
Your Library `Feature columns` toggle. The heading actions wrap safely on narrow
Analysis layouts. Player syntax, 35 tests, production build verification, and
diff whitespace checks pass.

Follow-up: Add music is hidden on the Analysis tab, leaving Analyze Tracks as
the sole heading action there. Add music remains available in Your Library.

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

Browser acceptance: inspected the owner’s Chrome player at 127.0.0.1:4175 and refreshed its existing library. All 61 tracks remain loaded (28 complete analysis, 2 partial, 1 saved playlist). App status reports 61 embedded titles, 59 artists, 59 both, zero neither. The two artist fallbacks are Laroze - Wildest Desire [www.slider.kz] and Rahul.mp3 x Hazboy - Girls Gone Wild. Tagged names visibly replace filenames. These counts describe this browser snapshot, not the 37-track test folder or the server cache. No acoustic analysis was run.

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

## 2026-09-19 — PlaylistIQ Iteration 1 delivered

Python 0.4.0 / player 0.3.0 now integrate `playlist-intent-v1.3` (configured low reasoning), `intent-compiler-v1.1`, `maest-intent-v1` ranking and `discogs-parents-v1`. Required genres use MAEST support; creative prompts use directional soft priorities. Genre OR/family matching, original-request clarification, per-track contributions and twenty-prompt review evidence are available. New result/catalog/translation/run writes use schema 0.2.0 and read historical 0.1.0.

422 Python tests and 50 web tests pass. Final compiler replay passes all 20 intent/constraint checks; live revision failures are preserved, and final optional/HTTP checks pass. Human listening acceptance remains pending. No new audio analysis or cloud work; YAML is still a consideration task.

See [implementation, prompt, contracts and verification](../prompt-to-playlist/docs/ITERATION_1.md). This current checkpoint supersedes older descriptions of v3-only translation, flat genre ties and missing parent matching; dated older sections remain historical evidence.

Final closure: 50 web tests, 32 JavaScript syntax checks and 23-file production manifest verification passed. Python package: 422 tests; parent: 54 tests. Offline Python 0.4.0 wheel/source builds passed. App status was inspected in the running normal app; PlaylistIQ at 320px has no document overflow or console errors. Test servers use isolated ports and the normal library origin is not migrated. Restart the normal player/reload its existing tab to activate the new assets.

## 2026-09-19 — Chrome batch recovery, unique Analysis and result playback

Recovered 54 exact-hash originals with complete saved analysis into the existing Chrome profile at `127.0.0.1:4173`: the older 37-track batch (including ten house tracks) plus 17 cached pool tracks. Chrome now has 115 library records / 109 unique Analysis tracks (83 complete, nine partial, 17 without analysis); PlaylistIQ has 88 genre-backed candidates. Six duplicate Analysis entries are collapsed by content hash, retaining stored audio/IDs and playlist references. Every PlaylistIQ result can play through the main player. Restore saved batch is repeatable and limited to the three established source folders; regular imports reattach matching cache data. No new audio inference.

57 web tests, 35 syntax checks, 24-file build verification and local HTTP checks pass. Chrome playback advanced on the selected second result, then was paused. Repeat recovery confirmed zero added / 54 already present. Human listening acceptance remains pending. See [recovery workflow and evidence](docs/LIBRARY_RECOVERY.md).


## 2026-09-19 — Natural-language PlaylistIQ score explanations

Every result now explains musical fit, strongest contributors, the main score gap, qualification and rank. Expandable per-objective details translate recorded evidence, preference direction, explicit/inferred origin, priorities, weights and earned points into plain language with 0–100 arithmetic. Missing evidence, genre alternatives/families, tempo ordering and rounding are explicit; raw engine notes remain available. Deterministic presentation adds no explanation LLM calls or ranking changes. See [explanation contract and example](docs/TRACK_EXPLANATIONS.md). 64 web tests pass; current Chrome beach-day request inspected.


## 2026-09-19 — Prompt-to-scene explanations and listener counterexample

Why this track now connects the exact request and saved planner scene to conditional listening roles for recorded audio evidence, before the numeric explanation. It makes scene assumptions and limits explicit: broad mood agreement does not establish that a track belongs in a setting. The notebook can reopen exact saved results without regeneration. Chrome verified the original 65.62-point Listen Over the Ocean result for “un dia en la playa”; Manuel/Grecia feedback was saved to that attempt, without assigning a whole-playlist verdict or changing ranking. 69 web tests pass. See [scene-fit case](docs/SCENE_FIT_FEEDBACK.md) and [explanation contract](docs/TRACK_EXPLANATIONS.md).

## 2026-09-22 — Hybrid estimator implementation and bounded validation

Owner requested immediate implementation following research. Expanded heads and MuQ ran on exactly Listen Over the Ocean and My Paradise - Edit from the established diverse folder. Each now has 56 theme + 40 instrument scores and three timestamped MuQ embeddings; source hashes/inventory are unchanged. Expanded-head time: 3.169 / 2.972 s; MuQ time: 17.33 / 13.25 s; largest measured MuQ process-tree RSS: 2814.9 MiB. Cache retries execute zero stages. Both results were attached through normal Chrome track actions and inspected in Analysis/details.

Seven live prompt calls across three creative cases preserve v1.4/v1.5 failures and v1.6's affected-case pass. v1.4 returned Spanish retrieval text and an unavailable warm preference; v1.5 fixed language in three cases but still chose warm; v1.6 constrains the soft enum and validates it locally. Final case: matched, 17.8 s, exact hybrid replay. Final offline structured/hybrid comparisons preserve three fixed queries. Semantic-only intimacy ranking still favors the house track; no listening acceptance is claimed.

Final regression: 442 Python tests, 77 web tests, 45 JS syntax modules, verified production build (28 files, 382314 bytes; SHA-256 `0c417bc697070198c03b101a90ac0d52d400ac15661b54a61832b46ca5c56036`). Runtime, failure, asset and replay evidence: [implementation log](../prompt-to-playlist/docs/ESTIMATOR_UPGRADE.md). Broader library upgrade and blind listener comparisons remain pending.


## 2026-09-22 — Local DJ mix delivery

DJ mixes now renders saved/imported manual plans through the existing local DJ engine and provides progressive AAC playback, lossless/downloadable completion, cache reuse, seeking and cancellation. Owner explicitly authorized this implementation after research. See [implementation and evidence](../../docs/MIX_DELIVERY.md). 77 web tests, syntax/build checks, live HTTP integrity/cancellation/ranges and browser playback/seek pass; 390px document width is 390px. Human listening, remote hosting and automatic MixPlan generation remain separate. Existing library state stays on its original browser origin.

## 2026-09-25 — Selectable supervised feature estimators

Music2Emo (MERT-95M + BTC/chord/key + J_all, corrected mode) and MusiCNN danceability are implemented as optional direct-feature challengers. The specialist reference remains default; MAEST top-six, MuQ and ranking weights are preserved. Complete compatible catalog coverage is required per challenger; otherwise everyone retains the reference. Two authorized sources passed six matched-window stages and zero-inference retries. Final checks: 481 Python tests, 80 web tests, 45 JS syntax modules, 28-file build, 40 exact fixed-query replays and one final successful live replay. One prior live intent proposal was rejected; no new listening judgments or superiority claim.

Exactly two local cache records have both challengers. Original Chrome was observed at 109 unique tracks; its final updated display was not confirmed because native interaction was interrupted by active use. The new reload migration attaches richer same-hash optional caches to completed reference records. Isolated browser acceptance verified real values, retry, profile/scope, saved-result reopening, App Status and 390/320px controls. No batch/new-corpus inference, audio upload, cloud work, commit or format migration.

Read [research, commands, failures, coverage and continuation](../prompt-to-playlist/docs/SUPERVISED_ESTIMATORS.md). Historical sections/publication cutoffs below remain evidence for their original dates.


## 2026-09-25 — Quality-first estimator research and implementation

Quality-first non-genre research and the selected available specialists are delivered locally. The web default selects Music2Emo theme/VA, MusiCNN vocals, VGGish aggression and independent PaSST OpenMIC instrument evidence, retaining EffNet happy/sad/relaxed/danceability. SheetSage2 supplies selected key evidence. MAEST, MuQ and planner weights remain unchanged. Two authorized sources passed 8/8 new stages; retries execute zero stages. Richer nuanced-emotion prediction and listening superiority remain unresolved; do not present encoder-only releases or the same 56 tags as solving that objective.

[Implementation, two research reports, setup, model contracts and verification](../prompt-to-playlist/docs/TOP_ESTIMATORS_IMPLEMENTATION.md). Final validation: 502 Python tests, 83 web tests, 45 syntax modules, 28-file build, eight successful final audio stages and 26 exact fixed-query replays. No new provider calls or listener judgments. The new optional specialist stages and quality/openmic vocabulary identity preserve reference records and saved-profile replay.

## 2026-10-01 — Test music relocated; local server restarted

The owner moved the three existing test corpora into `test_music/` and created `test_music/new_albums/`. Runtime recovery and bounded smoke/attachment scripts now use the new parent; current README commands are updated. Historical analysis files retain their recorded paths and hashes. The DJ engine resolves a missing legacy corpus folder to its existing `test_music` location without changing archived evidence; existing folders always take precedence. Source-output protection includes the new music parent, and Git excludes the whole local music tree.

Server uses the existing `http://127.0.0.1:4173` origin. Models, profiles, weights and analysis behavior are unchanged. The owner will manually import new albums and launch analysis; the agent did not import or analyze music. Bulk Analyze Tracks remains the standard pipeline; Details → Upgrade selected specialists runs the newer selected models. `new_albums` is not silently included in Restore saved batch.

Validation: 11 engine/path tests and 35 export-boundary tests passed; 83 web tests, 45 JS syntax checks and the 28-file static build passed. MuQ, supervised and all four specialist model asset checks passed without inference. The active historical DJ collection resolves all ten source files at the relocated paths. Local HTTP checks passed and recovery found 54 cached originals. Server remains on port 4173. No browser import, acoustic analysis or model/provider request was run.

## 2026-10-01 — Unified default analysis delivered and verified

Owner requested selected model replacements in ordinary Analyze Tracks, retained unreplaced/additional features and both Music2Emo/EffNet moods. Implemented `selected-estimators-v2` with eleven sequential guarded stages, isolated stage failures, missing-only retry, current-cache precedence, updated primary columns and explicit comparison labels. Fresh two-track test passed 22/22 stages in 129.19/182.31 seconds; peak worker RSS 3680.4/3064.3 MiB, minimum host available RAM 2532.7/2546.3 MiB. Both retries and real HTTP analysis requests executed zero stages. Hashes/inventories unchanged. Prior cache history and retired results preserved. 505 Python + 84 web tests, 45 syntax checks and 28-file build pass. One migration test fixture needed the new version; no real inference failure. Chrome Analysis verified and left ready with 109 unique tracks. No whole-library/new-album inference, cloud activity or commit. Two-track success does not guarantee every future file; whole-machine swap increased during the test.

See the maintained default-pipeline document for exact lineup, evidence paths and limitations.

## 2026-10-01 — 120-description bank ready

Owner authorized 120 concepts, precomputed text embeddings and replacement matching that reuses audio embeddings. Delivered `musical-character-v2-120` (30 emotion / 25 groove / 25 texture / 20 intensity / 20 arrangement), independent audio cache, bank-content and audio-fingerprint score invalidation, a model-free matching path, and current-version upgrade detection. UI groups two matches per dimension and spells out seconds sampled. Playlist ranking unchanged.

All 120 text embeddings prepared in 34.38 s, peak worker RSS 1574.8 MiB. Two existing acceptance tracks refreshed in ~42 ms each; exact audio vectors and other stages unchanged, no inference, repeated requests no-op. Real HTTP route accepted current records. 516 Python / 85 web tests pass. No whole-library inference or matching was launched. See CHARACTER_BANK_120.md for full concepts, artifact paths and unvalidated listening-quality limits.

Final acceptance for character-bank change: 45 JS modules pass syntax checks; 28-file production build succeeds. Chrome verified all five grouped dimensions and 120-description notice on the cached Ocean row, plus “90 seconds analyzed.” Search cleared; Analysis left ready with 237 unique tracks visible. No batch started. All preparation/analysis workers exited. New suggested labels remain unvalidated listening evidence; no automatic corrections based on these two examples.

## 2026-10-01 — Analysis incident diagnosis (no repair applied)

Owner supplied an error dialog with 219 entries: one track with decoder failures and 218 entries reporting `IDBDatabase: The database connection is closing`.

- `Xxamorxx -Hot Like Latina`, SHA-256 `42dc6f974099f21209cf1770318a16feb40d9af64b5cc326f0c74e354d6a3a4c`: AAC in an M4A container. Beat This `rhythm` exhausted its Torchaudio/SoundFile/madmom decode path; SheetSage2's direct SoundFile read rejected the format. Nine of eleven current stages succeeded, including 120-description MuQ matching. Older key/energy records remain. The two failed workers peaked at 373.9 / 590.2 MiB RSS with 4349.1 / 4675.7 MiB minimum host available memory: decoder failures, not memory-guard failures.
- `Sell Me Candy`, SHA-256 `b5899c5f7523c945ade3b8314cb31f69f4ace89d3372d82d3904595fd3b0a94f`: all eleven stages completed and the current 120-description record was saved on disk at 13:38:16 local time. It is the first browser-storage error in the pasted list. Evidence supports failure in the later browser save/read step rather than inference.
- The batch loop catches every error and continues; after a closed IndexedDB connection it attempts each remaining track against the same unusable handle. This explains the cascade of 218 repeated storage errors. Code has no reconnection or batch-stop handling for this condition. The precise event that initiated connection closure is not recorded; do not claim a proven cause such as memory pressure, quota, another tab or a browser crash.
- At inspection, 120 server feature records exist: 19 current complete, one current partial, 89 older complete and 11 older partial. These are cumulative cache counts, not all new successes from this batch. No PlaylistIQ workers remain active. No inference, restart, browser-storage clearing or app code changes were performed for this diagnosis.

Recommended repairs: decode supported containers consistently through FFmpeg into temporary PCM for Beat This/SheetSage2; reconnect or pause cleanly on IndexedDB loss, preserve server-side completion and restore by hash; add AAC/M4A and connection-loss integration cases. Earlier two-track smoke covered MP3 and did not exercise these failure modes. Original audio is not written by the analysis path; disk cache existence does not by itself prove the browser database is healthy.

## 2026-10-01 — M4A conversion and closed-storage recovery

Implemented the owner’s conversion-first pivot: MP3 passthrough, M4A conversion before import, provisional existing-library button, atomic original backup and invalidated stale features. Added connection recovery and batch stop on persistent storage errors. 90 tests, syntax and build pass; real generated-tone endpoint succeeds. Chrome button verified; read-only diagnostic found zero persisted tracks after reload, cause unresolved. No user corpus conversion/analysis run. [Details](docs/MP3_IMPORT.md).

## 2026-10-01 — Expanded recovery after the 54-track limit

The old recovery button was deliberately restricted to cached analysis in three flat source folders; it excluded new_albums, nested albums and uncached tracks. It was not a backup of the full browser collection. The owner reported only 54 restored tracks after losing a collection of more than 200.

Recovery now recursively scans the fixed project test_music root, including new_albums, excludes symlinks, deduplicates exact SHA-256, and restores source audio even without analysis. Saved features are attached only when available; missing features are never invented. Existing source bytes are preserved so compatible analysis remains reusable; M4A conversion stays a separate owner action after recovery. Source paths remain absent from public listings. Persistent storage errors stop recovery.

Measured disk inventory: 295 audio files, 255 unique hashes, 59 with valid saved web-feature records, 196 without. With 54 already restored, the next run can add 201, subject to browser audio/storage failures. This restores all available local originals, not an exact reconstruction of the previous 237-track selection; previously unloaded files may be included. Other cached hashes without matching originals in test_music cannot supply playable audio. Playlists/preferences are not reconstructed.

Verification: 92 web tests pass, including recursive uncached recovery, symlink exclusion, hash checking and idempotence; syntax/build pass. Live endpoint reports 255 entries/59 analyzed and no source paths. Server restarted on port 4173. No owner audio imported, converted or analyzed by this repair; reload and click Restore saved batch again.

## 2026-10-02 — Shared-library web edition preview

Web edition runs on port 4174 with layout 3, 187 verified fully analyzed MP3s, a single mix with transition timestamps, and brief white guide cards. Local edition stays on 4173 with layouts 1 and 3. Owner-only APIs are blocked in web mode. A live PlaylistIQ request and main-player playback passed; 95 tests pass. Same private repository, separate edition/config/build; no cloud deployment or audio upload performed. [Architecture, catalog gate, tests and next launch steps](docs/WEB_EDITION.md).

Failures/pivots: HTTP adapter native fetch needed a receiver-safe wrapper; initial guide CSS was placed in an unused file, then moved to the loaded radio stylesheet and visually verified. The cache had 193 current complete records; strict MP3/source eligibility admitted 187, including 8 browser-only copies. No incomplete record was admitted to meet a requested count.

## 2026-10-02 — Web visualization fixed to Falling

Owner requested one visualization in the web edition. Web now selects Falling independently of saved preferences and omits the view-selector markup. Local visualization choices remain available. Syntax and both edition builds verified.

## 2026-10-02 — Immutable cloud release and production server

D070/E058 implements the dedicated cloud entrypoint, frozen exporter and production
job supervisor, without modifying the local preview UI or restarting 4173/4174.
187 eligible MP3s and one existing mix are copied with exact hashes. Sessions,
CSRF/proxy/origin checks, private routes, streaming ranges, persistent quota and
full child-process-tree timeout cleanup are tested. Initial full suite:115 tests,
64 syntax modules; final review corrections and deployment evidence are tracked
in [PREPARATION.md](../../docs/cloud-library/first-release/PREPARATION.md).
No inference, audio conversion, provider mutation, upload or deployment.

## 2026-10-02 — Serverless candidate implemented locally (D072/E060)

[Current implementation checkpoint](../../docs/cloud-library/first-release/serverless/IMPLEMENTATION.md) supersedes the earlier plan-only status. Lambda worker, durable jobs/login, static playback transport, allowlisted export and five infrastructure templates are implemented locally. 123 player / 16 API-edge / 24 Python tests pass; offline Linux preserves all 60 planner cases. A separate preview on 4176 loaded 187 tracks and played/seeked audio with the API deliberately unavailable. Original release/model policy and 4173/4174 servers preserved.

One no-cost AWS quota request is now PENDING: concurrency 1,001 because AWS rejected 200 as below its standard default 1,000, despite the effective account limit of 10. App reservations remain worker=1/API=5. No compute/storage/subscription resource created, upload or paid model call. Final self-contained image export needs more disk (20 GiB free before build). CloudFront Free subscription is explicit in IaC; zero existing subscriptions observed, actual eligibility unproven. Hosted-key choice, alert email, real cloud benchmark/auth/ranges/rollback remain pending. Use the checkpoint and serverless runbook, not the historical VM provisioner. T034 remains in progress.

## 2026-10-03 — D073/E061 rollout completed; owner acceptance pending

Private 187-track playback and PlaylistIQ are live. Final cloud-only text loader preserves original vectors/planner evidence within 3,008 MB. Five cold plus ten warm AWS probes pass; the single production-key prompt returns ten matches in 63.41 seconds, 2,362 MB peak. Real auth/storage/range checks and paired alias/pointer rollback pass; duplicate terminal POST adds no paid call. Probe stack deleted, Free CDN ACTIVE, current aliases2/2 and AI enabled. Alert-email confirmation and owner desktop/phone listening remain; IAB blocked cloud navigation. No original analysis, source audio, local server or planner policy change. [Identity, failures, scan limits and receipts](../../docs/cloud-library/first-release/serverless/LIVE_ROLLOUT.md).

## 2026-10-03 — Web refresh ready for local review

The simplified web UI, 186 distinct recordings, PlaylistIQ deduplication, mobile mini/expanded player and iOS native-audio fix are implemented locally on 4174. Replacement password is privately staged. **Not deployed: owner confirmation required by the current request.** 135 tests, 70 syntax modules and 37-file web build pass; Chrome responsive and transition-seek checks pass. Real iPhone background/lock-screen acceptance remains. [Changes, evidence, limitations and deployment handoff](docs/WEB_REFRESH_2026-10-03.md).

## 2026-10-03 — Full-screen mobile refinement, local review only

Implemented the owner's second UI refinement: full-screen draggable player, clipped transform-only title/artist previews, shared-analyser mini spectrum, centered 20 Hz–20 kHz web plot, full-card library playback with three genres and three musical facts, concise IQ explanations/plan and bottom estimator icon, and current/upcoming-only queue with pull dismissal. Native iOS audio routing stays intact; progress rendering is now event-driven. Local preview restarted on 4174 after it was found stopped. The first browser reload reached an error page while it was down; a fresh in-app tab recovered once ready. Narrow score columns initially wrapped numbers; nowrap numeric cells and a balanced first column resolved it.

143 tests pass; 72 modules pass syntax; 38-file web build and manifest validation pass. Browser checked 320/393px and desktop, real local playback, next/previous swipes, full-screen geometry, dismissal from plot/text, current-first queue and mouse pull closure. IQ presentation used a temporary synthetic fixture, removed before build. No paid calls or provider mutations. Physical iPhone gestures/background listening remain unverified. [Evidence and continuation](docs/WEB_REFRESH_2026-10-03.md).


## 2026-10-03 — Shared listener saves and playback polish

Delivered local profile persistence, prompt history, attributed listening aggregates, Love/Add controls, smaller spectrum, slower sheets, theme-consistent sort, top-five character view and unified mix transport. Browser testing found and fixed mutable-preference aliasing that hid playlist changes from sync; added a regression. Concurrent/ambiguous retries are covered by permanent operation identities and transactional revision checks. 156 web tests, 21 API/edge tests, 4 template assertions, 79 syntax modules, 43-file build pass. No AWS mutation or paid inference. Current evidence and publication requirements: [SINGLE_USER_PROFILE.md](docs/SINGLE_USER_PROFILE.md). Local-review hold persists; physical iPhone acceptance remains.


## 2026-10-03 — Discovery and third player refinement

Implemented the owner's next local review list: 41.667dvh spectrum, icon-only actions above enlarged transport, centered track block, 75dvh queue, queue in tabs row, stacked track ellipsis/heart and direct top-five cosines. Randomized library order is stable during a visit; 50 prompt examples cover ten styles and produce a fresh pair per page load. Added derived listening habits. Seeking now distinguishes explicit pause intent and status occupies a fixed area to prevent control movement. 165 tests, 81 syntax modules and 44-file build pass. Checked 320/393/1280 widths, refresh variation, seeking, details and habits. No cloud writes/paid calls/audio changes; local-review hold remains. [Checkpoint](docs/WEB_DISCOVERY_REFINEMENT.md).

## 2026-10-03 — Authorized cloud/domain publication

Reduced expanded visualizer from 1.25× to 1.10× the original height and shifted it right by 12px. Published accumulated web/profile updates with API and worker aliases 3 (same worker image). Added exact custom-origin support, CORS and ACM-backed CloudFront alias for resonant.lat. Rotated the already-requested password privately. 165 web, 22 API and 5 infrastructure checks pass; cloud login/ranges/profile persistence verified. No audio/model modifications or paid AI calls. See DOMAIN_RELEASE.md for DNS cache limitation, receipts and rollback.

## 2026-10-04 — History, likes, sheet motion and real native spectrum

Local 4174 now includes permanent Liked Songs, revised navigation/footer/cards, slower rounded sheets and playable saved prompt results with new explanation snapshots. Replaced iPhone progress-grid fallback with audio-derived frequency files while preserving native playback. **168 web / 22 API tests; 85 syntax modules; 47-file build pass. Not deployed or pushed.** Read [current changes, evidence and publication handoff](docs/WEB_HISTORY_SPECTRUM_REFINEMENT.md). Three existing production prompts retain their ten saved tracks; no history reset. Physical iPhone acceptance remains.


## 2026-10-04 — History and native spectrum published

The owner-authorized release is live on resonant.lat and CloudFront: green PlaylistIQ tab (+15%), 1.6-second mini-spectrum pause easing, permanent Liked Songs, playable prompt history, prior sheet/UI refinements and real native-playback spectra. API/worker aliases 4/4, admissions enabled; audio/model/password unchanged. 168 web / 22 API / 5 infrastructure checks plus cloud auth, ranges, spectrum protection and profile persistence pass. [Production checkpoint](../../docs/cloud-library/first-release/serverless/HISTORY_SPECTRUM_RELEASE.md). Physical iPhone acceptance remains.
