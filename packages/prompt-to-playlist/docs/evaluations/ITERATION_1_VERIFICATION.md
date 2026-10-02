# Iteration 1 verification — 2026-09-19

Catalog: 108 already-cached tracks. No audio analysis. Model: `gpt-5.4-mini-2026-03-17`, prompt `playlist-intent-v1.3`, low reasoning, compiler `intent-compiler-v1.1`.

## Results

- Python: 422 tests passed; web: 50 tests passed (including benchmark-export consistency); parent engine: 54 tests passed.
- Final Python wheel/source build and 23-file web production manifest pass; 32 JavaScript modules pass syntax checks. The macOS telemetry checks require normal runtime access and passed outside the restricted sandbox. No telemetry gate was weakened.
- Final low-reasoning live suite: 19/20 initially accepted; P20 repeated the same soft preferences and was rejected. The compiler now deterministically deduplicates same-direction preferences, preferring explicit intent then highest priority. Opposite directions still fail. Raw proposals are retained.
- Recompiling the exact twenty recorded proposals with the final compiler: **20/20 behavioral checks pass**. This is a replay result, not a claim of twenty fresh live successes.
- A subsequent live P20 request and the final complete HTTP bridge check both pass. The HTTP check preserved the original mom request plus a rock/count answer and returned two ranked tracks.
- Initial none-reasoning runs and rejected plans remain in output/iteration1-*.json. No failed attempt was relabeled successful.
- Browser: actual controller with recorded plans, fictional identities and generated audio; verified question/answer, explained results, save, playback and reload persistence. No document overflow at 390 or 320px; desktop checked at 1280px. The normal app view/status was also inspected.
- Genre ablation: 70 of 85 multi-candidate genre queries changed top-ten order under probability ranking. This measures ordering behavior, not subjective improvement.
- Live low-reasoning latency: median 2.921 s, maximum 9.646 s in this sample.

**Human listening acceptance remains pending.** These cases test faithful planning, constraints and score accounting. They do not establish lyric meaning, personal familiarity, genre correctness or playlist quality.

## Case outcomes after final compilation

| Case | Status | Tracks | Behavioral checks |
|---|---|---:|---|
| P01 | matched | 10 | Pass |
| P02 | matched | 8 | Pass |
| P03 | matched | 6 | Pass |
| P04 | matched | 10 | Pass |
| P05 | matched | 8 | Pass |
| P06 | matched | 6 | Pass |
| P07 | no_matches | 0 | Pass |
| P08 | matched | 8 | Pass |
| P09 | needs_clarification | 0 | Pass |
| P10 | needs_clarification | 0 | Pass |
| P11 | partial_support | 10 | Pass |
| P12 | matched | 10 | Pass |
| P13 | matched | 10 | Pass |
| P14 | needs_clarification | 0 | Pass |
| P15 | matched | 8 | Pass |
| P16 | matched | 10 | Pass |
| P17 | needs_clarification | 0 | Pass |
| P18 | matched | 10 | Pass |
| P19 | matched | 5 | Pass |
| P20 | partial_support | 10 | Pass |

## Evidence

- [Machine-readable verification](ITERATION_1_VERIFICATION.json)
- [Maintained prompts](iteration1-prompts.json)
- [Example original prompt + clarification run](iteration1-example-run.json)
- `output/iteration1-final-live-v1.3-low.json`: live outputs, latency, raw rejected proposal, catalog/vocabulary, source hashes and controlled genre ablation.
- `output/iteration1-final-compiler-replay.json`: replay through final compiler.
- `output/iteration1-final-optional-live.json`: final direct P20 check.
- `output/iteration1-http-acceptance.json`: complete Node/Python/API integration check.
- Earlier revision failures are retained for diagnosis; output files are local evidence, not production web assets.
