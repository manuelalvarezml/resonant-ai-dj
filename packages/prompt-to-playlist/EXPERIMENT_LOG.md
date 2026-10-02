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

## 2026-09-10 — P-E004 — PlaylistIQ implementation and documentation audit

**Decisions:** P009/P010; parent D046. **Kind:** read-only implementation audit,
tests, build, and documentation. No audio analysis and no live model request.

- Searched all 48 Markdown files in the workspace (excluding environments and
  Git internals). Thirty-five contained PlaylistIQ, prompt-to-playlist, or
  local-library references. Historical decision/experiment
  text was retained; current status pages now supersede the 2026-09-08 pause.
- `uv run pytest -q`: **363 passed in 0.75 seconds**.
- Parent `uv run pytest -q`: **54 passed in 7.73 seconds**.
- `uv build`: the 0.2.0 wheel and source distribution built successfully.
- CLI and `ui` help completed successfully. `playlist.toml` loaded, its
  120-track catalog resolved, and the named credential was available; only a
  boolean availability result was printed.
- Catalog inspection confirmed 120 tracks, 120 durations, 116 artists, 22 BPM
  values, 62 tracks with mapped genre, and zero normalized mood, energy,
  vocals, or danceability evidence. Search can currently filter tags and BPM;
  duration and artist are not query fields.
- Code inspection confirmed the DJ engine separately stores stream facts,
  LUFS/LRA/true peak, key/Camelot, rhythm grids, sections, and loops. The
  PlaylistIQ DJ adapter imports only BPM/duration, and the folder adapter imports
  limited metadata. The public analyzer always attempts All-In-One; internal
  ingest/Beat-This stages are not a complete public no-All-In-One workflow.
- The current Essentia runtime reports version 2.1-beta6-dev and exposes the
  older `Danceability` algorithm, but not `TensorflowPredictEffnetDiscogs` or
  `TensorflowPredict2D`. No semantic model weights were installed or executed.
- Added the product-facing PlaylistIQ name and macOS launcher while preserving
  every compatibility identifier. Added the canonical audio-feature plan.

This audit verifies the preserved implementation and launch path. It does not
establish selection quality, acoustic semantic accuracy, UI screenshot quality,
or a production license. The second diverse-folder comparison remains pending
an explicit folder and the planned enrichment implementation.

## 2026-09-10 — P-E005 — Record next pipeline and later retrieval comparisons

**Decision:** P011/D047. **Kind:** Documentation-only steer.

Updated the takeover, roadmap, architecture, feature policy, README, decisions,
and changelog. The next implementation is descriptor extraction with a variable
folder input and versioned output, including full compatibility/error testing.
Matching stays outside that build. Later experiments now explicitly include
CLAP, TF-IDF/BM25 descriptor documents, lightweight text embeddings, and a
hybrid ranker while preserving the structured explanation trail.

No analyzer, matching adapter, dependency, schema, catalog, source audio, API
request, or test run was created by this documentation update. Commercial
licensing is retained as a future viability note, not a private-playground
blocker.

## 2026-09-10 — P-E006 — Build and bound the PlaylistIQ 0.3 descriptor pipeline

**Decision:** P012/D048. **Kind:** implementation, compatibility resolution,
automated tests, and an explicitly bounded two-track acoustic smoke. No
All-In-One MLX, render, live OpenAI request, catalog merge, or full-folder run.

### Implementation and compatibility

Added `analyze-folder` with a one-track default and explicit `--all-tracks`.
The input folder is variable; supported non-hidden regular files are discovered
deterministically and symlinks are skipped. Output must be disjoint from the
source. Existing output requires `--resume`. Each track/stage runs in a fresh
process with timeout, RSS and host-available-RAM limits, sampled process-tree
telemetry, atomic results, and a checkpoint bound to source/config/tool/model
hashes. Selected source hashes and full folder name/size inventory are compared
before/after.

The optional analysis environment resolved on macOS arm64 / Python 3.12.10:
`essentia-tensorflow 2.1b6.dev1389`, `beat-this 1.1.0`, `torch 2.13.0`,
`torchaudio 2.11.0`, NumPy 2.5.3, psutil 7.2.2, FFmpeg/FFprobe 8.0.1. Twenty-one
pinned Essentia/Beat This assets occupy 108,633,937 bytes (103.60 MiB). Every
download is streamed, bounded to 256 MiB and SHA-256 verified. All-In-One is
absent from the dependency group and execution graph.

The first one-track run exposed energy CPU at 523.7% despite a four-thread
request. Added TensorFlow intra/inter-op controls; the final two-track run
measured energy at 303.6% and 295.6%. Thread settings remain requests, so the
reports keep actual process-tree CPU and peak threads as authoritative.

### Bounded real-audio result

Command selected exactly two of ten files:

```sh
uv run --extra analysis prompt-playlist analyze-folder \
  --folder ../../test_folder_10_house_tracks \
  --output-dir output/playlistiq-descriptor-smoke-2tracks-2026-09-10 \
  --max-tracks 2 --cpu-threads 4
```

Selected files were `01 My Paradise - Edit.mp3` (339.576 s, SHA-256
`c4fa9722112e74661c9a4da26fa386d9a65564da8a3cef25048df25168f31bae`)
and `02 For The Record.mp3` (345.001383 s, SHA-256
`ef90c63da5fb3352752e0c9283cf3ef0d0d8a961b3d4585da5e11ffba2a8a098`).
All 12 stages completed; failures were zero. Both hashes and the ten-track
folder inventory were unchanged. The other eight tracks were not decoded or
analyzed. A subsequent `--resume` regenerated reports from all 12 verified
checkpoints without rerunning a descriptor algorithm.

| Algorithm | Mean wall s/track | Mean CPU % | Peak RSS MB | Wall min/audio h | Serial min/100 tracks | RAM/worker with 35% headroom |
|---|---:|---:|---:|---:|---:|---:|
| metadata | 0.45 | 30.7 | 34.8 | 0.08 | 0.75 | 0.05 GB |
| loudness | 15.33 | 102.2 | 100.1 | 2.69 | 25.56 | 0.13 GB |
| key | 2.40 | 90.0 | 403.1 | 0.42 | 3.99 | 0.53 GB |
| rhythm | 9.78 | 222.2 | 1,061.8 | 1.71 | 16.29 | 1.40 GB |
| semantic | 5.82 | 189.7 | 1,311.4 | 1.02 | 9.70 | 1.73 GB |
| energy | 8.34 | 299.6 | 1,051.7 | 1.46 | 13.91 | 1.39 GB |

Combined sequential stages measured 84.233 seconds for 684.577 seconds of
audio: 7.383 wall minutes per audio hour, 151.467 CPU seconds, mean effective
CPU 179.8%, and a linear 70.194-minute estimate per 100 tracks of the same
average duration. Maximum observed stage RSS was 1,311.422 MB; with 35%
headroom the memory-only sequential worker estimate is 1.729 GB. Reserving 25%
of host RAM implies at most 3/6/13 memory-limited workers on 8/16/32 GB hosts,
before CPU, I/O and contention limits. Peaks were sampled every 0.2 s and may
miss shorter spikes. The host already had about 1,164 MB swap in use; no peak
increase was observed. macOS VMS was retained in JSON but is not used for RAM
sizing.

The strict descriptor JSON is 104,653 bytes for two tracks (51.10 KiB/track,
about 4.99 MiB/100 tracks if linear). It contains beat arrays; the future
matching table should use the compact descriptor document/scalars rather than
send raw grids or full provenance to an LLM.

### Feature sanity observations—not accuracy claims

| Track | BPM | Key | LUFS | Top acoustic genres | Danceable | Voice | Happy | Aggressive | Raw arousal (DEAM expected 1–9) |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|
| My Paradise | 130.43 | Eb minor / 2A | -8.96 | electronic .722; dance .386; house .273 | .997 | .731 | .492 | .443 | 5.976 |
| For The Record | 130.43 | G minor / 6A | -8.99 | electronic .742; house .319; dance .302 | .998 | .244 | .207 | .410 | 6.441 |

Key and loudness match the existing DJ artifact for both tracks. Beat This
gives 130.43 BPM for each; the existing All-In-One artifact says 133 and 130,
respectively. This is estimator disagreement to evaluate, not a reason to
overwrite either value. Semantic probabilities and raw arousal remain
uncalibrated estimates; two house tracks cannot validate classification or
threshold quality.

### Automated validation and artifacts

`uv run --extra analysis pytest -q` passed **377 tests in 1.29 seconds**.
New tests cover deterministic discovery/symlink handling, source/output
separation, pinned asset hash rejection, projections without double-counting
audio, report output, verified resume, source-mutation detection, and real
FFprobe/FFmpeg analysis of generated audio. Final wheel/parent regression
results are recorded after documentation in the closing verification entry.

Artifacts are under
`output/playlistiq-descriptor-smoke-2tracks-2026-09-10/` and are ignored by Git:
`descriptor-run.json`, `performance-report.json`, `performance-report.md`, and
12 checkpoints. They are operational evidence, not a reviewed enriched catalog.
The full ten-track command remains for the user and is documented in README.

### Closing verification

- `uv run --extra analysis pytest -q`: **377 passed in 1.29 s**.
- `uv build`: built `prompt_to_playlist-0.3.0.tar.gz` and the 0.3.0 wheel.
- Isolated wheel environment: reported version 0.3.0, parsed the analyzer's
  one-track default, and validated the two-track descriptor run.
- Parent engine regression: **54 passed in 7.77 s**.
- `git diff --check`: passed.
- Final ignored artifact SHA-256 values: descriptor
  `60ec85c7b340bf224fd0edf8821331f364cdecb30ff41f80f646517712a1f791`,
  performance JSON
  `4032117e5b53657fa89b190cb2748392004fb30f4a523cf0631124048e60e509`,
  performance Markdown
  `044bec3c638661ada0b7c698366f4a73963ed5bc317658e982d56c1d718bf021`.
- Prepared full-run output `output/playlistiq-house-10-full` did not exist at
  handoff. No full run or commit occurred.

## 2026-09-11 — P-E007 — Audit user full run and repair Beat This decoding

**Decisions:** P013/D049. **Kind:** user-run ten-track output audit, dependency
repair, automated regression checks, and one-track real-audio verification. No
All-In-One, catalog merge, matching, render, provider request, cloud action, or
full agent-run folder pass.

### User-run output

The user executed the prepared `--all-tracks --cpu-threads 4` command against
`../../test_folder_10_house_tracks`, writing
`output/playlistiq-house-10-full/`. Run
`descriptor-run:059f70bec05313643ccf` started
`2026-09-11T16:28:27.504629Z` and finished
`2026-09-11T16:31:31.640712Z`: 184.136 seconds elapsed. It discovered and
selected all 10 MP3s, totaling 3,779.012916 seconds (62.984 minutes) of audio.
Both source-hash and folder-inventory gates passed. A fresh independent SHA-256
check after inspection matched every value in the parent `docs/CORPUS.md`
manifest exactly.

The result is partial: 50 of 60 stages succeeded. Metadata, loudness, key,
semantic, and energy each passed 10/10. Rhythm failed 10/10 with the exact
error `RuntimeError: Could not load audio from "…"`. Fifty successful
checkpoints exist; failed results were correctly not checkpointed.

| Stage | Passed/attempted | Mean wall s | Mean CPU % | Peak RSS MB | Serial min/100 same-length tracks |
|---|---:|---:|---:|---:|---:|
| metadata | 10/10 | 0.22 | 3.0 | 8.4 | 0.37 |
| loudness | 10/10 | 8.29 | 102.2 | 110.4 | 13.81 |
| key | 10/10 | 1.26 | 77.9 | 506.5 | 2.10 |
| rhythm | 0/10 | 0.94 to failure | 71.4 | 363.6 | invalid |
| semantic | 10/10 | 3.00 | 202.5 | 1,400.0 | 4.99 |
| energy | 10/10 | 4.66 | 302.9 | 1,128.7 | 7.77 |

The generated report summed 183.718 seconds of stage wall time, projected 2.917
wall minutes/audio hour and 30.620 serial minutes/100 tracks, and observed
1,400.047 MB peak RSS (1.846 GB with 35% headroom). Those combined figures are
**not valid complete-pipeline estimates** because rhythm only measured fast
decoder failures. The successful per-stage values remain usable observations.
Code now excludes failed attempts from capacity projections and includes only
fully successful tracks in the combined projection.

Semantic output exists for all ten tracks. Danceability is 0.9813–0.9998;
DEAM raw arousal is 5.3468–6.5721 and deferred raw valence 5.6479–7.1788;
loudness is −16.43 to −8.78 LUFS. Nine tracks' top genre is `electronic`; one
is `house`, while house probabilities span 0.1362–0.5048. Mood and vocal scores
vary but remain uncalibrated benchmark estimates. This homogeneous house set
cannot validate thresholds or prompt relevance and reinforces the planned
diverse-folder evaluation.

Original partial artifact SHA-256:

- `descriptor-run.json`: `53589bb8fae901bac9b9840679c9635cc2f48d603c2af87b35f1600a31b30651`
- `performance-report.json`: `6384a4ed364881dc83370cf3c604469f4784a26747d209a8f7a59ab17d169cb5`
- `performance-report.md`: `a0828240097dcdf7358253f7d7cbdc07a65ad455a77e1b37d419fccddd78a3f1`

### Root cause and bounded repair

Local package-source inspection showed Beat This 1.1 calls
`torchaudio.load`, then falls back to `soundfile`, then optional `madmom`.
Torchaudio 2.11 raised `ImportError: TorchCodec is required…`; SoundFile and
madmom were absent after the dependency cleanup. Restored and locked SoundFile
0.14.0 with cffi 2.1.1 and pycparser 3.0, added a rhythm preflight requirement,
and retained the lighter fallback instead of adding TorchCodec.

The agent then analyzed only `01 My Paradise - Edit.mp3` with the rhythm stage.
It succeeded with 130.4348 BPM, 738 beats and 185 downbeats; wall 9.809 seconds,
CPU 21.601 seconds / 220.2%, peak RSS 1,052.953 MB, peak 12 threads, minimum
available host RAM 4,294.703 MB, and unchanged 1,108.25 MB swap. Source hash
remained `c4fa9722112e74661c9a4da26fa386d9a65564da8a3cef25048df25168f31bae`;
both preservation gates passed. A second invocation reused and migrated that
checkpoint without analysis.

Repair artifact SHA-256 after resume-report regeneration:

- `descriptor-run.json`: `9843d32ca17725577962f78919acbf39d63c90809d4cf89943976cbb1781710e`
- `performance-report.json`: `08d67e577a207326f3f0918f087440eb3bbadb37f926e3f445f9dc978f05f41d`
- `performance-report.md`: `c2659afba7b4e53b24251c4fb569bd4bcc18a365fe70d46c00916c95fadff612`

`uv run --extra analysis pytest -q` passed **381 tests in 2.82 seconds**.
New coverage requires the decoder fallback, forces Torchaudio failure and
verifies SoundFile MP3 decoding, rejects failed-stage capacity projections,
and migrates the pre-SoundFile checkpoint digest without recomputation.

### User resume command

From the package directory:

```sh
uv run --extra analysis prompt-playlist analyze-folder \
  --folder ../../test_folder_10_house_tracks \
  --output-dir output/playlistiq-house-10-full \
  --all-tracks \
  --cpu-threads 4 \
  --resume
```

This reuses/migrates the 50 passing checkpoints and runs the ten missing rhythm
stages. The resulting zero-failure report must be audited before its complete-
pipeline projections replace the P-E006 two-track baseline.

## 2026-09-11 — P-E008 — Complete ten-track resume and baseline audit

**Decisions:** P014/D050. **Kind:** user-run repaired resume plus read-only
artifact/source/cross-artifact audit. No agent-run full analysis, All-In-One,
catalog merge, matching, render, provider request, cloud action, or commit.

The user ran the exact P-E007 `--all-tracks --cpu-threads 4 --resume` command
against `../../test_folder_10_house_tracks`. Run
`descriptor-run:525359d08f4efeeb05db` started
`2026-09-11T17:59:10.744512Z` and finished
`2026-09-11T18:00:46.708568Z`: **95.964 seconds elapsed**. It reused exactly
five checkpoints per track and executed one rhythm stage per track. The output
now has **60 checkpoints, 60/60 successful stages, zero failures**, and 10/10
complete tracks. SoundFile 0.14.0 is present in the recorded tool versions.

Both built-in preservation gates passed. An independent post-run SHA-256 check
again matched all ten canonical hashes in parent `docs/CORPUS.md`. Strict
`DescriptorRun` validation passed, and the performance JSON projections match
the descriptor artifact exactly.

### Final capacity observations

The report combines the preserved 50 original stage measurements with the ten
new rhythm measurements. It is the complete sequential pipeline baseline, not
the 95.964-second resume elapsed time.

| Stage | Passed | Mean wall s/track | Mean CPU % | Peak RSS MB | Wall min/audio h | Serial min/100 tracks |
|---|---:|---:|---:|---:|---:|---:|
| metadata | 10/10 | 0.22 | 3.0 | 8.4 | 0.04 | 0.37 |
| loudness | 10/10 | 8.29 | 102.2 | 110.4 | 1.32 | 13.81 |
| key | 10/10 | 1.26 | 77.9 | 506.5 | 0.20 | 2.10 |
| rhythm | 10/10 | 9.53 | 229.1 | 1,354.7 | 1.51 | 15.89 |
| semantic | 10/10 | 3.00 | 202.5 | 1,400.0 | 0.48 | 4.99 |
| energy | 10/10 | 4.66 | 302.9 | 1,128.7 | 0.74 | 7.77 |

Combined: 3,779.012916 audio seconds (62.984 minutes), 269.608748 stage-wall
seconds, 516.190125 CPU seconds, mean effective CPU 191.46%, 4.2806 wall
minutes/audio hour, and 44.9348 projected serial minutes/100 same-average-length
tracks. Peak stage RSS is 1,400.047 MB; 35% headroom gives 1.846 GB per
sequential worker. With 25% host reserve, memory-only worker limits are 3/6/13
on 8/16/32 GB. Model cache is 108,633,937 bytes (103.60 MiB). Descriptor JSON
is 471,167 bytes: 46.01 KiB/track, about 4.49 MiB/100 tracks if linear. These
are small-sample Mac measurements; VM architecture, storage, throttling and
parallel contention still require target-host benchmarks.

### Output sanity and reproducibility

Beat This BPM ranges from 120.0 to 136.3636: one 120, two 125, six 130.4348,
and one 136.3636 BPM result. Every Beat This BPM, beat array, downbeat array and
event count exactly matches the same Beat This 1.1 output retained in the prior
DJ `step1-collection.json` for all ten source hashes. This establishes repeatable
local execution. It does not establish musical truth. Beat This differs from
the All-In-One selected tempo by 0–3 BPM; Life Is Trippy has the largest 3 BPM
difference.

Nine tracks have downbeat/beat ratios from 24.4% to 26.3%, close to a four-beat
pattern. `Dj Yellow Ft Marlene - Je Tm.mp3` has 382 downbeats for 1,027 beats,
or 37.2%. This atypical estimate was reproduced exactly from the old artifact,
so it is not a new decoder regression. Retain the grid and warning for later
rhythm review; PlaylistIQ matching uses compact BPM rather than beat arrays.

Key names/Camelot agree with the prior artifact for nine tracks. Dj Yellow uses
the enharmonic name Ab minor instead of G# minor but the same 1A Camelot code.
All ten LUFS values match exactly. Semantic/energy ranges remain those audited
in P-E007: danceability 0.9813–0.9998, raw arousal 5.3468–6.5721, deferred
valence 5.6479–7.1788, house probability 0.1362–0.5048. These are uncalibrated
estimates from a homogeneous set, not reviewed tags.

Final artifact SHA-256:

- `descriptor-run.json`: `88c959b5f8dd694dae6b31daed0c34fa53db1dd00ac51ef07b6bf5834ddc3e52`
- `performance-report.json`: `d852eb3a8d9d75a1bde0d2c280299e6389fac79426107ee566ba0428b314e7cd`
- `performance-report.md`: `d860b2b472fc8f363ccd36822ea3d374bc61f4cd9b5969d738dd2b3aac9a5328`

The complete output is ready for the deliberate descriptor-to-catalog bridge.
It does not yet drive the current metadata-only UI, and it does not validate
prompt-to-song relevance. The next acoustic corpus must still be explicitly
named, hashed and authorized before analysis.

## 2026-09-11 — P-E009 — Diverse-37 manifest and cross-output reuse verification

**Decision:** P015/D052. **Kind:** read-only discovery, SHA-256 manifest,
implementation/tests, and checkpoint compatibility audit. No new-folder audio
decode or analysis, full corpus execution, All-In-One, catalog merge, matching,
render, provider request, cloud action, source write, or commit.

The user explicitly selected `../../test_folder_37_tracks_diff_genres`. Its
non-recursive inventory contains **37 MP3 files, 37 unique hashes, and
418,398,951 bytes**, with no discovery warnings. Hash intersection against the
completed `output/playlistiq-house-10-full` descriptor found all ten baseline
tracks byte-for-byte and 27 new hashes. The exact inventory is preserved in
`docs/DIVERSE_37_MANIFEST.md` before analysis.

PlaylistIQ now accepts repeatable `--reuse-from PRIOR_OUTPUT_DIR`. The guard
requires a real prior output outside the selected source, a strict descriptor
run whose source-hash and inventory gates passed, and compatible internal
checkpoints. Each checkpoint is accepted only when current source SHA-256,
pipeline, algorithm, tool versions, model hashes and four-thread configuration
match; accepted data is copied atomically into the separate new output.

A read-only compatibility pass against the live baseline found **60/60 usable
checkpoints**, six for each overlapping track. Focused pipeline/CLI validation
passed **33 tests in 2.51 seconds** in the final command-shaped check, including
renamed-file hash reuse, copied
new-output checkpoints, prior preservation-gate rejection, same-output
rejection and CLI forwarding. The prepared full command should therefore reuse
60 stages and execute 162 new stages. The user run and post-run report/source
audit remain pending.

Closing validation passed the complete PlaylistIQ suite: **383 tests in 3.03
seconds**. The parent engine retained **54 tests in 8.06 seconds**, the 0.3.0
source distribution and wheel built successfully, and `git diff --check`
passed. These checks used synthetic/test data and did not analyze the diverse
folder.

## 2026-09-11 — P-E010 — Complete diverse-37 descriptor audit

**Decision:** P015/D052. **Kind:** user-run full descriptor execution followed
by read-only artifact, checkpoint, source-hash, performance and feature-range
audit. No agent-run audio analysis, All-In-One, catalog merge, matching,
render, provider request, cloud action, source write, or commit.

Run `descriptor-run:36f6868a7872166f75a6` started
`2026-09-11T19:41:06.588141Z` and finished
`2026-09-11T20:30:04.570454Z`, a 2,937.982-second / 48.966-minute command span.
It selected 37/37 tracks, returned zero failures, reused exactly 60 verified
baseline checkpoints, ran 162 new stages, and produced 222/222 successful
results plus 222 current-compatible checkpoints. All 37 source hashes match the
pre-analysis manifest independently after the run, and both built-in source
gates passed. Reused descriptor values exactly match the ten-track baseline.

The complete report combines 269.609 seconds of retained prior measurements
with 700.622 seconds of newly executed worker stages: 970.231 stage-wall
seconds for 10,255.194 audio seconds, 1,776.215 CPU seconds, 5.677 wall
minutes/audio hour and 43.704 projected serial minutes/100 similarly distributed
tracks. Peak RSS is 1,415.031 MB; the 35%-headroom estimate is 1.866 GB/worker,
with memory-only 8/16/32-GB limits of 3/6/12 after host reserve. The 162 new
stages used 700.622 wall and 1,260.025 CPU seconds.

The new-stage sum is close to the 12.13-minute pre-run estimate, but the command
span contains an unexplained 2,237.360-second / 37.289-minute gap outside worker
telemetry. The artifact cannot distinguish system suspension/user pause from
parent-process, model or report overhead. Add explicit discovery/hash, asset,
checkpoint, worker, report and total monotonic timers before deriving VM cost
from end-to-end elapsed time.

Quick feature audit:

- BPM spans 85.714–187.500 with median 130.435. Extremes may be musically valid
  or half/double-time estimates and need listening labels.
- Raw DEAM arousal spans 3.985–7.218 with median 5.871; deferred valence spans
  4.350–7.737. Mood heads have visibly useful spread, but remain uncalibrated.
- Danceability spans 0.204–0.9998, but 28/37 are at least 0.95 and 23/37 are at
  least 0.98. Its median 0.987 makes a strong first-version rule poorly
  discriminative on this corpus.
- Acoustic top-1 genres are electronic 24, rock 4, reggae 3, hiphop 2, house 2,
  pop 1 and chillout 1. Twelve top scores are below 0.5 and seven below 0.4.
  Encoded genre exists for 24/37 tracks. Prefer encoded/reviewed evidence;
  acoustic top-N genre should be soft evidence with abstention, not truth.
- Downbeat/beat ratios range 24.4%–37.2%; several diverse tracks exceed 30%, so
  raw grids remain outside PlaylistIQ retrieval pending rhythm review.

Performance JSON projections exactly match the strict descriptor run. Artifact
sizes are 1,448,221-byte descriptors, 300,285-byte performance JSON and
28,555-byte Markdown; checkpoints total 1,126,199 bytes. Artifact hashes are
canonical in `docs/DIVERSE_37_MANIFEST.md`. Operational extraction is accepted;
semantic accuracy and prompt-to-song relevance are not yet accepted.

## 2026-09-12 — P-E011 — D058 consumer-boundary documentation audit

P016/D058 was reconciled across the package handoff, roadmap, README,
architecture, schemas, decision log and changelog. The future Resonant host may
turn candidates into an editable playlist, but PlaylistIQ still owns only the
validated query, evidence, matches and stable IDs. Playback/download source
capabilities, persistence, archives and mixes remain outside the package.

No package code, schema version, dependency, catalog, model request, source
audio or test behavior changed, so the runtime suite was not rerun. The parent
cloud validator passed64sources/112relative links with zero errors; `git diff
--check` passed.

## 2026-09-13 — P-E012 / E052 — MAEST Discogs519 setup and one-song verification

P017/D064 adds opt-in `genre_maest`; previous six default stages and EffNet
asset groups are unchanged. Downloaded the official MAEST 519-label v2 graph
(347,996,675 bytes) and JSON card (23,232 bytes) into ignored
`output/maest-models`; both SHA-256 values are pinned in `model_assets.py`.
The integrated sigmoid node is `PartitionedCall/Identity_13`, verified against
the card and a real inference. No separate embedding/head transfer is required.

Exactly one diverse source was decoded: `(1-1)DON'T DIE YOUNG (FLP INTRO).mp3`,
SHA-256 `5a1c8259dfb0b2e97818ad5900c6cb958ca00e58171a602338bbb9ea29b4d262`.
109.583675 seconds, four patches, 519 finite scores in [0,1], ten sorted review
entries. MAEST wall 18.176 s, peak RSS 2289.000 MiB.
Metadata and MAEST completed with zero failures; all selected hashes and folder
inventory unchanged. This checks extraction, not genre correctness. The full
37-song MAEST run remains for the user. Existing diverse/house baselines were
not modified. Separate smoke output: `output/maest-discogs519-smoke`.

Resume verification reused both checkpoints without inference. Package suite:
389 passed in 2.60 s, including default isolation, averaging-before-ranking,
non-normalization and invalid/logit output rejection. `git diff --check` passed.
The sandbox initially blocked DNS/telemetry; approved download and telemetry
execution succeeded. Initial sandbox suite had 388 passes and one telemetry
OSError; the same full suite passed with the required macOS access.
No new runtime dependencies, model replacement, catalog migration or commit.
Run instructions and output semantics: `docs/MAEST_DISCOGS519.md`.

## 2026-09-13 — MAEST diverse-37 output audit and offline listening review

The user completed the MAEST run: 37 tracks, 33 successful genre estimates and
four genre failures at the 4096 MiB worker RSS limit (Rock The House, Dj Yellow,
Wildest Desire and Life Is Trippy). All 37 fresh source hashes match the saved
manifest; both run preservation gates passed. Each successful song has 519
finite probabilities and exact top-ten agreement between the two output files.
Top-one genres span 22 labels; House leads on seven songs. Tech House appears
in eight top tens. This does not establish semantic accuracy or accept genres.

User requested a lightweight standalone listening review. Generated
`packages/prompt-to-playlist/output/maest-discogs519-diverse-37/listening-review.html`
with four views, full-score expansion, filters, sorting, local playback links
and folder picker, browser-local judgments and JSON export/import. Failed
songs stay visible and are excluded from prediction charts. Build and validation
contract: `tools/genre-review/README.md`. Report is 220,365 bytes, offline, with
no external dependencies or embedded audio. No analysis rerun or model change.

Static JavaScript and isolated DOM-stub behavior checks passed (37 rows, failure
search, eight-song Tech House filter, sorting branches, four views, full 519
expansion, correct count/percentage-point units). Browser tool rejected local
file navigation; no workaround was attempted. Visual layout, actual playback,
browser storage and download/import behavior remain unverified in a real browser.

## 2026-09-14 — Preloaded listening-review repair

User could not see result files in the HTML. Added server-independent build-time
rows: 37 songs, 330 probability bars, successful songs first, and a visible
33-song ready count. Scripts enhance an already populated document instead
of being required to show results. Existing filter/view checks pass; saved
estimates and audio unchanged. Report rebuilt at 300,181 bytes.

## 2026-09-14 — Download listener notes

Added a visible “Download my notes (.txt)” button above the results. Exports
`my-genre-review-notes.txt` with filenames, accepted genres, listening notes,
source hashes and model/dataset identity. Includes every nonblank review, even
when filtered out, supports partial reviews, and prevents empty downloads.
Existing JSON export/import and browser storage remain. Isolated checks pass
for both fields, Unicode/newlines, partial notes and filter-independent export.
Browser download remains unverified; no audio or estimates changed.

## 2026-09-14 — Visible export fallback

User reports no download in Chrome/Safari; exact browser cause is unconfirmed.
Export now captures live fields, reveals copyable plain text, and clicks an
attached persistent download link (previous code clicked a detached anchor
and revoked its URL after one second). Status says download requested rather
than claiming completion. If scripts fail, the initial HTML shows an explicit
warning and disables editing/export to avoid silently unrecorded input.
Isolated handler checks pass for download request and thrown/blocked download
with notes retained. Actual browser download remains unverified.

## 2026-09-14 — Preserved owner listening judgments

Saved all 33 pasted reviews to package `docs/evaluations/maest-listener-review-2026-09-14.json`;
findings and unresolved inconsistencies are in `docs/evaluations/MAEST_LISTENER_FINDINGS.md`.
HTML now embeds these reviews via generator `--reviews PATH` and isolates
script bindings, renaming the global top helper to topScore. Syntax and
isolated checks pass; browser root cause/download behavior remain unverified.
No model replacement, accepted-tag catalog import or new audio analysis.

## 2026-09-15 — MAEST top-six and local player integration

Validation: 393 Python tests and 32 player tests pass; 17 JavaScript modules pass syntax checks. Production build verifies 16 files / 267065 bytes, manifest SHA-256 `0e9b04ecedb6448b6793e65796d1d2c8f390fd35fe83e16e297e7e5d46933443`. Browser acceptance on localhost:4181 imported one authorized real song, reused hash/model-matched saved features, showed three/six genres, displayed audio details, and made one live OpenAI request (`1 house track`) that matched its fourth-ranked House genre. Save playlist and feature persistence survived reload. A fresh generated 35-second sine exercised all seven workers: six usable stages, including all 519 MAEST scores; rhythm honestly remained partial because no beat grid was detected. No full corpus rerun. Four historical MAEST RSS failures remain unresolved; no RAM cap increase. New controls were visually checked on desktop; fresh Safari/mobile acceptance is not claimed.

## 2026-09-15 — Analysis workspace and fresh-export repair

Analyze tracks and PlaylistIQ now sit in the top controls. Feature columns toggle in the track list; the Analysis tab uses the full width with sticky track names and headers, horizontal scrolling, genre scores, tempo/key/loudness/arousal, mood/danceability/vocal scores and missing-stage details. Option 2 uses compact transport in Analysis. PlaylistIQ is a themed page with analyzed-track count, prompt form and inline results/save action; the earlier technical introductory copy is removed.

Fresh MAEST analysis could finish and then crash in `review_document`: the new top-six export referenced undefined `ordered` (NameError). The earlier generated-audio acceptance preceded that export edit and did not cover the final code; this checkpoint supersedes that acceptance claim. Cached completed records bypassed the failing code. Export now uses the result’s top-six values or its historical top-ten slice, with passed/failed regression coverage. Malformed worker JSON now becomes a failed stage instead of aborting the track. Per-source stage checkpoints persist under `output/web-features/checkpoints`, allowing retries after later failures; prior deleted temporary output cannot be recovered. Local analysis diagnostics are retained in `output/web-features/last-analysis-error.log`; provider errors remain redacted. Source audio, memory limits and the top-six/no-threshold/no-overrides rule are unchanged.

Verification: 395 Python tests and 33 player tests pass, 17 JS modules pass syntax checks. The exact failing fresh path was reproduced through localhost:4173 with a generated 31-second tone, then rerun successfully after repair: all 519 MAEST scores saved; six stages usable and rhythm explicitly partial because the tone has no beat grid. No music corpus rerun. Browser checks cover feature toggle, full-width Analysis and PlaylistIQ page in both desktop options, populated saved song features, and narrow layout. Production build: 16 files / 274471 bytes; manifest `d16a9d365bc34fdbc1f8af6ddc4ca6346545392d28c0fe21cc3cf82218d673a5`. Reload the existing player tab; Analyze tracks retries incomplete tracks while retaining completed records.

## 2026-09-15 — Playful App status and V0 listening lab

Owner requested a more expressive status page and ten varied PlaylistIQ tests with commentary capture to close local V0 before cloud work. Status now uses staggered metrics, asymmetric cards, large typography, a numbered query flow and contrasting next steps, with compact transport and responsive stacking. Maintained snapshot remains the content source.

PlaylistIQ now includes ten loadable prompts and a persistent per-attempt notebook: exact prompt, candidate identities/hashes, full query/result/error, timing, verdict and notes. Repeated tests remain separate. Export provides a Download JSON link and copyable JSON fallback. See web-player/docs/V0_LISTENING_REVIEW.md for the suite, interpretation categories and proposed closure checklist. User listening/comments and interpretation are pending; V0 is not marked complete. Cloud is the subsequent milestone; no provider execution performed.

Validation: 42 tests, 27 syntax checks and production manifest verification pass. Browser checks confirm status content, mobile width 390 with no document overflow, prompt loading and JSON export fallback. No OpenAI test calls or user verdicts generated.

## 2026-09-17 — Creative-intent planner research and YAML evaluation

Research-only evidence: inspected current genre bridge, search, translator, models,
web bridge and maintained evaluation records; reviewed primary papers and official
code/specifications. Confirmed MAEST confidence is ignored by current ranking.
Created the [full report](docs/research/PLAYLIST_PLANNER_RESEARCH_2026-09-17.md) and [digest](docs/research/PLAYLIST_PLANNER_DIGEST_2026-09-17.md); no recommendation-quality
experiment, model request, training, download or audio analysis was run. Proposed
weights, prompts, schema and model comparisons are explicitly unmeasured.

ACE-Step paper v1 is versioned; official code was inspected on main with access date,
not independently pinned to an immutable commit. Peer review corrected genre OR
versus set coverage and added typed execution/gap semantics to the proposed plan.
The board uses its revision-checked store, with generated Markdown and prior history.

Verification for this research update: both report local-link/fence checks pass; board syntax checks and all six board tests pass. Revision 41 preserves every existing action, status, step and fact, adds PIQ-020 / LATER-PIQ-YAML and appends only a scope note to the old genre-experiment card. Generated Markdown matches the canonical board. No package-runtime tests or live recommendation evaluation were rerun for documentation changes.

## 2026-09-19 — PlaylistIQ Iteration 1 delivered

Python 0.4.0 / player 0.3.0 now integrate `playlist-intent-v1.3` (configured low reasoning), `intent-compiler-v1.1`, `maest-intent-v1` ranking and `discogs-parents-v1`. Required genres use MAEST support; creative prompts use directional soft priorities. Genre OR/family matching, original-request clarification, per-track contributions and twenty-prompt review evidence are available. New result/catalog/translation/run writes use schema 0.2.0 and read historical 0.1.0.

422 Python tests and 50 web tests pass. Final compiler replay passes all 20 intent/constraint checks; live revision failures are preserved, and final optional/HTTP checks pass. Human listening acceptance remains pending. No new audio analysis or cloud work; YAML is still a consideration task.

See [implementation, prompt, contracts and verification](docs/ITERATION_1.md). This current checkpoint supersedes older descriptions of v3-only translation, flat genre ties and missing parent matching; dated older sections remain historical evidence.

## 2026-09-22 — Hybrid estimator implementation and bounded validation

Owner requested immediate implementation following research. Expanded heads and MuQ ran on exactly Listen Over the Ocean and My Paradise - Edit from the established diverse folder. Each now has 56 theme + 40 instrument scores and three timestamped MuQ embeddings; source hashes/inventory are unchanged. Expanded-head time: 3.169 / 2.972 s; MuQ time: 17.33 / 13.25 s; largest measured MuQ process-tree RSS: 2814.9 MiB. Cache retries execute zero stages. Both results were attached through normal Chrome track actions and inspected in Analysis/details.

Seven live prompt calls across three creative cases preserve v1.4/v1.5 failures and v1.6's affected-case pass. v1.4 returned Spanish retrieval text and an unavailable warm preference; v1.5 fixed language in three cases but still chose warm; v1.6 constrains the soft enum and validates it locally. Final case: matched, 17.8 s, exact hybrid replay. Final offline structured/hybrid comparisons preserve three fixed queries. Semantic-only intimacy ranking still favors the house track; no listening acceptance is claimed.

Final regression: 442 Python tests, 77 web tests, 45 JS syntax modules, verified production build (28 files, 382314 bytes; SHA-256 `0c417bc697070198c03b101a90ac0d52d400ac15661b54a61832b46ca5c56036`). Runtime, failure, asset and replay evidence: [implementation log](docs/ESTIMATOR_UPGRADE.md). Broader library upgrade and blind listener comparisons remain pending.

## 2026-09-25 — Selectable supervised feature estimators

Music2Emo (MERT-95M + BTC/chord/key + J_all, corrected mode) and MusiCNN danceability are implemented as optional direct-feature challengers. The specialist reference remains default; MAEST top-six, MuQ and ranking weights are preserved. Complete compatible catalog coverage is required per challenger; otherwise everyone retains the reference. Two authorized sources passed six matched-window stages and zero-inference retries. Final checks: 481 Python tests, 80 web tests, 45 JS syntax modules, 28-file build, 40 exact fixed-query replays and one final successful live replay. One prior live intent proposal was rejected; no new listening judgments or superiority claim.

Exactly two local cache records have both challengers. Original Chrome was observed at 109 unique tracks; its final updated display was not confirmed because native interaction was interrupted by active use. The new reload migration attaches richer same-hash optional caches to completed reference records. Isolated browser acceptance verified real values, retry, profile/scope, saved-result reopening, App Status and 390/320px controls. No batch/new-corpus inference, audio upload, cloud work, commit or format migration.

Read [research, commands, failures, coverage and continuation](docs/SUPERVISED_ESTIMATORS.md). Historical sections/publication cutoffs below remain evidence for their original dates.


## 2026-09-25 — Quality-first estimator research and implementation

Quality-first non-genre research and the selected available specialists are delivered locally. The web default selects Music2Emo theme/VA, MusiCNN vocals, VGGish aggression and independent PaSST OpenMIC instrument evidence, retaining EffNet happy/sad/relaxed/danceability. SheetSage2 supplies selected key evidence. MAEST, MuQ and planner weights remain unchanged. Two authorized sources passed 8/8 new stages; retries execute zero stages. Richer nuanced-emotion prediction and listening superiority remain unresolved; do not present encoder-only releases or the same 56 tags as solving that objective.

[Implementation, two research reports, setup, model contracts and verification](docs/TOP_ESTIMATORS_IMPLEMENTATION.md). Final validation: 502 Python tests, 83 web tests, 45 syntax modules, 28-file build, eight successful final audio stages and 26 exact fixed-query replays. No new provider calls or listener judgments. The new optional specialist stages and quality/openmic vocabulary identity preserve reference records and saved-profile replay.

## 2026-10-01 — Test music relocated; local server restarted

The owner moved the three existing test corpora into `test_music/` and created `test_music/new_albums/`. Runtime recovery and bounded smoke/attachment scripts now use the new parent; current README commands are updated. Historical analysis files retain their recorded paths and hashes. The DJ engine resolves a missing legacy corpus folder to its existing `test_music` location without changing archived evidence; existing folders always take precedence. Source-output protection includes the new music parent, and Git excludes the whole local music tree.

Server uses the existing `http://127.0.0.1:4173` origin. Models, profiles, weights and analysis behavior are unchanged. The owner will manually import new albums and launch analysis; the agent did not import or analyze music. Bulk Analyze Tracks remains the standard pipeline; Details → Upgrade selected specialists runs the newer selected models. `new_albums` is not silently included in Restore saved batch.

Validation: 11 engine/path tests and 35 export-boundary tests passed; 83 web tests, 45 JS syntax checks and the 28-file static build passed. MuQ, supervised and all four specialist model asset checks passed without inference. The active historical DJ collection resolves all ten source files at the relocated paths. Local HTTP checks passed and recovery found 54 cached originals. Server remains on port 4173. No browser import, acoustic analysis or model/provider request was run.

## 2026-10-01 — Unified default analysis delivered and verified

Owner requested selected model replacements in ordinary Analyze Tracks, retained unreplaced/additional features and both Music2Emo/EffNet moods. Implemented `selected-estimators-v2` with eleven sequential guarded stages, isolated stage failures, missing-only retry, current-cache precedence, updated primary columns and explicit comparison labels. Fresh two-track test passed 22/22 stages in 129.19/182.31 seconds; peak worker RSS 3680.4/3064.3 MiB, minimum host available RAM 2532.7/2546.3 MiB. Both retries and real HTTP analysis requests executed zero stages. Hashes/inventories unchanged. Prior cache history and retired results preserved. 505 Python + 84 web tests, 45 syntax checks and 28-file build pass. One migration test fixture needed the new version; no real inference failure. Chrome Analysis verified and left ready with 109 unique tracks. No whole-library/new-album inference, cloud activity or commit. Two-track success does not guarantee every future file; whole-machine swap increased during the test.

See the maintained default-pipeline document for exact lineup, evidence paths and limitations.

## 2026-10-01 — 120-description bank ready

Owner authorized 120 concepts, precomputed text embeddings and replacement matching that reuses audio embeddings. Delivered `musical-character-v2-120` (30 emotion / 25 groove / 25 texture / 20 intensity / 20 arrangement), independent audio cache, bank-content and audio-fingerprint score invalidation, a model-free matching path, and current-version upgrade detection. UI groups two matches per dimension and spells out seconds sampled. Playlist ranking unchanged.

All 120 text embeddings prepared in 34.38 s, peak worker RSS 1574.8 MiB. Two existing acceptance tracks refreshed in ~42 ms each; exact audio vectors and other stages unchanged, no inference, repeated requests no-op. Real HTTP route accepted current records. 516 Python / 85 web tests pass. No whole-library inference or matching was launched. See CHARACTER_BANK_120.md for full concepts, artifact paths and unvalidated listening-quality limits.

## 2026-10-01 — Analysis incident diagnosis (no repair applied)

Owner supplied an error dialog with 219 entries: one track with decoder failures and 218 entries reporting `IDBDatabase: The database connection is closing`.

- `Xxamorxx -Hot Like Latina`, SHA-256 `42dc6f974099f21209cf1770318a16feb40d9af64b5cc326f0c74e354d6a3a4c`: AAC in an M4A container. Beat This `rhythm` exhausted its Torchaudio/SoundFile/madmom decode path; SheetSage2's direct SoundFile read rejected the format. Nine of eleven current stages succeeded, including 120-description MuQ matching. Older key/energy records remain. The two failed workers peaked at 373.9 / 590.2 MiB RSS with 4349.1 / 4675.7 MiB minimum host available memory: decoder failures, not memory-guard failures.
- `Sell Me Candy`, SHA-256 `b5899c5f7523c945ade3b8314cb31f69f4ace89d3372d82d3904595fd3b0a94f`: all eleven stages completed and the current 120-description record was saved on disk at 13:38:16 local time. It is the first browser-storage error in the pasted list. Evidence supports failure in the later browser save/read step rather than inference.
- The batch loop catches every error and continues; after a closed IndexedDB connection it attempts each remaining track against the same unusable handle. This explains the cascade of 218 repeated storage errors. Code has no reconnection or batch-stop handling for this condition. The precise event that initiated connection closure is not recorded; do not claim a proven cause such as memory pressure, quota, another tab or a browser crash.
- At inspection, 120 server feature records exist: 19 current complete, one current partial, 89 older complete and 11 older partial. These are cumulative cache counts, not all new successes from this batch. No PlaylistIQ workers remain active. No inference, restart, browser-storage clearing or app code changes were performed for this diagnosis.

Recommended repairs: decode supported containers consistently through FFmpeg into temporary PCM for Beat This/SheetSage2; reconnect or pause cleanly on IndexedDB loss, preserve server-side completion and restore by hash; add AAC/M4A and connection-loss integration cases. Earlier two-track smoke covered MP3 and did not exercise these failure modes. Original audio is not written by the analysis path; disk cache existence does not by itself prove the browser database is healthy.

## 2026-10-01 — Expanded recovery after the 54-track limit

The old recovery button was deliberately restricted to cached analysis in three flat source folders; it excluded new_albums, nested albums and uncached tracks. It was not a backup of the full browser collection. The owner reported only 54 restored tracks after losing a collection of more than 200.

Recovery now recursively scans the fixed project test_music root, including new_albums, excludes symlinks, deduplicates exact SHA-256, and restores source audio even without analysis. Saved features are attached only when available; missing features are never invented. Existing source bytes are preserved so compatible analysis remains reusable; M4A conversion stays a separate owner action after recovery. Source paths remain absent from public listings. Persistent storage errors stop recovery.

Measured disk inventory: 295 audio files, 255 unique hashes, 59 with valid saved web-feature records, 196 without. With 54 already restored, the next run can add 201, subject to browser audio/storage failures. This restores all available local originals, not an exact reconstruction of the previous 237-track selection; previously unloaded files may be included. Other cached hashes without matching originals in test_music cannot supply playable audio. Playlists/preferences are not reconstructed.

Verification: 92 web tests pass, including recursive uncached recovery, symlink exclusion, hash checking and idempotence; syntax/build pass. Live endpoint reports 255 entries/59 analyzed and no source paths. Server restarted on port 4173. No owner audio imported, converted or analyzed by this repair; reload and click Restore saved batch again.
