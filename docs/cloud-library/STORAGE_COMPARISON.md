# Cloud music storage comparison

## Decision and method

Shortlist B2 and R2 Standard for a later bounded comparison. Retain Spaces when a small bundled service reduces pilot setup effort. Do not select a provider from this desk study alone. The workload is private owned-audio storage with byte-range playback, direct uploads, media-worker reads and retained mix downloads.

Prices below are public USD observations accessed 2026-09-08, before taxes, negotiated discounts or separate services. Provider GB/GiB units and account-level allowances must be preserved in an invoice estimate. Recheck rates before expenditure. Requests, data durability claims and feature documentation are not measured performance.

## Commercial matrix

| Service | Current documented pricing basis | Retrieval / delivery caveat | Recommended disposition |
|---|---|---|---|
| Cloudflare R2 Standard | $0.015/GB-month; $4.50/million Class A and $0.36/million Class B; free-tier and billing-unit rules apply | Direct R2 egress free; Workers, logs and other services may charge | Finalist for playback-heavy workload |
| Backblaze B2 pay-go | $6.95/TB-month; standard A/B/C calls free, event-related exceptions | Free egress up to 3x average monthly storage, then $0.01/GB; partner routes need confirmation | Finalist for retained large libraries |
| DigitalOcean Spaces Standard | $5/month bundle: 250GiB storage and 1TiB outbound; extras $0.02/GiB and $0.01/GiB | Pool the bundle across the account; CDN traffic follows billing rules | Pilot alternative |
| Wasabi pay-go | Minimum 1TB; current example $7.99/TB with base-2 billing | Default 90-day minimum charges; regularly downloading above active storage is outside stated fit policy | Do not use as default playback/scratch store |
| AWS S3 Standard | Regional storage, request, transfer, optional replication and service charges | Selected-region rate quote required; direct internet delivery versus CDN is a separate model | Integration/residency reference; not priced winner |
| Supabase Storage Pro | Base plan from $25/month; 100GB storage then $0.0213/GB; separate 250GB cached and uncached outbound pools | Overages $0.03/GB cached and $0.09/GB uncached; other project charges possible | Convenient managed alternative; test full media bill |

Sources: [R2 pricing](https://developers.cloudflare.com/r2/pricing/) S001; [B2 pricing](https://www.backblaze.com/cloud-storage/pricing) S002; [Spaces](https://www.digitalocean.com/pricing/spaces-object-storage) S009; [Wasabi minimum](https://docs.wasabi.com/docs/how-does-wasabis-monthly-minimum-storage-charge-work) S004, [duration](https://docs.wasabi.com/docs/how-does-wasabis-minimum-storage-duration-policy-work) S005 and [egress policy](https://wasabi.com/pricing/faq) S006; [S3](https://aws.amazon.com/s3/pricing/) S007; [Supabase](https://supabase.com/pricing) S010 and [egress](https://supabase.com/docs/guides/platform/manage-your-usage/egress) S011.

B2's older $6 price and paid standard request assumptions are superseded by its [May price update](https://www.backblaze.com/blog/backblaze-pricing-and-product-updates/) S003. Supabase's billing overview rounds storage to $0.021 while the pricing page lists $0.0213; use the latter for this model and reconcile an actual invoice before procurement. Wasabi's interactive pricing page rendered zero placeholders; the current official minimum-charge documentation supplied the usable rate. S3 dynamic regional cells did not provide a sufficiently reliable quote here.

## Capability and integration matrix

“Documented” means a source advertises the primitive. Every selected-provider path still needs a contract test. “Verify” means this research does not establish the exact behavior.

| Requirement | R2 | B2 | Spaces | S3 | Supabase | Wasabi |
|---|---|---|---|---|---|---|
| SDK/local integration | S3 subset; Wrangler emulator available as a local option, parity untested | S3 subset/native API | S3 subset | Reference AWS SDK ecosystem | Storage SDK/TUS; application policy integration | S3-compatible offering; adapter spike required |
| Multipart / resumption | Documented S3 multipart; browser reselect separate | S3 multipart candidate; verify checksum/header details | S3 multipart candidate | Documented multipart | Documented TUS | Verify exact multipart behavior |
| Private signed access | S3 signed URL; custom domain differs | Signed S3 access candidate | Signed access/CDN interaction verify | Signed URL and IAM policies | Auth policies and signed access; verify revocation/cache | Verify scoped credentials and signing |
| Byte-range / seeking | Test private direct and worker paths | Test private endpoint and optional CDN | Test origin/CDN separately | Range primitive; test end-to-end | Test derivative and cached path | Test before reconsidering |
| Integrity | Own SHA-256 plus supported provider checksums | Same | Same | Multipart checksums; ETag is not canonical hash | Own hash; do not confuse TUS offset with integrity | Own hash; validate checksum mapping |
| Lifecycle / abandoned uploads | Documented lifecycle; verify expiry race | Verify lifecycle/version cleanup | Verify lifecycle limits | Documented lifecycle capabilities | Verify object+DB lifecycle coordination | Billing duration penalty distinct from deletion |
| Versioning / overwrite | No reliance on S3-versioning parity; use immutable keys | Verify native version/delete semantics | Verify exact API support | Native versioning available; still use logical source versions | Application revision model required | Verify version/object-lock retention |
| Regions / residency | Best-effort location hints; jurisdiction restriction is separate | Account/region placement | Regional buckets; verify desired region | Broad regional control; selected geography unresolved | Project region plus delivery path | Selected region and legal terms unresolved |
| Encryption | At-rest transport protections documented | Verify key management option for selected account | Verify selected service controls | Verify required KMS mode and costs | Verify storage/auth topology | At-rest documented; key controls to verify |
| Performance | Unmeasured | Unmeasured | Unmeasured | Unmeasured | Unmeasured | Unmeasured |
| Main lock-in | Worker bindings, cache/auth and event semantics | Native API/event/region semantics | CDN/bundle/API subset | IAM, events, managed service coupling | Auth/RLS/storage integration | Retention/commercial policy |
| Data exit | Reconstruct hashes and metadata in portable manifest | Same; egress volume matters | Same; bundle allowance applies | Same; transfer invoice matters | Export DB and objects separately | Deletion may leave minimum-duration charges |

Technical sources: [R2 compatibility](https://developers.cloudflare.com/r2/api/s3/api/) S013, [signing](https://developers.cloudflare.com/r2/api/s3/presigned-urls/) S012 and [location](https://developers.cloudflare.com/r2/reference/data-location/) S014; [B2 API](https://www.backblaze.com/docs/cloud-storage-s3-compatible-api) S017 and [regions](https://www.backblaze.com/docs/cloud-storage-data-regions) S018; [Spaces compatibility](https://docs.digitalocean.com/products/spaces/reference/s3-compatibility/) S019; [S3 multipart](https://docs.aws.amazon.com/AmazonS3/latest/userguide/mpuoverview.html) S020; [Supabase resumable uploads](https://supabase.com/docs/guides/storage/uploads/resumable-uploads) S022. Unknown cells are required follow-up work, not implicit support.

## Scenario math

The companion workbook calculates provider totals from one editable workload. A separate reference table models originals-only steady-state storage, excluding free tiers, requests, minimums, derivatives and backup:

| Original bytes, decimal GB | R2 storage/month | B2 storage/month |
|---|---:|---:|
| 25 | $0.375 | $0.17375 |
| 100 | $1.50 | $0.695 |
| 500 | $7.50 | $3.475 |
| 1,000 | $15.00 | $6.95 |

These small figures are not a subscription recommendation. They omit most service costs. The agent-readable model also includes low/normal/heavy traffic workloads and initial-upload times.

Let S be monthly-average decimal GB stored and E be chargeable GB leaving B2. Ignoring request/free-tier and routing differences, B2 costs 0.00695S + 0.01×max(E−3S,0); R2 costs 0.015S. Their simplified crossover is E=3.805S. This is arithmetic under listed rates, not evidence that a listener will generate that traffic. Count worker reads, exports, migration and cache misses in the applicable transfer path. Month-one average storage can be lower than end-month occupancy, so the B2 allowance should not use end-month bytes.

Avoid subtracting an allowance for every customer when it belongs to an account. R2 request billing rounds at the provider level; small fractional marginal costs do not predict a standalone invoice. Spaces uses GiB/TiB; convert decimal GB by 1.073741824 before its formula. Wasabi's minimum-duration charges require an object-age model, so the workbook reports only its retained-storage base and does not claim a full churn-adjusted invoice.

## Upload, analysis and playback traffic map

| Flow | Storage read/write | Other possible bill | Measurement needed |
|---|---|---|---|
| Browser → store | PUT / multipart requests; temporary parts | Browser bandwidth; optional upload middleware | Throughput and bytes resent |
| Store → worker | GET / range reads | Origin egress if applicable | Bytes per job and retries |
| Worker → store | Derivative/mix PUT | Worker-provider outbound | Result bytes, cross-cloud route |
| Store → owner | GET/HEAD/ranges | Origin/CDN/auth proxy | Playback bytes and request fan-out |
| Object → backup | Copy/GET and backup writes | Inter-region/provider transfer | Recovery cost and RPO |
| Account export | Reads of originals plus metadata | Download egress | Export size, expiry and retries |

A provider offering free outbound from storage does not waive another provider's outbound bill. A free CDN-partner route also does not imply private authentication, media delivery eligibility or zero CDN cost. Use a private direct origin for the first comparison and add CDN only when it has measured value.

## Candidate selection protocol

First resolve entity/geography, allowed processors, pilot cap, target library percentile and tolerated delivery bill. Then use equal file fixtures and an identical client in two providers. Proposed scope: generated or explicitly licensed test audio, two accounts/tenants, MP3 plus FLAC/WAV compatibility fixtures, 1MB–1GB files, 8–32MiB parts, 2–4 simultaneous transfers and a capped total dataset. No current music folders may be substituted.

Measure upload goodput, hash correctness, recovery after network interruption and browser restart, time to first audio, seeks at beginning/middle/end, expiring-URL recovery, cancellation, object visibility, deletion with caches and billable requests/bytes. Collect sample sizes, browser versions, origin region, client country and network conditions. Repeat cold and warm paths; do not rank providers with a single latency observation.

Proposed pass conditions: zero corrupted accepted objects; zero cross-tenant access in the defined matrix; at least 95% of interrupted test batches finish after resumption; p95 first-audio ≤3 seconds and seek ≤2 seconds on a stated broadband profile. These are product hypotheses and not vendor SLAs. If no finalist meets them at acceptable cost, revisit scope or region before adding complex infrastructure.

## Other routes screened out

Consumer Dropbox/Drive integration is useful for future bring-your-own-storage validation, but it adds OAuth permission, quota, link-revocation and sync conflicts. Treat it as a separate adapter, not as an assumed commercial media backend. Do not consume an individual's consumer storage allocation as pooled SaaS infrastructure.

Archive tiers are unsuitable as the default source for immediate playback and frequent rerendering. Self-hosted storage adds repair, backup, capacity and operator risk at an early stage. Multi-cloud replication, specialized search clusters and Kubernetes are deferred until measured requirements justify their recurring complexity.

Azure Blob and Google Cloud Storage were not deeply priced because entity/region is unresolved and the six-service comparison already yields a credible shortlist. Reopen them if residency, existing credits or a co-located worker materially changes total cost. This is a bounded research scope, not a claim that they are inferior.
