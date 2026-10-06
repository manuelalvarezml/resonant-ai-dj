# DJ Engine V1 Data Contracts

## 2026-10-06 — Individual accounts and spectrum motion

[Account release](../packages/web-player/docs/ACCOUNTS_RELEASE.md) replaces shared hosted state with email/username/password accounts, private playlists/PlaylistIQ results/listening counters, owner-only bounded analytics and a full-spectrum motion override. Google sign-in/linking is implemented but activation and real-provider acceptance await a Google web client ID. Owner authorized deployment, a test user, live-history reset and Git push. Current rollout receipt and limitations are maintained in the linked checkpoint; audio, saved analysis and planner policy are preserved.

## Status

- Schema family: `dj-engine`
- Draft version: `0.1.0`
- Updated: 2026-09-07
- State: Step 1 corpus JSON exists; Step 2A scoring, Step 2B clip tools,
  the manual MixPlan `render_set`, exact-grid transition timing,
  `house_eq_v1`, and downbeat-click diagnostics are implemented. The user
  accepted v2 transition duration/alignment as the first listening baseline.
  Step 3 and generic time-varying volume/EQ plan operations remain unimplemented
- Parallel contracts: independent `prompt-playlist` schema family (D039),
  implemented and independently tested in E027, with local-folder catalog
  import and OpenAI project configuration added in D040/E028; canonical reference:
  [`playlist schemas`](../packages/prompt-to-playlist/docs/SCHEMAS.md)
- Agent takeover: see `../AGENTS.md`

These contracts are provider-neutral and serialization-oriented. Pydantic
models in `src/dj_collection_set_builder/models.py` implement the JSON
shape. The markdown contract remains the source if code and docs diverge.

## Independent prompt-to-playlist boundary

Cloud discovery (D043) proposes separate host envelopes in
[cloud-library/CONTRACTS.md](cloud-library/CONTRACTS.md). They are design drafts,
not implemented schemas and do not change this schema family's version,
authority vocabulary or validation boundary.

`packages/prompt-to-playlist/` owns a separate `prompt-playlist` schema family,
version `0.1.0`, plus its own models, tool definitions, and validation. Refer
to the package README and linked schema documentation for the canonical
catalog, vocabulary, query, translation, result, and versioned
`prompt-playlist/run` contracts. The desktop form
and CLI use the same validated core and do not introduce alternate schemas.
Do not copy
those fields into `TrackAnalysis` or couple their release cycle to `dj-engine`.

The DJ adapter only reads this family's `CollectionAnalysis` JSON. It
preserves existing track identities and BPM evidence, including authority,
status, source, and confidence where present. It does not load source audio,
rerun analyzers, or relabel estimated values. File paths and rhythm arrays are
not needed by the playlist core.

E027 verified ten imported tracks, all retaining BPM authority
`benchmark_estimate` and status `warning`, with no fabricated semantic tags.
Public entry points revalidate existing model instances so later in-memory
mutations cannot bypass the catalog/vocabulary contract.

D040 adds an explicit local-folder adapter for the larger playlist pool. It
reads bytes for stable hashes and inspects ffprobe container/embedded-tag
metadata; it does not create `TrackAnalysis` or invoke acoustic models. The
catalog retains source provenance and warnings for unreviewed tag claims,
while a separate `prompt-playlist/folder-import` version `0.1.0` manifest
records source preservation and coverage. The existing catalog contract
remains at `0.1.0`. Embedded
BPM remains `benchmark_estimate`; an encoded genre value is evidence that a
tag was present, not a human-reviewed classification. Unmapped/absent labels
must not become positive tags or complete negative-filter coverage. Package
documentation owns these contracts and configuration validation.

The configured OpenAI model receives only the request, descriptor vocabulary,
and query contract. Its response retains `llm_proposal` authority. Model
selection and credential-variable names are application configuration, not
new fields in the engine's analysis or render contracts. E028 records live
smoke results separately from catalog-semantic coverage, using the package's
separate `prompt-playlist/live-check` version `0.1.0` report envelope.

D041 changes launch behavior and interpretation policy, not serialized schemas.
The desktop always uses OpenAI; explicit offline parsing remains a CLI/library
choice. `playlist-query-v3` requires a directly requested single genre, prefers
ordinary mood/energy descriptors, and treats “DJ set” alone as playlist context.
The modernized form displays criteria in ordinary language but exports the same
versioned run and full provenance. Missing energy annotations remain absent
in the catalog, not inferred from the request or BPM.

The imported catalog has no semantic tags unless an explicit evidence source
supplies them. The ten-track artifact contains no mood, genre, or energy
annotations. Request descriptors are query constraints, not facts newly
attributed to a track. Missing or rejected evidence must not satisfy a hard
constraint. The package uses the same exact authority vocabulary below.

Validated playlist results contain existing catalog IDs, matching evidence,
warnings, and deterministic ranking provenance. They are not `MixPlan`
objects and do not satisfy the renderer's validation contract. Any future
selection-to-MixPlan adapter is a separate integration; the renderer still
validates all original source hashes, timing references, and operation bounds.

## Design rules

1. Source MP3s are immutable.
2. Every derived value has provenance and authority.
3. Units are explicit.
4. Unknown/rejected values remain explicit; they are not zero or empty text.
5. Model estimates never silently become facts.
6. LLM output is declarative and validated before execution.
7. Tool versions, model IDs, parameters, and source hashes make results
   reproducible.
8. Schema versions change when a consumer-visible contract changes.

## Canonical authority values

| Value | Meaning | May planner use? | May be called authoritative? |
|---|---|---|---|
| `encoded_fact` | Intrinsic stream/container result from a pinned inspector | Yes | Yes, relative to inspected stream |
| `standardized_measurement` | Standards-defined measurement that passed validation | Yes | Yes |
| `deterministic_measurement` | Reproducible numerical transform with pinned PCM/parameters | Yes | Only for the numerical value, not subjective interpretation |
| `benchmark_estimate` | Fallible model or estimation algorithm output | Yes, with warnings/confidence | No |
| `user_verified` | Human-confirmed or corrected value | Yes | Yes, as a user decision |
| `llm_proposal` | Unexecuted planner suggestion | Only after validation | No |
| `executed_action` | Operation actually applied by deterministic renderer | N/A | Yes, as render history |

The tooling report terms `model_estimate`, `benchmark_prediction`, and
`benchmark_only` map to `benchmark_estimate`.

## Common status values

- `passed`
- `warning`
- `rejected`
- `unknown`
- `not_run`
- `failed`

## `FeatureValue`

Used for scalar or compact values.

```json
{
  "value": -10.8,
  "unit": "LUFS",
  "authority": "standardized_measurement",
  "status": "passed",
  "source_tool": "ffmpeg",
  "tool_version": "actual-runtime-version",
  "model_id": null,
  "confidence": null,
  "parameters": {},
  "validator": {
    "tool": "pyloudnorm",
    "version": "actual-runtime-version",
    "value": -10.8,
    "tolerance": 0.1,
    "difference": 0.0,
    "passed": true
  },
  "warnings": []
}
```

Rules:

- `value` is nullable.
- `confidence` is nullable and must identify its scale if present.
- `parameters` contains every behavior-changing analyzer option.
- A failed validator changes `status` to `warning` or `rejected`.
- Do not average unexplained validator disagreement.

## `TrackSource`

```json
{
  "track_id": "sha256:<hex>",
  "path": "test_folder_10_house_tracks/example.mp3",
  "filename": "example.mp3",
  "size_bytes": 12345678,
  "sha256_before": "<hex>",
  "sha256_after": "<hex>",
  "source_unchanged": true
}
```

`track_id` is content-derived for V1. A moved file with identical bytes retains
the same ID.

## `StreamFacts`

```json
{
  "authority": "encoded_fact",
  "status": "passed",
  "probe_tool": "ffprobe",
  "probe_version": "actual-runtime-version",
  "codec": "mp3",
  "sample_rate_hz": 44100,
  "channels": 2,
  "channel_layout": "stereo",
  "bit_rate_bps": 320000,
  "bit_rate_mode": "unknown",
  "duration_s": 382.41,
  "decode_health": "passed",
  "decoder_warnings": []
}
```

## `LoudnessAnalysis`

```json
{
  "integrated": {
    "value": -10.8,
    "unit": "LUFS",
    "authority": "standardized_measurement",
    "status": "passed"
  },
  "range": {
    "value": 6.2,
    "unit": "LU",
    "authority": "standardized_measurement",
    "status": "passed"
  },
  "true_peak": {
    "value": -0.4,
    "unit": "dBTP",
    "authority": "standardized_measurement",
    "status": "passed"
  },
  "primary_tool": {
    "name": "ffmpeg",
    "version": "actual-runtime-version",
    "filter": "chosen-versioned-filter-settings"
  },
  "validator": {
    "name": "pyloudnorm",
    "version": "actual-runtime-version",
    "integrated_difference_lu": 0.0,
    "lra_difference_lu": 0.0,
    "passed": true
  }
}
```

Do not label loudness as “energy.” Energy is subjective/model-relative.

## `TempoAnalysis`

```json
{
  "selected_candidate": {
    "value": 126.02,
    "unit": "BPM",
    "authority": "benchmark_estimate",
    "status": "warning",
    "source_tool": "all-in-one-mlx",
    "tool_version": "1.0.6",
    "confidence": null
  },
  "alternates": [
    {
      "value": 126.0,
      "unit": "BPM",
      "authority": "benchmark_estimate",
      "status": "passed",
      "source_tool": "beat-this-derived",
      "tool_version": "1.1.0",
      "confidence": null
    }
  ],
  "consensus": {
    "difference_bpm": 0.02,
    "half_double_ambiguity": false,
    "agrees_within_tolerance": true,
    "tolerance_bpm": 0.2
  },
  "grid_diagnostics": {
    "median_interval_s": 0.4761,
    "tempo_variability_bpm": 0.08,
    "fixed_grid_residual_ms_p50": null,
    "fixed_grid_residual_ms_p95": null,
    "end_drift_ms": null
  }
}
```

The selected candidate remains `benchmark_estimate` even when engines agree.

## `RhythmGrid`

Large event arrays may be stored in a referenced sidecar artifact.

```json
{
  "authority": "benchmark_estimate",
  "status": "warning",
  "source_tool": "all-in-one-mlx",
  "tool_version": "1.0.6",
  "tempo_bpm": 126.02,
  "meter_numerator": 4,
  "beats_s": [0.42, 0.90, 1.37],
  "downbeats_s": [0.42, 2.32],
  "beat_count": 802,
  "downbeat_count": 201,
  "challenger": {
    "source_tool": "beat-this",
    "tool_version": "1.1.0",
    "beat_match_f1": null,
    "downbeat_match_f1": null,
    "phase_warning": false
  },
  "warnings": []
}
```

For LLM context, provide counts and selected transition windows rather than
full event arrays. Deterministic tools retrieve details.

## `KeyAnalysis`

```json
{
  "authority": "benchmark_estimate",
  "status": "warning",
  "source_tool": "essentia-key-extractor",
  "tool_version": "actual-runtime-version",
  "model_profile": "edma",
  "tonic": "A",
  "mode": "minor",
  "standard_name": "A minor",
  "camelot": "8A",
  "open_key": "1m",
  "strength": 0.71,
  "alternates": [],
  "user_verified": false,
  "warnings": [
    "Global key is an estimate and may hide modulation."
  ]
}
```

Standard key name is canonical. Camelot and Open Key are derived display/index
fields.

## `Section`

```json
{
  "section_id": "section-04",
  "start_s": 96.2,
  "end_s": 160.1,
  "start_downbeat_index": 52,
  "end_downbeat_index": 86,
  "label": "chorus",
  "authority": "benchmark_estimate",
  "source_tool": "all-in-one-mlx",
  "tool_version": "1.0.6",
  "confidence": null,
  "warnings": []
}
```

Section labels are not automatically suitable loop regions.

## `LoopCandidate`

```json
{
  "loop_id": "loop-04-16",
  "track_id": "sha256:<hex>",
  "start_downbeat_index": 52,
  "start_s": 96.2,
  "bars": 16,
  "end_s": 126.68,
  "contained_in_section_id": "section-04",
  "crosses_novelty_boundary": false,
  "rhythm_sources_agree": true,
  "status": "passed",
  "derived_by": "downbeat-window-rule-v1"
}
```

Allowed V1 loop sizes: 4, 8, 16, or 32 bars.

## `TrackAnalysis`

```json
{
  "schema": "dj-engine/track-analysis",
  "schema_version": "0.1.0",
  "analysis_id": "uuid",
  "analyzed_at": "ISO-8601",
  "source": {},
  "stream": {},
  "loudness": {},
  "tempo": {},
  "rhythm_grids": [],
  "key": {},
  "sections": [],
  "loop_candidates": [],
  "warnings": [],
  "analyzer_failures": []
}
```

Each `{}` above is replaced by the corresponding defined object. Partial
analysis is valid when failures are recorded.

## `CollectionAnalysis`

```json
{
  "schema": "dj-engine/collection-analysis",
  "schema_version": "0.1.0",
  "collection_id": "uuid",
  "input_folder": "test_folder_10_house_tracks",
  "created_at": "ISO-8601",
  "platform": {
    "os": "macOS",
    "architecture": "arm64",
    "python": "actual-runtime-version",
    "ffmpeg": "actual-runtime-version"
  },
  "expected_audio_count": 10,
  "discovered_audio_count": 10,
  "tracks": [],
  "warnings": [],
  "failures": []
}
```

This is the Step 1 object intended for later deterministic planning and compact
LLM context generation.

## `ToolDefinition`

The LLM is informed of available capabilities through these records.

```json
{
  "name": "eq_band",
  "version": "1",
  "purpose": "Apply a bounded EQ change to one named band.",
  "arguments_schema": {
    "band": "low | mid | high",
    "gain_db": "number"
  },
  "hard_limits": {
    "gain_db_min": -18.0,
    "gain_db_max": 3.0,
    "low_hz": 120.0,
    "mid_hz": 800.0,
    "high_hz": 4000.0,
    "crossover_version": "eq-crossover-v1"
  },
  "availability": "implemented",
  "requires": []
}
```

D034 filled the previous `null` gain/EQ limits with initial numbers. The v1
listening result rejected 8-bar volume-only transitions. D036 implements the
first manual-plan `render_set`; D037 adds exact-grid overlap timing and
`house_eq_v1`. A generic `set_volume_envelope` stays `planned`.

Catalog:

- `list_available_dj_tools` — implemented
- `get_track_summary` — implemented
- `get_transition_windows` — implemented
- `score_harmonic_match` — implemented
- `score_tempo_match` — implemented
- `score_transition` — implemented
- `propose_tempo_wave_order` — implemented
- `load_track` — implemented
- `time_stretch` — implemented (`atempo`, max 4%)
- `set_gain` — implemented (−24 to +6 dB)
- `set_volume_envelope` — planned
- `eq_band` — implemented
- `low_cut` — implemented (80–300 Hz, default 180)
- `loop` — implemented (max 8 reps, 12 ms edge crossfade)
- `crossfade` — implemented (0.05–32 s)
- `house_transition` — implemented (`house-eq-v1`, 180 Hz midpoint bass handoff)
- `render_segment` — implemented (single-source op lists)
- `render_set` — implemented for strict manual plans (PCM WAV + manifest)

The CLI also exposes `dj-render downbeat-clicks`. It creates one centered
diagnostic excerpt per selected track using a named stored rhythm grid; it is
not a planner operation and does not promote estimates to facts.

## `TrackSummary`

Compact planner lookup. Do not include full beat arrays.

```json
{
  "track_id": "sha256:…",
  "filename": "example.mp3",
  "duration_s": 180.0,
  "bpm": 128.0,
  "bpm_authority": "benchmark_estimate",
  "standard_name": "A minor",
  "camelot": "8A",
  "key_strength": 0.7,
  "loudness_lufs": -10.0,
  "loudness_authority": "standardized_measurement",
  "section_count": 4,
  "preferred_loop_count": 2,
  "beat_count": 360,
  "downbeat_count": 90,
  "analyzer_failure_count": 0,
  "note": "Tempo, key, beats, and sections are benchmark_estimate values."
}
```

## `TransitionWindows`

Selected section list, preferred 8/16-bar loops that do not cross novelty,
and first/last downbeat anchors. Full `beats_s` arrays stay on
`TrackAnalysis`.

## `RenderArtifact`

```json
{
  "artifact_id": "clip",
  "path": "output/clip.wav",
  "duration_s": 8.0,
  "sha256": "…",
  "tool": "load_track",
  "warnings": []
}
```

## `MixBrief`

```json
{
  "schema": "dj-engine/mix-brief",
  "schema_version": "0.1.0",
  "request_text": "Create a high-energy house mix around 45 minutes.",
  "target_duration_minutes": 45,
  "style_terms": ["house", "high-energy"],
  "story_template": "tempo_wave",
  "hard_constraints": {
    "allowed_track_ids": [],
    "excluded_track_ids": [],
    "max_time_stretch_percent": 4.0,
    "harmonic_policy": "rekordbox-related-2"
  }
}
```

Style terms describe desired planning behavior. They do not imply that tracks
have authoritative genre, mood, or energy labels.

## `MixPlan`

```json
{
  "schema": "dj-engine/mix-plan",
  "schema_version": "0.1.0",
  "plan_id": "uuid",
  "planner": {
    "provider": "manual",
    "model": "manual",
    "prompt_version": "manual-v1"
  },
  "brief": {},
  "ordered_track_ids": [],
  "segments": [],
  "transitions": [],
  "requested_duration_s": 2700,
  "estimated_duration_s": 2674,
  "validation_status": "not_run",
  "warnings": [],
  "explanation": ""
}
```

The D036 plan is strict and declarative. It contains one
`PlannedTrackSegment` per ordered track and one `PlannedTransition` per
adjacent pair. It contains no path, shell command, Python, JavaScript,
filtergraph text, or arbitrary executable expression. The executor resolves
track IDs through the collection and verifies source hashes.

## `PlannedTrackSegment`

```json
{
  "segment_id": "segment-001",
  "track_id": "sha256:<hex>",
  "start_downbeat_index": 16,
  "end_downbeat_index": 144,
  "target_bpm": 126.0,
  "gain_db": -3.0,
  "reason": "Use a phrase-aligned excerpt with bounded gain and stretch."
}
```

Rules:

- Start/end indices resolve against the All-In-One downbeat grid, falling back
  to another non-empty grid only when necessary.
- The end index must be in range and greater than the start.
- `gain_db` stays within −24…+6.
- Optional `target_bpm` stays within the brief's maximum stretch and the
  hard 4% engine cap.

## `PlannedTransition`

```json
{
  "transition_id": "transition-001",
  "from_track_id": "sha256:<hex>",
  "to_track_id": "sha256:<hex>",
  "duration_bars": 16,
  "style": "house_eq_v1",
  "curve": "tri",
  "reason": "Detected-grid overlap with a midpoint bass handoff."
}
```

The only current bar counts are 4, 8, and 16. Transitions must exactly match
the consecutive ordered-track pairs, and adjacent effective BPMs must agree
within 0.2 BPM. `style` is `linear_crossfade` or `house_eq_v1`; `curve`
remains `tri` for the linear path. D037 derives seconds from the outgoing
segment's detected downbeat span after any stretch, aligns the incoming
segment at its selected downbeat, and rejects more than 70 ms of accumulated
incoming/outgoing grid drift across the overlap. Timing stays
`benchmark_estimate` until heard and marked `user_verified`.

D038 records `user_verified` as experiment evidence for the two transitions
in the rendered v2 plan and a positive report on the primary click diagnostic.
It does not rewrite the stored `RhythmGrid.authority`: unheard regions and
other tracks remain `benchmark_estimate`.

## `RenderManifest`

```json
{
  "schema": "dj-engine/render-manifest",
  "schema_version": "0.1.0",
  "render_id": "uuid",
  "plan_id": "uuid",
  "renderer": {
    "name": "undecided",
    "version": "undecided"
  },
  "source_track_hashes": [],
  "executed_operations": [],
  "requested_duration_s": 2700,
  "planned_duration_s": 2674,
  "rendered_duration_s": null,
  "output_path": null,
  "output_sha256": null,
  "output_measurements": {
    "integrated_lufs": null,
    "loudness_range_lu": null,
    "true_peak_dbtp": null,
    "sample_rate_hz": 44100
  },
  "status": "not_run",
  "warnings": [],
  "failures": []
}
```

Each executed operation records the validated tool name/arguments with
authority `executed_action`. D036 publishes the WAV atomically only after
duration/loudness/peak measurement and a second source-hash check.

## Versioning policy

- Patch: clarification that does not change valid serialized data.
- Minor: backward-compatible optional fields or enum additions.
- Major: renamed/removed fields, changed meaning, or incompatible validation.

Every artifact records its schema name and version. Parsers reject unsupported
major versions rather than guessing.

## Open schema decisions

- Exact confidence scale for each analyzer.
- Whether beat/downbeat arrays live inline or in compressed sidecars.
- Whether the initial gain/EQ bounds, crossover frequencies, and loop-edge
  policy survive listening tests.
- Mastered delivery formats beyond the implemented 44.1 kHz stereo
  `pcm_f32le` WAV.
- Transition score weights (initial v1 values in D033; not listening-validated).
- Practical V1 acceptance thresholds for using estimates in plans.

These remain provisional or explicitly unavailable until tested and recorded
in `DECISION_LOG.md`.
