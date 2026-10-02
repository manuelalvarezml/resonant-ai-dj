# PlaylistIQ: quality-first estimator selection

Research cutoff: 2026-09-25. Implementation specification, revision 1. This report supersedes the earlier assumption that adding Music2Emo alone fulfilled the estimator upgrade. Implementation and local measurements are recorded in [the implementation checkpoint](../TOP_ESTIMATORS_IMPLEMENTATION.md); the decisions below precede that work.

## Decision

Use a portfolio of specialists. Retain MAEST genre and MuQ retrieval unchanged. Select Music2Emo for the available joint mood/theme and valence/arousal path; add MusiCNN vocal detection, VGGish aggression, PaSST OpenMIC instruments, and attempt SheetSage2 key estimation. Retain Discogs-EffNet happy/sad/relaxed/danceability, Beat This tempo/beats, and standardized loudness. Retention is a research outcome, not a claim that every existing estimator is optimal.

The largest unresolved quality opportunity is **richer, reliable emotion prediction**. The strongest reviewed representation results and nuanced-emotion research do not all ship the trained prediction heads needed for inference. Installing their encoders does not reproduce those results. The implementation must report this gap plainly instead of manufacturing richer labels with an LLM or rebranding the same 56 labels.

Quality and evidence dominate this selection. Mac runtime affects execution strategy only after quality comparison. Licensing has no selection weight. No all-purpose numeric ranking combines incompatible datasets, targets, metrics or experimental splits. Within matched evaluations, compare the published metric; across evaluations, keep separate leader groups. “Available” means a released trained predictor with identifiable weights, preprocessing and label semantics—not merely an architecture, paper or encoder checkpoint.

## What the pipeline actually estimates

| Feature | Current evidence | Target and limitation |
|---|---|---|
| Mood/theme | EffNet Jamendo56; optional Music2Emo | Multi-label music annotations mixing emotion, occasion and theme; not 56 psychological emotions |
| Happy/sad/relaxed/aggressive | Four independent EffNet binary heads | Separate small MTG tasks; no mutually exclusive four-way emotion partition |
| Valence/arousal; energy preference | DEAM MusiCNN; optional Music2Emo | Raw regression; arousal is only a provisional energy interpretation |
| Danceability | EffNet binary head | Danceable vs not-danceable support; not calibrated continuous groove |
| Voice | EffNet binary head | Vocal vs instrumental, not lyrics meaning or singer identity |
| Instruments | EffNet Jamendo40 | Multi-label support, incomplete taxonomy and annotations |
| Tempo/beats/downbeats | Beat This final0, no DBN | Timing estimates; half/double-time ambiguity remains |
| Key | Essentia EDMA HPCP | Global tonic/mode estimate, currently analysis evidence rather than playlist constraint |
| Loudness | FFmpeg EBU R128 | Standardized measurement rather than learned prediction |
| Duration/codec/tags | FFprobe | Encoded facts; missing metadata stays missing |

Genre, retrieval/planner reasoning, stem separation, lyrics transcription, melody/chord transcription and personalized induced emotion are not silently added as new product features.

## Leading mood and emotion candidates

### 1. Strongest reviewed representation results: MERT-v2

The released MERT-v2-30s card reports MARBLE mood AP **.1668**, above the card's PupuJEPA-large **.153**, Dasheng **.155**, MuQ **.132** and MERT-large **.135**. Its instrument AP is .2289; FullSong reaches .2351. EmoMusic valence/arousal R² are .6323/.8001 for 30s and .6352/.7814 for FullSong. These are encoder-plus-task-probe results. The authors explicitly warn that copied baselines were not all rerun identically. The technical paper is not yet supplied. [Author model card](https://huggingface.co/m-a-p/MERT-v2-30s).

**Availability audit:** the inspected 30s release revision `5d9a407112c28ff8821fc17a9858406f4a7f85ad` contains encoder weights, configuration/code and benchmark metadata, but no trained mood, instrument or emotion-regression probe. FullSong likewise is a representation release. A plug-in encoder replacement under an old prediction head is invalid. Rank it first for a future trained-head reproduction, not as a completed mood installation. Source inventories are preserved under `output/top-estimators/research/`.

PupuJEPA is another strong representation candidate, but the inspected repository/linked model inventory supplies representation checkpoints, not ready PlaylistIQ emotion heads. The linked HF inventory currently uses PupuM2D names, so benchmark-to-release identity also needs resolution. [Author code](https://github.com/sizigi/PupuJEPA), [paper](https://arxiv.org/abs/2606.25713). Do not spend gigabytes downloading training optimizer states to call that an emotion implementation.

### 2. First verified released joint predictor: Music2Emo

The paper reports Jamendo PR-AUC **.1543**, ROC-AUC **.7810**, DEAM valence/arousal R² **.5184/.6228**, EmoMusic **.6512/.7616**, and PMEmo **.5473/.7940**. It explicitly targets categorical and dimensional emotion jointly. The available J_all weights and inference code make it actionable. [Paper](https://arxiv.org/html/2502.03979v1), [author implementation](https://github.com/AMAAI-Lab/Music2Emotion).

Selection is conditional: it is a credible released joint challenger, not a proven winner on this library. Its 56 Jamendo labels are unchanged. The paper scores do not certify the exact J_all deployment, our mode correction, or our three-excerpt aggregation. The existing implementation preserves those differences. Its EmoMusic valence result exceeds MERT-v2's reported value, while arousal does not; this itself rules out a universal mood winner. The regression target and sampling policy must stay visible.

### 3. Richer emotion taxonomy leader: SRGNN-Emo

SRGNN-Emo predicts nine GEMS dimensions using acoustic and relational information. On its reported setup, Jukebox-based SRGNN has RMSE **.7411**, R² **.4180**, versus DGI .7464/.4103. Some individual dimensions favor DGI, so even this comparison is not uniform. These are induced-emotion ratings and relational features, not Jamendo56 classification. [Author paper](https://humrec.github.io/publication/peintner-tismir-2025/peintner-tismir-2025.pdf).

**Availability audit:** inspected repository revision `faba51d8cea0d39f6457efa86386059609fd3e79` has training/evaluation code; its linked public Drive contains acoustic feature matrices, IDs and labels. No trained arbitrary-audio predictor was found in those release paths. Reproducing its graph/data setup is additional model development, not downloading a replacement head. This is the most relevant research direction for the user's request for subtler emotions. [Author repository](https://github.com/dbis-uibk/SRGNN-Emo).

### 4. Cross-taxonomy generalization

Cross-dataset emotion alignment maps MERT features into LLM label embeddings and evaluates transfer among Jamendo, CAL500 and Emotify. It is attractive for vocabulary expansion, but transfer scores are not interchangeable with in-domain mood accuracy. Its instructions require a user-supplied checkpoint or W&B artifact; the inspected release tree does not supply the trained predictor. [Author repository and results](https://github.com/AMAAI-Lab/cross-dataset-emotion-alignment).

Other reviewed contenders remain conditional rather than being promoted on headlines: BEE-MER/ASWEM uses audio plus lyrics and four quadrants ([paper](https://mir.dei.uc.pt/pdf/Conferences/MERGE/SMC_2025_Louro.pdf)); DAMER/Memo2496 uses a different instrumental dataset and discretized evaluation, with deployment weights/scale not verified; the linked Figshare inventory contains audio, features, labels and preprocessing files rather than a trained predictor ([paper](https://arxiv.org/html/2512.13998v1)); recent multimodal and distributional systems require release/target verification before selection. FIGMA is music-text retrieval, outside this direct-predictor comparison ([author page](https://nishitanand.github.io/figma-website/)). Caption richness is not evidence of calibrated emotion accuracy. CMI-Bench documents limitations of the audio LLMs it tested; it does not establish performance for later untested models ([benchmark](https://arxiv.org/html/2506.12285v1)).

## Matched released binary heads

The official metadata were fetched for five embedding families across the existing binary tasks. Entries below are published normalized five-fold accuracy, rounded to two decimals; no confidence intervals establish statistical significance. They support candidate choice, not a guaranteed real-world gain.

| Target | EffNet current | VGGish | YAMNet | MusiCNN | OpenL3 | Decision |
|---|---:|---:|---:|---:|---:|---|
| Happy | .87 | .86 | .85 | .84 | .79 | Retain EffNet |
| Sad | .90 | .89 | .89 | .85 | .88 | Retain EffNet |
| Relaxed | .91 | .89 | .90 | .89 | .87 | Retain EffNet |
| Aggressive | .98 | **.99** | .98 | .97 | .96 | Select VGGish; small uncertain gain |
| Danceable | **.97** | .94 | .94 | .95 | .82 | Retain EffNet; do not promote the earlier MusiCNN experiment |
| Voice | .96 | .97 | .97 | **.98** | .96 | Select MusiCNN |

Sources: [Essentia official heads](https://essentia.upf.edu/models/classification-heads/), [voice MusiCNN metadata](https://essentia.upf.edu/models/classification-heads/voice_instrumental/voice_instrumental-msd-musicnn-1.json), [aggression VGGish metadata](https://essentia.upf.edu/models/classification-heads/mood_aggressive/mood_aggressive-audioset-vggish-1.json). All fetched JSON files are archived locally. The voice benchmark has 1,000 tracks; aggression only 280. These sizes limit generalization claims.

For DEAM v2, MusiCNN and VGGish trade metrics rather than offering a clean replacement: valence R² .537 vs .524 favors MusiCNN; arousal RMSE .674 vs .673 narrowly favors VGGish, while CCC .647 vs .614 favors MusiCNN. The MusiCNN metadata contains a malformed arousal R² value `589`, which must not be interpreted as a valid score. [MusiCNN metadata](https://essentia.upf.edu/models/classification-heads/deam/deam-msd-musicnn-2.json), [VGGish metadata](https://essentia.upf.edu/models/classification-heads/deam/deam-audioset-vggish-2.json). Keep the reference for comparisons; use the joint Music2Emo branch for the selected available VA challenger.

No reviewed released continuous danceability predictor establishes a stronger human-annotated groove estimate. A rhythm-regularity formula or a regressor trained on unrelated Spotify features would change the target. Do not substitute one merely to increase the number of outputs.

## Instruments

Rank within OpenMIC: a later temporal-support study reports BEATs .870 and PaSST .869 mAP with newly trained pooling heads; those exact heads were not verified as released. The official PaSST inference package provides a **.85 mAP** OpenMIC checkpoint with 20 labels, making it the first verified deployable specialist reviewed here. The older v0.0.4-openmic registry URL returned 404; the maintained `hear21passt==0.0.26` registry resolves the v0.0.5 `openmic-passt-s-f128-10sec-p16-s10-ap.85.pt` asset. [Study](https://arxiv.org/html/2312.14005v1), [PaSST code and checkpoint registry](https://github.com/kkoutini/PaSST).

The 2026 DC-GAT paper claims improvements over its own baselines, but its OpenMIC table reports .75 mAP and does not compare PaSST. Its dataset description/protocol also differs. It is not grounds to displace PaSST. [Full paper](https://www.nature.com/articles/s41598-026-53872-y_reference.pdf).

Jamendo40 is a different taxonomy/protocol: current EffNet AP .20/ROC .78 beats the reviewed Discogs embedding variants; MERT-v2 probes offer higher reported AP but unavailable heads. Thus retain Jamendo40 evidence and expose PaSST's independent OpenMIC20 labels with explicit provenance. Never turn a missing OpenMIC class into absence, conflate generic guitar with acoustic/electric guitar, or average unrelated model probabilities. The vocabulary expansion adds specific supported instruments, not more emotion labels.

## Tempo, beats, downbeats and key

SheetSage2's released model card reports a matched key comparison: GiantSteps **77.73** vs SKEY **72.09** and madmom **74.62**; GTZAN **75.77** vs **74.43** and **72.05**. It ships a trained adapter over MERT-v2 FullSong. Select it first for key, subject to actual local validation. Evidence is an author model-card evaluation; its technical report is forthcoming. [Release and benchmark](https://huggingface.co/m-a-p/SheetSage2).

This does not justify replacing all rhythm outputs: that card's GTZAN beat F1 is **86.27**, below Beat This **89.01**, while downbeat F1 **80.45** exceeds **78.28**. Keep Beat This tempo/beats. SheetSage2's downbeat evidence is promising but should remain separately identified until its event path is tested. Engineering selection for the existing joint rhythm stage remains Beat This: preserve its internally consistent beat/downbeat grid and stronger GTZAN beat result. This does not claim it wins the isolated downbeat metric. SheetSage2 downbeat replacement is not implemented by the key-only adapter. SKEY is the verified smaller key fallback, with an actual trained checkpoint and pitch-equivariant inference; choose it only if the first-ranked release cannot be executed reliably, and record that reason. [SKEY paper](https://arxiv.org/html/2501.12907v2), [code](https://github.com/deezer/skey).

BeatFM reports improvements over Beat This in its experiment, including MusicFM downbeat F1 79.6 vs 75.5. A corresponding ready inference checkpoint was not found in the reviewed paper/release paths; do not fabricate a deployment. [Paper](https://arxiv.org/html/2508.09790v1). Retain Beat This final0 with its raw events and half/double-time diagnostics, rather than forcing a single tempo certainty.

Loudness, duration and encoded metadata need correct measurement and decoding, not a newer neural model. Preserve the current implementation and its provenance. Key confidence from different algorithms is not interchangeable.

## Implementation contract

1. Add separately versioned, optional specialist stages. Pin checkpoint, source, labels and preprocessing hashes. Explicit setup may download model assets; inference must be offline. Preserve prior caches and reference outputs.
2. Add a quality-selected profile: Music2Emo theme/VA plus MusiCNN voice, VGGish aggression and PaSST instruments. Retain the evidenced current heads for happy/sad/relaxed/danceability. Never quietly substitute the lower-scoring MusiCNN danceability experiment.
3. Model choice must be uniform for each feature across a compared catalog. Missing or incompatible stage coverage falls back for that whole feature, with a visible warning. New labels require complete coverage from their own model. Keep raw values, sampling intervals, sources and warnings inspectable.
4. Key is separate analysis evidence. Add the selected key estimator without modifying the genre or planner policy. Compare disagreement rather than asserting the new key is ground truth.
5. Run one or two already authorized exact sources only. Verify hashes before/after; measure worker time/RSS/swap; keep sequential bounded workers. Record failures and actual dependency compatibility. No new dataset download/training, corpus-wide analysis, remote audio or cloud work.
6. Validate contracts, label order, aggregation, cache invalidation, missing coverage, profile isolation and web persistence. A smoke test establishes executability, not emotional accuracy. Leave human listening ratings blank until supplied.

## Remaining evidence needed for a quality claim

The two-track smoke cannot prove better emotion recognition. A meaningful subsequent comparison needs blind, repeated owner judgments of target emotions, vocal presence, instrument presence and prompt fit on a diverse authorized set, with the same excerpts across models. Separate perceived music mood from autobiographical associations and induced feeling. Report per-target gains, losses and uncertainty; do not collapse everything into one accuracy number. Training a richer GEMS or MERT-v2 predictor is a separate reproducible development effort if a suitable trained release remains unavailable.
