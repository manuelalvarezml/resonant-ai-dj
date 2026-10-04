# First-release checklist and evidence

> **Superseded deployment target, 2026-10-02 (D071):** this is the preserved VM preparation/evidence. The active target is the [serverless plan](serverless/README.md). Do not run these VM deployment steps for the serverless release; portable library/model/parity artifacts remain reusable.

2026-10-02, D070/E058. [Preparation evidence](PREPARATION.md) separates local results from deployment acceptance. Unchecked items have not been verified.

## Complete locally

- [x] Parallel web edition's Chrome sanity check recorded separately in [WEB_EDITION.md](../../../packages/web-player/docs/WEB_EDITION.md).
- [x] Same repository, frozen shared library, local audio analysis and browser-local playlist scope established.
- [x] Owner selected `manueldev` / `manuel-web`; fresh STS exact identity captured privately. No default-profile fallback.
- [x] Lightsail read metadata permissions verified; active Ubuntu 24.04 / 8 GB / $44 bundle identified in us-east-2.
- [x] Frozen 187 MP3s / 1,910,985,140 bytes; exact exclusions reconciled from 316 caches.
- [x] Source-before/copy/source-after hashes match; originals preserved; all eleven required stages/current policy checked.
- [x] Portable public catalog, private raw features/vectors, five planner profiles, one mix and model assets copied and inventoried.
- [x] Public responses omit private paths/embeddings/secrets; runtime uses only the release and configured state/models.
- [x] Production canonical origin, proxy boundary, session/CSRF checks and private routes covered by local tests.
- [x] Analysis/conversion/restore/render/import endpoints reject direct calls.
- [x] Unknown hashes, forged metadata, traversal and oversized requests rejected; prompt results bound to their session.
- [x] One active job, persistent daily cap, timeout and full process-tree cleanup verified locally.
- [x] 60/60 frozen planner parity cases pass across all five profiles and scopes.
- [x] Real-release loopback HTTP smoke covers full catalog, three MP3 range variants, mix and denied routes.
- [x] Guarded provisioning/upload/activation/rollback scripts and a verified 60-file runtime context prepared.
- [x] Dedicated RSA-4096 SSH key, listener password, proxy/session secrets and bcrypt configuration generated privately; modes and Git ignores verified.

## Required before activation

- [ ] Hosting cost accepted: proposed $44/month before tax, snapshots/domain and separately metered OpenAI use.
- [ ] HTTPS hostname selected, DNS authority confirmed, DNS points to stable address.
- [ ] Listener access default accepted or adjusted: shared password protects entire site/API/media.
- [ ] Intended project OpenAI key placed privately; no generic-key fallback or secret in image/Git.
- [ ] SSH public key and owner `/32` supplied; exact-account preflight repeated before provider writes.
- [ ] Linux image built successfully with pinned CPU dependencies; clean import smoke passes.
- [ ] Offline uncached MuQ text result succeeds on Linux; cold/cache latency, RSS and memory floor recorded.
- [ ] Same Linux image passes all 60 parity cases; evidence binds its image ID, release and model digest.
- [ ] Remote release, model and runtime inventories fully verified after transfer.
- [ ] Actual Caddy authentication and trusted HTTPS work; unauthenticated HTML/catalog/audio/mix/API are denied.
- [ ] Direct backend/IP/alternate-host bypass fails; only intended public ports reachable.

## Public acceptance and recovery

- [ ] Fresh desktop browser and actual phone load all 187 tracks without local-library data.
- [ ] Mac disconnected: playback, mix and PlaylistIQ still work.
- [ ] Play/pause, seeking, queue advance, manual playlist and favorites persist as designed after reload.
- [ ] One real hosted OpenAI/MuQ prompt completes, result polling works and generated playlist plays.
- [ ] Both mix intervals display: 203.65–232.74 s and 407.29–436.38 s.
- [ ] Busy/failure/timeout behavior is understandable to a listener.
- [ ] Host/container restart preserves release, model/text cache and quota; interrupted prompt can be retried.
- [ ] Activation failure/rollback verified on the host; recovery from retained local bundles demonstrated.
- [ ] Public URL, runtime image ID, tests and remaining device limits recorded in PREPARATION.md.

No new audio analysis, cloud analyzers, per-user libraries, cross-device database or new rendering are required to publish this release. Historical commercial discovery gates remain independent.
