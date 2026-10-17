# DJ Collection Analyzer & Set Builder — Product Plan

## 2026-10-17 — Album artwork, local only

[Artwork checkpoint](docs/ALBUM_ARTWORK.md): embedded-first extraction, conservative MusicBrainz/CAA fallback, album/negative caches, provenance, 500/96px derivatives, post-storage local import hook and resumable backfill are implemented. Only compact library/result/minimized-player thumbnails; both spectrograms preserved. No deployment. Personal cloud upload lifecycle, private derivative delivery and physical iPhone acceptance remain pending. Transition, analysis and ranking work is unchanged.

## 2026-10-06 — Individual accounts and spectrum motion

[Account release](packages/web-player/docs/ACCOUNTS_RELEASE.md) replaces shared hosted state with email/username/password accounts, private playlists/PlaylistIQ results/listening counters, owner-only bounded analytics and a full-spectrum motion override. Google sign-in/linking is implemented but activation and real-provider acceptance await a Google web client ID. Owner authorized deployment, a test user, live-history reset and Git push. Current rollout receipt and limitations are maintained in the linked checkpoint; audio, saved analysis and planner policy are preserved.

## Document role

This is the durable product north star. It explains what the project is for and
maps the original two-phase idea to the current three-step DJ Engine v1.

For implementation details, use `V1_ENGINE_PLAN.md` as the canonical source.
Do not implement from this file alone.

## Registered

2026-08-20

## Current status

Updated 2026-09-08.

The project now has a private GitHub recovery baseline. Repository and
component versioning, evidence retention, binary exclusions, and restoration
are defined in [`VERSIONING.md`](VERSIONING.md) (D044/E031).

- **Stage:** Step 1 complete. Step 2A scoring implemented (D032 / E022).
  Step 2B clip tools, the minimal manual-plan `render_set` vertical slice,
  exact-grid transition timing, `house_eq_v1`, and downbeat-click diagnostics
  are implemented (D034 / D036 / D037, E023 / E024 / E025). Step 3 is not
  started.
- **Agent takeover:** `AGENTS.md` is the live operating brief.
- **Current build milestone:** first successful listening checkpoint reached
  (D038/E026). Preserve the user-accepted 16-bar exact-grid transitions and
  `house_eq_v1` behavior. Next close final-bus headroom (+1.04 dBTP in v2),
  then test the baseline on a larger manual set. Do not auto-render or
  batch-render the 10 house MP3s. All-In-One RAM refinements are backlog D031.
- **Authorized test corpus:** `test_folder_10_house_tracks`.
- **Corpus state:** 10 MP3 files re-hashed 2026-09-03 before analysis.
- **Source policy:** read-only. No source MP3 may be modified. Render
  outputs must stay outside the music folder.
- **Environment:** Python 3.12.10 `.venv`, FFmpeg 8.0.1, Essentia
  `2.1b6.dev1389`.
- **CLI:** `dj-analyze`, `dj-score`, `dj-render`.
- **Authorization boundary:** Step 1, 2A scoring, 2B clip renders, and the
  manual MixPlan executor and bounded diagnostics are approved and implemented.
  The v1 and v2 examples were rendered by the user; v2 transition duration and
  downbeat alignment are accepted for the first version. Automatic MixPlan
  generation remains out of scope. The user authorized independent
  prompt-to-playlist development on 2026-09-07 (D039); it does not require
  completion of the engine's next slice. D040 then authorizes the larger
  local pool's read-only metadata catalog and the user's project OpenAI key
  for request translation, without expanding engine analysis/render scope.
- **Parallel playlist track:** independently installable
  [`packages/prompt-to-playlist`](packages/prompt-to-playlist/README.md), with
  replaceable request-translation/catalog adapters and deterministic retrieval.
  The first slice is implemented and independently tested (E027), with a
  native desktop prompt form and CLI. D040/E028 adds a local-folder metadata
  adapter and explicit OpenAI project configuration. D041/E029 corrects
  natural-language launch defaults and refreshes the lightweight interface.
  Further playlist work is paused at the user's request. When resumed, the
  next items are reviewed tag evidence and broader model-interpretation
  evaluation.
- **Cloud product discovery:** activated research/planning (D042 / D043). The product
  hypothesis is a portable, listenable cloud library for DJs first and personal
  music collectors second, with descriptor browsing, prompt-built playlists,
  and deterministic prompt-built DJ mixes. No cloud implementation or change
  to the current engine boundary is authorized yet.

## Product goal

Given a folder of local music and a natural-language request:

1. Analyze the tracks for the musical and technical information needed to mix.
2. Select and order compatible tracks.
3. Plan bounded DJ operations.
4. Render one new approximately requested-duration DJ mix.

Version 1 deliberately uses ten house tracks expected around 120–130 BPM. This
reduces early genre and tempo ambiguity while the analysis, planning, rendering,
and validation contracts are established.

## Three-step V1

### Step 1 — Audio intelligence

Extract and normalize:

- Stream facts and decode health.
- Tempo candidate.
- Musical key/mode candidate and DJ notation.
- Integrated loudness, loudness range, and true peak where supported.
- Beats and downbeats.
- Structural section boundaries/labels.
- Confidence, disagreements, provenance, versions, and warnings.

Selected candidate stack:

- FFmpeg/ffprobe for canonical decode, stream facts, health, and EBU R128.
- pyloudnorm as an independent loudness validator.
- All-In-One MLX for tempo, beats, downbeats, and sections on Apple Silicon.
- Beat This as an independent beat/downbeat challenger.
- Essentia `KeyExtractor` with the EDM-oriented profile for the first key
  benchmark.
- librosa for deterministic DSP support features and diagnostics.

Tempo, key, downbeats, and sections are estimates—not authoritative facts.
They remain `benchmark_estimate` values unless a future annotated-corpus gate
promotes them.

Output: a versioned `CollectionAnalysis` object containing one
`TrackAnalysis` per source file. See `docs/SCHEMAS.md`.

### Step 2 — DJ compatibility and manipulation tools

Build deterministic tools for:

- Harmonic compatibility using canonical key names plus Camelot/Open Key
  derivations.
- BPM compatibility and required stretch percentage.
- Track ordering under a story/tempo arc.
- Pitch-preserving time stretch.
- Gain and volume envelopes.
- Three-band EQ automation and low-frequency handoff.
- Beat/downbeat-aligned loops.
- Crossfades and bounded segment rendering.

Initial harmonic-safe set follows rekordbox Traffic Light Related 2 / standard
Camelot practice:

- Same key.
- Relative major/minor.
- One Camelot number clockwise or counter-clockwise on the same ring.

Initial story template for ten tracks:

- Tracks 1–6: progressively non-decreasing effective tempo.
- Tracks 7–10: progressively non-increasing effective tempo.
- Prefer harmonic compatibility and section/downbeat-aligned transitions.
- Penalize large time stretch rather than forcing every transition.

FFmpeg is the first deterministic rendering engine for gain, EQ, fades,
trim, loop, and assembly. Pitch-preserving stretch currently uses FFmpeg
`atempo` because this 8.0.1 build has no `rubberband` filter. Rubber Band
Library remains a pending quality comparison. Stem separation is deferred.
The first `render_set` accepts a strict manual plan containing
downbeat-indexed segments and 4/8/16-bar transitions, then emits PCM WAV plus a
measured render manifest. Transition seconds are anchored to detected
downbeat spans rather than rounded BPM. The current house style performs a
180 Hz midpoint bass handoff instead of only opposing whole-track fades.
Automatic plan generation remains later.

### Step 3 — Full folder-to-mix pipeline

Input:

- Music-folder path.
- Approximate target length in minutes.
- Natural-language brief such as “high-energy house mix,” “downtempo mix,” or
  “slow latincore mix.”
- Optional hard constraints and story template.

The language model receives:

- Compact track analyses.
- Confidence and authority labels.
- Available Step 2 tools with JSON schemas and hard limits.
- Duration and story constraints.
- Valid-plan examples.

The model returns a declarative `MixPlan`, never executable code. Deterministic
software validates track IDs, bounds, loops, stretch, gain/EQ limits, tool
names, operation conflicts, and estimated duration before rendering.

Output:

- Rendered mix audio.
- `MixPlan`.
- `RenderManifest` containing exact executed operations, versions, hashes,
  warnings, requested duration, planned duration, and rendered duration.

## Future product phase — Cloud music library service

**Status:** Deep research and local planning activated by D043. The first
[research package](docs/cloud-library/README.md) is complete as a desk study,
with sources, proposed contracts, costs, gates and maintained agent registers.
Customer interviews, legal/license clearance and technical experiments remain
unperformed. Recommendation: continue discovery; no full cloud build.
This phase is not part of
the current V1 implementation authorization. The local DJ engine remains the
active implementation track; prompt-to-playlist development is paused with its
existing progress preserved.

### Hypothesis

Offer DJs—and, secondarily, people with personal digital music collections—a
portable cloud home for owned audio. A user makes one large initial upload and
then smaller incremental uploads as their library grows. The service turns the
local engine and playlist package into approachable product workflows without
requiring users to install specialist desktop software or run terminal
commands.

The hypothesis has two important adoption risks to test early: relatively few
people maintain substantial digital music libraries, and even those users may
resist a long first upload. The initial-upload cost should therefore be treated
as a product/onboarding problem, not only a technical transfer problem.

### Candidate product capabilities

- **AI playlist generator:** build editable playlists from natural-language
  prompts using only supported catalog evidence.
- **AI DJ mix generator:** choose and sequence tracks, produce a validated
  declarative MixPlan, and render a reproducible mix whose transitions and
  executed operations are deterministic. Allow the finished mix to be
  downloaded.
- **Cloud listenable library:** securely play a user's owned music from the web
  with practical seeking and retrieval times.
- **Musical descriptor library:** browse, search, filter and sort tracks by
  sourced descriptors such as genre, BPM, key, mood and energy, while retaining
  provenance, confidence and user corrections.
- **Later, not now:** a dedicated desktop/mobile application that makes the
  library feel more like a personal streaming service and simplifies ongoing
  sync.

### Discovery and definition backlog, in order

The original ordered backlog below is retained. Its current artifact/evidence
coverage is mapped in [TRACEABILITY.md](docs/cloud-library/TRACEABILITY.md).
Agents should continue from [STATUS.md](docs/cloud-library/STATUS.md), not
restart completed desk research. No empirical gate is passed by a report.

1. **Compare music-storage services first.** Produce a current decision matrix
   for the best cost, ease of integration and retrieval performance. Include
   storage price, request charges, internet egress/CDN cost, minimum-retention
   or retrieval fees, latency, byte-range playback, signed access, resumable
   multipart uploads, integrity checks, lifecycle/versioning, regions,
   encryption, SDK maturity, local-development support and vendor lock-in.
   Model at least small, medium and DJ-sized libraries plus initial upload,
   normal listening and mix-download traffic.
2. **Validate the market and primary user.** Interview DJs and personal-library
   owners; estimate library sizes, formats, current storage/workflows, upload
   tolerance, privacy concerns and willingness to pay. Test whether AI mixing,
   prompt playlists, cloud playback or descriptor organization is the actual
   acquisition/retention hook. Define evidence that would reject the idea.
3. **Define the smallest product workflow.** Specify onboarding, first upload,
   background processing, library browsing, playback, prompt-to-playlist,
   prompt-to-mix, progress/failure states, mix preview and download. Decide
   which user segment and browser/device is supported first and what is
   explicitly excluded from the MVP.
4. **Choose the cloud architecture and development cycle.** Compare a managed
   backend with a thin application service against serverless and container/job
   approaches. Define object storage, metadata database/search, authentication,
   queues, workers, cache/CDN, observability, infrastructure-as-code,
   local/staging/production environments, deployment/rollback, migrations and
   the cheapest realistic test loop. Prefer reversible choices until measured
   scale requires specialization.
5. **Design upload, import and incremental sync.** Cover direct-to-storage
   uploads, resumable/chunked transfer, concurrency, checksums and deduplication,
   duplicate/version policy, supported audio formats, metadata preservation,
   interrupted uploads, per-user quotas, folder/playlist structure and the
   later possibility of a sync helper without making an app part of the MVP.
6. **Define playback and retrieval behavior.** Decide whether the service plays
   originals, cached browser-compatible derivatives or both; evaluate seeking,
   byte ranges versus streaming manifests, waveform/preview generation,
   loudness handling, device/browser codec support, cache policy and acceptable
   time-to-first-audio. Keep downloadable originals separate from generated
   mixes and temporary analysis/render artifacts.
7. **Design descriptor ingestion and correction.** Separate encoded tags,
   standardized/deterministic measurements, fallible audio estimates,
   LLM proposals and user-verified edits. Decide which descriptors are required
   for MVP, where analysis runs, when it is retried, how versions are migrated,
   how a user corrects results and how large backfills are priced/scheduled.
8. **Define the AI and deterministic execution boundaries.** Reuse the
   prompt-to-playlist query/retrieval contracts and the DJ engine's
   MixPlan/RenderManifest boundary. Models may interpret intent and propose a
   plan; ordinary code must authorize data access, validate IDs and limits,
   execute transitions, and make a generated mix reproducible from pinned
   inputs and versions. Decide retention and privacy rules for prompts and
   model-provider data.
9. **Resolve account, security, privacy and rights requirements.** Specify
   tenant isolation, least-privilege signed URLs, encryption, secrets, audit
   records, deletion/export, backups and disaster recovery. Before launch,
   obtain appropriate legal guidance on storage/playback of user-owned music,
   terms, copyright complaints, prohibited sharing, generated-mix downloads,
   privacy/data-processing obligations and regional constraints.
10. **Build a full unit-economics model.** Include storage, upload/download
    transfer, repeated streaming egress, descriptor-analysis compute, waveform/
    derivative storage, model calls, mix rendering, queues, logs, support and
    abuse. Use it to propose quotas, job priority, trial limits and pricing, and
    test whether heavy listeners or repeated renders make the service
    uneconomic.
11. **Define reliability and operations.** Set targets for upload completion,
    library consistency, playback start, job latency and render success. Plan
    idempotent jobs, retries, cancellation, partial-failure recovery, source and
    artifact retention, monitoring, support diagnostics, abuse/rate limits and
    account deletion.
12. **Write the contracts and make a build/no-build decision.** Produce a threat
    model, architecture decision records, data model, API/job contracts, cost
    spreadsheet, user-flow prototype and a small end-to-end technical spike
    using non-sensitive test audio. Set explicit gates for demand, upload
    completion, retrieval/playback performance, deterministic render
    reproducibility, security and sustainable cost before prompting for or
    implementing the full cloud module.

### Boundary with current work

The cloud service is a possible host and product shell around the existing
components, not permission to merge them prematurely. The DJ engine's current
headroom and larger-manual-set work remains local. The playlist package stays
paused and independently reusable. Automatic MixPlan generation, cloud upload,
remote analysis/rendering, user accounts and production hosting each require a
later explicit implementation decision after the discovery gates above.

## Mapping from the original phases

The original plan had:

- Phase 1: collection analysis and prompt playlists.
- Phase 2: agentic DJ tools and automatic sets.

V1 maps them as follows:

- Original Phase 1 → V1 Step 1 plus the selection part of Step 3.
- Original Phase 2 → V1 Step 2 plus execution/rendering in Step 3.

Automatic audio-based genre/mood/energy tagging, semantic embeddings, catalog
enrichment, and broad similarity remain deferred from the engine. The tooling
report found that they do not meet its strict calculated-feature quality
requirement. D039 now authorizes a separate recommendation layer to interpret
requests and search supplied, provenance-bearing tags. That changes candidate
selection scope; it does not promote subjective labels into measured facts or
create missing labels for the real corpus.

## Independent prompt-to-playlist module

The user explicitly requested this track on 2026-09-07 so it can progress
alongside analysis and mixing and be reused by other projects.

- Own the module under `packages/prompt-to-playlist/` in this repository for
  versioning, with an independent install, runtime, lockfile, tests, and docs.
- Use explicit typed boundaries: request → translation proposal → validated
  query → deterministic matched tracks. Translation itself is replaceable and
  may be nondeterministic; normalization, validation, filtering, ranking, and
  track lookup belong to ordinary code.
- Use replaceable catalog adapters. The DJ adapter only reads the existing
  analysis JSON and preserves source IDs and estimate provenance. The explicit
  local-folder adapter hashes sources and reads ffprobe metadata (D040);
  normal playlist requests only read the resulting catalog JSON.
- Keep the first contract small: required/preferred/excluded descriptors,
  BPM bounds, excluded IDs, result count, and relevance/BPM ordering.
- Give the user a native natural-language OpenAI desktop form and CLI. Keep
  the limited offline grammar behind explicit CLI `--provider rules`; it must
  not become a silent product default or API-error fallback (D041).
- Configure the real-pool workflow with OpenAI through `playlist.toml`, a
  pinned editable model, and the project's named credential variable. Keep
  credentials out of the repository and local catalog/audio out of requests.
- Surface missing evidence and unresolved constraints. Do not infer energy
  from BPM/LUFS or assign a genre to every track from a folder description.
- Return candidates with evidence; do not create MixPlans, select transition
  windows, stretch audio, or publish playlists to another service.

The package README and its schema documentation own the detailed API. A
future DJ bridge can consume its track IDs after the engine's automatic
planning work is separately authorized. The Spotify project can reuse the
same core after adding its own catalog adapter and application-specific
constraints; that integration is still planning only.

## Non-goals for V1

- Modifying source MP3s.
- Stem separation or stem-level mixing.
- Live playback/controller integration.
- Automatic cue export into proprietary DJ libraries.
- Claiming model estimates are nearly perfect.
- Catalog identity/enrichment through Chromaprint, AcoustID, MusicBrainz,
  Discogs, Spotify, or Beatport.
- Allowing the LLM to execute shell commands or arbitrary code.
- Selecting the engine MixPlan planner's LLM vendor before its provider-neutral
  contract exists; D040 separately configures OpenAI for playlist translation.

## Canonical documents

- `AGENTS.md` — agent takeover brief; start here in a new session.
- `README.md` — entry point, status, and document map.
- `V1_ENGINE_PLAN.md` — implementation architecture, milestones, and acceptance
  criteria.
- `docs/SCHEMAS.md` — canonical JSON contracts and authority vocabulary.
- `docs/CORPUS.md` — authorized corpus, manifest, and substitution policy.
- `DECISION_LOG.md` — append-only decisions and supersessions.
- `EXPERIMENT_LOG.md` — append-only inspections, commands, outcomes, failures,
  and learnings.
- `docs/CHANGELOG.md` — document and plan revision history.
- `packages/prompt-to-playlist/README.md` — reusable playlist module setup,
  architecture, contracts, and independent validation.
- `AUDIO_ANALYSIS_TOOLING_REPORT.md` — sourced tool/evidence registry (research
  cutoff 2026-08-30; not live v1 status).

## Documentation discipline

Before a major tool or architecture change, re-read the canonical documents.

After each implementation or experiment:

1. Update `AGENTS.md` and milestone status in `V1_ENGINE_PLAN.md`.
2. Append decisions to `DECISION_LOG.md`.
3. Append commands, versions, results, failures, and lessons to
   `EXPERIMENT_LOG.md`.
4. Update `docs/CHANGELOG.md` for documentation changes.
5. Reconcile this product plan when scope changes.
6. Update the tooling report only when evidence, lifecycle, or a tool decision
   changes.

Never erase a failed path. Add a dated superseding entry explaining what
changed and why.

## Approval checkpoint

### 2026-08-31 — completed

Documentation was ready for review. The next authorized action was to audit
the existing `uv` scaffold and then implement Step 1 on the authorized
10-track corpus. That path completed through E006–E021.

### 2026-09-04 — completed

The manual MixPlan validator and `dj-render set` are implemented (D036 /
E024), with 50 tests passing. The checked-in three-track plan validates to
609.318 seconds. The user subsequently rendered and heard it.

### 2026-09-05 — engine checkpoint

The user reported both 8-bar transitions were too short, the opposing volume
fades were not a sufficient house transition, and the entries sounded
downbeat-misaligned. E025 traced the phase error to rounded-BPM overlap math,
not detector disagreement. The revised v2 plan validates and renders to
609.100 seconds with two exact-grid 29.090-second `house_eq_v1` transitions.
The user accepted transition duration and downbeat alignment as a much better
first version; the primary downbeat diagnostic was also good (D038/E026).
The next recommended product-quality slice is final-bus headroom/limiting,
because the accepted v2 render measured +1.04 dBTP, followed by a larger
manual-set test. Do not batch-render the corpus or start Step 3. All-In-One
host/model changes remain backlog D031.

### 2026-09-07 — parallel playlist track authorized

The user requested a simple, reusable prompt-to-playlist module with
deterministic tools and replaceable adapters, independent from continued
audio-engine work. D039 supersedes the blanket hold on LLM development only
for this candidate-selection track. E027 records the implemented desktop/CLI
slice, isolated tests, build, GUI smoke check, and metadata-only real-catalog
validation. Live model quality and real semantic tag coverage remain to be
evaluated. Automatic MixPlan generation and rendering integration
remain deferred. The engine's next slice above remains unchanged.

### 2026-09-07 — larger pool and OpenAI setup authorized

The user requested the approximately 120-track pool and their project OpenAI
key for the playlist form. D040 scopes this to read-only hashing/ffprobe
metadata import and bounded Responses API translation. `playlist.toml` and a
desktop launcher provide the project setup while preserving reusable offline
defaults. E028 records observed catalog coverage, source preservation, and
live API checks. Semantic gaps require reviewed evidence; a functioning model
must not invent track tags to fill them. Heavy acoustic analysis, automatic
MixPlans, audio rendering, and publication remain outside this request.

### 2026-09-07 — natural-language workflow correction

The user’s short “house dj set energetic” description reached a stale offline
window. D041 supersedes the old default: desktop always uses OpenAI and has
bounded project-profile discovery; generic CLI prompt also defaults to OpenAI.
A light Tk redesign makes criteria, artist/BPM results and missing energy
evidence visible without exposing grammar. Translator v3 requires a directly
requested single genre and keeps ordinary energy/mood as preferences. E029
records verification. The pool and engine boundaries remain unchanged.
