# Web player takeover

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
