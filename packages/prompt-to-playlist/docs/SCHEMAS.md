# PlaylistIQ contracts — package 0.3.0

## Current contracts — 2026-09-22

Catalog, translation, search result and playlist run write **0.3.0**, retaining readers for 0.1.0 and 0.2.0. Package release is 0.4.0; descriptor-run schema remains independent. Exact validation lives in [models.py](../src/prompt_to_playlist/models.py).

- `CatalogTrack.semantic_audio`: encoder identity, sampling policy, 1–3 segments with start/end seconds and finite, normalized 512-dimensional vectors.
- `PlaylistQuery.semantic`: positive `description`, up to three `avoid` descriptions, optional encoder identity and vectors (one per phrase). Unencoded queries remain valid and disclose fallback. New replay writes retain vectors; `search` does no inference.
- `IntentPlan.musical_description` and `avoid_descriptions`: audible English retrieval targets, separate from user-language interpretation/assumptions. `playlist-intent-v1.6` uses available-catalog descriptor IDs for soft preferences; full vocabulary for explicit constraints. Local validation rejects unavailable soft fields. Compiler is `intent-compiler-v1.2`.
- `CatalogTrack.preference_scores`: full `theme:*`, `instrument:*`, `valence:positive/negative` evidence plus existing scores. These are soft objectives, never automatically hard tags.
- `ScoreContribution.score_kind`: `model_support` or `relative_similarity`; `detail` preserves phrase, raw positive mean/range, negative contrast and relative-rank meaning. Groups now include `semantic`.
- `SearchResult.ranking_version`: `hybrid-semantic-v1` when fusion actually occurs; otherwise structured `maest-intent-v1` with warnings. Service reports `partial_support` when requested semantic evidence cannot be used.

For each eligible candidate, semantic contrast is mean positive cosine minus 0.25 times mean negative cosine. Midrank utility is `(strictly lower + 0.5 × tied) / eligible_count`, with a 1e-9 tie tolerance. Contributions use 30% semantic / 70% structured when both exist, or semantic alone without structured objectives. Explicit BPM ordering still precedes fit. New numeric objectives are removed for every eligible candidate when any lacks evidence, then remaining structured weights are normalized. Replay rejects explicit legacy ranking when semantic data would be discarded.

See [implementation and replay evidence](ESTIMATOR_UPGRADE.md). Earlier schema descriptions below are historical.

`models.py` implements these contracts. Extra properties, coercion from
strings/booleans to numbers, non-finite values and unknown schema versions
are rejected. Standalone artifacts identify `schema` and `schema_version`;
queries and evidence objects are embedded values. Changes to valid data or
meaning require an explicit schema-version change and consumer migration.
PlaylistIQ is the product name; existing serialized names remain stable.

Parent D058 changes only the future consumer narrative. Saved playlists,
source-specific playback/download capabilities and playlist-file archive
manifests belong to Resonant's host schema family, not `prompt-playlist/*`.
No package contract version changes here.

## Catalog

`prompt-playlist/catalog`: `catalog_id`, `tracks`, `warnings`.
Track IDs must be unique. An empty catalog is valid and yields no matches.

Each `CatalogTrack` contains:

| Field | Meaning |
|---|---|
| `track_id`, `title` | Required stable identity and display title |
| `artist` | Optional supplied metadata; unknown is null |
| `bpm`, `duration_s` | Nullable `NumericEvidence`, units in field names |
| `tags` | List of sourced `TagEvidence` |
| `complete_tag_axes` | Catalog-author assertion of exhaustive labels per axis |
| `warnings` | Track-local source cautions |

Numeric evidence is `{value, authority, source, status, confidence}`. BPM and
duration must be positive if supplied. Tag evidence replaces `value` with
canonical `tag` (`axis:value`). `source` identifies the provenance; the DJ
adapter stores a compact serialized provenance record with analysis/collection
IDs, original hash, field and analyzer/model versions. There are no source
paths, executable expressions or full beat arrays in this catalog.

Evidence authority accepts `encoded_fact`, `standardized_measurement`,
`deterministic_measurement`, `benchmark_estimate`, `user_verified`.
`llm_proposal` and `executed_action` cannot be track evidence. Status is
`passed`, `warning`, `rejected`, `unknown`, `failed`, or `not_run`; only
passed/warning evidence participates in search. Confidence is nullable 0–1,
supplied on a source-documented scale; it does not weight ranking. An adapter
must not normalize a different source scale without documenting its conversion.

Multiple tag sources may coexist. Positive evidence is their usable union;
any usable excluded tag rejects the track. There is no automatic arbitration
of conflicting annotations. `complete_tag_axes` must contain known axes with
no duplicates. For example, `exclude vocals:vocal` requires the `vocals` axis
to be complete, vocal to be absent, and no unusable annotation on that axis.
An instrumental tag alone does not establish exhaustive vocal annotation.

## Vocabulary

`prompt-playlist/vocabulary`: `vocabulary_id`, `descriptors`.
Each descriptor is `{id, description, aliases}`. IDs follow
`^[a-z][a-z0-9_-]*:[a-z][a-z0-9_-]*$`. IDs must be unique. Aliases are exact
after trimming and case-folding and cannot resolve to multiple IDs.
The bundled `descriptors-v1` has genre, mood, energy and vocals axes.
It defines request vocabulary, not evidence that any track has those labels.

## Query

```json
{
  "required_tags": ["genre:house"],
  "preferred_tags": ["mood:dark"],
  "excluded_tags": [],
  "min_bpm": 120.0,
  "max_bpm": 130.0,
  "limit": 3,
  "excluded_track_ids": [],
  "order": "relevance"
}
```

Lists default empty, BPM bounds null, limit 10, order relevance. Bounds are
inclusive and within (0, 400]; minimum cannot exceed maximum. Limit is 1–100.
Tags and excluded IDs cannot repeat within a list. Required/preferred tags
cannot also be excluded. Required and preferred lists may overlap: that tag
is both mandatory and part of the chosen coverage score. Vocabulary validation
rejects unknown canonical IDs. Orders: `relevance`, `bpm_ascending`,
`bpm_descending`. No paths, rendering operations, target duration or free-form
query language are accepted here.

## Translation and run

`prompt-playlist/translation`: `request_text`, `query`, `provider`, `model`,
`prompt_version`, `vocabulary_id`, `authority: llm_proposal`, `unresolved`,
`warnings`. Both live and rules interpretations occupy the proposal lane;
`provider: rules` / `model: explicit-grammar` distinguishes offline parsing
and does not claim a model was called. Provenance fields are assigned by code.
`playlist-query-v3` identifies the revised OpenAI interpretation policy: a direct
single-genre request is required; ordinary mood/energy is preferred unless
mandatory; “DJ set” alone does not ask for rendering. This is a prompt-policy
revision, not a schema change or a source of track evidence.

`prompt-playlist/run`: `translation`, `result` (nullable), `status`, `warnings`.
Statuses are `matched`, `no_matches`, `needs_clarification`. Any unresolved
requirement produces `needs_clarification` and null result, with no retrieval.
Malformed input/provider output raises an error rather than becoming an empty
playlist. CLI valid runs, including no matches/clarification, exit 0; invalid
input and provider failures exit 2. Inspect status in integrations.

The OpenAI wire DTO requires every query key (nullable values still explicit)
plus `unresolved` and `warnings`. It allows no metadata/evidence/track-inclusion
fields. The supplied vocabulary constrains tag enums. Local validation remains
required even with provider schema enforcement.

## Search result

`prompt-playlist/result`: `catalog_id`, `vocabulary_id`, `query`,
`ranking_version: tag-coverage-v1`, `matches`, `eligible_count`,
`excluded_count`, `warnings`, `catalog_digest`, `vocabulary_digest`, `result_id`.

`eligible_count` is before limit; `excluded_count` counts hard-filter failures,
not eligible candidates omitted by the limit. Each match includes the full
compact `track`, `score` (0–1), `matched_tags`, `missing_preferred_tags`, and
deterministic `reasons`. Matched tags contain requested positive tags only;
all supplied annotations remain visible in the track. Warnings report missing
catalog tags, unknown BPM/exclusion coverage, result shortfall, unmet preferences
and the lack of DJ-order validation. Search never pads with invented IDs.

## Generic tool catalog

`list_tools()` returns versioned read-only definitions and JSON argument schemas:

| Tool | Arguments | Output |
|---|---|---|
| `normalize_descriptors` | `terms: string[]` | Canonical tags and vocabulary ID |
| `search_tracks` | `query: PlaylistQuery` | SearchResult |
| `get_tracks` | `track_ids: string[]` | Tracks in requested order |

`dispatch_tool` validates arguments and executes only these names. Lookups
reject duplicate, unknown and more than 100 IDs. Normalization is exact alias
lookup; free-form prompt interpretation is the separate `Translator` protocol.
The catalog is provider-neutral and is not itself an OpenAI function envelope.

## Folder import manifest (v0.2 package, schema 0.1.0)

`prompt-playlist/folder-import` records `importer_version: mp3-metadata-v1`,
source folder, catalog/vocabulary identity, vocabulary digest, FFprobe executable
and version, per-probe timeout, start/finish times, inventory/hash verification,
entries, aliases, coverage counters, observed tag-key coverage and warnings.

Each entry preserves filename/path, SHA-256 before/after, source-unchanged flag,
container format, a restricted set of imported encoded fields (title, artist,
genre, BPM/TBPM/tempo), observed field names, mapped/unmapped genres, field
provenance, warnings and errors. Status is `imported`, `duplicate`, `skipped`,
`failed`, or `changed` (`pending` is internal during construction). Same bytes
share one ID with every alias retained. Symlinks, hidden files and other formats
are skipped explicitly; empty pools are rejected. The CLI publishes no catalog
if source bytes or directory inventory changed during the import.

Genre labels map only to exact aliases in the supplied vocabulary; multi-label
genre fields split on comma, semicolon or slash after whole-string alias lookup.
These are `encoded_fact` annotations with `warning` status: the fact is what
the metadata says, not verified genre truth. BPM annotations remain
`benchmark_estimate`/`warning`, even though their numeric string is encoded.
No axis is declared complete. Unknown raw labels and invalid/zero/conflicting
BPM are recorded without inventing replacements. Parent genres are not expanded.

## Project configuration

The explicitly selected TOML profile has `schema_version: 0.1.0`, `provider`,
`catalog`, optional `vocabulary`, and optional `openai` table (required for
provider OpenAI). The latter contains `model`, `api_key_env`, optional
`key_source_file`, and `timeout_s` in (0,120], default 30. Relative paths resolve
against the profile directory. Unknown properties are rejected. No actual key
value belongs in the configuration. For `ui` only, profile selection is explicit
`--config`, then current-directory `playlist.toml`, then the editable package
checkout’s profile. Other commands do not discover configuration implicitly.

`playlist.toml` chooses this user’s pool and project key. Explicit CLI catalog,
vocabulary and provider arguments override profile values. The desktop requires
OpenAI and rejects rules mode. Generic CLI `prompt` defaults to OpenAI; explicit
`--provider rules` selects offline parsing without reading a credential. An
explicitly selected rules profile also selects offline parsing for `prompt`;
`ui` rejects it. Library callers supply their own translator. These launch rules do not change any
serialized query, catalog or run schema.

## Live check report

`prompt-playlist/live-check`, schema version 0.1.0, records the model, catalog
and vocabulary identity, creation time, request count, overall pass/fail and
six case results in the current evaluation set. Each completed case has expected query fields/status,
observed versioned run, checks and elapsed seconds. It contains no credentials.
Execution is explicit and uses real API calls; regular test runs do not invoke it.

## Descriptor run (package 0.3.0, schema 0.1.0)

`prompt-playlist/descriptor-run` is the durable output of `analyze-folder`.
It is a sidecar, not a `Catalog`, and therefore does not silently change the
current UI/search behavior. It records pipeline/run identity, input/selection
bounds, requested algorithms and CPU threads, host/tool versions, pinned model
assets, tracks, per-algorithm projections, a combined sequential-pipeline
projection, source-preservation results, failures and warnings.

Each descriptor track has a SHA-256-based ID, relative path/display filename,
size and hashes before/after, duration, algorithm results, warnings, and a
controlled `descriptor_document` prepared for later lexical/text-embedding
experiments. Algorithm results retain implementation/version, authority,
passed/warning/failed state, raw values, warnings/error, and `StageMetrics`.
The semantic result keeps all class probabilities and aggregation details;
thresholded catalog tags are intentionally not invented.

`StageMetrics` records process-tree wall time; user/system/total CPU seconds;
raw and host-normalized CPU utilization; sampled peak RSS/VMS, threads and child
count; I/O counters where available; minimum available RAM; swap; audio length,
real-time factor and throughput; exit code; telemetry interval/sample count;
and errors. Raw CPU may exceed 100% on multicore work. Requested thread count
is not a runtime guarantee; measured telemetry is authoritative. RSS, not macOS
VMS, is used for capacity projections.

Algorithm projections retain observed totals/mean/median/max, CPU, peak RSS and
threads, wall minutes per audio hour, CPU core-hours per audio hour, projected
serial minutes per 100 same-length tracks, and memory-only worker limits on
8/16/32 GB hosts with 35% worker headroom and 25% host reserve. The combined
projection sums the sequential stages without double-counting audio duration
and includes the pinned model-cache size. Every projection warns that a small
Mac sample is not a target-VM benchmark.

Failed attempts remain in each track's `AlgorithmResult` and `StageMetrics`,
but are excluded from capacity extrapolation. `measured_tracks` counts attempts;
`passed_tracks` and `failed_tracks` expose their outcome. A combined pipeline
projection includes only tracks whose requested stages all succeeded. This
prevents fast initialization/decoder failures from making an incomplete
pipeline look cheaper than a working one.

`prompt-playlist/performance-report` 0.1.0 repeats host, combined and algorithm
projections plus per-track stage metrics and descriptor artifact sizing. The
Markdown report is a human-readable projection, not another data contract.
`.checkpoints` files are internal resume state keyed by source hash plus pipeline,
algorithm, tool versions, model hashes and CPU-thread configuration.
They are portable across explicitly supplied prior descriptor outputs through
`--reuse-from` only when the prior run passed both source-preservation gates and
the complete checkpoint identity still matches. Imported checkpoints are
copied into the new output; prior artifacts are not changed. Reuse is an
execution optimization, not a new serialized schema or evidence authority.

The existing `CatalogTrack` still has numeric evidence only for BPM and duration
plus categorical `TagEvidence`. A deliberate catalog-schema migration is still
required before model scores can drive the UI without discarding thresholds,
confidence or abstention. Do not squeeze probabilities into `TagEvidence` or
call model coverage a complete tag axis. The plan is maintained in
[`AUDIO_FEATURES.md`](AUDIO_FEATURES.md).

Later CLAP vectors, descriptor-document TF-IDF/BM25 representations, text
embeddings, and hybrid retrieval scores must use separate versioned index/run
contracts referencing the immutable descriptor snapshot. They are not fields
to improvise inside the next extraction artifact.

## 2026-09-13 — MAEST Discogs519

Added opt-in `genre_maest` with all 519 mean sigmoid scores in the existing
algorithm values and a separate `prompt-playlist/genre-review` 0.1.0
`genre-top10.json`. It retains failed tracks and source-preservation gates.
No catalog integration or replacement of existing genre evidence.
See [MAEST setup, aggregation and command](MAEST_DISCOGS519.md).

## 2026-09-13 — MAEST listening-review checkpoint

The user-run MAEST diverse-37 output has 33 genre results and four RAM-limit
failures; fresh source hashes all match. A standalone `listening-review.html`
is now beside those outputs. See the DJ project’s `tools/genre-review/README.md`
for regeneration, review semantics and verification limits. No audio analysis
was rerun. The earlier “full run not executed” checkpoint is superseded by
this audit; no genre-quality acceptance or model replacement is implied.

## 2026-09-15 — MAEST top-six and local player integration

CatalogTrack adds optional `preference_scores` (default empty), with `scored-preferences-v1` ranking for continuous mood, vocals and danceability preferences. DEAM arousal uses a provisional, unvalidated linear soft-preference mapping, not categorical energy labels. Hard unknown constraints are not relaxed. Only top-six genre candidates enter matching; no inferred parent expansion, legacy genre fallback or accepted-review overrides. Server/browser feature records retain all 519 scores. Full contract and workflow: [WEB_INTEGRATION.md](WEB_INTEGRATION.md).

## 2026-09-19 — Iteration 1 contracts

New writes of catalog, translation, result and run use 0.2.0; both 0.1.0 and 0.2.0 are readable. Historical records are not rewritten. Vocabulary format remains 0.1.0; identity includes `discogs-parents-v1`. Earlier catalog/genre hold descriptions above are superseded.

- TagEvidence: `source_label` and `parent_tags` retain the original selected Discogs label and documented family.
- PlaylistQuery: `any_tag_groups`, `preferences` (tag/direction/importance/origin/source_span) and `genre_scope`. Old inputs default to empty new fields and exact scope.
- Translation: normalized `plan`, original `proposed_plan`, clarification history, compiler version, prompt digest and reasoning setting.
- IntentPlan: `playlist-intent-v1`, with ready/partial_support/needs_clarification/unsupported dispositions; source-anchored hard constraints, BPM, count, order, preferences, assumptions and evidence gaps.
- TrackMatch: `score_contributions` records group, tags, direction, origin, nullable evidence value, utility, normalized weight, contribution and source.
- SearchResult: `maest-intent-v1`, ordered eligible IDs and taxonomy version; input digests and content-derived result ID remain.
- PlaylistRun: adds `partial_support` and `unsupported`. No retrieval for blocking dispositions.
- Local request: optional `clarifications`, maximum three question (1–500) / answer (1–1000) pairs; prompt (1–4000) and original IDs/hashes stay separate.
- `search_tracks` allowlist tool version becomes 2; normalize/get remain 1. No tools are passed to the planner.

See [complete contracts and compatibility](ITERATION_1.md), [exact instructions](INTENT_PROMPT.md), [concrete strict schema snapshot](evaluations/iteration1-intent-schema.json) and [example run](evaluations/iteration1-example-run.json). Schema snapshots have the evaluated library vocabulary; runtime enums are generated from the active vocabulary.

## 2026-09-25 — Supervised experimental evidence v1

Existing top-level catalog/run schema 0.3.0 and historical reads remain. Optional algorithm IDs are `emotion_music2emo` and `danceability_musicnn`; comparison-only `estimator_reference` never replaces production reference artifacts. `SampledEstimates` is a strict nested `supervised-estimates-v1` contract; [generated JSON schema](evaluations/supervised-estimates-v1.schema.json).

- `model_id`: code/assets/policy identity; `kind`: music2emo or musicnn-dance. Exact labels/order live in the pinned metadata and `extended_labels.json` (56 themes; dance classes `danceable`, `not_danceable`).
- `sampling_policy`: supervised-3x30s-v1; `duration_s`, `sampled_seconds`, `coverage_fraction`, and 1–3 timestamped `segments`; no overlap, out-of-track coverage or inconsistent means.
- `scores`: complete finite 0–1 uncalibrated classifier support, independent theme sigmoids or binary dance softmax. `valence_mean`/`arousal_mean`: required finite raw 1–9-target, unclipped regressions for Music2Emo; absent for danceability.
- Each segment retains scores/raw VA and optional `detected_key`, `detected_mode`, `encoded_mode`, `chord_events`. These are internal preprocessing provenance, not validated replacement track-key evidence.
- `score_kind`, `regression_units`, `aggregation` are literal contracts; unknown fields are rejected. Out-of-range raw VA is retained, but does not enter the provisional preference mapping.

Web requests add optional enum `estimator_profile`: reference/music2emo/musicnn-dance/supervised. No field means reference. Result input snapshots retain the request profile and projected catalog identity `+estimators-<profile>-v1`; NumericEvidence sources identify the selected model/mapping. Web feature envelopes add optional `supervised_status` (not_run/partial/complete), preserving base completeness. Notebook attempts add defaultable `estimatorProfile` and `candidateScope`; historical attempts reopen as reference/all.

[Full contracts, fallback and replay behavior](research/SUPERVISED_ESTIMATORS_2026-09-25.md).


## 2026-09-25 — Quality-first estimator research and implementation

Quality-first non-genre research and the selected available specialists are delivered locally. The web default selects Music2Emo theme/VA, MusiCNN vocals, VGGish aggression and independent PaSST OpenMIC instrument evidence, retaining EffNet happy/sad/relaxed/danceability. SheetSage2 supplies selected key evidence. MAEST, MuQ and planner weights remain unchanged. Two authorized sources passed 8/8 new stages; retries execute zero stages. Richer nuanced-emotion prediction and listening superiority remain unresolved; do not present encoder-only releases or the same 56 tags as solving that objective.

[Implementation, two research reports, setup, model contracts and verification](TOP_ESTIMATORS_IMPLEMENTATION.md). Final validation: 502 Python tests, 83 web tests, 45 syntax modules, 28-file build, eight successful final audio stages and 26 exact fixed-query replays. No new provider calls or listener judgments. The new optional specialist stages and quality/openmic vocabulary identity preserve reference records and saved-profile replay.
