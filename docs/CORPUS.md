# Corpus Policy and Manifest

## 2026-10-06 — Individual accounts and spectrum motion

[Account release](../packages/web-player/docs/ACCOUNTS_RELEASE.md) replaces shared hosted state with email/username/password accounts, private playlists/PlaylistIQ results/listening counters, owner-only bounded analytics and a full-spectrum motion override. Google sign-in/linking is implemented but activation and real-provider acceptance await a Google web client ID. Owner authorized deployment, a test user, live-history reset and Git push. Current rollout receipt and limitations are maintained in the linked checkpoint; audio, saved analysis and planner policy are preserved.

## Purpose

This document prevents accidental analysis of the wrong folder and records the
exact corpus intended for each milestone.

Cloud research D043/E030 accessed no source audio and performed no fresh
hashing, analysis or rendering. Existing preservation evidence remains
historical. Future cloud experiments specify generated/licensed fixtures and
need separate authorization; neither existing music folder is substituted.

## Authorized V1 corpus

Path:

`test_folder_10_house_tracks`

Status:

- Confirmed by direct directory inspection on 2026-08-31 and re-listed
  2026-09-03.
- Contains 10 MP3 files.
- Intended content: house music, expected roughly 120–130 BPM.
- Authorization: approved for Step 1 analysis and for Step 2 scoring/lookups
  against the resulting JSON. Clip/set renders may read explicitly planned
  MP3s but must write outside this folder. Do not batch-render these 10 files.
- Parallel playlist authorization (D039): read the existing analysis JSON for
  catalog import and retrieval; this does not authorize another audio-analysis
  or render run.
- Source policy: strictly read-only.

## Pre-analysis SHA-256 (2026-09-03, before first analyzer run)

Recorded with filesystem paths (Unicode as stored; do not renormalize):

| bytes | sha256 | filename |
|---|---|---|
| 13724255 | `c4fa9722112e74661c9a4da26fa386d9a65564da8a3cef25048df25168f31bae` | 01 My Paradise - Edit.mp3 |
| 13948035 | `ef90c63da5fb3352752e0c9283cf3ef0d0d8a961b3d4585da5e11ffba2a8a098` | 02 For The Record.mp3 |
| 13687582 | `ba1f70fcb558e4ff5d503ad6eec2fa6d0da0dd6224dfcb8cae2a14a8f309aa5e` | 03 Fantazia.mp3 |
| 17143685 | `61729acd08bdd113156aba71339314a33526fb4cbfc34c26a2fc8207cd757312` | Demi Riquisimo, CLINT - Love State.mp3 |
| 16266517 | `d5afdfa310e303d7b22ca34ddfcb7d62e7116dfd9ddb7a538010dad289e1cb12` | Demi Riquísimo - Certified.mp3 |
| 13094730 | `8d978efd1aa0445c320ceb95fde91f04cd2a7bdc02fc194556a6b7cd7f8d317c` | Demi Riquísimo, The Trip (UK) - Rock The House (Original Mix) 2.mp3 |
| 20445166 | `f195c619b1141d4bbe9fc480bef20196f327936e3e4bc6986c016e297fb2b473` | Dj Yellow Ft Marlene - Je Tm.mp3 |
| 12249789 | `5c14ad63ead29257845ca73b14f926f876594378b9b8d38c5283f9c2b1cc2161` | Laroze - Wildest Desire [www.slider.kz].mp3 |
| 19321390 | `b2a28ec1788e87957e84a395803d7a2ce06d7f18ec289ca04ceb48887fae6682` | Lemon8 - Triple Funk.mp3 |
| 12489209 | `c3db9c0d5e51987bbf15394b6fda1447843c222881d3fdec12974f04a89dedde` | Life Is Trippy (Original Mix).mp3 |

Post-run hashes must match these values exactly.

## Step 1 analysis progress (2026-09-04)

Complete All-In-One in `output/step1-collection.json` (E021): all 10 files.
Source SHA-256 still matches the pre-analysis table. Tempo/key/beats/sections
are `benchmark_estimate`, not facts.

Scoring (`dj-score`) consumes this JSON. It does not re-read or modify the
MP3s. First-transition stretch from 120 BPM to the rest of the corpus
cannot stay inside 4% (E022). `--summary` / `--windows` return compact
lookups without dumping beat arrays.

Clip renders (`dj-render`) must write outside this folder. Unit tests use
generated sine WAV/MP3s, not these 10 files. Do not batch-render the
corpus.

The D036 hand-authored plan in `examples/mvp-three-track-plan.json` selects
My Paradise → Rock The House → Lemon8 and validates to 609.318 seconds. The
plan was validated against IDs, hashes, downbeat indices, bounds, and duration
during E024. The user later ran it, producing
`output/mvp-three-track-set.wav` and its manifest without changing any source
hash. Listening rejected its two 14.44-second volume-only transitions and
reported perceived downbeat misalignment.

The D037 revision is `examples/mvp-three-track-plan-v2.json`. It retains the
same three sources and transition start positions, extends the first two
outgoing tails, and validates to 609.100 seconds. Both transitions resolve
from stored downbeat spans to 29.090 seconds with 0.010 and 0.000 seconds of
adjacent-grid drift. The user rendered it to
`output/mvp-three-track-set-v2.wav`; its manifest records 609.100 seconds,
−13.81 LUFS, 3.1 LU loudness range, +1.04 dBTP, and unchanged hashes for all
three source tracks. The user accepted transition duration and downbeat
alignment as a much better first version (D038/E026). The +1.04 dBTP warning
keeps final-bus headroom/mastering open.

`dj-render downbeat-clicks` also created three centered 30.000-second WAVs in
`output/downbeat-clicks/`. The user reported the primary downbeat diagnostic
was great. This is bounded `user_verified` listening evidence for the heard
diagnostic and v2 transitions; the immutable collection JSON continues to
label rhythm grids `benchmark_estimate` outside that scope.

## Playlist evidence and fixtures (2026-09-07, D039 / E027)

The independent `packages/prompt-to-playlist/` module may import
`output/step1-collection.json` as metadata. This adapter reads JSON only; it
does not open MP3s, resolve analysis by rerunning a model, or write into either
music folder. Existing track IDs, duration metadata, and BPM provenance remain
available for deterministic retrieval.

There are no per-track semantic mood, genre, or energy annotations in the
completed artifact. The corpus description “house” identifies the collection's
intended scope; it is not ten verified per-track tags. BPM, LUFS, filenames,
and the user's desired mood must not be converted into fabricated tag evidence.
Queries requiring unavailable semantic evidence may correctly return no
matches. This is a catalog-coverage limitation, not a retrieval failure.

Labeled examples under the new package are synthetic catalog fixtures for
testing translation and retrieval. Their tags and titles are not annotations
of these ten songs. A future reviewed annotation source must stay separate
from immutable Step 1 JSON and preserve provenance. Playlist tests and JSON
smoke checks are recorded in E027 separately from audio/listening experiments.

E027 imported all ten tracks in memory, preserved every BPM's
`benchmark_estimate` authority and `warning` status, and produced zero semantic
tags. A 130–133 BPM query found six eligible tracks and returned five at its
limit; requiring `genre:house` returned zero. All ten audio SHA-256 values
matched the manifest before and after the work. The collection JSON also
remained unchanged, SHA-256
`348d2f857b5d98476386e8da3499fbad15966cf68814beda497a9062459fdb93`.
No new audio analysis or corpus render was run.

## V1 display manifest

1. `01 My Paradise - Edit.mp3`
2. `02 For The Record.mp3`
3. `03 Fantazia.mp3`
4. `Demi Riquisimo, CLINT - Love State.mp3`
5. `Demi Riquísimo - Certified.mp3`
6. `Demi Riquísimo, The Trip (UK) - Rock The House (Original Mix) 2.mp3`
7. `Dj Yellow Ft Marlene - Je Tm.mp3`
8. `Laroze - Wildest Desire [www.slider.kz].mp3`
9. `Lemon8 - Triple Funk.mp3`
10. `Life Is Trippy (Original Mix).mp3`

The display list is for human review, not byte-exact path reconstruction. The
filesystem uses Unicode composition for some accented names. Code must use the
paths returned by the filesystem and must not reconstruct or normalize
filenames for access. Machine-readable paths and hashes are in
`output/step1-collection.json` and the table above.

`.DS_Store` is not an audio input.

## Playlist pool (D040, 2026-09-07)

Path:

`test_tracks_folder_mp3`

Known state:

- The 2026-09-07 metadata pass confirmed **120 MP3 files** (121 directory
  entries; one skipped), with no duplicate file hashes or import failures.
- It was the target context for the broad tooling report.
- The pool totals 1,381,021,989 source bytes and 33,587.244764 seconds of
  encoded duration metadata (approximately 9 h 20 min). This inventory is
  independent of the ten-track engine analysis corpus.

Policy:

- Do not silently substitute this folder for the V1 corpus.
- The user's follow-up explicitly authorizes this pool for the independent
  playlist selector. D040 supersedes the previous blanket no-use rule only
  for read-only source hashing and ffprobe container/embedded-tag inspection.
- The import produces local catalog/coverage JSON outside the music folder.
  It does not create decoded PCM, stems, acoustic estimates, or renders.
- Run metadata probes sequentially with bounded per-file timeouts; this is a
  lightweight metadata operation, not the high-RAM Step 1 stack. Do not run
  All-In-One, Beat This, Essentia, or another acoustic analyzer on this pool.
- Preserve exact discovered paths and verify SHA-256 before and after import.
  Embedded metadata must retain source provenance and its unreviewed status;
  absent metadata stays absent. Do not invent mood/genre/energy from filenames,
  folder identity, BPM, LUFS, or model knowledge.
- Only the playlist request, vocabulary, and query contract may go to OpenAI.
  The local pool's audio, file paths, titles, and catalog remain local.

### Canonical metadata snapshot (E028)

- Catalog: [`pool-catalog.json`](../packages/prompt-to-playlist/output/pool-catalog.json).
- Source/coverage manifest:
  [`pool-import-manifest.json`](../packages/prompt-to-playlist/output/pool-import-manifest.json).
- Importer `mp3-metadata-v1`, ffprobe 8.0.1, per-file timeout 10 seconds;
  canonical import elapsed 6.292754 seconds.
- All 120 source hashes and the directory inventory matched before/after.
  The manifest contains the exact discovered paths and all before/after
  SHA-256 values; do not reconstruct filenames from display text.
- Catalog SHA-256:
  `edee12016a37133218cfddeb620dad3b1bdfb563a1643af75f0654f444e32a8f`.
- Manifest SHA-256:
  `84236b16223d88c4bb0f41a33afecad53af4bfa31db87b65b1eec58276e9d009`.

| Imported metadata/evidence | Tracks |
|---|---:|
| Title | 120 |
| Artist | 116 |
| Encoded duration | 120 |
| Embedded BPM estimate | 22 |
| Any encoded genre text | 65 |
| Genre mapped to the project vocabulary | 62 |
| Unmapped genre text | 3 |
| Normalized mood/energy/vocal tags | 0 |
| Complete genre-axis coverage | 0 |

The project vocabulary has 39 descriptors. The three unmapped genre strings
are `Bar House Deep`, `Disco Italo-Disco`, and `LAGRIMA DE OURO`; they remain
unresolved source annotations instead of guessed classifications. Some raw
fields such as `mood` (three files) and `energylevel` (seven) are present in
the tag-key inventory but lack a reviewed mapping into the catalog contract.
The zero normalized coverage above does not assert those raw fields are absent.

E028's final read-only verification again matched all 120 pool hashes to the
manifest and all ten engine-source hashes to the original table. The engine
analysis JSON also remained unchanged at SHA-256
`348d2f857b5d98476386e8da3499fbad15966cf68814beda497a9062459fdb93`.
No acoustic analysis or real-audio render was run for this setup.

### Natural-language interface correction (D041/E029)

The saved metadata snapshot contains eight tracks with the exact `genre:house`
tag. A request such as “house dj set energetic” can select those house
annotations while keeping high energy as an unverified preference. No normalized
energy evidence exists, and no house-family expansion is implied. This UI and
translation correction reads the saved catalog only; it does not reimport,
analyze, render or modify either music pool. Source-preservation observations
above remain the E028 checks, not a new audio-hashing run.

## Discovery rules

- Accept explicit folder paths; never guess a nearby corpus.
- Default to non-recursive discovery for V1 unless the CLI says otherwise.
- Match supported extensions case-insensitively.
- Skip hidden files and unsupported formats with structured warnings.
- Sort only for deterministic processing; do not treat filename order as mix
  order.
- Record path exactly as discovered plus a stable relative-path representation.
- Reject an empty folder with a clear error.
- Reject or warn when the selected folder contains a different audio count than
  expected by the experiment.

## Source preservation

Before analysis:

- Record file byte size and SHA-256.
- Do not update tags, timestamps, names, or directory structure.
- Do not create sidecar files inside the source folder.

After analysis:

- Recalculate SHA-256 and require equality.
- Store generated JSON, temporary PCM, visualizations, and renders outside the
  source folder.
- Delete temporary PCM only after dependent analyzers finish and results are
  safely written.

## Corpus limitations

The 10-track set is useful for:

- Installation and compatibility validation.
- Schema validation.
- House-specific tempo/downbeat/section experiments.
- Basic harmonic-ordering and transition prototypes.
- First mix renders.

It is not sufficient to prove:

- Universal BPM, key, downbeat, or section accuracy.
- Generalization beyond house.
- Robust behavior on live drums, rubato, beatless music, variable tempo, or
  very different production styles.
- Semantic genre/mood accuracy.

Any claim about general performance requires a broader, intentionally selected,
manually reviewed corpus.

## Required experiment record

Every corpus run must append to `EXPERIMENT_LOG.md`:

- Date and goal.
- Exact folder path.
- Discovered filenames/count.
- Source hashes before and after.
- Tool, model, and system versions.
- Commands/configuration.
- Runtime and failures.
- Output paths and schema version.
- Accuracy/listening-review observations.
- What was learned and what decision is affected.
