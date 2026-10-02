# Local web analysis and PlaylistIQ — 2026-09-15

## 2026-10-01 — 120 character probes; audio embeddings reused

The replacement bank and all 120 text embeddings are ready. Analyze Tracks refreshes stale description scores from compatible cached audio vectors without audio inference. The current feature version is `selected-estimators-v3-character120`; the eleven estimators and playlist ranking remain unchanged. The new Musical character view groups results by dimension. Two cached-track matching tests passed with exact vector preservation; broader analysis remains a manual owner action. [Concepts, implementation, evidence and limits](CHARACTER_BANK_120.md). This supersedes earlier fixed-32/bundled-matching descriptions.

## 2026-10-01 — Selected estimators are the Analyze Tracks default

The owner requested one default pipeline with selected replacements, retained unreplaced features, added instruments, and both Music2Emo and previous EffNet moods. The web bridge now requires all eleven stages under `selected-estimators-v2`. Old DEAM/key/vocal results remain readable; those replaced estimators no longer execute in ordinary analysis. MusiCNN danceability stays an optional experiment because EffNet remains the selected head. [Implementation, safety behavior and verification](DEFAULT_ANALYSIS_PIPELINE.md). This supersedes earlier standard-bulk/optional-specialists descriptions. Whole-library and new-album analysis remains the owner’s next manual action.

## 2026-09-25 current selection

The web default is `quality`: Music2Emo theme/VA, MusiCNN voice, VGGish aggression and independent OpenMIC instrument support. EffNet happy/sad/relaxed/danceability, Beat This timing, MAEST and MuQ remain. SheetSage2 provides selected browser key evidence. Optional stages are `vocal_musicnn`, `aggression_vggish`, `instrument_passt`, `key_sheetsage2`; requests explicitly opt in with `specialists=1` / `--specialists`. `quality_status` records completion. Catalog identity gains `+estimators-quality-v1`, and its vocabulary gains `+openmic-v1`. No serialized format migration is required. Complete compatible coverage is required independently per scored target; unsupported new labels remain missing for everyone. The two real-track caches preserve all reference results.

[Research, setup, stage contracts and measured verification](TOP_ESTIMATORS_IMPLEMENTATION.md). Richer emotion vocabulary and improved local listening quality are not established. This checkpoint supersedes older reference-default wording below.

## Current upgrade — 2026-09-22

The browser now requests eight stages under `hybrid-estimators-v1`, including `semantic_audio`. Old complete seven-stage records remain usable and show an upgrade; **Analyze Tracks** includes old-version or partial records, while Details allows one-track upgrade/retry. Changed stage compatibility checks prevent stale semantic heads being silently accepted. Failed upgrades preserve old usable stage data and an explicit error. The bridge filters by the exact temporary source filename before applying the one-track limit.

MuQ runs in its own sequential worker with 6000 MiB RSS cap; existing acoustic workers retain 4096 MiB and the available-memory guard. Normal MuQ inference is offline. New Essentia assets live in `output/estimator-models`, MuQ in `output/semantic-models`, MAEST retains its existing directory. Setup and exact commands: [implementation guide](ESTIMATOR_UPGRADE.md#setup-and-use).

Catalog, query, contribution and run writes use schema 0.3.0. Browser, CLI and desktop prompt entry points supply the optional bounded local text encoder; pure `search` replays stored vectors. The configured LLM receives prompt, vocabulary and aggregate counts only. It does not receive track audio, titles, embeddings or per-track vectors, and has no new callable tool. Local workers are internal functions, not model-controlled tools.

Fusion needs compatible embeddings for all eligible tracks. Newly added theme/instrument/valence objectives also need complete eligible evidence. Partial upgrades therefore keep a visible structured fallback. The ordinary loaded library is not restricted to the two smoke-test songs, and they receive no special boost. Only those two were upgraded during agent testing; library-wide quality/coverage is not claimed.

## Frozen genre rule

Owner selects `maest-top6-v1`: MAEST replaces Jamendo genre estimation, match
against its six highest ranked candidate labels without a probability threshold,
show three with expansion to six, and retain all 519 probabilities. No accepted-
genre or listening-note overrides enter this path. Previous experiment files
remain historical. Revisit only if real usage warrants it; board card
`PIQ-GENRE-TOP6-REVISIT` is Later / could (low priority), not a launch blocker.

## Workflow

Start the web player using its existing launcher or `npm run dev`. Restart an
already running old server: the server now supplies the analysis/job routes.
Keep the same origin/port to retain the existing browser library.

1. Add music as before.
2. Analyze tracks processes missing/partial local tracks sequentially. Track
   options also provide a single-track analysis/retry action.
3. Genre candidates appear in the library. Track options show audio features.
4. Create with PlaylistIQ uses analyzed loaded tracks and displays coverage.
5. Find tracks interprets the prompt through the existing configured OpenAI
   translator, then deterministic catalog search. Inspect reasons/warnings and
   Save playlist. The normal player handles playback and editing.

Audio copies move from IndexedDB to a temporary directory on the same computer,
not a cloud service. Python retains feature JSON keyed by source SHA-256 in
`output/web-features`; temporary audio is cleaned after each job. Browser track
records retain full features. The source originals are unchanged. The existing
Python analysis environment and pinned model caches are required.

A loopback-only Node service guards POSTs by exact Host, Origin and a custom
header. It accepts bytes, never client-selected filesystem paths; limits input
size; runs a single job at a time; invokes the fixed package Python entry point
without a shell. JSON prompt bodies are validated. Job IDs are random and
expire after one hour. Closing the tab does not cancel an in-flight worker;
repeat Analyze after completion to retrieve cached successful features.

Saved trusted house/diverse descriptor runs can be reused only by exact source
hash and matching required model asset hashes, with passed preservation gates.
Legacy semantic genre is dropped during reuse. Failed stages remain failed or
are retried; no fallback to Jamendo or human judgments. MAEST's four historical
RSS failures are not repaired by raising the RAM limit. Current sequential
workers retain their 4096 MiB RSS cap and available-RAM guards.

## Matching contract

`feature_catalog.py` owns the descriptor-to-catalog bridge. Genre candidates
retain benchmark-estimate provenance and scores. Genre style names map to
canonical descriptor IDs; identical style names under different Discogs parent
families share a matching ID while the full labels remain in stored/displayed
scores. No parent taxonomy expansion beyond the selected styles is inferred.
BPM comes from Beat This. Raw key, loudness and all other stage results remain
stored and visible in details where useful.

A new `preference_scores` catalog field supports continuous soft preferences.
Exact happy/sad/relaxed/aggressive, vocal/instrumental and danceability outputs
rank requests without categorical thresholds. DEAM arousal uses an explicitly
unvalidated linear preference mapping on its 1–9 range: x=(arousal-1)/8,
high=x, low=1-x, medium=1-|2x-1|. Outside-range values remain unavailable.
These are preference weights, not calibrated classes. Dark/warm/uplifting and
other unmeasured labels remain unknown. Hard non-genre requirements are never
silently softened; absence cannot prove a negative. Consequently strict vocal,
energy, or genre-exclusion requests can have no eligible tracks. The UI shows
shortfalls. Ranking version is `scored-preferences-v1` for this catalog.

The OpenAI key stays in the Python process and follows existing playlist.toml
configuration. Only prompt, vocabulary and query contract are sent to OpenAI,
not audio, full feature vectors or track titles. The complete translation,
query, matched/missing evidence and result digests are saved in
`output/web-features/playlist-<uuid>.json`. Normal existing playlist persistence
stores selected track IDs. This is local integration, not a deployed cloud
backend; cloud hosting/auth/remote-audio execution remains deferred.

## Implementation checkpoint

Validation: 393 Python tests and 32 player tests pass; 17 JavaScript modules pass syntax checks. Production build verifies 16 files / 267065 bytes, manifest SHA-256 `0e9b04ecedb6448b6793e65796d1d2c8f390fd35fe83e16e297e7e5d46933443`. Browser acceptance on localhost:4181 imported one authorized real song, reused hash/model-matched saved features, showed three/six genres, displayed audio details, and made one live OpenAI request (`1 house track`) that matched its fourth-ranked House genre. Save playlist and feature persistence survived reload. A fresh generated 35-second sine exercised all seven workers: six usable stages, including all 519 MAEST scores; rhythm honestly remained partial because no beat grid was detected. No full corpus rerun. Four historical MAEST RSS failures remain unresolved; no RAM cap increase. New controls were visually checked on desktop; fresh Safari/mobile acceptance is not claimed.

## 2026-09-15 — Analysis workspace and fresh-export repair

Analyze tracks and PlaylistIQ now sit in the top controls. Feature columns toggle in the track list; the Analysis tab uses the full width with sticky track names and headers, horizontal scrolling, genre scores, tempo/key/loudness/arousal, mood/danceability/vocal scores and missing-stage details. Option 2 uses compact transport in Analysis. PlaylistIQ is a themed page with analyzed-track count, prompt form and inline results/save action; the earlier technical introductory copy is removed.

Fresh MAEST analysis could finish and then crash in `review_document`: the new top-six export referenced undefined `ordered` (NameError). The earlier generated-audio acceptance preceded that export edit and did not cover the final code; this checkpoint supersedes that acceptance claim. Cached completed records bypassed the failing code. Export now uses the result’s top-six values or its historical top-ten slice, with passed/failed regression coverage. Malformed worker JSON now becomes a failed stage instead of aborting the track. Per-source stage checkpoints persist under `output/web-features/checkpoints`, allowing retries after later failures; prior deleted temporary output cannot be recovered. Local analysis diagnostics are retained in `output/web-features/last-analysis-error.log`; provider errors remain redacted. Source audio, memory limits and the top-six/no-threshold/no-overrides rule are unchanged.

Verification: 395 Python tests and 33 player tests pass, 17 JS modules pass syntax checks. The exact failing fresh path was reproduced through localhost:4173 with a generated 31-second tone, then rerun successfully after repair: all 519 MAEST scores saved; six stages usable and rhythm explicitly partial because the tone has no beat grid. No music corpus rerun. Browser checks cover feature toggle, full-width Analysis and PlaylistIQ page in both desktop options, populated saved song features, and narrow layout. Production build: 16 files / 274471 bytes; manifest `d16a9d365bc34fdbc1f8af6ddc4ca6346545392d28c0fe21cc3cf82218d673a5`. Reload the existing player tab; Analyze tracks retries incomplete tracks while retaining completed records.

## 2026-09-19 — PlaylistIQ Iteration 1 delivered

Python 0.4.0 / player 0.3.0 now integrate `playlist-intent-v1.3` (configured low reasoning), `intent-compiler-v1.1`, `maest-intent-v1` ranking and `discogs-parents-v1`. Required genres use MAEST support; creative prompts use directional soft priorities. Genre OR/family matching, original-request clarification, per-track contributions and twenty-prompt review evidence are available. New result/catalog/translation/run writes use schema 0.2.0 and read historical 0.1.0.

422 Python tests and 50 web tests pass. Final compiler replay passes all 20 intent/constraint checks; live revision failures are preserved, and final optional/HTTP checks pass. Human listening acceptance remains pending. No new audio analysis or cloud work; YAML is still a consideration task.

See [implementation, prompt, contracts and verification](ITERATION_1.md). This current checkpoint supersedes older descriptions of v3-only translation, flat genre ties and missing parent matching; dated older sections remain historical evidence.


## 2026-09-25 — Selectable supervised experiments

`POST /api/local/analyze?filename=<file>&supervised=1` explicitly requests optional emotion/dance stages; ordinary analysis keeps its old scope. Loopback host, matching origin and X-Resonant-Local checks remain. Single-track Details controls own this action; failed/missing stages and older usable outputs remain visible. `supervised_status` is independent of base `status`.

Analysis displays baseline plus two experimental columns; Details exposes full scores, raw units, model identities and excerpt coverage. PlaylistIQ defaults to reference/all candidates; its optional compared-only scope changes only the submitted IDs, and per-stage catalog-wide coverage prevents partial upgrades from winning. The notebook preserves/reopens profile, scope and exact result. Startup restoration can attach richer same-hash optional cache data to completed reference records without rewriting audio/IDs or inferring new audio.

Maintained App Status source: `packages/web-player/public/app-status.json`; regenerate with `npm run build`. The final checks are 481 Python / 80 web, 45 JS modules and 28 build files. Browser acceptance used the actual two-track cache and a successful configured-provider request; original Chrome final refresh was interrupted by active use. Read [commands, exact coverage and evidence](SUPERVISED_ESTIMATORS.md) before reporting live library state.
