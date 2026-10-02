# PlaylistIQ roadmap

## 2026-10-01 — 120 character probes; audio embeddings reused

The replacement bank and all 120 text embeddings are ready. Analyze Tracks refreshes stale description scores from compatible cached audio vectors without audio inference. The current feature version is `selected-estimators-v3-character120`; the eleven estimators and playlist ranking remain unchanged. The new Musical character view groups results by dimension. Two cached-track matching tests passed with exact vector preservation; broader analysis remains a manual owner action. [Concepts, implementation, evidence and limits](docs/CHARACTER_BANK_120.md). This supersedes earlier fixed-32/bundled-matching descriptions.

## 2026-10-01 — Selected estimators are the Analyze Tracks default

The owner requested one default pipeline with selected replacements, retained unreplaced features, added instruments, and both Music2Emo and previous EffNet moods. The web bridge now requires all eleven stages under `selected-estimators-v2`. Old DEAM/key/vocal results remain readable; those replaced estimators no longer execute in ordinary analysis. MusiCNN danceability stays an optional experiment because EffNet remains the selected head. [Implementation, safety behavior and verification](docs/DEFAULT_ANALYSIS_PIPELINE.md). This supersedes earlier standard-bulk/optional-specialists descriptions. Whole-library and new-album analysis remains the owner’s next manual action.

## Current — 2026-09-25 quality-selected estimators

Research reports and the selected available specialists are implemented and validated on two authorized sources. [Checkpoint](docs/TOP_ESTIMATORS_IMPLEMENTATION.md). Richer emotion heads and listening-quality acceptance remain open. This supersedes the older next-task-only entry below.

## 2026-09-25 — Next: quality-first estimator research, then implementation

Owner requests a ranked shortlist of the strongest estimators for every non-genre feature, followed by full implementation of the highest-ranked available choices. Quality evidence dominates; local Mac feasibility is secondary and licensing has zero selection weight for this proof of concept. Deliver an implementation-ready technical report and a concise reader report before implementation. Preserve MAEST and the current planner/MuQ branch. This is recorded next work, not completed research; the existing optional challengers do not close the objective. Read the [full owner brief](docs/TOP_ESTIMATORS_NEXT_TASK.md).

## 2026-09-25 — Selectable supervised feature estimators

Music2Emo (MERT-95M + BTC/chord/key + J_all, corrected mode) and MusiCNN danceability are implemented as optional direct-feature challengers. The specialist reference remains default; MAEST top-six, MuQ and ranking weights are preserved. Complete compatible catalog coverage is required per challenger; otherwise everyone retains the reference. Two authorized sources passed six matched-window stages and zero-inference retries. Final checks: 481 Python tests, 80 web tests, 45 JS syntax modules, 28-file build, 40 exact fixed-query replays and one final successful live replay. One prior live intent proposal was rejected; no new listening judgments or superiority claim.

Exactly two local cache records have both challengers. Original Chrome was observed at 109 unique tracks; its final updated display was not confirmed because native interaction was interrupted by active use. The new reload migration attaches richer same-hash optional caches to completed reference records. Isolated browser acceptance verified real values, retry, profile/scope, saved-result reopening, App Status and 390/320px controls. No batch/new-corpus inference, audio upload, cloud work, commit or format migration.

Read [research, commands, failures, coverage and continuation](docs/SUPERVISED_ESTIMATORS.md). Historical sections/publication cutoffs below remain evidence for their original dates.


## Iteration 2 — Semantic matching and playlist quality (waiting for library balance)

Start Iteration 2 only after the planned albums have been downloaded and a current genre-distribution review confirms that the library has been balanced across genres. Then evaluate semantic matching and playlist quality against fixed prompts and listening judgments on that broader library. The existing two-track estimator smoke does not meet this prerequisite. This is tracked as `LATER-PIQ-ITERATION2` on the project board.

## 2026-09-22 — Hybrid estimator upgrade implemented

MuQ-MuLan-large now supplies local, segmented audio/text similarity; shared Discogs-EffNet supplies all 56 mood/theme and 40 instrument scores. Existing specialist estimators remain. Planner `playlist-intent-v1.6`, compiler `intent-compiler-v1.2`, schema 0.3.0 and `hybrid-semantic-v1` integrate this evidence with replayable contributions. Only descriptors with available evidence enter the planner's soft-preference enum. Historical records remain readable.

Two authorized tracks passed expanded-head and MuQ inference, source preservation and zero-inference retries. Both are attached to the existing Chrome library. Final checks: **442 Python tests, 77 web tests, 45 JS syntax modules and 28-file production build verification passed**. Seven live planner requests exposed and then corrected language/unsupported-field failures; the final affected case passed exact replay. Semantic-only intimacy ranking remains a negative quality finding, not a solved listener case.

The selected implementation is complete; the library-wide upgrade and listening acceptance are pending. Semantic fusion requires complete compatible coverage of eligible tracks. Expanded theme/instrument/valence objectives with incomplete eligible coverage are omitted for every candidate. Use the explicit Analyze Tracks / one-track upgrade actions; do not automatically rerun the whole corpus. No cloud/audio upload, rendered mix, new corpus, commit or YAML migration.

Continue from [research and decision](docs/research/ESTIMATOR_UPGRADE_2026-09-22.md), [digest](docs/research/ESTIMATOR_UPGRADE_DIGEST_2026-09-22.md) and [implementation, setup, failures and measurements](docs/ESTIMATOR_UPGRADE.md). This checkpoint supersedes older pending-bridge and four-mood-only descriptions below.

## 2026-09-19 — PlaylistIQ Iteration 1 delivered

Python 0.4.0 / player 0.3.0 now integrate `playlist-intent-v1.3` (configured low reasoning), `intent-compiler-v1.1`, `maest-intent-v1` ranking and `discogs-parents-v1`. Required genres use MAEST support; creative prompts use directional soft priorities. Genre OR/family matching, original-request clarification, per-track contributions and twenty-prompt review evidence are available. New result/catalog/translation/run writes use schema 0.2.0 and read historical 0.1.0.

422 Python tests and 50 web tests pass. Final compiler replay passes all 20 intent/constraint checks; live revision failures are preserved, and final optional/HTTP checks pass. Human listening acceptance remains pending. No new audio analysis or cloud work; YAML is still a consideration task.

See [implementation, prompt, contracts and verification](docs/ITERATION_1.md). This current checkpoint supersedes older descriptions of v3-only translation, flat genre ties and missing parent matching; dated older sections remain historical evidence.


## 2026-09-17 — Creative-intent planner research and YAML evaluation

Owner reports weak playlist relevance and requests probability-weighted MAEST
ranking plus support for creative occasion/emotion/recipient prompts. P019 records
the research direction. Read the [full report](docs/research/PLAYLIST_PLANNER_RESEARCH_2026-09-17.md) and
[digest](docs/research/PLAYLIST_PLANNER_DIGEST_2026-09-17.md) before the next planner change.

Confirmed in code: top-six MAEST scores are retained but ignored in relevance;
required-only genre requests tie at 1. Proposed first slice: score requested genres
using those estimates while retaining eligibility, then evaluate a typed intent
plan and hybrid retrieval in separate ablations. ACE-Step's structured planner is
architectural inspiration, not proof that YAML or chain-of-thought improves retrieval.
This research does not change the runtime, schemas, audio outputs or configured model.

PIQ-020 / LATER-PIQ-YAML adds the requested evaluation of YAML versus JSON between
modules. Compare the same typed objects, validation, token counts, parsing, hashes
and migration cost; no format migration is decided. Existing P018 personalization
and audio/cloud boundaries remain in force. Broader top-six eligibility/model
experiments remain separate from the requested probability-ordering correction.

## Role in Resonant's product evolution — D058

PlaylistIQ began as the independent prompt-to-playlist track beside a quick DJ
mix tool. The broader product is now planned as one Resonant DJ music workspace:
users can build/edit playlists, listen through the whole set sequence in-app,
download eligible playlist files and later request a deterministic mix.
PlaylistIQ remains the auditable proposal layer within that experience. It
returns criteria, matches, evidence and stable IDs; the host application owns
playlist persistence/order, source/provider availability, playback, archive
downloads and mix review. No cloud or provider dependency is added here.

Updated 2026-09-11. The implemented package remains independent of DJ render
work. The user resumed local evaluation under P009/D046 and named the product
PlaylistIQ. Technical package, CLI, import, and schema identifiers remain
unchanged for compatibility.

Parent D043 publishes [cloud discovery](../../docs/cloud-library/README.md)
with a proposed future playlist host boundary. Its contracts are planning
material only; PlaylistIQ remains independently versioned and no cloud build is
authorized.

## V0.1 — Implemented foundation

- Independent installation, runtime, lockfile, contract tests and documentation.
- Editable canonical descriptors; strict sourced tag/numeric evidence.
- Replaceable prompt translator with offline grammar and OpenAI adapter.
- Deterministic normalization, filtering/ranking, existing-ID lookup and tools.
- No-match/clarification handling and replayable result metadata.
- Native JSON catalog and read-only adapter for existing DJ collection JSON.
- CLI plus local desktop description field, evidence display and JSON export.
- Synthetic semantic examples; real-catalog numeric smoke validation.

## V0.2 — Configured pool and live OpenAI

- Explicit project profile and desktop launcher using the user's named key.
- Non-executing credential lookup with no unrelated-key fallback or copied secret.
- Read-only 120-file hash/FFprobe import, source manifest and 39-descriptor pool
  vocabulary; 62 mapped genres and 22 positive embedded BPM values.
- Live OpenAI English/Spanish, count, tempo/order, exclusion and unsupported-mix
  smoke checks passed. Initial fixed-count interpretation failure retained in logs.
- Desktop coverage display and saved live evaluation report; engine/runtime
  independence preserved.

## V0.2 follow-up — Natural language and interface correction

- OpenAI-only desktop with explicit/current-directory/editable-checkout profile
  selection. No hidden rules fallback; generic CLI prompt defaults to OpenAI.
- Explicit `--provider rules` retained for offline developer CLI workflows.
- Translator v3: direct single-genre requests require the genre; ordinary
  mood/energy stays a preference; “DJ set” alone does not request rendering.
- Modern light Tk interface, plain-language criteria, visible evidence gaps,
  artist/BPM results and optional detailed provenance; no new runtime dependency.
- User regression “house dj set energetic” passes live with eight house-tagged
  candidates and missing energy evidence; all six live cases pass.
  P-E003 records the actual outcomes and separates interpretation from the
  pool’s missing energy annotations.

## V0.3 — Implemented no-All-In-One descriptor extraction

- Variable-folder `analyze-folder` command with a one-track safety default and
  explicit `--all-tracks` opt-in.
- Sequential subprocess isolation, stage timeouts/RSS/available-RAM gates,
  source hashes before/after, source inventory verification, and safe external
  output paths.
- Pinned, SHA-256-verified Beat This and Essentia model assets; optional
  `analysis` dependency group leaves search/UI lightweight.
- Metadata, standardized loudness, key, Beat This rhythm, shared Discogs-EffNet
  genre/mood/danceability/vocal heads, and separate DEAM arousal extraction.
- Strict descriptor-run JSON, controlled descriptor-document text, verified
  resume and cross-output reuse checkpoints, and JSON/Markdown telemetry with per-algorithm plus
  combined 8/16/32 GB VM planning projections.
- Exactly two house tracks passed all six stages in P-E006; the later user full
  run passed 50/60 before P-E007 repaired rhythm decoding. Package suite: 383
  tests after verified cross-output reuse was added.

## Active next slice — catalog bridge, then diverse-folder evidence

The current UI is ready for a metadata-only baseline. The lightweight
descriptor extractor in [`docs/AUDIO_FEATURES.md`](docs/AUDIO_FEATURES.md) is
ready, but the present UI catalog still has no scored mood, energy,
danceability, or vocal evidence. A genuine second test of prompt fit therefore
needs the user-run descriptor pass, predeclared listening judgments, and a
deliberate descriptor-to-catalog/matching adapter.

The user's repaired ten-track execution now passes 60/60 stages. P-E007 records
the initial failure/repair and P-E008 records the complete result. The output
contains 60 verified checkpoints and is the current house-corpus performance
baseline, not semantic-accuracy proof.
CLAP/lexical/text-embedding matching remains explicitly later and is not hidden
in extraction.

The user explicitly selected and completed `test_folder_37_tracks_diff_genres`.
P-E009/P015 records its 37 immutable hashes and prepared reuse; P-E010 records
222/222 stages, zero failures, exact sources, 60 reuses and 162 new executions.
Genre collapse and danceability saturation require soft evidence/abstention;
mood and raw arousal are the stronger first bridge candidates.

1. Add parent/run-phase timers before using command elapsed for VM costing; the
   completed run has a 37.29-minute span not represented by worker telemetry.
2. Define and implement the deliberate descriptor-to-catalog bridge with raw
   scores, reviewed thresholds/abstention, model provenance, and no overwrite of
   encoded or human evidence.
3. Define a small annotation guide for the descriptors the user actually needs.
   Record tags and axis completeness in a separate native catalog or sidecar;
   retain source hashes/IDs and human verification scope. Do not edit audio or
   silently overwrite analysis. Start with reviewed examples before model tagging.
4. Run the bridge on the completed house sidecar and the new diverse sidecar;
   do not discard raw scores.
5. Broaden the configured model's fixed prompt set: genre/mood,
   positive/negative constraints, unknown tags, ambiguity, contradictory bounds,
   mixed supported/unsupported requests, and languages the user wants supported.
   Grade intent preservation separately from deterministic retrieval correctness.
   The initial five live checks are a baseline, not a comprehensive benchmark.
6. Record missed constraints and expected IDs before modifying prompts/weights.
   Do not call mocked tests a live evaluation or establish a blanket injection claim.
7. Compare the metadata-only and enriched catalogs using the same prompts and
   separate request-translation errors from selection errors.
8. Consider an edit-before-search query review flow if evaluation demonstrates
   a need. The current form shows the interpretation with results; it is read-only.

The structured query and evidence output are a product requirement because
**they let us audit why each track matched**. Any later learned ranking must
retain the eligible set, evidence, scores, versions, and a reproducible reason
record.

## Later, driven by concrete consumers

- Dedicated catalog-tag enrichment adapter and incremental snapshots.
- Additional numeric/era/history filters with explicit source semantics.
- Another LLM provider/local model via `Translator`.
- More capable retrieval/indexing only when catalog scale requires it.
- Learn a private, user-specific ranking signal from how the user repeatedly
  groups tracks in manually built playlists. Treat shared playlist membership
  as the primary evidence, with repeated co-grouping stronger than a single
  occurrence; evaluate adjacency/order only as a separate weaker signal.
  Playlist names may contribute a low-confidence hint when they meaningfully
  match a request, but must never dominate track-grouping evidence or become a
  catalog fact. Apply learned preferences only after explicit prompt filters
  and availability/rights checks. Preserve score contributions, source
  playlist IDs, model/version, opt-out/reset controls, minimum-support and
  cold-start behavior so personalization remains private, auditable and
  reversible. Imported/provider playlists require provenance and applicable
  platform-policy review before training use.
- Compare CLAP prompt-to-audio similarity, TF-IDF/BM25 over normalized
  descriptor strings, lightweight text embeddings over the same strings, and a
  hybrid that keeps structured hard filters before similarity ranking.
- Spotify or another application's catalog/export adapter after access research.
- Resonant host integration that turns candidates into an editable saved
  playlist while retaining query/evidence history. Continuous playback and
  rights-aware playlist-file download remain host responsibilities.
- Explicit downstream playlist-candidate → DJ planning integration with the
  existing renderer's separate validations. No automatic MixPlan in this slice.

No scheduling, vector database, remote publication, automatic rendering,
transition optimization, or set-duration promise is required to finish the
next descriptor-pipeline slice. Embedding retrieval is a recorded later
experiment, not a prerequisite for that slice.

## 2026-09-13 — Optional MAEST genre comparison

`genre_maest` is an opt-in parallel genre estimator; existing EffNet/Jamendo
and six-stage defaults are preserved. Setup and the one-song smoke are complete;
the user runs the full 37 songs. See [command and review format](docs/MAEST_DISCOGS519.md).

## 2026-09-13 — MAEST listening-review checkpoint

The user-run MAEST diverse-37 output has 33 genre results and four RAM-limit
failures; fresh source hashes all match. A standalone `listening-review.html`
is now beside those outputs. See the DJ project’s `tools/genre-review/README.md`
for regeneration, review semantics and verification limits. No audio analysis
was rerun. The earlier “full run not executed” checkpoint is superseded by
this audit; no genre-quality acceptance or model replacement is implied.

## 2026-09-15 — MAEST top-six and local player integration

Owner-authorized `maest-top6-v1` now replaces legacy genre estimation: match the top six, display three expandable to six, retain all 519 scores, and apply no probability threshold or human review overrides. Historical outputs remain preserved. The low-priority board card `PIQ-GENRE-TOP6-REVISIT` is Later / could; further genre experimentation is not a launch blocker.

The local web player now provides **Analyze tracks** and **Create with PlaylistIQ**. Its loopback Node job service invokes the existing Python environment; analysis persists by source hash and in IndexedDB, and prompt results save into normal playable playlists. Restart the player server on the same origin/port to retain the browser library. This explicit integration authorization supersedes older local bridge/Python-edit holds; cloud deployment, remote audio processing and automatic MixPlans remain deferred.

See [integration contract](docs/WEB_INTEGRATION.md).

## 2026-09-15 — Analysis workspace and fresh-export repair

Analyze tracks and PlaylistIQ now sit in the top controls. Feature columns toggle in the track list; the Analysis tab uses the full width with sticky track names and headers, horizontal scrolling, genre scores, tempo/key/loudness/arousal, mood/danceability/vocal scores and missing-stage details. Option 2 uses compact transport in Analysis. PlaylistIQ is a themed page with analyzed-track count, prompt form and inline results/save action; the earlier technical introductory copy is removed.

Fresh MAEST export NameError fixed; persistent checkpoints and invalid-worker-output recovery added. See the player WORK_LOG and PlaylistIQ WEB_INTEGRATION for evidence and retry instructions.

## 2026-09-15 — Playful App status and V0 listening lab

Owner requested a more expressive status page and ten varied PlaylistIQ tests with commentary capture to close local V0 before cloud work. Status now uses staggered metrics, asymmetric cards, large typography, a numbered query flow and contrasting next steps, with compact transport and responsive stacking. Maintained snapshot remains the content source.

PlaylistIQ now includes ten loadable prompts and a persistent per-attempt notebook: exact prompt, candidate identities/hashes, full query/result/error, timing, verdict and notes. Repeated tests remain separate. Export provides a Download JSON link and copyable JSON fallback. See web-player/docs/V0_LISTENING_REVIEW.md for the suite, interpretation categories and proposed closure checklist. User listening/comments and interpretation are pending; V0 is not marked complete. Cloud is the subsequent milestone; no provider execution performed.

Validation: 42 tests, 27 syntax checks and production manifest verification pass. Browser checks confirm status content, mobile width 390 with no document overflow, prompt loading and JSON export fallback. No OpenAI test calls or user verdicts generated.

## 2026-09-19 — Iteration 1 integration checkpoint (in progress)

Intent compiler, MAEST-weighted ranking, genre alternatives/taxonomy, directional preferences and web/CLI/native clarification are implemented. Twenty listening prompts preserve P01–P10 and add P11–P20. Focused checks pass; initial live validation failures are preserved and corrected with explicit prompt examples. Final regression/browser checks and documentation remain in progress. See [implementation checkpoint](docs/ITERATION_1.md).


## 2026-09-25 — Quality-first estimator research and implementation

Quality-first non-genre research and the selected available specialists are delivered locally. The web default selects Music2Emo theme/VA, MusiCNN vocals, VGGish aggression and independent PaSST OpenMIC instrument evidence, retaining EffNet happy/sad/relaxed/danceability. SheetSage2 supplies selected key evidence. MAEST, MuQ and planner weights remain unchanged. Two authorized sources passed 8/8 new stages; retries execute zero stages. Richer nuanced-emotion prediction and listening superiority remain unresolved; do not present encoder-only releases or the same 56 tags as solving that objective.

[Implementation, two research reports, setup, model contracts and verification](docs/TOP_ESTIMATORS_IMPLEMENTATION.md). Final validation: 502 Python tests, 83 web tests, 45 syntax modules, 28-file build, eight successful final audio stages and 26 exact fixed-query replays. No new provider calls or listener judgments. The new optional specialist stages and quality/openmic vocabulary identity preserve reference records and saved-profile replay.
