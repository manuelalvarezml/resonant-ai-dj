# First-release deployment plan

> **Superseded deployment target, 2026-10-02 (D071):** this is the preserved VM preparation/evidence. The active target is the [serverless plan](serverless/README.md). Do not run these VM deployment steps for the serverless release; portable library/model/parity artifacts remain reusable.

2026-10-02. Local exporter, planner, server and deployment kit are implemented. Read [PREPARATION.md](PREPARATION.md) for measured results and [the operator guide](../../../deploy/first-release/README.md) for executable commands. The sequence below describes the full launch; Linux execution and external deployment remain pending.

## Architecture

```text
Owner Mac: completed MP3s + saved analysis
  -> explicit release export, eligibility report and SHA-256 verification
  -> versioned private release directory on one Linux VM

Listeners -> HTTPS + shared access control (Caddy)
             |-> web static assets
             |-> catalog / range-capable audio / one saved mix
             `-> Node API -> Python PlaylistIQ -> OpenAI request translation
                                             `-> CPU MuQ text encoding + ranking
```

One x86 Linux VM, initially 8 GB RAM, and one active playlist request at a time. This is a sizing hypothesis; validate Linux text inference before downsizing. Lightsail's proposed $44 bundle has two vCPUs, so benchmark with a two-thread cap rather than assuming the existing four-thread setting is optimal. No GPU. No dependency on the Mac after publication.

Keep Caddy public on 80/443, app reachable only inside the private Docker network, SSH key access limited to the owner, and app/media permissions restricted to the service user. Use a pinned Linux container for Node/Python and Docker restart supervision. Secrets arrive through a private runtime file/environment; never copy shell profiles, AWS keys, the Mac virtual environment or the whole workspace.

The prepared scripts use these paths on the eventual host:

| Path | Contents |
|---|---|
| `/srv/resonant/releases/<release-id>/public/` | Built web assets and public-safe configuration only |
| `/srv/resonant/releases/<release-id>/private/` | Frozen planner, raw feature evidence/vectors and provenance |
| `/srv/resonant/releases/<release-id>/media/` | Verified immutable song bytes and the one existing mix |
| `/srv/resonant/models/` | Pinned MuQ text-runtime model assets |
| `/srv/resonant/state/` | Text-query cache and bounded private prompt/audit state |
| `/srv/resonant/current` | Atomic pointer to the accepted release |

The HTTP media handler resolves known IDs through the frozen manifest. Private files are never placed under Caddy's static root. A catalog digest identifies its public projection; a separate release manifest hashes every required file, including private feature data. Source paths from the Mac must not survive as runtime dependencies.

## Work in order

### 1. Freeze the web edition and make the library portable — complete locally

Owner: implementation agent, coordinating through files with the parallel UI work.

- Re-read the current web-edition checkpoint and finish its requested local sanity review on its separate port. Keep the original local app and data on their current origin.
- Extend the local exporter to stage only eligible MP3s, raw cached features, public projection, text-cache entries, model identifiers and the selected existing mix. Reuse the `fullyAnalyzed` policy rather than inventing a looser cloud definition.
- Require all eleven expected stages to pass or carry an accepted warning, current feature/policy versions and usable compatible semantic vectors. Warnings remain visible; `complete` alone is insufficient.
- Compare every copied MP3 digest against the feature record's source hash. Deduplicate by hash. Missing source, failed stage, invalid/stale vector, non-MP3 and stale-policy exclusions each get a distinct reason.
- Reconcile the latest 187-track preview with the earlier 190 eligible caches and owner's 200+ expectation. Recover browser-only analyzed MP3 bytes through the owner-local export flow where available; otherwise omit them and report the exact gap. No conversion or analysis is needed to publish the already eligible subset.
- Produce a manifest with release ID, relative paths, sizes, hashes, feature versions, required-stage outcomes, model/vector provenance, total tracks/bytes and exclusions. Do not commit music, private caches, weights or source-path maps.

Exit: export loads from an independent directory without `test_music`, IndexedDB or the original absolute paths. Final count is measured and disclosed.

### 2. Package the cloud runtime — code prepared; Linux acceptance pending

Owner: implementation agent. Preserve planner weights, selected estimators and MuQ behavior.

- Add a dedicated production entrypoint that reads the frozen release; do not publish the loopback development server or scan source folders on boot.
- Configure the canonical public HTTPS origin explicitly. Fix the current loopback-only Host/Origin checks and `http://` playback URLs. Trust forwarding headers only from the local proxy. Preserve CSRF protection for cookie-authenticated state-changing endpoints.
- Expose only catalog/playback/mix/playlist/job-result routes; reject analysis, restoration, conversion, arbitrary filesystem paths and unpublished track IDs server-side.
- Build a clean Linux dependency lock/image with the text runtime and required `psutil`; do not install the eleven audio analyzers. Make Python/model/cache paths configurable. Verify fresh imports and one uncached text embedding on Linux.
- Resolve the estimator-identity issue: published evidence is currently compared against installed analyzer package versions. Export frozen planner catalog(s) locally with provenance, or implement trusted published-evidence consumption without treating absent analyzers as evidence loss. Keep supported profile/scope behavior explicit.
- Compare local/cloud deterministic results for fixed structured queries and cached text vectors, including selected specialist coverage, ordering and scores. An independently live LLM response is not a deterministic parity fixture.
- Preserve the existing translation model/configuration. Inject only the intended `AUTODJ_OPENAI_API_DEV_KEY`; generic `OPENAI_API_KEY` is not its fallback.
- Add a health/readiness endpoint, bounded input length, one active prompt job, finite queue/retry behavior, request timeout and daily request limit. Keep model credentials and private prompt logs out of browser payloads/logging. Bind each prompt job/result to its initiating session or an unguessable per-request capability, even with shared listener credentials. Timeout/cancellation must terminate and reap the full child process tree before releasing the concurrency slot.

Exit: clean Linux boot, fixed-query parity, accepted uncached text result with measured memory/latency, playback route checks, no source paths or secrets exposed. This is the largest technical uncertainty.

### 3. Establish address, spending and access — AWS profile selected

Owner: user for account/billing identity and access preferences; agent for preparation/configuration.

- Account selected and reverified: `manueldev` / `manuel-web`, ending 3649, us-east-2. Confirm the monthly envelope; old $5 budget does not fund the proposed full runtime.
- Use an existing personal hostname/subdomain where possible; DNS points to the VM's stable address. A new domain is optional spending, not silently purchased. If none is available, choose and test a trusted HTTPS hostname/IP-certificate route before publishing; a bare HTTP IP is not the release URL.
- Default planning assumption pending the owner's answer: one shared listener password over HTTPS. Store its hash, distribute it out of band and protect HTML/API/media/mix consistently. Shared credentials have coarse revocation and no personal identity. If email allowlist is chosen, substitute a small authentication gateway without adding separate libraries.
- Do not interpret “share the app” as approval for unrestricted anonymous AI usage. If link-only public access is chosen, explicitly design the prompt budget/access boundary first.
- For AWS commands, use explicit personal profile plus an exact full-account-ID preflight; never fall back to `default`. Provision only after the account and charge are resolved.

Exit: verified account, region, instance price, hostname, access mode and secret source recorded privately. No secret values in this folder.

### 4. Deploy the exact staged release

Owner: deployment agent once external execution details are settled.

- Provision one VM and persistent disk under the chosen personal account. Keep an inventory of instance/address/DNS identifiers and charges; no load balancer, managed database, GPU or analyzer fleet.
- Upload the explicit artifact allowlist over SSH/resumable transfer. Verify remote SHA-256 for all selected MP3s and artifacts before activating the release. Models may be fetched at pinned revisions with checksums; never ship the entire Mac cache.
- Install/start Caddy and the pinned application service, inject the project OpenAI secret privately and enable automatic restart. Authentication must protect the first real-media response.
- Use a temporary release pointer and smoke checks; switch `current` atomically only on success. Use the same published hash IDs for audio, public features and Python ranking.
- Retain the owner-local sources and complete release bundle as the recovery copy. Cloud disk persists across process/release restarts but is not itself a backup. Paid VM snapshots are optional and must fit the chosen budget.

Exit: a stable HTTPS address serves the exact catalog and one mix, with remote integrity verified and the Mac disconnected.

### 5. Prove the release and share it

Run [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md). Minimum real-device checks: desktop Chrome and the actual phone/browser used for sharing; record Safari/iOS status honestly. Verify playback and seeking, a manual playlist, an actual PlaylistIQ prompt, both mix transition labels, denied access without credentials, direct media URLs, restart durability and rollback. No reanalysis or rerendering.

Retain a short evidence record with counts, release digest, account suffix, region, public URL, runtime versions, memory/latency measurements, actual tests and remaining limitations. Do not mark broad customer/commercial experiments complete.

## Operations and rollback

Keep previous static/private manifests and the exact model/runtime version. Rollback repoints `current` to the prior verified release and restarts the app; do not delete media needed by either release. A failed first release stays access-restricted. Verify recovery from the owner-local bundle onto an empty test directory before claiming backup restoration.

For v1, completed browser-local playlists persist, but an in-flight prompt interrupted by server restart may require an explicit retry; durable resumable prompt jobs are deferred. For initial operation: cap simultaneous prompt work at one, bound daily prompt requests and log retention, monitor disk and memory, and surface failures in the app. Record provider usage, including transfer and optional storage/snapshot charges; budget alerts alone do not enforce a hard bill cap. Do not automatically upgrade the instance or subscribe to extra services. Stop accepting paid AI calls at the configured application limit. Before deleting any server later, retain a restorable copy and get explicit deletion scope.

## Time and deferred work

The implementation work above is now prepared. Remaining duration depends on Linux image/text acceptance, provider permissions, upload and DNS/TLS; no measured launch-time promise is available. Release plus models is approximately 4.74 GB, about 32 minutes of ideal transfer at a usable 20 Mbit/s, excluding the image and verification overhead.

Defer R2 migration, D1/database sync, multiple owner libraries, browser uploads, resumable analysis jobs, autoscaling, full cloud analyzers, new mix rendering, payments, provider integrations and whole-playlist archive generation. None is needed for this frozen shared-library launch.

Keep deployment code in the same repository under an isolated cloud-runtime/deploy directory. Commit/push only the intended code/document diff when requested; the working tree already contains extensive unrelated work. Artifact deployment need not wait for new GitHub OAuth or a CI pipeline. Add CI after the first manual scripted deployment proves repeatable.
