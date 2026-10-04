# Sources and evidence — serverless launch

Reviewed 2026-10-02. These are primary documentation/price observations, not deployment or performance acceptance. Refresh before provisioning and prices after 30 days. Unknown page publication dates remain null. Current source observations are preserved separately from the earlier VM and broad cloud research.

## Source index

- **S073** — [S3 pricing](https://aws.amazon.com/s3/pricing/). Storage, request and retrieval pricing; separate class minimums.
- **S074** — [S3 storage classes](https://docs.aws.amazon.com/AmazonS3/latest/userguide/storage-class-intro.html). Availability, minimum durations and restore behavior differ by class.
- **S075** — [S3 FAQ](https://aws.amazon.com/s3/faqs/). Standard spans multiple AZs; binary units apply to storage billing.
- **S076** — [S3 Ohio public price list](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonS3/current/us-east-2/index.json). Standard $0.023/GB-month, IA $0.0125 plus retrieval $0.01/GB; saved rate excerpts.
- **S077** — [CloudFront S3 origin access control](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/private-content-restricting-access-to-s3.html). OAC supports private S3 REST origins with distribution-scoped bucket access.
- **S078** — [CloudFront flat-rate plans](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/flat-rate-pricing-plan.html). Free plan feature/usage limits, eligibility constraints and plan lifecycle; verify exact proposed configuration before subscribing.
- **S079** — [CloudFront pricing](https://aws.amazon.com/cloudfront/pricing/). Flat-rate and pay-as-you-go are distinct billing choices.
- **S080** — [CloudFront range requests](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/RangeGETs.html). Range GET delivery allows progressive media playback and seeking.
- **S081** — [CloudFront private content](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/private-content-overview.html). Trusted signing keys and private-content access; supported key types.
- **S082** — [CloudFront signed cookies](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/private-content-signed-cookies.html). Signed cookies grant bounded access to multiple files; expiry still applies to subsequent requests.
- **S083** — [CloudFront managed cache policies](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/using-managed-cache-policies.html). CachingDisabled for dynamic API; minimum TTL matters for static policies.
- **S084** — [CloudFront managed origin request policies](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/using-managed-origin-request-policies.html). AllViewerExceptHostHeader supports API Gateway origins without forwarding viewer Host.
- **S085** — [CloudFront FAQ](https://aws.amazon.com/cloudfront/faqs/). PAYG monthly allowances must not be stacked with flat-rate plan usage.
- **S086** — [Lambda quotas](https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html). Memory, image, timeout, payload and temporary-storage limits; new-account quotas may be restricted.
- **S087** — [Lambda container images](https://docs.aws.amazon.com/lambda/latest/dg/images-create.html). Read-only image, runtime interface client, single architecture and same-region ECR requirements.
- **S088** — [Lambda SnapStart](https://docs.aws.amazon.com/lambda/latest/dg/snapstart.html). Current support includes Python 3.12+ and supported containers; restrictions and snapshot/restore charges require measurement.
- **S089** — [Lambda asynchronous error handling](https://docs.aws.amazon.com/lambda/latest/dg/invocation-async-error-handling.html). Delivery can duplicate; throttle/system retries differ from function-error retry settings.
- **S090** — [Lambda asynchronous configuration](https://docs.aws.amazon.com/lambda/latest/dg/invocation-async-configuring.html). Maximum event age and function error retry controls.
- **S091** — [Lambda failure destinations](https://docs.aws.amazon.com/lambda/latest/dg/invocation-async-retain-records.html). Retain invocation records through destinations and monitor failed destination delivery.
- **S092** — [Lambda concurrency](https://docs.aws.amazon.com/lambda/latest/dg/configuration-concurrency.html). Reserve 100 executions for unreserved functions; reserved concurrency is not prewarmed capacity.
- **S093** — [Lambda internet access](https://docs.aws.amazon.com/lambda/latest/dg/configuration-vpc-internet.html). Customer VPC networking changes outbound internet requirements.
- **S094** — [Lambda pricing](https://aws.amazon.com/lambda/pricing/). GB-second billing and request charges; provisioned concurrency and SnapStart introduce other charges.
- **S095** — [DynamoDB pricing](https://aws.amazon.com/dynamodb/pricing/). On-demand request units and storage differ from provisioned capacity; class tradeoff.
- **S096** — [DynamoDB TTL](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/TTL.html). Expired rows can remain for days; logical expiry must be checked in application.
- **S097** — [API Gateway pricing](https://aws.amazon.com/api-gateway/pricing/). HTTP API request-based pricing; selected Ohio rate in saved regional excerpts.
- **S098** — [HTTP API quotas](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-quotas.html). Short integration timeout motivates asynchronous submission/status API.
- **S099** — [ECR pricing](https://aws.amazon.com/ecr/pricing/). Private image storage $0.10/GB-month; same-region transfers to Lambda not charged as internet egress.
- **S100** — [SQS pricing](https://aws.amazon.com/sqs/pricing/). Standard queue request pricing; monthly allowance not deducted in conservative model.
- **S101** — [SSM pricing](https://aws.amazon.com/systems-manager/pricing/). Standard parameters at standard throughput avoid advanced parameter/API charges.
- **S102** — [SecureString encryption](https://docs.aws.amazon.com/systems-manager/latest/userguide/secure-string-parameter-kms-encryption.html). Standard values limited to 4,096 bytes; AWS-managed aws/ssm key can encrypt them.
- **S103** — [AWS Budgets pricing](https://aws.amazon.com/aws-cost-management/aws-budgets/pricing/). Basic monitoring notifications versus paid action/report features; alerts are not a hard spending cap.
- **S104** — [CloudFront default hostname/certificate](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/DownloadDistValuesGeneral.html). Generated distribution domain supports initial HTTPS without an owner domain.
- **S105** — [CloudFront custom HTTPS certificate](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/cnames-and-https-requirements.html). ACM certificate for CloudFront belongs in us-east-1.
- **S106** — [S3 versioning](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Versioning.html). Previous versions consume storage and remain recoverable according to lifecycle.
- **S107** — [CloudWatch pricing](https://aws.amazon.com/cloudwatch/pricing/). Logs and alarms have distinct charges; regional rate excerpts preserved.
- **S108** — [SNS pricing](https://aws.amazon.com/sns/pricing/). Standard publish and email delivery priced separately; low-volume alert wiring only.
- **S109** — [Secrets Manager pricing](https://aws.amazon.com/secrets-manager/pricing/). Secret-month charge makes it unnecessary for manually rotated v1 secrets.
- **S110** — [FIFO Lambda behavior](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/fifo-queue-lambda-behavior.html). Serial message-group processing is an alternative, not the chosen dispatch path.

## Saved observations and reproducibility

- [S3 regional rate excerpts](serverless-s3-rates.json) and [service rate excerpts](serverless-service-rates.json) retain public offer URLs, publication dates, units and tier ranges. The latter includes Lambda, API Gateway, DynamoDB, ECR, SQS, CloudWatch and the rejected Secrets Manager alternative. No credential/account data is included.
- [Cost inputs](cost-inputs.json), [offline calculator](calculate_costs.py), [calculated output](cost-results.json) and [interpretation](COSTS.md) form a separate first-release model. Historical multi-user acquisition/economics remain unchanged.
- Read-only `output/cloud-preparation/serverless-account-readiness.json`: selected profile `manueldev`, account suffix 3649, us-east-2; regional and unreserved Lambda concurrency both 10. CloudFront Free eligibility has not been checked. An ARM microVM quota returned by Service Quotas is not evidence that the proposed x86 function can allocate 8 GB.
- Actual account identity was already established under D070; no new credential source or account was selected. No secrets were printed or copied into these documents.

## Retrieval failures and limits

The initial public price endpoints using offer codes `AmazonSQS` and `AmazonEC2ContainerRegistry` returned HTTP404. The AWS offer index identified the correct codes `AWSQueueService` and `AmazonECR`; those succeeded and their excerpts are retained. This was an endpoint-name correction, not a service outage or absence.

CDN Free-plan subscription compatibility, Lambda memory eligibility, expanded image size, model cold starts, queue correctness and real-device latency remain unmeasured. Region choice keeps data/compute together in the already selected Ohio account configuration; CloudFront places playback near listeners. No claim is made that Ohio minimizes every possible API latency or that this plan guarantees uninterrupted global playback.

Research and arithmetic validation are local/read-only. No provider resource, quota request, subscription, alert message, upload, inference or paid OpenAI request was performed.

### S111 — CloudFront pricing-plan API announcement

[AWS primary source](https://aws.amazon.com/about-aws/whats-new/2026/09/cloudfront-flat-rate-pricing-plans-api/), reviewed 2026-10-02. Programmatic plan management now available; Free activation differs from paid approval. See [implementation](IMPLEMENTATION.md) for actual local evidence and remaining limits.

### S112 — CloudFormation PricingPlanManager Subscription

[AWS primary source](https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-resource-pricingplanmanager-subscription.html), reviewed 2026-10-02. Explicit FREE subscription resource requires distribution and CloudFront-scope WAF; us-east-1 edge stack. See [implementation](IMPLEMENTATION.md) for actual local evidence and remaining limits.

### S113 — Managed origin request policies

[AWS primary source](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/using-managed-origin-request-policies.html), reviewed 2026-10-02. AllViewerExceptHostHeader supports API Gateway origins and forwards viewer cookies/headers without the viewer Host. See [implementation](IMPLEMENTATION.md) for actual local evidence and remaining limits.

### S114 — Lambda Runtime Interface Emulator v1.37

[AWS primary source](https://github.com/aws/aws-lambda-runtime-interface-emulator/releases/tag/v1.37), reviewed 2026-10-02. Official Linux x86 emulator used for local RIC bootstrap, with verified published asset checksum. See [implementation](IMPLEMENTATION.md) for actual local evidence and remaining limits.

### S115 — Lambda new-account memory restrictions

[AWS primary source](https://docs.aws.amazon.com/lambda/latest/dg/troubleshooting-deployment.html), reviewed 2026-10-03. New-account memory restrictions can be lower than the published standard; memory-limit increases cannot be requested. Actual function creation in the selected account rejected 8,192 MB with a 3,008 MB maximum despite concurrency 1,000. The final 3,008 MB worker passed AWS acceptance; see [live evidence](LIVE_ROLLOUT.md). Earlier account/eligibility statements above describe their dated read-only snapshot.
