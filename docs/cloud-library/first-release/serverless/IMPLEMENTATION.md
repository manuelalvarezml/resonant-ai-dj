# Serverless implementation checkpoint — D072/E060

**2026-10-03: private playback and PlaylistIQ are live.** Read [deployment evidence and remaining owner acceptance](LIVE_ROLLOUT.md). The actual worker uses 3,008 MB; Free CDN is ACTIVE, all 15 final text probes passed and the production prompt returned ten matches. Earlier dated planning/preparation statements below are historical.

**Local candidate implemented and tested; cloud publication is pending.** On 2026-10-02 the owner accepted the serverless plan and requested the next step. This supersedes the previous “runtime not implemented” planning status. The original 187-track release, source audio, planner/model policy and existing 4173/4174 servers are preserved. No hosting resource, subscription, audio upload or paid model request was created. A no-cost Lambda quota request is now PENDING; see the continuation below.

## Implemented

| Boundary | Delivered |
|---|---|
| Python Lambda worker | Separate deployment adapter; conditional job claim, provider-start marker, fenced completion, durable S3 requests/results/full audits/text cache; no MP3 access |
| Text encoder | One warm model per execution environment, original sentence-by-sentence embeddings and cache identity, bounded temporary workspace; original fingerprinted planner files unchanged |
| API | Node 24, shared-password bcrypt login, separate random sessions, CSRF/origin checks, 24-hour signed CDN cookies, session-owned status/results |
| Admission | Atomic DynamoDB job/slot/day/month transaction; three outstanding jobs, 30/day and 900/month; same-key retry survives ambiguous dispatch; no automatic second logical provider attempt |
| Browser | Versioned static catalog/media; API failure does not block authorized static playback; asynchronous PlaylistIQ, persisted pending request keys, exact-origin/checksummed signed result downloads |
| Export | 187 immutable MP3 references, eight pages of at most 25 tracks, one mix with transition timestamps; only explicit approved files can upload; public results omit raw vectors |
| Infrastructure | Five linted templates: ECR, isolated benchmark, Ohio foundation, us-east-1 edge, Ohio runtime. Private S3 Standard/OAC, DynamoDB, HTTP API/Lambdas, Free subscription/WAF, SSM access, failure SQS, four alarms and cost alerts |
| Operations | Reproducible API ZIP, fresh allowlisted worker context, read-only preflight, bounded local/cloud probes, local key/config preparation, parameter assembly, checksum uploader and staged [runbook](../../../../deploy/serverless/RUNBOOK.md) |

The API and worker are separate functions. Catalog/audio GETs go to S3 through CloudFront; API Gateway never carries MP3 bytes. A valid signed cookie permits cached playback without a working API until the cookie expires. Fresh login and cookie renewal still require the API. This is not an “always available” guarantee across regional/CDN outages.

## Local evidence

- **123/123 player tests**, including static playback during API outage, immutable media identity, result integrity and reuse of a pending idempotency key.
- **16/16 API/edge tests**, including cryptographic cookie signature verification, CSRF, session ownership, quota/slot admission, duplicate and uncertain dispatch, expiry and login backoff.
- **24/24 Python worker/tool/infrastructure-boundary tests**, including provider-call fencing, tampering, late completion, cache identity and private bucket/media separation.
- All five CloudFormation templates pass `cfn-lint 1.57.1` with no findings. This validates template structure, not actual IAM propagation or DynamoDB behavior.
- Player syntax: **66 modules**; web build: **33 static files**. API dependencies are pinned with a lockfile; ZIP contains pure JavaScript dependencies and no secrets/native addons.
- Offline Linux x86 dependencies import successfully; frozen planner passes **60/60 cases, 187 tracks, five profiles**. Final candidate-4 verification exit 0, no OOM, no network; ~60.2 seconds. Host available-memory floor was not reached.
- Official AWS Lambda Runtime Interface Emulator **v1.37** successfully invoked the Python Runtime Interface Client. RIE binary SHA-256 `6b1e686e62ab2baf5759c412c4864276ef2a88b094fca53ec070637ccba9b9a5`. This is local runtime compatibility, not AWS execution.
- Browser at **127.0.0.1:4176** loaded all 187 tracks with the API intentionally returning 503. Actual MP3 playback advanced to 17 seconds; seeking and pause reached 18 seconds. DJ mixes showed one 10:09 example and transitions 3:23–3:52 / 6:47–7:16. No captured browser console errors. CloudFront cookies, S3 CORS and phone playback still need live acceptance.

### Measured Linux text/worker probes

These used a Mac-hosted Linux container with 4 GiB RAM, no swap, two CPUs, 512 MiB scratch, a 300-second stop and no network. Generic text only; no audio analysis or OpenAI.

| Probe | Cold | Warm | Peak resident memory | Result |
|---|---:|---:|---:|---|
| Two generic text descriptions | 33.77 s | 0.20 s | 2.99 GiB | One model load, exact repeated vector hashes |
| Full 187-track worker, fake translation/storage | 34.11 s | 2.62 s | 3.29 GiB | Ten matches each; exact original-adapter ranking/evidence; duplicate ignored |

Local speed does **not** choose the AWS memory allocation. The prepared AWS runner compares 8/6/4 GiB with at most 45 invocations, records billed duration and stops after ambiguous invocation outcomes. It never calls OpenAI. Provider latency and container initialization charges are absent from the local timings.

## Immutable identities and private artifacts

- Original release: `4a4bb92196ed75cc95ac19ec6a25bd5062ed31cdabb0eb30ebca0f83d5b5ff57`; 187 MP3s, 1,910,985,140 audio bytes. All 415 frozen release files were reverified during static export.
- Model manifest: `290d4489a8cf56321485950f838125b4d374c9dff50d78c106a8185850360070`; six assets, 2,663,055,739 bytes.
- Current worker context: `output/serverless-build/candidate-4`, build ID `3ad54cfad41a0f74f28b4f98b2738b1282d48684c227fedc12c57563b8dcbda7`, 59 files / 2,731,860,628 bytes. **Not a self-contained exported image.**
- Dependency image used for tests: `resonant-lambda:dependencies`, image config SHA `c23ef49fcc120a18dd277e516253b94a49cfb4e6e0d3de415784012693878b76`.
- Static/API candidate: `output/serverless-assets/candidate-1`; app ID `dbefa28c07c2d1da8fdcbfee8caf06896f3a6725791b56849b92403d8d3d7bb8`; 235 mapped objects. API ZIP: 5,047,597 bytes, SHA `2cb2b126e5df2071f8bb983fd4470167c2d806d83780a82cdf55b44ecb2e3679`. Root pointers publish last.
- Private local configuration: `output/serverless-private/first-release`, directory 700/files 600. Existing listener password reused through its hash; fresh RSA-2048 CDN key and origin secret. OpenAI field deliberately empty pending the intended hosted-key choice. No AWS credentials are packaged.

Raw local probe records/logs and preview screenshot live under `output/serverless-build` and `output/serverless-assets/candidate-1`. Keep output and full account identity out of Git. Frozen core source checksums still match; this task's Python implementation lives under `deploy/serverless/runtime`.

## Account and release gates

Read-only checks reconfirmed `manueldev`, personal account suffix **3649**, Ohio. Effective Lambda concurrency was **10**. AWS rejected the planned request for 200 because its request API requires a value above the standard default of 1,000. A request for **1,001** was accepted as **PENDING**; worker=1/API=5 reservations and app quotas are unchanged. Approval and effective quota readback remain pending. New-account memory eligibility still unproven. PricingPlanManager returned **zero subscriptions**; this establishes available subscription count, not eligibility approval.

New AWS documentation provides `AWS::PricingPlanManager::Subscription`. The edge template requests **FREE** explicitly and associates a CloudFront-scope WAF in us-east-1. It must reach ACTIVE before content upload; no silent paid fallback. See S111–S114 in [source updates](SOURCES.md). Managed policies and exactly five cache behaviors are used; WAF rates apply to API paths, leaving audio range bursts alone.

Before a live release: complete the self-contained image build/size check, wait for quota approval/readback and verify memory eligibility, run the bounded AWS benchmark, review real resource change sets, configure owner-selected OpenAI key and alert email, then execute fixture/auth/range/rollback acceptance before library publication. No custom domain is required.

## Failures and fixes retained

1. Initial Linux image install missed two Runtime Interface Client transitives because the package metadata summary omitted them. Linux wheel metadata identified `simplejson` and `snapshot-restore-py`; pinned installation and `pip check` passed.
2. Full image build reduced host free disk to ~3.5 GiB; stopped before export. Pruned only four identified task-owned duplicate build-cache records, reclaiming 8.127 GB; other projects' images/cache were untouched. Read-only model/release mounts enabled Linux tests. Require **20 GiB free** before another full export; last host observation ~11 GiB free. Docker Desktop remains running with the dependency image.
3. A handwritten Runtime API fixture timed out twice. Replaced with checksum-verified official AWS RIE; bootstrap passed. The failed fixtures are not cloud failures.
4. First player test run had four `listen EPERM` sandbox failures; authorized loopback rerun passed all 123 tests.
5. Template lint caught a CORS property spelling and a nonexistent DynamoDB IAM action; corrected to `ExposedHeaders` and the underlying item permissions used by transactions. Final lint clean.
6. Private configuration generation initially lacked its parent directory; fixed recursive mode-700 creation and reran successfully. No secret was printed or transmitted.

## Continue

Use [deploy/serverless/README.md](../../../../deploy/serverless/README.md) and [RUNBOOK.md](../../../../deploy/serverless/RUNBOOK.md). T034 remains **in progress** because final image export and live fixture acceptance are incomplete. Do not mark deployment complete from template lint, fake providers, localhost playback or prior VM evidence. Do not rerun corpus audio analysis or change ranking to make Lambda fit.

### Quota continuation — CE024

The owner’s request to prepare the accepted cloud plan was applied to the no-cost capacity prerequisite. AWS returned `IllegalArgumentException` for 200: “You must provide a quota value greater than the default quota value of 1000.0”. Readback confirmed effective quota10 and no prior request; submitting1,001 returned PENDING. One request exists, with private receipt at `output/cloud-preparation/serverless-quota-request.json`. This is a provider control-plane write, not paid compute or approval to publish. Do not submit duplicate requests or silently remove worker reservations.
