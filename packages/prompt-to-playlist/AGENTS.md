# PlaylistIQ — takeover

## 2026-10-01 — Import compatibility and storage recovery

M4A-to-MP3 upload normalization and a provisional Analysis conversion button are implemented, alongside closed-storage reconnect/batch pause. 90 web tests pass. Chrome reload exposed zero persisted track rows; source restoration remains unresolved. No owner-library conversion or analysis launched. [Evidence and continuation](../web-player/docs/MP3_IMPORT.md).

## 2026-10-01 — 120 character probes; audio embeddings reused

The replacement bank and all 120 text embeddings are ready. Analyze Tracks refreshes stale description scores from compatible cached audio vectors without audio inference. The current feature version is `selected-estimators-v3-character120`; the eleven estimators and playlist ranking remain unchanged. The new Musical character view groups results by dimension. Two cached-track matching tests passed with exact vector preservation; broader analysis remains a manual owner action. [Concepts, implementation, evidence and limits](docs/CHARACTER_BANK_120.md). This supersedes earlier fixed-32/bundled-matching descriptions.

## 2026-10-01 — Selected estimators are the Analyze Tracks default

The owner requested one default pipeline with selected replacements, retained unreplaced features, added instruments, and both Music2Emo and previous EffNet moods. The web bridge now requires all eleven stages under `selected-estimators-v2`. Old DEAM/key/vocal results remain readable; those replaced estimators no longer execute in ordinary analysis. MusiCNN danceability stays an optional experiment because EffNet remains the selected head. [Implementation, safety behavior and verification](docs/DEFAULT_ANALYSIS_PIPELINE.md). This supersedes earlier standard-bulk/optional-specialists descriptions. Whole-library and new-album analysis remains the owner’s next manual action.

## 2026-10-01 — Test music relocated; local server restarted

The owner moved the three existing test corpora into `test_music/` and created `test_music/new_albums/`. Runtime recovery and bounded smoke/attachment scripts now use the new parent; current README commands are updated. Historical analysis files retain their recorded paths and hashes. The DJ engine resolves a missing legacy corpus folder to its existing `test_music` location without changing archived evidence; existing folders always take precedence. Source-output protection includes the new music parent, and Git excludes the whole local music tree.

Server uses the existing `http://127.0.0.1:4173` origin. Models, profiles, weights and analysis behavior are unchanged. The owner will manually import new albums and launch analysis; the agent did not import or analyze music. Bulk Analyze Tracks remains the standard pipeline; Details → Upgrade selected specialists runs the newer selected models. `new_albums` is not silently included in Restore saved batch.

## 2026-09-25 — Quality-selected estimators implemented

Quality-first non-genre research and the selected available specialists are delivered locally. The web default selects Music2Emo theme/VA, MusiCNN vocals, VGGish aggression and independent PaSST OpenMIC instrument evidence, retaining EffNet happy/sad/relaxed/danceability. SheetSage2 supplies selected key evidence. MAEST, MuQ and planner weights remain unchanged. Two authorized sources passed 8/8 new stages; retries execute zero stages. Richer nuanced-emotion prediction and listening superiority remain unresolved; do not present encoder-only releases or the same 56 tags as solving that objective.

Read the [research, implementation, measured results and continuation](docs/TOP_ESTIMATORS_IMPLEMENTATION.md). This checkpoint supersedes the older next-work and reference-default descriptions below. Broader corpus, cloud and source-preservation boundaries remain.

## 2026-09-25 — Next: quality-first estimator research, then implementation

Owner requests a ranked shortlist of the strongest estimators for every non-genre feature, followed by full implementation of the highest-ranked available choices. Quality evidence dominates; local Mac feasibility is secondary and licensing has zero selection weight for this proof of concept. Deliver an implementation-ready technical report and a concise reader report before implementation. Preserve MAEST and the current planner/MuQ branch. This is recorded next work, not completed research; the existing optional challengers do not close the objective. Read the [full owner brief](docs/TOP_ESTIMATORS_NEXT_TASK.md).

## 2026-09-25 — Selectable supervised feature estimators

Music2Emo (MERT-95M + BTC/chord/key + J_all, corrected mode) and MusiCNN danceability are implemented as optional direct-feature challengers. The specialist reference remains default; MAEST top-six, MuQ and ranking weights are preserved. Complete compatible catalog coverage is required per challenger; otherwise everyone retains the reference. Two authorized sources passed six matched-window stages and zero-inference retries. Final checks: 481 Python tests, 80 web tests, 45 JS syntax modules, 28-file build, 40 exact fixed-query replays and one final successful live replay. One prior live intent proposal was rejected; no new listening judgments or superiority claim.

Exactly two local cache records have both challengers. Original Chrome was observed at 109 unique tracks; its final updated display was not confirmed because native interaction was interrupted by active use. The new reload migration attaches richer same-hash optional caches to completed reference records. Isolated browser acceptance verified real values, retry, profile/scope, saved-result reopening, App Status and 390/320px controls. No batch/new-corpus inference, audio upload, cloud work, commit or format migration.

Read [research, commands, failures, coverage and continuation](docs/SUPERVISED_ESTIMATORS.md). Historical sections/publication cutoffs below remain evidence for their original dates.


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

## 2026-09-16 — Future playlist-pattern personalization

P018 and board card PIQ-019 plan a later private learning layer based mainly on
repeated track co-grouping in the user's manually built playlists. Playlist
names are weak optional context only. Learned scores may rerank only after hard
prompt, availability and rights constraints and must retain source playlist
IDs, score contributions, versioning, cold-start/minimum-support behavior and
opt-out/reset controls. Distinguish manual, generated, imported and system
playlists; review provider policy before remote playlist data enters training.
This is planning only: no collection, training, schema or runtime is active.

## 2026-09-15 — Playful App status and V0 listening lab

Owner requested a more expressive status page and ten varied PlaylistIQ tests with commentary capture to close local V0 before cloud work. Status now uses staggered metrics, asymmetric cards, large typography, a numbered query flow and contrasting next steps, with compact transport and responsive stacking. Maintained snapshot remains the content source.

PlaylistIQ now includes ten loadable prompts and a persistent per-attempt notebook: exact prompt, candidate identities/hashes, full query/result/error, timing, verdict and notes. Repeated tests remain separate. Export provides a Download JSON link and copyable JSON fallback. See web-player/docs/V0_LISTENING_REVIEW.md for the suite, interpretation categories and proposed closure checklist. User listening/comments and interpretation are pending; V0 is not marked complete. Cloud is the subsequent milestone; no provider execution performed.

Validation: 42 tests, 27 syntax checks and production manifest verification pass. Browser checks confirm status content, mobile width 390 with no document overflow, prompt loading and JSON export fallback. No OpenAI test calls or user verdicts generated.


## 2026-09-15 — Analysis workspace and fresh-export repair

Analyze tracks and PlaylistIQ now sit in the top controls. Feature columns toggle in the track list; the Analysis tab uses the full width with sticky track names and headers, horizontal scrolling, genre scores, tempo/key/loudness/arousal, mood/danceability/vocal scores and missing-stage details. Option 2 uses compact transport in Analysis. PlaylistIQ is a themed page with analyzed-track count, prompt form and inline results/save action; the earlier technical introductory copy is removed.

Fresh MAEST export NameError fixed; persistent checkpoints and invalid-worker-output recovery added. See the player WORK_LOG and PlaylistIQ WEB_INTEGRATION for evidence and retry instructions.


## 2026-09-15 — MAEST top-six and local player integration

Owner-authorized `maest-top6-v1` now replaces legacy genre estimation: match the top six, display three expandable to six, retain all 519 scores, and apply no probability threshold or human review overrides. Historical outputs remain preserved. The low-priority board card `PIQ-GENRE-TOP6-REVISIT` is Later / could; further genre experimentation is not a launch blocker.

The local web player now provides **Analyze tracks** and **Create with PlaylistIQ**. Its loopback Node job service invokes the existing Python environment; analysis persists by source hash and in IndexedDB, and prompt results save into normal playable playlists. Restart the player server on the same origin/port to retain the browser library. This explicit integration authorization supersedes older local bridge/Python-edit holds; cloud deployment, remote audio processing and automatic MixPlans remain deferred.

See [integration contract](docs/WEB_INTEGRATION.md).

Updated 2026-09-12. Read this before changing this package. The parent
[DJ handoff](../../AGENTS.md) retains authority for music and engine work.

Parent D058 now places PlaylistIQ inside Resonant's broader user journey: one
DJ music workspace for library listening, native/manual and AI-assisted
playlist editing, continuous in-app set-playlist playback, rights-aware
playlist-file download and later deterministic mixes. PlaylistIQ still owns
only prompt interpretation and auditable candidate selection. The host/player
owns saved playlists, source capabilities, playback and downloads; this package
must not absorb provider SDKs, audio archive creation or rendering.

## Scope and status

PlaylistIQ is the product name for the reusable prompt-to-playlist module
(parent D039/D046). The existing package path, `prompt-playlist` command,
Python import name, and serialized schema identifiers remain stable.
V0.2 implements standalone Python contracts, editable descriptor vocabulary,
rules/OpenAI translators, deterministic search/lookup tools, a read-only DJ
JSON adapter, CLI and local Tkinter desktop form. D040 authorizes the user's
120-file pool for bounded metadata/hash import and their project key for live
OpenAI translation. The project profile and launcher now use that pool and
`gpt-5.4-mini-2026-03-17`. Five live smoke cases passed in P-E002 after a recorded count
interpretation fix (`playlist-query-v2`). The next user report exposed a
still-running offline window. P007 makes the desktop OpenAI-only, adds bounded
project-profile discovery, and changes generic CLI prompt defaults to OpenAI.
`playlist-query-v3` treats a direct single-genre request as required and
ordinary energy/mood as preferences. “DJ set” alone is playlist context.
The lighter, modernized Tk form exposes missing preference evidence without
requiring users to inspect technical details. All six live v3 cases passed,
including the exact user request returning eight house-tagged tracks while
high energy remains unverified. Broad language/semantic quality remains open;
see P-E003 for this fix’s actual verification: 363 tests, successful wheel/
source builds, and real Tk state/geometry checks with no extra API calls.
Screenshot visual QA was unavailable.

V0.3 adds the separate, optional, no-All-In-One descriptor pipeline:
`analyze-folder` extracts metadata, loudness, key, Beat This rhythm, shared
Discogs-EffNet semantic heads, and DEAM arousal while recording per-stage
process-tree telemetry. P-E006 records the bounded two-track execution and
exact performance numbers. Closing verification: 377 package tests, 54 parent
tests, successful 0.3.0 wheel/source builds, and isolated wheel validation.

The user ran all ten house tracks on 2026-09-11. P-E007 records the initial
50/60 result and SoundFile repair. P-E008 records the completed resume: 50
checkpoints reused, ten rhythm stages executed, 60/60 stages, zero failures,
60 checkpoints, and exact sources. The final capacity baseline is 269.609
stage-wall seconds for 62.984 audio minutes and 1,400.047 MB peak RSS. The
partial report is historical and must not supersede P-E008.

On 2026-09-11 the user explicitly authorized
`test_folder_37_tracks_diff_genres` for the second PlaylistIQ descriptor test.
P-E009/P015 hash all 37 files without decoding them: 37 unique hashes, 10 exact
overlaps with the house baseline, 27 new tracks, and 60/60 compatible prior
stage checkpoints. P-E010 records the completed user run: 222/222 stages, zero
failures, 60 reuses, 222 checkpoints and exact sources.
`--reuse-from output/playlistiq-house-10-full --resume` preserves the original
baseline, imports verified checkpoints by audio hash, and resumes the new
output. The canonical pre-analysis inventory is
[`docs/DIVERSE_37_MANIFEST.md`](docs/DIVERSE_37_MANIFEST.md).

The user resumed local PlaylistIQ evaluation on 2026-09-10 (P009/D046). The
preserved UI is verified and the lightweight descriptor extraction path is now
implemented. The active direction is to build the deliberate descriptor-to-
catalog bridge, then evaluate a separately identified, more-diverse local
folder. All-In-One MLX is
excluded from this path. Parent
D042 registers a future
cloud music-library product hypothesis, but that does not authorize hosting,
cloud catalog integration or changes to this package.

Parent D043 now activates cloud research/planning only. Its maintained
[research package](../../docs/cloud-library/README.md) reviews these contracts
read-only and proposes a future host adapter. This does not resume playlist
implementation, make live model calls or authorize automatic mix generation.

This is an independent distribution inside the DJ repository, with its own
`pyproject.toml`, `uv.lock` and `.venv`. Pydantic remains the only core runtime
dependency. Audio dependencies are isolated in the explicit `analysis` extra;
do not make them necessary for catalog search, translation, or the UI. Do not
add engine, Spotify, web-hosting, or provider SDK dependencies to implement a
small catalog operation.
Parent automatic MixPlan/render planning is still deferred; this module
returns playlist candidates and stable IDs only.

## Boundaries

- `import-folder` may read the explicitly authorized pool using bounded
  FFprobe metadata probes and streaming hashes. Results/manifests stay outside
  the source folder. Prompt/search/UI consume the saved JSON snapshot.
- No render, heavy analyzer invocation, source file writes, hidden API calls,
  playlist publication or arbitrary model-selected execution.
- The 120-file `test_tracks_folder_mp3` pool remains authorized only for its
  completed metadata workflow. Do not run fresh acoustic analysis on it unless
  the user explicitly selects it for the new experiment. The future diverse
  test folder must be named explicitly and stay read-only.
- For `test_folder_10_house_tracks`, P-E006 used exactly two agent-run tracks.
  The user subsequently ran all ten; P-E007 audited/repaired the partial result
  and P-E008 completed 60/60 stages. Do not rerun the full corpus as an agent.
  Agent regression checks remain bounded to one or two tracks.
- `test_folder_37_tracks_diff_genres` is explicitly authorized and complete for
  its user-run no-All-In-One descriptor pass. Do not rerun all 37 as an agent. Keep
  its output at `output/playlistiq-diverse-37`, reuse the completed baseline
  only through verified `--reuse-from`, and audit both source-preservation
  gates plus failures after the user runs it.
- Missing genre/mood/energy/vocal labels stay missing. Do not infer them from
  BPM, LUFS, key, filename, folder name, or an LLM's knowledge.
- LLM interpretation is `llm_proposal`, not deterministic. Tool filtering,
  normalization and ranking are deterministic for fixed inputs and versions.
  Preserve this split because it lets us audit why each track matched. A result
  must retain the query, matched/missing evidence, provenance, versions and IDs.
- Numeric/tag source evidence retains its authority/status. Rejected/unknown
  values cannot satisfy constraints. All unknown provider constraints must
  block retrieval through `unresolved`; never silently relax them.
- The explicit `playlist.toml` project profile selects OpenAI. It reads only
  `AUTODJ_OPENAI_API_DEV_KEY` from the environment or its literal assignment
  in `~/.zshrc`, with no shell execution or unrelated-key fallback. Never print
  credentials or put them in project files. The desktop uses explicit config,
  current-directory `playlist.toml`, then the editable checkout’s profile;
  discovery is UI-only. `prompt` defaults to OpenAI; offline CLI parsing uses
  explicit `--provider rules` or an explicitly selected rules profile. The
  desktop rejects rules mode instead of
  presenting grammar as natural language. Library callers choose their
  translator explicitly. Automated tests mock HTTP; `live_check` explicitly
  makes real requests. Record live results separately from unit tests.
- Preserve parent logs and accepted DJ listening findings. No commits unless asked.

## Work and validation

```sh
uv sync --locked
uv run pytest -q
uv build
uv run prompt-playlist ui --config playlist.toml
uv sync --locked --extra analysis
uv run --extra analysis prompt-playlist analyze-folder --help
uv run prompt-playlist prompt --catalog examples/demo-catalog.json \
  --provider rules --text 'require house; prefer dark; bpm 120-130; count 3'
```

Use `README.md` for commands, `docs/ARCHITECTURE.md` for module ownership,
`docs/SCHEMAS.md` plus `models.py` for contracts, `PLAN.md` for the next slice,
and `EXPERIMENT_LOG.md` for actual verification outcomes. The implementation
coordination contract is historical, not a replacement for those documents.

After changes update this handoff, README/PLAN as relevant, schemas for
contract changes, and append decision/experiment/changelog entries. Update
the parent documentation set listed in its handoff when status or integration
boundaries change. Never rewrite previous experiment findings.

## Next slice

**Active local evaluation.** Use the existing UI against its preserved
metadata catalog as the baseline. The bounded, resumable, no-All-In-One
descriptor pipeline described in
[`docs/AUDIO_FEATURES.md`](docs/AUDIO_FEATURES.md) is implemented and verified
on the complete ten-track house folder: 60/60 stages and zero failures. The
diverse run is complete and audited. The next implementation slice is the
deliberate catalog bridge and a predeclared human/prompt-fit evaluation. Do not
claim the current UI uses acoustic semantic evidence: the
new descriptor artifact is not yet merged into its catalog/search contract.

The pool catalog contains 120 tracks, 62 with exactly mapped genre annotations
and 22 with positive BPM metadata; eight tracks have the exact house tag.
No normalized mood/energy/vocal/danceability evidence or complete tag axes
exist in the UI's current catalog. PlaylistIQ 0.3.0 now has a separate
descriptor artifact and an optional TensorFlow-enabled environment, but the
catalog still lacks scored semantic fields. Next define the catalog migration
and compare metadata-only and enriched retrieval on the same predeclared
prompts. Keep this independent of
the engine's headroom/limiter, larger manual-mix work, and cloud deployment.

The complete descriptor-extraction pipeline is built. It defaults to one track
and requires explicit `--all-tracks`; uses short-lived sequential workers,
verified model hashes and resumable stage checkpoints; refuses output inside
the source; and records hashes before/after plus folder inventory. The user's
full command completed; repeating README's `--resume` now reuses all 60
checkpoints to regenerate reports. The new cross-output `--reuse-from` path
validates source hash, pipeline, tool versions, model hashes, and CPU config,
then imports only compatible checkpoints into a separate output. Commercial-license questions stay noted for eventual
product viability but are not a blocker for this private feasibility playground.

Do not add matching experiments to that build. Keep a later comparison of CLAP
audio–text similarity, TF-IDF/BM25 descriptor-document retrieval, lightweight
text embeddings, and hybrid structured-filter-plus-similarity ranking in the
roadmap. All variants must be tested against the same prompts/judgments and must
retain an auditable explanation record.

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

## 2026-09-14 — Preserved owner listening judgments

Saved all 33 pasted reviews to package `docs/evaluations/maest-listener-review-2026-09-14.json`;
findings and unresolved inconsistencies are in `docs/evaluations/MAEST_LISTENER_FINDINGS.md`.
HTML now embeds these reviews via generator `--reviews PATH` and isolates
script bindings, renaming the global top helper to topScore. Syntax and
isolated checks pass; browser root cause/download behavior remain unverified.
No model replacement, accepted-tag catalog import or new audio analysis.

## 2026-09-19 — Iteration 1 integration checkpoint (in progress)

Intent compiler, MAEST-weighted ranking, genre alternatives/taxonomy, directional preferences and web/CLI/native clarification are implemented. Twenty listening prompts preserve P01–P10 and add P11–P20. Focused checks pass; initial live validation failures are preserved and corrected with explicit prompt examples. Final regression/browser checks and documentation remain in progress. See [implementation checkpoint](docs/ITERATION_1.md).
