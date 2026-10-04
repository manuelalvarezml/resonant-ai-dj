# Serverless implementation and rollout

**2026-10-03: private playback and PlaylistIQ are live.** Read [deployment evidence and remaining owner acceptance](LIVE_ROLLOUT.md). The actual worker uses 3,008 MB; Free CDN is ACTIVE, all 15 final text probes passed and the production prompt returned ten matches. Earlier dated planning/preparation statements below are historical.

Plan completion is not deployment completion. The existing VM artifacts remain a fallback; no Lightsail server is required by this design. The earlier 117 Node / 551 Python / 60 parity results are baseline evidence, not serverless integration tests.

## Ordered work and acceptance

| Stage | Work | Finish evidence |
|---|---|---|
| 0. Account preflight | Verify selected STS target; await pending Lambda concurrency1,001 request; confirm 8 GB eligibility and CloudFront Free compatibility; use generated hostname | Sanitized quota/configuration readback and reviewed costs |
| 1. Lambda feasibility | Build x86 Python image with runtime client and pinned planner/models; implement warm encoder and bounded scratch | Expanded image under 10 GB; 512 MB scratch sufficient; 60/60 parity; no secret layers |
| 2. Benchmark | Isolated function, generic text first; test cold/warm at 8/6/4 GB and 2 versus 4 threads where useful | At least five cold and ten warm trials per surviving candidate; billed duration, peak memory, p50/p95, vector hashes and cost/request |
| 3. Infrastructure code | Separate `deploy/serverless` CloudFormation/SAM stack for all proposed services, roles, policies and retention | Template validation and change-set review; correct account; private buckets; persistent resources retained |
| 4. Control plane | Login/cookies, durable jobs/results, idempotency, quota transactions, async dispatch and expiry recovery | Duplicate/crash/ownership/cap-race tests pass; denied direct origin access |
| 5. Static transport | Derive catalog pages and S3 mapping from original frozen manifest; adapt player URLs/results | All 187 tracks, 25 per page; no private fields; no Lambda on audio/catalog GET; Range 206/416 and HEAD work |
| 6. Fixture deployment | Reviewed resources, fake audio and fake planner first; enforce access policies before real data | Actual HTTPS/auth/cache isolation, origin headers, S3 denials and session expiry across two browsers |
| 7. Library publication | Upload explicit allowlist/checksums; verify every object; configure intended OpenAI secret privately | Full remote inventory; bounded real prompt; desktop and phone playback/seek/mix/queue with Mac disconnected |
| 8. Failures and rollback | Disable worker, force timeout, expire cookies and restore prior release/runtime | Authorized playback survives AI outage; no duplicate logical paid attempt; previous release restored |

Cloud benchmark/provisioning/upload stages are future execution, not already authorized by this research request. Complete local implementation and a concrete resource change set before the final launch approval. Account identity is settled; do not ask the owner to choose credentials again.

## Reuse and adaptation

Reuse the immutable 187-MP3 selection, exclusions, raw feature evidence, MuQ model assets, frozen five-profile planner and 60 parity cases. Keep the same repository and browser player. Preserve the prepared listener-password choice unless the owner changes it.

Adapt the exporter into S3 mappings and static pages; add signed-result downloads to the HTTP adapter. Change the text encoder's model lifetime and memory accounting without changing vectors/ranking. Replace local audit/cache files and job counters with durable S3/DynamoDB state.

For this target, replace the long-running Node job supervisor, disk queue, Caddy and VM Compose/SSH scripts. Preserve them as the superseded VM path. Its source digest is not a Lambda image digest. The RSA-4096 SSH key must not become the CloudFront signing key.

## Required failure tests

Before real paid translations, exercise concurrent same-token submissions, token/payload conflicts, crashes between S3 and DynamoDB writes, dispatch failures and lost dispatch acknowledgements. Duplicate delivery must not trigger another paid call. Test timeout after a possible provider charge, result-upload/state-write ordering, session ownership, event expiry, worker hard timeout and stale slot recovery when no browser was polling.

Use conditional state changes and a provider-started marker. Expose `outcome_unknown` after ambiguous paid work; an explicit retry creates a new counted attempt. A local timeout cannot establish whether the provider charged. A failure queue record does not itself update DynamoDB; logical expiry and reconciliation must work independently.

Verify failure-destination permissions and DestinationDeliveryFailures. Do not replay the diagnostic queue automatically. Test login failures, direct API origin calls, unsigned S3/CDN access, cookie expiry during seeking and separate browser sessions. Confirm a result URL cannot be obtained for another session's job.

## Release binding and rollback

Bind the frontend release ID, S3 manifest/version IDs, frozen planner fingerprint, model manifest, ECR digest and Lambda published version in one deployment record. No mutable `latest` image, `$LATEST` production invocation or automatic source scan.

For this small release: pause admissions, drain or expire outstanding jobs, verify the candidate tuple, switch the worker alias and active-release metadata, then publish the static pointer last. Deploy a root entry document referencing versioned app assets; do not assume S3 rewrites `/index.html` to `app/releases/...`. Old tabs receive an explicit 409 refresh response for new AI work; their immutable media remains available.

Retain the previous image/version and referenced objects. Rollback restores the same verified tuple after pausing/draining jobs. Do not casually delete queued events or media. CloudFront Free's separate continuous-deployment/staging-distribution feature is unavailable; use fixture prefixes and versioned application paths. Handle plan subscription lifecycle separately from distribution deletion.

## Operational handoff

Record the real URL, worker memory, measured cold/warm cost and latency, granted quota, account suffix, tested release/image tuple and device results here. Include Free-plan eligibility readback or an explicitly chosen and recosted PAYG fallback.

Retain verified local audio/model/release copies. Versioning covers mistakes; regional outage recovery would require restoration elsewhere and a CDN origin change. This plan does not implement active-active regional failover. Proposed latency goals are acceptance targets, not measurements.

Review at 80 GB/month or 800,000 CDN requests, near 900 AI requests/month, or when cold starts dominate cost. Wider sharing prompts an individual-account design. These thresholds never trigger an automatic paid upgrade.

No infrastructure, quota request, subscription, alert email, upload or scheduled monitor was created during the D071 planning stage. D072/CE024 later submitted the no-cost quota request as predeployment preparation.

## D072 continuation — local stages implemented

See [IMPLEMENTATION.md](IMPLEMENTATION.md). Worker/API/static transport/infrastructure code now exist and have local test evidence. Stage1 still lacks final self-contained image export; stages0/2/6–8 need provider execution/acceptance. T034 is in progress, not complete. Newly documented PricingPlanManager permits an explicit FREE subscription in the edge stack; no manual paid fallback. The existing frozen release remains exact.
