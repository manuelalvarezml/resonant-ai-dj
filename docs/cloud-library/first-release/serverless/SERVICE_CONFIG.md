# Service selections and exact starting settings

**2026-10-03: private playback and PlaylistIQ are live.** Read [deployment evidence and remaining owner acceptance](LIVE_ROLLOUT.md). The actual worker uses 3,008 MB; Free CDN is ACTIVE, all 15 final text probes passed and the production prompt returned ten matches. Earlier dated planning/preparation statements below are historical.

All regional services: **us-east-2**, selected profile **manueldev**, exact-account guard from the private target file. Global CloudFront and its WAF scope are exceptions; a later custom-domain ACM certificate belongs in us-east-1. Settings below are codified in the local candidate; live validation remains pending. See [IMPLEMENTATION.md](IMPLEMENTATION.md).

## CloudFront: prefer Free flat-rate, compatibility gate first

Use one standard distribution and all global edge locations (including South America). The Free plan lists $0/month, 1M requests, 100 GB delivery, 5 GB S3 Standard credit, five cache behaviors and included WAF. It lacks some custom policy features and a paid uptime SLA. Its allowances are not a license for unlimited sustained usage; delivery may be adjusted after significant excess. Verify account eligibility (including AWS Free Tier account restrictions), the exact config and subscription support before uploading audio. [S078–S079](SOURCES.md).

Use the following five behaviors, with no custom cache/origin-request policy requirement:

| Priority/path | Origin | Cache policy | Access |
|---|---|---|---|
| `/api/*` | API Gateway regional HTTPS origin | Managed CachingDisabled; AllViewerExceptHostHeader | App session/CSRF + secret origin header; login public but throttled |
| `/login/*` | site-media S3 REST/OAC | Managed CachingOptimized; object TTL 300 s | Public login HTML/assets only |
| `/library/*` | site-media S3 REST/OAC | Managed CachingOptimized; current no-cache (managed policy minimum 1 s), pages immutable | Trusted key group / signed cookies |
| `/media/*` | site-media S3 REST/OAC | Managed CachingOptimized; immutable | Trusted key group / signed cookies |
| Default `*` | site-media S3 REST/OAC | Managed CachingOptimized | Public allowlisted app shell; viewer-request function sends unsigned/expired document visits to login |

Default root index.html; distribute `/login/index.html` initially; S3 REST origins do not automatically resolve subdirectory index pages. Managed cache policies have a minimum TTL: do not use CachingOptimized on API/login responses with session cookies. `/login/` serves only static files; POST login is under `/api/`. Use HTTP→HTTPS redirect, TLS 1.2+, HTTP/2 and HTTP/3, IPv6, automatic text compression, OAC always-sign and no origin shield. Authenticated media cache keys omit listener cookies; CloudFront validates signed cookies separately. Forward no viewer cookies to S3. [Managed caching](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/using-managed-cache-policies.html), [API-origin policy](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/using-managed-origin-request-policies.html).

Use managed SecurityHeadersPolicy where supported; add app-specific CSP through a small response CloudFront Function if needed, not a paid custom-policy upgrade. No Lambda@Edge model/runtime. Limit WAF to the plan's five rules: scoped login rate rule, scoped API rate rule and only useful compatible protections after testing body/prompt false positives. Do not rate-limit normal media range bursts with the API threshold. Proposed API/login rates: API stage 10 requests/s burst 20; login 1 request/s burst 5 plus per-session/IP failure backoff. WAF is defense in depth, not an exact request/bill cap.

If Free is ineligible or cannot support signed cookies/origin secret/managed policies, **fallback to pay-as-you-go**, not automatic Pro/Business. PAYG has documented account-wide monthly allowances (1 TB delivery / 10M requests); check remaining eligibility/usage and geographic overage prices. Include separate WAF cost if retaining it on PAYG; otherwise use throttling/auth for the small password trial and acknowledge direct-login abuse risk. Decide with the owner from the concrete config/cost difference. No paid CDN subscription is selected now. [CloudFront FAQ](https://aws.amazon.com/cloudfront/faqs/).

## API Gateway and lightweight Lambda

Choose **HTTP API**, one default stage; no REST API, WebSocket API, cache cluster, custom API domain or VPC link. Target Node runtime with a published supported version at implementation, 512 MB memory, 10 s timeout, x86_64; do not pull ML dependencies into this function. Request/response JSON and cookies only. Reserve 5 executions after quota increase. IAM permission allows invoking only the worker production alias, not arbitrary functions. Session checks inside handler avoid a second Lambda authorizer invocation per poll.

Routes: login/logout/session refresh; POST playlist; GET job; static membership/release metadata if needed. Catalog pages and media bypass this service. HTTP API's 30 s integration ceiling is why submit immediately dispatches async work. API direct endpoint requires the CloudFront-origin secret. Authenticate before issuing any result URL. Payload 64 KiB; SDK integration uses session cookies correctly without forwarding the viewer Host as origin Host. [HTTP limits](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-quotas.html), [pricing](https://aws.amazon.com/api-gateway/pricing/).

## PlaylistIQ Lambda

| Setting | Starting value / choice |
|---|---|
| Deployment | Python 3.12, Linux x86_64 container, private ECR immutable digest and versioned alias |
| Memory | Benchmark at 8,192 MB, then 6,144 MB and 4,096 MB if each passes memory/latency/parity |
| CPU threads | Start 2 to match current model path; benchmark 4 only if it reduces billed GB-seconds without contention |
| Timeout | 360s; provider 30 s timeout retained; bound model work below remaining Lambda deadline |
| Concurrency | Reserved 1; API separately 5; no provisioned concurrency or periodic warmers |
| Filesystem | Read-only image with model assets; `/tmp` 512 MB for bounded job scratch/cache only |
| Dispatch | Native asynchronous Event; max event age 600 s; function-error retries 0; OnFailure → SQS Standard |
| Networking | **No customer VPC**; direct TLS to OpenAI/AWS; no NAT Gateway, EFS or load balancer |
| Secrets | Fetch only project OpenAI SecureString by role, cache briefly; no AWS keys or provider keys in image |
| Limits | 30 accepted attempts/day, 900/month, at most 3 outstanding; request budget separate from all-service dollar bill |

AWS allocates CPU with memory, so the cheapest memory size is not necessarily the cheapest completed request. Benchmark cold and warm end-to-end billed duration, peak memory, import/model-load time, selected scopes and result parity. New account memory eligibility is still unproven; the read-only quotas result did not establish access to 8 GB configurations. [Limits](https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html).

Bake the existing 2.663 GB model assets and the frozen planner/parity into the image, not MP3s or full raw-feature corpus. Verify expanded image below 10 GB; preserve file hashes. Adapt the pinned Debian/Python image using the Lambda runtime interface client or a tested AWS Python base image; use one architecture, no unsupported image attestations, and same-region ECR. Current Docker CMD/Node supervisor is not a Lambda handler. [Container rules](https://docs.aws.amazon.com/lambda/latest/dg/images-create.html).

Retain the frozen translator configuration: `gpt-5.4-mini-2026-03-17`, low reasoning, 30-second provider timeout and project-specific `AUTODJ_OPENAI_API_DEV_KEY` semantics. Do not silently select another model or a generic environment key. Cloud deployment stores the intended project key in the worker-only SSM parameter; this research does not call the provider.

Load the text model lazily **after** the durable job claim, then retain it in the execution environment for warm requests. Existing `cloud_text.bounded_encode` launches a new process on every cache miss; merely wrapping it would not yield a warm-model benefit. Refactor behind the encoder interface and prove unchanged vectors/ranking. `/tmp` is opportunistic, not durable. Hydrate/persist text-cache entries in private S3, keyed by model/sampling identity plus normalized text digest; never mix encoder versions. Validate actual Lambda memory accounting; the Mac psutil available-memory floor is not a Lambda quota guarantee.

**SnapStart is a later measured option, not categorically unsupported:** current AWS docs include Python 3.12+ and supported container images; restrictions include `/tmp` above 512 MB and EFS. Our first deployment leaves it off to avoid snapshot state/secret/randomness/restore concerns and unmeasured cache/restore charges. If cold starts fail the target, evaluate supported image hooks, refresh secrets and IDs after restore, and compare the actual bill. No promise that our existing custom image automatically qualifies. [Current SnapStart support](https://docs.aws.amazon.com/lambda/latest/dg/snapstart.html).

## Jobs, failures and secrets

| Service | Selection and integration | Rejected alternative |
|---|---|---|
| DynamoDB | One Standard on-demand table, no GSI/global tables/DAX; deletion protection; PITR off for disposable session/job state (immutable releases remain in versioned S3); TTL for sessions/jobs; strong reads/conditional transactions for quota and ownership; small rows, max on-demand throughput 50 RRU/s and 25 WRU/s if available | Provisioned free-tier capacity can be cheaper, but saves pennies here and adds capacity management; Standard-IA favors storage-heavy tables, not this request-heavy tiny state |
| Lambda async queue | Built-in dispatch; idempotency and incomplete-dispatch recovery in API; short reference-only payload | SQS FIFO primary queue adds poller/visibility tuning and can block behind a poisoned message; Step Functions adds orchestration we do not need for one bounded job |
| SQS Standard | Failure destination only, SSE-SQS, 14-day retention, queue policy grants only worker destination; alarm on messages; manual diagnosis/retry, no automatic consumer | FIFO/exact ordering offers no value for diagnostic failures; a dead-letter record does not automatically update DynamoDB state |
| Private ECR | One repository, immutable tags, digest-pinned deployment, AES256, basic scanning; keep active+previous referenced images; no automatic expiry until active/previous references are inventoried | Public registry, enhanced paid scanning, replication and image archiving unnecessary here |
| SSM Parameter Store | Separate Standard SecureStrings below 4 KB for project key, password hash, CDN signing key and origin secret; `aws/ssm`; exact-name IAM; no high-throughput mode | Secrets Manager is useful for managed rotation but not needed for four manually rotated values; priced separately if selected later |

[Database modes](https://aws.amazon.com/dynamodb/pricing/), [async config](https://docs.aws.amazon.com/lambda/latest/dg/invocation-async-configuring.html), [failure destinations](https://docs.aws.amazon.com/lambda/latest/dg/invocation-async-retain-records.html), [FIFO comparison](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/fifo-queue-lambda-behavior.html), [ECR](https://aws.amazon.com/ecr/pricing/), [SSM](https://aws.amazon.com/systems-manager/pricing/), [SecureString](https://docs.aws.amazon.com/systems-manager/latest/userguide/secure-string-parameter-kms-encryption.html).

## IAM, network, logs and address

Separate deployment, API and worker roles. Worker cannot read MP3s, change CDN/buckets or retrieve authentication secrets; API cannot read model/raw-feature objects or change releases. Both can access only their state prefixes/table keys as needed. Deployment uses named profile plus exact STS account guard, change-set review, Retain policies on persistent buckets/table/ECR. No broad `AdministratorAccess` runtime role and no copying ~/.aws to Lambda.

No VPC is needed because all dependencies are public managed service endpoints. Adding a private subnet would require deliberate outbound connectivity to OpenAI, often introducing NAT hourly cost. [Networking](https://docs.aws.amazon.com/lambda/latest/dg/configuration-vpc-internet.html).

CloudWatch: Standard logs, 7-day retention, structured request IDs/status/timing only; no audio, raw prompt, cookies, signed URLs or secrets. Four standard alarms initially: worker errors, API 5xx, failure queue messages, async event age > 300 s. Also inspect DestinationDeliveryFailures during acceptance and operations; add a fifth $0.10/month alarm if failure-destination permissions or reliability warrant it. Use native metrics; no custom high-cardinality metrics, Lambda Insights, full tracing or paid synthetic canary by default. Retain compact deployment/benchmark results locally. Use one SNS Standard topic with an owner-confirmed email subscription for those alarms; no FIFO, SMS, push or automatic remediation. Publish/email delivery charges fit the small ancillary allowance at trial volumes, but are usage charges. [SNS pricing](https://aws.amazon.com/sns/pricing/). No messages or subscriptions are created in this plan.

AWS Budgets: the candidate configures $5/$10 actual-cost notices for the whole selected account until app cost tags are activated. These are alerts, not a kill switch. Application disable flag rejects new jobs while media remains served; worker reserved concurrency 0 is an operator emergency stop with documented async failure-destination effects. OpenAI billing controls are separate. [Budgets](https://aws.amazon.com/aws-cost-management/aws-budgets/pricing/).

Use the generated CloudFront HTTPS hostname first. No Route 53 hosted zone, registration or standalone certificate is needed. If a custom name is later selected, reuse its DNS provider; request the CloudFront ACM certificate in us-east-1. Do not migrate an existing zone or buy a domain just to launch. [Default certificate](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/DownloadDistValuesGeneral.html), [ACM region](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/cnames-and-https-requirements.html).

## Real account prerequisite

Read-only evidence `output/cloud-preparation/serverless-account-readiness.json` reports concurrency 10 / unreserved 10. The original200 request was rejected by AWS as below the standard default1,000. A no-cost1,001 request is PENDING; after approval reserve1worker+5API, leaving995unreserved. The AWS 100-unreserved rule blocks that reservation at today's 10. Check supported memory/image quota separately and confirm service permissions. Do not silently drop the worker cap to get a deployment through. See CE024 and the private quota receipt; do not duplicate the pending request. [Concurrency rules](https://docs.aws.amazon.com/lambda/latest/dg/configuration-concurrency.html).

Implementation update: the Free subscription is an explicit PricingPlanManager CloudFormation resource in the us-east-1 edge stack, with a required associated WAF. Zero existing account subscriptions were observed; actual eligibility and ACTIVE status remain gates. Signed session tokens are random DynamoDB keys, so a separate session-signing secret is unnecessary.
