# Music2Emo inference subset

Source: https://github.com/AMAAI-Lab/Music2Emotion/tree/c5f7984f78d9928b841f25bd05a47377c12c58ca . MIT license retained in LICENSE.

Copied architecture and chord/key preprocessing; removed training/UI/evaluation imports. Relative imports isolate package names. Explicit asset/work directories replace shared working-directory deletion. SoundFile reads generated WAV excerpts. Safe checkpoint loading, strict state validation, eval/inference mode and local HuBERT-compatible MERT loading are owned by runtime.py. Full scores replace thresholded-label output. Corrected mode encoding to use parsed key_type (upstream loses mode after retaining tonic only). BTC normalization, chord ordering, first-100-event truncation, padding and Music21 chord-MIDI key estimation otherwise follow upstream. Sampled 3×30s aggregation is PlaylistIQ policy, not the published full-track benchmark protocol.

BTC code also derives from https://github.com/jayg996/BTC-ISMIR19 . Its original MIT notice (Copyright 2019 Jonggwon Park) is retained as LICENSE-BTC. Weight licensing and underlying dataset audio rights are separate; see the September 25 research report.
