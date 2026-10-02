# PlaylistIQ audio-feature policy

## 2026-10-01 — 120 character probes; audio embeddings reused

The replacement bank and all 120 text embeddings are ready. Analyze Tracks refreshes stale description scores from compatible cached audio vectors without audio inference. The current feature version is `selected-estimators-v3-character120`; the eleven estimators and playlist ranking remain unchanged. The new Musical character view groups results by dimension. Two cached-track matching tests passed with exact vector preservation; broader analysis remains a manual owner action. [Concepts, implementation, evidence and limits](CHARACTER_BANK_120.md). This supersedes earlier fixed-32/bundled-matching descriptions.

## 2026-10-01 — Selected estimators are the Analyze Tracks default

The owner requested one default pipeline with selected replacements, retained unreplaced features, added instruments, and both Music2Emo and previous EffNet moods. The web bridge now requires all eleven stages under `selected-estimators-v2`. Old DEAM/key/vocal results remain readable; those replaced estimators no longer execute in ordinary analysis. MusiCNN danceability stays an optional experiment because EffNet remains the selected head. [Implementation, safety behavior and verification](DEFAULT_ANALYSIS_PIPELINE.md). This supersedes earlier standard-bulk/optional-specialists descriptions. Whole-library and new-album analysis remains the owner’s next manual action.

## 2026-09-25 current selection

The web default is `quality`: Music2Emo theme/VA, MusiCNN voice, VGGish aggression and independent OpenMIC instrument support. EffNet happy/sad/relaxed/danceability, Beat This timing, MAEST and MuQ remain. SheetSage2 provides selected browser key evidence. Optional stages are `vocal_musicnn`, `aggression_vggish`, `instrument_passt`, `key_sheetsage2`; requests explicitly opt in with `specialists=1` / `--specialists`. `quality_status` records completion. Catalog identity gains `+estimators-quality-v1`, and its vocabulary gains `+openmic-v1`. No serialized format migration is required. Complete compatible coverage is required independently per scored target; unsupported new labels remain missing for everyone. The two real-track caches preserve all reference results.

[Research, setup, stage contracts and measured verification](TOP_ESTIMATORS_IMPLEMENTATION.md). Richer emotion vocabulary and improved local listening quality are not established. This checkpoint supersedes older reference-default wording below.

## Current policy — 2026-09-22

`hybrid-estimators-v1` adds MuQ-MuLan-large (`muq-3x10s-v1`, up to three ten-second samples), all 56 Jamendo mood/theme and 40 instrument scores, patch p10/p90 summaries, raw DEAM valence, existing key strength and beat-interval / half-double-tempo diagnostics. Existing MAEST 519/top-six, Beat This, KeyExtractor, LUFS, voice/danceability and four mood heads remain. This supersedes dated deferred-valence/pending-bridge language below.

Theme labels are not all emotions. Classifier support, raw 1–9 regression values and cosine similarities are different quantities. No calibrated scene acceptance, lyric inference or personal-taste claim is supported. Segment coverage is the union of sampled intervals (overlaps do not inflate short-clip coverage). The application exposes coverage, support versus similarity, and missing/failed stages.

The catalog projects full numeric vectors as soft evidence; they do not authorize hard instrument or mood absence claims. Expanded objectives require complete eligible coverage; semantic fusion requires compatible embeddings for all eligible tracks and at least two candidates. [Research rationale](research/ESTIMATOR_UPGRADE_2026-09-22.md), [implementation and measurements](ESTIMATOR_UPGRADE.md).

**Updated:** 2026-09-11  
**Decision:** P010 / parent D046  
**Status:** PlaylistIQ 0.3.0 descriptor extraction is complete on the ten-track
house corpus (60/60 stages) and the authorized 37-track diverse corpus (222/222
stages, zero failures, exact sources). Catalog integration, calibrated
thresholds and relevance evaluation remain pending

PlaylistIQ is the product name for the local prompt-to-playlist engine. The
existing directory, Python distribution, CLI command, import namespace, and
serialized `prompt-playlist/*` schema names remain unchanged so working
installations and saved evidence are not broken.

## What works today

The current desktop and CLI translate a natural-language request into a typed
query, then ordinary code searches a saved local catalog. OpenAI receives the
request, vocabulary, and query contract only. It does **not** receive the audio,
paths, track names, or a 120-row feature table. This separation is intentional:
the model interprets the request while deterministic code applies the evidence.
**It also lets us audit why each track matched**: the saved query, matched and
missing criteria, evidence provenance, catalog/version digests, and stable
track IDs explain the result instead of leaving selection inside an opaque
model response.

The real 120-track catalog currently contains:

| Catalog evidence | Coverage | Used by PlaylistIQ search now? |
|---|---:|---|
| Title / duration | 120 / 120 | Title displayed; duration stored but not filterable |
| Artist | 116 | Display only |
| Embedded BPM estimate | 22 | Yes: bounds and BPM order |
| Exactly mapped embedded genre | 62 | Yes: required/preferred/excluded tags |
| Mood / energy / vocals | 0 / 0 / 0 | Contract supports them, but there is no real evidence |
| Danceability | 0 | No vocabulary or contract field yet |

Consequently, the existing “house dj set energetic” check proves request
interpretation and exact house-tag retrieval. It does not prove acoustic
energy recognition or music recommendation quality.

## Descriptor pipeline implemented in 0.3.0

`prompt-playlist analyze-folder` now produces a separate, versioned descriptor
run without All-In-One. Its input folder is variable. It defaults to one track
and needs explicit `--all-tracks` for a full folder. Outputs are always outside
the source and include strict JSON descriptors, machine-readable performance
data, a readable Markdown report, and verified resume checkpoints.

Implemented feature stages:

| Stage | Implementation | Descriptor evidence |
|---|---|---|
| Metadata | FFprobe 8.0.1 | Duration, stream/container facts and restricted encoded tags |
| Loudness | FFmpeg `loudnorm` | Integrated LUFS, LRA, true peak and threshold; never semantic energy |
| Key | Essentia KeyExtractor | Global key/mode, Camelot and strength estimate |
| Rhythm | Beat This 1.1.0 `final0`, CPU | Beats, downbeats and BPM from median beat interval |
| Semantic | Discogs-EffNet shared embedding | 87-label genre; happy, sad, relaxed, aggressive; danceable; voice/instrumental probabilities |
| Energy candidate | MusiCNN plus DEAM | Raw arousal mean; raw valence retained but deferred |

The sidecar preserves raw probabilities and writes a compact controlled
descriptor document for later TF-IDF/BM25/text-embedding experiments. It does
not impose thresholds, create categorical catalog truth, or change the current
UI. That separation is necessary to evaluate false positives and abstention
before schema migration.

Every stage includes sampled process-tree wall time, CPU seconds/utilization,
peak RSS/VMS, threads/children, available RAM, swap, I/O where supported,
real-time factor and failure state. Reports calculate per-algorithm and combined
serial projections for audio hours, 100 tracks, and memory-limited worker counts
on 8/16/32 GB hosts. RSS is used for capacity; macOS VMS is only raw telemetry.
Thread settings are requests; measured CPU is authoritative.

P-E006 processed exactly two of the ten house tracks, not the full folder.
All 12 stages completed with zero failures and unchanged hashes/inventory.
For 684.577 seconds of audio, summed sequential stage time was 84.233 seconds
(7.383 wall minutes/audio hour; 70.194 projected serial minutes/100 same-length
tracks). Peak stage RSS was 1,311.422 MB; a 35% headroom estimate is 1.729 GB
per sequential worker. The model cache is 103.60 MiB. Two tracks prove runtime
integration only; they do not validate semantic accuracy or VM performance.

### Ten-track user run and decoder repair (P-E007)

The user ran the prepared command on all ten house tracks. Metadata, loudness,
key, semantic, and energy succeeded for every track; rhythm failed for every
track before inference because Torchaudio 2.11 requested TorchCodec and Beat
This's SoundFile fallback was absent. All source hashes and the folder inventory
still matched. SoundFile 0.14.0 is now an explicit analysis dependency and
preflight requirement. A one-track real-MP3 repair check passed in 9.81 seconds
with 1,053.0 MB peak RSS and 220.2% process-tree CPU.

The original partial report's 183.72 seconds stage wall and 30.62 minutes per
100 tracks exclude working rhythm inference and must not be used as a complete
pipeline estimate. Projections now exclude failed stages and only form a
combined estimate from tracks whose requested stages all succeeded. Use the
README `--resume` command to reuse 50 passing checkpoints and fill ten rhythm
results; only that final report can replace the two-track capacity baseline.

The successful semantic outputs already show why the diverse-folder test is
needed: all ten house tracks score very high on danceability (0.981–0.999),
while raw arousal occupies a narrower 5.347–6.572 band. These are useful sanity
signals, not threshold validation or proof of prompt-selection quality.

### Completed ten-track baseline (P-E008)

The repaired user resume reused 50 verified checkpoints, executed ten rhythm
stages, and completed all 60 requested results with zero failures. The command
elapsed 95.964 seconds. The complete sequential pipeline accumulates 269.609
seconds of stage wall time for 3,779.013 seconds of audio: 4.281 wall minutes
per audio hour and 44.935 projected serial minutes per 100 same-length tracks.
Peak stage RSS is 1,400.047 MB; with 35% headroom, plan 1.846 GB per sequential
worker. Memory-only limits with 25% host reserve are 3/6/13 workers on
8/16/32 GB hosts. These are local linear projections, not VM benchmarks.

Beat This outputs exactly reproduce the prior DJ artifact's Beat This BPM and
beat/downbeat arrays for all ten files. They disagree with the All-In-One
selected tempo by 0–3 BPM, which remains estimator evidence rather than an
error to hide. `Dj Yellow Ft Marlene - Je Tm.mp3` has an atypical 382
downbeats for 1,027 beats (37.2%, versus 24.4–26.3% for the other tracks), so
downbeats remain a deferred mixing diagnostic and are not a PlaylistIQ
retrieval feature. The compact matching document uses BPM, not raw beat grids.

### Completed diverse-37 baseline (P-E010)

The user-run diverse pass completed 222/222 stages with zero failures, exact
sources, 60 verified reuses and 162 new executions. Acoustic top-1 genre is
`electronic` for 24/37 tracks and 12/37 top scores are below 0.5. Preserve
encoded genre priority and treat acoustic top-N labels as soft evidence with
abstention rather than hard truth.

Danceability is at least 0.95 for 28/37 tracks and has median 0.987, so it is
too saturated for a strong first-version rule without reviewed calibration.
Raw arousal spans 3.985–7.218 with median 5.871; happy, relaxed and aggressive
heads also show useful separation. Mood and arousal are therefore the stronger
initial scored-preference candidates, while all thresholds remain subject to
human review. BPM spans 85.714–187.500; listen for half/double-time errors before
using extremes as hard constraints.

## Audio outputs already implemented elsewhere

The local DJ analyzer can produce the following without relying on All-In-One
MLX for the calculation itself:

| Source | Outputs | Evidence class | PlaylistIQ state |
|---|---|---|---|
| FFprobe / FFmpeg | codec, sample rate, channels, bitrate, duration, decode health | `encoded_fact` | Folder importer keeps duration and limited embedded metadata only |
| FFmpeg + pyloudnorm | integrated LUFS, loudness range, true peak | `standardized_measurement` when validation passes | PlaylistIQ now measures these with FFmpeg `loudnorm`; still not in the search catalog |
| Essentia KeyExtractor | tonic, mode, standard key, Camelot, Open Key, strength | `benchmark_estimate` | PlaylistIQ sidecar now keeps key/Camelot/strength; still not in search |
| Beat This on CPU | beat/downbeat timestamps and BPM derived from beat intervals | `benchmark_estimate` | PlaylistIQ 0.3 now has a public isolated rhythm stage |
| Downbeat rules | loop candidates from a rhythm grid | `benchmark_estimate`/derived status | Mixing aid; not a playlist descriptor |

All-In-One currently supplies the primary BPM/grid and every stored section
label in the completed DJ-engine ten-track artifact. The public `dj-analyze`
command always attempts that stage; it has no `--skip-all-in-one` option.
PlaylistIQ's separate `analyze-folder` command now supplies the lightweight
public path. It publishes descriptors, not a search-ready catalog; the later
catalog adapter remains a deliberate boundary.

The installed non-TensorFlow Essentia build exposes its older `Danceability`
algorithm, but PlaylistIQ does not call it. Its roughly 0–3 output is an
estimate with no project calibration, so it is a benchmark candidate, not a
current tag.

## First web-version selection features

These are the compact fields that can materially change prompt retrieval. They
belong in a versioned evidence sidecar and then in the catalog; model outputs
must use `benchmark_estimate` (or a future `semantic_estimate` authority only
after a coordinated schema decision), confidence, model/version, aggregation,
threshold, and warnings.

| Priority | Feature | Why it affects selection | First-version decision |
|---:|---|---|---|
| 1 | Genre/style | The most common hard filter and essential on a diverse folder | Keep sourced metadata; benchmark an acoustic fallback with abstention; never overwrite reviewed or encoded evidence |
| 1 | Mood | Directly expresses dark, happy, relaxed, aggressive, melancholic, uplifting, and similar requests | Add a small controlled taxonomy, not every available label |
| 1 | Energy/arousal | Needed for “energetic,” warm-up, peak-time, and cooldown requests | Store a calibrated continuous estimate plus optional low/medium/high bands; never derive it from BPM or LUFS alone |
| 1 | Danceability | Directly distinguishes dance-floor intent from listening/background intent | Add a score and conservative danceable/not-danceable tag with abstention |
| 1 | Vocal profile | Makes “instrumental,” “with vocals,” and negative-vocal requests usable | Add vocal/instrumental probabilities; do not mark the axis complete for uncertain cases |
| 2 | BPM | Strong, objective-looking prompt constraint, but still an estimator | Use Beat This in the no-All-In-One path and retain `benchmark_estimate` |
| 2 | Key/Camelot | Useful only for explicit harmonic requests and later deterministic ordering | Retain as an estimate; expose to code filters before considering LLM ranking |
| 2 | Duration | Useful for future playlist-duration budgeting | Already stored; add deterministic duration filtering later |

Integrated loudness, LRA, and true peak remain valuable for playback safety and
mix preparation, but they are not semantic energy. Keep them out of energy
matching. The model should not receive raw beat arrays, section boundaries,
loop candidates, codec details, or long provenance blobs; those are execution
or audit data, not selection language.

## Best lightweight prototype option

For the next **local, non-production** experiment, the best-supported candidate
from the maintained research is Essentia TensorFlow with one shared
Discogs-EffNet embedding pass and small classifier heads:

- `mtg_jamendo_genre-discogs-effnet` for an 87-label genre fallback.
- `mood_happy`, `mood_sad`, `mood_relaxed`, and `mood_aggressive` heads for a
  deliberately small mood set.
- `danceability-discogs-effnet` for danceable/not-danceable.
- `voice_instrumental-discogs-effnet` for vocal/instrumental.
- Benchmark DEAM arousal as the energy candidate. It uses a separate MusiCNN
  embedding, so measure whether its extra pass is justified. Do not rename
  arousal “energy” or convert it into low/medium/high until the diverse-folder
  labels establish thresholds.

The official model cards report 0.97 normalized five-fold accuracy for the
danceability head on 306 tracks, 0.96 for voice/instrumental on 1,000 excerpts,
and 0.87/0.98 for happy/aggressive heads on small in-house sets. Those are
author-reported validation results, not expected accuracy on this library. The
87-label genre head reports test PR-AUC 0.20, and the 56-label mood/theme head
reports PR-AUC 0.14. For that reason, do not import all mood/theme or genre
predictions as confident tags; apply per-label thresholds, abstention, and a
human-reviewed test set.

Official references:

- [Essentia model catalog](https://essentia.upf.edu/models.html)
- [Danceability model card](https://essentia.upf.edu/models/classification-heads/danceability/danceability-discogs-effnet-1.json)
- [Voice/instrumental model card](https://essentia.upf.edu/models/classification-heads/voice_instrumental/voice_instrumental-discogs-effnet-1.json)
- [MTG-Jamendo genre model card](https://essentia.upf.edu/models/classification-heads/mtg_jamendo_genre/mtg_jamendo_genre-discogs-effnet-1.json)
- [MTG-Jamendo mood/theme model card](https://essentia.upf.edu/models/classification-heads/mtg_jamendo_moodtheme/mtg_jamendo_moodtheme-discogs-effnet-1.json)
- [DEAM arousal/valence model card](https://essentia.upf.edu/models/classification-heads/deam/deam-msd-musicnn-2.json)
- [Essentia TensorFlow installation](https://essentia.upf.edu/machine_learning.html)

The package's optional analysis environment now installs
`essentia-tensorflow==2.1b6.dev1389` on Python 3.12/Apple Silicon and exposes
`TensorflowPredictEffnetDiscogs`, `TensorflowPredictMusiCNN`, and
`TensorflowPredict2D`. Exact model/checkpoint URLs and SHA-256 values are pinned;
the cache refuses mismatches. The ordinary UI/search environment still does not
need these dependencies.

### Commercial-viability note, not a playground gate

Essentia is AGPLv3 for non-commercial use or commercially licensed. Its official
licensing page says MTG models are CC BY-NC-ND 4.0 for non-commercial use and
available under proprietary terms. Some model-catalog wording has differed, so
commercial viability remains recorded for a future hosted/product decision.
It is **not a limitation on the current private feasibility playground** and
must not delay the next local pipeline build or evaluation. Local feasibility
does not itself decide later production licensing.

- [Essentia and model licensing](https://essentia.upf.edu/licensing_information.html)

## Deferred because impact does not justify first-version cost

| Feature | Decision |
|---|---|
| Full 56-label mood/theme output | Defer: too broad for the present vocabulary and weak aggregate PR-AUC; test a curated mood set first |
| Detailed instruments | Defer: lower prompt frequency, multi-label ambiguity, and vocal presence captures the immediate use case |
| Valence as a separate user-facing axis | Defer: overlaps the curated mood vocabulary; retain only if the energy experiment shows an independent retrieval benefit |
| Engagement / approachability | Defer: unclear user wording and no present query contract |
| CLAP or other text-audio embeddings | Defer from the next build, but explicitly benchmark later as a direct prompt-to-audio retrieval alternative |
| Low-level spectral descriptors | Retain only for analysis/debugging; do not ask the LLM to infer mood, energy, or danceability from centroid, RMS, flux, or LUFS |
| Beat/downbeat arrays, sections, loops | Keep for DJ planning, not PlaylistIQ candidate filtering |
| Stems and source separation | Exclude: high compute and no demonstrated candidate-selection benefit |
| Popularity, release era, user history | Useful later, but they are metadata/product signals rather than audio-analysis tags |

## Later retrieval experiments kept in the book

The structured-query path remains the first baseline because it is predictable
and lets us audit why each track matched. Now that descriptor extraction works,
compare it later against these separately measured retrieval approaches; do not
mix them into catalog migration before a clean structured baseline exists.

1. **CLAP audio–text similarity:** preprocess each track once into a normalized
   audio embedding, embed the user prompt at query time, and rank by cosine
   similarity. Measure preprocessing time/RAM, index size, query latency,
   cross-genre quality, and whether results can be explained well enough.
2. **TF-IDF or BM25 over descriptor documents:** arrange each track's normalized
   descriptors as a controlled text document, for example `house, dark,
   high-energy, danceable, instrumental, 126-bpm`, then compare the prompt with
   sparse lexical vectors. TF-IDF is not a neural embedding, but it is cheap,
   local, inspectable, and a useful baseline.
3. **Text embeddings over the same descriptor documents:** embed each
   comma-separated descriptor document once with a lightweight sentence/text
   embedding model, embed the prompt, and rank by similarity. Compare this with
   TF-IDF so apparent semantic flexibility is measured against its extra cost
   and reduced explainability.
4. **Hybrid retrieval:** preserve hard structured constraints and their audit
   trail, then use CLAP, lexical, or text-embedding similarity only to rank the
   eligible candidates. This may retain explainability while testing whether
   learned similarity improves softer prompt fit.

Use the same predeclared prompts and human relevance judgments for every method.
Report precision of the first results, false positives/negatives, stability,
offline resource cost, and an explanation record. This later comparison is
both a product experiment and a stronger ML-engineering demonstration than
delegating all matching to an LLM.

## Implemented build boundary

The variable-folder pipeline and durable JSON/report outputs are implemented.
JSON is the first storage choice because it retains nested raw predictions,
provenance, warnings and metrics and is easily audited at the current scale.
The two-track result averaged 51.10 KiB/track including beat/downbeat arrays,
about 4.99 MiB/100 tracks if linear. A future matching table should omit raw
grids and use compact scalars/descriptor documents. Revisit Parquet or a local
database only when measured size/query patterns justify it.

This build does not implement CLAP, TF-IDF/BM25, text-embedding matching, or
the final prompt-to-song ranking comparison.

## Required second-test sequence

1. The user runs the documented full-house-folder command from the terminal if
   desired; the agent must not run all ten tracks. Review the generated report.
2. The user identifies one explicit diverse local folder. It remains read-only;
   all hashes, catalogs, feature sidecars, and reports are written elsewhere.
3. Use the implemented analyzer to create its immutable descriptor sidecar.
4. Extend the catalog contract for scored semantic estimates and add
   danceability vocabulary. Preserve raw probabilities; thresholded tags are a
   derived view and may abstain.
5. Before tuning, define a small prompt set and human expectations for genre,
   mood, energy, danceability, and vocals. Include beatless, live-drum,
   half-time, sparse-vocal, and cross-genre examples.
6. Compare the current metadata-only catalog against the enriched catalog using
   the same prompts. Grade request interpretation separately from track choice.
7. Listen to selected and rejected tracks, record false positives/negatives,
   time, and RAM. Do not claim an axis is complete from model coverage alone.
8. Only after the local gate passes should the UI display these estimates or a
   web implementation depend on them. Cloud upload/deployment remains a
   separate authorization and license decision.

## 2026-09-13 — MAEST Discogs519

Added opt-in `genre_maest` with all 519 mean sigmoid scores in the existing
algorithm values and a separate `prompt-playlist/genre-review` 0.1.0
`genre-top10.json`. It retains failed tracks and source-preservation gates.
No catalog integration or replacement of existing genre evidence.
See [MAEST setup, aggregation and command](MAEST_DISCOGS519.md).

## 2026-09-15 — MAEST top-six and local player integration

Owner-authorized `maest-top6-v1` now replaces legacy genre estimation: match the top six, display three expandable to six, retain all 519 scores, and apply no probability threshold or human review overrides. Historical outputs remain preserved. The low-priority board card `PIQ-GENRE-TOP6-REVISIT` is Later / could; further genre experimentation is not a launch blocker.

The local web player now provides **Analyze tracks** and **Create with PlaylistIQ**. Its loopback Node job service invokes the existing Python environment; analysis persists by source hash and in IndexedDB, and prompt results save into normal playable playlists. Restart the player server on the same origin/port to retain the browser library. This explicit integration authorization supersedes older local bridge/Python-edit holds; cloud deployment, remote audio processing and automatic MixPlans remain deferred.

See [integration contract](WEB_INTEGRATION.md).

## 2026-09-25 — Optional direct-estimator profiles

`reference` remains default. `music2emo` replaces only Jamendo `theme:*` and valid-scale VA preference mappings; the four distinct MTG binary moods remain. `musicnn-dance` replaces only binary danceable-class support. `supervised` selects both independently. Each stage requires complete same-model **catalog** coverage; otherwise its reference remains for everyone. This is stricter than MuQ's eligible-coverage gate. No threshold, learned weights or genre-policy change.

Optional values use up to three nonoverlapping 30-second windows, duration-weighted means and disclosed sampled coverage. Scores are uncalibrated support. Raw VA remains unclipped; only 1–9 means may project through `(r−1)/8` and existing provisional preference mappings. Invalid-scale means retain reference for that axis across the catalog. Per-window dispersion is sampling variability, not calibrated uncertainty. Beat tempo, LUFS, groove, perceived arousal and listener-induced emotion remain different estimands.

[Research and target/license/benchmark audit](research/SUPERVISED_ESTIMATORS_2026-09-25.md) · [operation and exact evidence](SUPERVISED_ESTIMATORS.md). No automatic optional batch inference.
