# V0 local pipeline listening review

Status: prepared; owner listening and interpretation pending. This is the final local evaluation before the cloud implementation milestone, not a declaration that V0 has passed.

## Run the review

1. Use the same browser/origin and finish analysis for the intended test pool first. Record any deliberately partial tracks. Last observed owner library: 61 loaded, 28 fully analyzed, 2 partial; the rest were not fully analyzed. Recheck live counts before testing.
2. Keep the pool fixed through all ten prompts. PlaylistIQ → V0 listening lab → Use prompt → Find tracks. Each request uses the configured OpenAI interpretation service.
3. Save the result as a playlist to listen in the player, then return to the lab notebook. The recorded result survives navigation.
4. For every attempt choose Good, Mixed, Poor or Expected limitation and note specific tracks that fit, fail or are missing; also judge the interpreted intent, quantity and order. Do not score solely by whether a full list is returned.
5. Export review JSON, then click Download JSON. A complete selectable JSON fallback is provided. Share that file with Codex for interpretation and the maintained evaluation record.

## Prompts

### P01 — Sparse

House.

Review: Does one word produce a useful interpretation without inventing extra constraints?

### P02 — Simple

Give me 8 house tracks.

Review: Check requested count and genre relevance; fewer is valid if the catalog cannot supply eight.

### P03 — Broad genre

Give me 6 rock tracks.

Review: Check broad rock coverage across subgenres.

### P04 — Mood only

Something relaxed and happy for a slow Sunday afternoon.

Review: Check whether mood stays a preference and the context is interpreted sensibly.

### P05 — Hard bounds

Give me 8 house tracks between 120 and 128 BPM.

Review: Every returned tempo should respect the bounds; inspect empty or short results.

### P06 — Several preferences

Give me 6 reggaeton tracks, preferably energetic and danceable.

Review: Check genre eligibility separately from the strength of energy/danceability ranking.

### P07 — Negative constraint

Give me 6 house tracks, but no techno.

Review: Check exclusion handling and explanations; unknown negative evidence may legitimately restrict results.

### P08 — Casual Spanish

Ponme unas 8 canciones de reggaetón para bailar, alegres pero no demasiado agresivas.

Review: Check language, quantity, mood and negative preference interpretation.

### P09 — Contradictory

Give me 10 tracks that are below 100 BPM and above 130 BPM at the same time.

Review: Should explain the contradiction or ask for clarification, never silently ignore one bound.

### P10 — Out of scope

Make a 30-minute journey from ambient into peak-time techno, with smooth harmonic transitions and no repeated artists.

Review: Check honest handling of duration, sequencing, harmonic mixing and artist-diversity requests that are not fully supported.

## Interpretation and completion

Preserve raw notes, original prompts, all attempts, candidate IDs/hashes, model/query evidence, output order and timings. Separate failures into metadata/analysis, prompt interpretation, hard filtering, preference ranking, catalog coverage and UI/persistence. Record user intent and specific examples before changing policy. Repeated runs remain separate rather than replacing earlier evidence.

Proposed closure checklist: all ten cases reviewed; supported hard constraints respected; contradictions and unsupported requests handled honestly; shortlist relevance accepted by the owner; save/play/reload and review export checked with real results; regressions fixed and affected prompts rerun, or remaining limits explicitly accepted. User approval closes the milestone after the commentary analysis. No fabricated passing result or automatic completion based on test count. Genre top-six policy remains unchanged; further genre tuning stays low priority.

After local acceptance, continue cloud architecture/execution planning from the maintained cloud package. This preparatory UI/review work does not execute deployment or remote audio processing.

## Evidence format

Browser key: resonant:playlist-review-v1. Export: playlistiq-v0-review.json, version 1, attempts (id, timestamp, testId, exact prompt, elapsed milliseconds, candidate catalog, full run or error, verdict, notes), export timestamp and testSuite. Browser notes are not a backup; storage failures retain the session in memory and show an export warning. No audio is included. Raw reviews stay separate from the accepted findings document that Codex will write after receiving the export.

## 2026-09-19 — PlaylistIQ Iteration 1 delivered

Python 0.4.0 / player 0.3.0 now integrate `playlist-intent-v1.3` (configured low reasoning), `intent-compiler-v1.1`, `maest-intent-v1` ranking and `discogs-parents-v1`. Required genres use MAEST support; creative prompts use directional soft priorities. Genre OR/family matching, original-request clarification, per-track contributions and twenty-prompt review evidence are available. New result/catalog/translation/run writes use schema 0.2.0 and read historical 0.1.0.

422 Python tests and 50 web tests pass. Final compiler replay passes all 20 intent/constraint checks; live revision failures are preserved, and final optional/HTTP checks pass. Human listening acceptance remains pending. No new audio analysis or cloud work; YAML is still a consideration task.

See [implementation, prompt, contracts and verification](../../prompt-to-playlist/docs/ITERATION_1.md). This current checkpoint supersedes older descriptions of v3-only translation, flat genre ties and missing parent matching; dated older sections remain historical evidence.

