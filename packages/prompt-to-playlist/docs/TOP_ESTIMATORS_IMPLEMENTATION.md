# Quality-selected PlaylistIQ estimators — implementation checkpoint

2026-09-25. [Technical research](research/TOP_ESTIMATORS_2026-09-25.md) · [Reader report](research/TOP_ESTIMATORS_DIGEST_2026-09-25.md) · [Owner brief](TOP_ESTIMATORS_NEXT_TASK.md).

## Delivered locally

The quality-first research covers every existing non-genre direct feature. Its released-model selection is implemented as the `quality` profile, now the **web UI default**. Reference, Music2Emo-only and the earlier dance experiments remain selectable. Genre remains MAEST top-six; MuQ and planner/ranking weights are unchanged.

The profile uses the existing Music2Emo theme/VA integration, adds **MusiCNN vocal presence, VGGish aggression and PaSST OpenMIC20 instrument evidence**, and retains EffNet happy/sad/relaxed/danceability. **SheetSage2** supplies the selected analysis/browser-filter key when available; the old EDMA result stays in Details. Beat This remains the coherent tempo/beat/downbeat stage. The new key adapter does not claim to implement SheetSage2's rhythm or transcription tasks.

This delivers the strongest usable selection supported by the reviewed evidence, with explicit exceptions. It does **not** deliver a demonstrated improvement in nuanced emotion recognition or expand Music2Emo's 56-label mood vocabulary. MERT-v2 and richer-emotion research leaders remain ahead-of-deployment candidates because the inspected releases lack the required trained emotion heads. No local listening superiority has been established.

Exactly **two** authorized local sources have the complete new profile. Larger library reanalysis is not performed. Selecting the quality profile for a larger catalog retains reference evidence for any target lacking complete compatible coverage; it never rewards only the upgraded subset. “Specialist tracks only” makes the two-track comparison accessible. In a larger browser library, this is a coverage gate, not automatic batch analysis.

## Model and inference contracts

The packaged `specialist_assets.json` pins **43 assets / 3,392,327,840 bytes** from official releases. Setup verifies exact sizes and SHA-256 hashes. Inference verifies only the requested stage's assets and never downloads. Stage identity covers the relevant asset records, adapter file and dependency versions. Existing Music2Emo code/identity is unchanged.

| Stage | Predictor / identity | Inference |
|---|---|---|
| `vocal_musicnn` | `voice_instrumental-msd-musicnn-1` + `msd-musicnn-1` | 16 kHz mono; up to three non-overlapping 30 s excerpts; mean patch support then duration-weighted mean |
| `aggression_vggish` | `mood_aggressive-audioset-vggish-1` + `audioset-vggish-3` | Same excerpt selection; official VGGish embedding output and binary head |
| `instrument_passt` | PaSST v0.0.5 `openmic-passt-s-f128-10sec-p16-s10-ap.85.pt`; `hear21passt==0.0.26`, `timm==0.4.12` | 32 kHz mono; each selected 30 s excerpt split into three 10 s inputs; 128 mel bins, 800-sample window, 320 hop, 1024 FFT, eval-mode normalization; sigmoid then duration-weighted mean |
| `key_sheetsage2` | SheetSage2 revision `55bfe14e32d8b663629b3a86b0f3285c2ca5da0b`; parent MERT-v2 FullSong `d8ba1c745e733b3908ce6ad16ebeb17ac7600a42` | Full song; upstream paper window/prefix policy; timestamp+key prompts; CPU float32; major/minor key intervals; global key by longest total duration |

SheetSage2 loads the hash-verified local package directly. Its parent weights/code are also verified against the upstream expected hashes; adapter merging is float32. SoundFile replaces an obsolete Torchaudio file-decoder API, while upstream channel averaging and Torchaudio resampling remain. The resulting deployment is not asserted to exactly reproduce the paper preprocessing or its aggregate score.

PaSST's 20-class order was checked against OpenMIC's official `class-map.json`. Its `openmic:*` preferences remain distinct from `instrument:*` Jamendo scores. Five additional exact instrument names are banjo, cymbals, mallet percussion, mandolin and ukulele. Overlapping names are separate model evidence, not new semantic concepts. No probability averaging or automatic acoustic/electric-guitar substitution occurs.

Typed contracts reject invalid label order/sets, non-finite/out-of-range support, inconsistent aggregation, overlapping/out-of-bounds excerpts and malformed key intervals. Key confidence is not invented from interval duration. All new scores are benchmark estimates with warning status, not calibrated probabilities. Sampled coverage is explicit; the key stage covers the whole song.

## Setup and use

From `packages/prompt-to-playlist`:

```sh
uv sync --locked --extra analysis --extra semantic --extra supervised --extra specialists
uv run --no-sync python scripts/setup_supervised.py
uv run --no-sync python scripts/setup_specialists.py
```

The local installation and model download are already complete on this Mac. The additional PaSST packages are isolated in the optional `specialists` extra; catalog-only use does not require audio ML dependencies. The pinned model root defaults to `output/top-estimators/models`; override with `PLAYLISTIQ_SPECIALIST_MODELS`.

In Resonant, use a track's Details → **Upgrade selected specialists** (or **Check selected specialists** after completion). The PlaylistIQ selector defaults to **Quality-selected specialists**. Reference remains available for comparison. The existing bulk Analyze Tracks action does not silently run the new optional specialists. Analysis shows selected key, retained reference columns, specialist outputs and source identities. Library key sorting/filtering uses the selected SheetSage2 key when present. Saved attempts retain estimator profile and candidate scope.

For a bounded regression, `scripts/smoke_specialists.py` accepts only the two pinned source filenames/hashes, one optional stage and a simple output run name. It uses sequential workers, a 4,096 MiB cap for classification, 8,000 MiB for the larger key model and a 1,024 MiB host-available-memory gate. Source hashes and source-folder inventory are checked. Do not turn this into a larger corpus run without its existing authorization boundary being met.

## Measured local evidence

Final run: `output/top-estimators/runs/final-v4`. Durable compact evidence: [eight-stage smoke results](evaluations/top-estimators-smoke-2026-09-25.json).

| Source | Voice s / MiB | Aggression s / MiB | Instruments s / MiB | Key s / MiB |
|---|---:|---:|---:|---:|
| Listen Over the Ocean | 4.08 / 654 | 17.19 / 3,686 | 12.94 / 1,285 | 58.05 / 3,342 |
| My Paradise - Edit | 4.02 / 690 | 16.58 / 3,625 | 12.72 / 1,282 | 112.00 / 3,407 |

All **8/8 stages passed** with warning status for estimation uncertainty; zero final failures. Both source hashes and inventories were unchanged. The machine already had about 3.3 GiB swap in use; host swap rose by about 118 MiB during the Ocean aggression worker and stayed flat during subsequent stages. This is host telemetry, not attribution of every swapped page to the model. No GPU/cloud execution or external audio transmission occurred.

New key outputs are C minor / 5A for Ocean and D# minor / 2A for Paradise. These are predictions, not accepted listener truth. Voice supports are .6093 / .9077 and aggression supports .0388 / .5056. PaSST's leading outputs are synthesizer for both tracks. Such numbers demonstrate valid output paths, not correctness.

The two same-hash web records now preserve their previous ten stages plus four specialists. `attach_specialist_smoke.py` validates source identities, model identity, preservation gates and each stage contract before attachment; it saves prior cache history. Bridge retry executed **zero** stages for both tracks and reused all fourteen. Fixed-query comparison produced **26 exact replays**, including new instrument targets and planner capability-schema availability; no provider requests or listener ratings were generated.

## Failures and repairs retained

- The old PaSST v0.0.4-openmic URL returned 404. The maintained inference package's v0.0.5 asset was downloaded and pinned; strict state loading passed. Its convenience wrapper also used an obsolete architecture alias, so the adapter constructs `arch='openmic'` explicitly with downloading disabled.
- SheetSage2's first attempt failed when Transformers' dynamic source copier omitted a transitive local module. Loading the verified local package directly resolved it. The second failed on removed `torchaudio.info`; SoundFile waveform input resolved it. Both failed descriptor runs are retained under `specialists-v1` and `local-import-v2`; `soundfile-v3` records the first successful full-song key run.
- Cache attachment initially rejected valid serialized key intervals because strict Pydantic tuple validation received decoded JSON lists. JSON-mode validation fixed this without changing or rerunning the model. A round-trip regression prevents recurrence.
- Two initial tests could not read macOS swap telemetry in the filesystem sandbox. The approved telemetry-enabled run passed. An added web request test initially omitted its required artist field; the fixture was corrected.

## Verification and remaining limits

Final Python regression: **502 tests**. Web: **83 tests**, syntax checks for **45 JavaScript modules**, **28-file** production build. Wheel and source distribution build successfully; the current wheel includes the specialist module and pinned asset manifest. Tests cover profile isolation, per-target uniform fallback, taxonomy/aggregation validation, JSON persistence, stale identity rejection, zero unsupported instrument evidence, hard-constraint preservation, cache migration and visible provenance.

Browser verification checks are recorded with the final UI acceptance below. The original large Chrome library is not reanalyzed or asserted to have complete new coverage. Audio inference stayed limited to the two named sources. No commitments, uploads, cloud rollout, commits or YAML migration are part of this change.

Next quality evidence must come from blind, predeclared listening/annotation on an authorized diverse set, plus a reproducible trained richer-emotion head if available. Do not mark that outcome complete based on installation or these two songs. To revisit a leading model, inspect the linked release inventory for its task head, verify exact target/split/checkpoint identity, then compare on matching inputs before changing this selection.


### Final browser acceptance

The isolated in-app browser retained its two real tracks and one generated playback fixture. Reload restored **2** upgraded records; PlaylistIQ showed **Specialist tracks only (2)** and **Quality-selected specialists · default**. Analysis showed C minor / D# minor with SheetSage2 attribution, real vocal/aggression/OpenMIC supports and the preserved reference values. The track Details action **Check selected specialists** completed through the actual HTTP job path with “Analysis complete. Ready for PlaylistIQ.” The saved result confirms zero executed algorithms. No browser error/warning logs were observed.

Specialist-only scope selection worked. Document width equaled viewport width at 390 and 320 pixels; the temporary viewport override was reset. The original large Chrome library was not driven or reanalyzed during this acceptance. Reloading that same local origin will attach the two compatible same-hash upgraded caches; other tracks still need an explicit selected-track upgrade.
