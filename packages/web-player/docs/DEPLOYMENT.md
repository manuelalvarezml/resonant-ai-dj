# Later deployment handoff

**D057 planning update:** [FAST_CLOUD_LAUNCH.md](../../../docs/cloud-library/FAST_CLOUD_LAUNCH.md)
is the current R2-first recommendation and setup sequence. This handoff still
defines the portable frontend boundary; no provider is configured here.


Local player/static release implemented; no host, bucket, account, auth, DNS or
deployment configured. Preserve D054 player scope and D055 cloud-readiness work.
The linked recommendation does not pass any empirical cloud gate.

## Release

1. Node ≥22: `npm run check`, `npm test`, `npm run build` (no installation).
2. Stop dev preview; `npm run preview`, then `node scripts/verify-preview.mjs`.
   Inspect exact build on intended browsers and `dist/build-manifest.json`.
3. When authorized deploy **only dist/**. No corpora, repository root, Python
   outputs, browser database or temporary files. Correct HTML/CSS/JS/JSON/SVG/TTF/TXT
   MIME types; hash navigation means no SPA route rewrites. Relative assets also
   work under a URL prefix.
4. Keep local config until actual authenticated services implement API.md.
   HTTP mode must not point at speculative/placeholder services. Local imports
   do not upload anything in either mode.
5. Record exact artifact manifest, public config, security headers and checks.
   Rollback restores prior static artifact/config. No server migration ships here.

## Open service work

| Boundary | Required result |
|---|---|
| Host | HTTPS static origin, access policy, headers and rollback |
| Authentication | Established session, server ownership, login/logout/account-change clearing |
| Catalog | Authorized stable snapshot projection, bounded pages |
| Playback | Exact-source entitlement/publication checks, expiring capability, rate limits |
| Storage | Private immutable audio, byte ranges, codec eligibility, CORS/cache/deletion policy |
| Uploads | Separately verified quota-controlled ingestion, not a fake browser upload |
| Collections | Account namespace, sync/revision conflicts and export/import integration |
| Connected sources | Official adapter/auth, separate play/external-open/download capabilities and visible unavailable states |
| Playlist-file archive | Revision snapshot, rights/quota/byte preflight, ordered eligible audio, M3U/JSON manifest, omissions, expiry/cancel/cleanup; ellipsis-menu entry only |

No OpenAI key/provider credential is needed. PlaylistIQ and DJ rendering remain
independent. Never expose the loopback development server publicly as hosting.

## Hosting headers

Apply through the chosen host's native header configuration:

```text
Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' blob: data:; media-src 'self' blob:; connect-src 'self'; font-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'; form-action 'self'
Referrer-Policy: no-referrer
X-Content-Type-Options: nosniff
Permissions-Policy: camera=(), microphone=(), geolocation=()
```

Inline allowance is styles only (slider CSS variable); no inline scripts/eval,
external fonts or analytics. Add only selected media origins to `media-src` for
HTTP mode, reconcile CORS/redirects. frame-ancestors requires an HTTP header.
Use no-cache/no-store for HTML/config and no-store for private API responses.
Asset filenames are not content-hashed: do not set long immutable caching unless
the host uses versioned release URLs. HSTS belongs only on configured HTTPS hosts.

## Acceptance before connecting real music

- Two identities: deny arbitrary IDs, deleted/quarantined sources and stale
  versions; verify bucket privacy and logout/account-switch clearing.
- HEAD, 200/206/416, suffix/open-ended ranges and accurate Content-Length,
  Content-Range, Accept-Ranges/MIME. Seeking must retrieve intended bytes.
- Real capability expiry/re-authentication, long-track multiple renewals,
  deletion mid-playback, source identity and no URL logging/leakage.
- CORS/CDN isolation, stale config/asset rollout and rollback.
- Desktop Chromium/Safari/Firefox, actual intended iOS/Android: codec support,
  autoplay, seeking, interruptions, background/lock-screen controls, volume
  restrictions, file selection and storage eviction. Resizing one desktop
  browser is not real-device acceptance.
- Owner-approved storage/request/transfer budget and stop conditions. No vendor
  cost estimate is changed by this package's local tests.
- Playlist archive with generated/licensed fixtures: ordering, filename
  collisions, manifest/omissions, changed rights, cancellation, expiry,
  interrupted download and cleanup. Never use provider playability as audio
  export authority.

Browser references reviewed 2026-09-12:
[play promises](https://developer.mozilla.org/en-US/docs/Web/API/HTMLMediaElement/play),
[Media Session](https://developer.mozilla.org/en-US/docs/Web/API/Media_Session_API),
[IndexedDB](https://developer.mozilla.org/en-US/docs/Web/API/IndexedDB_API),
[HTTP ranges](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Range_requests).
These support implementation choices, not measured provider/device claims.
