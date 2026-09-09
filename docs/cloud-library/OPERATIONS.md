# Reliability and operating plan

## Service objectives

All targets are proposed for an authorized beta, not observed performance or contractual SLAs. Record network/browser/region and sample sizes with every result.

| Journey | Proposed objective | Measurement and exclusions |
|---|---|---|
| Eligible file acceptance | ≥99% for supported valid files on stable network | Count distinct files; separate user cancel/unsupported from service failure |
| Interrupted batch recovery | ≥95% finish without resending verified completed files | Report client restart/reselect and network cases separately |
| Playback start | p95 ≤3s, cold path on defined 20Mbps+ broadband | Time from play action through auth to audible audio |
| Seek | p95 ≤2s | Beginning/middle/end; direct versus derivative path |
| API/library availability | 99.5% monthly beta objective | Define eligible requests and maintenance policy before launch |
| Metadata readiness | p95 ≤60s for ≤20MB MP3 after verification at nominal load | Larger/unsupported inputs classified separately |
| Render execution success | ≥95% of valid supported plans in defined workload | Quality acceptance separate; infrastructure retries count |
| Tenant isolation | Zero observed unauthorized successful access in test matrix | Security hard stop, not a probabilistic SLO |
| Metadata recovery | Proposed RPO ≤24h, RTO ≤4h | Restore rehearsal required; tighter paid targets may cost more |

Avoid promising render wait times until cold-start and compute benchmarks exist. Show queue position or stage when known; otherwise show queued/running rather than a fabricated ETA.

## Failure taxonomy

Errors must distinguish transient transport, provider throttling, credentials, unsupported codec, corrupt source, hash mismatch, quota exhaustion, decoder timeout, memory limit, scratch exhaustion, analysis failure, inadequate evidence, invalid plan, render quality rejection, stale publication and deletion conflict. Each error carries a safe user message, retry eligibility, attempt/budget ceiling and operator diagnostic ID.

Do not retry permanent media/plan failures automatically. Do not rerun a memory-exhausted job repeatedly at identical settings. A proposed larger worker requires authorized budget and benchmark evidence. Never reduce the local reclaimable memory floor to make a cloud hypothesis look viable.

## Queue and reconciliation

Use durable jobs with leases, attempt histories, heartbeat timestamps and dead-letter state. Limit concurrency per tenant and worker class. Interactive library actions have priority over backfills. Rendering cannot starve playback authorization or upload completion.

Reconcile quota reservations against actual object bytes and completed jobs. Sweep abandoned multipart uploads and orphan staged outputs after their retention windows. Retry a notification, not the media job, when only result delivery failed. A failed callback must not double-charge or lose a successful artifact.

Before publication, recheck source lifecycle, approved-plan revision, tenant status, fencing token and result checks. The DB publication transaction records artifact availability and usage events together through an outbox. Object existence alone never means a ready track or mix.

## Incident playbooks

| Incident | Immediate action | Recovery / evidence |
|---|---|---|
| Suspected tenant leak | Disable capability minting and affected delivery path; preserve restricted audit evidence | Scope exposure, rotate/revoke as applicable, counsel notification review, regression proof |
| Runaway cost | Disable new expensive jobs/uploads, retain private playback where safe | Attribute bytes/jobs, reconcile bill, fix quota path before reopening |
| Provider outage | Backoff with jitter; show partial availability; stop noisy retry storms | Reconcile terminal jobs/objects; do not invent successful uploads |
| Worker OOM/disk full | Stop affected worker class, preserve safe metrics, cleanup scratch | Reproduce on synthetic fixture, adjust authorized profile or reject input |
| Corrupt/missing original | Quarantine reference; stop dependent analysis/render | Verify replicas/backups and checksums; communicate actual recoverability |
| Bad deployment/migration | Disable feature flag, restore compatible image, pause impacted queue | Apply forward-compatible correction; destructive rollback separately reviewed |
| Rights complaint | Restricted case record and appropriate access restriction | Follow approved jurisdiction procedure; retain only necessary evidence |
| Account deletion stuck | Keep tombstone and access block; alert operator | Complete provider/cache/backup reconciliation; report residual retention honestly |

Record incident timestamps, severity, affected tenants/jobs, detection, customer effect, containment, root cause or current hypothesis, corrective action, owner and verification. A research retrieval problem is not a production incident.

## Backup and disaster recovery

Object durability is not a backup plan. Immutable keys protect logical versions but not accidental deletion by a privileged service. Evaluate independently controlled backup copies against costs, rights and deletion obligations. Keep database restore points consistent enough to reconstruct object references or recover through manifests.

At an authorized rehearsal, create two synthetic tenants, upload fixtures, correct tags, save a playlist, create a bounded artifact, delete one source, take/restore backups and replay tombstones before enabling traffic. Check source/artifact hashes, tenant ownership, deleted-data denial and reproducibility references. Measure recovery time and document unrecoverable windows.

Full-library loss is materially different from a delayed derivative job. The product must never market itself as the sole backup until a tested recovery and financial plan supports that promise.

## Observability and support

Track active users, usable libraries, upload bytes/goodput/resends, orphan bytes, provider requests/egress, auth failures, playback start/seek errors, job queue age, attempts, CPU/GPU seconds, peak RSS, scratch high-water mark, catalog coverage, plan rejection reasons and mix quality outcomes.

Avoid song titles, full prompts, filenames and signed URLs in general logs. Use tenant/job IDs with controlled lookup. Provide an opt-in sanitized support bundle: app/browser version, request IDs, error category, counts and relevant timing. Do not ask for audio to diagnose an authentication failure.

Define who responds before accepting customers. Record weekly operations review only once a beta exists; no scheduled monitoring or messages have been created by this research. A maintained runbook is not an on-call service.
