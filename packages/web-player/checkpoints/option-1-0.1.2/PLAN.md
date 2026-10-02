# Staged web-player build

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
