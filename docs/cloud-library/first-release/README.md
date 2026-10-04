# Resonant first cloud release

## 2026-10-03 — Private release live

[Open Resonant](https://dl3pumk9rpbun.cloudfront.net/). Private187-track playback and PlaylistIQ are active using S3 Standard/CloudFront Free and on-demand3008MBLambda. Production-key test returned ten matches in63.41seconds; real auth/ranges/rollback passed. Password location, measurements, recovery and remaining owner desktop/phone/email acceptance are in the [authoritative live checkpoint](serverless/LIVE_ROLLOUT.md). This supersedes the dated preparation statuses below.

## 2026-10-02 — Serverless candidate implemented locally (D072/E060)

[Current implementation checkpoint](serverless/IMPLEMENTATION.md) supersedes the earlier plan-only status. Lambda worker, durable jobs/login, static playback transport, allowlisted export and five infrastructure templates are implemented locally. 123 player / 16 API-edge / 24 Python tests pass; offline Linux preserves all 60 planner cases. A separate preview on 4176 loaded 187 tracks and played/seeked audio with the API deliberately unavailable. Original release/model policy and 4173/4174 servers preserved.

One no-cost AWS quota request is now PENDING: concurrency 1,001 because AWS rejected 200 as below its standard default 1,000, despite the effective account limit of 10. App reservations remain worker=1/API=5. No compute/storage/subscription resource created, upload or paid model call. Final self-contained image export needs more disk (20 GiB free before build). CloudFront Free subscription is explicit in IaC; zero existing subscriptions observed, actual eligibility unproven. Hosted-key choice, alert email, real cloud benchmark/auth/ranges/rollback remain pending. Use the checkpoint and serverless runbook, not the historical VM provisioner. T034 remains in progress.

**Active target: [serverless deployment plan](serverless/README.md), D071/E059.** S3 Standard/CloudFront keep the shared library available; Lambda runs PlaylistIQ on demand. Read the [service configuration](serverless/SERVICE_CONFIG.md), [cost scenarios](serverless/COSTS.md) and [ordered implementation/rollout](serverless/DELIVERY.md).

The selected AWS profile remains `manueldev` / `manuel-web`, account suffix 3649, us-east-2. The frozen 187-track library, model bundle and planner parity cases are reusable. Serverless implementation, account quota increase, Free-plan eligibility, cold benchmarks and deployment remain pending. No cloud resources have been created.

## Historical VM preparation — preserved evidence, superseded target

The following checkpoint records the earlier local VM kit. Its cost/hostname/deployment instructions do not govern the new target; the generated CloudFront HTTPS hostname removes the immediate custom-domain requirement.

Updated 2026-10-02 (America/Lima). **Local deployment preparation is implemented; cloud publication has not run.** Parent D070/E058; cloud CD021/CE021/T032. The owner selected AWS profile **`manueldev`**, verified as IAM user **`manuel-web`**, account ending **3649**, region **`us-east-2`**.

Use the same repository and one x86 Linux server for the web player, Python PlaylistIQ, and frozen library. Audio analysis stays on the Mac. The proposed Lightsail 8 GB / two-vCPU server is $44/month before tax and extras; that recurring charge still needs acceptance. The previous storage-only $5 estimate does not cover the current text-model runtime. See [provider evidence](PROVIDERS_AND_COSTS.md).

## Prepared now

- **187 fully analyzed MP3s**, 1,910,985,140 audio bytes. The complete immutable release is 2,075,449,410 inventoried bytes across 415 files, including public web assets, private features/vectors, planner snapshots and one existing mix.
- Separate production server: verified release loading, canonical HTTPS URLs, range playback, session-bound playlist jobs, one worker, timeout/process-tree cleanup and a persistent 30-prompt daily limit. Owner analysis/conversion/restore routes are absent.
- Frozen planner behavior for all five profiles; **60/60** portable parity cases pass. The original model/configuration and ranking are preserved.
- Six verified local model assets, 2,663,055,739 bytes plus their manifest. No audio analysis or model download was needed.
- Docker/Caddy configuration and scripts for guarded AWS provisioning, transfer, integrity checks, Linux acceptance, activation and rollback. Twelve deployment tests, syntax and Compose configuration checks pass; the service is not running yet.

Release ID: `4a4bb92196ed75cc95ac19ec6a25bd5062ed31cdabb0eb30ebca0f83d5b5ff57`.

**Start with [PREPARATION.md](PREPARATION.md)** for artifacts, verification, exclusions and the next exact actions. The executable operator guide is [deploy/first-release/README.md](../../../deploy/first-release/README.md).

## Remaining launch inputs and checks

1. Accept the proposed hosting cost and choose the HTTPS hostname. The account choice is settled; do not ask for a replacement profile again.
2. Use the generated shared-listener password as the v1 access default, or choose a different access policy before launch. Everyone admitted sees the same library; playlists/favorites remain browser-local.
3. Confirm the existing project OpenAI key is intended for hosted use, then place it privately in runtime configuration. Never paste credentials into chat.
4. Build and test the exact Linux image: clean imports, offline uncached MuQ text memory/latency, and frozen-query replay. The Mac's Docker daemon was stopped; Linux execution is still unverified.
5. Provision, transfer verified artifacts, configure DNS/TLS, then pass protected public playback, a real PlaylistIQ request, restart/rollback and phone-browser checks.

No server, upload, billable resource, DNS change or public URL was created by this preparation. The existing local servers on 4173/4174 were left running unchanged. No new inference, conversion or rendering was performed.

## Durable task records

| File | Purpose |
|---|---|
| [PREPARATION.md](PREPARATION.md) | Current implementation, artifact identities, tests and next steps |
| [DEPLOYMENT_PLAN.md](DEPLOYMENT_PLAN.md) | Architecture and ordered launch sequence |
| [ACCOUNTS.md](ACCOUNTS.md) | Selected AWS identity and remaining private configuration |
| [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md) | Completed evidence versus unrun launch acceptance |
| [RUNTIME_GAPS.md](RUNTIME_GAPS.md) | Historical initial audit, with current resolution pointer |
| [PROVIDERS_AND_COSTS.md](PROVIDERS_AND_COSTS.md) | Dated primary sources and cost assumptions |

The explicit request to prepare everything before deployment supersedes older implementation holds for this local preparation. It does not accept a recurring hosting charge. Historical multi-user discovery gates and economics are retained; none is falsely marked passed. Update this folder and the cloud registers/events after each deployment step. Never commit music, features, models, configuration secrets or full AWS account identity.
