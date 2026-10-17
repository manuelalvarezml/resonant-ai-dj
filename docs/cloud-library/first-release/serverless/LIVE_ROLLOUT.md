# Private cloud release — 2026-10-03 — D073/E061

## 2026-10-17 — Shared-library artwork live

[Artwork checkpoint](../../../ALBUM_ARTWORK.md): shared-library covers and compact queue/library/results/minimized-player layouts are live on resonant.lat. 165/187 tracks have covers; both spectrograms remain. Protected image delivery, audio playback and mobile/desktop layout checks pass. API/PlaylistIQ 11/11 and mix 5 are unchanged; the later transition candidate was not deployed. Personal cloud uploads and their automatic processing remain pending, as does physical iPhone acceptance.

## 2026-10-04 — History and native spectrum release

[Current production checkpoint](HISTORY_SPECTRUM_RELEASE.md): latest web refinements and profile API are live, aliases 4/4. Audio-derived iPhone spectra replace the progress fallback. Green PlaylistIQ (+15%) and gradual pause easing included. Domain/CloudFront auth, audio ranges, protected spectra and cross-session saves passed.

## 2026-10-03 — Web refresh and resonant.lat

[Domain release checkpoint](DOMAIN_RELEASE.md) supersedes this page’s original app/API tuple: refreshed mobile UI, shared profile, requested password rotation, API/worker aliases 3, ACM certificate and Namecheap ALIAS are deployed. Music/model release remains unchanged. Authoritative/public DNS and custom-domain TLS checks passed; local browser DNS cache expiry remains.

**Live:** [Resonant](https://dl3pumk9rpbun.cloudfront.net/). Private playback and PlaylistIQ are enabled. The published library contains **187 fully analyzed MP3s**, eight catalog pages and one DJ mix. Analysis stays local. One production PlaylistIQ request returned ten matches in **63.41 seconds**.

Use the shared password in `output/cloud-config/first-release/listener-password.txt`. It is intentionally absent from this document and Git. Credentials, cookies, account identifiers, signed URLs and detailed AWS receipts remain in ignored private `output/` files. No additional credentials are needed for the running release.

## Owner actions and remaining acceptance

The AWS alert subscription is now **confirmed**, verified against this deployment’s exact SNS topic. Actual alarm delivery has not been triggered as a test.

1. Open the site on desktop and phone, sign in, and test play/seek, queue advance and the DJ mix with the Mac disconnected. Real cloud HTTP acceptance passed. Automated in-app browser navigation was blocked by `ERR_BLOCKED_BY_CLIENT`; that restriction was not bypassed. Remote browser/device listening remains owner acceptance.

This working private release does not close broader discovery, listening-quality or multi-user gates. Existing saved playlists remain browser-local; individual accounts and cross-device private playlist synchronization are outside this release.

## Deployed configuration

| Component | Verified configuration |
|---|---|
| Account | Personal `manueldev` / `manuel-web`, suffix 3649; exact account guard before writes |
| Regions | Data/API/worker in `us-east-2`; edge/WAF/subscription in `us-east-1` |
| Media | Private **S3 Standard**, exact CloudFront OAC access, versioned release pointers |
| Delivery | CloudFront **FREE / ACTIVE**, signed cookies; audio bypasses Lambda |
| Access | Shared password; 24-hour sessions, secure cookies, same-origin/CSRF protection |
| API | HTTP API and lightweight Lambda, reserved concurrency 5 |
| PlaylistIQ | Private x86 Lambda, **3,008 MB**, 360-second timeout, 512 MB scratch, concurrency 1 |
| State | DynamoDB on-demand; private S3 requests, audits, results and text cache |
| Admissions | Enabled; 30 accepted jobs/day, 900/month, at most three outstanding |
| Secrets | Four SSM Standard SecureString parameters; separate owner-selected production OpenAI key |
| Alerts | Four CloudWatch alarms, failure SQS queue, account-wide $5/$10 actual-cost notices; email subscription confirmed |
| No recurring server | No VM, NAT Gateway, load balancer, EFS, provisioned concurrency or automatic warmer |

The Free-compatible WAF rule permits 6,000 requests per five minutes per IP globally. API Gateway and DynamoDB retain tighter API/login limits. An earlier path-scoped WAF candidate was rejected by the Free subscription and fully rolled back; no paid fallback was selected.

Effective AWS concurrency is 1,000; the earlier 1,001 request remains CASE_OPENED and needs no duplicate request. Actual function creation proved a separate **3,008 MB memory cap**. AWS documentation says memory-limit increases cannot be requested; concurrency approval does not resolve it. See S115 in [sources](SOURCES.md).

## Release identity and recovery

- Release: `4a4bb92196ed75cc95ac19ec6a25bd5062ed31cdabb0eb30ebca0f83d5b5ff57`.
- Worker image: `sha256:7e6a834c44cd6269a72dc4b65534aa085fcd1ff3e8a388ece2f760ee6389de4e`.
- Worker build: `5572e2bb6f342108df5f9f3689dc4527e887e0b5516360dd1e808cba40817024`.
- API ZIP SHA-256: `2cb2b126e5df2071f8bb983fd4470167c2d806d83780a82cdf55b44ecb2e3679`.
- Planner SHA-256: `c1e37b04f3c5d85a34fe3241ba4fc9a5a217c237b58c84b1ba3029b990d11f32`.
- Model manifest SHA-256: `290d4489a8cf56321485950f838125b4d374c9dff50d78c106a8185850360070`.

`output/serverless-cloud/active-deployment.json` owns current paired API/worker aliases, both pointer VersionIds, release/image/code/revision and prior CONFIG. `playback-deployment.json` preserves the initial playback-only tuple. Prior function versions, referenced images and media are retained. Pointer VersionIds were updated after the successful restoration exercise.

Pause `CONFIG#ACTIVE.enabled` to stop new jobs while audio continues. Drain jobs before changing paired aliases and release pointers. Never automatically replay `outcome_unknown` jobs or failure messages. Use [the runbook](../../../../deploy/serverless/RUNBOOK.md); do not use superseded VM scripts or regenerate signing keys.

## Actual AWS measurements

| Trial | Result |
|---|---|
| Final generic text benchmark | 15/15 passed: five cold and ten warm at 3,008 MB |
| Cold text seconds | 200.397, 64.308, 16.646, 16.550, 16.363 |
| Warm text seconds | 0.160–0.242 |
| Generic text peak memory | 1,940 MB |
| Final benchmark gross compute | $0.015820 |
| Production request | Ten matched tracks; 63.41 seconds end to end |
| Worker REPORT | 56.679 seconds execution; 57.881 seconds billed; 1.202 seconds initialization; 2,362 MB peak |
| Worker compute for that request | Approximately $0.002834, excluding OpenAI and other AWS services |

These are small samples. Warm embedding latency is not whole-job latency. Cold starts vary and can take several minutes; there is no warm-start guarantee. The full job left 646 MB below its memory allocation. Audio remains independent of AI startup and pauses.

All generic probe compute, including failed/diagnostic candidates, totals approximately **$0.050873**, below the $3 authorized ceiling. Logs, storage, API and one OpenAI request are separate. The translator does not retain the provider usage envelope, so actual OpenAI token charges require its project billing dashboard. Updated [cost scenarios](COSTS.md) use 3,008 MB instead of the original 8 GiB assumption.

## Acceptance evidence

Private receipts are under `output/serverless-cloud/acceptance/` unless otherwise specified.

| Check | Result |
|---|---|
| Frozen release | 187 MP3s, 1,910,985,140 audio bytes; original hashes preserved |
| Inventory | 233 immutable objects plus two entry pointers; all checksums/S3 versions verified |
| Worker storage | Six actual DynamoDB/S3 claim, fencing, provider-marker, terminal replay and result checks; fixtures removed |
| API transactions | Nine actual persistence checks, including duplicate race, quota slots, expiry and ownership; dispatch intercepted |
| CDN/S3 | Nine checks: signed/unsigned access, HEAD, exact 206 bytes, 416, cache/expiry, direct-S3 denial and result CORS |
| Hosted login | Eleven checks: secure cookies, wrong password, session, CSRF/origin denial, refresh and logout |
| Real playback | Root/library pointer SHA match; actual MP3 bytes 100000–132767 match the original |
| Failure destination | Reserved-concurrency-zero fixture reached SQS as ZeroReservedConcurrency; that fixture alone was removed |
| Delivery metric | DestinationDeliveryFailures explicitly queried: no datapoints. Absence is not measured zero; actual SQS receipt proves the path |
| Production AI | Exactly one normal production-key prompt; matched, ten results, signed-result SHA verified |
| Replay/rollback | Same terminal request reused job/counters without another provider call; paused admissions returned 503; retained alias pair restored; both pointers restored from saved versions; session/MP3 seek survived; current aliases/admissions restored |
| Local compatibility | 123 player, 16 API/edge, 24 Python tests; five templates linted; 60 frozen Linux planner cases |

An offline capture verified the OpenAI outbound request contains prompt, clarifications, vocabulary and aggregate capability counts. It contains no audio, track IDs/hashes or per-track feature vectors. `store=false` is not a claim about broader provider retention. Automatic approval review initially blocked suspected full-library disclosure; this inspection disproved that premise and the reviewed execution succeeded. A preflight AWS concurrency response-field bug was fixed before any submission. There was exactly one actual production prompt and no automatic replay.

## Startup repair and known limits

The original image timed out at 360 seconds. A bounded 120-second diagnostic located repeated full-model SHA hashing at startup. Cloud startup now checks manifest identity and file sizes in a digest-pinned read-only image; full hashes are verified at build time. A second candidate returned identical vectors but peaked at 3,004 MB, leaving insufficient full-job headroom.

The final cloud-only loader omits construction of the unused audio tower. Original verified checkpoint, text forward/projection/normalization, float precision, encoder identity and strict loading of retained keys are preserved. Cloud audio inference explicitly raises. Original local analysis/loader/planner policy is unchanged. All tested text vectors match original hash `89f18c6ef0314ec9dcbd04d8c5d10121c4ba7d4546c98cd445b9309058399d87`; all 60 planner cases pass.

OS updates reduced ECR findings from 8 critical/48 high to **3 critical/13 high/7 medium/2 low**. The final image was scanned separately. Remaining critical findings concern unused Perl Storable/regex/Socket paths. This is not a clean scan; retain receipts and revisit upstream fixes. No model/core replacement was introduced to hide findings.

Versioning protects against changes/deletion, not complete regional outage. No active regional failover or paid SLA is implemented. Shared access has a global AI quota. Human listening quality, phone/background playback and actual alarm delivery remain open.

## First-visit entry correction

The owner’s fresh browser exposed a missed launch check: the main URL returned CloudFront `MissingKey` before the login redirect ran. The original default behavior required a signed cookie before the visitor could sign in. Earlier API login checks had bypassed this entry path and did not establish a working first visit.

An in-place CloudFront update makes only the allowlisted app shell (HTML/JS/CSS/fonts/config) public so the entry function can redirect unsigned or expired visitors to `/login/index.html`. `/library/*` and `/media/*` still require valid signed cookies; the API still enforces sessions/CSRF, and S3 remains private. No new resource, paid tier, model call or audio change. Main URL: https://dl3pumk9rpbun.cloudfront.net/ . Direct login: https://dl3pumk9rpbun.cloudfront.net/login/index.html .

Fresh-cookie HTTP acceptance now passes six groups: root/index302 to login, public login resources200, unsigned/invalid-cookie catalog and audio403, fresh login opens exact app/catalog, authenticated MP3 seek matches original bytes, and logout returns to login. Receipt: `output/serverless-cloud/acceptance/entry-smoke.json`; script: `deploy/serverless/cloud-entry-smoke.py`. Seventeen API/edge tests and three deployment configuration tests pass; edge template lints. Browser/device listening remains owner acceptance.

## Cleanup and continuation

The isolated probe stack was deleted, verified by a final readback, after archiving all 130 log events and completed benchmark receipts. Read `output/serverless-cloud/resonant-text-probe/cleanup.json` before recreating it. Production stacks are resonant-registry, resonant-data, resonant-edge and resonant-runtime; retain their rollback assets. No broad Docker/ECR cleanup or source deletion was performed.

Next: owner acceptance above, followed by observed billing/latency review after real use. No recurring monitor was scheduled. New library releases require a new immutable export and review; never sweep local folders or partial analysis into S3.

## 2026-10-03 — Separate local UI/audio candidate (not published)

The owner requested a local-first web/mobile refresh and iPhone background-audio repair. See [local review checkpoint](../../../../packages/web-player/docs/WEB_REFRESH_2026-10-03.md). Source changes and a new password hash are ready locally; no AWS mutation, production password change or active deployment tuple change occurred for this candidate. The live state documented above remains authoritative until explicit publication confirmation.
