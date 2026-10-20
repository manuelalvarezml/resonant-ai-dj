# Resonant — AI Music Discovery & DJ Mixing

Resonant is a music application connecting natural-language requests to explainable playlists and DJ mixes.

**Product status:** active development, with an AWS-hosted private trial at [resonant.lat](https://resonant.lat). The trial requires an approved account; it is not a public signup or a claim of broad adoption.

**Repository scope:** the source snapshot below was last published in September 2026. The later October private deployment adds accounts, durable owner-scoped jobs and private progressive mix playback; those later changes have not all been synchronized to this public snapshot. See the [current case study](https://manuelalvarez.cc/project-resonant) for the deployed product's capabilities and boundaries.

Core engineering work includes semantic retrieval, deterministic ranking, musical-feature analysis, explainable playlist construction and audio rendering. Acoustic analysis remains local; cloud deployment uses exported catalog evidence and text inference.

Built by [Manuel Alvarez](https://manuelalvarez.cc/). [Contact / request a walkthrough](https://manuelalvarez.cc/contact).

---

# DJ Collection Set Builder

Local-first DJ engine that analyzes a folder of owned music, plans compatible
transitions, and renders a new approximately requested-duration mix from a
natural-language brief.

## Current status

**Step 1 corpus analysis is complete. Step 2A scoring, Step 2B clip
renders, and a minimal manual MixPlan set renderer are implemented. A reusable
prompt-to-playlist package is implemented as an independent track and is now
paused. A future cloud music-library product is recorded as a discovery-only
hypothesis.**

Agents taking over: read [`AGENTS.md`](AGENTS.md) first.

Repository history, component version namespaces, checkpoint tags, tracked
evidence, excluded audio, and recovery are defined in
[`VERSIONING.md`](VERSIONING.md). The first durable repository baseline is
`checkpoint-2026-09-09` in the private GitHub repository
`manuelalvarezml/resonant-ai-dj`.

All 10 tracks are in `output/step1-collection.json`. Source hashes match.
Tempo/key/beats/sections remain `benchmark_estimate`. Clip and set render
tools write PCM outside the music folder (D034 / D036). The manual
`render_set` path is implemented and synthetically tested. The user rendered
and heard the v1 three-track set; its 14.44-second volume-only transitions were
too short and sounded downbeat-misaligned. D037/E025 adds exact detected-grid
timing, a 29.09-second `house_eq_v1` bass handoff, and audible downbeat-click
diagnostics. The user rendered v2 and accepted its transition duration and
downbeat alignment as a strong first version (D038/E026). Automatic MixPlan
generation is not started. Final-bus headroom is still pending:
the successful v2 render measured +1.04 dBTP. All-In-One RAM options remain
backlog D031.

## Parallel prompt-to-playlist track

[`packages/prompt-to-playlist`](packages/prompt-to-playlist/README.md) owns
request translation, a versioned descriptor vocabulary, deterministic
filtering/ranking, and matched-track lookup (D039/E027). It is an independently
installable Python package with its own dependencies, tests, lockfile, and
documentation. Its first slice passed 190 isolated tests; the engine's 54
tests still pass. E027 records the build and catalog/UI smoke checks.
The current real-pool/OpenAI package is version 0.2.0, with 363 package
tests passing and a successful standalone wheel/source build (E029).

The user enters a set description in a native desktop form or the CLI.
A replaceable translator proposes a strict
query; code validates the descriptors and constraints, searches a supplied
catalog, and returns track IDs with evidence and explanations. A limited
offline rules mode supports repeatable local testing; the LLM adapter
only sees the request, vocabulary, and query contract. Unknown or unsupported requests remain
explicit rather than silently broadening the search. Neither this package nor
its model gets audio-render tools.

The existing DJ JSON can be imported without reading audio. It contains BPM
estimates and source metadata but no semantic tags, so mood/genre/energy
matching requires separately supplied evidence. BPM and loudness do not
become mood or energy labels. Synthetic labeled examples demonstrate that
path. Package setup, prompt-entry usage, and contracts live in its README.

The user's follow-up authorizes the larger local track pool and their project
OpenAI key (D040/E028). The new folder adapter only hashes source files and
reads container/embedded-tag metadata through ffprobe; it does not run the
heavy audio-analysis stack. Its catalog and import manifest stay in the
playlist package's `output/` directory. Unreviewed embedded tags retain their
provenance and warnings; missing mood/energy/genre evidence stays missing.
The pool contains 120 tracks. Its metadata catalog contains embedded BPM for
22 and recognized genre labels for 62, with no imported mood/energy/vocal
annotations. Some raw mood/energy-related fields exist but need review before
mapping into usable evidence.

From this project directory, open the form using the real-pool configuration:

```bash
cd packages/prompt-to-playlist
uv sync
uv run prompt-playlist ui --config playlist.toml
```

The package's `Open Playlist.command` launcher opens the same form.
`playlist.toml` selects OpenAI and the local catalog; the model is the editable
snapshot `gpt-5.4-mini-2026-03-17`. Its credential is the named project variable
`AUTODJ_OPENAI_API_DEV_KEY`, loaded from the environment or a literal assignment
in the explicitly configured `~/.zshrc` fallback. The shell file is never
executed, and no key value is stored in this repository. Only the request,
vocabulary, and query contract leave the computer. See the package README for
catalog refresh, configuration precedence, and offline demo commands.

The desktop always uses OpenAI. It selects explicit `--config`, then a
current-directory `playlist.toml`, then the editable package checkout’s profile.
Generic CLI prompt requests also default to OpenAI; offline developer examples
now require `--provider rules`. D041 corrects the older offline window path
that rejected the user’s natural-language description. Try “house dj set
energetic”: the model requires house and prefers high energy. Eight pool tracks
have the exact house tag, but energy remains unknown and is shown as such.
The refreshed interface presents simple criteria and artist/BPM results, with
detailed evidence available on demand; it adds no UI dependencies.

E028 separates live API
smoke results from the real pool's catalog coverage; neither a successful
connection nor schema-valid output establishes semantic recommendation quality.
The original five live checks passed for English/Spanish genre requests,
track counts, BPM sorting, unknown negative evidence and unsupported mix
requests. E029 adds the exact user regression and reruns the original cases:
all six pass with translation policy v3. The initial count-interpretation
mistake and the later offline-window failure remain in the logs.

This separation allows the mixer and playlist selector to progress
independently and lets other projects supply different catalogs or model
providers. Automatic MixPlan creation remains a later integration.
Further playlist work is paused at the user's request. When resumed, its next
slice is reviewed real-track annotations and broader prompt evaluation,
independently of the engine's headroom work.

## Future cloud music-library phase

The product roadmap now includes a discovery-only cloud service hypothesis for
DJs first and personal music collectors second. Candidate capabilities are a
secure listenable library, descriptor browsing/filtering/sorting, prompt-built
playlists, and downloadable deterministic AI DJ mixes. A dedicated streaming-
style app may be considered later, but is not part of the initial phase.

The first research revision is now available in the
[cloud discovery package](docs/cloud-library/README.md) (D043 / E030), including
a six-provider storage comparison, product/architecture/contracts reports,
security and rights review packet, formula cost workbook and agent registers
for gates, decisions, rejected paths, failures and future steers. Start with
[current status](docs/cloud-library/STATUS.md). The recommendation is continue
discovery; no full cloud build. Real customer/provider/audio experiments and
legal clearance remain unperformed. The full ordered backlog in
[`PLAN.md`](PLAN.md) then covers demand validation, upload/sync, cloud
architecture and development workflow, playback formats, descriptor analysis,
AI/execution boundaries, security/privacy/rights, unit economics, reliability,
and explicit build/no-build gates. This is not authorization to implement
hosting, accounts, uploads, remote analysis/rendering or automatic MixPlans.

## V1 scope

V1 uses 10 house tracks expected around 120–130 BPM:

`test_folder_10_house_tracks`

The source files are read-only.

### Step 1 — Audio intelligence

Produce structured track objects containing:

- Tempo candidate.
- Key/mode candidate and DJ notation.
- Loudness, loudness range, and true peak.
- Beats and downbeats.
- Sections and loop/transition candidates.
- Stream facts, versions, confidence, disagreements, and warnings.

### Step 2 — DJ tools

Provide deterministic tools for:

- Harmonic and tempo compatibility.
- Progressive tempo-story ordering.
- Pitch-preserving time stretch.
- Gain/volume envelopes.
- EQ and bass handoff.
- Beat-aligned loops.
- Crossfades and rendering.

Stem separation is deferred.

### Step 3 — Full pipeline

A provider-neutral language-model planner receives track summaries, the exact
available-tool catalog, duration/story constraints, and valid-plan examples.
It returns a declarative `MixPlan`. Deterministic code validates and renders
that plan.

## Accuracy policy

Stream facts and validated loudness can be authoritative. Tempo, key,
beats/downbeats, sections, and stems are fallible estimates.

V1 may use estimates for planning, but stores them as `benchmark_estimate`.
Unknown is preferable to invented certainty.

## Document map

- [`AGENTS.md`](AGENTS.md) — **agent takeover brief** (status, hard stops,
  next slice). Read this first if you are a new agent.
- [`PLAN.md`](PLAN.md) — product north star and V1 mapping.
- [`V1_ENGINE_PLAN.md`](V1_ENGINE_PLAN.md) — canonical implementation plan.
- [`docs/SCHEMAS.md`](docs/SCHEMAS.md) — JSON contracts and authority classes.
- [`docs/CORPUS.md`](docs/CORPUS.md) — authorized corpus manifest and policy.
- [`DECISION_LOG.md`](DECISION_LOG.md) — append-only decisions/supersessions.
- [`EXPERIMENT_LOG.md`](EXPERIMENT_LOG.md) — append-only inspections, results,
  failures, and learnings.
- [`docs/CHANGELOG.md`](docs/CHANGELOG.md) — plan/document revision history.
- [`packages/prompt-to-playlist/README.md`](packages/prompt-to-playlist/README.md)
  — independent playlist package setup, usage, contracts, and tests.
- [`AUDIO_ANALYSIS_TOOLING_REPORT.md`](AUDIO_ANALYSIS_TOOLING_REPORT.md) —
  sourced tooling and evidence registry (frozen research; not live status).

## Documentation operating rule

Before major work, consult `AGENTS.md`, then the plan, schemas, corpus policy,
decision log, experiment log, and relevant tooling evidence.

After work, update `AGENTS.md` and record in the durable logs:

- What changed.
- Why it changed.
- What was tested.
- What failed.
- What was learned.
- What was discarded and why.
- What remains unknown.
- The next approved action.

Do not erase mistakes; supersede them with dated evidence.

## Build history and next checkpoint

Completed for Step 1 scaffolding:

1. Audited the existing `uv` scaffold (E006).
2. Pinned Essentia `2.1b6.dev1389` after the latest wheel failed (E007).
3. Implemented Step 1 schemas, analyzer, CLI, and unit tests (E008).
4. Ran the authorized 10-track corpus (E019–E021). Artifact:
   `output/step1-collection.json`.
5. Started Step 2A scoring (D032, E022):

```bash
uv run dj-score output/step1-collection.json
uv run dj-score output/step1-collection.json --summary "01 My Paradise - Edit.mp3"
```

6. Started Step 2B clip renders (D034, E023). Tests use generated tones, not
   the 10 house MP3s:

```bash
uv run dj-render --help
```

7. Added the manual MixPlan validator and `render_set` vertical slice
   (D036 / E024). The user rendered and heard its checked-in v1 plan.
8. Diagnosed the listening result and added exact detected-downbeat overlap
   timing, `house_eq_v1`, a revised plan, and a click-overlay command
   (D037 / E025). The v2 plan validates to 609.100 seconds with two 29.090 s
   transitions. The user rendered it and accepted the timing/alignment as the
   project's first successful listening checkpoint (D038 / E026):

```bash
uv run dj-render set \
  --analysis output/step1-collection.json \
  --plan examples/mvp-three-track-plan-v2.json \
  --out output/mvp-three-track-set-v2.wav
```

To check the stored downbeats independently, create one centered 30-second
click-overlay WAV per planned track:

```bash
uv run dj-render downbeat-clicks \
  --analysis output/step1-collection.json \
  --plan examples/mvp-three-track-plan-v2.json \
  --out-dir output/downbeat-clicks
```

The primary diagnostic clips were also reported good. Preserve the accepted
transition behavior. The next small product-quality gap is deterministic
final-bus headroom/limiting because the successful render measures +1.04 dBTP;
then test the same baseline on a larger manual set. All-In-One host/model
refinements are backlog (D031). Automatic MixPlan generation remains deferred.
The independent playlist package has its own next checkpoint in
[`AGENTS.md`](AGENTS.md) and package documentation.
