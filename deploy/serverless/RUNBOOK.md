# Serverless operations and release runbook

**Current release is live.** Start with [LIVE_ROLLOUT.md](../../docs/cloud-library/first-release/serverless/LIVE_ROLLOUT.md) and [machine-readable evidence](../../docs/cloud-library/first-release/serverless/implementation-verification.json). Private 187-track playback and PlaylistIQ passed real AWS acceptance. Owner desktop/phone listening remains; the exact AWS alert subscription is confirmed.

Use `manueldev`, the existing private exact-account guard and regional resources in **us-east-2**. Edge/WAF/subscription live in **us-east-1**. Never fall back to the default profile, use the preserved Lightsail provisioner, regenerate signing keys or expose secret parameter files.

## Current state and private files

| Item | Location / actual state |
|---|---|
| Site | https://dl3pumk9rpbun.cloudfront.net/ |
| Shared password | `output/cloud-config/first-release/listener-password.txt`, mode 600 |
| Authoritative active tuple | `output/serverless-cloud/active-deployment.json` |
| Prior playback-only tuple | `output/serverless-cloud/playback-deployment.json` |
| Final AWS readback | `output/serverless-cloud/acceptance/final-state.json` |
| Runtime parameters | `output/serverless-cloud/resonant-runtime/parameters-text-only.json` |
| Actual resources | resonant-registry / resonant-data / resonant-edge / resonant-runtime |
| Ephemeral probe | Deleted; evidence in `output/serverless-cloud/resonant-text-probe` and `output/serverless-benchmark` |
| API / worker live aliases | Published versions 2 / 2, never `$LATEST` |
| Worker | x86, 3,008 MB, 360 seconds, 512 MB scratch, reserved 1 |
| API | reserved 5; same immutable ZIP verified by CodeSha256 |
| CloudFront | FREE subscription ACTIVE; no PAYG/paid fallback |
| Secrets | Four SSM Standard SecureStrings; production OpenAI key separate from local development |
| Job caps | 30/day, 900/month, 3 outstanding, 1 running; CONFIG enabled |

Production stacks and immutable objects are retained. Current private tuple records the exact release, both pointer VersionIds, paired aliases, code/image and revision; do not reconstruct versions from a chat summary. The paired rollback exercise updated pointer VersionIds without changing their bytes.

Account concurrency is 1,000 and its memory cap is 3,008 MB. The earlier 1,001 quota request is CASE_OPENED; do not duplicate it or assume it changes memory. No additional key/email choice is needed. The configured email subscription is confirmed; inspect this deployment’s exact Alerts topic rather than unrelated account-wide subscriptions. Budget notices are alerts, not spending limits; OpenAI billing is separate.

## Read-only inspection

```sh
output/serverless-tools/bin/python deploy/serverless/cloud-stacks.py status --stack resonant-runtime
output/serverless-tools/bin/python deploy/serverless/cloud-stacks.py status --stack resonant-data
output/serverless-tools/bin/python deploy/serverless/cloud-stacks.py status --stack resonant-edge
```

These helpers enforce the selected account and save detailed outputs privately. Also inspect active Free subscription status, exact Lambda image/ZIP hashes and alias versions, CONFIG release/enabled, SQS failures, AWS alarms and subscription confirmation. DestinationDeliveryFailures was explicitly queried with no datapoints; that is not a measured zero. A real SQS failure-destination fixture did pass.

## Pause and investigate

1. Conditionally set DynamoDB `CONFIG#ACTIVE` / `sk=META` to `enabled=false` only for the current release. Media remains independent in S3/CloudFront.
2. Read outstanding jobs and let them become terminal or logically expire before changing runtime aliases. Never decrement slots manually; terminal/deadline reconciliation reclaims them.
3. Preserve request, full audit, browser result, Lambda REPORT and failure receipt. A provider-start marker with ambiguous outcome may already represent a charge.
4. Never automatically replay failure-queue messages or create a fresh request key to work around uncertainty. A retry with the **same** exact idempotency key resolves to the same logical job. A genuinely new retry is a counted potential paid attempt.
5. Worker reserved concurrency 0 is emergency containment; it can route queued async events to SQS. It is not the ordinary pause switch.

## Paired rollback

Pause admissions and drain first. Verify the saved release/image/API/pointer tuple and retained versions. Restore **both** API and worker aliases with revision checks, copy both `index.html` and `library/current.json` from their recorded S3 versions, verify SHA and remote readback, then restore matching CONFIG. Record newly created pointer VersionIds. Retain media/images/prior function versions throughout.

The first-release exercise restored versions 1/1 with admissions disabled, copied both entry pointers from saved versions, verified a valid hosted session and actual MP3 seek, then restored 2/2 and enabled admissions. Both tuples share the same library because this is the first release; this does not claim migration testing between different catalogs. `acceptance/live-operations.json` records the checks.

## New release or runtime change

1. Produce a new allowlisted immutable candidate; never edit the frozen release or sweep source folders into S3. Preserve fully analyzed MP3 qualification, all planner/model fingerprints and the original local pipeline.
2. Prepare a new context with `prepare.py`. Full image builds need 20 GiB free; verified thin builds with a matching basis receipt need 8 GiB and stop at 5 GiB. Use `build-image.py`; never prune unrelated projects. Build linux/amd64 and inspect expanded image below 10 GB.
3. Run appropriate tests, 60 frozen planner parity cases, original-vector checks and bounded full-worker memory checks. Full hashes are verified during build; startup uses manifest identity/sizes in the digest-pinned image. Do not reintroduce the unused audio tower or expensive repeated startup hashing.
4. Push an immutable ECR digest with `push-image.py`, inspect its scan and record architecture/size. Remaining documented critical/high OS findings are not a clean scan. Retain referenced images.
5. Repackage the API ZIP only for actual API changes; record S3VersionId/CodeSha256. `parameters.py runtime` hashes configuration into RuntimeRevision and changes both function configurations before version publication. WorkerConcurrency defaults 0 for staged work; current measured production is 1.
6. Generate templates and lint. Use `cloud-stacks.py plan`, then `review`, then `execute` for the exact named stack. Review replacements/removals before execution; only Lambda version replacement is normal. Do not paste private parameters into output.
7. Benchmark a materially changed worker in an isolated private text-only function with explicit budget/trial bounds. Keep the 3,008 MB account cap, one invocation at a time and no automatic replay after ambiguity. Force real cold environments using versions. Archive evidence and delete only the isolated stack afterward.
8. Exercise fixtures without admitting real paid jobs. Existing transaction fixture tools assume empty state and must **not** be rerun against the live populated table. Login smoke logs out its own session; understand its private cookie receipt lifecycle.
9. Upload explicit immutable objects first, save the complete prior tuple, deploy verified paired runtime/release and publish the two entry pointers last. `upload-assets.py` requires exact account, ACTIVE FREE subscription and hash/version verification. No broad directory sync.
10. Submit a bounded real prompt only within explicit scope. `activate-and-smoke.py` already has a successful receipt and deliberately refuses rerun; inspect rather than deleting its guard. `verify-live-operations.py` likewise already passed and is not a routine health probe.

## Remaining owner acceptance and costs

Test desktop/phone play/seek/queue/mix with the Mac disconnected. Automated IAB navigation was client-blocked; do not bypass it or claim HTTP checks establish browser listening. Shared session cookies expire after 24 hours and refresh through the API; S3 playback does not require the Mac or AI worker to stay on.

Use [cost scenarios](../../docs/cloud-library/first-release/serverless/COSTS.md), now based on 2.9375 GiB. At 900 jobs/month and 30/60 average billed seconds, modeled AWS totals are about $2.58/$3.91 with the optional S3 credit, excluding OpenAI/tax. Actual one-job worker compute was about $0.002834. No VM charge, warm-up scheduler or provisioned concurrency exists. Review real usage near 80 GB/800,000 CDN requests or 900 AI jobs; no automatic paid upgrade or monitor was created.

Local preview remains `node deploy/serverless/preview.mjs output/serverless-assets/candidate-1` on 4176 with deliberate API 503. Existing 4173/4174 servers are unrelated and untouched. Local audio/model/release copies remain intact.

## Fresh-visitor entry regression

Root and `/index.html` must redirect anonymous viewers to `/login/index.html` before requiring signed cookies. Default app-shell behavior is public; library/media behaviors remain signed. Never reapply TrustedKeyGroups to the default behavior: that prevented the login redirect with MissingKey. `cloud-entry-smoke.py` checks the real empty-cookie flow, protected denials, fresh login, exact audio range and logout, without AI calls. This is additional to API-only login tests.
