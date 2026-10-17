# Agent takeover — DJ Collection Set Builder

## 2026-10-17 — Album artwork, local only

[Artwork checkpoint](docs/ALBUM_ARTWORK.md): embedded-first extraction, conservative MusicBrainz/CAA fallback, album/negative caches, provenance, 500/96px derivatives, post-storage local import hook and resumable backfill are implemented. Only compact library/result/minimized-player thumbnails; both spectrograms preserved. No deployment. Personal cloud upload lifecycle, private derivative delivery and physical iPhone acceptance remain pending. Transition, analysis and ranking work is unchanged.

## 2026-10-06 — Individual accounts and spectrum motion

[Account release](packages/web-player/docs/ACCOUNTS_RELEASE.md) replaces shared hosted state with email/username/password accounts, private playlists/PlaylistIQ results/listening counters, owner-only bounded analytics and a full-spectrum motion override. Google sign-in/linking is implemented but activation and real-provider acceptance await a Google web client ID. Owner authorized deployment, a test user, live-history reset and Git push. Current rollout receipt and limitations are maintained in the linked checkpoint; audio, saved analysis and planner policy are preserved.

**Read this file first.** It replaces the prior chat. Durable logs still win
on exact experiment numbers; this file is the operating brief.

- **Date:** 2026-09-09
- **Project root:** `projects/dj-collection-set-builder/`
- **Workspace:** `music-ai-projects` (DJ engine and parallel playlist package)
- **Do not start from** `AUDIO_ANALYSIS_TOOLING_REPORT.md` or parent `LOG.md`
  as live status. Those are a frozen research registry and an older problem
  log.

## Hard stops

- Never modify files in `test_folder_10_house_tracks/`. SHA-256 before/after
  must match `docs/CORPUS.md`.
- `test_tracks_folder_mp3/` is authorized only for read-only hashing and
  ffprobe metadata import into the playlist catalog (D040). Do not run heavy
  audio analysis or render that pool, or substitute it for the engine corpus.
- Never write renders, JSON, or work dirs inside the music folder.
- Never auto-render the 10 house MP3s (RAM/time). Render tests use generated
  sine WAV/MP3s in tmp.
- Do not start automatic MixPlan generation or connect a model to rendering.
  The user authorized a separate prompt-to-playlist track on 2026-09-07
  (D039); this replaces the old blanket hold on all LLM work.
- Do not swap All-In-One model/fold/demix or lower the reclaimable kill
  floor (~768 MB). That is backlog D031, not the next slice.
- Do not relabel tempo, key, beats, downbeats, or sections as facts. They
  are always `benchmark_estimate` (D003 / D014).
- Do not commit unless the user asks.
- Authority strings must be exact: `encoded_fact`,
  `standardized_measurement`, `deterministic_measurement`,
  `benchmark_estimate`, `user_verified`, `llm_proposal`, `executed_action`.

## Repository checkpoint

The user authorized the initial GitHub snapshot on 2026-09-09 (D044/E031).
The private GitHub repository is `manuelalvarezml/resonant-ai-dj`. It tracks
code, documentation, locks, compact analysis and
catalog evidence, and manifests. It excludes source MP3s, rendered WAVs,
credentials, environments, caches, and disposable work directories. Read
[`VERSIONING.md`](VERSIONING.md) before changing release or checkpoint policy.
Use append-only decision/experiment records and do not rewrite shared history.

`checkpoint-2026-09-09` is the recovery baseline. The accepted v2 audio itself
remains local; its plan, manifest, source hashes, and listening evidence are
tracked. This checkpoint does not change any audio, playlist, cloud, or model
authorization boundary.

## Where the work is

V1 is a local folder-to-mix engine in three steps:

1. Extract mixing features from owned MP3s.
2. Deterministic DJ tools (score, order, bounded FFmpeg ops).
3. LLM returns a declarative `MixPlan`; code validates and renders.

**Done:** Step 1 corpus JSON, Step 2A scoring, Step 2B clip renders and
planner lookups, the first manual MixPlan validator / `render_set` vertical
slice (D036 / E024), and the D037/E025 timing diagnosis plus
`house_eq_v1` / downbeat-click diagnostic implementation. D038/E026 records
the first user-accepted mix result: v2 transition duration and downbeat
alignment are good for the first version.

**Not done:** final-bus headroom/mastering, broad corpus-level verification of
the stored downbeats, generic `set_volume_envelope`, stretch listening tests,
automatic plan generation, Step 3.

**Parallel track (D039 / E027):** the independently installable
[`packages/prompt-to-playlist`](packages/prompt-to-playlist/README.md) package
has its own runtime dependencies, lockfile, tests, and documentation. Its
boundary is prompt → validated query → deterministic catalog matches.
Translation and catalog adapters are replaceable; neither runtime imports the
other. The first slice is implemented and independently tested (E027), with
a native desktop prompt form and CLI. D040/E028 adds the larger local pool's
metadata-only catalog and explicit OpenAI project configuration. D041/E029
corrects the old offline UI path: the desktop is OpenAI-only, discovers the
project profile within defined bounds, and exposes natural-language criteria
and missing evidence in a modern light Tk interface. The engine
can continue without this package, and this package can run
without the audio stack. Read its
[`AGENTS.md`](packages/prompt-to-playlist/AGENTS.md) and README before playlist
work. Further playlist work is paused by the user as of 2026-09-08; preserve
the implemented package and its existing evidence until explicitly resumed.

**Cloud discovery phase (D042 / D043):** `PLAN.md` records a cloud music-library
service as a product hypothesis and ordered discovery backlog. Its proposed
surface is a listenable owned-music library with descriptor browsing,
prompt-built playlists, and downloadable deterministic DJ mixes. This does not
authorize cloud implementation, uploads, accounts, hosting, remote analysis,
automatic MixPlan generation, or production rendering. D043 activates deep
research and local planning; revision 1.0 is available in
[docs/cloud-library](docs/cloud-library/README.md). Read its
[takeover](docs/cloud-library/AGENTS.md) and [status](docs/cloud-library/STATUS.md).
The desk comparison shortlists B2/R2, but selects no provider. Customer,
legal/license, portability, playback/security and economics gates remain
unpassed. The package includes proposed contracts, a cost workbook, structured
registers and append-only events; none authorizes a cloud build.

The real Step 1 JSON has no per-track semantic genre/mood/energy tags. Import
only existing evidence and provenance; do not invent tags from a filename,
the corpus's house description, BPM, or LUFS. Vocabulary terms describe a
request, not new audio measurements. Synthetic labeled examples exercise
semantic retrieval in tests. The larger pool supplies some unreviewed encoded
genre/BPM metadata with provenance and warnings (D040/E028); it does not
establish reviewed mood, energy, or vocal evidence.

## Environment

- macOS Apple Silicon, **16 GB RAM**.
- Python **3.12.10** via `uv` in `.venv`.
- FFmpeg **8.0.1** Homebrew GPL (`acrossfade`, `afade`, `volume`,
  `equalizer`, `highpass`, `atempo`). **No `rubberband` filter.**
- Essentia **`2.1b6.dev1389`** (newer wheel is cp314-only; D019).
- All-In-One MLX `harmonix-all`, Beat This `final0` on **CPU** (D026),
  `demucs-mlx[convert]`. Harmonix still runs **HTDemucs** internally;
  stems are discarded (D008).

```bash
cd projects/dj-collection-set-builder
uv run pytest -q
uv run dj-score output/step1-collection.json
uv run dj-score output/step1-collection.json --summary "01 My Paradise - Edit.mp3"
uv run dj-render --help
uv run dj-render set --analysis output/step1-collection.json \
  --plan examples/mvp-three-track-plan-v2.json \
  --out output/mvp-three-track-set-v2.wav
uv run dj-render downbeat-clicks --analysis output/step1-collection.json \
  --plan examples/mvp-three-track-plan-v2.json \
  --out-dir output/downbeat-clicks
```

Last engine test run: **54 passed** (2026-09-07). Separate playlist suite:
**363 passed** (E029; E028 had 346 and the first slice had 190 in E027).
Playlist distribution version **0.2.0** rebuilt successfully as a wheel and
source distribution. E029 also records six passing live requests and native
Tk state/geometry checks; screenshot visual QA was unavailable.
The package uses its own
Python 3.12.10 environment with Pydantic 2.13.5 and pytest 9.1.1; no audio/ML
dependencies are installed for it.

To open the playlist form from this project directory:

```bash
cd packages/prompt-to-playlist
uv run prompt-playlist ui --config playlist.toml
```

The package's `Open Playlist.command` launcher opens the same configured
form. `playlist.toml` selects the real-pool catalog, OpenAI, and the editable
snapshot `gpt-5.4-mini-2026-03-17`. It resolves only the project credential
`AUTODJ_OPENAI_API_DEV_KEY` from the environment or an explicit literal
assignment in the configured `~/.zshrc` fallback; do not execute the shell
file or copy/log the key. Normal requests send only request text, vocabulary,
and the query contract to OpenAI. See E028 for actual live checks and
coverage limits: five cases passed after a count-interpretation correction,
including Spanish genre requests, BPM sorting, unknown vocal exclusions, and
unsupported mix requests. D041 supersedes the old offline default: the desktop
uses explicit config, current-directory `playlist.toml`, then the editable
package checkout’s profile, and rejects rules mode. Generic CLI `prompt`
defaults to OpenAI; `--provider rules` is an explicit offline developer option.
The user’s “house dj set energetic” request is handled by translation policy
`playlist-query-v3`: house is required and high energy is preferred. The
catalog has eight exact house tags and no normalized energy evidence; show
that shortfall rather than claiming those tracks are energetic. All six live
v3 cases pass, including this exact request. E029 records verification,
separate from the earlier E028 checks.

The v1 plan was run by the user and rejected: both 8-bar transitions were too
short, sounded misaligned, and a pure triangular volume crossfade was not
musically sufficient. The user then ran v2 and the primary click diagnostics.
V2 is 609.100 s with two 29.090 s `house_eq_v1` transitions using My Paradise
→ Rock The House → Lemon8. The user says the second render is much better and
accepts transition duration and downbeat alignment for this first version.
This is the project's first successful listening checkpoint (D038/E026).
Manifest warning to retain: true peak is +1.04 dBTP, so final-bus headroom is
not delivery-ready.

## Corpus and artifact

Authorized folder: `test_folder_10_house_tracks` (10 house MP3s, Unicode
filenames as stored; do not renormalize).

Separate playlist pool: `test_tracks_folder_mp3`, **120 MP3s** (D040/E028).
The catalog contains embedded BPM on 22 tracks and recognized genre metadata
on 62; imported mood/energy/vocal evidence and complete-axis coverage are
absent. Raw tag-key inventories are recorded for later review. The explicit folder
adapter is authorized for hashes and ffprobe container/embedded-tag metadata
only. Its catalog and preservation/coverage manifest live under
`packages/prompt-to-playlist/output/`; see `docs/CORPUS.md` and E028.

Artifact: `output/step1-collection.json`  
Collection ID: `ed63d449-758f-4bbd-a7d7-99b0867ebcf6`  
Tracks: 10/10. Collection `failures`: 0. Source hashes match
`docs/CORPUS.md`.

| Track | LUFS | Key | All-In-One BPM | Sections |
|---|---|---|---|---|
| 01 My Paradise - Edit | -8.96 | Eb minor 2A | 133 | 25 |
| 02 For The Record | -8.99 | G minor 6A | 130 | 24 |
| 03 Fantazia | -9.37 | Bb minor 3A | 130 | 24 |
| Love State | -9.21 | B minor 10A | 130 | 24 |
| Certified | -10.53 | Bb minor 3A | 125 | 22 |
| Rock The House | -9.05 | Eb minor 2A | 133 | 24 |
| Dj Yellow | -12.87 | G# minor 1A | 120 | 25 |
| Wildest Desire | -8.78 | F major 7B | 136 | 16 |
| Lemon8 | -13.91 | F# major 2B | 133 | 32 |
| Life Is Trippy | -16.43 | D minor 7A | 128 | 16 |

Lemon8 133 BPM is slightly above the 120–130 house guess; still an estimate.

## How Step 1 actually runs

Package: `src/dj_collection_set_builder/`. CLI: `dj-analyze`.

Staged **subprocess per track**: ingest (ffprobe / loudness / key) →
All-In-One MLX → Beat This CPU. Parent stays light. Temps deleted after
each stage. Live stderr: `rss`, `reclaimable`, `swap`, `wired`.

Flags: `--resume`, `--retry-failed` (default on), `--max-tracks` (default
**1**; `0` = unlimited), `--max-worker-rss-mb` (default **7168**),
`--min-reclaimable-ram-mb` (2048 start-gate). Kill floor is
`max(768, min_reclaimable * 0.4)`. On retry, ingest and Beat This are
**reused** if present; only All-In-One re-runs (D030).

All-In-One: `harmonix-all`, `multiprocess=False`, `keep_byproducts=False`,
`mlx_in_memory=False`, `mlx_compile=False`, `ensemble_parallel=False`,
`demix_seed=1234`. Unique work dirs beside the output, not in the music
folder.

**Do not re-run the 10-track All-In-One corpus** unless the user asks.
The 16 GB Mac only finished it after ENOSPC, SIGKILL, laptop freezes,
reclaimable-floor kills, and RSS-cap kills. Worker RSS is a poor signal
during demix (Metal wired ~9–12 GB). Spectrograms ~3.5–4.7 GB RSS, scale
with duration. Raising the RSS cap to 7168 plus reuse finished Love State /
Dj Yellow / Lemon8 (peaks ~4671–4731 MB). Details: E016–E021, D028–D030.

## Step 2A — scoring (D032, D033, E022)

Code: `compatibility.py`, `story.py`, `catalog.py`, `score_cli.py`.  
CLI: `uv run dj-score output/step1-collection.json`

- Harmonic default: rekordbox Related 2 (same / relative / ±1 Camelot same
  letter). Related 3 opt-in. Missing Camelot → not a match.
- Tempo: prefer ≤2% incoming stretch, allow ≤4%, reject above, never
  auto-reinterpret half/double. Shared BPM = outgoing BPM.
- Transition weights: harmonic 0.45, tempo 0.35, phrase 0.12, loudness 0.08.
  Outside-policy harmonic **caps combined score at 0.15**.
- Phrase: 1.0 if both tracks share a usable 8- or 16-bar loop; 0.8 other
  shared loop sizes; 0.55 if both have sections; else 0.3.
- Loudness: 1.0 if ΔLUFS ≤3, then 0.75 / 0.45 / 0.2 at 6 / 10 / above.
- `propose_tempo_wave_order`: greedy climb then descend; climb length 6/10.

**Corpus observation (not a DJ-ready set):** greedy starts at Dj Yellow
120 BPM 1A. Next corpus BPM is Certified 125 (4.17% > 4%). First hop often
120→133 (9.77%, infeasible). Later Related-2 misses are capped at 0.15.

These numbers are planning heuristics, not mix laws.

## Step 2B — lookups, clips, and manual set render (D034–D038, E023–E026)

Lookups: `summaries.py` — `find_track`, `get_track_summary`,
`get_transition_windows`. Compact: no full beat arrays. Preferred loops:
8/16-bar, not crossing novelty. Downbeat anchors: first and last ~8.

CLI: `dj-score --summary TRACK` / `--windows TRACK` (id, sha256, or unique
filename).

Render: `render.py` + `render_cli.py` (`dj-render`). 32-bit float PCM at
44100 stereo. `load_track` re-hashes the source after copy. Writes into
the source folder are refused.

| Tool | Status | Bound |
|---|---|---|
| `get_track_summary` | implemented | — |
| `get_transition_windows` | implemented | — |
| `load_track` | implemented | accurate `-ss` after `-i` |
| `set_gain` | implemented | −24…+6 dB |
| `eq_band` | implemented | 120/800/4000 Hz, −18…+3 dB (`eq-crossover-v1`) |
| `low_cut` | implemented | 80–300 Hz, default 180 |
| `time_stretch` | implemented | FFmpeg `atempo`, max 4% |
| `loop` | implemented | max 8 reps, 12 ms edge fade (`loop-edge-v1`) |
| `crossfade` | implemented | 0.05–32 s `acrossfade` |
| `house_transition` | implemented | `house-eq-v1`, 180 Hz midpoint bass handoff |
| `render_segment` | implemented | single-source op list only |
| `set_volume_envelope` | **planned** | — |
| `render_set` | implemented | Manual, typed downbeat segments; PCM WAV + manifest |
| `downbeat-clicks` | implemented | centered 30 s clips from one stored rhythm grid |

`render_set` validates schema versions, ordered IDs, source paths/hashes,
allowed/excluded IDs, downbeat bounds, gain/stretch limits, consecutive
transitions, matched effective BPM, and duration tolerance. Transitions are
4/8/16-bar transitions. D037 changed overlap timing from rounded BPM math to
the outgoing segment's exact detected downbeat span and rejects adjacent-grid
drift above 70 ms. `linear_crossfade` remains available; `house_eq_v1` splits
at 180 Hz, hands bass ownership over near the midpoint, and uses broader
high-band fades. The renderer writes the final WAV atomically, measures
duration/LUFS/LRA/true peak, re-checks source hashes, and emits a
`RenderManifest`. This is the minimal manual-plan executor, not Step 3.

D038 accepts the 16-bar exact-grid duration/alignment and `house_eq_v1` as the
first house baseline for these two heard transitions. Other D034 bounds remain
initial. Rubber Band is a later quality comparison, not installed here.

## Code map

| Path | Role |
|---|---|
| `src/dj_collection_set_builder/analyze.py` | Step 1 orchestration, RAM caps |
| `track_worker.py` / `engines.py` / `memory.py` | staged workers, telemetry |
| `ingest.py` / `loudness.py` / `key_estimate.py` | stream, LUFS, key |
| `rhythm.py` | grids, loops from downbeats |
| `compatibility.py` / `story.py` | scores and tempo-wave order |
| `summaries.py` | compact planner lookups |
| `render.py` | FFmpeg clip tools |
| `set_renderer.py` | manual MixPlan validation, set execution, manifest |
| `downbeat_diagnostics.py` | centered click-overlay renders from stored grids |
| `catalog.py` / `models.py` / `constants.py` | catalog, schemas, bounds |
| `cli.py` / `score_cli.py` / `render_cli.py` | `dj-analyze` / `dj-score` / `dj-render` |
| `tests/` | schema, keys, rhythm, memory, scoring, summaries, render |
| `output/step1-collection.json` | completed Step 1 artifact |
| `packages/prompt-to-playlist/` | independent prompt/query/retrieval package; own environment and docs |

## Decisions not to relitigate

| ID | Keep |
|---|---|
| D003 / D014 | estimates stay estimates |
| D006 | Related 2 default |
| D008 | no stems in v1 |
| D009 | never modify source MP3s |
| D019 | Essentia `2.1b6.dev1389` |
| D020 | FFmpeg 8.0.1, not the report’s 9.0.1 |
| D026 | Beat This CPU, All-In-One MLX |
| D028 / D030 | RSS 7168 MB; reclaimable kill floor ~768 MB |
| D029 | staged workers + live RAM |
| D031 | All-In-One host/model/fold/demix changes are backlog |
| D033 / D034 | scoring/general render bounds remain initial unless superseded by listening |
| D035 | `AGENTS.md` is the live takeover brief; update it after work |
| D036 | manual typed MixPlan + deterministic `render_set` before Step 3 |
| D037 | exact detected-grid overlap timing + `house_eq_v1`; keep estimates labeled |
| D038 | accept v2 duration/alignment as the first heard baseline; retain +1.04 dBTP warning |
| D039 | independent playlist selection track; no engine runtime dependency or automatic MixPlan/render integration |
| D040 | larger pool metadata catalog and explicit OpenAI translation authorized; no heavy analysis/render expansion |
| D041 | natural-language desktop always uses OpenAI; explicit offline CLI only; visible semantic evidence gaps |
| D042 | cloud library is a discovery-only product hypothesis; storage research first; no cloud build authorization |
| D043 | activate comprehensive cloud research/planning and maintained agent records; no implementation authorization |

D032 (scoring-only, no render) is **superseded in part by D034**. One bounded
three-track listening success now exists; this is not corpus-wide validation.

## Next slices

### DJ engine

The v2 render and primary click diagnostics were heard and accepted as the
first successful version. Preserve its 16-bar exact-grid timing and
`house_eq_v1` defaults. The smallest remaining delivery gap is a deterministic
final-bus headroom/limiter policy because the accepted WAV measures +1.04
dBTP. After that, exercise the same baseline on a larger manual plan before
automatic planning. Do not treat one accepted three-track mix as corpus-wide
analyzer validation.

Do not start automatic MixPlan generation. Do not “fix” All-In-One RAM by
lowering the reclaimable floor.

### Prompt-to-playlist

**Paused by the user on 2026-09-08.** The first isolated package is implemented and validated (E027): desktop prompt
entry, CLI, strict translation, descriptor normalization, deterministic search,
ordered lookup, and JSON-only DJ catalog import. D040/E028 adds an explicit
metadata importer for the larger pool and the configured OpenAI workflow.
D041/E029 corrects desktop launch defaults and short natural-language requests
without changing the catalog or engine. When work resumes, collect realistic
request examples, add a reviewed source of semantic annotations, and broaden
live interpretation evaluation. Keep these two quality questions separate:
correct request interpretation and sufficient
catalog evidence. Do not infer recommendation quality from synthetic fixtures,
mocked responses, or a small live connectivity check. Keep unresolved
constraints visible and block silent partial execution. No heavy acoustic
analysis or render is needed.

### Future cloud library phase

Discovery is activated by D043. Start with
[docs/cloud-library/STATUS.md](docs/cloud-library/STATUS.md) and its registers.
The first desk-research revision is complete; empirical discovery is not.
Continue research/planning within the current scope, resolve open questions
and prepare bounded experiments. Interviews/outreach, expenditure, provider
accounts/uploads and remote audio experiments require their own explicit
authorization. The recommendation is continue discovery, no full cloud build.
The engine's headroom/manual-set work and automatic-planning hold remain.

## After you change anything

Update: this file, `README.md`, `PLAN.md`, `V1_ENGINE_PLAN.md`,
`docs/SCHEMAS.md`, `docs/CORPUS.md`, `docs/CHANGELOG.md`,
`DECISION_LOG.md`, `EXPERIMENT_LOG.md`, parent `PROJECTS.md`.
Never erase log entries; supersede them.

## Read next (only if you need depth)

1. `README.md` — human entry + commands
2. `docs/CORPUS.md` — hashes and substitution policy
3. `docs/SCHEMAS.md` — JSON contracts
4. `V1_ENGINE_PLAN.md` — architecture
5. `DECISION_LOG.md` / `EXPERIMENT_LOG.md` — D028–D041, E016–E029
6. `PLAN.md` — product north star (do not implement from it alone)
7. `AUDIO_ANALYSIS_TOOLING_REPORT.md` — research only; v1 already chose
   tools and the 10-track corpus
