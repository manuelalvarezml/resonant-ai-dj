# DJ Engine Experiment and Learning Log

Append results chronologically. Record failures and partial results; do not
rewrite history to make experiments appear successful.

## 2026-08-31 — E001 — Initial workspace and corpus inspection

### Goal

Verify project state before creating the v1 environment.

### Observations

- The project contained only `PLAN.md`,
  `AUDIO_ANALYSIS_TOOLING_REPORT.md`, `.DS_Store`, and two track directories.
- `test_tracks_folder_mp3` is populated with approximately 120 MP3 files.
- `test_folder_10_house_tracks` exists but contains zero files.
- Workspace file indexing did not expose the MP3s, but direct directory
  inspection confirmed the 120-track folder and empty 10-track folder.
- The workspace root is not a git repository.

### Environment

- Architecture: Apple Silicon `arm64` from prior research.
- `uv`: 0.10.8.
- System Python: 3.13.7.
- FFmpeg: 8.0.1 Homebrew build.
- FFmpeg build enables GPL components and Apple VideoToolbox/AudioToolbox.

### Decision / learning

- Do not silently copy or guess ten house tracks from the full collection.
- Build Step 1 and test empty-folder behavior while waiting for the intended
  ten tracks.
- Capture the actual installed FFmpeg version in results rather than pretending
  the latest researched release is installed.
- Use `uv` with a project-selected Python version instead of depending on the
  system Python.

### Current blocker

The requested real-corpus run cannot complete until
`test_folder_10_house_tracks` contains the intended audio files.

## 2026-08-31 — E002 — Harmonic compatibility source check

### Goal

Choose the first deterministic key-matching policy for Step 2.

### Sources checked

- AlphaTheta rekordbox Traffic Light:
  https://support.alphatheta.com/en-us/articles/8113187558553
- Mixed In Key Camelot workflow:
  https://mixedinkey.com/workflows/how-to-use-the-camelot-wheel/
- Essentia KeyExtractor:
  https://essentia.upf.edu/reference/std_KeyExtractor.html
- Essentia high-resolution HPCP tutorial:
  https://essentia.upf.edu/tutorial_tonal_hpcpkeyscale.html

### Findings

- rekordbox exposes Same Key and Related Key 1–3.
- Its official 2A example expands as:
  - Same: 2A.
  - Related 1: 2A and 2B.
  - Related 2: add 1A and 3A.
  - Related 3: add 1B and 3B.
- Standard Camelot safe moves are same code, same number/opposite letter, and
  ±1 number on the same letter.
- Essentia supports a 36-bin HPCP and an `edma` key profile designed for
  electronic dance music.

### Decision / learning

- Use rekordbox Related 2 behavior as the v1 default harmonic-compatible set.
- Store a standard key as canonical and derive Camelot/Open Key labels.
- Keep key confidence and allow unknown; compatibility is meaningless when the
  source estimate is weak.

## 2026-08-31 — E003 — Reconcile current project and corpus state

### Goal

Verify stale planning facts before the documentation-only architecture review.
Do not install packages, mutate the environment, analyze audio, or implement
source code.

### Read-only checks

- Direct directory listing of `test_folder_10_house_tracks`.
- `git status --short --branch`.
- `git rev-parse --verify HEAD`.
- Read existing plans, logs, tooling report, project metadata, and stub source.

### Observations

- `test_folder_10_house_tracks` contains exactly 10 MP3 files plus `.DS_Store`.
- The exact track manifest is recorded in `docs/CORPUS.md`.
- The broader `test_tracks_folder_mp3` still exists but was not inspected,
  substituted, or analyzed during this documentation pass.
- Git is initialized on branch `main`.
- Git reports `No commits yet on main`; `HEAD` does not resolve.
- Project files are currently untracked.
- `README.md` existed but was empty.
- `pyproject.toml`, `uv.lock`, `.python-version`, `.venv`, and the source package
  already exist.
- The source package remains a stub; no Step 1 analyzer or tests were found.
- Current declared Python requirement is `>=3.12`.
- Current declared packages include All-In-One MLX, Beat This, librosa, NumPy,
  Pydantic, pyloudnorm, SoundFile, and Typer.
- Essentia is selected in the plan but absent from declared dependencies.
- FFmpeg is a system dependency and is not represented by the Python lockfile.

### Corrections to earlier observations

- E001's empty 10-track folder was true when observed but is now superseded.
- E001's “workspace root is not a git repository” no longer describes the
  project directory; Git has since been initialized.
- The immediate action “create the uv project” is stale because the scaffold
  already exists.

### Learning

Filesystem/index visibility is not reliable for binary corpus discovery. Direct
directory inspection is required before declaring an audio folder empty.

Existing scaffolds must be audited before recreation. Presence of a lockfile or
virtual environment is not evidence that selected native/ML dependencies import
together successfully.

### Result

Documentation blocker removed. Build remains intentionally blocked on explicit
user approval.

## 2026-08-31 — E004 — Plan and schema consistency audit

### Goal

Compare `PLAN.md`, `V1_ENGINE_PLAN.md`, the tooling report, logs, project
metadata, corpus state, and the requested three-step product flow.

### Inconsistencies found

- Original two-phase language competed with the new three-step architecture.
- Original Phase 1 still suggested genre, mood, and energy while the strict
  tooling report rejects them as authoritative calculated facts.
- Authority terms differed across documents.
- Structural sections and exact DJ loops were conflated.
- Harmonic and tempo compatibility were grouped into one transition score.
- The plan said to create an environment that already exists.
- The 120-track research corpus and 10-track V1 corpus were not clearly
  separated.
- LLM access to the Step 2 tool catalog was described conceptually but lacked a
  named interface.
- Schema object names existed, but field-level contracts and examples did not.
- README onboarding and document-change tracking were missing.

### Documentation changes made

- Reframed `PLAN.md` as product north star and `V1_ENGINE_PLAN.md` as the
  implementation source of truth.
- Added explicit phase-to-step mapping.
- Added canonical authority vocabulary.
- Added `docs/SCHEMAS.md`, `docs/CORPUS.md`, and `docs/CHANGELOG.md`.
- Populated `README.md`.
- Split `score_harmonic_match`, `score_tempo_match`, and `score_transition`.
- Added a downbeat-derived loop-candidate strategy.
- Added `list_available_dj_tools`, `get_track_summary`, and
  `get_transition_windows` to the planner boundary.
- Recorded unverified dependency and processing decisions as open questions
  instead of guessed constants.
- Updated the parent project registry and tooling report corpus note.

### What was deliberately not done

- No `uv sync`.
- No package installation or removal.
- No import/compatibility test.
- No FFmpeg invocation.
- No audio decode, feature extraction, or source hashing.
- No Python source implementation.
- No test creation or execution.
- No commit.

### Learning

The documentation must distinguish:

- Product value from measurable truth.
- Section labels from loop-safe timing.
- Harmonic compatibility from tempo feasibility.
- Planner proposals from deterministic operations.
- Existing files from verified working infrastructure.

### Next action

Await user review and approval. After approval, begin with a read-only audit of
the existing environment and record all compatibility results before changing
dependencies.

## 2026-08-31 — E005 — Documentation directory creation retry

### Goal

Create the `docs` directory for the schema, corpus, and changelog documents.

### Failure

The first `mkdir -p docs` process produced no output and remained running for
approximately 40 seconds, which is abnormal for a local directory operation.

### Response

- Inspected the running process state.
- Terminated the hung process safely.
- Confirmed the directory had not been created.
- Retried with `mkdir docs`.
- Retry completed successfully in under one second.

### Learning

Even trivial commands can stall because of transient shell/process behavior.
Do not repeat a hanging command blindly. Inspect state, stop it safely, confirm
the filesystem result, and then retry the smallest operation.

### Impact

No project data was lost or modified beyond the intended creation of `docs`.

## 2026-09-03 — E006 — Environment audit after build approval

### Goal

Audit the existing `uv` scaffold instead of recreating it, then confirm the
Python, FFmpeg, and declared-package baseline before writing Step 1 code.

### Commands / observations

- `.python-version` pins `3.12`.
- `.venv` uses Python 3.12.10 (conda-forge). System Python is 3.13.7 and was
  not used.
- `uv` 0.10.8.
- FFmpeg/ffprobe 8.0.1 at `/opt/homebrew/bin`; `ebur128` and `loudnorm`
  filters are present. This is the Homebrew GPL build, not the tooling
  report's 9.0.1.
- Declared imports succeeded in the existing venv: numpy 2.5.2, librosa
  1.0.0, soundfile 0.14.0, pyloudnorm 0.2.0, pydantic 2.13.5, typer 0.27.2,
  allin1_mlx 1.0.6, beat_this. First combined import took ~35 seconds.
- Git is initialized on `main` with no commits. No commit was created.
- The package was still a stub (`Hello from dj-collection-set-builder!`).
- Essentia was not declared in `pyproject.toml` at audit time.

### Learning

Keep the existing venv. Pin runtime versions from the machine, not from the
tooling report. Do not use system Python 3.13.

## 2026-09-03 — E007 — Essentia install pivot

### Goal

Install Essentia `KeyExtractor` for the selected `edma` / `hpcpSize=36`
key path.

### Failure

`uv add essentia` resolved to `2.1b6.dev1438`, which only publishes a
`cp314` macOS arm64 wheel. Install aborted:

```
Distribution essentia==2.1b6.dev1438 can't be installed because it doesn't
have a source distribution or wheel for the current platform
hint: You're using CPython 3.12 (cp312), but essentia only has wheels with
the Python implementation tag: cp314
```

### Pivot

PyPI scan of macOS arm64 wheels:

- `2.1b6.dev1110`: cp39/cp310/cp311 only
- `2.1b6.dev1177`: includes cp312, macosx_11_0
- `2.1b6.dev1389`: includes cp312, macosx_15_0
- `2.1b6.dev1438`: cp314 only

Installed `essentia==2.1b6.dev1389` and `pytest==9.1.1`.
`import essentia` reports `2.1-beta6-dev`. `KeyExtractor` accepts
`profileType="edma"`, `hpcpSize=36`, `sampleRate=44100`.

### Learning

Do not follow “latest Essentia” on this Python. The newest wheel dropped
cp312. Record the pin; a later Python upgrade could reverse this.

## 2026-09-03 — E008 — Step 1 unit tests

### Goal

Lock schema, Camelot/Open Key, rhythm diagnostics, and empty-folder CLI
behavior before the 10-track run.

### Result

`uv run pytest -q` → 12 passed.

Fixes found while testing:

- A Typer group/callback CLI treated the folder path as a subcommand.
  Replaced with a single-command Typer app so `dj-analyze FOLDER --out FILE`
  works.
- Writing `--out` inside the source folder is rejected. The empty-folder CLI
  test must place JSON outside the music directory.

### Learning

Keep analysis artifacts outside the corpus folder in tests and in the real
run. That matches D009 / corpus policy.

## 2026-09-03 — E009 — One-track smoke test failed, then rerun

### Goal

Run one corpus track through the full Step 1 pipeline before the 10-track
job, using a symlink so source files stay untouched.

### Command

```
uv run dj-analyze output/smoke-input --out output/step1-smoke.json --expected-count 1
```

### Failure

Exit 0 with a collection JSON, but zero tracks. Collection warning:

`Partial failure for 01 My Paradise - Edit.mp3: name 'STATUS_NOT_RUN' is not defined`

Cause: `probe_stream` set `decode_health=STATUS_NOT_RUN` without importing
the constant. Beat This still downloaded `final0.ckpt` (77.3 MB) and selected
`device=mps`. All-In-One never ran because the track pipeline aborted at
ffprobe normalization.

The collection was preserved (partial-failure path worked). Source MP3s were
not modified.

A follow-up test failure: removing an unused-looking `shutil` import from
`ingest.py` broke `require_ffmpeg()` (`shutil.which`). Restored the import.

### Fix

Import `STATUS_NOT_RUN` in `ingest.py`. Keep `shutil`. Re-run the smoke test.

## 2026-09-03 — E010 — Smoke rerun: loudness/key/Beat This work; All-In-One blocked

### Goal

Confirm the STATUS_NOT_RUN fix and measure which engines actually complete.

### Result

- Source SHA-256 unchanged (`c4fa9722…`).
- Stream: mp3, 339.576 s, decode_health `passed`.
- Loudness: integrated -8.96 LUFS, pyloudnorm difference 0.009 LU, LRA
  difference 0.065 LU. Validator passed → `standardized_measurement`.
- Key: Eb minor / Camelot 2A / strength 0.806. Still `benchmark_estimate`.
- Beat This: `device=mps`, return order `postprocessor-beats-then-downbeats`,
  738 beats / 185 downbeats, derived tempo 130.43 BPM.
- All-In-One MLX failed immediately:

  `Model conversion requires the [convert] extras. Install with: pip install 'demucs-mlx[convert]'`

  Runtime was ~44 s because demix never started.

### Pivot

Installed `demucs-mlx[convert]`, which pulled `demucs==4.1.0` plus julius,
lameenc, safetensors, sphn. Torch was already present via Beat This.

This is a first-run weight-conversion dependency, not a replacement for the
All-In-One analyzer choice.

## 2026-09-03 — E011 — Combined smoke stalled after HTDemucs conversion

### Goal

Re-run the one-track smoke after installing convert extras.

### Observation

The CLI printed conversion success (`htdemucs.safetensors`, 160.2 MB) and
`Analyzing 01 My Paradise - Edit.mp3: 0%`, then the process vanished. No new
JSON was written. PID was gone; source MP3s were unchanged.

### Interpretation

Beat This had already been loaded on MPS in that process. All-In-One then
used MLX/Metal for demix. Sharing those backends in one process is the
leading failure hypothesis.

## 2026-09-03 — E012 — Isolated All-In-One MLX success

### Goal

Run `allin1_mlx.analyze` alone on `01 My Paradise - Edit.mp3`.

### Result

- ~70 s after weights were already converted.
- BPM 133 (int from the model).
- 732 beats, 183 downbeats, 25 segments.
- JSON written under `output/allin1-debug/`, not in the music folder.
- Source folder still contains only the original 10 MP3s plus `.DS_Store`.

### Decision affected

D026: keep Beat This on CPU in the combined pipeline.

## 2026-09-03 — E013 — Combined smoke completed All-In-One then crashed on sections

### Goal

Re-run the one-track CLI with Beat This on CPU.

### Result

- Beat This device: cpu.
- All-In-One finished in 53.58 s.
- Process wrote JSON with exit 0, but zero tracks.
- Failure: `'Segment' object is not subscriptable`.

### Cause

`getattr(segment, "start", segment["start"])` evaluates the default argument
even when the attribute exists. All-In-One returns dataclass `Segment`
objects, which are not mappings.

### Fix

Read dataclass attributes or dict keys without evaluating a subscript
default. Re-run smoke, then the 10-track corpus.

## 2026-09-03 — E014 — Combined one-track smoke succeeded

### Command

```
uv run dj-analyze output/smoke-input --out output/step1-smoke.json --expected-count 1
```

### Result (~86 s)

- Source hash unchanged.
- Loudness -8.96 LUFS, pyloudnorm ΔI 0.009 LU, ΔLRA 0.065 LU →
  `standardized_measurement`.
- Key: Eb minor / 2A / 7m / strength 0.806 → `benchmark_estimate`.
- All-In-One: 133 BPM (int), 732 beats, 183 downbeats, 25 sections
  (intro/verse/chorus/outro).
- Beat This CPU: 130.435 BPM from intervals, 738 beats, 185 downbeats.
- Consensus: BPM difference 2.57, `agrees_within_tolerance=false`.
- Event agreement is still high: beat F1 0.996, downbeat F1 0.995, no phase
  warning. Integer All-In-One BPM and interval BPM can diverge from Beat
  This even when the grids match.
- Loop candidates: 672 total, 109 `passed` (in-section, engines agree),
  563 `warning`, 0 `rejected`.
- Beat This return-order heuristic chose `postprocessor-beats-then-downbeats`.

### Learning

Do not treat BPM consensus as a proxy for beat-grid quality. Store both.

## 2026-09-03 — E015 — 10-track in-process run killed (exit 137)

### Command

```
uv run dj-analyze test_folder_10_house_tracks --out output/step1-collection.json --expected-count 10
```

### Result

- Track 1 completed (~72 s All-In-One).
- Track 2 completed (~71 s).
- Track 3 (`03 Fantazia.mp3`) started, then the process was killed (exit 137)
  after ~5 minutes total. That code is SIGKILL; OOM is the likely cause.
- Warning: `resource_tracker: There appear to be 1 leaked semaphore objects`.
- No collection JSON was written because the parent only dumped at the end.
- Source MP3s were not modified.

### Pivot

D027: subprocess per track, incremental JSON, `--resume`.

## 2026-09-03 — E016 — Isolated 10-track run paused after laptop hard restart

### Goal

Finish `test_folder_10_house_tracks` with one subprocess per track and
incremental `output/step1-collection.json`.

### Machine state after restart

- No `dj-analyze` / All-In-One / Beat This process running.
- Data volume ~99% full (~5.3 GB free before cleanup).
- High swap history from the previous session (millions of swapouts).
- User had to hard-restart because RAM was exhausted.

### Partial result saved

`output/step1-collection.json` (collection `ed63d449-…`, 7 of 10 tracks):

| Track | Loudness | Key | Tempo source | All-In-One | Source unchanged |
|---|---|---|---|---|---|
| 01 My Paradise - Edit | -8.96 LUFS pass | Eb minor 2A | 133 all-in-one | 25 sections | yes |
| 02 For The Record | -8.99 LUFS pass | G minor 6A | 130 all-in-one | 24 sections | yes |
| 03 Fantazia | -9.37 LUFS pass | Bb minor 3A | 130 all-in-one | 24 sections | yes |
| Demi Riquisimo, CLINT - Love State | -9.21 LUFS pass | B minor 10A | Beat This 130.43 | failed: disk full (ENOSPC) | yes |
| Demi Riquísimo - Certified | -10.53 LUFS pass | Bb minor 3A | 125 all-in-one | 22 sections | yes |
| Demi Riquísimo … Rock The House | -9.05 LUFS pass | Eb minor 2A | 133 all-in-one | 24 sections | yes |
| Laroze - Wildest Desire | -8.78 LUFS pass | F major 7B | 136 all-in-one | 16 sections | yes |

Missing / incomplete:

- `Dj Yellow Ft Marlene - Je Tm.mp3` — worker killed (`exited -9`).
- `Lemon8 - Triple Funk.mp3` — started in the log, not in the JSON.
- `Life Is Trippy (Original Mix).mp3` — not started.
- Love State's All-In-One JSON write hit `Errno 28 No space left on device`.
  Loudness, key, and Beat This for that file did complete.

### Cleanup (safe, no analysis)

Deleted leftover `output/.dj-engine-work/` (~563 MB of demix/PCM temps).
Collection JSON and smoke JSON were kept. Disk recovered to ~5.9 GB free
and is still ~99% full.

### Decision / learning

Do **not** resume All-In-One on this machine until there is clear RAM and
disk headroom. The remaining three tracks plus a Love State All-In-One
retry would load HTDemucs/MLX again. Disk-full plus Metal/MLX already
caused ENOSPC, SIGKILL, and a hard restart.

## 2026-09-03 — E017 — Disk recovered; resume under a RAM cap

### Disk

About 17 GB free on the Data volume. That is enough for the remaining
tracks if per-track temp dirs are deleted after each file (~50–120 MB
each, not gigabytes).

### RAM

Host is 16 GB. Before resume: ~62 MB truly free, ~3949 MB reclaimable,
~5469 MB in the compressor. Cursor/Chrome/ChatGPT are already large.
RAM, not disk, is the risk.

### Policy used for the resume

D028: 3584 MB worker RSS cap, 2048 MB start-gate, delete temps after
each track, retry failed All-In-One, pause between tracks.

### Resume result (stopped to protect RAM)

All-In-One demix on Love State dropped reclaimable RAM from ~3966 MB to
**467 MB** in seconds. Worker process RSS was not a reliable signal
(Metal/GPU allocations). The guard killed the worker. After the kill,
reclaimable RAM recovered to ~7068 MB.

The parent was then stopped so it would not keep launching workers.

Bug: `--retry-failed` removed Love State's previous partial record
(loudness/key/Beat This) from the JSON before the retry succeeded. That
track is no longer in `step1-collection.json`. Code now restores the old
record if a retry is killed.

No further All-In-One launches until the user has more spare RAM or
closes other heavy apps (Chrome, ChatGPT, Cursor extras).



`--resume` can skip the six completed hashes later. Love State still
needs an All-In-One retry because it is no longer in the JSON.

## 2026-09-03 — E018 — Staged one-track pipeline (no corpus All-In-One)

### Change

Implemented D029: ingest, All-In-One, and Beat This each run in their own
subprocess. Temps are deleted after each stage. `--max-tracks` defaults to
1. Live stderr lines report worker RSS, peak RSS, reclaimable RAM, free,
wired, and swap.

### Tests

Unit tests cover EngineResult roundtrip, assemble-from-staged-payloads,
`--max-tracks 1` stopping after one new file, and CLI help.

### Not run

Did not launch All-In-One against the remaining four corpus files in this
change. That still needs ~5–6 GB reclaimable headroom during demix. The
intended Cursor command is:

```bash
uv run dj-analyze test_folder_10_house_tracks \
  --out output/step1-collection.json \
  --resume --max-tracks 1
```

### Collection JSON at this point

Six complete tracks in `output/step1-collection.json`. Missing: Love State
(retry), Dj Yellow, Lemon8, Life Is Trippy.

## 2026-09-04 — E019 — Staged `--max-tracks 4` corpus resume

### Command

```bash
uv run dj-analyze test_folder_10_house_tracks \
  --out output/step1-collection.json \
  --resume --max-tracks 4
```

Started with 6 complete tracks, ~5044 MB reclaimable, ~2415 MB swap.

### Result

JSON now has all 10 filenames. Source SHA-256 unchanged on every file.

| track | ingest | Beat This | All-In-One |
|---|---|---|---|
| Love State | yes; -9.21 LUFS; B minor 10A | 926 beats | killed at 720 MB reclaimable; wired ~12 GB |
| Dj Yellow | yes; -12.87 LUFS; G# minor 1A | 1027 beats | killed at 705 MB reclaimable |
| Lemon8 | yes; -13.91 LUFS; F# major 2B | 1058 beats | killed at 660 MB reclaimable |
| Life Is Trippy | yes; -16.43 LUFS; D minor 7A | 681 beats | **passed**; 128 BPM; 640 beats; 16 sections; peak RSS 3538 MB |

Worker RSS during failed demix was 38–225 MB. The RAM that disappeared was
wired Metal (~9–12 GB), which `ps` RSS does not show. After each kill,
reclaimable recovered to ~10–11 GB. Life Is Trippy survived because demix
bottomed at ~1355 MB reclaimable, above the ~768 MB kill floor.

CLI reported 5 collection failures: two leftovers from earlier Love State
runs (ENOSPC, old RAM kill) plus the three new All-In-One kills.

### Learning

The staged pipeline did what it was supposed to: keep ingest/Beat This,
free All-In-One after a kill, continue to the next file, do not freeze the
laptop. HTDemucs still needs a demix window that this 16 GB Mac cannot
hold while Cursor and ~2 GB of swap are already present. Retry All-In-One
only for the three failed hashes, preferably after swap has dropped.

Tempo/key/beats/sections remain `benchmark_estimate`.

## 2026-09-04 — E020 — All-In-One retry died on spectrogram RSS, not demix

### Command

```bash
uv run dj-analyze test_folder_10_house_tracks \
  --out output/step1-collection.json \
  --resume --max-tracks 3
```

Start: 10 tracks in JSON, ~10260 MB reclaimable, ~1378 MB swap.

### Result

Demix survived on all three retries (wired ~10–13 GB, reclaimable stayed
above ~1.2 GB). Then "Extracting spectrograms" grew worker RSS to:

- Love State: 4806 MB
- Dj Yellow: 4982 MB
- Lemon8: 4932 MB

Each was killed by the 4096 MB RSS cap. Beat This and ingest were redone
unnecessarily. Life Is Trippy stayed complete. Leaked-semaphore warning
from All-In-One multiprocessing showed up at kill time again.

### Learning

The 4096 MB RSS cap was the wrong limit once swap had dropped. Spectrogram
RSS scales with track length; Life Is Trippy peaked at 3538 MB and
finished. D030 raises the cap to 7168 MB and reuses ingest/Beat This on
retry. Do not lower the reclaimable floor; that is what stopped Metal from
freezing the laptop in E019.

## 2026-09-04 — E021 — 10/10 All-In-One complete under 7168 MB RSS cap

### Command

```bash
uv run dj-analyze test_folder_10_house_tracks \
  --out output/step1-collection.json \
  --resume --max-tracks 3
```

Start: RSS cap 7168 MB, ~9493 MB reclaimable, ~1732 MB swap. Ingest and
Beat This reused.

### Result

All three remaining All-In-One workers exited 0. Source SHA-256 unchanged.

| track | LUFS | key | All-In-One BPM | sections | peak RSS |
|---|---|---|---|---|---|
| Love State | -9.21 | B minor 10A | 130 | 24 | 4689 MB |
| Dj Yellow | -12.87 | G# minor 1A | 120 | 25 | 4671 MB |
| Lemon8 | -13.91 | F# major 2B | 133 | 32 | 4731 MB |

Corpus is now 10/10 complete in `output/step1-collection.json`. CLI still
printed 8 collection failures because resume had kept old kill records;
those were pruned so collection `failures` matches current track objects
(empty).

Tempo/key/beats/sections remain `benchmark_estimate`. Lemon8's 133 BPM is
slightly above the 120–130 house expectation and is still an estimate.

### Learning

D030 was sufficient: spectrogram/analyze RSS peaked ~4.7 GB, under 7168.
The reclaimable floor did not fire. Skipping ingest/Beat This left more
RAM for All-In-One. Step 1 corpus run is done. Step 2 is not authorized
by this result.

## 2026-09-04 — E022 — Step 2A scoring on the 10-track JSON

### Change

Implemented D032/D033: harmonic, tempo, and transition scorers plus a
greedy `tempo_wave` order. CLI: `dj-score COLLECTION.json`. 31 unit tests
passing.

### All-In-One refinement note (not executed)

Inspected `allin1_mlx` 1.0.6 loaders: `harmonix-all` averages eight folds.
Single-fold names `harmonix-fold0`–`harmonix-fold7` exist. Demix still runs
HTDemucs before those folds. D031 records later options (single fold,
internal demix changes, different model, Amazon VM). No config swap in
this change.

### Corpus score observation

`dj-score output/step1-collection.json` starts at Dj Yellow 120 BPM 1A.
No other corpus BPM is within 4% of 120 (next is Certified 125, 4.17%
incoming stretch), so the first climb cannot satisfy the stretch cap.
Greedy then prefers Camelot-adjacent 2A at 133 BPM (9.77% stretch,
infeasible). Several later pairs are harmonic-incompatible under Related 2
and are capped at 0.15. This is expected on a 10-track, 120–136 BPM set
with a 5 BPM hole at the bottom; it is not a claim that the order is a
good DJ set.

Tempo/key inputs remain `benchmark_estimate`.

## 2026-09-04 — E023 — Step 2B lookups and FFmpeg clip renders

### Change

Implemented D034: `get_track_summary` / `get_transition_windows` plus
FFmpeg clip tools (`load_track`, `set_gain`, `eq_band`, `low_cut`, `loop`,
`crossfade`, `time_stretch`, `render_segment`). CLIs: `dj-score --summary`
/ `--windows` and `dj-render`. 43 unit tests passing.

### What was tested

- Synthetic `TrackAnalysis` summaries omit full beat arrays and drop
  novelty-crossing loops.
- Generated sine WAV/MP3s in tmp (not the 10-track corpus): source hash
  unchanged after `load_track`; writes into the music folder are refused;
  gain/EQ/stretch bounds reject; 128→130 `atempo` shortens duration;
  2-rep loop loses ~12 ms; 0.5 s crossfade of two 2 s clips is ~3.5 s.
- Corpus JSON: compact summary for `01 My Paradise - Edit.mp3` via
  `dj-score --summary` (133 BPM, Eb minor 2A, −8.96 LUFS, 25 sections).

### Not executed

No render of the 10 house MP3s. No Rubber Band comparison. No MixPlan
`render_set`. No Step 3.

### Learning

FFmpeg 8.0.1 `acrossfade`, `volume`, `equalizer`, `highpass`, and `atempo`
are enough for bounded clip tests. Worker RAM is not an issue at 1–2 s
tones. Stretch/EQ quality is still unheard.

## 2026-09-04 — E024 — Manual MixPlan validator and synthetic set render

### Goal

Create the smallest end-to-end set command before automatic/LLM planning.
Do not render or re-analyze the ten-track corpus.

### Change

- Added strict `MixBrief`, `MixPlan`, downbeat-indexed segment,
  bar-duration transition, and `RenderManifest` models.
- Added deterministic validation for schemas, duration agreement, unique and
  ordered IDs, source containment/hashes, downbeat bounds, gain/stretch
  limits, consecutive transitions, matched effective BPM, and duration
  tolerance.
- Added `dj-render set --analysis ... --plan ... --out ...`.
- Added atomic PCM WAV publication, atomic manifest writes, final
  LUFS/LRA/true-peak/duration/hash measurements, and source re-hashing.
- Fixed render CLI defaults so outputs beside input sources are refused.
  Moved output-directory creation after the source-folder safety check.
- Made collection checkpoint JSON writes atomic, rejected cross-folder resume,
  preserved current collection-level worker failures, and stopped
  mislabeling FFmpeg sample format as MP3 bitrate mode.

### Synthetic test

Three generated six-second stereo float WAV tones at a synthetic 240 BPM were
cut by downbeat indices, one received −1 dB gain, and two four-bar crossfades
were assembled. The result was approximately 10 seconds. Its manifest
contained executed load/gain/crossfade actions and non-null integrated LUFS
and true peak. All synthetic source hashes remained unchanged.

`uv run pytest -q` → **50 passed**.

`uv lock --check` → lock resolved without changes.

### Real-corpus validation without render

`examples/mvp-three-track-plan.json` validated against
`output/step1-collection.json`:

- 3 source hashes matched.
- 3 downbeat-indexed segments resolved.
- 2 consecutive eight-bar transitions resolved.
- Planned duration: 609.318 seconds for a 600-second request.
- No time stretch.

No corpus MP3 was decoded into a render, no set WAV was created, and no source
file was modified.

### Learning

The existing analysis and clip primitives were sufficient for a minimal set
executor. The next unknown is auditory quality, not another architecture or
analyzer choice. The first real render remains an explicit user checkpoint.

## 2026-09-05 — E025 — First listening diagnosis and exact-grid house-transition revision

### Input and user evidence

The user ran the D036 command between sessions. The preserved artifacts are
`output/mvp-three-track-set.wav` and
`output/mvp-three-track-manifest.json`. The manifest reports 609.3178 seconds,
−13.91 LUFS, 3.2 LU loudness range, −0.16 dBTP, unchanged source hashes, and
two 14.4361-second eight-bar triangular crossfades.

The user reported the same three problems on both transitions:

- The transition was too quick; desired total overlap is about 30 seconds.
- Only lowering the outgoing volume while raising the incoming volume is not
  a satisfactory house transition.
- Incoming and outgoing downbeats did not sound synchronized.

### Diagnosis

The 8-bar plan was expected to be short: 8 × 4 × 60 / 133 = 14.436 seconds.
More importantly, the renderer used that rounded-BPM calculation even though
the actual outgoing detected 8-bar spans are 14.55 and 14.54 seconds. The
overlap therefore began 0.114 and 0.104 seconds before the intended outgoing
downbeat. Extending the old formula to 16 bars would have increased the first
offset to about 0.218 seconds.

The stored analyzers do not show evidence that rerunning is the first fix:

- My Paradise: beat F1 0.9959, downbeat F1 0.9946, no phase warning.
- Rock The House: beat F1 0.9957, downbeat F1 0.9972, no phase warning.
- Lemon8: beat F1 0.9991, downbeat F1 0.9962, no phase warning.

All-In-One downbeat spacing is about 1.82 seconds on all three tracks. Across
the proposed 16-bar overlaps, outgoing vs incoming grid lengths differ by
0.010 seconds for pair one and 0.000 seconds for pair two.

### Change

- Transition duration now comes from the outgoing detected downbeat span,
  scaled only when the segment is explicitly time-stretched.
- Validation rejects more than 70 ms adjacent-grid drift across an overlap.
- Added `house_eq_v1`, a 180 Hz crossover with a midpoint bass handoff and
  broad high-band entry/exit envelopes.
- Added `dj-render downbeat-clicks --analysis ... --plan ... --out-dir ...`.
  It uses stored grids and creates one centered 30-second click-overlay WAV per
  selected track; it does not rerun All-In-One or Beat This.
- Added `examples/mvp-three-track-plan-v2.json`. Extending the first two
  outgoing endpoints preserves the v1 transition start positions while both
  overlaps grow to 16 bars / 29.090 seconds. Validated set duration is 609.100
  seconds.

### Synthetic verification

- A 4-second `house_eq_v1` overlap over two six-second generated tones
  produced the expected eight-second result.
- Non-rounded synthetic grids proved overlap duration follows detected
  timestamps instead of the BPM label.
- The click command produced three centered diagnostic WAVs from three
  generated tracks and preserved all source hashes.
- Full suite: `uv run pytest -q` → **54 passed**.

### Not run / remaining unknown

No real v2 WAV or real click diagnostic was rendered during E025. The actual
correctness of each downbeat and the musical quality/headroom of
`house_eq_v1` remain listening questions. The next experiment is the three
click clips followed by one explicit v2 render—not re-analysis, batch render,
or Step 3.

## 2026-09-05 — E026 — V2 first-success listening checkpoint

### Goal

Register the user's listening result for the D037 revision without expanding
one successful three-track test into a corpus-wide claim.

### Produced artifacts

- `output/mvp-three-track-set-v2.wav`
- `output/mvp-three-track-set-v2.manifest.json`
- Three primary-grid diagnostic WAVs in `output/downbeat-clicks/`

The manifest confirms:

- Plan: `mvp-three-track-133-v2`.
- Rendered duration: 609.100 seconds.
- Transition 1: 29.090 seconds, 0.010 seconds adjacent-grid drift.
- Transition 2: 29.090 seconds, effectively 0.000 seconds drift.
- Integrated loudness: −13.81 LUFS.
- Loudness range: 3.1 LU.
- True peak: +1.04 dBTP.
- Output SHA-256:
  `7b7f7517aae943649ecef1f9911aa88bef3c98379725d6d7235ede66a0f8c21f`.
- All three source hashes unchanged.

Each primary downbeat diagnostic is exactly 30.000 seconds.

### User listening result

The user described the second mix as “much better” and accepted both the
transition duration and downbeat alignment for this first version. The user
also reported the first/primary downbeat diagnostic was great.

### Interpretation

This is the first successful auditory checkpoint for an end-to-end set. The
accepted behavior is the 16-bar exact-grid `house_eq_v1` baseline on the two
specific transitions in this three-track plan. The listening report is
`user_verified` evidence at that scope only; stored analysis values remain
`benchmark_estimate` for other excerpts and tracks.

The transition problem is resolved for the first product version. The render
is not yet delivery-mastered because +1.04 dBTP leaves no safe playback/encode
headroom. Preserve that as an optimization note rather than changing the
accepted transition in this experiment.

### Next recommendation

Implement a deterministic final-bus headroom/limiter policy with measured
postconditions, then test the accepted transition on a larger manual set.
Automatic/LLM planning remains deferred.

## 2026-09-07 — E027 — Independent prompt-to-playlist first slice

### Goal and scope

Implement the D039 boundary: prompt entry → replaceable query translation →
strict validation → deterministic catalog retrieval and matched-track lookup.
Keep installation and tests independent from the audio engine so both tracks
can progress in parallel.

### Established inputs

- The user explicitly authorized this track and reusable modular packaging.
- Existing accepted audio behavior remains D038/E026; no new listening claim
  is part of this experiment.
- The completed `output/step1-collection.json` is the only real DJ catalog
  input for this slice. The adapter reads metadata only.
- The artifact lacks per-track semantic genre/mood/energy tags. Synthetic
  labeled catalog fixtures are needed to test descriptor retrieval without
  inventing annotations for the real songs.
- Implementation location: `packages/prompt-to-playlist/`; independent
  Python distribution with Pydantic v2 as its only runtime dependency.

### Implementation

- Independent `prompt-to-playlist` 0.1.0 distribution with strict versioned
  models (including the top-level `prompt-playlist/run` 0.1.0 envelope),
  vocabulary normalization, deterministic search/ranking and ID lookup,
  tool schemas/dispatch, and a small orchestration service.
- Replaceable catalog and translation adapters. The DJ adapter reads JSON
  only. The optional OpenAI adapter makes one bounded structured-output
  request with explicit model/key environment configuration. The default
  rules translator works offline and identifies unsupported constraints.
- `prompt-playlist` CLI plus a native Tkinter desktop form. Both use the same
  validation and retrieval core; the form needs no server, browser, hosting,
  or deployment.
- Independent package documentation, examples, environment, lockfile, and
  build artifacts.

### Environment and commands

Standalone `uv sync` created a separate Python 3.12.10 environment with
Pydantic 2.13.5 and pytest 9.1.1. Pydantic is the only package runtime
dependency; audio/ML libraries are not required. The form used Tk 8.6.13.

From `packages/prompt-to-playlist/`:

```bash
uv sync
uv run pytest -q
uv build
uv run prompt-playlist prompt --catalog examples/demo-catalog.json \
  --text 'require house; prefer dark; bpm 120-130; count 3'
uv run prompt-playlist search --catalog examples/demo-catalog.json \
  --query examples/house-query.json
uv run prompt-playlist ui --catalog examples/demo-catalog.json
```

### Validation results

- Final standalone full suite: `uv run pytest -q` → **190 passed in 0.24
  seconds**, including translator revalidation regression cases.
- Engine regression from the DJ project root: `uv run pytest -q` →
  **54 passed in 5.17 seconds**. The engine's test baseline is unchanged.
- `uv build` successfully produced the standalone source distribution and
  wheel.
- Offline prompt CLI and direct JSON-query search completed successfully.
- The actual GUI event loop submitted the rules example and rendered three
  rows; the first was `Night Grid (Fictional Demo)`.
- In-memory import of the existing DJ artifact produced ten catalog tracks.
  All ten BPMs retained `benchmark_estimate` authority and `warning` status;
  the catalog contained zero semantic tags.
- A 130–133 BPM query found six eligible tracks and returned five at its
  limit. Requiring `genre:house` returned zero, correctly exposing absent
  evidence instead of inventing per-track genre annotations.
- Before/after SHA-256 checks matched all ten source MP3s to `docs/CORPUS.md`.
  The collection JSON SHA-256 was unchanged:
  `348d2f857b5d98476386e8da3499fbad15966cf68814beda497a9062459fdb93`.

### Review findings and fixes

Review found that already-created catalog and vocabulary models could be
mutated in memory before reaching a public boundary. Revalidation was added
so those changes cannot bypass the strict contract. Regression cases cover
the relevant catalog, vocabulary, and translator entry points. Live provider
response handling was exercised with mocks; those tests do not establish
model interpretation quality.

### Evidence boundaries and next checks

Offline fixtures and mocked provider responses cannot establish live model
quality. The real-catalog JSON import/search establishes interoperability and
missing-evidence behavior, not semantic recommendation quality. No live API
call, new audio analysis, corpus render, or new listening verification was
performed. Offline checks required no credentials; no API-key values were
read or logged. Automatic MixPlan generation remains deferred.

Next collect realistic request examples, add a small reviewed tag source, and
evaluate live model interpretation with an explicitly configured provider
before judging semantic results on the real collection. Continue the engine's
headroom/manual-set work independently.

## 2026-09-07 — E028 — Real playlist pool and project OpenAI setup

### Goal and authorization

Use the user's larger local music pool in the independent playlist module and
connect the prompt form to their project OpenAI credential. D040 scopes this
to read-only metadata catalog import and bounded live request translation.
The engine's accepted D038/E026 mix, ten-track analysis corpus, RAM limits,
and deferred automatic MixPlan/render integration remain unchanged.

### Inputs and implementation

- Pool: `test_tracks_folder_mp3` under the DJ project root; direct inventory
  confirmed 120 MP3s in 121 directory entries, with one skipped entry.
- The explicit `import-folder` adapter computes source hashes and runs
  sequential, timeout-bounded ffprobe container/embedded-tag inspections.
  It writes new catalog and `prompt-playlist/folder-import` version `0.1.0`
  manifest JSON outside music folders. No acoustic model or PCM intermediate
  is required. The catalog contract remains `0.1.0`.
- Encoded genre labels retain metadata provenance and warnings; embedded BPM
  remains a `benchmark_estimate`. Missing tags/axes remain missing, and
  incomplete tag coverage cannot prove a negative filter. The project
  vocabulary is separate from the reusable default vocabulary.
- Explicit `playlist.toml` selects the local catalog, project vocabulary,
  OpenAI, and `gpt-5.4-mini-2026-03-17`. The snapshot was checked against
  [OpenAI's official model documentation](https://developers.openai.com/api/docs/models/gpt-5.4-mini).
  The `Open Playlist.command` launcher opens the configured form; reusable
  operation without a project config retains offline rules mode.
- The configured credential is `AUTODJ_OPENAI_API_DEV_KEY`. A named environment
  value takes precedence over the explicit literal-assignment fallback in
  `~/.zshrc`. The fallback never executes shell code, expands substitutions,
  selects unrelated credentials, or copies the key into repository files.
  Configuration/credential errors omit input values. No secret values belong
  in this record.
- Live requests send only the playlist request, descriptor vocabulary, and
  strict query contract to the official OpenAI Responses endpoint. The local
  catalog, source paths, track names, and audio are not sent. One validated
  proposal feeds deterministic local retrieval; there is no arbitrary tool
  execution or fallback to an unrequested provider.

### Commands

From `packages/prompt-to-playlist/`:

```bash
uv run prompt-playlist import-folder --folder ../../test_tracks_folder_mp3 \
  --vocabulary pool-vocabulary.json \
  --out output/pool-catalog.json --manifest output/pool-import-manifest.json
uv run prompt-playlist ui --config playlist.toml
uv run pytest -q
uv build
```

The checked-in configuration contains names and paths, never a key value.
Generated catalog/manifest and live-check results belong under package
`output/`, not a source music directory.

### Live interpretation finding and correction

The first real request established successful credential resolution,
authentication, model access, and structured output. Its semantic assertion
failed: the phrase “up to five tracks” was interpreted as the default limit
10 plus an unresolved fixed-limit constraint. Retrieval did not run because
unresolved constraints block execution.

The correction clarified maximum-count semantics in the translator
instructions and schema field description and advanced prompt provenance to
`playlist-query-v2`. This preserves the failed observation instead of claiming
that connection success proved correct interpretation. Follow-up live cases
and final verification outcomes are recorded below.

### Initial metadata inventory

The first complete importer pass produced 120 catalog tracks from 120 MP3s,
with no duplicate source hashes or import failures. It took 5.576542 seconds
and read 1,381,021,989 source bytes. Encoded duration metadata totals
33,587.244764 seconds. Source hashes and the source directory inventory
matched before and after the pass.

Titles were available for all 120 tracks, artists for 116, duration for 120,
and embedded BPM for 22. Sixty-five files had encoded genre text; 62 matched
known descriptors, while three stayed unmapped: `Bar House Deep`,
`Disco Italo-Disco`, and `LAGRIMA DE OURO`. There were no imported mood,
energy, vocal, or complete-axis annotations. This is metadata coverage, not
reviewed classification accuracy. The canonical import below additionally
records the actual ffprobe version in its manifest.

### Canonical catalog and source preservation

- Catalog: `packages/prompt-to-playlist/output/pool-catalog.json`.
- Manifest: `packages/prompt-to-playlist/output/pool-import-manifest.json`.
- Importer: `mp3-metadata-v1`; ffprobe version 8.0.1, with the exact version
  string/executable path recorded in the manifest; per-file probe timeout 10 s.
- Vocabulary: `pool-descriptors-v1`, 39 descriptors. Only known metadata
  labels are normalized; descriptor vocabulary membership creates no track
  annotation by itself.
- Canonical pass: 2026-09-07 21:36:39.192004–21:36:45.484758 UTC,
  **6.292754 seconds**. It produced 120 catalog tracks, no duplicate files,
  no failed files, and one skipped `.DS_Store` entry. Coverage matches the
  initial inventory above.
- Both `source_hashes_unchanged` and `source_inventory_unchanged` are true.
  The manifest stores every exact discovered source path and before/after
  SHA-256; it is the complete machine-readable preservation record.
- Catalog SHA-256:
  `edee12016a37133218cfddeb620dad3b1bdfb563a1643af75f0654f444e32a8f`.
- Manifest SHA-256:
  `84236b16223d88c4bb0f41a33afecad53af4bfa31db87b65b1eec58276e9d009`.

The manifest also records raw tag-key coverage. For example, three files
contain a `mood` key and seven an `energylevel` key. These have not been
mapped into normalized semantic evidence: the catalog's zero mood/energy
coverage is not a claim that no related raw metadata exists. Review source
meaning, provenance, and the value-to-vocabulary mapping before using them.

### Validation recorded during implementation

- Intermediate independent package suite: **343 passed in 0.36 seconds**;
  the final result after additional publication/source regressions is below.
- Configuration/credential-specific checks included 96 passing tests; folder
  importer checks included 50 passing tests. They use fixtures and mocks,
  keeping real API calls explicit and separate.
- After the count-semantics correction, the bounded live retest completed in
  1.45 seconds with `limit: 5`, required house, and no unresolved constraints.

### Five-case live smoke evaluation

`packages/prompt-to-playlist/output/openai-live-check.json` stores complete
runs, expected/observed assertions, elapsed time, and model/catalog/vocabulary
identities under `prompt-playlist/live-check` version `0.1.0`. The configured
snapshot and `playlist-query-v2` passed all five cases on the real local
catalog:

| Request | Observed result | Elapsed |
|---|---|---:|
| “Find up to five tracks. Only include tracks tagged as house.” | Correct count/genre constraints; 5 matches | 2.000 s |
| “Dame tres canciones. Solo incluye canciones etiquetadas como dembow.” | Spanish request resolved to dembow; 3 matches | 1.391 s |
| “Give me four tracks between 120 and 130 BPM, sorted from slower to faster.” | Correct BPM bounds and ascending order; 4 matches | 1.676 s |
| “Find three house tracks with no vocals.” | Correct hard vocal exclusion; 0 matches because vocal-axis coverage is unknown | 1.600 s |
| “Make a 45-minute continuous mix with beatmatched transitions.” | Unsupported mix planning surfaced as `needs_clarification`; no retrieval | 1.198 s |

Seven live requests were made during setup: the first semantic failure, its
corrected retest, and these five cases. There was no automatic retry or silent
provider fallback. Output destination/CLI configuration validation occurs
before any API request. The project credential source remained unchanged.

These checks establish a working connection and bounded examples of useful
request interpretation. They do not prove broad language accuracy, subjective
recommendation quality, annotation correctness, or prompt-injection resistance.
The no-vocals result demonstrates honest coverage limits rather than invented
negative evidence. The unsupported-mix result preserves the separate engine
boundary.

### Final verification and delivery

- Standalone package suite: **346 passed in 0.37 seconds**. The final additions
  cover CLI source-change publication gates and hidden-MP3 handling.
- Engine regression suite: **54 passed in 4.60 seconds**. Engine behavior and
  its independent test environment remain intact.
- `uv build` produced the **0.2.0** standalone source distribution and wheel.
  Existing catalog/run/query schemas remain `0.1.0`; new config/import/live
  report contracts are separately versioned.
- The configured native Tkinter form displayed the 120-track catalog and
  model snapshot in its header. Submitting the saved successful translation
  through the form produced five real catalog rows. The UI check reused that
  recorded live translation and made **zero additional API requests**; it is
  a UI/retrieval smoke check, not another independent model-quality sample.
- Final source verification matched all **120 pool source hashes** to the
  canonical import manifest and all **10 original engine source hashes** to
  `docs/CORPUS.md`.
- The immutable engine analysis JSON retained SHA-256
  `348d2f857b5d98476386e8da3499fbad15966cf68814beda497a9062459fdb93`.
- No new corpus audio analysis, real audio render, MixPlan generation,
  external playlist publication, or source-file modification occurred.

### Remaining quality work

The project form is configured for real requests and the 120-track local
catalog. Next review existing raw annotations and the three unmapped genres,
add a provenance-bearing semantic sidecar where necessary, and broaden real
request evaluation before claiming robust semantic recommendation quality.
Preserve the independent engine's accepted transition baseline and continue
its headroom/larger-manual-set work separately. E027's original 190 package
tests and prior engine/listening findings remain historical evidence.

## 2026-09-07 — E029 — Natural-language playlist and interface correction

### Reported failure

The user entered “house dj set energetic” in the desktop and received offline
semicolon-grammar instructions. Process inspection found the old offline
window still running alongside the configured OpenAI window. E028’s bounded
configured-window smoke did not establish a reliable launch path for the
user. D041 and package P007 supersede the old implicit offline default.

The desktop now requires OpenAI and resolves explicit/current-directory/
editable-checkout configuration; generic CLI prompt defaults to OpenAI, with
`--provider rules` reserved for explicit offline developer use. The refreshed
light Tk interface shows simple criteria, artists/BPM and missing preference
evidence, with detailed provenance on demand. No UI dependency, serialized
schema, catalog or engine behavior changes. Translator `playlist-query-v3`
requires a directly requested single genre, prefers ordinary mood/energy, and
treats “DJ set” alone as playlist context.

### Actual live regression and retained checks

The explicit live runner made **six real OpenAI requests**, all passing,
using configured `gpt-5.4-mini-2026-03-17` and the existing 120-track snapshot.
Complete prompts, expected/observed fields, IDs, evidence and timings are in
[`openai-live-check-natural-language-v3.json`](packages/prompt-to-playlist/output/openai-live-check-natural-language-v3.json)
and detailed in package P-E003.

| Case | Result | Seconds |
|---|---|---:|
| Exact “house dj set energetic” | Required house, preferred high energy, limit 10; eight matches, no unresolved clauses | 2.924 |
| English count/house | Five matches, correct required genre and limit | 2.395 |
| Spanish dembow | Three matches, correct required genre and limit | 3.720 |
| BPM bounds/order | Four matches, 120–130 BPM, ascending | 2.087 |
| No vocals | Zero matches; unknown negative evidence respected | 1.874 |
| 45-minute continuous beatmatched mix | Clarification, no retrieval | 1.521 |

All eight user-regression matches have exact `genre:house` annotations and
missing preferred `energy:high`. There are no normalized energy tags in the
snapshot. The result therefore demonstrates a working natural-language query
and honest retrieval shortfall, not verified energetic recommendations. All
returned IDs belong to the catalog. Six calls here are in addition to E028’s
seven historical setup calls, with no automatic retries/fallbacks.

### Verification and scope

- Independent package suite: **363 passed**; no live calls in those tests.
- Version 0.2.0 wheel/source distribution rebuilt successfully with `uv build`.
- Actual Tk event-loop replay displayed eight rows, required-house criteria,
  visible missing-energy evidence and the original description. It verified
  busy/duplicate-submission handling, error/retry state, stale export/result
  removal, and full error details. No extra API calls were made.
- Checked controls fit both 1200×840 and 1000×700 windows with details shown
  and hidden. Long clarification text remains bounded in the overview and
  available in full details. Screenshot visual QA was unavailable; these are
  actual widget-state/geometry checks, not screenshot inspection.
- UI check: [`desktop-refresh-check.json`](packages/prompt-to-playlist/output/desktop-refresh-check.json).
  Earlier engine-suite evidence remains 54 passing tests in E028; no engine
  source/dependency changes were needed for this interface correction.

The work reads the saved catalog and does not access/modify source audio, reimport
metadata, run heavy analysis, render, generate MixPlans, publish playlists or
change `.zshrc`. Prior preservation observations remain E028 checks rather
than a new source-hashing run. Engine headroom and manual-set work remain
independent; reviewed semantic annotations and broader live language evaluation
are still the playlist quality gaps.

## 2026-09-08 — E030 — Cloud desk research and planning-artifact verification

**Decision:** D043. **Kind:** Research/documentation and artifact checks, not
an audio or cloud experiment.

### Published artifacts

[docs/cloud-library](docs/cloud-library/README.md) contains approximately
17,000 words of reports and operating documentation, 45 primary-source
records, proposed architecture/data/API/job contracts, market/onboarding
protocols, threat model and legal/license packet, reliability/runbooks,
conditional delivery tasks and a formula cost workbook. Structured registers
contain ten gates, sixteen questions, twenty risks, seventeen routes with
motives/reopening conditions, twelve decisions, seven unrun experiments,
twenty-four tasks and five actual research-access/source-conflict records.

### Actual verification

- JSON/JSONL parse, unique IDs, event targets, task/gate dependencies and
  source references checked. No dependency cycles or broken relative links
  in the new package were found; machine output:
  [verification.json](docs/cloud-library/verification.json).
- Three workbook sheets recalculated; all three cases drive the same model.
  Changed storage and zero-revenue checks passed. An unselected blank leaves
  the active case intact; selecting it exposes missing input. Final formula
  error scan returned zero matches.
- All workbook sheets/ranges visually inspected. Corrected B2 rate display
  precision and included retained 48kHz/24-bit WAV masters in storage and
  worker-output costs before delivery.
- Independent standard-library arithmetic agrees for eleven key results in
  each of the three scenarios. Saved XLSX retains formulas and the checked
  cached values. Native Excel application recalculation was not performed.
- Generation/validation helpers live only under the documentation package.
  No application code, dependency or live-schema tests were changed or run.

### Findings and limits

B2/R2 are a proposed shortlist, with Spaces retained as a pilot alternative.
No vendor is selected. Five research limitations/conflicts are retained,
including dynamic regional S3/Lexicon price extraction and superseded B2
pricing. Documented features do not establish retrieval latency or usability.

The medium scenario (100 users, 100GB originals each, hypothetical $19/month)
has about $688.77 monthly recurring contribution before initial acquisition/
analysis allocation, but about -$1,075.12 after that allocation. These are
calculated assumptions, not observed costs or commercial forecasts. Sample
compute/support/retention inputs remain unmeasured and excluded licensing,
legal, tax and maintenance costs need review. The result illustrates why
selective analysis and paid/limited onboarding should be tested.

### Scope preserved

No customers/vendors contacted; no account, cloud resource, upload, hosting,
model request, remote analysis/render or automatic MixPlan created. No source
audio was accessed or newly hashed. Earlier preservation/listening/test
evidence remains historical. Playlist implementation stays paused; local DJ
headroom/larger-manual-set work stays active. All empirical cloud gates are
unpassed. No commits or recurring automations were created.

## 2026-09-09 — E031 — Initial private GitHub recovery checkpoint

**Decision:** D044. **Kind:** Version-control setup and preservation checks;
no engine, playlist, cloud, model, or audio behavior change.

### Repository result

- Created private repository
  `https://github.com/manuelalvarezml/resonant-ai-dj` under the authenticated
  `manuelalvarezml` account.
- Existing project Git root retained on `main`; root commit
  `b1b5c4d5a1a31de25e452207bc0f364832786878` pushed and verified through the
  remote branch reference.
- The initial snapshot contains 139 files. The largest tracked file is the
  completed collection analysis JSON at 4,121,419 bytes.
- The dated annotated tag `checkpoint-2026-09-09` identifies the final
  documented baseline after this verification entry.

### Preservation and exclusion checks

- Re-hashed both local music pools and retained outputs before changing Git
  state. All ten engine corpus hashes matched `docs/CORPUS.md`; filenames on
  disk were not modified or normalized.
- Confirmed both MP3 folders, both virtual environments, caches, rendered WAVs,
  and disposable work directories are ignored. No MP3, WAV, FLAC, AIFF, M4A,
  virtual-environment path, `.DS_Store`, or populated `.env` file was staged.
- Tracked compact JSON/PDF evidence, manifests, plans, logs, schemas, lockfiles,
  tests, and the cloud research workbook. The accepted 205 MiB v2 WAV remains
  local and is represented by its plan, manifest, hashes, and D038/E026 result.
- Scanned staged text for common OpenAI, GitHub, AWS, Google, and private-key
  credential signatures; none matched. The tracked `.env.example` contains an
  empty placeholder only.

### Validation

- Engine suite: **54 passed**.
- Independent prompt-to-playlist suite: **363 passed**.
- Cloud discovery validator: 45 sources, 36 links, three workbook sheets,
  three independent arithmetic cases, and zero errors.
- GitHub reports the repository as private with `main` as its default branch.

### Scope preserved

The repository checkpoint is a recovery and audit mechanism. It does not
authorize source-audio redistribution, cloud implementation, remote audio,
automatic MixPlan generation, resumption of playlist development, or changes
to the accepted v2 transition baseline. Large audio requires its own
rights-appropriate backup; hashes establish identity but cannot restore lost
audio bytes.
