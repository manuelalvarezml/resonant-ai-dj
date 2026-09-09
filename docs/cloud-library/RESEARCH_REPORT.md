# Cloud music library research report

## Recommendation

Continue focused discovery for a private DJ library product. Do not authorize the complete cloud service on the current evidence. A credible product could combine a small-crate upload, trustworthy descriptor browsing, private playback, editable prompt playlists and eventually reproducible downloadable mixes. The commercial and technical case for that combination remains conditional.

The best initial storage comparison is Backblaze B2 versus Cloudflare R2 Standard, with DigitalOcean Spaces retained as a simple pilot option. B2 is attractive for large retained libraries and moderate downloads. R2 becomes more attractive when delivery volume and transfer predictability matter. The choice must include worker traffic, request fan-out, authentication and geographical playback measurements, rather than storage price alone.[^1][^2]

This is a discovery decision, not provider procurement. Market interviews, upload observation, commercial rights review and a tightly bounded portability spike remain prerequisites. A library-only pilot and an automatic-mix pilot should have separate go/no-go decisions so a problem in automatic mixing does not force untested promises into library playback.

## Product opportunity and substitutes

The intended primary customer is a DJ who owns digital tracks, repeatedly organizes crates and wants to review music away from the main workstation. The job is preparation and rediscovery, with an exportable result. A general-purpose personal streaming service has a weaker starting position because inexpensive and free alternatives already serve private collections.

rekordbox combines cloud library management with its established performance workflow. Its Professional plan currently advertises 5TB of Dropbox storage at $36 monthly or $360 annually. Lexicon offers DJ library management, conversion and cloud storage features. These products make compatibility, cue/playlist preservation and trust important switching considerations.[^3][^4] This project should initially complement a DJ's existing software. Native DJ database writes and cue round-tripping require a later integration decision.

iBroadcast advertises a $3.99 monthly premium personal locker. YouTube Music supports up to 100,000 personal uploaded songs, and Plexamp offers personal-library listening and discovery through Plex Media Server.[^5][^6][^7] These are strong reference alternatives for interviews. Their advertised features do not establish their active-user counts or this project's addressable market. No defensible paying-DJ market-size estimate was established in this research; do not convert broad streaming-industry revenue into a claimed market for owned-file cloud tools.

The product hypothesis should therefore be tested feature by feature. Ask whether a prospective customer would pay for better crate preparation, remote auditioning, reliable metadata correction, or a finished mix. A request for more backup space is not automatically demand for AI. Interest in AI is not evidence of willingness to upload a collection or pay a subscription.

## Initial upload is a first-order constraint

The roadmap's one-large-upload assumption is too expensive to make mandatory before value. At 20Mbps upload and 70% useful transfer efficiency, 25GB takes about four hours, 100GB roughly sixteen hours, and 500GB roughly seventy-nine hours. These are calculated transfer scenarios, not user measurements. Device sleep, browser restarts, hashing, retries and unsupported files can extend them.

Start with a deliberately selected 20–100-track crate. Show the byte total, estimated transfer time, supported formats and missing-tag risks before transfer. Let completed files become usable while the rest upload. Make paused, retried, quarantined and unsupported files visible separately. Offer incremental additions through another explicit folder/file selection.

A browser cannot be assumed to watch a folder indefinitely or retain permission through all browser/device lifecycle events. The MVP should promise resumable batch imports where the tested browser supports them. A dedicated sync helper remains deferred; full bidirectional sync is a different product commitment.

## Storage and delivery

The provider comparison has six directly reviewed services and a bounded shortlist. B2's current advertised standard price is $6.95/TB-month, with free egress up to three times average monthly stored data. R2 Standard is $0.015/GB-month with paid request classes and no direct egress fee. Wasabi's pay-go minimums and recurring egress-fit policy require special care for active listening and short-lived render outputs.[^1][^2][^8]

DigitalOcean Spaces includes storage and outbound transfer in a small account-level bundle. Supabase combines database/auth convenience with storage, but separate cached and uncached egress charges can matter for a media product.[^9][^10] A managed database/auth service can still be paired with separate object storage. That introduces an authorization bridge that must be tested: database ownership checks do not automatically protect a separate bucket.

For initial playback, prefer private original MP3 playback over HTTP byte ranges when tested browsers handle the file correctly. Use a separately identified browser derivative only when needed. Keep originals, derivatives, mix masters, compressed exports and worker scratch distinct. HLS should be introduced only if measured network, seeking or device requirements justify its segment processing and operational cost.[^11]

Public caching is incompatible with the proposed private-library boundary unless authorization is enforced before every cache delivery and the cache cannot cross tenants. Expiring URLs are bearer capabilities, not DRM. A downloaded track cannot be revoked from a device. R2 presigned S3 URLs also cannot simply be moved to a custom-domain URL.[^12]

## Architecture and reusable components

Prefer a modular service with managed relational metadata and authentication, private object storage, a durable job queue, and separate bounded media workers. Keep a thin application API responsible for authorization and billing/quota reservations. Upload bytes should go directly to storage, while the application confirms integrity and ownership before a file becomes playable.

The existing Python playlist package and engine should remain independently versioned. A cloud application consumes their contracts through explicit adapters. The current implementation is local, and the current MLX analysis stack is optimized for Apple Silicon. Ordinary Linux CPU or GPU jobs require a verified implementation path and comparative outputs. Upstream availability is not a portability test.

Do not run long analysis or rendering within ordinary web requests. Lambda's documented 15-minute invocation ceiling illustrates why execution limits must be evaluated. Container jobs support a different execution envelope, but long permitted runtimes do not make a job economical or reliable.[^13][^14] Begin with CPU metadata/decode work and separately benchmark any heavy analysis worker under explicit limits.

The proposed contracts include tenant-scoped identities, immutable source versions, upload reservations, analysis evidence, catalog snapshots, playlist runs, validated plan artifacts, render jobs and manifests. At-least-once queue delivery requires idempotent effects and bounded retries. “Exactly once” should not be a system claim.

## Analysis and AI quality

The current larger catalog has 120 tracks, with normalized genre metadata on 62 and embedded BPM on 22. Mood, energy and vocal evidence are missing. This is a local project observation from D040/E028 and D041/E029, not a representative market sample. A model can interpret “energetic house,” but cannot establish that a retrieved track is energetic when that evidence is absent.

Encoded fields, measurements, estimates, proposals and user corrections must retain their exact authority labels. A confidence score is not a substitute for validation. User corrections should overlay a derived value without erasing raw metadata or historical analysis. Catalog coverage is a separate quality metric from prompt interpretation.

Automatic plan generation remains deferred. The future model may propose track IDs and bounded operations, but code must resolve tenant ownership, validate sources and timing references, reserve quota, enforce DSP limits and execute an approved plan. Reproducibility means pinning inputs, plan, tool versions and environment. Byte-identical output across architectures is a stronger claim requiring a separate test.

The local accepted three-track v2 mix is evidence that the timing/EQ baseline can work in one case. It is not evidence for broad genres, larger sets or commercial delivery quality. The +1.04 dBTP warning, listening coverage and cloud portability are independent gates.

## Rights and privacy

Personal ownership of a file does not itself settle the service's rights to store, transform, stream or distribute it. The launch jurisdiction and operating entity are still unknown. A qualified review must distinguish private storage, owner playback, analysis copies, downloadable derivative mixes, public sharing and third-party performance. U.S. Section 512 safe harbors are conditional liability provisions, not blanket music licenses.[^15]

Software and model licensing deserves a separate gate. Essentia's vendor describes AGPL/commercial licensing and distinct pretrained-model restrictions; FFmpeg licensing depends on the compiled features. A repository's MIT label does not clear every transitive dependency or model artifact.[^16][^17] The current local prototype is not automatically approved for a commercial network service.

A private product should not claim end-to-end encryption while server-side workers can decode audio. Proposed controls include encryption in transit/at rest, tenant isolation, minimal operator access, lifecycle deletion and an export path. Regional privacy requirements depend on who operates the service and whom it targets.

For text translation, preserve the current minimal-data approach. Avoid audio, raw library paths or whole-catalog uploads to the language model. OpenAI's application-state controls and abuse-monitoring retention are distinct; setting store=false is not equivalent to an approved zero-retention arrangement.[^18]

## Economics and decision gates

Price by constrained storage and bounded processing, not an unlimited promise. Stored originals are only one cost: derivatives, backups, version history, transient uploads, retries, worker reads/writes, prompt tokens, support, payment fees and trial abuse also matter. Acquisition and initial analysis create cash expenses before recurring revenue.

The included model separates provider storage/delivery estimates from whole-service contribution scenarios. Compute and support inputs are clearly labeled assumptions pending measurement. Profitability is not asserted. At early scale, fixed operations and support can dominate the difference between storage vendors.

The full-build gate remains open until evidence supports all of the following: recurring customer need, acceptable upload completion, usable private playback, maintainable tenant isolation and deletion, viable licensed analysis, credible quality/reproducibility, sustainable cost and explicit implementation authorization. If demand centers on local preparation with little willingness to upload, a local-first or selective-cloud direction should replace the full-library hypothesis.

## Research limitations

No customers were contacted; no accounts, cloud resources or uploads were created; no new audio analysis or render was run. Competitor features were assessed from their own documentation. Provider latency, real cache hit rates, support burden, churn and willingness to pay are unmeasured. Exact regional S3 prices and some dynamic competitor prices were not reliably extracted and are registered as gaps.

The reports provide a practical specification for answering these questions. They do not mark the unanswered gates complete.

## Sources

[^1]: Cloudflare, [R2 pricing](https://developers.cloudflare.com/r2/pricing/), updated August 7, 2026. S001.
[^2]: Backblaze, [B2 pricing](https://www.backblaze.com/cloud-storage/pricing), accessed September 8, 2026. S002.
[^3]: AlphaTheta, [rekordbox plans](https://rekordbox.com/en/plan/), accessed September 8, 2026. S027.
[^4]: Lexicon DJ, [product overview](https://www.lexicondj.com/), accessed September 8, 2026. S029.
[^5]: iBroadcast, [Premium](https://www.ibroadcast.com/premium/), accessed September 8, 2026. S031.
[^6]: Google, [YouTube Music uploads](https://support.google.com/youtubemusic/answer/9716522?hl=en), accessed September 8, 2026. S033.
[^7]: Plex, [Plexamp](https://www.plex.tv/plexamp/), accessed September 8, 2026. S032.
[^8]: Wasabi, [pricing FAQ](https://wasabi.com/pricing/faq), accessed September 8, 2026. S006.
[^9]: DigitalOcean, [Spaces pricing](https://www.digitalocean.com/pricing/spaces-object-storage), accessed September 8, 2026. S009.
[^10]: Supabase, [pricing](https://supabase.com/pricing), accessed September 8, 2026. S010.
[^11]: Mozilla, [HTTP range requests](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Range_requests), accessed September 8, 2026. S023.
[^12]: Cloudflare, [presigned URLs](https://developers.cloudflare.com/r2/api/s3/presigned-urls/), updated August 22, 2026. S012.
[^13]: AWS, [Lambda quotas](https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html), accessed September 8, 2026. S025.
[^14]: Google Cloud, [job task timeout](https://docs.cloud.google.com/run/docs/configuring/task-timeout), accessed September 8, 2026. S026.
[^15]: U.S. Copyright Office, [Section 512](https://copyright.gov/512/), accessed September 8, 2026. S040.
[^16]: UPF, [Essentia licensing](https://essentia.upf.edu/licensing_information.html), accessed September 8, 2026. S035.
[^17]: FFmpeg, [legal considerations](https://ffmpeg.org/legal.html), accessed September 8, 2026. S036.
[^18]: OpenAI, [data controls](https://developers.openai.com/api/docs/guides/your-data), accessed September 8, 2026. S044.

The complete publisher/date/claim/limitation inventory is [SOURCES.md](SOURCES.md).
