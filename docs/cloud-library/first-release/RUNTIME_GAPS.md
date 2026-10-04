# First shared-library release: runtime audit

> **Superseded deployment target, 2026-10-02 (D071):** this is the preserved VM preparation/evidence. The active target is the [serverless plan](serverless/README.md). Do not run these VM deployment steps for the serverless release; portable library/model/parity artifacts remain reusable.

**Current resolution, 2026-10-02:** The audit below predates implementation.
The exporter, frozen planner, production server and deployment kit are now built
locally. Read [PREPARATION.md](PREPARATION.md) for exact artifacts and tests.
Linux image/text acceptance and actual HTTPS deployment remain pending. The
initial findings are retained as history, not a list of still-unbuilt features.

2026-10-02 · Read-only implementation audit, followed by this documentation write.
The parallel web-edition chat is modifying the same checkout. Findings describe
the files observed during this audit, not a frozen release or deployed service.
All deployment, Linux-runtime, cloud playback and cloud security tests are **unrun**.
No server was started/stopped, no audio or text inference ran, and no credentials
were inspected in this audit.

## Shortest functionality-preserving route

Use one **x86 Linux VM with Caddy, Node and Python**, serving a prepared immutable
library release and the existing completed mix. Keep the current repository and
one shared collection. Favorites and saved playlists remain browser-local, as
the new web edition currently implements. Protect the whole app with the chosen
shared access mechanism and keep the OpenAI credential on the server.

An initial **8 GB RAM and at least 30 GB disk** allocation is a
conservative sizing hypothesis for the current full-model text encoder, not a
measured minimum. The proposed Lightsail tier has two vCPUs; benchmark with two
CPU threads. Four vCPUs are preferable where affordable, not a launch requirement.
Provider choice, current pricing and approved budget belong
to the accompanying deployment decision. Measure one uncached Linux text query
before downsizing or claiming latency.

This route avoids porting Python/Torch to a Worker and avoids adding a database
for a shared immutable catalog. It also removes dependence on the owner's Mac
being awake. R2/object storage can be added later if bandwidth, backup or library
growth justifies it. A static-only deployment does not preserve current
PlaylistIQ: novel descriptions require server-side text encoding.

The release excludes cloud audio analysis, browser uploads/conversion, source
recovery, dynamic mix rendering, automatic MixPlan generation, personal cloud
libraries, public signup, cross-device preference sync and a playlist-file
archive service. It preserves playback, analysis display, filtering, current
prompt planning/ranking and one completed DJ mix. Do not silently replace the
semantic branch with structured-only ranking to fit a smaller host.

## Current code, including the parallel web edition

| Behavior | Implementation evidence |
|---|---|
| Same repository, separate web configuration | [`scripts/serve.mjs`](../../../packages/web-player/scripts/serve.mjs), lines 12–27: `--web`, HTTP adapter, `edition:web`, selected route allowlist |
| Fully analyzed MP3 eligibility | [`src/release-policy.js`](../../../packages/web-player/src/release-policy.js), lines 1–2: current feature version, complete status, MAEST policy, all eleven stages passed/warning, metadata codec MP3 |
| Source-backed catalog generation | [`scripts/web-library.mjs`](../../../packages/web-player/scripts/web-library.mjs), lines 25–40: scan sources, select eligible hashes, build public tracks and private source mapping |
| Local browser-audio export support | [`scripts/web-library.mjs`](../../../packages/web-player/scripts/web-library.mjs), lines 11–21: owner-local POST, complete-feature check and byte-hash equality before saving |
| Catalog and playback endpoints | [`scripts/web-service.mjs`](../../../packages/web-player/scripts/web-service.mjs), lines 12–23: paginated tracks, playback sessions, MP3 GET/HEAD |
| One completed mix | [`scripts/web-service.mjs`](../../../packages/web-player/scripts/web-service.mjs), lines 24–29: completed M4A and graph-derived transition starts |
| Real PlaylistIQ retained | [`scripts/serve.mjs`](../../../packages/web-player/scripts/serve.mjs), line 26, and [`scripts/local-features.mjs`](../../../packages/web-player/scripts/local-features.mjs), lines 61–70: published-track allowlist then Python worker |
| Browser-local web preferences | [`src/app.js`](../../../packages/web-player/src/app.js), lines 26, 39–40: web edition saves favorites/playlists in localStorage |
| Static build excludes music | [`scripts/build.mjs`](../../../packages/web-player/scripts/build.mjs), lines 6–13: copies public/src and records hashes |

The older static-only deployment/API handoffs predate these new files. Their
future-work statements must not override the observed new web-edition behavior.
The new implementation is still a local preview, not a production server.

## Later same-day reconciliation

The parallel [web-edition checkpoint](../../../packages/web-player/docs/WEB_EDITION.md)
advanced to 187 MP3s. A follow-up read/stat check confirmed 187 source files,
1,910,985,140 audio bytes, eight staged MP3s totaling 72,317,539 bytes and a
16,916,601-byte catalog. The remaining mappings still depend on local sources.
No fresh digest verification ran. The detailed table below retains the earlier
179-track audit rather than relabeling its measurements. Recompute all final
eligibility/exclusion counts when freezing the release.

## Observed release/data snapshot

Method: read the saved `catalog.json` and `sources.json`; count catalog entries;
check source-file existence and sum filesystem `stat` sizes; parse cache JSON
and apply the current strict eligibility predicate; sum files beneath model,
text-cache, virtualenv and dist directories. No fresh media hash pass, audio
decoding, inference, browser storage inspection or manifest regeneration ran.
The 190-record eligibility count is across cached feature files; the 179-track
catalog count requires a resolved source in the saved manifest.

| Item | Observed value |
|---|---:|
| Saved published catalog tracks | 179 |
| Source mappings / existing mapped source files | 179 / 179 |
| Mapped MP3 bytes | 1,838,667,601 bytes; about 1.84 GB / 1.71 GiB |
| Public catalog JSON | 16,171,408 bytes |
| Private source mapping JSON | 40,441 bytes |
| Strict release-eligible MP3 feature files | 190 |
| Bytes in those 190 raw feature files | 39,871,966 bytes |
| All hash-named feature cache records | 236 complete, 80 partial; includes legacy versions |
| Files staged in `output/web-release/audio/` | Zero bytes |
| Pinned semantic-model asset directory | 2,663,058,281 bytes |
| Existing semantic-text cache | 1,829,559 bytes |
| Existing macOS package virtualenv | 1,672,451,501 bytes; not portable to Linux |
| Existing static dist directory | 404,553 bytes; may precede current source edits |
| Selected completed M4A mix | 26,022,836 bytes; duration 609.1 seconds |

Local evidence locations: [`catalog.json`](../../../output/web-release/catalog.json),
[`sources.json`](../../../output/web-release/sources.json),
[`web-features/`](../../../packages/prompt-to-playlist/output/web-features/),
[`semantic-models/manifest.json`](../../../packages/prompt-to-playlist/output/semantic-models/manifest.json),
and the selected [`mix manifest`](../../../output/mix-delivery/12fd88424ba311ff55d3d55d85a9a169d095e61620099f4a3ac6698971350b41/manifest.json).
These ignored runtime outputs are local evidence, not files to put in Git.

The saved source mapping currently contains local absolute paths. With the
release audio directory empty, this is **not yet a portable release bundle**.
Eleven eligible cache records are absent from this saved source-backed catalog;
browser-only converted MP3s are one possible cause, not a verified explanation.
The parallel chat's export work may change these counts. Reconcile sources and
freeze the final release; do not claim that 200+ tracks are cloud-ready from the
owner's estimate or the broad `complete` count alone.

The mix's two transitions are 203.65–232.74 seconds and 407.29–436.38 seconds,
approximately **3:23–3:52** and **6:47–7:16**. Evidence is the existing
[`graph.txt`](../../../output/mix-delivery/12fd88424ba311ff55d3d55d85a9a169d095e61620099f4a3ac6698971350b41/graph.txt).
Cloud playback of this completed file needs no renderer or source-track decoder.

## Python, models and memory

[`web_bridge.py`](../../../packages/prompt-to-playlist/src/prompt_to_playlist/web_bridge.py),
lines 161–185, reads raw saved features by hash, builds a planner catalog, calls
OpenAI, runs the query encoder and saves query/result evidence. Browser-facing
features strip embeddings through `publicFeatures`; those public records cannot
replace the private raw feature inputs used for semantic ranking.

[`semantic_audio.py`](../../../packages/prompt-to-playlist/src/prompt_to_playlist/semantic_audio.py),
lines 44–74, constructs and loads the complete MuQ-MuLan model for an uncached
description, including both towers. Lines 84–102 cache exact text vectors. Lines
252–274 run a bounded subprocess: four CPU threads, **6,000 MiB maximum worker
RSS**, **1,024 MiB minimum host available RAM**, and a **300-second timeout**.
Those are configured limits, not measured consumption or service guarantees.

The model weight file is 2,653,954,401 bytes; the whole model directory is slightly
larger, as shown above. Neither number is a RAM measurement. Historical macOS
audio smoke runs peaked at approximately 2,600 and 2,815 MiB process-tree RSS
([`ESTIMATOR_UPGRADE.md`](../../../packages/prompt-to-playlist/docs/ESTIMATOR_UPGRADE.md),
lines 46–48). They are audio-run measurements, not text-only Linux memory
measurements. No retained text-worker RAM measurement was found in the searched
JSON evidence. Linux cold/warm text latency and memory remain unmeasured.

The text-query path has no identified macOS-only execution requirement. The
watchdog uses psutil, and Torch runs on CPU. However, the existing Mac virtualenv
contains platform-specific binaries and must be rebuilt on Linux. Native wheel
availability/import compatibility needs an actual fresh Linux test.

Required runtime work:

- Pin a minimal CPU/Linux dependency set for Python >=3.12, Pydantic, MuQ,
  Transformers/tokenizer dependencies, Torch stack, NumPy and psutil. Node needs
  >=22. Do not copy the development virtualenv or install every analyzer.
- The current `semantic` extra does not explicitly include psutil, while
  `run_worker` imports it. NumPy is also imported by `analysis_worker` before
  dispatch. Inspect [`pyproject.toml`](../../../packages/prompt-to-playlist/pyproject.toml),
  lines 10–24, [`analysis_worker.py`](../../../packages/prompt-to-playlist/src/prompt_to_playlist/analysis_worker.py),
  line 17, and [`analysis_pipeline.py`](../../../packages/prompt-to-playlist/src/prompt_to_playlist/analysis_pipeline.py),
  line 264. A successful semantic-only installation cannot be assumed.
- Preserve the pinned semantic manifest/assets and encoder identity. Existing
  `identity()` checks installed asset presence/sizes even for cached text; the
  current runtime therefore needs those assets unless intentionally refactored.
- Parameterize model, raw-feature, text-cache, temporary-job and audit paths;
  retain writable cache/audit storage across application releases.
- Run one uncached text query and one cache hit on the chosen Linux host. Record
  peak process-tree RSS, cold/warm latency and unchanged ranking evidence.

## Critical portability risk: cached specialist provenance

[`estimator_profiles.py`](../../../packages/prompt-to-playlist/src/prompt_to_playlist/estimator_profiles.py),
lines 64–78, accepts specialist cache evidence only if its `model_id` matches
`identity(stage)` on the executing host. [`specialists.py`](../../../packages/prompt-to-playlist/src/prompt_to_playlist/specialists.py),
lines 37–43, hashes the installed versions of Essentia, PaSST, timm, Torch,
Torchaudio, Transformers and NumPy, plus adapter source and asset declarations.
Missing/different analyzer packages in a slim Linux service change this identity.
The quality profile can then fall back to older reference evidence despite the
published tracks having completed specialist analysis locally.

Before launch, decouple acceptance of **trusted published evidence** from the
serving host's installed inference packages, or export and validate frozen
planner catalogs locally for the supported profiles. Retain recorded source
hashes, model identities, sampling policies and provenance. Do not solve this by
installing all eleven analyzers in cloud, weakening evidence validation, or
silently accepting ranking changes. Prove local/cloud catalog and fixed-query
result parity, including selected specialist fields and semantic vectors.

## Production checklist

All items below are proposed implementation/verification tasks; none is marked
as a passed deployment test by this audit.

- [ ] Reconcile the final MP3 source inventory with strict current-stage
  eligibility; document excluded, missing and duplicate hashes.
- [ ] Build an immutable portable release containing exact eligible MP3 bytes,
  public catalog, private raw features, one mix stream and release checksums.
  Validate hashes before publication and again after transfer.
- [ ] Add a production server entrypoint that loads the frozen manifest rather
  than scanning local corpora or rewriting it at startup.
- [ ] Replace hardcoded localhost/HTTP assumptions with configured HTTPS origin
  validation and a trusted reverse-proxy boundary. Current blockers are
  `serve.mjs` lines 21/46, `web-service.mjs` lines 17/20 and
  `local-features.mjs` lines 17–21. Merely proxying the existing server is insufficient.
- [ ] Put Caddy HTTPS and the chosen access control in front of all static,
  catalog, audio, mix, PlaylistIQ and polling paths. Host/Origin checks are not
  authentication. Permit only intended production routes; owner-local analysis,
  conversion, recovery, import/export preparation and rendering stay unavailable.
- [ ] Keep the production web root limited to the static artifact. Dev static
  serving currently restricts itself to `public/` and `src/`, or `dist/`, and
  rejects traversal/dot components (`serve.mjs` lines 37–43); it is not an
  arbitrary repository file server. Preserve that separation. Never expose
  `sources.json`, raw embeddings, audit files, model weights or secrets.
- [ ] Rebuild and pin the Linux CPU Python runtime; fix trusted-feature
  compatibility and prove deterministic local/cloud replay parity.
- [ ] Configure the OpenAI key as a server environment secret. The current
  selected name is **`AUTODJ_OPENAI_API_DEV_KEY`**, from
  [`playlist.toml`](../../../packages/prompt-to-playlist/playlist.toml), line 9.
  `OPENAI_API_KEY` is not an implicit substitute. The local profile's fallback
  `~/.zshrc` is unnecessary on cloud; use environment injection instead.
  [`config.py`](../../../packages/prompt-to-playlist/src/prompt_to_playlist/config.py),
  lines 133–158, checks the selected environment name before bounded file lookup.
  Credential validity, account ownership and spending approval were not audited here.
- [ ] Retain the configured planner model/reasoning unless deliberately changed:
  `gpt-5.4-mini-2026-03-17`, low reasoning (`playlist.toml`, lines 8/14). Check
  actual model access in the intended personal OpenAI project before launch.
- [ ] Retain one active prompt worker initially; add prompt rate/spending bounds,
  sensible prompt timeout, restart behavior and generic client errors. Current
  jobs are in-memory and the wrapper timeout is four hours
  (`local-features.mjs`, lines 13, 50, 53, 69–70).
- [ ] Test the frozen release: unauthorized direct/alternate routes, full library
  load, eligible counts, saved browser state, play/pause/seek, mix transitions,
  HEAD/200/206/416 and range bytes, fresh PlaylistIQ request, reload/restart,
  backup restoration and previous-release rollback.
- [ ] Perform owner sanity checks on the final HTTPS URL, including the intended
  mobile browser. Desktop resizing alone is not mobile playback acceptance.

For the first release, restarting may discard an in-flight prompt job and require
a retry; durable background audio jobs are outside scope. Browser preferences
are intentionally local to each visitor/device, and publishing the owner's
library does not imply shared or synchronized playlist edits.
