# Individual accounts and spectrum preference — 2026-10-06

Owner requested implementation, live publication, Git push, a test account and a reset of prior shared listening/history data. This supersedes the shared-password/profile design for the hosted edition. Local analysis remains separate.

## Behavior

Email + username + password signup; sign in by case-insensitive email or username. Usernames accept 3–24 letters/numbers/underscores. Passwords accept 12–128 characters and use salted scrypt (N=131072, r=8, p=1, 64-byte output). Native password-manager autocomplete is enabled; the application never stores plaintext passwords in browser storage. Secure HttpOnly SameSite cookies remember sessions for 30 days, while private media cookies renew daily. Old shared sessions are rejected.

Each account has private likes, playlists, listening statistics, prompt history and explanation snapshots. Jobs belong to the account, allowing reconnection from another session for the same account. All testers share the unchanged 187 MP3s (186 distinct recordings), analysis and existing mix. New accounts start empty. A transaction reserves unique email and username identities. Signup cannot choose roles or provider identities. Ten accounts is the small-trial safety cap; the initial target remains about five testers. Current daily/monthly PlaylistIQ cost caps and worker concurrency remain global.

Account identity is resolved before loading private state. Browser caches/outboxes, preferences, review notebooks and pending jobs are scoped by account. The hosted edition purges the legacy shared cache and never imports it. Logout clears hosted private caches and alerts other tabs; server requests verify the expected account as well as CSRF. Older tabs cannot synchronize shared-profile data into a new account. Account identity API failure now blocks initial app boot instead of opening possibly stale private state.

Google Identity Services button, server JWT verification and explicit account linking are implemented. Signatures, issuer, audience, expiration, verified email and one-use browser-bound nonce are checked using `jose`. Email matches never silently link accounts: an existing password user must sign in and explicitly link the matching Google account in Account settings. New Google users can supply a username on the signup form; otherwise they receive a stable `dj_…` username. Google activation still needs a web OAuth client ID with the production JavaScript origins authorized. No client secret is required by this ID-token flow. The UI reports Google as unavailable until configured. Real Google-provider acceptance remains pending.

Email/password registration does not verify mailbox ownership or send email. Email is an account identifier; no automatic account recovery is offered in this bounded private trial. Lost access requires owner assistance. This is not a claim of production-scale identity readiness.

## Animation

Full spectrum animation is the default, including on devices with Reduce Motion enabled. Account → Spectrum animation can select Follow device Reduce Motion (5 fps). The setting is device-local and applies only to the spectrum; sheet motion still respects the OS. The earlier frame-budget and cached-grain optimization remains: recorded/native visualization targets 30 fps and history advances at 20 Hz. The recording-derived source is still 10 Hz with interpolation. Device performance can constrain actual FPS; physical iPhone 12 confirmation remains pending.

## Analytics and privacy

Existing measured listening progress produces per-account seconds, starts, qualified plays, completions and early skips. Seeks/background inactivity are not counted as listened time. Product telemetry batches allowlisted event types, app-view names, control identifiers, timestamps and a pseudonymous session reference. It does not capture input values, prompt text, playlist names, DOM text, URLs/query strings, passwords, keystrokes, IP addresses or unrelated browsing activity. Authentication throttling uses a salted IP hash with a short TTL, separately from analytics.

A disclosure appears at signup and in Account. Only a persisted owner role can request `/api/admin/analytics`. The dashboard shows global and per-user totals, feature counts and recent click/navigation sequences; private playlist/prompt contents are not returned. Detailed events expire after 90 days and are filtered out immediately when beyond retention, independently of DynamoDB TTL cleanup. The dashboard labels its latest-1,000-event sample per user; it is not an exhaustive all-time click count. Listening totals and saved private content persist. Product events are best-effort and bounded (100 queued on device, 20 per batch, 300 batches per account/day); they are not a billing-grade audit log.

## Migration / operations

`deploy/serverless/api/manage-accounts.mjs` provisions accounts after an exact AWS account guard and writes generated credentials only into ignored mode-0600 files under `output/accounts/`. Owner defaults to username `manuel` and the existing deployment alert email; the separate test login is `tester`. Never put credentials into Git, public docs or logs.

`deploy/serverless/reset-legacy-profile.py` privately archives pre-account profile rows, sessions and request/result/audit objects before removing their live references. It preserves library, analysis, model caches, cost counters and new account namespaces. Historical S3 versions remain recoverable; this is a live reset, not a secure-erasure claim. Profile reset must not be followed by an unguarded rollback to the old shared-profile API once individual users exist.

The refresh helper stages immutable assets, keeps login changes until publication, records previous login/pointer versions and invalidates `/login/*` together with entry pointers. The music release and worker image remain unchanged. Google client configuration uses private `AUTH#CONFIG`; there is no application secret in frontend code.

## Verification / release state

Pre-publication: 173 web tests, 31 API tests, syntax and build pass. Isolated Chrome at 390×844 with Reduce Motion enabled verified login, signup, logout, account switching, full-animation default/override and owner/listener dashboard visibility, with zero browser exceptions. Google token rejection tests are local cryptographic fixtures, not a live Google login. AWS and Git publication receipts are appended after rollout.

References: [Google ID token verification](https://developers.google.com/identity/gsi/web/guides/verify-google-id-token), [Google web client setup](https://developers.google.com/identity/gsi/web/guides/get-google-api-clientid), [OWASP password storage](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html).

## Published and reset

Live on https://resonant.lat/; runtime UPDATE_COMPLETE, API/worker aliases **6/6**, PlaylistIQ admissions enabled with the unchanged cost caps. App ID `b2493783bb8847f5ce96c9d1e361296b31243536657601eb6341c0e81e509df4`. Final API ZIP SHA-256 `16eb55ad8a5c7338008ebc9ee4a37176f3d988d2317a839adffbd901054c052f`. No music uploads or model calls.

Live HTTP checks passed: fresh profiles, same-ID cross-account save isolation, same-account cross-session persistence, owner-only aggregate analytics, account binding/CSRF, event ingestion, 1,024-byte audio range, protected native spectra and logout. Real public signup starts empty and ignores caller-supplied owner/provider fields; its temporary account was removed. Isolated live Chrome at 320px verified email login, full spectrum setting under Reduce Motion, hidden owner controls for a listener and logout with zero browser exceptions.

First live analytics read failed because DynamoDB rejects an empty sort-key predicate. The corrected whole-partition query was verified against real AWS, deployed as version 6 and regression-tested at the SDK boundary. Final checks: **173 web / 32 API / 5 infrastructure**. Physical iPhone FPS, email delivery/recovery and live Google sign-in are not claimed.

Reset archived **332 legacy rows and 12 prior job objects** privately. After live checks, temporary playlists/events/sessions were cleared again. Strongly consistent readback confirms exactly **two accounts**, empty profile and event partitions for each, and admissions enabled. Credentials are in ignored `output/accounts/manuel.json` and `output/accounts/tester.json` (mode 0600), never in Git. Owner email came from the pre-existing alert configuration.

Private release folders: `output/web-refresh/accounts-live/` and `output/web-refresh/accounts-query-fix/`; HTTP/browser/signup/final-state receipts are in `output/accounts/`. Prior API version 4 uses shared state and is not a safe automatic rollback after this migration; prefer the isolated account API or a forward fix.

Google continuation: create a Google OAuth **Web application** client with JavaScript origins `https://resonant.lat` and optionally `https://dl3pumk9rpbun.cloudfront.net`. Store its public ID as `{"googleClientId":"…apps.googleusercontent.com"}` in a private local config, then use `manage-accounts.mjs google` against the guarded deployment table. The button enables from server configuration without another app deployment. Real sign-in/linking on Safari and Chrome is the remaining acceptance step.
