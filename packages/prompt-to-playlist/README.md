# PlaylistIQ

## 2026-10-01 — 120 character probes; audio embeddings reused

The replacement bank and all 120 text embeddings are ready. Analyze Tracks refreshes stale description scores from compatible cached audio vectors without audio inference. The current feature version is `selected-estimators-v3-character120`; the eleven estimators and playlist ranking remain unchanged. The new Musical character view groups results by dimension. Two cached-track matching tests passed with exact vector preservation; broader analysis remains a manual owner action. [Concepts, implementation, evidence and limits](docs/CHARACTER_BANK_120.md). This supersedes earlier fixed-32/bundled-matching descriptions.

## 2026-10-01 — Selected estimators are the Analyze Tracks default

The owner requested one default pipeline with selected replacements, retained unreplaced features, added instruments, and both Music2Emo and previous EffNet moods. The web bridge now requires all eleven stages under `selected-estimators-v2`. Old DEAM/key/vocal results remain readable; those replaced estimators no longer execute in ordinary analysis. MusiCNN danceability stays an optional experiment because EffNet remains the selected head. [Implementation, safety behavior and verification](docs/DEFAULT_ANALYSIS_PIPELINE.md). This supersedes earlier standard-bulk/optional-specialists descriptions. Whole-library and new-album analysis remains the owner’s next manual action.

## 2026-09-25 — Selectable supervised feature estimators

Music2Emo (MERT-95M + BTC/chord/key + J_all, corrected mode) and MusiCNN danceability are implemented as optional direct-feature challengers. The specialist reference remains default; MAEST top-six, MuQ and ranking weights are preserved. Complete compatible catalog coverage is required per challenger; otherwise everyone retains the reference. Two authorized sources passed six matched-window stages and zero-inference retries. Final checks: 481 Python tests, 80 web tests, 45 JS syntax modules, 28-file build, 40 exact fixed-query replays and one final successful live replay. One prior live intent proposal was rejected; no new listening judgments or superiority claim.

Exactly two local cache records have both challengers. Original Chrome was observed at 109 unique tracks; its final updated display was not confirmed because native interaction was interrupted by active use. The new reload migration attaches richer same-hash optional caches to completed reference records. Isolated browser acceptance verified real values, retry, profile/scope, saved-result reopening, App Status and 390/320px controls. No batch/new-corpus inference, audio upload, cloud work, commit or format migration.

Read [research, commands, failures, coverage and continuation](docs/SUPERVISED_ESTIMATORS.md). Historical sections/publication cutoffs below remain evidence for their original dates.


## 2026-09-22 — Hybrid estimator upgrade implemented

MuQ-MuLan-large now supplies local, segmented audio/text similarity; shared Discogs-EffNet supplies all 56 mood/theme and 40 instrument scores. Existing specialist estimators remain. Planner `playlist-intent-v1.6`, compiler `intent-compiler-v1.2`, schema 0.3.0 and `hybrid-semantic-v1` integrate this evidence with replayable contributions. Only descriptors with available evidence enter the planner's soft-preference enum. Historical records remain readable.

Two authorized tracks passed expanded-head and MuQ inference, source preservation and zero-inference retries. Both are attached to the existing Chrome library. Final checks: **442 Python tests, 77 web tests, 45 JS syntax modules and 28-file production build verification passed**. Seven live planner requests exposed and then corrected language/unsupported-field failures; the final affected case passed exact replay. Semantic-only intimacy ranking remains a negative quality finding, not a solved listener case.

The selected implementation is complete; the library-wide upgrade and listening acceptance are pending. Semantic fusion requires complete compatible coverage of eligible tracks. Expanded theme/instrument/valence objectives with incomplete eligible coverage are omitted for every candidate. Use the explicit Analyze Tracks / one-track upgrade actions; do not automatically rerun the whole corpus. No cloud/audio upload, rendered mix, new corpus, commit or YAML migration.

Continue from [research and decision](docs/research/ESTIMATOR_UPGRADE_2026-09-22.md), [digest](docs/research/ESTIMATOR_UPGRADE_DIGEST_2026-09-22.md) and [implementation, setup, failures and measurements](docs/ESTIMATOR_UPGRADE.md). This checkpoint supersedes older pending-bridge and four-mood-only descriptions below.

## 2026-09-19 — PlaylistIQ Iteration 1 delivered

Python 0.4.0 / player 0.3.0 now integrate `playlist-intent-v1.3` (configured low reasoning), `intent-compiler-v1.1`, `maest-intent-v1` ranking and `discogs-parents-v1`. Required genres use MAEST support; creative prompts use directional soft priorities. Genre OR/family matching, original-request clarification, per-track contributions and twenty-prompt review evidence are available. New result/catalog/translation/run writes use schema 0.2.0 and read historical 0.1.0.

422 Python tests and 50 web tests pass. Final compiler replay passes all 20 intent/constraint checks; live revision failures are preserved, and final optional/HTTP checks pass. Human listening acceptance remains pending. No new audio analysis or cloud work; YAML is still a consideration task.

See [implementation, prompt, contracts and verification](docs/ITERATION_1.md). This current checkpoint supersedes older descriptions of v3-only translation, flat genre ties and missing parent matching; dated older sections remain historical evidence.


## 2026-09-17 — Creative-intent planner research and YAML evaluation

Read the [full planner research](docs/research/PLAYLIST_PLANNER_RESEARCH_2026-09-17.md) or [reader digest](docs/research/PLAYLIST_PLANNER_DIGEST_2026-09-17.md) for the
proposed MAEST-weighted ranking, creative-intent plan, ACE-Step comparison,
retrieval methods and listening evaluation. These are research proposals; current
runtime behavior is unchanged. YAML-versus-JSON evaluation is tracked as PIQ-020.

PlaylistIQ is an independently installable prompt-to-playlist engine for
turning a description into catalog-backed local-library candidates. It lives in
the DJ repository for shared
version control, but has its own dependencies, tests, schemas, and roadmap.
It does not import or require the DJ engine or audio-analysis libraries.

Under parent D058, PlaylistIQ is the auditable proposal component inside a
broader Resonant DJ music workspace. The product is evolving from a quick local
mix tool plus this separate utility into one experience for library listening,
native and AI-assisted playlist editing, continuous set-playlist playback,
eligible-file download and later deterministic mixes. This package still
returns candidates and evidence only; the host/player owns saving, playback,
source rights and downloads.

The product name is PlaylistIQ. Compatibility identifiers stay unchanged:
directory/distribution `prompt-to-playlist`, command `prompt-playlist`, Python
package `prompt_to_playlist`, and schemas `prompt-playlist/*`.

Its structured-query boundary is intentional: **it lets us audit why each track
matched** through the saved query, matched/missing criteria, evidence
provenance, versions, digests, and stable track IDs. OpenAI interprets the
request; ordinary local code applies it to catalog evidence.

**Status:** V0.3.0 is implemented and validated. The current UI still uses the
preserved metadata-only catalog; the new no-All-In-One descriptor artifact is
not silently merged into search. The user's repaired ten-track run now has
60/60 successful stages, zero failures, 60 checkpoints, and unchanged sources.
Its complete performance report is the current house-corpus runtime baseline;
catalog integration and the later diverse-folder relevance test remain next.
The 37-track cross-genre corpus is now explicitly authorized, hashed and
complete: 222/222 stages, zero failures and exact sources. See the
[audio-feature policy](docs/AUDIO_FEATURES.md).

The full, resumable no-All-In-One descriptor pipeline takes any explicit source
folder as a variable input and writes a versioned JSON artifact plus performance
reports for later matching. Commercial licensing remains documented for future
viability but does not block this private feasibility playground.
CLAP, TF-IDF/BM25 descriptor-document matching, lightweight text embeddings,
and hybrid retrieval are recorded later experiments, not part of that next
pipeline build.

The parent project's [cloud discovery reports](../../docs/cloud-library/README.md)
(D043) reference this package without resuming development or changing its
runtime contracts.

## Analyze a folder into PlaylistIQ descriptors

Install the optional analysis environment once:

```sh
cd packages/prompt-to-playlist
uv sync --locked --extra analysis
```

The safe default processes only one discovered track:

```sh
uv run --extra analysis prompt-playlist analyze-folder \
  --folder /absolute/path/to/music \
  --output-dir output/playlistiq-descriptor-test
```

The user completed the repaired full ten-track house run on 2026-09-11 with:

```sh
uv run --extra analysis prompt-playlist analyze-folder \
  --folder ../../test_music/test_folder_10_house_tracks \
  --output-dir output/playlistiq-house-10-full \
  --all-tracks \
  --cpu-threads 4 \
  --resume
```

That execution recognized and migrated the original 0.3.0 checkpoints, reused
metadata/loudness/key/semantic/energy for every track, and executed only the
ten missing rhythm stages. Repeating the command now reuses all 60 verified
checkpoints and regenerates the reports. Never put `--output-dir` inside the
music folder.

For the authorized 37-track cross-genre run, use this exact command from this
package directory:

```sh
uv run --extra analysis prompt-playlist analyze-folder \
  --folder ../../test_music/test_folder_37_tracks_diff_genres \
  --output-dir output/playlistiq-diverse-37 \
  --reuse-from output/playlistiq-house-10-full \
  --all-tracks \
  --cpu-threads 4 \
  --resume
```

The pre-analysis audit found 37 unique hashes: ten byte-identical house
baseline tracks and 27 new tracks. `--reuse-from` validates and copies all 60
compatible prior stage checkpoints by audio hash plus pipeline/tool/model/CPU
configuration; filenames are not trusted. The completed split was 60 reused
stages and 162 new stages. `--resume` also makes this exact command safe to
repeat after interruption. The original ten-track output remains unchanged.
The house baseline linearly projects the 27 new tracks at about 12.13 minutes
of serial stage time and 1.846 GB RAM/worker with headroom; this is not a
promise for the more-diverse songs or the command's total elapsed time.
See the [immutable pre-analysis manifest](docs/DIVERSE_37_MANIFEST.md).

P-E010 audits the completed output. The command spanned 48.97 minutes, while
new worker stages totaled 11.68 minutes; the unexplained 37.29-minute gap is a
run-phase telemetry backlog item. The complete report projects 43.70 serial
minutes/100 similarly distributed tracks and observed 1,415.03 MB peak RSS
(1.866 GB with headroom). Acoustic genre and danceability remain soft/deferred
because top-1 genre collapsed to electronic for 24/37 tracks and danceability
was at least 0.95 for 28/37. Mood and raw arousal are better-separated
candidates for the deliberate catalog bridge, still subject to human review.

The command runs six sequential stages without All-In-One MLX:

| Stage | Output |
|---|---|
| `metadata` | FFprobe duration, stream/container details, restricted encoded tags |
| `loudness` | FFmpeg EBU R128 integrated LUFS, LRA, true peak and threshold |
| `key` | Essentia global key/mode, Camelot and strength estimate |
| `rhythm` | Beat This CPU beats/downbeats and BPM derived from median beat interval |
| `semantic` | One Discogs-EffNet pass feeding genre, happy, sad, relaxed, aggressive, danceability and voice/instrumental heads |
| `energy` | MusiCNN plus DEAM raw arousal; raw valence is retained but deferred from matching |

Each stage runs in a short-lived process. The parent samples process-tree wall
time, CPU seconds/utilization, peak RSS/VMS, threads, available RAM, swap, I/O
when the OS exposes it, real-time factor and exit state. The JSON report adds
per-algorithm and combined serial projections for audio hours, 100 same-length
tracks, and memory-limited workers on 8/16/32 GB hosts. These are extrapolations
from the measured machine, not VM benchmarks.

Outputs are:

- `descriptor-run.json`: strict `prompt-playlist/descriptor-run` 0.1.0 data,
  raw scores, provenance, source hashes and a normalized descriptor document.
- `performance-report.json`: complete machine-readable telemetry and projections.
- `performance-report.md`: the same operational result in a readable report.
- `.checkpoints/`: hash/version/config-verified per-track/per-stage resume data.

Models are downloaded once into `~/.cache/playlistiq/models/v1`, streamed with
a 256 MiB per-file cap, and accepted only when their pinned SHA-256 matches.
The current pinned cache is 103.60 MiB. Source audio is never written, and the
run fails its preservation gate if selected hashes or folder inventory change.

The bounded P-E006 smoke processed only `01 My Paradise - Edit.mp3` and
`02 For The Record.mp3`: 12/12 stages completed, 0 failures, 684.58 seconds of
audio took 84.23 seconds of summed stage wall time, and peak stage RSS was
1,311.4 MB. The measured serial projection is 7.38 wall minutes per audio hour,
or 70.19 minutes per 100 tracks of the same average length. Read the generated
[performance report](output/playlistiq-descriptor-smoke-2tracks-2026-09-10/performance-report.md)
for per-stage numbers. Two tracks are an integration smoke, not a capacity or
accuracy benchmark.

The user's P-E007 full command discovered 10 tracks and preserved all source
hashes/inventory, but Beat This failed to decode every MP3 because Torchaudio
2.11 required uninstalled TorchCodec and the Beat This SoundFile fallback had
been removed. The five other stages passed for all tracks. Its reported
183.72-second summed stage time, 30.62 minutes/100-track projection, and failed
rhythm timing are **partial-run numbers, not a valid complete-pipeline
projection**. The explicit `soundfile 0.14.0` dependency fixed decoding; a
one-track repair check produced 130.43 BPM, 738 beats and 185 downbeats in
9.81 seconds at 1,053.0 MB peak RSS and 220.2% CPU. P-E007 has the complete
failure audit and repair evidence.

P-E008 records the completed resume: the command itself took 95.96 seconds,
reused 50 checkpoints, ran 10 rhythm stages, and ended with 60/60 successful
stages and zero failures. The full six-stage pipeline measures 269.61 seconds
of accumulated stage wall time for 62.98 minutes of audio: 4.28 wall minutes
per audio hour and 44.93 projected serial minutes per 100 same-length tracks.
Peak stage RSS is 1,400.0 MB, or 1.85 GB with 35% headroom. Read the completed
[performance report](output/playlistiq-house-10-full/performance-report.md).

## Launch the current PlaylistIQ UI

From the repository root, run exactly:

```sh
cd packages/prompt-to-playlist
uv sync --locked
uv run prompt-playlist ui --config playlist.toml
```

On macOS, you can instead double-click **`Open PlaylistIQ.command`** in this
directory. `Open Playlist.command` remains as a compatibility launcher.

The project profile uses the imported 120-track pool, its descriptor vocabulary,
and OpenAI `gpt-5.4-mini-2026-03-17`. The description field accepts normal
language. Try “house dj set energetic”. The model translates that request into
house as a required genre and high energy as a preference; code searches the
catalog. There are eight tracks with the exact house tag. Energy is not yet
annotated, so the interface says it cannot verify that preference rather than
calling the returned tracks energetic.

`ui` uses the current directory’s `playlist.toml` when present, then the
editable package checkout’s profile. Explicit `--config` takes precedence.
This automatic discovery is limited to the desktop command; library calls
still receive a translator explicitly, and other CLI commands require
`--config` to load a project profile. The desktop only accepts OpenAI; it
never silently switches to the offline grammar. Missing configuration or
credentials produces a setup error.

The same profile works from the command line:

```sh
uv run prompt-playlist prompt --config playlist.toml \
  --text 'Dame tres canciones. Solo incluye canciones etiquetadas como dembow.'
```

`playlist.toml` stores only configuration references. The key reader uses
`AUTODJ_OPENAI_API_DEV_KEY` from the environment, or its single literal
assignment in `~/.zshrc`. It does not execute/source the shell file, modify it,
copy the key into project files, or fall back to an unrelated `OPENAI_API_KEY`.
Relative catalog/vocabulary paths resolve against the profile's directory.
To change the model, edit `openai.model` in that profile. The
[model documentation](https://developers.openai.com/api/docs/models/gpt-5.4-mini)
lists Responses and structured-output support and the pinned snapshot.

Current coverage: **120 tracks, 62 with mapped genre tags, 22 with usable
embedded BPM**. These are supplied metadata annotations, not verified audio
classifications. The pool has no normalized mood, energy, vocal, or
danceability evidence in this catalog. Some raw tags exist but their
meaning/scales need review
before mapping. Three genre strings remain unmapped. Negative vocal filters
therefore return no matches instead of assuming untagged tracks are instrumental.

The catalog was built with a bounded metadata/hash import:

```sh
uv run prompt-playlist import-folder --folder ../../test_music/test_tracks_folder_mp3 \
  --vocabulary pool-vocabulary.json --out output/pool-catalog.json \
  --manifest output/pool-import-manifest.json
```

Those files already exist. Imports/exports refuse overwrites; use new names for
a refresh, review the new manifest and update the profile's catalog path.
FFprobe is required only for folder import (8.0.1 verified here). The command
does not run the DJ analyzers or render audio. It checks all source hashes and
directory inventory before publishing a catalog; changed sources produce a
diagnostic manifest and failure. Every track ID maps back to a source path in
the local manifest. No music files are modified.

Six live OpenAI checks pass on this pool: the user’s short natural-language
house/energy request, English count/genre, Spanish genre, BPM bounds/order,
negative evidence and unsupported mixing requests. This is a small smoke
evaluation, not a broad language or recommendation benchmark. See
[validation results](EXPERIMENT_LOG.md). An explicit live rerun makes six real
requests and writes a new report:

```sh
uv run python -m prompt_to_playlist.live_check --config playlist.toml \
  --out output/openai-live-check-new.json
```

That command makes six live provider requests. It is not required merely to
launch the UI, and it does not analyze audio.

## Library and offline developer examples

From this directory:

```sh
uv sync
uv run prompt-playlist prompt --catalog examples/demo-catalog.json \
  --provider rules --text 'require house; prefer dark; bpm 120-130; count 3'
uv run prompt-playlist search --catalog examples/demo-catalog.json \
  --query examples/house-query.json
uv run prompt-playlist tools
uv run pytest -q
```

Omit `--text` for an interactive prompt. The demo catalog contains fictional
tracks with explicitly authored example tags. It is not evidence about the
ten real house tracks.

`ui` opens a light desktop interface with a natural-language description
field, visible OpenAI status, candidate titles/artists/BPM, plain-language
criteria and JSON export. Missing preference evidence is visible alongside
results; detailed provenance is available on demand. It requires a Python
build with Tkinter (Tk 8.6.13 is installed here); the library and CLI do not.
The interface uses the standard library, adds no browser or UI dependency,
and keeps model requests off the UI thread.

## Natural-language interpretation

Outside this project profile, `prompt` defaults to OpenAI. Configure
`OPENAI_API_KEY` and `OPENAI_MODEL` in your shell, or supply your own explicit
`--config` profile. The model is an explicit setting, so each host can choose one
available to its account. `.env.example` documents the variables; no `.env`
file is loaded automatically. Never put a key in source files or CLI arguments.

```sh
uv run prompt-playlist prompt --catalog examples/demo-catalog.json \
  --provider openai --text 'Find three dark house tracks between 120 and 130 BPM'
```

One bounded Responses API request translates the text. Only the user request,
descriptor vocabulary and query contract leave the process. Track names, paths,
audio and the catalog are not sent. There is no model-chosen tool loop.
Code validates the proposal and runs the same deterministic search tool that
other agent hosts can call directly. Provider failures are explicit; there is
no automatic fallback or retry. API integration has offline boundary tests and
the bounded live pool evaluation above; broader language-quality evaluation
remains open.

The adapter uses [OpenAI structured outputs](https://developers.openai.com/api/docs/guides/structured-outputs)
and handles refusals, incomplete output and invalid proposals. Schema adherence
does not establish correct interpretation of a user's intent.

The `rules` provider remains an explicitly selected offline grammar parser
for development: `--provider rules` (or an explicit rules profile) with
`require house; prefer dark; exclude vocal; bpm 120-130; count 5`. It is not
available in the desktop form and is never a fallback for a model error.
Ordinary user descriptions need no semicolons or syntax.

The current translation policy (`playlist-query-v3`) treats a direct request
for a single genre, such as “house dj set”, as a required genre. Ordinary
energy and mood descriptions are preferences unless explicitly mandatory.
“DJ set” alone describes the playlist context; an explicit request for
rendering, transitions or a fixed mixed duration is still unsupported and
requires clarification. Missing catalog evidence does not prevent interpreting
a supported descriptor, but it can prevent satisfying it in retrieval.

## Reuse and integration

```python
from pathlib import Path
from prompt_to_playlist.adapters import load_catalog
from prompt_to_playlist.service import build_playlist
from prompt_to_playlist.translators import RulesTranslator
from prompt_to_playlist.vocabulary import load_vocabulary

run = build_playlist(
    "require house; prefer dark; count 3",
    load_catalog(Path("examples/demo-catalog.json")),
    load_vocabulary(),
    RulesTranslator(),
)
print(run.model_dump_json(by_alias=True, indent=2))
```

Consumers need only the catalog and query contracts. Replace the translator
to change LLM provider, the catalog adapter to change music source, or the
vocabulary JSON to change descriptors. `--vocabulary FILE` supplies a custom
vocabulary. No database, vector store, agent framework, Spotify connection,
or rendering dependency is required for this slice.

A Resonant host may turn the returned stable IDs into a user-editable playlist,
but it must resolve each source's separate playback/download capabilities. A
track that an official provider can play in-app is not automatically eligible
for whole-playlist audio download. Playlist archive creation and its ellipsis-
menu UX therefore stay outside this package.

To use the completed DJ analysis without reanalyzing any audio:

```sh
uv run prompt-playlist import-dj --analysis ../../output/step1-collection.json \
  --out output/dj-catalog.json
uv run prompt-playlist prompt --catalog output/dj-catalog.json \
  --provider rules --text 'bpm 130-133; count 5'
```

The adapter preserves stable track IDs and tempo provenance. It intentionally
does not invent mood, energy, genre, or vocal labels. A genre-required query
against this untagged snapshot returns no matches. Tag enrichment is a separate
catalog responsibility; human-reviewed annotations or a future analyzer can
produce the same `TagEvidence` contract without changing search or the LLM.

To reuse the distribution elsewhere, install its directory with `uv add
/absolute/path/to/prompt-to-playlist`, or run `uv build` and install the wheel.
The packaged default vocabulary works without the original source checkout.

## Guarantees and limits

- All required tags and BPM bounds must have usable evidence. Negative-tag
  filters also require complete coverage of the relevant tag axis.
- Preferred tags rank candidates and may remain unsatisfied; results say so.
- Stable ID tie-breaking and versioned ranking make identical inputs replayable.
- Scores describe tag coverage, not musical quality or confidence.
- Unknown values remain unknown. BPM/loudness never become mood or energy.
- Candidate order is relevance or BPM sorting, not a validated DJ mix order.
- Set duration, transitions, harmonic sequencing, artist-history and era filters
  are not supported in this release. Free-text requests for these must be unresolved.
- Exports are new JSON files; existing files, audio destinations and music
  directories are refused. Catalog IDs are retained; source paths are omitted.

See [AGENTS.md](AGENTS.md), [architecture](docs/ARCHITECTURE.md),
[schemas](docs/SCHEMAS.md), [roadmap](PLAN.md), and [validation log](EXPERIMENT_LOG.md).

## 2026-09-13 — Optional MAEST genre comparison

`genre_maest` is an opt-in parallel genre estimator; existing EffNet/Jamendo
and six-stage defaults are preserved. Setup and the one-song smoke are complete;
the user runs the full 37 songs. See [command and review format](docs/MAEST_DISCOGS519.md).

## 2026-09-13 — MAEST listening-review checkpoint

The user-run MAEST diverse-37 output has 33 genre results and four RAM-limit
failures; fresh source hashes all match. A standalone `listening-review.html`
is now beside those outputs. See the DJ project’s `tools/genre-review/README.md`
for regeneration, review semantics and verification limits. No audio analysis
was rerun. The earlier “full run not executed” checkpoint is superseded by
this audit; no genre-quality acceptance or model replacement is implied.

## 2026-09-15 — MAEST top-six and local player integration

Owner-authorized `maest-top6-v1` now replaces legacy genre estimation: match the top six, display three expandable to six, retain all 519 scores, and apply no probability threshold or human review overrides. Historical outputs remain preserved. The low-priority board card `PIQ-GENRE-TOP6-REVISIT` is Later / could; further genre experimentation is not a launch blocker.

The local web player now provides **Analyze tracks** and **Create with PlaylistIQ**. Its loopback Node job service invokes the existing Python environment; analysis persists by source hash and in IndexedDB, and prompt results save into normal playable playlists. Restart the player server on the same origin/port to retain the browser library. This explicit integration authorization supersedes older local bridge/Python-edit holds; cloud deployment, remote audio processing and automatic MixPlans remain deferred.

See [integration contract](docs/WEB_INTEGRATION.md).

## 2026-09-15 — Analysis workspace and fresh-export repair

Analyze tracks and PlaylistIQ now sit in the top controls. Feature columns toggle in the track list; the Analysis tab uses the full width with sticky track names and headers, horizontal scrolling, genre scores, tempo/key/loudness/arousal, mood/danceability/vocal scores and missing-stage details. Option 2 uses compact transport in Analysis. PlaylistIQ is a themed page with analyzed-track count, prompt form and inline results/save action; the earlier technical introductory copy is removed.

Fresh MAEST export NameError fixed; persistent checkpoints and invalid-worker-output recovery added. See the player WORK_LOG and PlaylistIQ WEB_INTEGRATION for evidence and retry instructions.


## 2026-09-25 — Quality-first estimator research and implementation

Quality-first non-genre research and the selected available specialists are delivered locally. The web default selects Music2Emo theme/VA, MusiCNN vocals, VGGish aggression and independent PaSST OpenMIC instrument evidence, retaining EffNet happy/sad/relaxed/danceability. SheetSage2 supplies selected key evidence. MAEST, MuQ and planner weights remain unchanged. Two authorized sources passed 8/8 new stages; retries execute zero stages. Richer nuanced-emotion prediction and listening superiority remain unresolved; do not present encoder-only releases or the same 56 tags as solving that objective.

[Implementation, two research reports, setup, model contracts and verification](docs/TOP_ESTIMATORS_IMPLEMENTATION.md). Final validation: 502 Python tests, 83 web tests, 45 syntax modules, 28-file build, eight successful final audio stages and 26 exact fixed-query replays. No new provider calls or listener judgments. The new optional specialist stages and quality/openmic vocabulary identity preserve reference records and saved-profile replay.
