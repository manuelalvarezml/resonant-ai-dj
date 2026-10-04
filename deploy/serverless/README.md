# Serverless deployment and local development

**2026-10-03: deployed and live.** See [current cloud evidence](../../docs/cloud-library/first-release/serverless/LIVE_ROLLOUT.md) and [operations runbook](RUNBOOK.md). The final worker uses 3008 MB; 15 AWS text probes and the real production request passed. Earlier candidate commands below are development references.

This is the Lambda path. Do not use the preserved `deploy/first-release` VM commands. Deployment status and measured results live in [IMPLEMENTATION.md](../../docs/cloud-library/first-release/serverless/IMPLEMENTATION.md).

## Local compatibility build

Prepare a **new** allowlisted output directory. Original frozen artifacts are never modified:

```sh
packages/prompt-to-playlist/.venv/bin/python deploy/serverless/prepare.py \
  --release output/cloud-releases/first-release \
  --models output/cloud-models/first-release \
  --output output/serverless-build/CHOOSE-NEW-NAME

docker build --platform linux/amd64 --provenance=false \
  -t resonant-lambda:CHOOSE-NEW-NAME output/serverless-build/CHOOSE-NEW-NAME
```

The build checks every allowlisted file, model identity and frozen planner parity, and imports Linux dependencies. It never runs audio inference or OpenAI. Inspect image size/architecture before pushing; Lambda requires less than 10 GB uncompressed. Local text benchmarks require an explicit bounded memory/CPU/time wrapper; a Mac emulation result is not AWS latency.

## Durable worker contract

Private event: `{"jobId":"<uuid>","releaseId":"<sha256>"}`. Inputs live in S3 `requests/<uuid>.json`, hashed with sorted compact JSON. DynamoDB key is `pk=JOB#<uuid>, sk=META`; row includes `status`, `releaseId`, `requestSha256`, `deadline`, `owner`, `ttl`. Initial status is `dispatching` or `queued`.

Only a conditional transition claims work. Provider-start is marked before the sole paid attempt. Store audit/result first, then conditionally finish. Duplicate delivery returns without a provider call. Ambiguous failure becomes `outcome_unknown`; timeouts retain the claim until API reconciliation. Terminal states and deadlines allow the API to reclaim one of three slot rows atomically. There is no worker-side decrement that could double-release a slot.

Results and audits are separate S3 objects; browser authorization and presigned result URLs belong to the API, not this private worker. Warm MuQ weights persist only opportunistically. Text cache is durable in S3 and copied into a temporary per-job directory; original encoder identity, text and normalization remain unchanged. No MP3 access is needed by the worker role.

## Infrastructure and cloud benchmark

- `registry-template.json`: private immutable ECR with basic scan; Retain on delete. No automatic tag expiry can remove a deployed image.
- `benchmark-template.json`: one private x86 Lambda, one reserved execution, 360-second timeout, 512 MB scratch, logs-only role, seven-day logs. No URL, API, S3 permission, OpenAI key or provider calls. Fixed generic text only.
- `preflight.py`: read-only `manueldev` STS account guard and concurrency check. Never falls back to default. The account must permit reserved concurrency before deployment.

The isolated probe stack is separate from the application stacks. Login/API, static S3 transport, production IAM, jobs/admission reconciliation and CloudFront templates are now implemented locally. Their real AWS acceptance is recorded; use [RUNBOOK.md](RUNBOOK.md). Probe image upload itself transfers the frozen catalog/model bundle; it needs the same deliberate cloud execution review as other uploads.

The cloud benchmark should compare 8/6/4 GB, at least five real cold starts and ten warm invocations per surviving candidate. Force cold starts using distinct published probe configurations, not a claimed cache reset; verify `coldModel` and Lambda REPORT/init fields. Invoke synchronously, one at a time, with no retries after an ambiguous response. Upper bound before running: 45 × 360 s × 8 GiB × $0.0000166667 = $2.16000432 compute, plus ECR/logs. The original 8/6/4 GB comparison was blocked by the actual 3008 MB cap; final 3008 MB acceptance passed five cold and ten warm probes.

## Validation

```sh
PYTHONPATH=packages/prompt-to-playlist/src packages/prompt-to-playlist/.venv/bin/python \
  -m pytest -q deploy/serverless/tests
```

Tests exercise duplicates, checksum tampering, ambiguous provider outcomes, late completion, low remaining time, S3 failures and warm/cache behavior. Real DynamoDB concurrency, AWS execution/cold starts, auth/CDN and device playback remain required acceptance work.

## Disk-conscious local validation

The `dependencies` build target excludes model/release copies. Build it from a small context containing the Dockerfile and four lock files, then use the prepared full context as a read-only bind mount. This proves Linux runtime compatibility but does not produce the final self-contained Lambda image.

```sh
packages/prompt-to-playlist/.venv/bin/python deploy/serverless/run-local.py \
  --context output/serverless-build/candidate-4 \
  --output output/serverless-build/CHOOSE-NEW-RESULT.json --action text
```

The wrapper caps Linux at 4 GiB, no swap, two CPUs and 300 seconds, with a 768 MiB host-available floor. No network or writable source mount. An OOM or host-floor stop is a bounded negative result; it does not prove an 8 GiB AWS function will fail. Never raise the local cap blindly on this 16 GiB Mac. Final image export should start with at least 20 GiB of free host disk; earlier task-owned duplicate cache was reclaimed by exact cache IDs, without touching other projects.

The cloud runner is **plan-only by default**:

```sh
python3 deploy/serverless/run-cloud-benchmark.py
```

Its explicit `--execute` mode checks the personal account, function tag, image digest, entrypoint, concurrency and resource bounds. It publishes distinct probe versions to establish cold trials, limits total calls, saves attempt identity before each invocation and stops after an ambiguous response. It never retries a paid invocation automatically. It is not a routine health check; completed AWS receipts already exist.
