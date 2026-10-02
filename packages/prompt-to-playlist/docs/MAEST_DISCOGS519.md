# MAEST Discogs519

## MAEST Discogs519 genre comparison (2026-09-13)

The optional `genre_maest` algorithm uses `discogs-maest-30s-pw-519l-2`
with its integrated 519-class Discogs classifier. It reads the explicit sigmoid
node `PartitionedCall/Identity_13`, not the logits node. The previous Jamendo
87-label/EffNet model and all six default stages remain unchanged.

From this package directory, run the 37-song comparison in your terminal:

```sh
uv run --locked --extra analysis prompt-playlist analyze-folder \
  --folder ../../test_folder_37_tracks_diff_genres \
  --output-dir output/maest-discogs519-diverse-37 \
  --algorithms metadata genre_maest \
  --model-dir output/maest-models \
  --all-tracks --cpu-threads 4 --resume
```

The model is already downloaded into ignored `output/maest-models` and both
assets are SHA-256 pinned in `model_assets.py`. The MAEST graph alone has a
384 MiB download ceiling; all previous assets retain the 256 MiB ceiling.
No additional dependencies are needed beyond the existing analysis extra.

Read `output/maest-discogs519-diverse-37/genre-top10.json` after completion:
filenames, source hashes, status and ten descending `{genre, probability}`
entries per song. Probabilities are independent multi-label scores in [0,1],
not calibrated certainty and not normalized to sum to one. All 519 scores,
patch counts, model provenance, preservation checks and telemetry remain in
`descriptor-run.json`. A failed track stays visible with an empty top ten and
an error. `warning` means the result is an unverified estimate, not a failed run.

Inference covers the full decoded song at 16 kHz, using 1876-frame patches,
1875-frame hop, batch size one, repeating the final partial patch. Song scores
are the arithmetic mean of patch probabilities. Sequential workers retain the
existing RAM/time guards. `--resume` reuses successful hash/config/version-
verified checkpoints and retries missing/failed stages. Ctrl-C may leave the
final review file unwritten; rerun the same command to finish from checkpoints.
Keep the output separate from both source music and the old descriptor runs.

Setup verification used only the first diverse song: 109.584 s audio, four
patches, 18.18 s MAEST wall time, 2289.0 MiB peak RSS, zero failures and unchanged
source hashes/inventory. The 37-song MAEST run is prepared, not executed.

Official sources:
- https://essentia.upf.edu/models/feature-extractors/maest/discogs-maest-30s-pw-519l-2.json
- https://essentia.upf.edu/reference/std_TensorflowPredictMAEST.html

## 2026-09-13 — MAEST listening-review checkpoint

The user-run MAEST diverse-37 output has 33 genre results and four RAM-limit
failures; fresh source hashes all match. A standalone `listening-review.html`
is now beside those outputs. See the DJ project’s `tools/genre-review/README.md`
for regeneration, review semantics and verification limits. No audio analysis
was rerun. The earlier “full run not executed” checkpoint is superseded by
this audit; no genre-quality acceptance or model replacement is implied.
