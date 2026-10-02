# PlaylistIQ estimator research — reader summary

September 25, 2026. [Technical evidence and implementation specification](TOP_ESTIMATORS_2026-09-25.md).

The best path is a combination of specialists. Music2Emo alone does not fulfill the broader upgrade, and its 56 tags do not give us a richer emotional vocabulary.

| Feature | Selection | Why |
|---|---|---|
| Mood/theme and emotional positivity/intensity | Music2Emo, with its limitations explicit | Strong released joint predictor; broader research leaders do not all publish the trained emotion head |
| Nuanced emotions | SRGNN-Emo and cross-dataset alignment are research leaders to pursue | More relevant emotional targets; ready trained predictors were not found in the inspected releases |
| Happy, sad, relaxed | Keep current EffNet heads | They lead the matched released-head comparison |
| Aggression | VGGish head | Small published advantage; not yet a proven listening improvement |
| Vocal vs instrumental | MusiCNN head | Better published matched accuracy |
| Danceability | Keep EffNet | It beats the earlier optional MusiCNN alternative on the published task |
| Instruments | Add PaSST OpenMIC alongside Jamendo evidence | Strong released polyphonic specialist; five additional instrument labels, with separate scores for overlapping labels |
| Key | Try SheetSage2 first | Strongest reviewed matched key result with a released trained model |
| Tempo and beats | Keep Beat This | Still strong; SheetSage2 does not win every rhythm comparison |
| Loudness and metadata | Keep current measurements | These need accurate measurement, not a newer neural network |
| Genre | Keep MAEST | Outside this change, as requested |

The newest MERT-v2 representations lead several reviewed benchmarks. But an audio encoder produces features, not finished mood predictions. Its released files do not contain the trained mood heads behind those scores. Installing it alone would not reproduce that quality. The richer SRGNN work has a similar deployment gap: its inspected release provides training code and data features rather than a ready predictor for your tracks. [MERT-v2 release](https://huggingface.co/m-a-p/MERT-v2-30s), [SRGNN-Emo release](https://github.com/dbis-uibk/SRGNN-Emo).

Quality determined these choices. Mac speed was secondary, and licensing had no weight. Several existing choices survive because the evidence supports keeping them; other features get a different specialist. Music2Emo remains an evidence-based candidate, but neither its published benchmark nor successful installation proves it understands your music better. [Music2Emo paper](https://arxiv.org/html/2502.03979v1).

The [implementation checkpoint](../TOP_ESTIMATORS_IMPLEMENTATION.md) records the local installation, tests and measured runs, including failures. The main unresolved objective is more reliable, nuanced emotion detection. We must not describe that as solved by extra instrument labels, model installation or two-track smoke tests. A richer trained emotion release—or a separately evaluated training effort—is still needed to close that gap.
