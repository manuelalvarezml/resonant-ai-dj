# PlaylistIQ estimator upgrade — research and implementation decision

Date: 2026-09-22. Owner requested further research on the attached hybrid-estimator report, a decision, immediate implementation and small pipeline tests. This document separates published evidence, engineering judgment and measured local results. Implementation evidence lives in [the work log](../ESTIMATOR_UPGRADE.md).

## Decision

Build a **hybrid local estimator and retrieval system**: MuQ-MuLan-large for musical descriptions; the Essentia Discogs-EffNet Jamendo 56-label mood/theme and 40-label instrument heads for interpretable acoustic evidence; retain MAEST, Beat This, KeyExtractor and standardized loudness. Preserve the four historical mood heads for comparison and compatibility. Expose DEAM valence alongside arousal as an estimate, not emotional truth. Cache segmented semantic embeddings and use a separate, explicitly provisional ranking branch.

This is the best-supported implementation choice for our current machine and creative-prompt problem, **not a demonstrated universal best mood estimator**. Success means a working, auditable pipeline first. Better recommendations require listener judgments; two smoke-test tracks cannot establish quality superiority.

### Why a single mood model cannot fix the beach example

“Un día en la playa” names a setting without choosing between quiet sunbathing, social afternoon or dancing. Manuel and Grecia also disagree about energy, and Grecia rejects the calm example as intimate after-date music. Four scores cannot express that difference. More labels help, but the planner must preserve the intended musical scene, and similarity must distinguish calm/open/airy from calm/intimate/sensual. It must disclose assumptions and accept clarification. Neither a song title, minor key, loudness nor an LLM's knowledge establishes the listener's desired mood.

We estimate **expressed musical character**. Induced emotion, personal memories, lyric meaning and situational appropriateness are different targets. A high similarity score supports an acoustic comparison; it cannot certify a good beach choice. Saved feedback remains evaluation data, not fabricated ground truth or a hidden rule that boosts/rejects a particular song.

## Candidate assessment

| Candidate | Verified evidence | Decision for this build |
|---|---|---|
| MuQ-MuLan-large | Official music/text model, 24 kHz input, 512-dimensional shared representation, serial ten-second processing; code recommends fp32. English and Chinese are explicitly supported. | Main semantic branch; planner supplies concise English musical descriptions for Spanish requests. Raw cosine remains separate from classifier outputs. |
| Essentia Jamendo mood/theme + instrument heads | Released Discogs-EffNet-compatible heads with 56 and 40 independent labels. Reuse the embedding already needed for existing heads. | Install both. Keep every score plus temporal summaries; distinguish theme labels from emotions. |
| Music2Emo | MERT plus key/chord features; multitask emotion regression and 56-label classification. Official wrapper returns thresholded labels, though sigmoid scores exist internally. | Supervised challenger, not silently substituted as a tiny EffNet head. Its extra preprocessing and different dependencies need their own controlled comparison. |
| FIGMA, ACL 2026 | New retrieval model with promising author-reported fine-grained retrieval results. Released implementation uses MuQ + multilingual E5 and global cosine at inference. | Strong next ablation, not assumed better for occasion/mood requests from attribute-heavy benchmarks. |
| CLaMP3 | Multilingual aligned music representations, with longer context and audio/symbolic possibilities. | Reserve comparison for multilingual/retrieval evaluation; avoid three large model runtimes before evidence. |
| Commercial mood APIs | Potential broader taxonomy, but opaque calibration, recurring service dependency and audio transfer. | No account, upload or API execution in this local solution. |

### Primary evidence and caveats

**MuQ.** The [official repository](https://github.com/tencent-ailab/MuQ) documents 24 kHz MuQ-MuLan inference, fp32, serial processing and separate code/weight licenses. The [model repository](https://huggingface.co/OpenMuQ/MuQ-MuLan-large) is pinned for this build to `2e01c796b71dca71b45251384c04cd7b237c9020`. Its configuration names an upstream MuQ audio encoder and XLM-R base text encoder. The [MuQ paper](https://arxiv.org/abs/2501.01108) supports music-representation potential; its tagging results do not validate our scene-ranking policy. Our implementation must pin auxiliary configurations/tokenizer as well as the top checkpoint. Loading an unpinned nested model on every request would defeat reproducibility.

**Music2Emo.** The [official implementation](https://github.com/AMAAI-Lab/Music2Emotion) reports Jamendo PR-AUC 0.1543 / ROC-AUC 0.7810 for its joint-data model and regression results on DEAM, EmoMusic and PMEmo. Those datasets and metrics are not directly comparable to free-text retrieval recall. Its `predict` wrapper thresholds sigmoid outputs at 0.5 and returns valence/arousal. A future adapter must expose the full vector, pin MERT/chord/key assets and record segment aggregation. The [paper](https://arxiv.org/abs/2502.03979) motivates combining complementary musical information. Our decision to keep it as a challenger is an engineering judgment, not a finding that EffNet is more accurate.

**FIGMA.** The [project results](https://nishitanand.github.io/figma-website/) report MusicBench text-to-audio R@1 of 34.52 versus 28.43 for CLaMP3 and 20.81 for MuQ-MuLan, and FMACaps-Eval 13.00 versus 7.50 and 4.10 respectively. These are author-reported comparisons with particular candidate sets, not expected PlaylistIQ acceptance rates. The [paper](https://arxiv.org/abs/2606.06615) studies fine-grained attributes and frame/token training. Crucially, [released source](https://github.com/nishitanand/FIGMA/blob/main/figma_model.py) explicitly uses global embeddings at inference. The model's 22M trainable parameters omit frozen backbones; deployment is not a 22M-parameter workload. The [model card](https://huggingface.co/nishitanand/FIGMA) describes English-centric captions and noncommercial research weights. Code review also found permissive checkpoint loading and unpinned nested downloads; a future production adapter must tighten both.

**CLaMP3.** The [model card](https://huggingface.co/sander-wood/clamp3) describes multilingual text and music embeddings, with audio derived from MERT. The [paper](https://arxiv.org/abs/2502.10362) studies cross-modal alignment. The appropriate comparison is common prompts, common tracks and independent listener judgments. A multilingual encoder is useful, but it does not resolve cultural or personal interpretation automatically.

**Essentia.** Official [mood/theme metadata](https://essentia.upf.edu/models/classification-heads/mtg_jamendo_moodtheme/mtg_jamendo_moodtheme-discogs-effnet-1.json) and [instrument metadata](https://essentia.upf.edu/models/classification-heads/mtg_jamendo_instrument/mtg_jamendo_instrument-discogs-effnet-1.json) define the class order and compatible graph. Pin both metadata and graph hashes. A theme like Christmas, documentary or corporate is not a feeling. Preserve the exact label and axis; never present every label as a mood, nor assume these independent scores sum to one.

## Parameter-by-parameter implementation

- **Mood, atmosphere, movement, texture:** use curated descriptive phrases in the shared audio/text space, plus the supervised Jamendo vector. Include intimate, romantic, wistful, melancholic, hopeful, tense, playful, triumphant, airy, spacious, dark, warm, dreamy, hypnotic, driving and bouncy distinctions. Curated concepts are retrieval probes, not newly trained classifiers.
- **Instruments:** use all 40 head outputs as soft evidence. A weak score is not proof that an instrument is absent. Avoid hard exclusions without an evidence policy that supports them.
- **Energy:** keep raw DEAM arousal; expose raw valence too. Existing 1–9-to-preference mapping remains explicitly unvalidated. Do not derive energy from BPM or LUFS. Loud but sparse music and quiet fast music exist.
- **Genres:** keep MAEST's 519 independent scores and top-six eligibility. Preserve current parent-family matching and probability-aware weighting. An estimator upgrade is not authorization to silently change genre policy.
- **Rhythm:** retain Beat This; report beat-interval spread and half/double-time hypotheses when meaningful. These are diagnostics, not three simultaneous true tempi or calibrated confidence.
- **Key:** retain KeyExtractor's strength and label uncertainty. A global key can hide modulation; low strength must remain visible. Do not use key as an emotion proxy.
- **Vocals/danceability:** retain head scores with accurate wording. Mean voice support is not the fraction of seconds containing vocals. Saturated danceability in this library is an evaluation concern, not proof that all tracks suit a dance floor.
- **Loudness/duration:** preserve measured LUFS and encoded duration. Neither supplies missing semantic facts.

## Retrieval and scoring contract

1. Local source hashing and measurements remain separate from LLM planning.
2. The planner emits a short English description of audible musical character, and optional separate negative musical descriptions. Context and assumptions stay visible in the user's language. No audio leaves the machine.
3. Local text embedding is compared against cached audio segments. Retain mean and range and exact phrases; do not claim the best matching excerpt represents the whole track.
4. Apply explicit eligibility rules first. A semantic match never overrides BPM or genre constraints.
5. Fuse **relative ranks**, not raw classifier support plus raw cosine. Preserve structured evidence points and semantic points independently. Proposed initial semantic share is 30%, with 70% structured score, subject to listening evaluation. Similarity-only requests can use the semantic branch alone when structured objectives are unavailable.
6. Enable fusion only with complete compatible embedding coverage of eligible candidates. Otherwise return the unchanged structured ranking and a clear upgrade/coverage warning; never silently reward only the freshly analyzed subset.
7. Missing/failed semantic inference falls back visibly. Negative descriptions are contrastive preferences, not proof of absence and not hard exclusions. Do not use `1 - cosine` as a probability.
8. Determinism is for fixed query embeddings, catalog, versions and policy. Store those inputs or their content hashes for replay. New fields are versioned and old records remain readable.

Relative ranking is provisional: the best of a poor library may still be a poor match. Equal similarities must tie. One eligible track gives no comparative evidence and should not get a fabricated perfect semantic score. Longer-term fusion should be learned/calibrated on held-out listener judgments, not tuned until this one example wins.

## Runtime, preservation and cache policy

Use one CPU worker at a time, fp32 and bounded ten-second segments distributed over the track. The first policy samples up to three segments; display sampled duration/coverage and preserve timestamps and segment embeddings. This is an economical track summary, not exhaustive analysis. Full-track sliding windows are a separate measured policy. Decode bounded windows with ffmpeg instead of keeping an entire long file in memory.

Model acquisition is an explicit setup action. Normal inference is offline, with pinned revisions and file hashes, no model downloads or remote code execution. Cache identity includes source SHA-256, model identity, sampling policy and descriptor-bank version. Store failures as failures, not zero vectors. Keep old completed stages and rerun only missing or incompatible stages. Do not mark a historical seven-stage record as upgraded merely because its old status is complete.

For this machine, prioritize reusable small heads and a single semantic model. Avoid concurrent TensorFlow/PyTorch residency. Preserve the existing analysis environment where possible. Log actual peak RSS, time, failure and retry evidence before suggesting larger runs. Agent-run acoustic checks stay bounded to one or two tracks from the established authorized corpus.

## Evaluation needed before claiming better recommendations

First validate mechanics: score dimensions/finiteness, source hashes, exact class order, cache invalidation, model identity, hard constraints, missing-data fallback, deterministic replay, UI labels and score arithmetic. Then compare the current baseline, expanded labels, semantic retrieval and hybrid ranking on the same candidate library.

Begin listening review with beach (energetic and calm variants), post-date intimacy, picnic, heartbreak, dance party, study, tension, celebration and unspecified-recipient prompts. Record track-level relevance, scene errors, false lyrical claims, diversity and playlist-level acceptance. Preserve the original beach counterexample without forcing its label. Recruit Manuel and Grecia as separate judges: disagreement is information, not annotation noise to erase.

For a larger benchmark, aim for 30–50 diverse prompts and approximately 200 genre-balanced tracks, split by artist/release, with randomized blind comparisons and confidence intervals. Use nDCG/recall for ranked relevance, label PR-AUC and regression errors only where appropriate labels exist, and measured time/RAM. Test Spanish prompts through the planned English musical paraphrase versus direct text. Add FIGMA and Music2Emo only as controlled ablations. Personalization can eventually learn from explicit judgments, with a separate cold-start policy.

## Scope and adoption gates

The full selected solution is the hybrid pipeline above, not every candidate listed. No commercial account, audio upload, cloud service, new source folder, full-library reanalysis or training run is part of this implementation. Model licenses are recorded for future product decisions. Research weights are not represented as commercially cleared.

Adopt the new runtime after bounded smoke tests and regression checks. Enable result fusion only when coverage permits. Expand library analysis through the existing explicit Analyze action; old results remain available in the meantime. Listening quality, calibration, exhaustive temporal modeling and trained personalization remain open evidence questions.


## Implementation outcome and recommendation after testing

The full selected pipeline is implemented. **442 Python tests and 77 web tests pass**; two authorized songs completed real expanded-head and MuQ processing, exact source-preservation checks, cache reuse and Chrome attachment. Peak observed MuQ RSS was 2814.9 MiB; its two stage times were 17.33 and 13.25 seconds. Three creative cases were exercised through actual planning, local text embedding, ranking and replay, with seven calls across prompt revisions. Final planner v1.6 restricts soft preferences structurally to available catalog evidence; a language fix alone had failed to prevent an unsupported warm field. Full failures and commands are in the [implementation log](../ESTIMATOR_UPGRADE.md).

The important counterevidence is that MuQ's semantic-only branch still preferred the house example for the intimate-evening description, with weak negative cosines. The combined score retained Ocean first but reduced its lead. The new system therefore provides richer, auditable evidence and working retrieval infrastructure; **these tests do not demonstrate better mood accuracy or solve the beach counterexample**. I recommend using this as the measured baseline for listening comparisons, keeping FIGMA and Music2Emo as active challengers. A model should earn the label “best for PlaylistIQ” on our judged prompts and library.

The application avoids partially upgraded-library bias: fusion requires compatible embeddings for all eligible tracks; newly added theme/instrument/valence objectives with incomplete eligible coverage are omitted for everyone. Only the two smoke tracks were upgraded in this task. No claim of full-library semantic readiness, calibrated confidence, new listening verdicts or commercial weight clearance is made.
