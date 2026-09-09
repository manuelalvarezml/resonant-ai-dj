# Prompt to Playlist

An independently installable Python module for turning a description into
catalog-backed playlist candidates. It lives in the DJ repository for shared
version control, but has its own dependencies, tests, schemas, and roadmap.
It does not import or require the DJ engine or audio-analysis libraries.

**Status:** V0.2 and its natural-language UI follow-up are implemented and
validated. Further playlist development is paused as of 2026-09-08; the
commands below document the preserved working package.

The parent project's [cloud discovery reports](../../docs/cloud-library/README.md)
(D043) reference this package without resuming development or changing its
runtime contracts.

## Your 120-track pool with OpenAI

Open **`Open Playlist.command`** in this directory, or run:

```sh
uv run prompt-playlist ui --config playlist.toml
```

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
classifications. The pool has no normalized mood, energy or vocal evidence
in this catalog. Some raw tags exist but their meaning/scales need review
before mapping. Three genre strings remain unmapped. Negative vocal filters
therefore return no matches instead of assuming untagged tracks are instrumental.

The catalog was built with a bounded metadata/hash import:

```sh
uv run prompt-playlist import-folder --folder ../../test_tracks_folder_mp3 \
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
