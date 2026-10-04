# Resonant domain and web refresh — 2026-10-03

Owner authorized publishing the accumulated local web changes and connecting **resonant.lat**. This supersedes the earlier local-review hold for this release.

## Changes

Expanded visualization: 36.667dvh (1.10 × the original third-screen height), starts at 12.5dvh, left inset 12px. Track metadata stays centered in the remaining space. All previous mobile, queue, discovery, explanations and native iPhone audio changes are included.

Shared likes, playlists, prompt history and listening aggregates now use authenticated `/api/profile` routes backed by the existing DynamoDB table. UUID operation markers make retries idempotent; profile rows have no expiry. The existing worker image, planner, model files and 187-MP3 frozen release are preserved. The UI collapses one duplicate recording and displays 186 tracks.

The requested shared password is rotated through SSM. Plaintext/hash and rollback copies remain only in ignored private output, never Git.

## Domain architecture

Namecheap DNS ALIAS at `@` points to `dl3pumk9rpbun.cloudfront.net`. ACM certificate lives in us-east-1, validated through a persistent CNAME for automatic renewal. CloudFront uses SNI and TLSv1.2_2021. The original CloudFront URL remains usable. Exact allowed origins, host-only signed cookies and S3 result CORS cover both addresses; foreign origins remain rejected. No new hosting subscription, DNS hosted zone, compute instance, or audio upload.

References: [CloudFront custom URLs](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/CNAMEs.html), [ACM regions](https://aws.amazon.com/certificate-manager/faqs/), [Namecheap ALIAS records](https://www.namecheap.com/support/knowledgebase/article.aspx/10128/2237/how-to-create-an-alias-record/).

## Verification and operations

165 web tests, 22 API tests, 5 infrastructure tests, 81 syntax modules and the 44-file web build pass. Browser geometry at 430×932: x=12, y=116.5, height=341.734, as specified. Physical iPhone lock-screen/background acceptance remains an owner test.

The existing cloud URL passed anonymous/login/logout, exact app/catalog checks and authenticated MP3 byte-range verification. Saved playlists passed cross-session persistence and retry idempotency, using a uniquely named temporary playlist removed after verification. No paid PlaylistIQ request was submitted during this refresh.

`deploy/serverless/refresh-release.py` provides bounded preparation, asset staging, admission pause, publication and activation. It validates the selected personal account, active Free subscription, unchanged release/model and new API checksum. Existing audio/library objects are verified and skipped. Review and execute infrastructure changes through `cloud-stacks.py`. The private `output/web-refresh/domain-release/` folder contains the prior deployment tuple/parameters/pointer versions, API package, staged asset receipts, certificate, password rollback and acceptance results. `output/serverless-cloud/active-deployment.json` records the live runtime and app.

## Status

Frontend and profile API published; runtime aliases API=3 / worker=3 and admissions enabled. HTTPS certificate ISSUED and edge stack UPDATE_COMPLETE. Namecheap apex ALIAS saved; both authoritative servers and Google public DNS resolve CloudFront addresses. Custom-domain login, exact app/catalog, protected audio ranges, logout and cross-session profile tests passed with proper resonant.lat TLS using a scoped CloudFront DNS override. The local resolver/Chrome retained a negative DNS cache at the time of this checkpoint; normal browser acceptance on resonant.lat remains pending that cache expiry. The existing CloudFront URL was verified in Chrome and remains available. DNS is one-minute TTL, but an earlier negative response advertised about one hour; some clients may take that long to recover. Only the requested apex domain is configured; www remains the registrar’s original parking record.
