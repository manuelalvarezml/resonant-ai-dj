# History and native spectrum release — 2026-10-04

Owner authorized publication of the latest local web changes, plus a dark muted green PlaylistIQ label enlarged by 15% and a gradual pause animation for the mini spectrum.

Status: **live on https://resonant.lat/ and the original CloudFront address**. API and worker aliases are both 4, admissions enabled. Runtime stack UPDATE_COMPLETE; code and worker image identities verified. Git publication is recorded with the release commit.

## Release contents

Includes the [October 4 local refinement](../../../../packages/web-player/docs/WEB_HISTORY_SPECTRUM_REFINEMENT.md): permanent Liked Songs, playable prompt history, compact saved explanations for future requests, navigation and card cleanup, slower player/queue sheets, rounded drag dismissal, themed estimator menu, and real native-playback frequency visualization.

PlaylistIQ and subtle action accents use muted green `#789786`; the tab is 15% larger than its peers. Mini spectrum amplitudes ease back to the dotted baseline over 1.6 seconds after pausing. Reduced-motion preference uses the resting line immediately. Rendering remains capped at 20 fps and stops when the document is hidden.

Native iPhone audio still bypasses AudioContext. The spectrum uses 188 locally derived frequency files (187 frozen MP3s and one mix), about 65.3 MB, under authenticated `/library/spectra/v1/`. Original audio, ranking, analysis and worker image are preserved. Existing three production prompts have saved track IDs and were not reset; old missing explanations are clearly labeled. Future completed requests store compact explanation snapshots through the updated profile API.

## Preparation and rollback

Private execution folder: `output/web-refresh/green-release/`. Fresh candidate app ID: `2e5fa9593af2889f750a07a12fc5e3836f999b2a8be611ca31ee6ce65794676a`. API package SHA-256: `aae73f3215ac6d7c8787966d0bc54e2500bfc3c3bf81d2044bbdeb594da10e03`.

The refresh helper accepts an explicit work directory to preserve previous rollout receipts. Password rotation is now opt-in; this release leaves the current credential unchanged. Staging allows new private spectrum files but refuses mismatched existing library/audio assets. `before.json` retains prior aliases, CONFIG, pointer versions and stack parameters. Use the [paired rollback procedure](../../../../deploy/serverless/RUNBOOK.md), preserving all older function versions and S3 versions.

Reviewed runtime change set modifies only API/worker functions, their versions and aliases. Version replacement is expected; no database, bucket, role or subscription replacement. The worker image digest remains unchanged; only the paired deployment revision changes.

## Local verification

168 web tests, 22 API/edge tests, five infrastructure delivery checks passed. Syntax check: 85 modules; build: 47 static files. Chrome mobile review observed waves still present just after pause, followed by the resting dots; green label and 15% font increase verified. Physical iPhone lock-screen/background playback is still an owner check.

## Production acceptance

235 new static objects (47 app files and 188 spectra) staged with checksum verification; 200 existing objects verified and skipped, zero audio uploads. Previous paired aliases were 3/3 and remain available for rollback.

Both custom-domain and CloudFront smoke checks passed using public DNS: first-visit login redirect, public login resources, unauthorized catalog/audio/spectrum denial, authenticated exact app/catalog hashes, original MP3 byte-range equality, track/mix spectrum equality and logout. Shared profile persistence across sessions and retry idempotency passed; only the uniquely named temporary verification playlist was removed afterward. No paid AI request was submitted.

Chrome on the actual domain loaded the green label with an exact 1.15 font-size ratio, then played an existing track using the diagnostic native-audio path and visibly rendered the measured spectrum without console errors. This is browser verification, not physical iPhone background testing. Local preview was restarted on port 4174.

Receipts: `output/web-refresh/green-release/domain-smoke.json`, `cloudfront-smoke.json`, `profile-smoke.json`, `before.json`, `staged-assets.json` and `published-pointers.json`. Current tuple: `output/serverless-cloud/active-deployment.json`.
