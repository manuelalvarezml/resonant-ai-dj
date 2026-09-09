# Security, privacy and rights discovery

## Launch posture

Private libraries only is the proposed initial boundary. No sharing links, public catalog, user-to-user audio transfer, commercial-streaming imports, URL downloading or DRM circumvention belongs in the MVP. These exclusions reduce scope; they do not establish legal permission for the remaining uses.

The launch entity, customer jurisdictions and applicable rights basis remain unresolved. This is an issue map and review packet, not legal clearance. Full cloud build and external beta remain blocked on the relevant gates.

## Assets and trust boundaries

Protect originals and unpublished music, source identities, metadata corrections, playlists, prompts, generated mixes, account identities, credentials and billing/job records. A music collection can expose sensitive personal preferences; private links and filenames can leak through analytics and support systems.

Trust boundaries are browser↔API, API↔DB, browser↔storage, queue↔worker, worker↔storage, API↔model provider and operator↔production. A worker receives only job-scoped data. A provider event is untrusted until validated and mapped to a known session.

## Threat model

| Threat / abuse path | Proposed control | Required proof |
|---|---|---|
| IDOR / tenant ID substitution | Resolve tenant from session; authorize every object/query/job; DB defense in depth | Two-tenant matrix across all endpoints and storage capabilities |
| Signed URL disclosure | Short TTL, scoped method/key, no URL logs, referrer policy | Expiry and log-redaction tests; no promise to revoke downloaded bytes |
| Shared-cache leak | Initially private/no shared cache; later auth before cache hit | Cross-tenant cache warm/read and deletion tests |
| File type spoof / parser exploit | Allowlist, signature/probe validation, patched decoder, sandbox and resource limits | Malformed fixtures, process isolation and protocol allowlist |
| Path traversal / command injection | Internal keys; safe argument arrays; no shell command from metadata/LLM | Adversarial filenames/metadata and URL-protocol cases |
| Storage/compute cost attack | Quota reservations, rate limits, bounded parts/jobs/retries, kill switch | Concurrent reservation/overrun and abandoned-upload tests |
| Queue replay / stale worker | Idempotency, leases, fencing and final revision checks | Duplicated events, crash and cancellation races |
| Cross-tenant dedup inference | Dedup within tenant only; opaque IDs | Same hash in two accounts reveals no existence/status |
| Prompt injection in tags | Tags are data; no tools or authority from model text | Adversarial metadata cannot change tenant, budget or operations |
| Credential theft | Server-only scoped secrets, rotation, environment isolation | Secret scan, rotation rehearsal, staging cannot read prod |
| Operator misuse | Least privilege, just-in-time break-glass access, audit, consent-based support | Access review and support diagnostic packet |
| Account takeover | Managed auth, session invalidation, secure recovery, MFA for admins | Recovery and logout tests; no bypass through playback token minting |
| Data resurrection after restore | Tombstones replayed before reopening traffic | Delete→backup restore→verify inaccessible |
| Supply-chain/model artifact change | Locked dependencies, approved hashes and licenses, signed/digested images | SBOM and changed-artifact review |
| Excessive private telemetry | Redacted event fields and short retention | Sample log inspection, retention/deletion audit |

Upload security follows layered validation; extension/MIME filtering alone is insufficient. [OWASP file upload guidance](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html) S043. Presigned links are bearer capabilities; the product cannot equate expiration with DRM. [R2 signing](https://developers.cloudflare.com/r2/api/s3/presigned-urls/) S012.

## Privacy data map and retention proposal

| Data | Proposed purpose | Proposed default | Decision needed |
|---|---|---|---|
| Account/email | Authentication, service operations | Account lifetime plus required legal records | Entity, processor, lawful basis and recovery design |
| Originals and metadata | Private library | Until user deletion | Backup residual period and rights scope |
| Prompts | Translation and optional saved history | No indefinite debug retention; optional history | Consent/UI, minimum useful retention |
| Analysis and mix manifests | Explainability and reproducibility | Linked artifact lifecycle | Redaction after source/account deletion |
| Playback events | Reliability and limited usage billing | Aggregate where possible; raw events 30 days proposed | Actual need and local privacy rules |
| Diagnostic logs | Security/support | 14 days proposed, security incidents separately governed | Access, legal holds, costs |
| Backups | Disaster recovery | 30 days proposed | Deletion tombstones and access isolation |
| Billing records | Payments, tax and disputes | Jurisdiction-defined, not invented here | Accountant/counsel guidance |

All durations are design proposals. Minimize collection before debating long retention. Do not store full presigned URLs or tokens. Use private identifiers in support packets, not song names, paths or audio. End-to-end encryption is not claimed because analysis/playback derivatives require server-side access to clear audio. A future client-encrypted vault is a different feature set.

OpenAI's documentation separates abuse-monitoring records from application state. The proposed translation request should set storage behavior deliberately and avoid audio, paths and catalog content. Approved Zero Data Retention has eligibility and endpoint conditions; do not infer it from store=false. [OpenAI data controls](https://developers.openai.com/api/docs/guides/your-data) S044.

## Jurisdiction screening

For a U.S. operation or service exposure, counsel should assess applicable storage/playback/transformation rights and Section 512 conditions, including designated-agent and notice/counter-notice/repeat-infringer procedures where applicable. Safe harbor is conditional and does not itself license music transformation. [U.S. Copyright Office](https://copyright.gov/512/) S040.

For EU customers or operations, assess GDPR Article 3 scope, lawful bases/transparency, erasure/access/portability, processor terms, security and international transfers. A region-specific bucket does not alone establish compliance across logs, authentication, support and model processing. [Official GDPR text](https://eur-lex.europa.eu/eli/reg/2016/679/oj/eng) S041. This report does not determine which obligations apply to an undecided business.

If Peru is relevant to the operator or users, the review must include Law 29733 and Decreto Supremo 016-2024-JUS. The official regulation entry was screened; a complete provision-by-provision compliance assessment was not performed. [Peru ANPD regulation entry](https://www.gob.pe/institucion/anpd/normas-legales/6554453-16-2024-jus) S042. Do not infer launch geography from the developer's timezone.

Ask counsel to provide a written allowed-use matrix by jurisdiction and user/file type. Distinguish purchased tracks, self-created recordings, label promos, DJ-pool licenses and subscription-service files. The product should preserve a user's rights attestation but not treat a checkbox as independent proof.

## Music rights action matrix

| Activity | Question to resolve | Gate impact |
|---|---|---|
| Private storage/backup | Permitted reproduction and service-provider role for the intended users | Blocks real customer uploads |
| Private on-demand playback | Rights and contractual obligations for remote personal listening | Blocks external playback beta |
| Decode/transcode/analysis copies | Whether temporary/derived copies and processing are within the permitted scope | Blocks analysis features |
| Downloadable continuous mix | Composition/recording, reproduction/adaptation/distribution and license implications | Separate mix gate; ownership alone insufficient |
| Public sharing/performance | Additional rights and platform obligations | Deferred; no implied authorization |
| Complaint/takedown | Applicable procedure, records, response time and appeals | Required before external launch |
| Provider suspension | Terms and abuse handling across host/storage/model services | Exit plan and user export required |

Do not rely on a competitor's marketing assertion that exported audio can be used anywhere. S034 is used only to establish product workflow, not legal permissions.

## Software and model bill of materials review

| Component | Current local role | Documentary finding | Required next evidence |
|---|---|---|---|
| FFmpeg 8.0.1 local Homebrew GPL build | Decode, measurements, deterministic DSP/render | FFmpeg licensing depends on enabled components | Exact cloud build flags, dependency licenses and distribution obligations |
| Essentia 2.1b6.dev1389 | Key estimation | Vendor discusses AGPL/commercial licensing; model terms are separate | Actual license text, linking/deployment analysis and commercial quote if needed |
| Beat This final0 | Independent rhythm challenger | Upstream states MIT for code and published weights with training-data caveat | Exact package/weight hashes and dependency review |
| All-In-One / MLX port | Primary rhythm/structure path | Upstream repository MIT; MLX port is platform-specific | Code, converted weights, upstream dependencies and artifact provenance |
| Demucs/MLX internals | Internal separation despite discarded stems | Local dependency confirmed, full license chain not audited | Exact code/weights/convert dependencies and cloud-use review |
| Playlist package / model provider | Intent translation and deterministic retrieval | Local package boundary known | Repository ownership/license declaration and model-provider terms |
| Audio fixtures | Future tests/benchmarks | None selected or uploaded in this research | Permission for processing, retention and any redistribution |

Sources: [Essentia](https://essentia.upf.edu/licensing_information.html) S035; [FFmpeg](https://ffmpeg.org/legal.html) S036; [Beat This](https://github.com/CPJKU/beat_this) S037; [All-In-One](https://github.com/mir-aidj/all-in-one) S038; [MLX port](https://github.com/ssmall256/all-in-one-mlx) S039.

Do not shorthand AGPL as “commercial use prohibited.” Open-source license obligations, vendor commercial offerings and pretrained-model noncommercial restrictions are distinct. A proprietary deployment may need a different license strategy, compliance architecture or replacement. None is selected here. Placing a component in another process or container is not by itself a proven way to eliminate obligations.

## Review packet and acceptance

Prepare a data-flow diagram, proposed terms/use restrictions, list of launch territories, source-file license examples, subprocessor list, retention/deletion map, full software/model inventory, support access design and complaint procedure. Assign qualified legal/security reviewers before any external pilot.

Pass G004 only with documented approved uses, outstanding exceptions and an affordable license/compliance path. Pass G007 only after independent tenant-isolation and deletion/recovery evidence. A signed contract with a cloud provider does not pass either gate by itself.
