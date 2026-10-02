# Default Analyze Tracks pipeline — 2026-10-01

## 2026-10-01 — 120 character probes; audio embeddings reused

The replacement bank and all 120 text embeddings are ready. Analyze Tracks refreshes stale description scores from compatible cached audio vectors without audio inference. The current feature version is `selected-estimators-v3-character120`; the eleven estimators and playlist ranking remain unchanged. The new Musical character view groups results by dimension. Two cached-track matching tests passed with exact vector preservation; broader analysis remains a manual owner action. [Concepts, implementation, evidence and limits](CHARACTER_BANK_120.md). This supersedes earlier fixed-32/bundled-matching descriptions.

## Owner request and delivered behavior

Analyze Tracks, Analyze track, and the ordinary local analysis endpoint now run the selected estimators automatically. No specialist flag is needed. Records use `selected-estimators-v2`; older complete records become upgradeable, and compatible stages are reused. No automatic library-wide analysis starts on reload. The user will import and analyze the new albums manually.

| Feature | Default estimator / action |
|---|---|
| Metadata, duration | Keep ffprobe |
| Loudness | Keep FFmpeg loudnorm |
| BPM / beat grid | Keep Beat This |
| Genre | Keep MAEST Discogs519, existing top-six rule |
| Audio/text embeddings | Keep MuQ-MuLan and its existing sampling policy |
| Mood | Keep both EffNet mood/theme + four binary mood heads and Music2Emo themes |
| Valence/arousal | Music2Emo replaces DEAM execution |
| Vocals | MusiCNN replaces EffNet vocal-head execution |
| Aggression | VGGish selected; EffNet aggression retained as part of previous mood evidence |
| Danceability | Keep EffNet, selected by the latest research; MusiCNN dance remains an optional comparison |
| Instruments | Add PaSST OpenMIC; retain Jamendo because its 40-label taxonomy differs from OpenMIC's 20 labels |
| Key | SheetSage2 replaces Essentia KeyExtractor execution |

The eleven stages are `metadata`, `loudness`, `rhythm`, `semantic`, `genre_maest`, `semantic_audio`, `emotion_music2emo`, `vocal_musicnn`, `aggression_vggish`, `instrument_passt`, and `key_sheetsage2`. This changes the web bridge default, not the historical research CLI's default algorithm list.

The selected semantic worker no longer executes the EffNet vocal head. Historical v3 semantic records remain compatible supersets, so upgrades can reuse their mood/instrument/dance data. Explicit matched-window reference experiments retain the old semantic function, including vocals. Historical DEAM/key/experimental results remain readable and are retained when present; they are not recomputed by the new default.

## App and scoring integration

Analysis shows EffNet mood/themes and Music2Emo separately. Main arousal/valence and vocal columns, plus arousal sorting, prefer the selected model outputs and fall back to historical values if unavailable. Key already prefers SheetSage2. Details exposes full scores, windows, coverage and model identity. The extra Details experiment now clearly names MusiCNN danceability; selected specialists no longer require a second button.

The default PlaylistIQ profile remains `quality`. Its existing compatible-coverage gates, MuQ fusion, MAEST handling and ranking weights are unchanged. Selection does not demonstrate superior listening quality. “Reference” can compare previous moods on new records, but retired DEAM/key/vocal outputs exist only where historically cached; unavailable values remain missing rather than being manufactured.

Current complete cache records take precedence over older complete records with more retired stages. The reload migration may restore richer same-hash cache data without inference. Existing track and playlist identities are preserved.

## Execution and failure behavior

Each stage runs sequentially in a separate guarded subprocess, releases its models, and saves a checkpoint. RSS caps remain 4096 MiB for ordinary workers, 6000 MiB for MuQ and 8000 MiB for SheetSage2. The host-available-memory floor remains 1024 MiB; timeouts remain 600 seconds except SheetSage2 at 1800 seconds. No memory limit was relaxed for this change.

Setup/decoder errors are recorded per stage and later stages continue. A track is complete only when all eleven required stages are compatible successes. Failed upgrades preserve prior usable evidence and expose the error. Retry reuses successful stages. Source inventory/hash preservation failures still stop the operation. Model `warning` statuses mean estimates have interpretation limitations; the telemetry distinguishes those from execution failures.

## Reproducible bounded verification

`scripts/smoke_default_pipeline.py` verifies the two previously authorized hashes, executes all eleven stages fresh in `output/default-pipeline-smoke-2026-10-01`, then checks zero-stage retries. It never discovers another corpus. Sources are `test_music/test_folder_37_tracks_diff_genres/04 Listen Over the Ocean.mp3` and `01 My Paradise - Edit.mp3`.

Run from this package with `.venv/bin/python scripts/smoke_default_pipeline.py`. The environment needs the existing analysis, semantic, supervised and specialist extras. macOS memory/swap telemetry requires normal host process access. Source audio is unchanged. This deliberately expensive smoke command reruns both tracks; ordinary Analyze Tracks uses caches.

Measured results and final acceptance follow below.

## Measured acceptance — completed 2026-10-01

| Source | Fresh required stages | End-to-end time | Peak worker RSS | Minimum host available RAM | Retry inference |
|---|---:|---:|---:|---:|---:|
| Listen Over the Ocean | 11/11 | 129.19 s | 3680.4 MiB | 2532.7 MiB | 0 stages |
| My Paradise – Edit | 11/11 | 182.31 s | 3064.3 MiB | 2546.3 MiB | 0 stages |

All 22 subprocess metrics report `passed`: no crashes, timeout or memory guard termination. All source hashes and inventories remained unchanged. Every ML result still carries its normal model-estimate warnings. System-wide swap was already 5467 MiB at the first run and peaked at 8740 MiB during the second; these are whole-machine readings with other applications active, not estimator-only allocation. The run stayed above the memory floor, but a two-track smoke cannot guarantee arbitrary files, durations, a full-library run, or future machine load.

Fresh records are preserved as `ocean-fresh.json` and `paradise-fresh.json`; detailed stage telemetry is in `output/default-pipeline-smoke-2026-10-01/measurements.json`. They were merged into the ordinary web cache with prior JSON saved under `history/<hash>/`. Three previously stored retired/experimental stages remain, explaining why those two production records contain 14 records despite only 11 fresh executions.

Both tracks also passed the real ordinary `/api/local/analyze` HTTP route, without specialist flags, returning current complete/quality-complete records and **zero executed stages**. Evidence: `http-verification.json` in the smoke directory. The app, feature module and status endpoint returned HTTP 200.

Chrome was opened at the existing `127.0.0.1:4173` origin. The saved library loaded; Analysis showed 109 unique tracks. The tested Ocean row visibly showed SheetSage2 C minor, Music2Emo arousal 4.8 and valence 5.4, MusiCNN vocal support 60.9%, previous EffNet themes, separate Music2Emo themes and specialist scores. Search was cleared and Analysis left ready. No whole-library analysis was started.

Final verification: **505 Python tests, 84 web tests, 45 JS syntax checks and the 28-file production build passed**. Added tests cover a stage setup failure continuing to later stages, partial status, missing-only retry, zero-stage subsequent retry, required default membership and selected display precedence with both moods retained. One web migration fixture initially failed because it represented a supposedly current cache without a version; the fixture now supplies the current version and the suite passes. No real model-inference failure or model-selection pivot occurred.
