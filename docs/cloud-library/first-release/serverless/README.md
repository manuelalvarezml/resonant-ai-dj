# Resonant serverless launch plan

**2026-10-03: private playback and PlaylistIQ are live.** Read [deployment evidence and remaining owner acceptance](LIVE_ROLLOUT.md). The actual worker uses 3,008 MB; Free CDN is ACTIVE, all 15 final text probes passed and the production prompt returned ten matches. Earlier dated planning/preparation statements below are historical.

## 2026-10-02 — Serverless candidate implemented locally (D072/E060)

[Current implementation checkpoint](IMPLEMENTATION.md) supersedes the earlier plan-only status. Lambda worker, durable jobs/login, static playback transport, allowlisted export and five infrastructure templates are implemented locally. 123 player / 16 API-edge / 24 Python tests pass; offline Linux preserves all 60 planner cases. A separate preview on 4176 loaded 187 tracks and played/seeked audio with the API deliberately unavailable. Original release/model policy and 4173/4174 servers preserved.

One no-cost AWS quota request is now PENDING: concurrency 1,001 because AWS rejected 200 as below its standard default 1,000, despite the effective account limit of 10. App reservations remain worker=1/API=5. No compute/storage/subscription resource created, upload or paid model call. Final self-contained image export needs more disk (20 GiB free before build). CloudFront Free subscription is explicit in IaC; zero existing subscriptions observed, actual eligibility unproven. Hosted-key choice, alert email, real cloud benchmark/auth/ranges/rollback remain pending. Use the checkpoint and serverless runbook, not the historical VM provisioner. T034 remains in progress.

2026-10-02 — D071/E059, CD022/CE022/T033. **Researched plan, not deployed infrastructure.** The owner chooses S3/CloudFront playback plus on-demand Lambda PlaylistIQ. This supersedes the VM recommendation; retain its portable release and parity evidence. Do not run the old Lightsail provision/activation commands for this plan.

## Recommended configuration

| Job | Choice | Why it fits this release |
|---|---|---|
| Website, catalog and MP3 storage | Private S3 **Standard**, general-purpose buckets, Ohio | Immediate retrieval and multi-AZ storage; the tiny library offers only cents of potential tier savings |
| Continuous audio delivery | CloudFront **Free flat-rate plan**, subject to account/configuration eligibility | Managed delivery separate from AI, bounded CDN charges, adequate trial allowance |
| Login, submit and status | API Gateway **HTTP API** + small Node Lambda | One HTTPS origin, route throttles, short control requests |
| PlaylistIQ | Private Python container Lambda, **8,192 MB starting benchmark**, x86_64 | Runs only for playlist requests; preserves current CPU model/runtime |
| Jobs and quotas | DynamoDB **Standard, on-demand** | Durable status, session ownership, conditional idempotency and request counters |
| Dispatch | Lambda native asynchronous invocation | Built-in delivery queue; no primary SQS poller or Step Functions workflow needed |
| Failed invocations | One SQS **Standard** failure-destination queue | Retain failures for diagnosis; no automatic paid replay |
| Container registry | Private ECR, same region, immutable image digest | Holds the worker image including pinned model assets |
| Secrets | SSM Parameter Store **Standard SecureString**, AWS-managed key | Small number of manually rotated secrets, cached reads, no advanced tier |
| Operations | CloudWatch short-retention logs/basic alarms, AWS Budgets | Small bounded observability footprint; budgets warn rather than enforce a total bill cap |
| Initial address | Generated `https://<distribution>.cloudfront.net` | No domain purchase or DNS dependency for first launch |

Full settings and alternatives are in [SERVICE_CONFIG.md](SERVICE_CONFIG.md). This is a recommendation based on documented capabilities; cold-start performance is not yet measured.

## Expected cost

At the planning workload, target **roughly $1–9/month of AWS charges** for up to 900 playlist requests taking 30–60 billed seconds each, with the Free CDN plan eligible. This excludes OpenAI, tax and optional domain purchase. It is not a quote or cap. Slow 300–360-second requests materially change the answer and can erase Lambda's advantage. [Reproducible scenarios, rates and exclusions](COSTS.md).

The release's 1,910,985,140 MP3 bytes cost about **$0.041/month** in S3 Standard before credits, requests and retained copies. Standard-IA would save only about **$0.019/month** before retrieval costs. [Storage comparison](STORAGE.md).

## Findings that affect launch

- **Actual account quota is 10 regional concurrent Lambda executions**, verified read-only in `manueldev` / `manuel-web`, account suffix 3649, us-east-2. Request **200** before assigning worker=1 and API=5 reservations; AWS reserves 100 for unreserved functions. The request has not been submitted.
- CloudFront's Free flat-rate plan is different from pay-as-you-go free allowances. Eligibility and our exact five-behavior configuration must pass a preflight. Do not silently buy Pro/Business or stack both kinds of allowances.
- Our current VM Docker image is not a Lambda handler. Packaging, durable jobs, login/signed cookies and the HTTP adapter still need implementation. Frozen 187-track data, copied model assets and 60 parity cases can be reused.
- The first cloud URL does not require an owner domain. A later custom domain uses an ACM certificate in us-east-1 and the existing DNS provider.
- No inference, paid call, provider mutation, upload, quota request or deployment occurred during this research.

## Reading order

1. [ARCHITECTURE.md](ARCHITECTURE.md): request flows, availability boundaries, authentication and data contracts.
2. [STORAGE.md](STORAGE.md): S3 classes, exact costs, bucket layout, retention and recovery.
3. [SERVICE_CONFIG.md](SERVICE_CONFIG.md): each service's proposed settings and rejected alternatives.
4. [COSTS.md](COSTS.md): formulas, scenarios, known unknowns and spend controls.
5. [DELIVERY.md](DELIVERY.md): ordered implementation, acceptance and rollback.
6. [SOURCES.md](SOURCES.md): dated primary evidence and retrieval limitations.

The next work is the Lambda compatibility/cold-start proof and infrastructure-as-code implementation. Account quota and CDN-plan eligibility are parallel prerequisites. Owner inputs still needed for actual publication: hosted OpenAI key choice, shared-password acceptance/adjustment, budget envelope and an owner alert address. No credentials need to be pasted into chat.
