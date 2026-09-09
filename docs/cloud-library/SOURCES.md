# Cloud library research sources

Accessed 2026-09-08. Publisher dates are recorded only when visible. These are source observations, not hands-on provider validation. Recheck prices and terms before expenditure and after 30 days. No paid interviews, latency benchmarks, cloud accounts, or audio uploads occurred. Source identifiers are stable; supersede records rather than reusing IDs. The full machine-readable inventory is [sources.json](sources.json).

<a id="s001"></a>
## S001

Cloudflare. [R2 pricing](https://developers.cloudflare.com/r2/pricing/). Published/updated 2026-08-07. Accessed 2026-09-08.

**Used for:** R2 Standard $0.015/GB-month; Class A $4.50/million; Class B $0.36/million; no direct egress charge; billed-unit rounding; IA retrieval and minimum duration.

**Limits:** Documentation claim; no hands-on product or provider benchmark.

<a id="s002"></a>
## S002

Backblaze. [B2 Cloud Storage pricing](https://www.backblaze.com/cloud-storage/pricing). Publisher date not established. Accessed 2026-09-08.

**Used for:** $6.95/TB-month; 3x average monthly storage free egress then $0.01/GB; A/B/C calls free; D exceptions.

**Limits:** Documentation claim; no hands-on product or provider benchmark.

<a id="s003"></a>
## S003

Backblaze. [Pricing and product updates](https://www.backblaze.com/blog/backblaze-pricing-and-product-updates/). Publisher date not established. Accessed 2026-09-08.

**Used for:** May 1 price change from $6 to $6.95/TB and standard API calls free; supersedes old pricing.

**Limits:** Documentation claim; no hands-on product or provider benchmark.

<a id="s004"></a>
## S004

Wasabi. [Monthly minimum storage charge](https://docs.wasabi.com/docs/how-does-wasabis-monthly-minimum-storage-charge-work). Published/updated 2026-07-01. Accessed 2026-09-08.

**Used for:** 1 TB minimum; example $7.99 and base-2 billing.

**Limits:** Documentation claim; no hands-on product or provider benchmark.

<a id="s005"></a>
## S005

Wasabi. [Minimum storage duration policy](https://docs.wasabi.com/docs/how-does-wasabis-minimum-storage-duration-policy-work). Published/updated 2026-01-09. Accessed 2026-09-08.

**Used for:** Pay-go default 90-day minimum charged on early deletion.

**Limits:** Documentation claim; no hands-on product or provider benchmark.

<a id="s006"></a>
## S006

Wasabi. [Pay as You Go pricing FAQ](https://wasabi.com/pricing/faq). Publisher date not established. Accessed 2026-09-08.

**Used for:** Regular egress exceeding active storage volume is a poor fit and may lead to limiting or suspension.

**Limits:** Documentation claim; no hands-on product or provider benchmark.

<a id="s007"></a>
## S007

Amazon Web Services. [Amazon S3 pricing](https://aws.amazon.com/s3/pricing/). Publisher date not established. Accessed 2026-09-08.

**Used for:** Regional storage, requests, transfer and other charges; dynamic region-specific rate cells not reliably extracted in this pass.

**Limits:** Regional price extraction incomplete; obtain quote.

<a id="s008"></a>
## S008

DigitalOcean. [Spaces pricing](https://docs.digitalocean.com/products/spaces/details/pricing/). Published/updated 2026-07-13. Accessed 2026-09-08.

**Used for:** $5/month includes 250 GiB; incremental storage $0.02/GiB.

**Limits:** Documentation claim; no hands-on product or provider benchmark.

<a id="s009"></a>
## S009

DigitalOcean. [Spaces object storage pricing](https://www.digitalocean.com/pricing/spaces-object-storage). Publisher date not established. Accessed 2026-09-08.

**Used for:** 1 TiB outbound allowance; extra outbound $0.01/GiB; account bundle rather than per user.

**Limits:** Documentation claim; no hands-on product or provider benchmark.

<a id="s010"></a>
## S010

Supabase. [Pricing](https://supabase.com/pricing). Publisher date not established. Accessed 2026-09-08.

**Used for:** Pro from $25/month; 100GB storage then $0.0213/GB; separate 250GB cached/uncached egress pools.

**Limits:** Documentation claim; no hands-on product or provider benchmark.

<a id="s011"></a>
## S011

Supabase. [Manage egress usage](https://supabase.com/docs/guides/platform/manage-your-usage/egress). Publisher date not established. Accessed 2026-09-08.

**Used for:** Uncached $0.09/GB; cached $0.03/GB, with independent quotas.

**Limits:** Documentation claim; no hands-on product or provider benchmark.

<a id="s012"></a>
## S012

Cloudflare. [R2 presigned URLs](https://developers.cloudflare.com/r2/api/s3/presigned-urls/). Published/updated 2026-08-22. Accessed 2026-09-08.

**Used for:** Bearer URLs; S3 hostname only, no custom-domain substitution; GET/PUT direct access.

**Limits:** Documentation claim; no hands-on product or provider benchmark.

<a id="s013"></a>
## S013

Cloudflare. [R2 S3 compatibility](https://developers.cloudflare.com/r2/api/s3/api/). Publisher date not established. Accessed 2026-09-08.

**Used for:** Operation and header compatibility must be checked individually.

**Limits:** Documentation claim; no hands-on product or provider benchmark.

<a id="s014"></a>
## S014

Cloudflare. [R2 data location](https://developers.cloudflare.com/r2/reference/data-location/). Publisher date not established. Accessed 2026-09-08.

**Used for:** Location hints are best-effort; jurisdiction restrictions distinct.

**Limits:** Documentation claim; no hands-on product or provider benchmark.

<a id="s015"></a>
## S015

Cloudflare. [R2 data security](https://developers.cloudflare.com/r2/reference/data-security/). Publisher date not established. Accessed 2026-09-08.

**Used for:** Storage encryption reference; does not establish end-to-end encryption.

**Limits:** Documentation claim; no hands-on product or provider benchmark.

<a id="s016"></a>
## S016

Cloudflare. [R2 consistency model](https://developers.cloudflare.com/r2/reference/consistency/). Publisher date not established. Accessed 2026-09-08.

**Used for:** Object consistency differs from cached delivery visibility.

**Limits:** Documentation claim; no hands-on product or provider benchmark.

<a id="s017"></a>
## S017

Backblaze. [S3-compatible API](https://www.backblaze.com/docs/cloud-storage-s3-compatible-api). Publisher date not established. Accessed 2026-09-08.

**Used for:** S3 API subset/integration reference.

**Limits:** Documentation claim; no hands-on product or provider benchmark.

<a id="s018"></a>
## S018

Backblaze. [Cloud storage data regions](https://www.backblaze.com/docs/cloud-storage-data-regions). Publisher date not established. Accessed 2026-09-08.

**Used for:** Regional account placement requires deliberate selection.

**Limits:** Documentation claim; no hands-on product or provider benchmark.

<a id="s019"></a>
## S019

DigitalOcean. [Spaces S3 compatibility](https://docs.digitalocean.com/products/spaces/reference/s3-compatibility/). Publisher date not established. Accessed 2026-09-08.

**Used for:** S3 subset; validate versioning, signing and CDN behavior in spike.

**Limits:** Documentation claim; no hands-on product or provider benchmark.

<a id="s020"></a>
## S020

Amazon Web Services. [Multipart upload overview](https://docs.aws.amazon.com/AmazonS3/latest/userguide/mpuoverview.html). Publisher date not established. Accessed 2026-09-08.

**Used for:** Independent part retries; complete/abort lifecycle; multipart ETag not a whole-file integrity guarantee.

**Limits:** Documentation claim; no hands-on product or provider benchmark.

<a id="s021"></a>
## S021

tus project. [Resumable upload protocol](https://tus.io/protocols/resumable-upload). Publisher date not established. Accessed 2026-09-08.

**Used for:** Offset-based resumable protocol with extensions.

**Limits:** Documentation claim; no hands-on product or provider benchmark.

<a id="s022"></a>
## S022

Supabase. [Resumable uploads](https://supabase.com/docs/guides/storage/uploads/resumable-uploads). Publisher date not established. Accessed 2026-09-08.

**Used for:** Managed TUS option, contrasted with direct multipart.

**Limits:** Documentation claim; no hands-on product or provider benchmark.

<a id="s023"></a>
## S023

Mozilla. [HTTP range requests](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Range_requests). Publisher date not established. Accessed 2026-09-08.

**Used for:** 206/Content-Range and 416 behaviors for seeking.

**Limits:** Documentation claim; no hands-on product or provider benchmark.

<a id="s024"></a>
## S024

Mozilla. [Web audio codec guide](https://developer.mozilla.org/en-US/docs/Web/Media/Guides/Formats/Audio_codecs). Publisher date not established. Accessed 2026-09-08.

**Used for:** Codec/container/browser support must be evaluated together.

**Limits:** Documentation claim; no hands-on product or provider benchmark.

<a id="s025"></a>
## S025

Amazon Web Services. [Lambda quotas](https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html). Publisher date not established. Accessed 2026-09-08.

**Used for:** Invocation timeout 900 seconds.

**Limits:** Documentation claim; no hands-on product or provider benchmark.

<a id="s026"></a>
## S026

Google Cloud. [Cloud Run job task timeout](https://docs.cloud.google.com/run/docs/configuring/task-timeout). Publisher date not established. Accessed 2026-09-08.

**Used for:** CPU job tasks up to 168 hours; GPU task maximum 1 hour.

**Limits:** Documentation claim; no hands-on product or provider benchmark.

<a id="s027"></a>
## S027

rekordbox / AlphaTheta. [Plans and pricing](https://rekordbox.com/en/plan/). Publisher date not established. Accessed 2026-09-08.

**Used for:** Professional shows 5TB Dropbox; $36 monthly or $360 annual ($30 effective monthly), USD.

**Limits:** Documentation claim; no hands-on product or provider benchmark.

<a id="s028"></a>
## S028

rekordbox / AlphaTheta. [Cloud features](https://rekordbox.com/en/feature/cloud/). Publisher date not established. Accessed 2026-09-08.

**Used for:** Cloud library sync and performance ecosystem; Dropbox/Google Drive integrations.

**Limits:** Documentation claim; no hands-on product or provider benchmark.

<a id="s029"></a>
## S029

Lexicon DJ. [Product and pricing overview](https://www.lexicondj.com/). Publisher date not established. Accessed 2026-09-08.

**Used for:** DJ library management and cloud tracks; exact paid prices not extractable.

**Limits:** Exact paid prices unavailable.

<a id="s030"></a>
## S030

Lexicon DJ. [Manual](https://www.lexicondj.com/manual/all). Publisher date not established. Accessed 2026-09-08.

**Used for:** Library editing, smartlists, analysis and conversion workflows.

**Limits:** Documentation claim; no hands-on product or provider benchmark.

<a id="s031"></a>
## S031

iBroadcast. [Premium membership](https://www.ibroadcast.com/premium/). Publisher date not established. Accessed 2026-09-08.

**Used for:** $3.99/month or $44.99/year; personal cloud storage/listening competitor.

**Limits:** Documentation claim; no hands-on product or provider benchmark.

<a id="s032"></a>
## S032

Plex. [Plexamp](https://www.plex.tv/plexamp/). Publisher date not established. Accessed 2026-09-08.

**Used for:** Personal server music; smart playlists, fades and premium discovery capabilities.

**Limits:** Documentation claim; no hands-on product or provider benchmark.

<a id="s033"></a>
## S033

Google. [Upload music to YouTube Music](https://support.google.com/youtubemusic/answer/9716522?hl=en). Publisher date not established. Accessed 2026-09-08.

**Used for:** Up to 100,000 personal uploaded songs; owner-only playback.

**Limits:** Documentation claim; no hands-on product or provider benchmark.

<a id="s034"></a>
## S034

Mixed In Key. [Mashup workflow](https://mashup.mixedinkey.com/how-to-make-mashups/create-epic-mashups). Publisher date not established. Accessed 2026-09-08.

**Used for:** Tempo/key-assisted mixing, EQ editing and audio export; marketing rights claims not relied on.

**Limits:** Documentation claim; no hands-on product or provider benchmark.

<a id="s035"></a>
## S035

UPF / Music Technology Group. [Licensing Essentia](https://essentia.upf.edu/licensing_information.html). Publisher date not established. Accessed 2026-09-08.

**Used for:** AGPL/commercial licensing discussion; separate noncommercial pretrained models; third-party dependencies require review.

**Limits:** Documentation claim; no hands-on product or provider benchmark.

<a id="s036"></a>
## S036

FFmpeg. [License and legal considerations](https://ffmpeg.org/legal.html). Publisher date not established. Accessed 2026-09-08.

**Used for:** LGPL default with GPL options; binary configuration matters.

**Limits:** Documentation claim; no hands-on product or provider benchmark.

<a id="s037"></a>
## S037

CPJKU. [Beat This repository](https://github.com/CPJKU/beat_this). Publisher date not established. Accessed 2026-09-08.

**Used for:** MIT code and published weights; training-data caveat; no version-specific legal clearance.

**Limits:** Documentation claim; no hands-on product or provider benchmark.

<a id="s038"></a>
## S038

mir-aidj. [All-In-One repository](https://github.com/mir-aidj/all-in-one). Publisher date not established. Accessed 2026-09-08.

**Used for:** MIT repository, PyTorch/NATTEN stack; does not clear all weights/dependencies.

**Limits:** Documentation claim; no hands-on product or provider benchmark.

<a id="s039"></a>
## S039

ssmall256. [All-In-One MLX port](https://github.com/ssmall256/all-in-one-mlx). Publisher date not established. Accessed 2026-09-08.

**Used for:** Apple Silicon optimized port; cloud portability remains untested.

**Limits:** Documentation claim; no hands-on product or provider benchmark.

<a id="s040"></a>
## S040

U.S. Copyright Office. [Section 512 resources](https://copyright.gov/512/). Publisher date not established. Accessed 2026-09-08.

**Used for:** Conditional liability safe harbors and notice/takedown procedures, not a music license.

**Limits:** Documentation claim; no hands-on product or provider benchmark.

<a id="s041"></a>
## S041

European Union. [General Data Protection Regulation](https://eur-lex.europa.eu/eli/reg/2016/679/oj/eng). Published/updated 2016-04-27. Accessed 2026-09-08.

**Used for:** Territorial scope, rights, security and processor/transfer framework; article applicability requires legal assessment.

**Limits:** Documentation claim; no hands-on product or provider benchmark.

<a id="s042"></a>
## S042

Peru ANPD. [Decreto Supremo 016-2024-JUS](https://www.gob.pe/institucion/anpd/normas-legales/6554453-16-2024-jus). Published/updated 2024-11-30. Accessed 2026-09-08.

**Used for:** Official entry for regulation under Law 29733; jurisdiction screening, not completed legal opinion.

**Limits:** Official landing entry screened; full legal application not assessed.

<a id="s043"></a>
## S043

OWASP. [File Upload Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html). Publisher date not established. Accessed 2026-09-08.

**Used for:** Layered file validation, storage isolation and upload constraints.

**Limits:** Documentation claim; no hands-on product or provider benchmark.

<a id="s044"></a>
## S044

OpenAI. [Data controls in the OpenAI platform](https://developers.openai.com/api/docs/guides/your-data). Publisher date not established. Accessed 2026-09-08.

**Used for:** Default abuse-monitoring retention distinct from application state and approved zero-retention arrangements.

**Limits:** Documentation claim; no hands-on product or provider benchmark.

<a id="s045"></a>
## S045

OpenAI. [GPT-5.4 mini model](https://developers.openai.com/api/docs/models/gpt-5.4-mini). Publisher date not established. Accessed 2026-09-08.

**Used for:** Standard input $0.75/million and output $4.50/million tokens; used only as a cost scenario.

**Limits:** Documentation claim; no hands-on product or provider benchmark.

