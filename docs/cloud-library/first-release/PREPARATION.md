# Deployment preparation checkpoint

> **Superseded deployment target, 2026-10-02 (D071):** this is the preserved VM preparation/evidence. The active target is the [serverless plan](serverless/README.md). Do not run these VM deployment steps for the serverless release; portable library/model/parity artifacts remain reusable.

2026-10-02 — D070/E058, CD021/CE021/T032. Local code and artifacts prepared. AWS profile `manueldev` / principal `manuel-web` selected by the owner and reverified with STS after the usage-limit interruption. No cloud resources or uploads exist from this task.

## Artifacts ready on the Mac

All paths in this table are relative to the repository. Generated artifacts are ignored by Git; keep them for upload/recovery. Do not mutate a finalized release in place.

| Path | Identity / contents |
|---|---|
| `output/cloud-releases/first-release` | 187 MP3s, one mix, web assets, raw private features, planner and parity fixtures; 415 inventoried files / 2,075,449,410 bytes |
| `output/cloud-releases/first-release/release.json` | Release ID `4a4bb92196ed75cc95ac19ec6a25bd5062ed31cdabb0eb30ebca0f83d5b5ff57`; manifest file SHA-256 `56cd5c8558e80ca4564c7cf07e32f8d60349738b72baa7cbcc6802b79df4f4c3` |
| `output/cloud-runtime/first-release` | 60-file allowlisted Linux build context; source digest `87e7d95c43165a7cf00d9938e145e38a1d6b857468b4edc9e274ec993af5ff9e`; image tag `resonant:87e7d95c43165a7cf` (image not built yet) |
| `output/cloud-config/first-release` | Generated `.env`, `app.env`, `caddy.env`, listener password; directory 700 / files 600. Image/release filled; hostname/OpenAI blank. |
| `output/cloud-models/first-release` | Six copied model assets / 2,663,055,739 bytes; manifest SHA-256 `290d4489a8cf56321485950f838125b4d374c9dff50d78c106a8185850360070` |
| `output/cloud-preparation/deployment-kit-verification.json` | 12 offline deployment tests, Python/shell syntax, Compose configuration and verification limits |
| `output/cloud-preparation/planner-evidence.json` | Python suite, planner artifacts and limits |
| `output/cloud-preparation/planner-verification.json` | 60 exact serialized planner parity cases |
| `output/cloud-preparation/local-http-smoke.json` | Real-release HTTP transport checks, no inference |
| `output/cloud-preparation/model-copy.json` | Per-model checksums and source-preservation evidence |
| `output/cloud-preparation/aws-readiness.json` | Read-only active bundle/blueprint/zone metadata; no mutation permission or capacity claim |
| `output/cloud-preparation/linux-dependency-metadata.json` | All 61 pinned Python package artifacts and exact dependency closure checked for Linux CPython 3.12; no installation |
| `output/cloud-config/ssh/resonant-lightsail-rsa` | Dedicated RSA-4096 private SSH key and adjacent `.pub`, local mode 600; not imported |
| `output/cloud-preparation/aws-target.json` | Private exact account/principal guard, mode 600; full identity is deliberately absent from tracked documents |

The release plus model payload is approximately **4.74 GB** before the Linux image. At a usable 20 Mbit/s, ideal transfer time is about 32 minutes plus protocol overhead and verification; this is arithmetic, not a measured upload speed.

## Why 187 rather than 200+

The exporter examined 316 feature-cache records. It published 187 and excluded 129: **69 incomplete analysis, 54 outdated feature versions, three non-MP3 records and three eligible records without a source in the frozen published inventory**. The private exclusions report records each hash/reason. Eight earlier browser-only MP3 copies had already been recovered by the parallel web task and are included.

Admission reuses the current policy: `selected-estimators-v3-character120`, `maest-top6-v1`, all eleven required stages passed or warning, compatible vectors and exact source hash. The exporter checks source-before/copy/source-after hashes. Originals and raw feature evidence were preserved. Increasing the catalog requires a new owner-local successful analysis/recovery and new export; it is not required to launch this valid subset.

## Implementation delivered

[Exporter documentation](../../../packages/web-player/docs/CLOUD_RELEASE_EXPORT.md) describes the immutable inventory and public/private separation. [Planner documentation](../../../packages/prompt-to-playlist/docs/CLOUD_RUNTIME.md) explains frozen specialist identities, profile/scope behavior, source fingerprints and offline text inference.

The separate Node production entrypoint reads only the release. It validates hashes and refuses stale or mismatched artifacts. It serves the catalog in 25-track pages, MP3 ranges, one saved mix, static assets and PlaylistIQ jobs. It rejects owner routes, unpublished IDs and private files. Canonical Host/Origin and a secret proxy header form the backend boundary; Caddy supplies whole-site shared-password authentication and HTTPS. Caddy compresses JSON/text with gzip/zstd. Shutdown bounds unfinished HTTP streams with a one-second grace period after jobs stop. Session cookies are signed, HttpOnly and SameSite Strict; each prompt result belongs to its initiating session. Another listener's job ID is insufficient.

One prompt job runs at a time. Busy requests receive an explicit retry response. The default persistent UTC quota is 30 accepted prompts/day; the timeout is 360 seconds. A timed-out child process group is terminated before its slot can be reused. Private audit retention is seven days / 200 request pairs. Browser-local playlists/favorites survive reload, but are not cross-device synchronized. A server restart can interrupt an in-flight prompt and require retry.

The slim Python runtime consumes the published evidence without installing or running the eleven audio analyzers. All five original profiles, subset coverage decisions, vocabulary and ranking remain available. The model is still MuQ-MuLan; OpenAI settings retain `gpt-5.4-mini-2026-03-17`, low reasoning, 30-second provider timeout and `AUTODJ_OPENAI_API_DEV_KEY`. There is no generic key fallback.

[Deployment kit](../../../deploy/first-release/README.md): allowlisted Linux image context, CPU dependencies, non-root application container, Caddy, exact-account AWS guard, source/model/runtime integrity verification, resumable transfer, bounded Linux acceptance, activation and rollback. Only proxy ports are published; app and model paths stay private. No AWS credentials belong on the VM.

## Verification actually performed

| Check | Result / limits |
|---|---|
| Full web test suite | **117 passed**, including export integrity, sessions/CSRF, ranges, queue limits and real descendant-process cleanup |
| Web syntax | **64 modules passed** |
| Full Python suite | **551 passed in 5.37 s**, including 35 cloud cases; mocked memory telemetry tests required sandbox escalation, not real analysis |
| Frozen real catalog parity | **60/60 passed** across five profiles, full/subset/reordered scopes, catalog/vocabulary/result digests and existing cached text/audio vectors |
| Real portable HTTP smoke | All 187 tracks paginated; static/config/proxy checks; three MP3 HEAD/prefix/suffix/invalid ranges; one mix with two transitions; owner/private routes denied |
| Source/model preservation | Exact copied digests; no audio decoded, analyzed, converted or rerendered |
| Deployment kit | **12 offline tests passed**, Python/shell syntax passed, Docker Compose 2.39.1 `config --quiet` passed; no daemon needed |
| Linux dependency metadata | **61 pinned packages passed** artifact compatibility and exact dependency closure; installation/imports remain unrun |
| Selected AWS identity | Fresh read-only STS succeeded for `manueldev` → `manuel-web`, account suffix 3649, region us-east-2 |

The parallel web-edition task separately recorded Chrome layout, guide cards, playback and a live prompt in [WEB_EDITION.md](../../../packages/web-player/docs/WEB_EDITION.md). This preparation did not repeat its paid call or UI design work.

**Not yet verified:** Linux image execution/imports, uncached Linux text inference and resource use, actual Caddy login/TLS, remote file verification, paid cloud OpenAI call, public mobile playback, host restart and rollback. Loopback HTTP and deterministic parity do not establish these results. Deployment scripts make the Linux acceptance evidence a prerequisite to activation. Activation also validates the pinned Linux Caddy configuration before starting services. An optional Mac Caddy download could not be matched to its release checksum and was never executed; this is not evidence of an upstream defect. The target validation remains pending.

## Continue without reconstructing chat

1. Read the [operator guide](../../../deploy/first-release/README.md) and [accounts](ACCOUNTS.md). Use the selected profile; preserve the exact account guard from the private file.
2. Resolve hosting cost, hostname and project-key use. Shared password and SSH key are already generated privately. Fill only the missing hostname and intended project OpenAI key. Obtain the current owner public IPv4 `/32` at deployment time. Secrets stay in private files.
3. Build the pinned image on a suitable Linux x86 host. Run offline import/text/parity acceptance with the frozen artifacts and record image ID, peak RSS, cold/cache latency, release ID and model digest.
4. Follow guarded provision/bootstrap/upload commands, configure DNS and private runtime files, and activate only the tested image with the verified release. No default-profile fallback or automatic instance upgrade.
5. Run HTTPS transport/access checks and then real desktop/phone prompt/listening/restart/rollback acceptance. Record the public URL and limitations in this checkpoint and [checklist](RELEASE_CHECKLIST.md).

No new app UI changes, analyzer fixes or broader corpus processing are needed for this subset's deployment. Failed tracks can be repaired locally later and shipped in a subsequent immutable release.

## Final documentation checks

Cloud validation passes: 72 sources, 124 top-level relative links, three workbook
sheets and three independently checked economics cases. All 21 historical
readiness mutation tests still pass. The first-release/deployment Markdown links
and scoped Git whitespace checks pass. No historical empirical gate was promoted
by these local results. The private configuration files and dedicated SSH key
are mode 600 under mode-700 directories and confirmed ignored by Git.
