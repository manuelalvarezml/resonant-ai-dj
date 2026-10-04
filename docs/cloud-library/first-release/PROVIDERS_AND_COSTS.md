# Provider choice and cost notes

> **Superseded deployment target, 2026-10-02 (D071):** this is the preserved VM preparation/evidence. The active target is the [serverless plan](serverless/README.md). Do not run these VM deployment steps for the serverless release; portable library/model/parity artifacts remain reusable.

Reviewed 2026-10-02. Primary documentation only; no purchases, account creation, provider benchmarks or inference. Prices exclude tax, domain, optional backups, transfer overages and OpenAI usage unless explicitly stated. Recheck checkout/region before provision.

## Recommendation

Use one portable Linux deployment. **AWS Lightsail is the fastest existing-account candidate** with owner-selected `manueldev`, once $44/month is accepted. It avoids new-provider onboarding and preserves the current Python/Node application. An 8 GB machine is a conservative trial size, not an experimentally established requirement; a successful measured 4 GB test could reduce cost later.

| Route | Current evidence | Decision for this release |
|---|---|---|
| AWS Lightsail Linux / public IPv4 / 8 GB | $44/month maximum bundle charge; 2 vCPU, 160 GB SSD, listed 5 TB transfer (region-dependent) | Selected AWS route; recurring cost acceptance pending; no GPU or separate storage service needed |
| AWS Lightsail Linux / public IPv4 / 4 GB | $24/month; 2 vCPU, 80 GB SSD | Only after uncached text peak-memory testing; do not risk launch on an untested smaller tier |
| Hetzner CX33 / EU / 8 GB | 4 vCPU, 80 GB; published new base price $9.99 or €8.49, excluding IPv4 and tax | Lower-cost alternative; account/token not configured and public catalog currently labels it unavailable. Console capacity is unverified; not a guaranteed ASAP route |
| Cloudflare Workers + R2 plus a Python host | R2 may cover this small audio library in its storage free tier; Workers runtime memory is 128 MB | Retain for later. Multiple services and a separate model runtime are needed; static deployment alone does not preserve PlaylistIQ |

AWS prices/specifications are from [Lightsail bundle documentation](https://docs.aws.amazon.com/lightsail/latest/userguide/amazon-lightsail-bundles.html) (S065). No free trial/credits assumed. Read-only metadata now confirms `large_3_0` and `ubuntu_24_04` active in the selected `us-east-2` region. STS and metadata permissions pass; mutation permissions, quota and capacity remain untested.

Hetzner data: [June 2026 price adjustment](https://docs.hetzner.com/general/infrastructure-and-availability/price-adjustment/) (S066), [current cost-optimized catalog](https://www.hetzner.com/cloud/cost-optimized/) (S067), and [billing FAQ](https://docs.hetzner.com/cloud/billing/faq/) (S068). Budget roughly $12–15/month before tax for an available CX33 with IPv4 and optional backup allowance; that is a planning allowance, not a checkout quote. Backups cost 20% of server price. Account approval, EU latency and capacity may delay this route. Do not automatically choose a more expensive tier if unavailable.

Cloudflare references: [R2 pricing](https://developers.cloudflare.com/r2/pricing/) (S072) and [Workers limits](https://developers.cloudflare.com/workers/platform/limits/) (S069). R2 Standard includes 10 GB-month free and free direct egress, with request allowances. A normal Worker cannot host the current multi-gigabyte PyTorch model path within its 128 MB isolate. This claim concerns the ordinary Workers runtime, not every Cloudflare compute product.

## Workload and money boundaries

The frozen release is 2.075 GB, including 1.911 GB of MP3s, one 26 MB example mix, public catalog, raw features and planner snapshots. Model assets add about 2.663 GB, plus rebuilt Linux dependencies. Disk needs include temporary uploads, an old release and caches; ≥30 GB is a planning minimum, well within the proposed bundled disk. Do not copy the 1.672 GB Mac virtual environment.

At 320 kbit/s, music delivery is approximately 0.144 GB/listening-hour before overhead: 100 shared listening hours would be 14.4 GB. This arithmetic is not measured traffic. Viewers share one library, so storage is not multiplied by the number of people who receive the link.

OpenAI charges are separate and unestimated until actual configured-model token usage is measured. Retain existing model selection, measure a small bounded request, and choose an application request/usage limit. A provider budget alert is not a guaranteed cutoff. Do not claim “free hosting” from R2's allowance while omitting the Python host.

The [old economics revision 2.0](../UNIT_ECONOMICS.md) stays intact as historical 1/3/10-user storage-only modeling. These new one-library estimates do not overwrite that workbook or imply a budget increase was accepted.

## HTTPS and access references

[Caddy automatic HTTPS](https://caddyserver.com/docs/automatic-https) and [hashed basic authentication](https://caddyserver.com/docs/caddyfile/directives/basic_auth) (S070–S071) support the proposed proxy/access approach. Trusted certificate issuance depends on the selected hostname/address and ACME validation; it has not been tested here. Authentication configuration must cover media and API, with no plaintext password in the checked-in Caddyfile.
