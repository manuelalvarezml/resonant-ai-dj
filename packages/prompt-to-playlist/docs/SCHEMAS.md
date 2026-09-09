# Prompt-playlist contracts — 0.1.0

`models.py` implements these contracts. Extra properties, coercion from
strings/booleans to numbers, non-finite values and unknown schema versions
are rejected. Standalone artifacts identify `schema` and `schema_version`;
queries and evidence objects are embedded values. Changes to valid data or
meaning require an explicit schema-version change and consumer migration.

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
