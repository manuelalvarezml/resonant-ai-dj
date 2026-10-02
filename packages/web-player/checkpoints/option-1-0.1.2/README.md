# Resonant web player

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
