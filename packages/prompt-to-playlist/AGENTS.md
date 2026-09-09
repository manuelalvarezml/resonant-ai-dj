# Prompt to Playlist — takeover

Updated 2026-09-08. Read this before changing this package. The parent
[DJ handoff](../../AGENTS.md) retains authority for music and engine work.

## Scope and status

User authorized a parallel reusable prompt-to-playlist module (parent D039).
V0.2 implements standalone Python contracts, editable descriptor vocabulary,
rules/OpenAI translators, deterministic search/lookup tools, a read-only DJ
JSON adapter, CLI and local Tkinter desktop form. D040 authorizes the user's
120-file pool for bounded metadata/hash import and their project key for live
OpenAI translation. The project profile and launcher now use that pool and
`gpt-5.4-mini-2026-03-17`. Five live smoke cases passed in P-E002 after a recorded count
interpretation fix (`playlist-query-v2`). The next user report exposed a
still-running offline window. P007 makes the desktop OpenAI-only, adds bounded
project-profile discovery, and changes generic CLI prompt defaults to OpenAI.
`playlist-query-v3` treats a direct single-genre request as required and
ordinary energy/mood as preferences. “DJ set” alone is playlist context.
The lighter, modernized Tk form exposes missing preference evidence without
requiring users to inspect technical details. All six live v3 cases passed,
including the exact user request returning eight house-tagged tracks while
high energy remains unverified. Broad language/semantic quality remains open;
see P-E003 for this fix’s actual verification: 363 tests, successful wheel/
source builds, and real Tk state/geometry checks with no extra API calls.
Screenshot visual QA was unavailable.

Further playlist development is paused by the user as of 2026-09-08. Preserve
V0.2, its artifacts and its recorded evidence; do not start the next slice
until the user explicitly resumes this package. Parent D042 registers a future
cloud music-library product hypothesis, but that does not authorize hosting,
cloud catalog integration or changes to this package.

Parent D043 now activates cloud research/planning only. Its maintained
[research package](../../docs/cloud-library/README.md) reviews these contracts
read-only and proposes a future host adapter. This does not resume playlist
implementation, make live model calls or authorize automatic mix generation.

This is an independent distribution inside the DJ repository, with its own
`pyproject.toml`, `uv.lock` and `.venv`. Do not add audio, engine, Spotify,
web-hosting or SDK dependencies to implement a small catalog operation.
Parent automatic MixPlan/render planning is still deferred; this module
returns playlist candidates and stable IDs only.

## Boundaries

- `import-folder` may read the explicitly authorized pool using bounded
  FFprobe metadata probes and streaming hashes. Results/manifests stay outside
  the source folder. Prompt/search/UI consume the saved JSON snapshot.
- No render, heavy analyzer invocation, source file writes, hidden API calls,
  playlist publication or arbitrary model-selected execution.
- The 120-file `test_tracks_folder_mp3` pool is authorized for this metadata
  workflow. No full All-In-One/Beat This/Essentia batch or corpus rendering.
- Missing genre/mood/energy/vocal labels stay missing. Do not infer them from
  BPM, LUFS, key, filename, folder name, or an LLM's knowledge.
- LLM interpretation is `llm_proposal`, not deterministic. Tool filtering,
  normalization and ranking are deterministic for fixed inputs and versions.
- Numeric/tag source evidence retains its authority/status. Rejected/unknown
  values cannot satisfy constraints. All unknown provider constraints must
  block retrieval through `unresolved`; never silently relax them.
- The explicit `playlist.toml` project profile selects OpenAI. It reads only
  `AUTODJ_OPENAI_API_DEV_KEY` from the environment or its literal assignment
  in `~/.zshrc`, with no shell execution or unrelated-key fallback. Never print
  credentials or put them in project files. The desktop uses explicit config,
  current-directory `playlist.toml`, then the editable checkout’s profile;
  discovery is UI-only. `prompt` defaults to OpenAI; offline CLI parsing uses
  explicit `--provider rules` or an explicitly selected rules profile. The
  desktop rejects rules mode instead of
  presenting grammar as natural language. Library callers choose their
  translator explicitly. Automated tests mock HTTP; `live_check` explicitly
  makes real requests. Record live results separately from unit tests.
- Preserve parent logs and accepted DJ listening findings. No commits unless asked.

## Work and validation

```sh
uv sync --locked
uv run pytest -q
uv build
uv run prompt-playlist ui --config playlist.toml
uv run prompt-playlist prompt --catalog examples/demo-catalog.json \
  --provider rules --text 'require house; prefer dark; bpm 120-130; count 3'
```

Use `README.md` for commands, `docs/ARCHITECTURE.md` for module ownership,
`docs/SCHEMAS.md` plus `models.py` for contracts, `PLAN.md` for the next slice,
and `EXPERIMENT_LOG.md` for actual verification outcomes. The implementation
coordination contract is historical, not a replacement for those documents.

After changes update this handoff, README/PLAN as relevant, schemas for
contract changes, and append decision/experiment/changelog entries. Update
the parent documentation set listed in its handoff when status or integration
boundaries change. Never rewrite previous experiment findings.

## Next slice

**Paused.** When the user resumes playlist work, the backlog is:

The pool catalog contains 120 tracks, 62 with exactly mapped genre annotations
and 22 with positive BPM metadata; eight tracks have the exact house tag.
No normalized mood/energy/vocal evidence
or complete tag axes exist. Inspect raw metadata scales and review annotations
before expanding mappings; never guess tags to improve coverage. Broaden the
six-case live evaluation with more user examples. Keep this independent of the
engine's headroom/limiter and larger manual-mix work.
