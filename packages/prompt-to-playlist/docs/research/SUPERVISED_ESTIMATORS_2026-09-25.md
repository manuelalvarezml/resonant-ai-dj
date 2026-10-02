# PlaylistIQ direct feature estimators: research, implementation and evidence

Research and implementation date: **2026-09-25**. Read the [reader digest](SUPERVISED_ESTIMATORS_DIGEST_2026-09-25.md) first for the decision. [Operations/checkpoint](../SUPERVISED_ESTIMATORS.md) owns commands and continuation. This is new Markdown evidence; the published executive, technical and foundations PDFs retain their existing cutoffs.

## Decision and evidence standard

Implement **Music2Emo as a selectable emotion challenger**, plus **MusiCNN danceability as a separate selectable control**. Keep the existing specialist reference as default. No tested candidate has demonstrated superior musical quality on this library. “Practical” here means official usable weights, auditable targets, feasible measured local inference and reversible integration—not universal best accuracy.

| Parameter | Default retained | Implemented challenger / decision | What would justify promotion |
|---|---|---|---|
| Mood/theme | Discogs-EffNet + Jamendo 56-label head | Music2Emo J_all, MERT-95M + BTC/chord/key, continuous 56 scores | Better held-out scene fit and per-label relevance, without replacing emotions with dataset themes |
| Four binary moods | Independent MTG happy/sad/relaxed/aggressive heads | Retain: their targets differ from Jamendo tags | A matched-target labeled evaluation, including disagreement and calibration |
| Valence | MusiCNN + DEAM v2, raw 1–9 | Music2Emo joint raw VA, selectable with themes | Held-out perceived-valence ranking/error improvement and range reliability |
| Arousal / current energy preference | MusiCNN + DEAM v2 | Music2Emo arousal, same explicitly provisional mapping | Separate arousal and perceived intensity judgments; no equation with LUFS/BPM |
| Danceability | EffNet binary head | MusiCNN binary head, selectable; evidence does **not** favor promotion | Human movement/groove judgments on diverse held-out examples, beyond easy dance/non-dance distinctions |
| Vocal presence | EffNet voice/instrumental | Retain | Better matched music-domain evidence; no need to add speech detectors or source separation here |
| Instruments | EffNet + 40 Jamendo instrument labels | Retain | Instrument-specific precision/recall and missing-instrument evaluation |
| Genre | MAEST Discogs519, top six | Preserved exactly | Outside this task; Manuel's positive feedback supports retaining it |
| Broad acoustic scene similarity | MuQ-MuLan embeddings, bank and prompt branch | Preserved exactly | Separate future retrieval comparison |
| Tempo/key/loudness | Beat This / Essentia KeyExtractor / FFmpeg | Preserved | Different estimands; not emotion replacements |

Published results motivate the challenger. Engineering measurements establish feasibility. Human feedback establishes a specific scene-fit problem. None substitutes for the others.

## Baseline audit

The actual baseline has 56 independent mood/theme scores and 40 instrument scores, four additional binary moods, binary voice/danceability, DEAM VA and MuQ segment evidence. It is not a four-mood-only system. Read-only inspection of the saved diverse-37 run found **28/37 EffNet danceability scores ≥0.95**, median **0.987203**. This concentration may reduce useful within-library discrimination; without labels, it is not proof that 28 predictions are wrong.

The Jamendo mood/theme head reports PR-AUC 0.14 and ROC-AUC 0.76 on 18,486 tracks; its 56-output sigmoid head takes 1,280-dimensional EffNet embeddings. Independent outputs need not sum to one. `christmas`, `advertising`, `documentary` and `sport` are themes/use contexts, not discrete human emotions. [Official mood/theme metadata](https://essentia.upf.edu/models/classification-heads/mtg_jamendo_moodtheme/mtg_jamendo_moodtheme-discogs-effnet-1.json).

The instrument head reports PR-AUC 0.20 / ROC-AUC 0.78 on 25,135 full tracks. Its 40 labels are tag-presence targets, not source-separated stems or time occupancy. [Official instrument metadata](https://essentia.upf.edu/models/classification-heads/mtg_jamendo_instrument/mtg_jamendo_instrument-discogs-effnet-1.json). Both use shared embeddings; replacing them individually with larger encoders would add cost without demonstrated local benefit.

| Binary head | Dataset size | Published normalized five-fold accuracy |
|---|---:|---:|
| Happy | 302, class counts 139/163 | 0.87 |
| Sad | 230, 96/134 | 0.90 |
| Relaxed | 446, 145/301 | 0.91 |
| Aggressive | 280, 133/147 | 0.98 |
| Danceability / EffNet | 306, 124/182 | 0.97 |
| Voice/instrumental | 1,000 excerpts, 500/500 | 0.96 |

These are small in-house binary classification tasks, not a common mutually exclusive mood taxonomy, cross-cultural emotional truth, or validated probability calibration. Sources: [happy](https://essentia.upf.edu/models/classification-heads/mood_happy/mood_happy-discogs-effnet-1.json), [sad](https://essentia.upf.edu/models/classification-heads/mood_sad/mood_sad-discogs-effnet-1.json), [relaxed](https://essentia.upf.edu/models/classification-heads/mood_relaxed/mood_relaxed-discogs-effnet-1.json), [aggressive](https://essentia.upf.edu/models/classification-heads/mood_aggressive/mood_aggressive-discogs-effnet-1.json), [danceability](https://essentia.upf.edu/models/classification-heads/danceability/danceability-discogs-effnet-1.json), [voice](https://essentia.upf.edu/models/classification-heads/voice_instrumental/voice_instrumental-discogs-effnet-1.json).

The DEAM v2 metadata specifies `(valence, arousal)`, 200-dimensional MusiCNN inputs and a 1,802-song training source. It reports arousal CCC 0.647, Pearson 0.773, RMSE 0.674; valence CCC 0.778, Pearson 0.738, R² 0.537, RMSE 0.635. **Arousal R² is written as `589` in the official JSON; it is invalid as a normal R² claim and is not silently corrected.** Dataset-level metrics do not certify a particular library track. [DEAM head metadata](https://essentia.upf.edu/models/classification-heads/deam/deam-msd-musicnn-2.json).

## Candidate research and deployability

### Music2Emo: selected experimental emotion estimator

The paper combines MERT representations, chord progression modeling and key with a multitask classification/regression head and knowledge distillation. Its classification target is the same 56 Jamendo tags, not 56 newly discovered nuanced emotions. Static VA labels are normalized to 1–9. Data sources are Jamendo, DEAM, EmoMusic and PMEmo; the paper uses official Jamendo splits and random 70/15/15 splits for the dimensional sets. Its reported dataset counts differ across description and split table, so those tables should not be treated as a manifest of the released checkpoint. [Paper, sections III–IV](https://arxiv.org/html/2502.03979v1).

The official repository reports multi-dataset J+D+E+P PR-AUC **0.1543**, ROC-AUC **0.7810**; R² valence/arousal **0.5184/0.6228** on DEAM, **0.6512/0.7616** on EmoMusic, **0.5473/0.7940** on PMEmo. Its table compares MERT-95M 0.1340/0.7640, MERT-330M 0.1400/0.7650 and MediaEval best 0.1508/0.7747 for Jamendo. These support investigating supervised harmonic/contextual features. They do not establish that PlaylistIQ's released `J_all.ckpt`, corrected adapter and sampled aggregation reproduce that row, nor a paired win over our EffNet/DEAM system. [Official implementation/results](https://github.com/AMAAI-Lab/Music2Emotion).

**Exact deployed identity:** Music2Emotion commit `c5f7984f78d9928b841f25bd05a47377c12c58ca`; official inference-default `J_all.ckpt` (12,958,092 bytes); BTC checkpoint (12,229,576 bytes). Checkpoint filename alone does not prove its full training recipe or which published row it represents. No reconstructed/fine-tuned weights are substituted.

The MERT component is pinned to `m-a-p/MERT-v1-95M` revision `12af15fef9d0ac838c3f475bfbbf26d2060dd4f5`, using 24 kHz mono audio and 12 transformer layers. Its model card describes 95M parameters and 20,000-hour music pretraining. We use supervised head outputs, not audio–text cosine or MERT as a replacement retrieval branch. [MERT model card](https://huggingface.co/m-a-p/MERT-v1-95M).

Local source audit found several integration hazards in the upstream convenience wrapper: thresholded tags lose continuous evidence; shared working-directory cleanup is unsafe; unrestricted pickle and unpinned remote code loading are unnecessary; tonic-only parsing subsequently checks for mode, defaulting to major. Our vendored inference subset retains the architecture, uses unique temporary directories, local pinned weights, safe tensor loading and explicit full scores. It corrects mode encoding to the actual parsed `key_type`, as the training loaders do. This correction is a versioned implementation difference, **not a claim of benchmark parity**. Attribution and both MIT notices are retained.

MERT hidden states drop the embedding state and concatenate means at indices 5 and 6 of the remaining states (actual hidden states 6 and 7). This follows released code; paper layer wording is ambiguous. Chords use the original CQT/BTC route, chord-MIDI Music21 key estimate, transposition by mode, first-100-event truncation and padding. Errors in harmony/key propagate to emotion. Per-excerpt key is an internal auxiliary value and does not replace the existing track key estimator.

### Danceability and VA alternatives

**MusiCNN danceability:** same 306-track binary task, 200-dimensional MusiCNN embeddings, two softmax classes `danceable`/`not_danceable`, published normalized accuracy **0.95** versus EffNet's **0.97**. Usable official graph and code exist. Its 82,458-byte head reuses a 3,197,999-byte backbone. Low incremental cost makes it a useful controlled challenger; neither the published comparison nor our two outputs supports replacing EffNet. [Official model](https://essentia.upf.edu/models/classification-heads/danceability/danceability-msd-musicnn-1.json).

**Essentia EmoMusic MusiCNN VA:** deployable, same 16 kHz/200-dimensional feature family and `(valence, arousal)` head. Metadata reports arousal R² 0.646 / RMSE 0.667 and valence R² 0.515 / RMSE 0.760; its description incorrectly mentions DEAM while its dataset field names EmoMusic. Different test sets/scales/protocol details prevent interpreting larger numbers as a matched improvement. Retain as a cheap future calibration/control experiment; no new inference was warranted within two-track scope. [Official metadata](https://essentia.upf.edu/models/classification-heads/emomusic/emomusic-msd-musicnn-2.json).

**Signal-processing Danceability (DFA):** available directly in Essentia, based on detrended fluctuation analysis. This is a rhythmic regularity diagnostic with its own scale; it is not a learned human movement preference or calibrated alternative to the binary classifier. Defer rather than silently mix it into `danceability:danceable`. [Algorithm definition](https://essentia.upf.edu/reference/std_Danceability.html).

### Newer work considered but not deployed

| Candidate | Target, availability and comparison limits | Decision / evidence that could change it |
|---|---|---|
| SRGNN-Emo, TISMIR 2025 | Nine continuous GEMS intensities: wonder, transcendence, tenderness, nostalgia, peacefulness, power, joyful activation, tension, sadness. Models induced emotion using user/tag/genre graph relations and audio representations; this target is more nuanced but different. Official code expects node features, graph and labels; PyTorch Geometric/FAISS, GPL-3.0 code. No verified arbitrary-file inference checkpoint/adapter was established. | Promising research direction; unsuitable as a direct local-file drop-in without its graph and training pipeline. Require released inductive audio-only inference, weight identity/license and out-of-graph validation. [Paper](https://humrec.github.io/publication/peintner-tismir-2025/peintner-tismir-2025.pdf), [code](https://github.com/dbis-uibk/SRGNN-Emo). |
| DAMER / Memo2496, Dec 2025 | Dual mel/cochleagram, adaptive fusion and style-memory/contrastive components. Memo2496 contains 2,496 instrumental tracks with VA annotations by 30 specialists. Reports improvements using accuracy/AUC rather than our regression protocol. Code/data advertised on Figshare; web/API access did not yield a verified deployable checkpoint, exact runtime or separate licenses. | Instrumental coverage is interesting; no local implementation claim. Revisit when checkpoint, preprocessing, target discretization/scales and license are verified. No dataset audio downloaded. [Paper](https://arxiv.org/html/2512.13998v1), [advertised release](https://figshare.com/articles/dataset/Memo2496/25827034). |
| TPCNet, 2026 | Target-conditioned distributional emotion, CNN–BiLSTM/cross-attention and triple-path consistency. Distributional labels may represent mixtures better; not equivalent to independent sigmoid tags. Current search found unrelated same-name repos, not an authenticated deployable music checkpoint. Exact label ontology, weights, license and Apple CPU measurements remain unverified. | Paper-level candidate; request an official reproducible release before integration. [Publisher record](https://www.sciencedirect.com/science/article/abs/pii/S0950705126000614). |
| Multi-output continuous MER benchmark, Aug 2026 | Compares classical/sequence models on OpenSMILE, psychoacoustic and Librosa features; also probes MERT/HuBERT/wav2vec2 and a scratch Conformer. MERT has strongest absolute reported MED (0.201); random segment evaluation is not our held-out scene task. Article data statement cites public datasets but does not establish a ready inference artifact. | Supports careful music-domain baselines and paired testing; no reason to retrain a large ensemble here. CPU/checkpoint/licensing details unverified for a deployable bundle. [Primary article](https://link.springer.com/article/10.1007/s00521-026-12370-y). |

Larger MERT alone is a backbone, not a released supervised emotional estimator for arbitrary labels. Multimodal lyric models, speech emotion classifiers and streaming-provider features introduce target/data mismatches and extra inputs; none is silently adopted. FIGMA and other fine-grained approaches in the September 22 report remain research leads; this task does not implement an unverified release. MuQ-versus-CLAP stays separate.

## Generalization, uncertainty and licensing

Jamendo labels are uploader tags on Creative Commons music; they contain commercial themes and incomplete positives. Official artist-disjoint splits help within that dataset, but don't establish generalization to this DJ library's releases, languages or scene preferences. DEAM/PMEmo emphasize Western popular music; EmoMusic broadens genre coverage without proving cultural/language balance. Neither selected model exposes a calibrated per-track uncertainty distribution or listener-specific response. No exact overlap audit against private pretrained corpora was possible. Shared public training sources and random dimensional splits make leakage/domain overlap plausible concerns; no unsupported claim of confirmed leakage is made. [Jamendo dataset/splits](https://github.com/MTG/mtg-jamendo-dataset), [DEAM dataset](https://cvml.unige.ch/databases/DEAM/).

| Component | Code | Weights | Dataset/audio considerations |
|---|---|---|---|
| Music2Emo | Repository MIT; notice preserved | Released within repository; no separate comprehensive weight/data-rights statement verified | Uses multiple datasets and pseudo/teacher targets; code license does not grant rights to their audio |
| MERT-95M | Official implementation uses Transformers/HuBERT; this adapter uses installed Transformers | Model card CC-BY-NC-4.0 | Pretraining music rights do not follow from code availability |
| BTC | Upstream MIT, Jonggwon Park copyright retained | Bundled checkpoint; independent commercial grant not verified | Original training uses Isophonics/Robbie Williams/UsPop; source states audio excluded for copyright reasons |
| Essentia / heads | AGPL/commercial licensing framework | Official model terms include CC-BY-NC-ND-4.0; check individual/commercial license | Small MTG collections and public tagging/emotion datasets have separate terms |
| MTG-Jamendo | Dataset scripts Apache-2.0 | Not a weight license | Per-track Creative Commons notices; current repository restricts dataset use to noncommercial research/academic use without Jamendo permission |
| DEAM / EmoMusic / PMEmo | Separate dataset releases | Not interchangeable with model license | This task did not acquire dataset audio or establish commercial redistribution rights; audit originals before future training/distribution |

License sources: [Music2Emo](https://github.com/AMAAI-Lab/Music2Emotion), [MERT](https://huggingface.co/m-a-p/MERT-v1-95M), [BTC](https://github.com/jayg996/BTC-ISMIR19), [Essentia model terms](https://essentia.upf.edu/models/README.md), [Jamendo terms](https://github.com/MTG/mtg-jamendo-dataset#license). These are future commercial viability checks, not a blocker to the authorized private local experiment.

## Implementation and contracts

The optional stages are `emotion_music2emo` and `danceability_musicnn`; `estimator_reference` exists only for matched comparison evidence. Existing default stages are unchanged. `supervised-estimates-v1` stores exact ordered labels, full continuous scores, raw VA, model identity, `supervised-3x30s-v1`, total/sample duration, coverage, timestamps, per-window values and auxiliary key/mode/chord evidence. Strict Pydantic contracts reject nonfinite values, wrong dimensions/order/sets, overlap, inconsistent means and coverage. Regression values outside 1–9 are preserved unclipped; they never become high-confidence probabilities.

Sampling selects at most three nonoverlapping windows of at most 30 seconds, distributed from start to end; a single window is centered, subsecond sources fail explicitly. Means are weighted by excerpt duration. These are sampled track summaries, not continuous emotional trajectories. The exact windows and all per-window scores allow range inspection and later alternative aggregation. Windows for baseline and both challengers are identical. Historical full-track baseline remains separately identified.

Workers run sequentially, CPU-only, four requested threads, 4,096 MiB process-tree RSS limit and 600-second timeout in the smoke harness. Host available-memory checks remain active. Normal inference is offline. Setup downloads only pinned public weights/configuration (406,053,669 bytes total, excluding the retained research archive), with exact byte lengths/SHA-256 and atomic replacement. No audio is sent to model providers.

The code/model/sampling identity is hashed in `supervised.py`; pipeline checkpoint digests additionally include source hash, CPU settings, dependency/tool versions and model assets. Pinning `uv.lock` reproduces the tested environment. A dependency change invalidates pipeline reuse through recorded versions; web compatibility checks model/adapter identity and typed outputs, not the current environment's dependency versions. Historical estimates remain readable with provenance. The optional-stage manifest is intentionally one conservative bundle; even the dance-only worker currently verifies all bundle assets.

The pinned MERT configuration disables CQT, deepnorm and relaxed custom attention. Loading into the matching installed HuBERT architecture is strict and offline; missing/unexpected weights fail. An independent generated two-second signal comparison with the pinned official MERT source produced **zero maximum absolute error in every one of 13 hidden states**. This validates the substitution for this pinned configuration, not arbitrary MERT models. J_all loading accepts the exact 36 model tensors and explicitly ignores four known training-loss buffers; BTC uses tensor-only loading with a narrow allowlist for legacy numeric NumPy scalars.

### Projection and ranking

Profiles: `reference`, `music2emo`, `musicnn-dance`, `supervised`. Reference is default. Each challenger requires valid, same-model coverage for **every catalog candidate**. This is deliberately stricter than MuQ's post-hard-filter eligible-coverage gate. Partial/mixed-version coverage keeps reference values for everyone and adds a visible warning. No upgraded subset earns a hidden advantage.

Music2Emo replaces only `theme:*`, plus valid-scale valence/arousal mappings. `mood:relaxed` remains the independent binary MTG estimate: Jamendo `theme:relaxing` is a different label. Instruments, voice, genres, beats and MuQ remain intact. Danceability selection replaces only the binary danceable support. Profiles select a source; they do not average incompatible sigmoid, softmax, regression and cosine scales.

For a raw VA mean `r` within 1–9, `x=(r−1)/8`. Positive/high preference is `x`, negative/low is `1−x`, medium energy is `1−abs(2*x−1)`. These are named, provisional preference mappings, not empirical calibration. If any selected candidate's mean is outside range, that axis retains the reference for all candidates. Model identity, mapping name and warning authority remain in each contribution. Missing evidence never proves “low” or absence.

Catalog projection precedes the existing aggregate capability declaration, so the planner's soft enum reflects evidence actually available. No inferred lyric, personal taste, language or scene-truth fields are introduced. Hard MAEST top-six membership, exclusions, BPM limits/order and deterministic tie behavior remain unchanged. Existing 65/35 genre-feature, 3/2/1 priority and 30/70 semantic-structured weights are untouched. Stored catalogs, vocabulary, compiled queries and evidence preserve exact replay.

### App and migration

Analysis adds two experimental columns; Details retains full scores, units, coverage and windows plus the explicit one-track **Compare feature estimators / Check experimental estimates** action. Optional failures stay visible and usable older evidence survives failed upgrades. A base retry no longer erases a failed optional stage. No batch experiment starts by implication.

PlaylistIQ offers profile selection and an explicit **Compared tracks only** candidate set; defaults remain all analyzed tracks/reference. This lets the two-track development set be compared uniformly. The listening notebook records profile, candidate scope and exact result, restores them when reopening, and appends four scene prompts while preserving the original P01–P20 benchmark. App Status describes these capabilities and displays live optional coverage. Server mutation routes retain loopback/origin/header restrictions.

`integrate_supervised.py` admits only the two fixed smoke hashes and validated successful descriptor runs, checks model manifests and current identity, snapshots old cache JSON, and appends optional outputs. It verifies baseline/MuQ algorithm objects are unchanged. Browser cache retry executed **zero algorithms**, reusing all ten stages for Ocean. No original audio, existing playlist or playback record is rewritten by migration.

## Measurements, comparisons and limitations

Machine: macOS 26.5.1 ARM64, 16 GiB RAM, 10 logical CPUs. Tested Python 3.12 environment: Torch 2.13.0, Transformers 4.57.6, NumPy 2.5.3, librosa 1.0.0; optional pins Music21 9.3.0, PrettyMIDI 0.2.10, mir-eval 0.8.2, PyYAML 6.0.3, setuptools 80.9.0. No GPU/MPS performance claim. Peak RSS samples are process-tree observations at 0.2 seconds, not a guaranteed peak or a future concurrency budget. Host swap already existed before inference; RSS is not total host memory pressure.

| Source / stage | Elapsed seconds | Peak process-tree MiB | Sampled coverage |
|---|---:|---:|---:|
| Ocean / Music2Emo | 16.27 | 2108.0 | 90 s / 34.66% |
| Paradise / Music2Emo | 11.44 | 2067.6 | 90 s / 26.50% |
| Ocean / MusiCNN dance | 2.50 | 672.2 | same windows |
| Paradise / MusiCNN dance | 2.51 | 694.8 | same windows |
| Ocean / matched EffNet+DEAM | 4.37 | 1483.0 | same windows |
| Paradise / matched EffNet+DEAM | 4.59 | 1850.2 | same windows |

Six stages passed with original source hashes and folder inventories unchanged. CPU cost includes decode/model load/chord/key preprocessing and head inference. Two timings do not support throughput or whole-library cost projections.

| Matched-window output | Ocean | Paradise |
|---|---:|---:|
| DEAM valence / arousal | 5.3318 / 5.2951 | 6.4023 / 5.4898 |
| Music2Emo valence / arousal | 5.3877 / 4.8000 | 7.0432 / 6.9422 |
| EffNet danceable support | 0.426758 | 0.988660 |
| MusiCNN danceable support | 0.940455 | 0.971896 |

Music2Emo's strongest Ocean tags include documentary, sad, dream and calm; Paradise includes funny, energetic, party and retro. These illustrate disagreement and taxonomy limitations, not accuracy. The dance challenger compresses the two examples near the top of its scale; that is counterevidence to using it as an automatic cure for saturation. The full-track reference is different (Ocean dance about 0.293, Paradise about 0.997); matched-window and historical figures must not be conflated.

`compare_supervised.py` freezes both catalogs and all four profiles. It runs seven predetermined structured scene probes plus three previously recorded provider queries, including their existing semantic embeddings: **40 exact replays**, with contribution arithmetic checked at the engine's reporting precision. The scene probes are explicit diagnostic hypotheses, not new LLM interpretations or listener ground truth. Raw results, historical baseline and matched outputs remain in the [comparison manifest](../../output/supervised-estimators/comparison-v1/manifest.json). No weight/threshold calibration or title-specific rule was fitted.

## Listening evaluation: what remains unproven

The [prior feedback](../../../web-player/docs/SCENE_FIT_FEEDBACK.md) is retained: Manuel finds Ocean too calm for his energetic beach experience; Grecia accepts calm beach mood but associates this track more with a quiet after-date moment. This does not assign an objective romantic label or justify changing every beach request.

| Scene | Distinction to judge, independently of model scores |
|---|---|
| Calm beach | Low/moderate activation plus outdoor/social fit; intimacy is not equivalent |
| Energetic beach | Movement and positive activation without automatically maximizing aggression |
| Intimate evening | Romantic/soft foreground role and personal associations, not merely low arousal |
| Picnic | Pleasant background/social suitability, not arbitrary genre or BPM |
| Heartbreak | Sadness/valence and personal response; lyrical meaning remains unsupported |
| Celebration | Shared joy/activation; not every celebration is a dance party |
| Dance party | Groove/movement plus energy and useful variation; BPM alone is insufficient |

The [listening workflow and track lookup](../evaluations/SUPERVISED_LISTENING.md) accompanies separate Markdown/JSON sheets. The reusable development sheets blind estimator identity and randomize profile order separately for Manuel and Grecia. They contain **no entered judgments**. The organizer keeps the mapping separate; identical rankings remain valid ties. Reviewers rate perceived VA, movement, scene fit and personal induced feeling separately, without seeing scores. These two known smoke songs remain development examples.

For a quality decision, first obtain explicit corpus scope for additional analysis. Select an artist/release-disjoint held-out set, cover both beach interpretations and the remaining scenes, reserve it before tuning, and freeze profiles/windows/query plans. Use independent reviewers, equal loudness for listening without altering originals, randomized order and repeat a subset to assess consistency. Report per-scene pairwise preference/ties, relevance@k/nDCG when graded labels exist, MAE/CCC for VA when the scale is appropriate, per-label PR-AUC for actual tag labels, movement rank correlation, missing/invalid rates and uncertainty via track/artist-level resampling. Do not treat two reviewers or repeated ratings of one song as independent population evidence. Promote only with a consistent practical benefit and no important scene/constraint regression; otherwise keep the reference or choose per-feature specialists. This protocol is prepared, not executed.

## Failures and remaining engineering questions

- Initial public downloads failed under sandbox DNS; approved official-source acquisition succeeded. No audio transmitted.
- Upstream full requirements would alter the working stack. Minimal inference dependencies were pinned instead. PrettyMIDI required `pkg_resources`; setuptools 84 lacked it, so tested 80.9.0 is explicit.
- First model attempt failed strict J_all loading because four training-loss buffers were present. The fix allows exactly those known buffers, retaining strict model-key validation. The failed `matched-v1` run remains preserved; final successes are `matched-v2`.
- BTC legacy checkpoint required narrowly allowlisted numeric NumPy constructors. Unrestricted pickle was not enabled.
- Two initial package tests failed because macOS sandbox blocked swap telemetry. The same suite passed with host access, 481/481. No memory-guard behavior was weakened.
- Appending scene prompts initially broke two tests expecting exactly 20 prompts. Tests now verify the original 20 remain identical and four new cases are appended; 80/80 web tests pass.
- Comparison arithmetic initially used an unrealistically strict 1e-9 against rounded scores. It now uses 1e-5 for display-precision sums; complete replay objects remain exactly equal.
- Browser inspection exposed oversized inherited select labels; compact responsive controls were added. The native Chrome session was actively used, interrupting acceptance. Isolated browser acceptance avoids disturbing that session; Chrome coverage must be distinguished from cache coverage.
- One live intimate-evening planner proposal was rejected by existing local validation; no query accepted. The original response was not retained by that pre-existing failure path, so the exact rejected field is unknown. This remains a planner robustness gap, not evidence of estimator failure. Final live/browser result is recorded in the operations checkpoint.

Remaining questions include released J_all training/checkpoint provenance, culturally varied calibration, per-excerpt vs whole-song harmonic aggregation, long-track sampling bias, silent/very short input behavior beyond contract tests, and stage-specific asset/dependency minimization. None is hidden behind a “best model” claim.

## Final acceptance supplement

The second and final live request, “Energetic and danceable music.”, succeeded with profile `supervised`, two compared candidates and `hybrid-semantic-v1`. Paradise scored 0.825136 and Ocean 0.570411. The saved input catalog/query replays exactly. Reopening the notebook result restored both estimator profile and candidate scope without another request. 390px and 320px checks showed no document horizontal overflow and both controls inside the viewport. The in-app App Status showed 2 compared tracks.

A final cache-migration audit found that the old browser recovery code skipped already complete reference records. It now permits a richer same-hash optional cache to attach without reading/replacing audio or changing IDs; a dedicated regression covers this. Original Chrome refresh was interrupted by active use, so its final displayed optional coverage is not claimed. Backend coverage is exactly 2/113 cached records; the in-app acceptance set has 2/3 compared, with the third being an existing generated fixture. Prior Chrome 115-record/109-unique, 88-candidate figures are separately labeled in the checkpoint.
