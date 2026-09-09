# Experiments and validation

## 2026-09-07 — P-E001 — Standalone vertical slice

Goal: implement the authorized parallel prompt-to-playlist foundation with
deterministic retrieval and replaceable adapters, without changing the DJ
mixing engine or its runtime.

Environment: Python 3.12.10, Pydantic 2.13.5, pytest 9.1.1, Tk 8.6.13 on
the existing Apple Silicon Mac. Independent `uv sync` resolved 12 packages;
Pydantic is the only direct runtime dependency. No heavy analyzer dependencies
were installed into the package environment. No engine lockfile changes.

### Verification

| Check | Outcome |
|---|---|
| Package `uv run pytest -q` | 190 passed in 0.24 seconds |
| Parent engine `uv run pytest -q` | 54 passed in 5.17 seconds |
| `uv build` | Source distribution and wheel built successfully |
| Wheel in isolated `uv run --no-project --with …whl` environment from `/tmp` | Import and rules translation passed; 14 packaged descriptors; no DJ engine import available |
| Desktop actual Tk event-loop smoke | Submitted the default synthetic query; rendered three result rows, first Night Grid (Fictional Demo) |
| CLI synthetic prompt and query search | Returned deterministic evidence-backed candidates |
| Existing DJ artifact import | 10 tracks; all BPM retains `benchmark_estimate` / `warning`; zero semantic tags |
| Actual catalog query, BPM 130–133 inclusive, limit 5, BPM ascending | 6 eligible tracks, 5 returned |
| Actual catalog required `genre:house` | 0 matches; missing tag evidence reported |

Synthetic prompt: `require house; prefer dark; bpm 120-130; count 3`.
Candidates: Night Grid, Warehouse Lantern, Sunroom (all fictional demo tracks).
First two have dark evidence; Sunroom has coverage 0 for that preference and
explicitly lists it as missing. No fake source audio accompanies the examples.
Fixture `user_verified` means authored test metadata and is explicitly marked
as not a listening verification of real music.

Generated local artifacts, all outside music folders:

- `output/dj-catalog.json`: native snapshot imported from existing analysis.
- `output/demo-result.json`: complete versioned synthetic prompt run.
- `dist/prompt_to_playlist-0.1.0-py3-none-any.whl` and source distribution.

Public tool tests cover hard/soft filters, negative-tag completeness, failed
and unknown statuses, numeric bounds, IDs, stable ordering/digests, custom
vocabulary, no semantic inference and unsupported operation rejection. Provider
tests (106 cases) use mocked HTTP throughout, including refusal, incomplete
response, malformed/duplicate JSON keys, size bounds, unknown tags, invalid
constraints, network errors and mutation at the vocabulary boundary. CLI tests
cover interactive input, JSON output, failure exits and output safety.

### Findings and fixes

Independent review found that mutable lists could bypass construction-time
validation: `get_tracks` could accept a caller-added duplicate ID, and a
caller-added alias could change vocabulary resolution. Fixed by revalidating
catalog/vocabulary snapshots at public lookup, normalization, query, service
and translator boundaries. Regression cases now pass before network dispatch.
No test failures remained in the final run.

The first synthetic desktop smoke created and destroyed a real Tk window and
submitted the form through its event loop. This verifies widget/service
wiring; it is not a broad platform/accessibility or live-provider UI evaluation.
The library and CLI remain usable without Tkinter.

### Preservation

Before and after development, SHA-256 for all ten authorized MP3 files matched
the immutable table in the parent `docs/CORPUS.md`. No source metadata, names,
directory contents or audio were modified. The secondary MP3 folder was not
analyzed or used. There were no corpus renders or analyzer runs; engine tests
use synthetic temporary audio only.

Stored `../../output/step1-collection.json` also remained byte-identical:
`348d2f857b5d98476386e8da3499fbad15966cf68814beda497a9062459fdb93`.

### What is not established

No live OpenAI request was made. A model is not configured in `OPENAI_MODEL`
in this session; the host must explicitly select one for the live provider.
Credentials were not printed or written. Mocked tests establish adapter and
validation behavior, not language accuracy, model availability or resistance
to every prompt injection. Supported wire behavior was checked against the
[official Structured Outputs guide](https://developers.openai.com/api/docs/guides/structured-outputs).

The real corpus has no semantic tags, so mood/genre/energy match quality cannot
be assessed from this artifact. A reviewed annotation set and a fixed live
prompt evaluation are the next independent playlist checkpoint. This work
does not establish DJ transition compatibility, total set duration or render
readiness, and does not resolve the accepted mix's +1.04 dBTP headroom issue.

## 2026-09-07 — P-E002 — Authorized 120-file pool and live OpenAI setup

### Request and scope

The user explicitly requested use of the 120-track pool and the project key
named `AUTODJ_OPENAI_API_DEV_KEY` in `/Users/manuelalvarez/.zshrc`.
Parent D040/E028 record the scoped supersession of the prior pool hold. Work
was limited to metadata/hash import, configuration, live prompt translation
and local catalog retrieval. No full audio-model analysis or rendering ran.
Package version is now 0.2.0; existing catalog/query/run schemas remain 0.1.0.

### Import and evidence

Pool: `../../test_tracks_folder_mp3`, exactly 120 regular MP3-named files,
1,381,021,989 bytes. One `.DS_Store` entry was skipped. Canonical import took
6.292754 seconds according to its manifest timestamps and used FFprobe 8.0.1.
A preceding 5.58-second development preflight is retained separately; it did
not overwrite final artifacts. Both passes verified source preservation.

Command:

```sh
uv run prompt-playlist import-folder --folder ../../test_tracks_folder_mp3 \
  --vocabulary pool-vocabulary.json --out output/pool-catalog.json \
  --manifest output/pool-import-manifest.json
```

| Result | Count |
|---|---:|
| Imported unique catalog tracks | 120 |
| Failed/duplicate files | 0 / 0 |
| Embedded titles / artists | 120 / 116 |
| Container durations | 120 |
| Usable positive embedded BPM | 22 |
| Embedded genre annotations | 65 |
| Exactly mapped genre annotations | 62 |
| Unmapped genre annotations | 3 |
| Normalized mood / energy / vocal evidence | 0 / 0 / 0 |
| Complete tag axes | 0 |

Three BPM annotations were zero and remain unknown. Unmapped genre values:
`Bar House Deep`, `Disco Italo-Disco`, `LAGRIMA DE OURO`. The pool-specific
`pool-descriptors-v1` vocabulary has 39 entries and does not alter the bundled
14-entry vocabulary. No subtype/parent genre expansion or filename inference
occurs. Raw tag keys include mood on three files and energylevel on seven;
their scale/meaning has not been normalized or verified, so the catalog does
not claim those descriptors. Some MP3-named files report other containers;
the manifest preserves that warning without renaming or decoding them to PCM.

Artifacts and SHA-256:

- `output/pool-catalog.json`:
  `edee12016a37133218cfddeb620dad3b1bdfb563a1643af75f0654f444e32a8f`.
- `output/pool-import-manifest.json`:
  `84236b16223d88c4bb0f41a33afecad53af4bfa31db87b65b1eec58276e9d009`.
- Preflight artifacts: `output/pool-*-preflight-2026-09-07.json`.
- Initial inspection: parent `output/playlist-pool-inspection-2026-09-07.json`.

All 120 source hashes and directory inventory matched before/after import.
A final verification also rehashed all 120 against the manifest, checked the
original ten-track corpus against `../../docs/CORPUS.md`, and verified the
original analysis JSON digest from P-E001. All matched. No source or `.zshrc`
modifications were made, and no credentials were printed or persisted here.

### OpenAI setup and first failure

`playlist.toml` selects OpenAI `gpt-5.4-mini-2026-03-17`, the pool catalog and
vocabulary, and the explicitly named key source. The model and structured
output support were checked against the
[official model page](https://developers.openai.com/api/docs/models/gpt-5.4-mini)
and [Structured Outputs guide](https://developers.openai.com/api/docs/guides/structured-outputs).
The parser reads only the requested literal assignment if the named environment
variable is absent. It does not source the shell file or use another API key.

First real request: “Find up to five tracks. Only include tracks tagged as house.”
Authentication and schema output succeeded in 3.23 seconds, but intent
preservation failed: the model returned limit 10 and an unresolved claim that
the limit was fixed. The service would withhold retrieval, preserving the
unresolved requirement. Artifact: `output/openai-live-translation.json`.

Revised the prompt to `playlist-query-v2` and added the count field description:
explicit numbers/number words set the 1–100 upper bound; 10 is only the default
when no count is requested. The same real request then returned required house,
limit 5 and no unresolved requirements in 1.45 seconds. Artifact:
`output/openai-live-translation-v2.json`. No automatic fallback/retry was used.

### Five-case live evaluation

```sh
uv run python -m prompt_to_playlist.live_check --config playlist.toml \
  --out output/openai-live-check.json
```

| Case | Expected/observed result | Seconds |
|---|---|---:|
| English count and house-only genre | Limit 5, required house, 5 real matches | 2.000 |
| Spanish dembow-only request | Limit 3, required dembow, 3 real matches | 1.391 |
| BPM and ordering | Limit 4, 120–130 bounds, ascending BPM, 4 matches | 1.676 |
| No vocals | Exclusion preserved, 0 matches because vocal evidence is incomplete | 1.600 |
| 45-minute beatmatched continuous mix | `needs_clarification`, no search result | 1.198 |

All checks passed, including catalog ID membership. Complete expected/observed
queries, original prompts, matched IDs/evidence, errors and elapsed times are
in the versioned report. Total live calls for this work: seven (first failure,
its corrected retest, five evaluation cases). Neither catalog nor audio was
sent to the model; only request text, vocabulary and query instructions/schema.

### Code, packaging and UI validation

- Final package suite: **346 passed in 0.37 seconds**.
- Engine regression suite: **54 passed in 4.60 seconds**.
- `uv sync` and `uv build`: v0.2.0 source distribution and wheel succeeded;
  runtime dependencies still only Pydantic, with optional installed FFprobe/Tk.
- Configuration tests use fake keys; verify literal-only parsing, ambiguity,
  bad TOML, hostile shell syntax, redacted errors and exact variable precedence.
- Import tests cover missing/invalid fields, source changes, duplicates,
  hidden files/symlinks, subprocess bounds/failures, empty pools and versions.
- CLI verifies output paths before live requests and refuses catalog publication
  when source bytes/inventory change, keeping only a diagnostic manifest.
- Actual configured Tk event-loop smoke: displayed 120 tracks/model/coverage;
  replayed the prior real translation and displayed five real matches. This
  UI check made no additional API request. It is not broad accessibility QA.
- One intermediate suite failure was an assertion still expecting the previous
  prompt version; updated it to v2 and retained wire count-bound checks.

The configured launcher is `Open Playlist.command`; it passes the explicit
profile. Generic no-profile CLI/library defaults remain offline, and regular
tests never invoke the explicit live-check command. No engine code or lockfile
changes and no commits were made.

### Remaining limits

The setup is operational for the pool's available metadata. Five prompts do
not prove general language accuracy, prompt-injection resistance, subjective
music fit or tag correctness. Metadata genre coverage is partial; BPM is an
unverified embedded annotation. Reviewed source annotations, normalization of
additional metadata and broader user examples remain the next playlist work.
Automatic MixPlan/render integration and engine headroom remain separate.

## 2026-09-07 — P-E003 — Natural-language launch regression and light UI

### Trigger and correction

The user typed the unmodified description “house dj set energetic” and was
told to write semicolon-separated clauses. Read-only process inspection found
the old `ui --catalog output/dj-catalog.json` offline window still alive
alongside the configured `ui --config …/playlist.toml` window. E002’s successful
configured-window smoke had not removed that user-visible ambiguity.

P007/D041 changes the product boundary: the desktop requires OpenAI, honors
explicit config then current-directory and editable-checkout profiles, and
rejects rules mode. Generic CLI prompt defaults to OpenAI; explicit rules
parsing remains available to developers. Library callers continue supplying
a translator. No automatic fallback or extra model/tool loop was introduced.

The native Tk interface now uses light styling, plain-language criteria,
artist/BPM columns, an immediately visible missing-preference notice and
optional technical evidence. Percentage scores are removed from the normal
view because descriptor coverage is not musical quality. Input is locked
during a request and duplicate submission is blocked. No UI/runtime dependency
was added; distribution version remains 0.2.0 and schemas remain 0.1.0.

### Six actual OpenAI requests

Command: `uv run python -m prompt_to_playlist.live_check --config playlist.toml
--out output/openai-live-check-natural-language-v3.json` (one command).
The report records `gpt-5.4-mini-2026-03-17`, `playlist-query-v3`,
`pool-descriptors-v1`, 120 catalog tracks, six attempted requests and overall
`passed: true`. The snapshot/catalog were already imported; no source audio
was opened for this correction.

| Request case | Observed behavior | Seconds |
|---|---|---:|
| Exact user text: house dj set energetic | Required house; preferred high energy; limit 10; eight matches; no unresolved clauses | 2.924 |
| English count and house | Required house; limit 5; five matches | 2.395 |
| Spanish dembow and count | Required dembow; limit 3; three matches | 3.720 |
| BPM bounds and ordering | 120–130 BPM; ascending order; limit 4; four matches | 2.087 |
| House with no vocals | Vocal exclusion retained; zero matches because negative vocal evidence is incomplete | 1.874 |
| 45-minute beatmatched continuous mix | Clarification required; duration/transitions retained as unresolved; no search | 1.521 |

Every returned ID belongs to the saved catalog. For the exact user request,
all eight matches carry the exact sourced `genre:house` annotation and
`missing_preferred_tags: ["energy:high"]`; BPM bounds remain open and order is
relevance. No energy tag, parent-genre expansion or mix-readiness claim was
fabricated. A “DJ set” phrase alone is treated as playlist context, while the
explicit continuous-mix case still blocks unsupported work.

Report: [`openai-live-check-natural-language-v3.json`](output/openai-live-check-natural-language-v3.json).
These six API calls are separate from P-E002’s seven historical setup calls.
Only the request, vocabulary and contract were sent; no audio, catalog or
credential value was added to prompt text.

### Validation and remaining limits

- Final isolated package suite: **363 passed**. Tests use mocked provider
  responses; the six real requests are recorded separately above.
- `uv build`: version 0.2.0 wheel and source distribution both succeeded.
- Real Tk event-loop replay of the saved successful OpenAI translation:
  **all recorded checks passed**, with **zero additional API calls**. It
  displayed eight results, required house, the missing-energy notice and the
  unchanged natural-language request. There is no percentage-confidence column.
- Verified busy input locking, disabled export while waiting, one service call
  for duplicate submission, recovery after provider failure, removal of stale
  results/exports after a failed new request, and full error text in details.
- Verified all checked controls stay inside 1200×840 and 1000×700 windows with
  details both closed and open. Long clarification text stays compact in the
  overview and complete in details. These are widget geometry/state checks;
  screenshot-based visual QA was unavailable through desktop automation.
- Local native-check artifact: [`desktop-refresh-check.json`](output/desktop-refresh-check.json).
  This is development verification, not a new public playlist data contract.

The regression’s live result establishes this request’s interpretation, not
general language coverage or that the pool contains energetic music. Reviewed
energy/mood/vocal annotations and broader user examples remain separate work.
No engine code, engine lockfile, source music, import catalog or `.zshrc`
change is part of this correction. No new audio-hash claim supersedes E002.

Final handoff check: the development preview was closed and the current
OpenAI-configured native view reopened with the saved, verified eight-track
result for the user's exact prompt. Subsequent searches use the real configured
translator; reopening made no API request. A scan of 55 package/output text
artifacts found no project credential value. Saved catalog and import-manifest
SHA-256 values still match P-E002; no music was read for this check.
