# DJ Engine Decision Log

This is an append-only record. Do not delete superseded decisions; add a new
entry that references and replaces the old one.

## 2026-08-31 — D001 — Divide v1 into three steps

**Status:** Accepted

**Decision:** Build the engine as:

1. Audio intelligence.
2. DJ compatibility, planning, and manipulation tools.
3. Language-model planning plus deterministic execution/rendering.

**Why:** It separates uncertain analysis from audio processing and from LLM
reasoning. Each layer can be tested independently.

## 2026-08-31 — D002 — Restrict the first corpus

**Status:** Accepted, blocked on files

**Decision:** The first end-to-end analysis target is ten house tracks around
120–130 BPM in `test_folder_10_house_tracks`.

**Why:** A narrow genre and tempo range reduces early ambiguity and supports
simple progressive-tempo storytelling.

**Current fact:** The directory exists but was empty when inspected. The
populated 120-track folder will not be substituted silently.

## 2026-08-31 — D003 — Preserve strict authority labels

**Status:** Accepted

**Decision:** Tempo, key, beats/downbeats, and sections are stored as
`benchmark_estimate` in v1. Stream facts and validated loudness can be stored as
standards-based measurements.

**Why:** The engine needs estimates to mix, but the research does not support
calling them nearly-perfect facts. This resolves the apparent conflict between
the tooling report and the v1 product requirements.

## 2026-08-31 — D004 — Select Step 1 analyzers

**Status:** Accepted for compatibility testing

**Decision:**

- FFmpeg/ffprobe for decode, technical facts, health, and EBU R128 loudness.
- pyloudnorm as an independent loudness validator.
- All-In-One MLX for the primary combined tempo, beats, downbeats, and sections
  estimate on Apple Silicon.
- Beat This as an independent beat/downbeat challenger.
- Essentia `KeyExtractor` using a high-resolution HPCP and EDM-oriented profile
  for key/mode/strength.
- librosa for deterministic support features and diagnostics.

**Why:** This is the best available combination from the research for the
specific Apple Silicon, house-music prototype.

**Caveat:** Successful installation does not promote model estimates to facts.

## 2026-08-31 — D005 — Exclude identity enrichment

**Status:** Accepted

**Decision:** Chromaprint, AcoustID, MusicBrainz, Discogs, and related identity
or catalog tools are not included in the v1 analysis path.

**Why:** They do not improve the requested locally calculated mixing features.
Chromaprint is an identity fingerprint, not a transcript or music-feature
extractor.

## 2026-08-31 — D006 — Use Camelot-compatible harmonic matching

**Status:** Accepted for Step 2

**Decision:** Store standard key names as canonical and derive Camelot and Open
Key notation. Default safe matches follow rekordbox Traffic Light Related 2:

- Same key.
- Relative major/minor.
- One position clockwise/counter-clockwise on the same ring.

**Why:** This matches widespread DJ practice and AlphaTheta's documented
related-key behavior while keeping the internal representation vendor-neutral.

**References:**

- https://support.alphatheta.com/en-us/articles/8113187558553
- https://mixedinkey.com/workflows/how-to-use-the-camelot-wheel/

## 2026-08-31 — D007 — Keep LLM output declarative

**Status:** Accepted for Step 3

**Decision:** The LLM may return only a structured `MixPlan` using the
registered Step 2 tool catalog. It may not emit or execute arbitrary code.

**Why:** Audio bounds, gain, EQ, looping, time stretch, and duration need
deterministic validation before execution.

## 2026-08-31 — D008 — Defer stems

**Status:** Accepted

**Decision:** No stem separation in v1.

**Why:** It increases compute, storage, licensing, and artifact risk without
being necessary for the first EQ/loop/crossfade engine.

**Revisit when:** Full-band transitions work and a specific stem-assisted
transition has a measurable benefit.

## 2026-08-31 — D009 — Do not modify source MP3s

**Status:** Accepted

**Decision:** Analysis is read-only; rendered audio uses temporary PCM and a
new output file.

**Why:** This preserves reproducibility, existing DJ metadata, and user files.

## 2026-08-31 — D010 — Use a provider-neutral planner boundary

**Status:** Accepted

**Decision:** Do not choose an LLM provider during Step 1. Define JSON schemas
and a planner interface first.

**Why:** Tool execution, validation, and rendering must be portable across
models and usable without an LLM for testing.

## 2026-08-31 — D011 — Documentation precedes build approval

**Status:** Accepted

**Decision:** Complete and reconcile the plan, schemas, corpus policy, decision
log, experiment log, changelog, README, and tooling references before any new
environment mutation, installation, audio analysis, or source implementation.

**Why:** The user requested a reviewable architecture checkpoint before
authorizing the build. This prevents package choices and code from outrunning
the product contract.

## 2026-08-31 — D012 — Ten-track corpus is ready

**Status:** Accepted; supersedes only the blocked state in D002

**Decision:** `test_folder_10_house_tracks` remains the authorized V1 corpus and
is now ready for Step 1 after build approval.

**Evidence:** Direct inspection confirmed exactly 10 MP3 files on 2026-08-31.
The manifest is recorded in `docs/CORPUS.md`.

**Why:** The earlier empty-folder blocker is no longer true. The 120-track
folder remains an unauthorized silent substitute.

## 2026-08-31 — D013 — Audit the existing uv scaffold

**Status:** Accepted

**Decision:** Do not recreate the project environment after approval. First
audit the existing `pyproject.toml`, `uv.lock`, `.python-version`, `.venv`, and
stub package, then make only evidence-backed compatibility changes.

**Why:** The scaffold already exists. Recreating it could erase useful state,
hide dependency conflicts, or repeat work.

**Known gap:** Essentia is selected as the first key candidate but is not
declared in the current project dependencies. FFmpeg is a system dependency.
Rubber Band is a Step 2 candidate only.

## 2026-08-31 — D014 — Standardize authority vocabulary

**Status:** Accepted

**Decision:** Use only these authority values:

- `encoded_fact`
- `standardized_measurement`
- `deterministic_measurement`
- `benchmark_estimate`
- `user_verified`
- `llm_proposal`
- `executed_action`

**Why:** Existing documents used `benchmark_prediction`, `model_estimate`, and
`benchmark_only` for the same concept. One vocabulary prevents code, schema,
and planner drift.

## 2026-08-31 — D015 — Separate compatibility scoring tools

**Status:** Accepted for Step 2 design

**Decision:** Implement separate deterministic
`score_harmonic_match` and `score_tempo_match` tools. Combine their results
with phrase, loudness, confidence, and story constraints in
`score_transition`.

**Why:** Key compatibility and BPM manipulation are different constraints.
Separating them makes rules testable, explainable, and independently usable by
the planner.

## 2026-08-31 — D016 — Derive loops from downbeats, not section labels alone

**Status:** Accepted for Step 1/2 design

**Decision:** Create 4-, 8-, 16-, and 32-bar loop candidates from downbeat
anchors. Prefer candidates contained inside a detected section and reject or
warn when rhythm engines disagree.

**Why:** A structural label such as chorus or verse does not guarantee exact
bar alignment or a click-free loop.

## 2026-08-31 — D017 — Expose the DJ tool catalog to the planner

**Status:** Accepted for Step 3 design

**Decision:** The planner receives a versioned `ToolDefinition` catalog and may
query it through `list_available_dj_tools`. Compatibility scoring remains
deterministic.

**Why:** The model must know exactly which tools, units, schemas, and limits are
available without inventing capabilities or executable code.

## 2026-08-31 — D018 — Adopt the durable document set

**Status:** Accepted

**Decision:** Maintain:

- `README.md`
- `PLAN.md`
- `V1_ENGINE_PLAN.md`
- `docs/SCHEMAS.md`
- `docs/CORPUS.md`
- `DECISION_LOG.md`
- `EXPERIMENT_LOG.md`
- `docs/CHANGELOG.md`
- `AUDIO_ANALYSIS_TOOLING_REPORT.md`

**Why:** Product direction, implementation contracts, corpus facts, decisions,
empirical results, document changes, and external evidence have different
lifecycles. Keeping each role explicit reduces repeated mistakes without
creating competing plans.

## 2026-09-03 — D019 — Pin Essentia 2.1b6.dev1389 for CPython 3.12

**Status:** Accepted

**Decision:** Use `essentia==2.1b6.dev1389` on the current Python 3.12.10
Apple Silicon environment. Do not install the latest PyPI release
(`2.1b6.dev1438`); it only ships a cp314 wheel.

**Why:** E007. The selected algorithm is still `KeyExtractor` with
`profileType="edma"` and `hpcpSize=36`. Only the distribution pin changed.

**License:** Essentia remains AGPLv3; v1 is a local prototype.

## 2026-09-03 — D020 — Accept local FFmpeg 8.0.1 as the v1 inspector

**Status:** Accepted

**Decision:** Capture and persist the runtime FFmpeg/ffprobe version. The
authorized local build is Homebrew 8.0.1, not the tooling report's 9.0.1.

**Why:** Stream facts must describe the inspector that actually ran.

## 2026-09-03 — D021 — Loudness validator tolerances

**Status:** Accepted for Step 1

**Decision:**

- Integrated loudness: ±0.1 LU vs pyloudnorm.
- Loudness range: ±0.5 LU vs pyloudnorm.
- True peak: FFmpeg `loudnorm` `input_tp` only; pyloudnorm has no true-peak
  counterpart.
- If the integrated check fails, do not label the field
  `standardized_measurement`. Store the FFmpeg value as
  `deterministic_measurement` with `status=warning`. Do not average the two
  readings.

**Why:** The plan required 0.1 LU for loudness. LRA implementations differ
more in practice, so the independent LRA check uses a looser documented
tolerance rather than inventing an average.

## 2026-09-03 — D022 — Beat This device and return-order heuristic

**Status:** Accepted for Step 1

**Decision:** Prefer `device="mps"` when `torch.backends.mps` is available;
fall back to CPU on init or inference failure. Keep `dbn=False`. Interpret
`File2Beats` output as `(beats, downbeats)` unless the first array is
materially shorter than the second, in which case treat it as swapped
(`File2File` naming) and record a warning.

**Why:** `Postprocessor` returns beats then downbeats, but `File2File`
unpacks the opposite names. The heuristic makes the bug visible instead of
silently trusting either convention.

## 2026-09-03 — D023 — Analysis output location

**Status:** Accepted

**Decision:** Write `CollectionAnalysis` JSON under the project `output/`
directory, never inside `test_folder_10_house_tracks`. Temporary PCM and
all-in-one work directories live beside the output under `.dj-engine-work/`
and are deleted after the run unless `--keep-work` is set.

**Why:** Source immutability and corpus policy. All-in-one defaults would
otherwise write `demix/` / `spec/` relative to CWD.

## 2026-09-03 — D024 — Decode-once compromise for ML wrappers

**Status:** Accepted for Step 1

**Decision:** Decode 44.1 kHz stereo PCM once for loudness validation and
Essentia key. All-In-One MLX and Beat This still load the original MP3
through their own wrappers.

**Why:** Those packages own their preprocessing. Re-feeding PCM would fork
their pipelines. Document the double-decode; do not pretend one canonical
PCM fed every engine.

## 2026-09-03 — D025 — Declare demucs-mlx convert extras


**Status:** Accepted for Step 1

**Decision:** Add `demucs-mlx[convert]` to project dependencies so All-In-One
MLX can convert HTDemucs weights to MLX on first run.

**Why:** E010. The MLX port raises instead of demixing when the convert extra
is missing. This does not change authority: tempo/beats/sections remain
`benchmark_estimate`.

## 2026-09-03 — D026 — Run Beat This on CPU while All-In-One uses MLX

**Status:** Accepted for Step 1; supersedes the D022 MPS preference

**Decision:** Default Beat This to `device="cpu"` in the Step 1 pipeline.
Keep the D022 return-order heuristic and `dbn=False`.

**Why:** E011. Loading Beat This on MPS and then running All-In-One MLX in
the same process stalled after HTDemucs conversion, and the combined CLI
process disappeared without writing a new JSON. Isolated All-In-One on MLX
completed in ~70 s (E012). Sharing Metal between PyTorch MPS and MLX is not
reliable enough for v1.

## 2026-09-03 — D027 — Isolate each track in a subprocess and write incrementally

**Status:** Accepted for Step 1

**Decision:** Run each track in a fresh Python subprocess. Write the
collection JSON after every track. Support `--resume` by SHA-256.

**Why:** E015. A long-lived process analyzing the 10-track corpus was killed
with exit 137 during track 3 (`03 Fantazia.mp3`) after two successful
All-In-One runs, with a leaked multiprocessing semaphore warning. Incremental
JSON plus process isolation prevents losing completed tracks and should
release MLX memory between files.

## 2026-09-03 — D028 — Hard RAM caps for 16 GB Mac

**Status:** Accepted for Step 1

**Decision:**

- One track worker at a time.
- Kill the worker if its process-tree RSS exceeds 4096 MB.
- Do not start a worker unless about 2048 MB looks reclaimable; kill it if
  reclaimable RAM falls below ~768 MB.
- Pause and delete temp work after every track.
- Retry tracks whose JSON exists but All-In-One failed.
- Keep Beat This on CPU; disable All-In-One `mlx_in_memory` and ensemble
  parallelism for lower peak RAM.
- Prefer failing one track over freezing the laptop.

**Why:** E016. The host has 16 GB RAM. Cursor and other apps already use a
large share. Disk is no longer the blocker (~17 GB free); RAM is.

## 2026-09-03 — D029 — Staged one-track workers and live RAM telemetry

**Status:** Accepted for Step 1; supersedes D027's single worker per full track

**Decision:**

- Analyze at most one new track per CLI invocation by default (`--max-tracks 1`).
- Split each track into three short-lived subprocesses: ingest (ffprobe,
  loudness, key) → All-In-One MLX → Beat This CPU.
- Kill the stage process, delete its temp files, and wait for reclaimable
  RAM to recover before starting the next stage.
- Print live `rss` / `reclaimable` / `swap` / `wired` lines on stderr every
  few seconds so a Cursor terminal run is observable.
- If All-In-One is killed or cannot start, keep ingest (and Beat This if it
  still fits) and write the partial track JSON instead of dropping the file.
- `--max-tracks 0` remains available but is not the Cursor workflow.

**Why:** One process that loaded HTDemucs/MLX and Beat This together was the
RAM killer (E016, E017). The user needs to run remaining files from Cursor
without freezing the session. Metal allocations still bypass RSS; the
reclaimable-RAM kill from D028 still applies to the All-In-One stage.

## 2026-09-04 — D030 — Raise All-In-One RSS cap; reuse ingest and Beat This

**Status:** Accepted for Step 1; updates the 4096 MB RSS number from D028

**Decision:**

- Default `--max-worker-rss-mb` is 7168 MB. The reclaimable-RAM kill floor
  (~768 MB) stays. Ingest and Beat This keep their smaller stage caps.
- On `--retry-failed`, reuse a track's existing loudness/key and Beat This
  grid. Only All-In-One runs again.

**Why:** E020. With ~10 GB reclaimable, HTDemucs demix survived. Spectrogram
extraction then grew process-tree RSS to 4806–4982 MB and hit the old
4096 MB cap. Life Is Trippy had completed at 3538 MB because it is a
shorter file. Spectrograms scale with duration; the longer remaining
tracks need a higher CPU RSS ceiling, not a lower reclaimable floor.
Re-running ingest and Beat This on every All-In-One retry wastes RAM
before the demix even starts.

## 2026-09-04 — D031 — All-In-One RAM shortcomings; defer model/host changes

**Status:** Accepted; refinement backlog, not an immediate code change

**Decision:** Keep the current Step 1 All-In-One MLX path (`harmonix-all` +
internal HTDemucs demix) as the corpus producer. Record the following as
later refinement options, not v1 blockers:

1. **Lighter config of the current stack.** `harmonix-all` is an 8-fold
   ensemble (`harmonix-fold0` … `harmonix-fold7`). A single fold is the
   first config experiment. It may shrink spectrogram/analyze RSS (~4.7 GB
   on long tracks). It is unlikely to remove the HTDemucs demix spike
   (~9–12 GB wired Metal), because Harmonix still expects a 4-stem
   spectrogram.
2. **Internal changes to this package.** Inspect whether demix can be
   skipped, replaced with a smaller Demucs, streamed, or forced off-Metal.
   That is a fork/config experiment with a new accuracy comparison, not a
   silent swap.
3. **Different model.** Beat This already supplies an independent beat
   grid. A future decision may replace All-In-One for sections/BPM if a
   lighter local model is good enough on this house corpus.
4. **Amazon VM / larger host.** An EC2 (or similar) instance with 32–64 GB
   RAM, or a GPU box, can run the current pipeline as-is so the 16 GB Mac
   is not the analysis host. Source MP3s stay read-only; copy in, copy JSON
   out. This does not promote estimates to facts.

**Why:** E016–E021. The 16 GB Mac can finish ten tracks only with staged
workers, a reclaimable kill floor, and a 7168 MB RSS cap. The bottleneck
is All-In-One's internal demix plus ensemble/spectrogram RAM, not ingest
or Beat This. Switching models or hosts is authorized as future work, not
as a change to the completed 10-track JSON.

## 2026-09-04 — D032 — Start Step 2 with scoring tools only

**Status:** Superseded in part by D034 (clip renders now exist; listening
experiment still pending)

**Decision:** Begin Step 2 with 2A/2C deterministic tools:
`score_harmonic_match`, `score_tempo_match`, `score_transition`,
`propose_tempo_wave_order`, and `list_available_dj_tools`. Do not implement
gain/EQ/stretch/render (2B) until a later approval that includes a
listening/measurement experiment.

**Why:** The user asked to continue after Step 1. Scoring does not modify
audio, uses already-recorded estimates, and is testable without FFmpeg
renders. Rendering still has open dB/crossover/stretch-engine decisions.

## 2026-09-04 — D033 — Initial v1 scoring numbers

**Status:** Accepted as an initial rule set, pending listening tests

**Decision:**

- Harmonic default: rekordbox Traffic Light Related 2 (D006).
- Stretch: prefer ≤2%, allow ≤4%, reject above 4%, never auto-reinterpret
  half/double tempo.
- Transition weights: harmonic 0.45, tempo 0.35, phrase 0.12, loudness 0.08.
- Outside-policy harmonic matches cap the combined score at 0.15.
- `tempo_wave` climb length is 6 of 10 tracks, scaled by the same 6/10
  ratio for other collection sizes.

**Why:** The plan required explicit numbers to implement 2A. These are
planning heuristics over `benchmark_estimate` inputs, not mix laws.

## 2026-09-04 — D034 — Initial clip-render bounds and FFmpeg atempo

**Status:** Accepted as an initial rule set, pending listening tests

**Decision:** Implement Step 2B clip tools now. Do not wait for a full
listening experiment before writing bounded FFmpeg operations. Record the
first numbers as initial, not mix laws:

- Sample rate 44100 Hz stereo, 32-bit float PCM intermediates.
- Gain −24 dB to +6 dB.
- EQ bands 120 / 800 / 4000 Hz (`eq-crossover-v1`), gain −18 dB to +3 dB.
- Low-cut 80–300 Hz, default 180 Hz.
- Loop max 8 repetitions, 12 ms edge crossfade (`loop-edge-v1`).
- Mix crossfade 0.05–32 s.
- Stretch still prefer ≤2%, allow ≤4%, reject above. Engine: FFmpeg
  `atempo`, because this Homebrew 8.0.1 build has no `rubberband` filter.
- Outputs must not be written under the source music folder. `load_track`
  re-hashes the source after the copy.
- `set_volume_envelope` and MixPlan `render_set` stay planned.

**Why:** The user asked to continue building immediately after 2A. Lookups
and clip renders are testable on generated tones without touching the 10
house MP3s. Rubber Band remains a later quality comparison (same open
question as D032).

## 2026-09-04 — D035 — AGENTS.md is the live takeover brief

**Status:** Accepted

**Decision:** `AGENTS.md` in this project is the operating brief for a new
agent. Workspace `AGENTS.md` and `.cursor/rules/dj-engine.mdc` point to it.
Chat history is not required to continue. Update `AGENTS.md` whenever
status, hard stops, or the next slice change.

**Why:** The user is switching agents and asked that the complete context
be visible in the repo.

## 2026-09-04 — D036 — Ship a manual MixPlan vertical slice before Step 3

**Status:** Accepted and implemented

**Decision:** Implement the first end-to-end set command around a strict,
hand-authored `MixPlan` before adding automatic or LLM planning.

- One downbeat-indexed segment is required per ordered track.
- Optional constant gain and target BPM remain inside D034 bounds.
- Every consecutive pair requires one 4/8/16-bar triangular crossfade.
- Adjacent effective BPMs must match within 0.2 BPM.
- The validator resolves IDs through `CollectionAnalysis`, confines sources
  to its input folder, and verifies hashes against Step 1.
- The renderer publishes a 44.1 kHz stereo 32-bit-float WAV atomically, then
  emits a `RenderManifest` with executed actions, duration, hash, LUFS, LRA,
  true peak, and source-preservation results.
- Direct render CLI commands protect source parents by default; validation
  checks occur before output directories are created.

The first real-corpus plan is checked in at
`examples/mvp-three-track-plan.json`. It uses the 133 BPM 2A → 2A → 2B
cluster without time stretch. E024 validated it but did not render it.

**Why:** A small audible vertical slice is the shortest path from tested
components to a product. Manual planning isolates renderer and transition
quality before an LLM adds another source of uncertainty.

**Deferred:** Volume/EQ envelopes, cue optimization, mastered delivery
formats, automatic subset/order planning, and Step 3.

## 2026-09-05 — D037 — Anchor overlaps to detected grids and use a house bass handoff

**Status:** Accepted and implemented; listening validation pending

**Decision:** Supersede the D036 example's 8-bar triangular-only transition
for the next listening plan.

- Use 16 bars for this 133 BPM house example: the detected grids resolve each
  overlap to 29.090 seconds.
- Derive overlap seconds from the outgoing segment's actual detected downbeat
  span after any stretch, not from the rounded selected BPM value.
- Start the incoming segment at its selected detected downbeat and reject a
  transition when adjacent grids accumulate more than 70 ms drift across the
  overlap.
- Add `house_eq_v1`: split at 180 Hz, keep incoming bass out until the
  midpoint, exchange bass ownership across at most three seconds, bring the
  incoming high band in over the first half, and take the outgoing high band
  out over the second half.
- Keep `linear_crossfade` for comparison; do not implement automatic style
  selection or Step 3.
- Provide centered 30-second click-overlay diagnostics from a named stored
  grid so a person can verify downbeats without rerunning either analyzer.

**Evidence:** The user's v1 listening notes rejected both 14.44-second
volume-only transitions and reported phase mismatch. E025 found the old
renderer began overlap 0.114 and 0.104 seconds before the relevant outgoing
detected downbeat because it used rounded 133 BPM. All-In-One and Beat This
agree strongly on the three tracks (beat/downbeat F1 approximately
0.995–0.999; no phase warnings), so re-analysis is not the first fix.

**Plan:** `examples/mvp-three-track-plan-v2.json` preserves the original
transition start positions by extending the first two segment endpoints eight
bars. It validates to 609.100 seconds with 0.010 and 0.000 seconds of
adjacent-grid drift. It has not been rendered.

**Deferred:** User verification of the clicks, v2 listening, envelope tuning,
generic `set_volume_envelope`, mastered delivery, and automatic planning.

## 2026-09-05 — D038 — Accept v2 timing and alignment as the first house baseline

**Status:** Accepted from user listening evidence

**Decision:** Preserve the D037 `house_eq_v1` transition behavior and 16-bar
exact-grid duration as the first working baseline for the two heard pairs in
`mvp-three-track-133-v2`.

- Both transitions are 29.090 seconds.
- The user says the second mix is much better and explicitly accepts the
  transition time and downbeat alignment for this first version.
- The primary click-overlay diagnostic was also reported great.
- Record this as localized `user_verified` experiment evidence. Do not change
  the immutable collection JSON's rhythm-grid authority or generalize the
  result to unheard regions/tracks.
- Do not tune the accepted transition merely because more parameters are
  available. Exercise it again before expanding transition complexity.

**Measurement caveat:** The accepted v2 WAV is 609.100 seconds at −13.81 LUFS,
3.1 LU LRA, and +1.04 dBTP. Its source hashes are unchanged. Transition
behavior is accepted, but the positive true peak means delivery headroom is
not complete.

**Next recommended slice:** Add a deterministic, measured final-bus
headroom/limiter policy, then use the accepted transition on a larger manual
set. Automatic planning and Step 3 remain deferred.

## 2026-09-07 — D039 — Develop reusable prompt-to-playlist selection in parallel

**Status:** Accepted and implemented; offline and mocked-provider validation
recorded in E027

**Authorization:** The user requested a local field for describing a desired
set, LLM integration with deterministic tools, and a simple reusable module
that can progress independently of audio analysis and mixing.

**Decision:** House an independently installable Python distribution in
`packages/prompt-to-playlist/` within the DJ repository. It has its own
runtime, lockfile, tests, schemas, and documentation and can be reused without
installing the DJ audio stack. Neither runtime imports the other.

- Translate a request through a replaceable provider into a strict,
  provenance-bearing query proposal. Model interpretation is not deterministic
  retrieval and is never a new measurement of a track.
- Let code own the versioned vocabulary, descriptor normalization, validation,
  hard filtering, explicit ranking, and ordered lookup of existing track IDs.
- Keep the first query contract to tags, BPM bounds, result count, exclusions,
  and relevance/BPM ordering. Surface unsupported constraints and stop the
  request from silently executing only the supported fragments.
- Provide a native desktop prompt form and CLI, a limited offline rules translator,
  and an optional structured-output LLM adapter. The provider receives only
  the user request and vocabulary, without catalog metadata or audio tools.
- Put source-specific parsing in catalog adapters. The DJ adapter reads only
  the existing `CollectionAnalysis` JSON and preserves IDs and estimate
  provenance. The core's only runtime dependency is Pydantic v2.
- Treat missing semantic tags honestly. Do not derive mood/energy from
  loudness or BPM, or per-track genre from a folder description. Use synthetic
  labeled fixtures until explicit reviewed real-track evidence is available.

**Scope supersession:** This authorizes LLM-assisted candidate selection and
replaces the earlier blanket hold on LLM work for this separate module. D036
and D038's automatic MixPlan/render-planning hold remains. The accepted
`house_eq_v1` behavior and final-bus headroom next slice remain unchanged.

**Why:** Translation, catalog evidence, retrieval policy, user interface, and
audio execution change for different reasons. Keeping their boundaries small
supports pivots and reuse in a future Spotify or other catalog application
without introducing a general agent framework or coupling the heavy audio
runtime to every playlist request.

**Deferred:** Automatic MixPlan generation, DJ-safe sequencing/duration
planning, real-corpus semantic annotation, embeddings, Spotify integration,
playlist publishing, and live-provider quality/cost evaluation.

## 2026-09-07 — D040 — Use the larger local playlist pool with project OpenAI configuration

**Status:** Accepted and implemented; verification recorded in E028

**Authorization:** The user requested use of the approximately 120-track pool
and their project OpenAI API key, stored under `AUTODJ_OPENAI_API_DEV_KEY` in
`~/.zshrc`, for natural-language playlist requests. No additional approval is
needed for the bounded catalog import and live translation setup they asked
for.

**Decision:** Add an explicit local-folder catalog adapter and a small project
configuration/launcher around the existing independent package.

- Import `test_tracks_folder_mp3` through read-only hashing and sequential,
  timeout-bounded ffprobe container/embedded-tag inspection. Write catalog
  and source-preservation/coverage manifest JSON outside all music folders.
  The expected work is a lightweight metadata pass with no decoded PCM or
  acoustic-analysis model; E028 records actual count, runtime, and failures.
- Preserve hash-derived identities and source provenance. Encoded genre
  labels remain unreviewed metadata with warnings; embedded BPM remains a
  `benchmark_estimate` with a warning. Do not claim missing/partial tag axes
  are complete or infer semantic tags from names, BPM, or model knowledge.
- Keep ordinary playlist requests JSON-only. Local catalogs, file paths,
  track names, and audio stay local. The OpenAI Responses API receives only
  the user request, vocabulary, and query contract, returning an
  `llm_proposal` which code validates before deterministic retrieval.
- Use explicit `--config playlist.toml` for this project's catalog, OpenAI
  provider, model, and credential-variable settings. The reusable no-config
  interface retains offline rules mode. An `Open Playlist.command` launcher
  selects the project configuration for the desktop form.
- Pin the configured translation model to `gpt-5.4-mini-2026-03-17`, verified
  against [OpenAI's official model documentation](https://developers.openai.com/api/docs/models/gpt-5.4-mini)
  during setup. This choice is
  editable project configuration, not a core retrieval or mixer dependency.
- Resolve the project key from the named environment variable or an explicit
  literal assignment in the configured `~/.zshrc` fallback. Never execute or
  source the shell file to load it. Never log the secret, put it in CLI
  arguments, copy it into the repository, or fall back to an unrelated key.
- Validate the real connection with bounded live translation examples, then
  report request-interpretation evidence separately from the local catalog's
  semantic coverage. Small smoke checks do not establish broad model quality.

**Scope supersession:** Supersedes the previous blanket ban on using the
larger pool only for this metadata catalog purpose. It does not authorize
All-In-One/Beat This/Essentia analysis, corpus rendering, automatic MixPlan
generation, or publishing playlists. The ten-track engine corpus, immutable
source rule, accepted D038 listening baseline, and RAM hard stops remain.

**Why:** The requested real pool and a configured model make the existing form
usable for actual requests while preserving the package's replaceable
translation and catalog boundaries. A metadata catalog can expose its limits
without blocking progress on the independent mixer or hiding absent labels.

**Deferred:** Reviewed semantic enrichment and broader prompt-quality
evaluation; all existing automatic mixing, acoustic batch analysis, external
catalog integration, and playlist-publication deferrals remain.

## 2026-09-07 — D041 — Natural-language playlist defaults and light interface

**Status:** Accepted; implementation/verification recorded in E029 and package
P007/P-E003.

**Trigger:** The user typed “house dj set energetic” and received offline
semicolon-grammar instructions. Process inspection found the old offline
window still running alongside the configured OpenAI window. The user asks
for ordinary language to become rules through the LLM and a modern, light UI.

**Decision:** Require OpenAI for the desktop and reject rules mode. Resolve
its profile from explicit `--config`, current-directory `playlist.toml`, then
the editable package checkout. Generic CLI `prompt` defaults to OpenAI;
`--provider rules` remains an explicit offline developer option. No model
failure falls back to grammar. Keep library translators explicitly supplied.
This supersedes D040’s no-config offline UI/CLI default; profile discovery
is restricted to the desktop. Credential resolution and API scope stay as
recorded in D040.

Version the translator policy to `playlist-query-v3`: a direct single-genre
request makes the genre required; ordinary energy/mood descriptions remain
preferences unless explicitly mandatory. “DJ set” by itself is playlist
context; explicit rendering, transition and mixed-duration requests remain
unsupported. The LLM proposes intent; deterministic code searches sourced
metadata and never invents evidence. The catalog’s eight exact house tags do
not establish energy, and house subgenres are not automatically expanded.

Modernize the standard-library Tk form with light styling, plain-language
criteria, artist/BPM results, always-visible missing preference evidence and
optional technical details. Keep its Pydantic-only runtime dependency and
independence from audio analysis/rendering. No schema or mixer behavior changes.

**Remaining work:** Broader interpretation evaluation and reviewed semantic
annotations. No larger-pool analysis, rendering, source writes, automatic
MixPlan generation or publication is authorized by this interface correction.

## 2026-09-08 — D042 — Register a cloud music-library product hypothesis

**Status:** Accepted as a future discovery phase; implementation not authorized

**Trigger:** The user proposed cloud storage as both a potential product and a
practical host for exposing the DJ engine and playlist selector without asking
customers to install platform-specific software or run terminal commands. The
proposed primary audience is DJs, with personal digital-music collectors as a
secondary audience. The user also paused further playlist development while
the local DJ tool remains active.

**Decision:** Add an ordered cloud-product discovery phase to `PLAN.md`.

- Candidate capabilities are a secure listenable owned-music library,
  descriptor browsing/filtering/sorting, natural-language playlist generation,
  and prompt-driven downloadable DJ mixes executed through deterministic,
  reproducible transitions and a validated plan.
- Treat limited ownership of digital music libraries and the burden of the
  first large upload as core demand/onboarding risks. A later sync or
  streaming-style application may improve the experience, but is not part of
  the initial phase.
- The first to-do is a current storage-service comparison across cost,
  integration effort and retrieval/playback performance, including realistic
  storage, request, transfer and CDN scenarios.
- Before a full build, define and test the target user and MVP, upload and
  incremental-sync behavior, media delivery, descriptor processing and user
  corrections, cloud architecture/development workflow, AI-versus-
  deterministic execution boundaries, tenancy/security/privacy/rights,
  reliability, operations, unit economics and explicit build/no-build gates.
- Reuse the existing playlist contracts and MixPlan/RenderManifest boundaries
  where they remain suitable; cloud hosting does not erase their provenance,
  validation or source-preservation rules.

**Scope boundary:** This is roadmap registration, not authorization to select a
vendor, create cloud resources, upload audio, build accounts, run remote
analysis/render jobs, integrate automatic MixPlan generation or ship a hosted
product. The local engine's headroom/manual-set milestone remains active.
Further prompt-to-playlist work is paused with its current implementation and
evidence preserved until the user resumes it.

## 2026-09-08 — D043 — Activate cloud deep research and maintained planning records

**Status:** Accepted for research and local documentation. Implementation is
not authorized. This activates D042's discovery work without removing its holds.

**Trigger:** The user requests full deep research on the cloud-library phase,
professional reports optimized for agent understanding/building, and durable
records for updates, steers, failures, unviable paths and their reasons.

**Decision:** Publish the maintained discovery package at
[docs/cloud-library](docs/cloud-library/README.md). It contains a current
storage comparison first, product/market/onboarding research, architecture and
development workflow, proposed data/API/job contracts, security/privacy/rights
and software/model licensing review, unit economics, operations, build gates
and a conditional delivery backlog. Use stable source/record IDs, current
structured registers and append-only events for future agent updates.

**Research recommendation:** Continue discovery; no full cloud build now.
B2/R2 are a proposed storage shortlist, not a selected vendor. Prefer a small
crate onboarding experiment and selective analysis before mandatory full-library
upload/processing. Separate private-library release gates from automatic-mix
gates. These are recommendations, not accepted implementation decisions.

**Evidence and limits:** Revision 1.0 records 45 primary sources, a checked
formula scenario workbook, proposed experiments and explicit unknowns. No
customer interviews, provider benchmarks, legal clearance or cloud audio tests
were performed. Exact dynamic/regional price gaps are retained. E030 records
the actual research/artifact verification and limitations.

**Scope:** Research and local planning artifacts are authorized. Accounts,
uploads, cloud resources, remote audio analysis/rendering, automatic MixPlans,
customer/vendor outreach, spending and hosted implementation need later
explicit scope decisions. The playlist package stays paused; the local engine's
headroom/larger-manual-set work remains active. No recurring automation or
commit is created. Future documentation maintenance follows the package's
MAINTENANCE.md and preserves prior logs by supersession.
# 2026-09-09 — D044 — Establish the private GitHub recovery baseline

**Status:** Accepted and implemented; verification recorded in E031

**Authorization:** The user requested a full GitHub repository of the current
project under `manuelalvarezml`, asked that the latest summaries' reasons for
version control be retained, and authorized the initial commit and push.

**Decision:** Use the existing `dj-collection-set-builder` Git root as the
repository boundary and publish it privately as
`manuelalvarezml/resonant-ai-dj`. Track the engine, the independent
prompt-to-playlist package, cloud discovery, lockfiles, compact analysis and
catalog evidence, manifests, and append-only logs in one history. Keep source
MP3s, rendered WAVs, environments, caches, credentials, and disposable work
outside Git. Record excluded audio through hashes and manifests. Use `main` as
the recoverable line and annotated `checkpoint-YYYY-MM-DD` tags for accepted
whole-repository states; component packages, schemas, translator policies, and
research revisions retain their independent versions.

**Why:** D038/E026 contains the first accepted listening behavior, E021 was
expensive to reproduce on the available machine, D039 depends on coordinated
track identities while preserving package independence, and the cloud
maintenance protocol requires decisions, failures, and superseded conclusions
to remain auditable. A compact Git checkpoint preserves those assets without
publishing rights-sensitive audio or bloating normal repository history.

**Consequences:** `VERSIONING.md` is the policy and recovery guide. Material
changes update their relevant decision, experiment, and changelog records in
the same commit. Private visibility does not authorize committing secrets or
redistributing audio. This decision changes recordkeeping only; all engine,
playlist, source-audio, cloud, and automatic-planning boundaries remain.
