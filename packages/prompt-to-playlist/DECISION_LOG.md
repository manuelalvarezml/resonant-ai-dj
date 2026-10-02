# Decisions

## 2026-09-07 — P001 — Independent package in the DJ repository

The user explicitly requested parallel progress and recyclable modules.
Keep one independently installable distribution under `packages/` with its own
runtime/lock/tests/docs, and avoid changes to the engine's dependency graph.
This gives shared version control now and a clean extraction boundary later.
Parent D039 records authorization; automatic DJ MixPlan work is still deferred.

## 2026-09-07 — P002 — One interpretation, deterministic retrieval

Free-form translation is probabilistic. A bounded provider call emits a query
proposal and unsupported requirements; code validates and searches. Provide
the same normalization/search/lookup primitives to future agent hosts.
An autonomous tool loop is unnecessary for the current fixed workflow.
Use a small controlled JSON vocabulary, exact aliases, explicit hard/soft
criteria, stable ID ties and complete evidence for exclusions. Prefer explicit
unknowns/shortfalls over relaxing or padding results. No BPM/LUFS semantic tags.

## 2026-09-07 — P003 — Replaceable adapters, explicit configuration

Runtime dependency: Pydantic only. The first optional live adapter uses OpenAI
Responses structured outputs through isolated standard-library HTTP. No model
is hardcoded; model/key are configured by the host. One request with bounds,
no retries/fallback and no catalog/audio sent. The offline provider is explicitly
a grammar parser. Live behavior remains unevaluated. The local desktop form
uses optional Tkinter so it adds no dependency to headless consumers or renderer.

## 2026-09-07 — P004 — Existing corpus supplies numeric evidence only

The DJ adapter consumes explicit stored JSON, validates its schema/version and
hash/ID consistency, preserves benchmark tempo status/source, and omits paths,
beat arrays and semantic assumptions. Demo semantic metadata is fictional and
labeled accordingly. Real semantic evaluation requires external annotations.
The package performs no source-audio reads, analysis or rendering.

## 2026-09-07 — P005 — Authorize the pool and configure live OpenAI

The user explicitly requested the 120-track pool and their project-specific
`AUTODJ_OPENAI_API_DEV_KEY` stored in `~/.zshrc`. Parent D040 supersedes the
previous pool hold only for read-only metadata/hash import and playlist use.
The audio-analysis/mixing engine remains independent, with no large analyzer
batch or render triggered by this request.

Add a bounded sequential FFprobe adapter and full-operation source manifest.
Use exact metadata label mappings from a separate 39-entry pool vocabulary;
retain ambiguous labels, invalid BPM and absent semantic evidence as unknown.
Use `encoded_fact` only for the supplied annotation, with warning; BPM stays
`benchmark_estimate`. Do not derive metadata from titles or infer mood/energy.

Configure `playlist.toml` with OpenAI `gpt-5.4-mini-2026-03-17`, an explicitly
pinned model supporting Responses/structured outputs per the
[official model page](https://developers.openai.com/api/docs/models/gpt-5.4-mini).
This is a project profile, not a new hidden library default. A native launcher
selects it. It reads the named environment variable or one literal assignment
in the configured shell file; it never executes shell code, copies the key,
or falls back to an unrelated generic key. Source credentials remain in place.

## 2026-09-07 — P006 — Learn from the first live count failure

The first authenticated request produced a schema-valid but wrong interpretation:
“up to five tracks” became limit 10 plus an invented fixed-limit restriction.
Search was correctly withheld because `unresolved` was nonempty. Preserve
that failure; schema validation alone does not establish intent preservation.

Version the translator prompt to `playlist-query-v2` and clarify that explicit
counts (including number words) set the query's adjustable 1–100 maximum;
10 applies only when no count is requested. Add a descriptive wire-schema
field and retain local bounds. The same live request then passes, followed
by five successful live pool cases. Do not generalize this small evaluation
to all prompts, languages, genre mappings or recommendation quality.

## 2026-09-07 — P007 — Make natural language the product default

The user entered “house dj set energetic” and received the offline grammar
help. Process inspection found the old offline form still running alongside
the configured OpenAI form. A configured launcher alone did not make the
user experience reliable; the old silent rules default was inappropriate
for a natural-language product. This supersedes P005’s no-config offline
CLI/UI behavior without changing the library’s explicit translator boundary.

Require OpenAI in the desktop, reject an explicit rules selection, and select
its profile from explicit `--config`, current-directory `playlist.toml`, then
the editable package checkout. Do not extend discovery to ordinary CLI data
commands or installed library consumers. Generic `prompt` defaults to OpenAI;
`--provider rules` remains an explicit offline developer option. Missing setup
and provider failures remain actionable errors, with no grammar fallback.

Revise translation to `playlist-query-v3`: direct single-genre requests require
that genre; ordinary energy/mood terms are preferences unless explicitly hard.
“DJ set” alone is playlist context, while rendering/transition/duration
operations remain unsupported. Do not silently broaden a house request to
other genres, and do not invent energy evidence to satisfy “energetic”.

Modernize the native Tk form with a light visual hierarchy, plain-language
criteria, titles/artists/BPM, visible preference-evidence gaps and optional
technical provenance. Retain standard-library UI/HTTP and Pydantic-only runtime
dependencies. The current pool has eight exact house annotations and no
normalized energy annotations. Review semantic evidence separately from
request translation. Parent D041/E029 and P-E003 record this correction.

## 2026-09-08 — P008 — Pause further playlist development

The user paused this package after the implemented V0.2 natural-language
workflow. Preserve its current contracts, catalog artifacts, tests and recorded
evaluation. Reviewed semantic annotation and broader prompt evaluation remain
the next backlog items, but are not active work until explicitly resumed.

Parent D042's cloud music-library hypothesis may eventually consume this
package through its existing typed boundary. It does not authorize cloud
hosting, remote catalogs, automatic MixPlan generation, rendering integration
or other implementation changes here.

## 2026-09-10 — P009 — Resume local evaluation and name the product PlaylistIQ

The user explicitly resumed the package to test its current state and prepare a
second evaluation on a more diverse local folder. Use **PlaylistIQ** as the
product and UI name. Preserve the installed technical identifiers—directory and
distribution `prompt-to-playlist`, CLI `prompt-playlist`, Python namespace
`prompt_to_playlist`, and serialized `prompt-playlist/*` schemas—to avoid a
breaking rename with no retrieval benefit.

The current 120-track catalog remains the metadata-only baseline. The resumed
scope does not authorize automatic MixPlans, rendering, cloud upload/deployment,
or silently running acoustic analysis on either existing music pool. A new
diverse folder must be identified explicitly before audio is read.

## 2026-09-10 — P010 — First-web feature policy excludes All-In-One

The first web-version selection layer should prioritize genre, curated mood,
energy/arousal, danceability, vocal profile, BPM, and optionally key/duration.
Keep the LLM as request interpreter and deterministic code as catalog filter;
do not send the full track table or audio to OpenAI. Loudness cannot become
energy, and low-level spectral features cannot become mood or danceability.

For the next local prototype, evaluate an Essentia TensorFlow
Discogs-EffNet shared embedding with small genre/mood/danceability/voice heads,
plus a separately measured DEAM-arousal candidate only if its extra pass is
affordable. Every output remains a model estimate with confidence, thresholds,
abstention, version, and provenance. The existing plain Essentia environment
lacks the required TensorFlow algorithms. Official author metrics are screening
evidence, not accuracy claims for this library.

Defer full mood-theme taxonomies, detailed instruments, standalone valence,
engagement/approachability, CLAP embeddings, stems, and LLM-visible low-level
DSP until an observed prompt/use case justifies them. Essentia/model commercial
and hosted use is not cleared; resolve the official non-commercial/proprietary
license path before a web deployment. `docs/AUDIO_FEATURES.md` is canonical.

## 2026-09-10 — P011 — Make auditability core and preserve later retrieval comparisons

The structured query plus deterministic evidence matching remains the primary
PlaylistIQ path because **it lets us audit why each track matched**. Preserve
the validated query, matched/missing criteria, evidence provenance, versions,
digests, stable IDs, and ranking inputs. A learned scorer may later rank an
eligible set, but it must not erase this explanation trail.

The next implementation command is descriptor extraction only: accept a folder
path as a variable input, process every supported track without All-In-One,
choose and write a versioned durable descriptor artifact for later matching,
and fully test/resolve the selected libraries, models, repositories, runtime
errors, resume behavior, and resource bounds.

After that baseline works, compare CLAP prompt-to-audio similarity, TF-IDF/BM25
over controlled comma-separated descriptor documents, lightweight text
embeddings over the same documents, and a hybrid structured-filter-plus-
similarity ranker. Use identical predeclared prompts and human relevance
judgments. This is explicitly later work, not part of the next build.

Commercial licensing stays recorded for eventual hosted/product viability but
is not a limitation or stop condition for the current private feasibility
playground. This updates P010's license wording without changing its selected
semantic features or deferred first-version list.

## 2026-09-10 — P012 — Ship descriptors as a measured sidecar before catalog migration

Implement PlaylistIQ 0.3.0 with an optional `analysis` dependency group and a
separate `analyze-folder` command. Keep the existing metadata importer,
catalog/search contract, and UI lightweight and unchanged. The analyzer writes
strict JSON plus JSON/Markdown performance evidence; it does not decide
thresholds, claim tag-axis completeness, or silently feed estimates to search.

Use JSON for the first descriptor artifact because it preserves nested raw
probabilities, provenance, warnings, timing and resume evidence; it is directly
inspectable by the user and LLM tooling at the present small scale. Revisit
columnar storage only after measured catalog size/query needs justify it.

Use sequential short-lived workers with explicit one-track default and
`--all-tracks` opt-in. Pin/hash model assets, verify source hashes/inventory,
keep output outside the music folder, and key checkpoints by source/config/tool/
model identity. Record process-tree wall time, CPU, RSS and supporting telemetry
for every algorithm and provide combined linear VM-planning estimates. Measured
CPU is authoritative because library thread requests are not guarantees.

The first semantic suite is the P010 list: acoustic genre, happy/sad/relaxed/
aggressive, danceability, voice/instrumental and DEAM arousal, plus BPM/key/
duration. Raw DEAM valence is retained at no extra inference cost but remains
deferred from matching. Loudness is retained for playback/mix use and is not
energy. All-In-One MLX remains excluded. The current private playground is not
blocked on commercial terms; production viability remains a later gate.

## 2026-09-11 — P013 — Make Beat This decoding explicit and reject failed-stage projections

The user's first full ten-track execution established that Beat This 1.1's
audio loader is not self-contained in the pinned environment: Torchaudio 2.11
requires TorchCodec, and Beat This only succeeds without it when SoundFile is
installed. Keep the lighter `soundfile==0.14.0` path as an explicit optional-
analysis dependency and preflight requirement. Do not add TorchCodec merely to
duplicate a working local decoder fallback. Commercial terms remain a future
viability note rather than a private-playground blocker.

Preserve valid pre-repair checkpoints by accepting their otherwise-identical
tool-version digest once and migrating it during resume. Failed attempts remain
auditable in track/stage telemetry, but they cannot contribute to capacity
extrapolation. A combined projection is valid only for tracks whose requested
stages all succeeded. The user, not the agent, runs the full repair with
`--all-tracks --resume`; bounded agent verification remains one or two tracks.

## 2026-09-11 — P014 — Accept the house runtime baseline, not semantic accuracy

P-E008 completes the repaired ten-track run with 60/60 successful stages and
unchanged sources. Treat its wall/CPU/RSS/output-size measurements as the
current local runtime and capacity-planning baseline for similarly sized house
tracks. They remain linear Mac observations, not VM benchmarks.

Do not promote raw genre, mood, danceability, vocal, arousal, valence, key,
tempo, beat, or downbeat estimates to reviewed truth. Beat This exactly
reproduces its earlier ten-track DJ-artifact outputs, which establishes local
reproducibility but not correctness. The atypical Dj Yellow downbeat ratio
keeps raw beat/downbeat grids out of PlaylistIQ retrieval; retain them as
provenance and future mixing diagnostics. The compact retrieval document may
use BPM with estimate authority.

Next implement a deliberate descriptor-to-catalog bridge with versioned
thresholds, abstention, raw-score preservation and evidence priority. Then run
the same matching evaluation on one explicitly authorized diverse folder.
Preserve the structured query/evidence trail because it lets us audit why each
track matched. CLAP, lexical/text embeddings and hybrid retrieval remain later
comparisons.

## 2026-09-11 — P015 — Authorize diverse-37 and reuse verified work by audio identity

The user explicitly names `test_folder_37_tracks_diff_genres` as PlaylistIQ's
second, more-diverse local descriptor corpus and keeps the full run as a user
terminal action. Its source is read-only. Record its immutable pre-analysis
inventory before decoding and write results only to the separate
`output/playlistiq-diverse-37` directory.

Reuse completed work by SHA-256 and the complete checkpoint identity—not by
filename and not by overwriting the house baseline. Add repeatable
`--reuse-from` inputs. A reuse source must be a valid prior descriptor output
whose source-hash and inventory gates passed. Each imported stage must still
match the current pipeline, algorithm, tool versions, model hashes, and CPU
configuration; copy it atomically into the new output. Missing or incompatible
stages execute normally, while `--resume` handles interruptions in that new
output.

The manifest has 37 unique tracks: ten exact baseline overlaps and 27 new
hashes. All 60 expected old checkpoints pass current compatibility validation,
so the planned run should import 60 stages and execute 162. This prepares
descriptor evidence only. It does not merge the catalog, run matching, claim
semantic accuracy, invoke All-In-One, render, call a provider, or activate
cloud work.

## 2026-09-12 — P016 — Keep PlaylistIQ independent inside the unified Resonant workflow

Parent D058 evolves the user-facing product from a quick mix tool plus a
standalone prompt utility into one DJ workspace for library listening, playlist
editing, continuous playback, eligible-file download and later deterministic
mixes. PlaylistIQ supplies an auditable playlist proposal—query, candidates,
evidence and stable IDs—which the Resonant host may turn into an editable saved
playlist.

Keep playlist persistence/order, provider authentication and availability,
playback, whole-playlist archive jobs and mix rendering outside this package.
Provider playability is not download authorization. This decision changes no
package schema, runtime, dependency, catalog, model call or local evaluation
boundary; it clarifies the future consumer contract and preserves independent
reuse.

## 2026-09-13 — P017 — Add opt-in MAEST Discogs519

User authorizes setup alongside the existing genre model and requests a terminal
command for the 37-song folder. Use the MAEST v2 graph with integrated Discogs519
sigmoid output, pinned assets, batch one, full-song patch mean and top-ten JSON.
Reuse existing bounded workers and checkpoints. Six-stage defaults and existing
outputs remain preserved. Agent smoke is one song; full run belongs to the user.
See docs/MAEST_DISCOGS519.md.

## 2026-09-13 — User-authorized standalone MAEST listening review

Preserve the 33 valid estimates and four failed songs in an offline review;
join top-ten and full scores by source hash, keep human judgments separate,
and export them explicitly. No new analysis or change to memory limits.
The report is a local artifact, not a hosted product or catalog integration.

## 2026-09-15 — MAEST top-six and local player integration

Owner-authorized `maest-top6-v1` now replaces legacy genre estimation: match the top six, display three expandable to six, retain all 519 scores, and apply no probability threshold or human review overrides. Historical outputs remain preserved. The low-priority board card `PIQ-GENRE-TOP6-REVISIT` is Later / could; further genre experimentation is not a launch blocker.

The local web player now provides **Analyze tracks** and **Create with PlaylistIQ**. Its loopback Node job service invokes the existing Python environment; analysis persists by source hash and in IndexedDB, and prompt results save into normal playable playlists. Restart the player server on the same origin/port to retain the browser library. This explicit integration authorization supersedes older local bridge/Python-edit holds; cloud deployment, remote audio processing and automatic MixPlans remain deferred.

See [integration contract](docs/WEB_INTEGRATION.md).

## 2026-09-15 — Analysis workspace and fresh-export repair

Analyze tracks and PlaylistIQ now sit in the top controls. Feature columns toggle in the track list; the Analysis tab uses the full width with sticky track names and headers, horizontal scrolling, genre scores, tempo/key/loudness/arousal, mood/danceability/vocal scores and missing-stage details. Option 2 uses compact transport in Analysis. PlaylistIQ is a themed page with analyzed-track count, prompt form and inline results/save action; the earlier technical introductory copy is removed.

Fresh MAEST export NameError fixed; persistent checkpoints and invalid-worker-output recovery added. See the player WORK_LOG and PlaylistIQ WEB_INTEGRATION for evidence and retry instructions.

## 2026-09-16 — P018 — Learn taste mainly from repeated playlist grouping

A future PlaylistIQ iteration should personalize candidate ranking from the
user's own playlist-building patterns. Shared membership in manually built
playlists is the primary signal: repeated co-grouping is stronger evidence than
one shared playlist. Track adjacency or order may be evaluated separately, but
mere absence from a playlist is not negative preference evidence.

Playlist names are optional, low-confidence context because naming is sparse,
inconsistent and often decorative. A title/request match may slightly inform a
ranking only when supported by the playlist's tracks; it must not create genre,
mood or other catalog facts and must not outweigh repeated grouping behavior.

Personalization ranks only the set left after explicit request constraints,
availability and rights checks. It must preserve the baseline score and expose
each learned contribution, source playlist IDs, training snapshot/version and
minimum-support/cold-start behavior. Give the user opt-out, rebuild and reset
controls. Keep learning private to the user, distinguish manual playlists from
generated/imported/system playlists, and review provider policy before using
remote playlist data. This is roadmap authorization only; no collection,
training, schema change or runtime behavior is implemented by this decision.

## 2026-09-17 — Creative-intent planner research and YAML evaluation

### P019 — Research better creative-prompt planning; evaluate serialization separately

The owner reports limited result quality and requests ranking with MAEST scores,
broader creative-prompt planning research, ACE-Step 1.5 inspection, full/digest
reports and a YAML-versus-JSON to-do. The reports recommend probability-aware
ordering first, then typed intent planning, grounded hybrid retrieval and measured
playlist selection. Preserve explicit constraints, distinguish inferred preferences,
and treat recipient taste and lyrical themes as separate evidence needs.

The old low-priority genre-experiment note does not prohibit this newly requested
probability-ranking work. Keep changes to top-six eligibility, thresholds, taxonomy
and estimator choice independently evaluated. No implementation is delivered in
this research pass; numerical weights and planner schema examples are proposals.
No new audio, live inference, training, cloud/provider execution or format migration.

[Full report](docs/research/PLAYLIST_PLANNER_RESEARCH_2026-09-17.md); [digest](docs/research/PLAYLIST_PLANNER_DIGEST_2026-09-17.md). Board PIQ-020 / LATER-PIQ-YAML tracks
serialization comparison rather than a decision to adopt YAML.

## 2026-09-19 — PlaylistIQ Iteration 1 delivered

Python 0.4.0 / player 0.3.0 now integrate `playlist-intent-v1.3` (configured low reasoning), `intent-compiler-v1.1`, `maest-intent-v1` ranking and `discogs-parents-v1`. Required genres use MAEST support; creative prompts use directional soft priorities. Genre OR/family matching, original-request clarification, per-track contributions and twenty-prompt review evidence are available. New result/catalog/translation/run writes use schema 0.2.0 and read historical 0.1.0.

422 Python tests and 50 web tests pass. Final compiler replay passes all 20 intent/constraint checks; live revision failures are preserved, and final optional/HTTP checks pass. Human listening acceptance remains pending. No new audio analysis or cloud work; YAML is still a consideration task.

See [implementation, prompt, contracts and verification](docs/ITERATION_1.md). This current checkpoint supersedes older descriptions of v3-only translation, flat genre ties and missing parent matching; dated older sections remain historical evidence.

## 2026-09-22 — P020 — Implement the bounded hybrid estimator upgrade

Owner explicitly requested more research, a decision, full implementation and small pipeline tests. Choose MuQ-MuLan-large plus shared Discogs-EffNet Jamendo 56 mood/theme and 40 instrument heads; retain specialist estimators and legacy moods, expose raw DEAM valence. Music2Emo and FIGMA remain controlled comparison candidates. This is a practical selected baseline, not a proven best mood estimator.

Versioned segment/query embeddings support deterministic local replay. Hard constraints precede provisional 30% semantic / 70% structured fusion; complete eligible coverage is required. Newly added numeric objectives also require complete eligible coverage. Missing/failed inference is disclosed, old usable evidence survives failed upgrades, and cached source identity prevents wrong-file reuse. Soft preferences are constrained by a catalog-derived schema, while explicit constraints retain the full vocabulary so unsupported requirements cannot disappear.

Read [research rationale](docs/research/ESTIMATOR_UPGRADE_2026-09-22.md) and [implementation evidence](docs/ESTIMATOR_UPGRADE.md). Two-track regression scope, private local audio, no automatic whole-library run; JSON remains the current serialization and the YAML consideration task remains open.

## 2026-09-25 — Selectable supervised feature estimators

Music2Emo (MERT-95M + BTC/chord/key + J_all, corrected mode) and MusiCNN danceability are implemented as optional direct-feature challengers. The specialist reference remains default; MAEST top-six, MuQ and ranking weights are preserved. Complete compatible catalog coverage is required per challenger; otherwise everyone retains the reference. Two authorized sources passed six matched-window stages and zero-inference retries. Final checks: 481 Python tests, 80 web tests, 45 JS syntax modules, 28-file build, 40 exact fixed-query replays and one final successful live replay. One prior live intent proposal was rejected; no new listening judgments or superiority claim.

Exactly two local cache records have both challengers. Original Chrome was observed at 109 unique tracks; its final updated display was not confirmed because native interaction was interrupted by active use. The new reload migration attaches richer same-hash optional caches to completed reference records. Isolated browser acceptance verified real values, retry, profile/scope, saved-result reopening, App Status and 390/320px controls. No batch/new-corpus inference, audio upload, cloud work, commit or format migration.

Read [research, commands, failures, coverage and continuation](docs/SUPERVISED_ESTIMATORS.md). Historical sections/publication cutoffs below remain evidence for their original dates.


## 2026-09-25 — Next: quality-first estimator research, then implementation

Owner requests a ranked shortlist of the strongest estimators for every non-genre feature, followed by full implementation of the highest-ranked available choices. Quality evidence dominates; local Mac feasibility is secondary and licensing has zero selection weight for this proof of concept. Deliver an implementation-ready technical report and a concise reader report before implementation. Preserve MAEST and the current planner/MuQ branch. This is recorded next work, not completed research; the existing optional challengers do not close the objective. [Scope, deliverables and acceptance](docs/TOP_ESTIMATORS_NEXT_TASK.md). Documentation only in this handoff; no inference, model selection or runtime change performed.


## 2026-09-25 — Quality-first estimator research and implementation

Quality-first non-genre research and the selected available specialists are delivered locally. The web default selects Music2Emo theme/VA, MusiCNN vocals, VGGish aggression and independent PaSST OpenMIC instrument evidence, retaining EffNet happy/sad/relaxed/danceability. SheetSage2 supplies selected key evidence. MAEST, MuQ and planner weights remain unchanged. Two authorized sources passed 8/8 new stages; retries execute zero stages. Richer nuanced-emotion prediction and listening superiority remain unresolved; do not present encoder-only releases or the same 56 tags as solving that objective.

[Implementation, two research reports, setup, model contracts and verification](docs/TOP_ESTIMATORS_IMPLEMENTATION.md). Final validation: 502 Python tests, 83 web tests, 45 syntax modules, 28-file build, eight successful final audio stages and 26 exact fixed-query replays. No new provider calls or listener judgments. The new optional specialist stages and quality/openmic vocabulary identity preserve reference records and saved-profile replay.
