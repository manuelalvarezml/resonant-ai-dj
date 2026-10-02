# Player service contract 1

Version0.1.1 changes presentation/assets only; API envelopes are unchanged.
Future auth/collections/import implementation is ordered in the
[cloud launch plan](../../../docs/cloud-library/FAST_CLOUD_LAUNCH.md).


Implemented frontend consumer/projection, **not an implemented backend**.
Separate versioning from the broader proposed cloud envelopes and Python
packages. Server tenant/object IDs stay internal; no vendor selected.

## Runtime configuration

Default `public/config.json`, copied into dist:

```json
{"contract_version":"resonant-player/config/1","mode":"local","apiBase":"/api/","mediaOrigins":[]}
```

Future example (not active):

```json
{"contract_version":"resonant-player/config/1","mode":"http","apiBase":"/api/","mediaOrigins":["https://media.example.com"]}
```

API base must be same-origin, end in `/`, with no credentials/query/fragment.
Media origins are exact HTTPS origins; reconcile hosting CSP with them.
The development server is a static preview, not an API proxy. Host/application
establishes authentication separately. Requests use same-origin cookies, JSON,
no-store, no redirects and a 15-second timeout. No credentials in browser config.

## GET /api/v1/tracks?limit=100&cursor=...

```json
{
  "contract_version":"resonant-player/library/1",
  "revision":"snapshot-001",
  "next_cursor":null,
  "tracks":[{
    "id":"track-001", "sourceVersion":"source-001-v1",
    "title":"Example owned track", "artist":"Example artist",
    "album":"Example collection", "duration":215.4,
    "addedAt":1789171200000, "status":"ready", "color":0,
    "evidence":[{"field":"Title","value":"Example owned track",
      "authority":"encoded_fact","source":"ffprobe/container-tags"}]
  }]
}
```

- Opaque id: 1–128 ASCII letters/digits/underscore/hyphen; title/artist ≤500 chars.
- Duration: seconds or null; addedAt: Unix milliseconds. Status:
  ready/processing/unavailable. Only ready tracks can start.
- Color: one of six abstract fallbacks. HTTP forces kind=cloud.
- Max 100 tracks/page, 50 pages/5,000 tracks/load. Stable snapshot revision,
  unique track IDs and non-repeating cursors are enforced client-side too.
- Only public projection fields survive validation. Do not send private paths,
  object keys, playback URLs or tenant choices in the catalog.
- Evidence entries have string field/value/source plus one exact authority:
  encoded_fact, standardized_measurement, deterministic_measurement,
  benchmark_estimate, user_verified, llm_proposal, executed_action.
  Missing evidence stays unknown. Search matches title/artist/album only.

Frontend validation is not server authorization. Server resolves authenticated
tenant ownership, scopes snapshot/pagination and enforces independent limits.

## POST /api/v1/playback-sessions

```json
{"contract_version":"resonant-player/playback-request/1","track_id":"track-001","source_version":"source-001-v1","position_seconds":42.5}
```

Illustrative response; create actual future expiry at runtime:

```json
{"contract_version":"resonant-player/playback-session/1","track_id":"track-001","source_version":"source-001-v1","url":"https://media.example.com/opaque-capability","expires_at":"2026-09-12T12:05:00Z"}
```

Response identity must match the exact requested published source version.
Expiry needs >5 seconds remaining. URL must be same-origin or an allowed HTTPS
media origin, without userinfo/fragment. Server must deny deleted, quarantined,
unentitled and wrong-tenant sources. Protect POST using session authentication,
Origin/CSRF checks and rate/capability limits. CORS is not authorization.

Native audio fetches the URL; this player does not attach arbitrary Authorization
headers to media requests. Server must choose compatible cookie/capability
semantics. Bearer URLs stay only in memory, never logs, exports or preferences.
Local object URLs are revoked on switch/clear. No media prefetch/cache worker.

An expired seek or media error re-resolves the same track/version/position.
One consecutive renewal is allowed; >1 second of actual resumed progress resets
the budget for a later expiry. New selection aborts old requests. Pause during
loading and paused queue edits stay paused. Failed playback stops visibly rather
than silently skipping tracks or looping requests. Real provider expiry/byte
range behavior remains unverified by fake-response tests.

401/403 requests sign-in/access review, 404 unavailable, 429 later retry. Other
failures show generic messages; provider response bodies/stack traces/URLs are
not printed. Actual sign-in, logout and account-switch UI is future hosting work;
account change must destroy current state and reload the authorized library.

## Saved state and exports

Local: IndexedDB `resonant-library-v1` stores selected file blobs and track
metadata atomically across two stores; localStorage
`resonant-player:preferences:1:local` stores bounded preference data only.
HTTP: playlists/favorites are memory-only pending authenticated account/library
namespace and sync design. Never restore a single `http` storage key across
accounts. Complete logout/switch isolation must accompany future authentication.

Export `resonant-player/playlist-export/1` includes name, ordered track IDs,
public title/artist/source references. No audio, absolute paths or capabilities.
The dialog exposes copyable JSON plus a download link. Export re-import/account
sync is a later contract; this browser package currently creates local playlists.

D058 proposes a separate future playlist-file archive service. It must snapshot
the saved-playlist revision, resolve `play_in_app` and `download_original`/
`include_in_playlist_archive` independently for every source, return a preflight
of eligible/omitted items and bytes, then create an ordered archive plus M3U/JSON
manifest behind an expiring capability. The UI entry is **Download playlist
files** inside playlist More options. It is not this JSON export and not a DJ
mix render. No endpoint or client behavior is implemented in0.1.1.
