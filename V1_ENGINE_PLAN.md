# DJ Engine v1 Implementation Plan

## 2026-10-06 — Individual accounts and spectrum motion

[Account release](packages/web-player/docs/ACCOUNTS_RELEASE.md) replaces shared hosted state with email/username/password accounts, private playlists/PlaylistIQ results/listening counters, owner-only bounded analytics and a full-spectrum motion override. Google sign-in/linking is implemented but activation and real-provider acceptance await a Google web client ID. Owner authorized deployment, a test user, live-history reset and Git push. Current rollout receipt and limitations are maintained in the linked checkpoint; audio, saved analysis and planner policy are preserved.

## Status

- Registered: 2026-08-31
- Plan version: 0.13 — repository recovery/versioning baseline added; V1 boundary unchanged
- Engine milestone: final-bus headroom, then a larger manual-set test
- Parallel milestone: reusable playlist slice (D039/E027), larger metadata
  pool and OpenAI configuration (D040/E028), natural-language defaults and
  desktop correction (D041/E029); further playlist work is paused by the user
- Future product milestone: cloud discovery research/planning activated
  (D043); [research package](docs/cloud-library/README.md) revision 1.0 exists.
  Empirical gates remain unpassed; no cloud/V1 implementation expansion
- Build status: Step 1 corpus complete (E021). Step 2A scoring implemented
  (D032, E022). Step 2B clip tools implemented (D034, E023). Manual
  MixPlan validation / `render_set` implemented (D036, E024). The user heard
  the v1 plan; exact-grid timing, `house_eq_v1`, click diagnostics, and v2
  followed (D037, E025). The user rendered v2 and accepted its duration and
  downbeat alignment (D038, E026). Step 3 not started. All-In-One RAM
  refinements deferred (D031).
- Target corpus: `test_folder_10_house_tracks`
- Corpus status: ready; 10 MP3 files confirmed 2026-08-31 and re-hashed
  2026-09-03 before analysis
- Platform: Apple Silicon macOS
- Environment manager: `uv`; Python 3.12.10 in `.venv`
- FFmpeg: local 8.0.1 Homebrew GPL build (`atempo`; no `rubberband` filter)
- Essentia: `2.1b6.dev1389` (latest PyPI wheel is cp314-only; see D019 / E007)
- Output: `output/` CollectionAnalysis JSON and render WAV outside the
  source folder
- Authorization boundary: Step 1, 2A, 2B clips, manual MixPlan execution, and
  bounded click diagnostics approved. V2 listening is complete.
  Automatic MixPlan generation remains out of scope. Independent LLM-assisted
  candidate selection is authorized by D039. D040 authorizes read-only
  hashing/metadata import of the larger local pool and OpenAI translation
- Agent takeover: `AGENTS.md` is the live operating brief for a new session

## Product goal

Given a folder of local music and a natural-language mix request, choose tracks,
order them, plan transitions, execute a constrained set of DJ operations, and
render one approximately requested-duration audio mix.

Version 1 targets ten house tracks expected to fall around 120–130 BPM. This
restricted corpus is deliberate: it reduces genre and tempo ambiguity while the
pipeline, schemas, and validation discipline are established.

## Non-negotiable principles

1. Preserve source audio. Analysis and rendering never modify input MP3s.
2. Separate measurements, model estimates, LLM proposals, and executed actions.
3. Pin tool and model versions in every output.
4. Allow unknown/rejected values; never fabricate a complete record.
5. The LLM may plan with supplied facts and tools, but cannot execute arbitrary
   shell commands or invent tool capabilities.
6. Validate every plan with deterministic code before rendering.
7. Keep an append-only record of decisions, failures, and learned constraints.
8. Re-read `PLAN.md`, this document, `DECISION_LOG.md`,
   `EXPERIMENT_LOG.md`, and `AUDIO_ANALYSIS_TOOLING_REPORT.md` before major
   tool or architecture changes.

## Reconciliation with the research report

The research report uses a strict “nearly perfect authoritative feature” gate.
Under that gate:

- Stream facts and loudness can be accepted with standards/conformance checks.
- Tempo, key, downbeats, and sections are fallible model estimates.

The v1 mixer cannot be prototyped without those fallible estimates. Therefore,
v1 does **not** redefine them as truth. It stores them under
`benchmark_estimate`, retains confidence and alternate outputs, and exposes
uncertainty to the planner. A later manually annotated corpus decides whether
any estimator can be promoted.

### Canonical authority vocabulary

Use these values consistently across plans, schemas, code, and logs:

- `encoded_fact`: intrinsic bitstream/container result from a pinned inspector.
- `standardized_measurement`: standards-defined calculation that passed its
  validator and tolerance.
- `deterministic_measurement`: reproducible numerical transform with pinned PCM
  and parameters.
- `benchmark_estimate`: fallible model/algorithm output available to the v1
  planner with confidence and warnings.
- `user_verified`: explicit human correction or confirmation.
- `llm_proposal`: unexecuted planner suggestion.
- `executed_action`: deterministic operation actually applied during rendering.

The tooling report's `model_estimate`, `benchmark_prediction`, and
`benchmark_only` language maps to the canonical v1 value
`benchmark_estimate`. `authoritative` is not a stored authority value; it is a
lane containing accepted encoded facts, validated standardized measurements,
approved deterministic measurements, and user-verified corrections.

## Step 1 — Audio intelligence

### Required outputs

For each track:

- Stable track ID derived from the source-file SHA-256.
- Path, filename, byte size, source hash, analysis timestamp.
- Decoder and analyzer versions.
- Codec, sample rate, channels, bit rate, duration, and decode-health status.
- Tempo estimate in BPM.
- Beat and downbeat timestamps.
- Tempo-consistency and fixed-grid residual diagnostics.
- Global key and mode estimate.
- Key strength/confidence.
- Standard key name, Camelot code, and Open Key code.
- Integrated loudness in LUFS.
- Loudness range in LU.
- true peak in dBTP when available.
- Section boundaries and labels.
- Warnings, rejected values, and missing analyzer results.

### Selected tools

| Need | Primary v1 candidate | Independent check | Stored authority |
|---|---|---|---|
| Tempo | All-In-One MLX 1.0.6 | Median intervals from Beat This 1.1.0 beats | `benchmark_estimate` |
| Key / mode | Essentia `KeyExtractor` with `edma` profile | Human review initially; no reviewed open detector is near-perfect | `benchmark_estimate` |
| Loudness / LRA | FFmpeg EBU R128 | pyloudnorm 0.2.0 | `standardized_measurement` only after tolerance passes |
| Beats / downbeats | All-In-One MLX | Beat This | `benchmark_estimate` |
| Sections | All-In-One MLX functional boundaries | Downbeat-aligned novelty/phrase diagnostics | `benchmark_estimate` |
| Stream facts / decode | ffprobe and FFmpeg | MediaInfo only if a disagreement needs diagnosis | `encoded_fact` |

“Primary” means first candidate to test, not presumed ground truth. The
tooling report remains the evidence source; the authorized corpus run decides
whether these candidates are useful enough for v1 planning.

#### Stream truth and loudness: FFmpeg/ffprobe

Why:

- Strongest operational decoder and stream inspector from the research.
- EBU R128/ITU-R BS.1770-compatible loudness filters.
- Local, scriptable, deterministic with pinned build and arguments.

Use:

- `ffprobe` JSON for intrinsic stream facts.
- Full or analysis decode to detect damaged MP3s.
- `loudnorm=print_format=json` for input integrated loudness, LRA, threshold,
  and true peak.

Local baseline detected at registration: FFmpeg 8.0.1, Homebrew GPL build.
The code must capture the actual local version rather than hard-coding the
research report's newest release.

#### Tempo, beats, downbeats, and sections: All-In-One MLX

Why:

- Best one-pass Apple Silicon fit for the exact requested output set.
- Version 1.0.6 supports BPM, beat/downbeat events, section boundaries and
  labels, machine-readable output, and local MLX inference.
- Its output is especially suitable for the later planner because events and
  sections share one timeline.

Limit:

- Accuracy is inherited from a dataset-specific upstream model.
- The MLX port has no independent collection-level accuracy proof.
- Output remains `benchmark_estimate`.
- **RAM (E016–E021, D031):** on a 16 GB Mac the blocker is internal
  HTDemucs demix (~9–12 GB wired Metal, nearly invisible in process RSS)
  plus spectrogram/analyze RSS that scales with duration (~3.5–4.7 GB).
  `harmonix-all` is an 8-fold ensemble; single folds exist but are not
  swapped in yet. Later refinement options: single-fold config, skip or
  replace demix inside the package, a different section/BPM model, or run
  the current pipeline on an Amazon VM / 32–64 GB host. Do not silently
  change the completed 10-track JSON.

#### Independent rhythm challenger: Beat This

Why:

- Strongest modern public beat/downbeat evidence reviewed.
- Independent model family exposes disagreements that one analyzer cannot.
- Version 1.1 supports non-CUDA accelerators.

Use:

- Run as a validator/challenger where installation and runtime allow.
- Derive a robust BPM candidate from median beat intervals.
- Store both event sets and consensus diagnostics.

Limit:

- No sections or key.
- Published downbeat quality is far below perfect on several datasets.

#### Key: Essentia `KeyExtractor`

Why:

- Best practical local open implementation selected for this prototype.
- Returns key, major/minor scale, and strength.
- Supports tuning correction, high-resolution HPCP, and an `edma` profile
  intended for electronic dance music.

Why not the apparent alternatives:

- KeyMyna has promising author-reported 2026 results but no clear software
  license, no maintained product package, and no deployment-quality Apple
  workflow.
- Mixed In Key is useful as a black-box human benchmark but exposes no public
  headless analysis API or confidence contract.
- LibKeyFinder is older, GPL, and materially below near-perfect in the reviewed
  benchmark.

Essentia is therefore the best *implementable first benchmark*, not a claim
that it is the most accurate possible closed or research-only detector.

Proposed settings:

- Canonical 44.1 kHz mono analysis PCM.
- `profileType="edma"`.
- `hpcpSize=36`.
- Tuning-aware/high-resolution configuration.

Limit:

- It is a global-key estimate, not ground truth.
- Modulating or harmonically ambiguous tracks can produce misleading output.
- Essentia is AGPLv3 or commercially licensed; v1 is a local prototype.
- Latest PyPI Essentia (`2.1b6.dev1438`) has no cp312 wheel. V1 is pinned to
  `2.1b6.dev1389` (D019, E007).

#### Loudness validator: pyloudnorm

Why:

- Independent Python BS.1770 implementation.
- Published conformance evidence.
- Useful for catching FFmpeg invocation or parsing mistakes.

Use:

- Cross-check integrated loudness and LRA from canonical PCM.
- Record disagreement; do not average unexplained mismatches.

#### Section and phrase strategy

All-In-One section labels are evidence, not loop instructions. V1 will derive
loop and transition candidates separately:

1. Use detected downbeats as bar anchors.
2. Generate 4-, 8-, 16-, and 32-bar windows.
3. Prefer windows fully contained inside a structural section.
4. Penalize windows crossing a high-novelty boundary.
5. Store the original section source/confidence and the derived phrase rule.
6. Reject loop candidates when downbeat engines disagree beyond tolerance.

This closes a major ambiguity: “section” describes musical structure, while a
DJ loop requires an exact, rhythm-aligned interval.

### Canonical analysis flow

1. Discover supported files without modifying them.
2. SHA-256 the input.
3. Collect ffprobe JSON.
4. Perform a decoder-health check.
5. Decode once to temporary 44.1 kHz PCM.
6. Run loudness analysis and validator.
7. Run Essentia key estimation.
8. Run All-In-One MLX.
9. Run Beat This when available.
10. Normalize outputs into the canonical schema.
11. Calculate rhythm disagreement and grid diagnostics.
12. Write one JSON document for the collection and optional one-per-track JSON.
13. Remove temporary PCM.

### Step 1 acceptance criteria

- Clean `uv sync` on Apple Silicon.
- CLI accepts an input folder and output path.
- Empty folders fail with a clear message and non-zero exit status.
- Unsupported files are skipped with structured warnings.
- Input MP3s remain byte-identical.
- Every result records tool versions and authority class.
- Loudness fields parse successfully and include units.
- Tempo/key/downbeat/section outputs are visibly labeled as estimates.
- Partial analyzer failure produces a partial record, not collection loss.
- Tests cover schema validation, key notation, rhythm diagnostics, and empty
  directory behavior.
- The requested ten-track run is recorded in `EXPERIMENT_LOG.md`.

## Step 2 — DJ planning and manipulation tools

Step 2A scoring and Step 2B clip-level FFmpeg tools are implemented. The first
manual-plan `render_set` is implemented. Automatic plan generation and
time-varying volume/EQ automation are still later.

### 2A. Harmonic and tempo compatibility

Build three deterministic tools:

- `score_harmonic_match(from_key, to_key, policy)`
- `score_tempo_match(from_bpm, to_bpm, stretch_policy, story_target)`
- `score_transition(from_track, to_track, context)` combines the two scores
  with phrase, loudness, confidence, and story constraints.

Keeping harmonic and tempo matching separate makes each rule testable and lets
the planner explain whether a transition was chosen for key, tempo, story, or a
trade-off.

#### Harmonic matching

Use standard key names internally and derive Camelot/Open Key display codes.
The initial safe compatibility set follows AlphaTheta rekordbox Traffic Light
and standard Camelot guidance:

- Same key.
- Same Camelot number, opposite A/B letter: relative major/minor.
- Same letter, one Camelot number clockwise or counter-clockwise.

Rekordbox's official example for 2A:

- Same: `2A`.
- Related 1: `2A`, `2B`.
- Related 2: add `1A`, `3A`.
- Related 3: add `1B`, `3B`.

Version 1 should use Related 2 as the default safe set. Related 3 and creative
energy moves such as `+2` are opt-in and receive lower compatibility scores.
Key confidence gates the score; unknown/weak keys cannot be treated as matches.

Initial `score_harmonic_match` result:

- Canonical source/destination key and mode.
- Derived Camelot and Open Key codes.
- Relationship: `same`, `relative`, `adjacent_same_mode`, `related_3`,
  `incompatible`, or `unknown`.
- Normalized score from 0 to 1.
- Rule ID and reference.
- Confidence-adjusted score.
- Rejection/warning reason.

Primary references:

- AlphaTheta Traffic Light documentation:
  https://support.alphatheta.com/en-us/articles/8113187558553
- Mixed In Key Camelot workflow:
  https://mixedinkey.com/workflows/how-to-use-the-camelot-wheel/

#### Tempo matching

Inputs:

- Source and destination BPM candidates.
- Confidence/consensus.
- Allowed pitch-independent time-stretch range.
- Story arc target at this position.

Outputs:

- Required stretch percentage for each track.
- Candidate shared transition BPM.
- Feasible/rejected status.
- Penalty for large stretch.
- Half/double-tempo ambiguity diagnostics.
- Story-arc direction agreement: `up`, `down`, `flat`, or `conflict`.

Initial rule for 120–130 BPM house:

- Prefer adjacent tracks requiring at most 2% stretch.
- Allow up to 4% in v1 only when harmonic and phrase matches are strong.
- Reject larger moves unless a non-overlap transition is explicitly planned.
- Never silently reinterpret half/double tempo.

### 2B. Audio manipulation tool contract

All operations use typed arguments, explicit units, bounded ranges, and
deterministic validation.

- `load_track(track_id, start_time_s, end_time_s)`
- `time_stretch(track_id, target_bpm, preserve_pitch=true)`
- `set_gain(track_id, gain_db, start_s, end_s, curve)`
- `set_volume_envelope(track_id, points_db, interpolation)`
- `eq_band(track_id, band, gain_db, start_s, end_s, curve)`
- `low_cut(track_id, cutoff_hz, start_s, end_s, curve)`
- `loop(track_id, start_downbeat, bars, repetitions, crossfade_ms)`
- `crossfade(out_track, in_track, start_s, duration_s, curve)`
- `render_segment(operations)`
- `render_set(plan, output_path)`

Initial EQ behavior for a basic bass handoff:

1. Start the incoming track below full mix level.
2. Reduce its low band during the overlap.
3. Exchange low-frequency ownership near a phrase/downbeat boundary.
4. Restore the incoming low band while reducing or exiting the outgoing track.
5. Preserve mix-bus headroom; never boost both low bands simultaneously by
   default.

Initial bounded policy (D034), pending listening tests:

- Time stretch: prefer at most 2%; permit at most 4%; reject above 4%.
  Engine: FFmpeg `atempo` (this 8.0.1 build has no `rubberband` filter).
- Gain: −24 dB to +6 dB. Positive gain is allowed but warned.
- EQ: named bands `low` / `mid` / `high` at 120 / 800 / 4000 Hz
  (`eq-crossover-v1`); gain −18 dB to +3 dB.
- Low-cut: 80–300 Hz, default 180 Hz.
- Loops: planner still prefers 4/8/16/32-bar downbeat windows; the clip
  tool repeats a prepared PCM clip up to 8 times with a 12 ms edge
  crossfade (`loop-edge-v1`).
- Mix crossfade: 0.05–32 s via `acrossfade`.
- House transition: `house-eq-v1` splits at 180 Hz, keeps incoming bass out
  until the midpoint, hands low-frequency ownership over across at most three
  seconds, and uses broader opposing high-band envelopes.
- Intermediates: 32-bit float PCM outside the source music folder; source
  SHA-256 is re-checked after `load_track`.

Implemented tools: `load_track`, `set_gain`, `eq_band`, `low_cut`,
`loop`, `crossfade`, `house_transition`, `time_stretch`, `render_segment`,
the manual MixPlan `render_set`, and the downbeat-click diagnostic command.
Still planned: a generic `set_volume_envelope` and automatic plan generation.

The D036 executor accepts one downbeat-indexed segment per ordered track,
optional bounded constant gain and target BPM, and one consecutive
4/8/16-bar transition per adjacency. D037 derives transition seconds from the
outgoing detected downbeat span, checks incoming-grid drift against the 70 ms
event window, and supports `linear_crossfade` or `house_eq_v1`. It verifies source hashes
against Step 1 before rendering and again before publishing an atomic
32-bit-float WAV. Its `RenderManifest` records executed actions, final
duration/hash, integrated LUFS, LRA, true peak, and source preservation.

Rubber Band Library remains a later quality comparison. Do not treat D034
numbers as mix laws until a listening/measurement experiment is recorded.

### 2C. Basic story arc

Represent story as constraints, not free prose.

Initial `tempo_wave` template for ten tracks:

- Tracks 1–6: monotonically non-decreasing effective BPM.
- Tracks 7–10: monotonically non-increasing effective BPM.
- Preserve harmonic compatibility where possible.
- Penalize repeated artists/tracks and large stretch.
- Prefer section/downbeat-aligned transition windows.

The arc is a planner objective, not a requirement to alter every track.

## Step 3 — Full folder-to-mix pipeline

Status: deferred. D039's independent playlist module covers candidate
selection only; it does not implement this automatic mix-planning step.

### Input

- Folder path.
- Requested mix length in minutes.
- Natural-language brief such as “high-energy house” or “slow latincore.”
- Optional story template and hard constraints.

### Planner context

The LLM receives:

- Compact analyzed track objects.
- Explicit confidence/authority fields.
- Requested duration and style.
- The exact registered tool catalog and JSON argument schemas.
- Planning rules and hard safety limits.
- Examples of valid plans.

The registered catalog is itself an explicit planner tool:

- `list_available_dj_tools()` returns names, purposes, schemas, units, hard
  limits, and examples.
- `get_track_summary(track_id)` returns compact accepted/estimated features.
- `get_transition_windows(track_id)` returns detailed section/downbeat windows
  only when needed.
- `score_harmonic_match(...)`, `score_tempo_match(...)`, and
  `score_transition(...)` let deterministic code—not the language model—apply
  compatibility rules.

Do not send raw beat arrays when a compact summary and selected transition
windows will suffice. Detailed timing remains available through deterministic
lookup tools.

V1 prompt limitation: because genre, mood, and energy classifiers are excluded,
phrases such as “high energy” need an explicit interpretation before they can
control tempo arc, transition density, loop usage, or duration. They cannot
reliably select “high-energy tracks”
unless the user supplies trusted labels or later approves a subjective feature
layer. The planner must disclose this limitation rather than pretend the
missing attributes were analyzed.

### Planner output

The LLM returns a structured `MixPlan`, not executable code:

- Ordered track IDs.
- Target effective BPM per track/transition.
- Entry and exit section/downbeat references.
- Loop requests.
- Gain/EQ envelopes.
- Crossfade duration and curve.
- Estimated total length.
- Explanation and uncertainty.

### Deterministic validation

Before execution:

- Every track ID must exist.
- Every operation must be a registered Step 2 tool.
- All times must be in track bounds.
- Loops must align to known beats/downbeats unless explicitly overridden.
- Gain/EQ/time-stretch values must stay within policy limits.
- No two incompatible operations may target the same interval.
- Estimated duration must be within the configured tolerance.

Invalid plans are rejected or repaired by deterministic code before any render.

### Duration policy

The requested duration is approximate. Initial tolerance:

- Target within ±10% or one track transition, whichever is smaller.
- Prefer clean phrase-aligned endings over exact seconds.
- Report requested, planned, and rendered duration separately.

## Canonical object boundaries

- `TrackAnalysis`: immutable source facts and analyzer outputs.
- `FeatureValue`: value, units, source, version, authority, confidence, status.
- `Section`: start/end, label, source, confidence.
- `RhythmGrid`: BPM, beat/downbeat arrays, source, residuals, confidence.
- `ToolDefinition`: name, purpose, JSON argument schema, hard limits.
- `MixBrief`: parsed user intent and constraints.
- `MixPlan`: ordered tracks, typed downbeat-indexed segments, and typed
  transitions in the manual v1 slice; later planner operations must remain
  equally declarative.
- `RenderManifest`: exact executed operations, versions, hashes, and output.

Field-level contracts and examples live in `docs/SCHEMAS.md`. Code must not
silently introduce alternate field names.

## Independent playlist selection (D039 / D040 / D041)

The implementation lives in
[`packages/prompt-to-playlist`](packages/prompt-to-playlist/README.md), with
its own Python distribution, lockfile, environment, tests, and docs. The DJ
engine does not import it; the package does not import the DJ engine or
acoustic-analysis stack. Its explicit local-folder import may hash sources
and inspect container metadata with ffprobe (D040); normal playlist requests
read catalog JSON. Keeping it in the same repository supports coordinated versioning
without coupling installation to the audio/ML stack.

Its boundaries are deliberately small:

1. A native desktop form or CLI accepts the user's description.
2. A translator proposes a typed query using a supplied versioned vocabulary.
3. Deterministic normalization and validation reject unknown descriptors,
   contradictions, malformed output, and unsupported constraints.
4. Deterministic catalog search applies hard constraints, ranks eligible
   tracks with an explicit versioned rule, and returns evidence and IDs.
5. A lookup tool resolves only existing IDs in the requested order.

The translation adapter may be an LLM or a limited offline rules grammar;
neither is the retrieval algorithm. The OpenAI provider receives only the
request, descriptor vocabulary, and query contract, while catalogs stay local. No agent loop,
audio tools, embedding service, database, or provider SDK is required by the
core. Pydantic v2 is its only runtime dependency.

D040 configures this project's real-pool workflow through explicit
`--config playlist.toml`, selecting `gpt-5.4-mini-2026-03-17` and the named
credential `AUTODJ_OPENAI_API_DEV_KEY`. The configured fallback reads a literal
assignment in `~/.zshrc` without executing it or copying the secret into the
repository. The package’s desktop launcher applies the project configuration.
D041 supersedes the old offline defaults: the desktop always uses OpenAI and
selects explicit config, current-directory profile, then editable-checkout
profile. Generic CLI prompt defaults to OpenAI; rules parsing uses an explicit
`--provider rules` or rules profile. Library callers choose their translator.

The refreshed standard-library Tk interface keeps ordinary descriptions in the
main flow and technical evidence available on demand. Missing preference
evidence stays visible. Translator `playlist-query-v3` interprets a direct
single genre as required and ordinary energy/mood as preferred; “DJ set” alone
is context, while an explicit render/transition request remains unsupported.
The exact user regression and validation outcomes are recorded in E029.

The DJ catalog adapter reads `CollectionAnalysis` JSON, checks its identity
and version, and retains BPM authority/status/source. The real ten-track
artifact has no semantic tags. Synthetic labeled fixtures exercise descriptor
retrieval; future manual annotations or a reviewed tag source must carry
provenance. Neither BPM nor loudness is a substitute for subjective labels.

The local-folder adapter separately imports the user-authorized larger pool
through source hashes and sequential ffprobe metadata probes. It preserves
embedded-tag claims and warnings, does not assert complete semantic coverage,
and emits a catalog plus import manifest outside music folders. The larger
pool is not a new Step 1 analysis corpus. E028 records the actual count,
coverage, source-preservation checks, runtime, and live translation results.

Package schemas and tool definitions are canonical in package documentation;
`docs/SCHEMAS.md` records the bridge boundary without duplicating them.
Results are candidate lists, not compatible transition plans, duration-aware
mixes, or published streaming-service playlists. Automatic MixPlan work
remains separately deferred. E027 records independent installation, tests,
distribution builds, CLI and native Tkinter form smoke checks, and metadata-only
interoperability with the real ten-track collection. E028 adds bounded live
provider smoke checks against the local pool. Broad interpretation quality
and reviewed semantic tag coverage remain separate open questions.

## Documents and update cadence

After every implementation or experiment:

1. Update `AGENTS.md` (takeover brief) and status in this file.
2. Append decisions to `DECISION_LOG.md`.
3. Append commands/results/failures to `EXPERIMENT_LOG.md`.
4. Reconcile affected claims in `PLAN.md`.
5. Update `docs/CHANGELOG.md` for documentation changes.
6. Update `AUDIO_ANALYSIS_TOOLING_REPORT.md` only when evidence or tool
   lifecycle changes.

Never erase a failed path from the logs. Supersede it with a dated decision.

## Known blockers and open questions

Still open:

- Key-estimation acceptance needs human verification.
- D034 set initial EQ/gain/loop/crossfade numbers. The v1 listening experiment
  rejected 8-bar volume-only transitions; the user accepted D037's 16-bar
  exact-grid `house_eq_v1` behavior for the two v2 transitions. That is a
  bounded first baseline, not a corpus-wide mix law.
- Stretch currently uses FFmpeg `atempo` (D034). Rubber Band remains a
  quality comparison, not the v1 engine yet.
- The manual MixPlan / PCM WAV `render_set` is implemented. Volume
  envelopes, mastered delivery formats, and automatic plan generation remain
  undecided / unimplemented.
- The accepted corpus-level BPM/key/downbeat/section error thresholds for
  practical v1 planning must be documented without relabeling estimates as
  authoritative.
- The MixPlan provider/model remains undecided until Step 3. The independent
  playlist package has a replaceable translation interface and an optional
  provider adapter; this does not select a vendor for the mix planner.
- `test_tracks_folder_mp3` is authorized for a read-only playlist metadata
  catalog (D040). It remains outside the engine's acoustic-analysis/render
  scope and must not silently substitute for `test_folder_10_house_tracks`.
- All-In-One RAM refinements (single fold, internals, other model, Amazon
  VM) are backlog D031.

Resolved since the 2026-08-31 draft (kept here so the old blockers are not
re-opened by accident):

- Build authorization for Step 1, 2A, and 2B clip renders is no longer
  pending.
- `pyproject.toml` / `.venv` were audited (E006) and now run the selected
  stack, including Essentia `2.1b6.dev1389`.
- All-In-One MLX, Beat This, and Essentia coexist via staged subprocess
  workers (D029).
- Installed FFmpeg 8.0.1 was accepted as the v1 build (D020). The research
  registry still names 9.0.1 as the latest reviewed release; they remain
  separate facts.

## Reconciled inconsistencies

- **Original two phases vs. three V1 steps:** mapped explicitly in `PLAN.md`;
  V1 step names are canonical for implementation.
- **Genre/mood/energy vs. strict calculated features:** deferred from V1's
  authoritative lane. D039 allows supplied semantic evidence in a separate
  selection module; natural-language style is not a trusted track fact and
  missing corpus tags are not fabricated.
- **Empty corpus vs. ready corpus:** superseded by direct inspection confirming
  10 MP3 files; recorded in `EXPERIMENT_LOG.md`.
- **Create an environment vs. existing scaffold:** the scaffold already existed;
  the audit ran as E006, then Step 1–2B were implemented on it.
- **120-track report target vs. 10-track V1 target:** the report remains broad
  research; `docs/CORPUS.md` defines the 10-track folder as the only authorized
  V1 engine corpus. D040 separately authorizes the larger pool's read-only
  playlist metadata import without expanding the engine corpus.
- **Authority vocabulary drift:** canonical values are defined above and in
  `docs/SCHEMAS.md`.
- **Latest researched FFmpeg vs. installed FFmpeg:** remain separate facts;
  runtime outputs must record the actual executable/build used.

## Immediate next action

A new agent should read `AGENTS.md` first.

The manual MixPlan validator and `dj-render set` are implemented. The user
heard v1 and rejected its 14.44-second volume-only transitions. E025 fixed the
renderer's rounded-BPM phase offset and introduced the v2 plan. The user then
heard v2 and accepted its two 29.090-second `house_eq_v1` transitions and
downbeat alignment as a much better first version; the primary click
diagnostic was also good (D038/E026). Preserve that behavior. The next smallest
delivery gap is deterministic final-bus headroom/limiting because v2 measured
+1.04 dBTP, followed by a larger manual-set exercise. Do not batch-render the
corpus, start automatic MixPlan generation, change All-In-One, or substitute
the playlist pool into an engine run.

The independent prompt-to-playlist first slice is validated in E027, and
D040/E028 records larger-pool metadata import and explicit OpenAI setup.
D041/E029 corrects natural-language defaults and modernizes the lightweight
desktop while preserving source-evidence limits. Further playlist work is
paused; when resumed, add reviewed tag evidence and broaden real-description
evaluation before judging semantic retrieval quality on the real corpus.
Neither track must wait for the other; keep their experiments and acceptance
claims separate.

D042 adds a future cloud music-library product hypothesis to `PLAN.md`. It is
not a V1 engine milestone and does not authorize cloud implementation. Its
first discovery task was storage-provider cost/integration/retrieval research.
D043 activates research and local planning, with revision 1.0 maintained in
[docs/cloud-library](docs/cloud-library/README.md). The comparison and proposed
specifications do not pass customer, legal, security, cost or audio gates.
Read its takeover for next discovery work; implementation remains unauthorized.
