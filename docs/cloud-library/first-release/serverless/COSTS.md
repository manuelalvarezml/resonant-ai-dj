# First-release cost model

Deployment and measured acceptance: [live rollout](LIVE_ROLLOUT.md). This revision uses the actual **3,008 MB (2.9375 GiB)** worker. The original 8 GiB [inputs](cost-inputs-2026-10-02-8gib.json) and [results](cost-results-2026-10-02-8gib.json) are retained as historical scenarios.

Prices reviewed 2026-10-02, USD, us-east-2. **Planning estimates, not a bill or spending cap. OpenAI and taxes are excluded.** No AWS credit balance or free Lambda compute is assumed. CloudFront Free is verified ACTIVE for this release. Any future PAYG fallback requires a separate review.

## Monthly scenarios

| Workload | Jobs/month | Average billed worker time/job | Worker compute | AWS with eligible S3 credit | AWS without S3 credit |
|---|---:|---:|---:|---:|---:|
| Idle | 0 | 0 s | $0.00 | **$1.21** | $1.33 |
| Occasional | 100 | 30 s | $0.15 | **$1.36** | $1.48 |
| Regular | 300 | 30 s | $0.44 | **$1.67** | $1.78 |
| Daily cap average | 900 | 30 s | $1.32 | **$2.58** | $2.70 |
| Slower requests | 900 | 60 s | $2.64 | **$3.91** | $4.03 |
| Cold/slow stress | 900 | 300 s | $13.22 | **$14.58** | $14.70 |
| Timeout-duration stress | 900 | 360 s | $15.86 | **$17.25** | $17.36 |

Both columns assume the ACTIVE CloudFront Free plan covers the modeled workload. The second removes only its S3 storage credit; it is not PAYG. No bill or credit application has been observed yet. All durations include billable initialization; they are sensitivity cases, not average-latency predictions.

At 900 jobs averaging 30 billed seconds, worker compute is **$1.32** of approximately **$2.58** AWS total with the modeled credit; at 60 seconds, **$2.64** of **$3.91**. At 360 seconds, worker compute alone is $15.86. Sparse usage can make most jobs cold. Storage, logs and API usage remain conservative assumptions.

The one actual production job billed 57.881 worker seconds at 3,008 MB: approximately **$0.002834 worker compute**. End-to-end latency was 63.41 seconds. This is one observation, not a forecast. Generic probe compute, including failed/diagnostic candidates, was approximately $0.050873 total; other service charges and OpenAI are separate. The previous $44/month VM was never provisioned.

## Rates and assumptions

| Item | Unit price or allowance | Modeled use |
|---|---|---|
| S3 Standard | $0.023/GiB-month | 8 GiB total: library, models, retained release, results/cache; optional 5 GiB credit |
| S3 requests | GET $0.40/million; PUT/LIST $5/million | Baseline 10,000 GET and 1,000 PUT plus 5 GET / 4 PUT per job |
| Worker Lambda x86 | $0.0000166667/GiB-second; $0.20/million requests | 2.9375 GiB × billed duration × jobs |
| API Lambda | Same compute/request rates | 0.5 GiB and 0.1 billed seconds/call, an unmeasured assumption |
| HTTP API | $1/million requests at modeled tier | 1,000 base calls + (ceil(job seconds/5)+3) per job |
| DynamoDB Standard on-demand | $0.625/million WRU; $0.125/million RRU | 20 billable write units/job including transactions; one strong read unit/call, rows under 4 KiB |
| Private ECR | $0.10/GiB-month | 6 GiB stored unique compressed image layers retained; conservative retention allowance; final image has about 2.46 GiB compressed before deduplication across versions |
| CloudWatch | $0.50/GiB ingestion; $0.10/standard alarm-month | 0.1 GiB/month logs and four alarms |
| SQS Standard failures | $0.40/million requests | Three operations per failed job at assumed 1% failure |
| Ancillary allowance | $0.08/month, **budget assumption, not a tariff** | Small retained log/state storage, KMS decrypts, optional low-volume SNS email alerts and tiny direct result egress |
| SSM Standard, basic Budgets, IAM | No separate recurring fee for selected basic configuration | No advanced parameters, paid budget actions or customer-managed KMS key |

Exact public rate excerpts and source URLs are in [SOURCES.md](SOURCES.md). AWS request units differ by item/payload sizes and transactions; recompute if the proposed small records grow. API polling assumes a five-second steady interval without long queue waits; the initial two-second polling, retries and waiting can add calls. At these rates ordinary extra polls cost little, but an attack or buggy retry loop is outside the table. Logs, stored images and accumulated versions are also usage assumptions, not hard caps.

The ancillary allowance is intentionally explicit rather than pretending unknown sub-cent activity is zero. Replace it with measured categories in the first billing review. Direct S3 presigned result downloads bypass the CDN and can incur internet transfer; keep browser results compact, estimate actual bytes, and revisit that path if large or frequent. Audio never uses this direct path. Lambda internet transfer to the text provider is likewise not covered by CloudFront.

## Listening allowance

CloudFront Free publishes 100 GB/month and 1 million requests, subject to plan terms/eligibility. At a conservative 320 kbps, one hour of audio is about 0.144 decimal GB before headers and retries:

| Total listening hours/month | Approximate audio GB |
|---:|---:|
|20|2.88|
|100|14.4|
|500|72.0|

This excludes web/catalog traffic and replayed ranges. Library size does not equal monthly transfer. Review at 80 GB or 800,000 CDN requests; do not describe the plan as unlimited guaranteed delivery. Free-plan delivery adjustments and absence of a paid SLA matter if sustained usage exceeds allowances. [CloudFront plans](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/flat-rate-pricing-plan.html).

## Controls and exclusions

- Application default: 30 accepted attempts/day and 900/month globally, one running worker, three outstanding jobs, 360 s function timeout, 600 s queue age. Count clarifications/retries if they invoke paid work. A request cap does not cap storage, API abuse, logs, transfer or provider bills.
- No provisioned concurrency, warm-up scheduler, NAT Gateway, load balancer, EFS, MediaConvert or server. No paid CDN upgrade, domain or customer KMS key by default.
- Configured AWS notices: $5 actual and $10 actual; SNS email confirmation is still pending; they can arrive after usage and do not enforce a limit. Disable new AI jobs without disabling media when investigating costs.
- OpenAI retains the existing pinned project configuration. The existing translator does not retain the usage envelope; actual token charges from the single hosted test must be checked in the OpenAI project dashboard. Do not infer OpenAI cost from Lambda duration. Set the provider's available project limits separately and verify their enforcement semantics.
- Local container build is assumed; hosted builds, optional support, cloud benchmarks, staging resources, paid SnapStart/provisioned capacity, tax and domain are excluded. Benchmark costs are one-time additional usage and require a bounded run.
- If CloudFront Free is ineligible, compare PAYG allowances and geographic overage prices using actual account usage; do not silently substitute Pro/Business or retain a separately billed WAF without recosting.

## Recalculate

From the repository root:

```sh
python3 docs/cloud-library/first-release/serverless/calculate_costs.py
```

[Inputs](cost-inputs.json) own rates and assumptions. [Results](cost-results.json) are generated; do not hand-edit totals. The formula is jobs × memory GiB × billed seconds × compute rate, plus per-service usage. Independently, 900 × (3008/1024) × 30 × 0.0000166667 = $1.32187764375 for worker compute. Only the optional 5 ×$0.023 S3 credit is subtracted; no other free allowances are stacked.
