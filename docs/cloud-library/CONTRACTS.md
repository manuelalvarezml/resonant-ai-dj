# Proposed cloud contracts

## Status and authority

Design draft 0.1, not implemented. This file does not change dj-engine or prompt-playlist serialized contracts. Existing models and ../SCHEMAS.md remain canonical for the local engine. New cloud envelopes must version independently and embed references to existing artifacts rather than silently changing their shape.

Every cloud record carries contract_version, id, tenant_id, created_at and updated_at with UTC timestamps. The server resolves tenant_id from authenticated context; the client may not choose it. Client-supplied IDs are validated against that context. Object paths remain internal. UTC time is not a unique job identity.

## Proposed records

| Record | Required fields beyond common envelope | Invariants |
|---|---|---|
| Library | owner_id, name, lifecycle_state, revision | Owner/account membership checked on every operation |
| SourceVersion | library_id, byte_size, sha256, original_name, raw_tag_artifact_id, object_ref, verification_state | Verified bytes immutable; filename is presentation data |
| Track | library_id, current_source_version_id, display_metadata, revision | Multiple editions may share recording/title but never collapse by title |
| FolderReference | library_id, parent_id, display_name, track_id, order | Relative hierarchy only; no filesystem traversal |
| UploadSession | library_id, expected_bytes, expected_sha256, reservation_id, provider_upload_ref, expires_at, state | Tenant-scoped capability, quota reserved, no playback until verified |
| AnalysisRun | source_version_id, pipeline_version, tool/model manifest, params_hash, stages, state | Outputs tied to exact source and stage versions |
| Annotation | track_id, descriptor, value, authority, source, confidence, status, evidence_ref, revision, supersedes_id | Raw evidence survives corrections; unknown ≠ false |
| CatalogSnapshot | library_id, revision, track/source/annotation references, vocabulary_version, digest | Repeatable retrieval against immutable membership/evidence |
| PlaylistRun | snapshot_id, request_ref, translator_manifest, validated_query_ref, result_ref, unresolved_constraints | Never invent descriptors or silently satisfy missing hard evidence |
| SavedPlaylist | library_id, name, ordered_track_refs, source_run_id, revision | Explicit current versus snapshot behavior; revision conflicts visible |
| PlanProposal | snapshot_id, proposed_plan_ref, authority, validation_report_ref | llm_proposal until validated; validation does not execute |
| RenderJob | approved_plan_ref, input_manifest_ref, profile_version, reservation_id, idempotency_key, state | Recheck ownership/deletion and hash before any work |
| MediaArtifact | source_refs, role, object_ref, sha256, bytes, profile_version, retention_until, state | Only verified published artifacts can be served |
| JobAttempt | job_id, attempt_number, lease_token, worker_manifest, started_at, ended_at, resource_usage, error | Old lease cannot publish; retry records preserved |
| UsageLedger | tenant_id, event_id, reservation_or_charge, quantity, unit, job_ref, reconciliation_state | Append-only; duplicate event cannot bill twice |
| DeletionRequest | scope, cutoff_revision, tombstone, requested_at, completed_at, residual_retention | Stop access/jobs first, erase all linked objects and replay tombstones after restore |
| ExportRequest | scope_revision, manifest_ref, expiry, state | Tenant authenticated; expiring artifact download, no public sharing |

The common tenant field on UsageLedger is inherited, not a second independent ownership value. Monetary amounts use integer minor units plus currency; storage uses integer bytes; duration uses explicit units; confidence is null when not established.

## Evidence and correction

Keep the exact seven authority values: encoded_fact, standardized_measurement, deterministic_measurement, benchmark_estimate, user_verified, llm_proposal, executed_action. A provenance value names tool/version or user/revision and the underlying source. Do not introduce synonyms.

A raw embedded genre tag means a tag was encoded. It does not establish a reviewed genre. Estimated BPM/key/beats/downbeats/sections remain benchmark_estimate. A user edit creates user_verified evidence, superseding the displayed estimate without deleting it. Lower-priority future analysis cannot overwrite that correction.

Hard negative filtering requires affirmative negative evidence or complete-axis coverage under the existing playlist semantics. Unknown vocal status cannot satisfy “no vocals.” Preferred energy can be unmet with a visible warning; an explicitly required energy descriptor must block a false match.

## Upload state machine

```text
reserved → uploading → uploaded → verifying → accepted
                  ↘ paused ↗           ↘ rejected
reserved/uploading/paused → cancelled
reserved/uploading/paused → expired
```

uploaded means the provider accepted bytes, not that the application trusts them. Completion must verify expected size, full hash, source eligibility and reservation validity. A client callback cannot directly mark accepted. A retry of completion returns the existing terminal result for the same session. A conflicting hash/size produces a conflict and quarantine.

Race rules:
- Cancel before publication invalidates the session and schedules multipart abort.
- Complete arriving after cancel/expiry cannot resurrect a track.
- A network loss after provider completion is reconciled by stat/hash checks.
- Duplicate accepted bytes may reuse a tenant-local source but preserve the new logical import record.
- Oversized actual bytes are quarantined and reservation reconciled; do not grant unlimited signed writes.
- An orphan provider upload is removed after the disclosed abandonment window.

## Job state machine

```text
queued → leased → running → validating → succeeded
             ↘ retry_wait → queued
             ↘ failed_permanent
queued/leased/running/validating → cancel_requested → cancelled
```

An attempt has its own status; the logical job has the state above. A retry never creates a new logical charge. Retryable transport and capacity failures use bounded exponential backoff with jitter and a max attempt/budget limit. Unsupported codec, invalid plan, hash mismatch, policy rejection and absent entitlement are permanent until a corrected request creates a new job.

Cancellation is cooperative plus a deadline: fence publication immediately, then terminate subprocesses and reclaim scratch. If the worker finishes after cancellation, staged output is not published. Deletion of an input blocks both queued and running publication.

## Proposed API surface

All mutation endpoints require authentication, tenant authorization, a versioned request and an Idempotency-Key where a duplicate creates cost or durable state. Reusing a key with a different body is 409. Never let the language model call these endpoints directly.

| Endpoint | Request / response | Required edge behavior |
|---|---|---|
| POST /v1/uploads | library, expected bytes/hash, display name → session and scoped transfer instructions | 413 oversized, 422 unsupported, quota refusal before transfer |
| GET /v1/uploads/{id} | Session and accepted part inventory | Reauthenticate before new capability; opaque provider refs |
| POST /v1/uploads/{id}/parts | Requested part numbers → short-lived capabilities | Enforce part number/count/size bounds |
| POST /v1/uploads/{id}/complete | Part identities → accepted/verification-pending | Server verifies provider state; idempotent |
| POST /v1/uploads/{id}/cancel | → cancellation state | Terminal cancel cannot be reversed by stale completion |
| GET /v1/tracks | Cursor, bounded filters, snapshot revision → page | Stable pagination; tenant and query limits |
| PATCH /v1/tracks/{id}/annotations | expected revision, change → new revision | If-Match/409 conflict; preserve provenance |
| POST /v1/playback-sessions | artifact/source and position → short capability + expiry | Verify state/entitlement; deny deleted/quarantined data |
| POST /v1/playlist-runs | request text, snapshot → proposed/validated result | Feature gate; refusal/incomplete/unsupported visible |
| POST /v1/plan-proposals | request + snapshot → proposal and validation report | Future-only authorization; no render side effect |
| POST /v1/render-jobs | approved plan, revision, budget acknowledgement → job | Separate approval and quota reservation |
| GET /v1/jobs/{id} | Stage, attempts, progress, terminal result | No fabricated percentage for unknown progress |
| POST /v1/jobs/{id}/cancel | → cancellation state | Fenced publication and bounded cleanup |
| POST /v1/exports | scope revision → export job | Own tenant only; no arbitrary URLs |
| POST /v1/deletions | scope revision → tombstone/request | Revoke future capabilities, cancel linked work |

Error envelope: code, safe_message, request_id, retryable, retry_after_seconds (when known), details with non-sensitive field errors. Retain provider debug details server-side with redaction. Unknown IDs use a consistent non-enumerating response policy. Never return bucket credentials, stack traces, private paths or full presigned URLs in support logs.

## Proposed event envelope

```json
{
  "contract_version": "cloud-event/0.1",
  "event_id": "opaque-unique-id",
  "type": "source.verified",
  "tenant_id": "resolved-by-server",
  "aggregate_id": "source-version-id",
  "aggregate_revision": 3,
  "occurred_at": "2026-09-08T00:00:00Z",
  "causation_id": "upload-session-id",
  "correlation_id": "request-id",
  "payload_ref": "internal-immutable-reference"
}
```

This is a non-executable design example, not a production schema or record. Use an outbox transaction for application events tied to DB writes. Deduplicate consumers by event_id and meaningful aggregate revision. A storage webhook must be authenticated, normalized and looked up against a valid upload; it cannot mint tenant ownership.

## Render reproducibility and publication contract

The cloud envelope references an unchanged approved MixPlan and RenderManifest family. The proposed additional execution manifest records source SHA-256 values, source versions, analysis snapshot/hash, exact plan/hash, renderer commit/package version, container digest, CPU architecture, FFmpeg build/configuration, decoder/encoder parameters, thread/determinism settings, output SHA-256 and all executed warnings.

Define separate assertions:
1. Plan reproducibility: the saved validated plan and sources can be recovered.
2. Same-environment render reproducibility: repeated execution yields byte-identical PCM or a documented tolerance for an explicitly approved nondeterministic path.
3. Cross-environment equivalence: measured duration/alignment/loudness and listening agreement under a documented tolerance.
4. Delivery acceptance: no clipped/unsafe output under the chosen headroom policy and accepted listening results.

Do not call all four “deterministic” without separate evidence. Pin or remove metadata timestamps for byte comparison. Lossy encoder changes create new profiles and hashes. Preserve reproducibility inputs for the retention promised to the customer; deletion can intentionally make an old render unreproducible, which must be disclosed in its manifest status.

## Contract verification plan

EX003–EX006 cover duplicate completion, interrupted uploads, wrong tenant IDs, stale revisions, corrupt hashes, spoofed MIME, repeated queue events, worker crash before/after publication, cancellation races, deletion during render, unsupported input, quota exhaustion and missing descriptor evidence.

Use generated synthetic identifiers and licensed/generated audio. At least two tenants are required for authorization tests. No current engine schema is changed until a separately authorized implementation task maps this draft against actual model fields and proposes a migration.
