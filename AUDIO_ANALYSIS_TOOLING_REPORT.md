# DJ Metadata and Audio-Analysis Tooling Report

**Revision:** 2.0 — strict calculated-feature edition  
**Research cutoff:** 2026-08-30  
**Target:** 120 MP3 tracks on an Apple Silicon Mac  
**Durable role:** canonical tooling, evidence, lifecycle, and rejection registry

## Live v1 status (read this first)

This report is a **frozen research registry**. It is not the implementation
plan and not current project status.

- Takeover brief: [`AGENTS.md`](AGENTS.md)
- V1 corpus is 10 house tracks, not the 120-file folder named here
- Installed FFmpeg is **8.0.1** (D020), not the 9.0.1 release reviewed here
- Stretch in v1 uses FFmpeg `atempo` (D034); this report does not choose
  the render engine
- Do not “follow Stage 1” below (make 120 files visible, pin FFmpeg 9.0.1)

Update this registry only when evidence, lifecycle, or a tool-selection
decision changes. Implementation status lives in `AGENTS.md` and
`V1_ENGINE_PLAN.md`.

## Executive summary

The first edition was too broad. It rewarded useful tools even when their output
did not meet the project's actual requirement: retain only calculated audio
features that can be defended as nearly perfect.

That stricter requirement materially changes the result:

- **Keep FFmpeg/ffprobe** as the canonical decoder, stream inspector, integrity
  checker, and standards-based measurement engine.
- **Keep FFmpeg EBU R128 plus pyloudnorm** for loudness and loudness-range
  measurements, with version-pinned cross-validation.
- **Keep librosa** only for mathematically defined, deterministic DSP
  measurements. Do not promote its tempo, beat, key, or segmentation estimates
  as facts.
- **Keep selected Essentia core algorithms** only when the output is a defined
  deterministic measurement and its AGPL/commercial licensing is acceptable.
- **Use MediaInfo only as an independent stream-fact cross-check.**
- **Benchmark All-In-One MLX and Beat This**, but do not write BPM, beats,
  downbeats, or sections as authoritative fields until they pass a collection
  ground-truth gate. Published results prove that neither is nearly perfect
  across arbitrary music.
- **Do not retain automatic global key as authoritative.** Every reviewed key
  detector remains materially fallible or lacks deployment-quality evidence.
- **Dispose of all genre, mood, energy, danceability, instrumentation,
  free-text embedding, and semantic classifiers** from the authoritative
  feature lane. They are probabilistic judgments, not objective measurements.
- **Dispose of identity and catalog enrichment tools** from this project's
  calculated-feature scope.
- **Treat proprietary DJ suites only as black-box benchmarks and export
  compatibility targets.** None exposes a stable headless analysis API or
  rigorous current-version accuracy evidence.
- **Defer stem separation.** Demucs and `audio-separator` are useful, but stem
  bleed and artifacts prevent near-perfect status.

The result is intentionally smaller than the requested feature wish list.
Useful-but-wrong output is worse than a missing field.

## Chromaprint correction and disposal decision

Chromaprint does **not** produce a transcript, low-quality or otherwise. It
creates a compact acoustic fingerprint designed to identify the same or
near-identical recording. That is a different task from transcription and from
calculating BPM, key, beats, sections, loudness, genre, instruments, or mood.

Chromaprint remains technically strong for identity matching: it began in 2010,
released version 1.6.1 on 2026-07-28, is actively maintained, and recently
received security and parser fixes. We are disposing of it because:

1. Recording identity is outside the revised calculated-feature-only goal.
2. Its output cannot improve the accuracy of the requested acoustic features.
3. Adding it would create an AcoustID/MusicBrainz enrichment branch, network
   terms, caching, and maintenance that do not advance the current goal.

Final disposition: **NOT NEEDED — scope mismatch**, not “bad transcription.”

## What “nearly perfect” means here

No MIR model reviewed is universally nearly perfect. To avoid moving the goal
posts, the project adopts explicit quality classes and gates.

### Output classes

1. **Encoded facts:** codec, sample rate, channels, frame properties, file
   duration, and decoder errors. These can be exact relative to the encoded
   stream.
2. **Standards-based measurements:** EBU R128/ITU-R BS.1770 loudness, sample
   peak, and true peak under pinned settings. These can be accepted within the
   standard's tolerance and implementation cross-checks.
3. **Deterministic DSP measurements:** RMS, spectra, chroma vectors, onset
   envelopes, spectral centroid, bandwidth, rolloff, contrast, and similar
   numerical transforms. These are reproducible for pinned PCM and parameters,
   but their musical interpretation is not objective.
4. **Event/model estimates:** BPM, beats, downbeats, meter, key, pitch, chords,
   sections, and stems. These require reference annotations, uncertainty, and a
   reject option.
5. **Semantic judgments:** genre, mood, energy, danceability, instrumentation,
   vocals, similarity, and text alignment. These are taxonomy- and
   model-dependent; they cannot enter the authoritative feature lane.

### Default acceptance gate

Until the user changes it, “nearly perfect” means:

- Deterministic reruns are numerically stable within a documented tolerance.
- Standards-based results pass official conformance material and agree with an
  independent implementation within the applicable tolerance.
- Continuous reference values stay within the feature-specific tolerance on
  every representative validation item.
- Event outputs achieve at least 0.995 F1 on the project's representative
  annotated set, with no catastrophic half/double-tempo or phase errors.
- Categorical outputs achieve at least 0.995 macro-F1 with calibrated
  abstention. On a small collection this effectively means no unreviewed
  mistakes.
- Any analyzer may return **unknown**. It must not guess to fill a column.
- Passing one genre does not authorize the analyzer for every genre.

These thresholds are intentionally severe. Current beat, key, structure,
semantic, and source-separation systems do not clear them generally.

## How to read the registry

Two scores prevent category confusion:

- **Technical quality:** how good and credible the tool is at its intended job,
  independent of this project.
- **Strict project fit:** usefulness for nearly-perfect locally calculated audio
  features. A technically excellent catalog or fingerprint tool can score zero.

Both use 0–10 engineering scores. They are not published benchmark percentages.

### Decision labels

- **KEEP:** belongs in the authoritative calculation pipeline for a limited,
  explicitly named output class.
- **OPTIONAL INFRA:** useful plumbing but not a calculated-feature source.
- **BENCHMARK:** run for comparison; output is not ground truth.
- **RESEARCH ONLY:** informative experiment with no production authority.
- **NOT NEEDED:** valid tool, wrong purpose or redundant.
- **REJECT:** abandoned, inaccessible, insufficiently licensed, destructive, or
  clearly below the required quality.

### Source grades

- **A:** official documentation, release registry, standard, model card,
  license, or peer-reviewed paper.
- **B:** primary source with missing chronology, incomplete validation, or
  author-only parity/accuracy evidence.
- **C:** preprint-only, conflicting licensing, sparse project history, or weak
  vendor/community evidence.

Source-grade summary across 68 registry entries:

- **54 A-grade:** strong evidence for existence, lifecycle, scope, or published
  benchmark.
- **12 B-grade:** primary evidence exists, but chronology or independent
  validation is incomplete.
- **2 C-grade:** KeyMyna and Platinum Notes have major evidence or licensing
  gaps.

An A grade does not mean near-perfect output. It means the statement about the
tool is sourced well. Many A-grade papers explicitly demonstrate substantial
error.

## Canonical enriched registry

Dates are the latest verifiable public release or meaningful code/service
update as of the cutoff. `Unknown` is deliberate. “Abandoned?” is binary as
requested; maintained live services and maintenance-only projects are `No`.

### Metadata, stream inspection, identity, and enrichment

| Tool | Why people care overall | Purpose for this project | Output-quality summary | Technical quality | Strict fit | Source | First release | Last verified update | Ongoing? | Abandoned? | License / access | Decision | Unknowns |
|---|---|---|---|---:|---:|---|---:|---|---|---|---|---|---|
| Mutagen | Mature frame-level metadata I/O across audio formats | Only needed if raw ID3 preservation or later tag writes return to scope; calculates no acoustic feature | High metadata fidelity; not an analyzer | 8.7 | 2.0 | A — official changelog and docs | 2006 | 2026-06-25 v1.48.1 | Yes | No | GPL-2.0+ | OPTIONAL INFRA | Transactional-write guarantees require project tests |
| FFmpeg / ffprobe | Industry-standard decode, probing, validation, resampling, and filters | Canonical decoder, stream truth, corruption check, and measurement substrate | Exact stream facts and deterministic decode subject to pinned build/options | 9.5 | 10.0 | A — official releases and filter docs | 2000 | 2026-08-12 v9.0.1 | Yes | No | LGPL-2.1+ or GPL by build | KEEP | ffprobe-specific initial year unknown |
| TagLib | Mature cross-format C++ metadata library | No calculated-feature role; redundant if tags are out of scope | Strong tag I/O only | 8.5 | 1.0 | A — official dated releases | 2004 | 2026-07-20 v2.3.1 | Yes | No | MPL/LGPL core | NOT NEEDED | None material |
| pytaglib | Python binding to TagLib | Adds no acoustic analysis | Wrapper quality follows TagLib | 7.8 | 1.0 | A — PyPI history | 2012 | 2026-02-03 v3.2.0 | Yes | No | GPL-3.0+ wrapper | NOT NEEDED | None material |
| eyeD3 | Focused MP3/ID3 editing and inspection | No calculated-feature role | Good MP3 metadata handling only | 7.5 | 0.5 | A — PyPI history | 2002 | 2025-11-16 v0.9.9 | Yes | No | GPL-3.0 | NOT NEEDED | None material |
| MediaInfo | Rich independent technical-media reports | Cross-check ffprobe duration, codec, channels, and bitrate mode | High-quality stream facts; not a full decoder validator | 9.0 | 4.0 | A — official changelog | 2002 | 2026-05-12 v26.05 | Yes | No | BSD core | BENCHMARK | None material |
| TinyTag | Tiny dependency-free tag/property reader | Redundant with ffprobe; no MIR features | Reliable common fields, intentionally read-only | 7.5 | 1.0 | A — PyPI and changelog | 2014 | 2026-07-31 v2.3.0 | Yes | No | MIT | NOT NEEDED | Earliest public year based on registry |
| ExifTool | Extremely broad forensic metadata inspection | Diagnose unusual metadata only; no calculated audio feature | Excellent metadata breadth, not MP3 analysis | 9.0 | 1.0 | A — official site/releases | 2003 | 2026-05-27 v13.59 | Yes | No | Artistic/GPL | NOT NEEDED | Production-designated release lags latest |
| music-tag | Simplifies Mutagen behind a common API | Hides details and provides no feature extraction | Stale convenience wrapper | 4.0 | 0.0 | A — PyPI proves inactivity | 2019 | 2021-06-05 v0.4.3 | No | Yes | MIT wrapper plus GPL dependency | REJECT | Maintainer intent unknown |
| AudioMeta | Unified tag and rating API | Beta metadata scope; pinned old dependency; no feature calculation | Young and insufficiently proven | 6.0 | 0.0 | A — PyPI | 2025 | 2026-04-11 v1.4.3 | Yes | No | Package-dependent | REJECT | Destructive corpus behavior unvalidated |
| Pillow | Standard Python image processing | Cover-art validation only; no audio feature | Excellent image tooling, irrelevant to signal analysis | 9.0 | 0.0 | A — official release notes | 2010 | 2026-07-01 v12.3.0 | Yes | No | MIT-CMU | NOT NEEDED | None material |
| Chromaprint / fpcalc | Fast identity fingerprint for matching the same recording | No purpose under calculated-feature-only scope; not transcription | Excellent identity signal, zero descriptive-feature value | 9.0 | 0.0 | A — official purpose and releases | 2010 | 2026-07-28 v1.6.1 | Yes | No | MIT | NOT NEEDED | Identity can return only if scope changes |
| pyacoustid | Python bridge for fingerprints and AcoustID | Identity only | Good adapter; no feature quality contribution | 8.0 | 0.0 | A — PyPI | 2011 | 2026-04-09 v1.3.1 | Yes | No | MIT plus service terms | NOT NEEDED | None material |
| AcoustID service | Maps fingerprints to recording IDs | Remote identity lookup is outside local calculation | Strong identity lookup; not a measurement source | 8.5 | 0.0 | A — live official status and docs | 2010 | 2026-08-11 operational evidence | Yes | No | Non-commercial free tier | NOT NEEDED | Commercial terms vary |
| MusicBrainz API | Open editorial recording/release identifiers | No calculated-feature purpose | High-quality catalog evidence, not acoustic truth | 9.0 | 0.0 | A — official server update/API | 2006 | 2026-08-04 server release | Yes | No | CC0 core data plus API policy | NOT NEEDED | Earlier RDF lineage not counted |
| MusicBrainz Picard | Human-reviewed tagging with fingerprint support | Collection tagging is outside strict scope | Excellent guided tagger; not headless feature analysis | 8.5 | 0.0 | A — official changelog | 2005 or earlier | 2026-08-11 v3.0.0b9 | Yes | No | GPL-2.0+ | NOT NEEDED | Exact initial public year unknown |
| beets | Extensible CLI music-library manager | Adds unrelated import/tagging scope | Mature orchestration, not feature ground truth | 8.0 | 0.5 | A — official releases | 2010 | 2026-07-29 v2.13.1 | Yes | No | MIT | NOT NEEDED | None material |
| Discogs API / dumps | Rich release, pressing, label, and style catalog | Editorial data cannot validate calculated features | Valuable catalog depth; no local acoustic authority | 8.5 | 0.0 | A — official dated dumps | 2007 | 2026-08-02 August dump | Yes | No | CC0 plus restricted fields | NOT NEEDED | Field-level rights vary |
| Last.fm API | Listening behavior, popularity, and crowd tags | Behavioral/editorial data is outside objective calculation | Useful social evidence, inconsistent semantic labels | 6.0 | 0.0 | B — live official docs without changelog | 2008 modern API | Unknown | Yes | No | Non-commercial by default | NOT NEEDED | Latest API update unknown |
| One Tagger | DJ-oriented multi-source bulk tagging | Mostly imports provider claims rather than calculating precise features | Useful tagging UX, stale production release | 7.0 | 0.5 | B — active repo but lagging releases | 2021 | 2026-06-25 repository | Yes | No | GPL-3.0 | NOT NEEDED | Latest stable remains 2023 |
| SongKong | Automated matching, metadata repair, and reports | Collection management, not signal analysis | Mature commercial metadata product | 8.0 | 0.0 | A — official current download | 2011 | 2026-08-17 v12.8 | Yes | No | Commercial | NOT NEEDED | None material |
| Spotify Audio Features | Once offered ready-made BPM/key/energy estimates | Remote, proprietary, inaccessible, and not reproducible from local files | Historical estimates with no current independent contract | 4.0 | 0.0 | A — official access-removal notice | 2016 | 2024-11-27 restriction | No for new apps | Yes for this integration | Unavailable to new apps | REJECT | Grandfathered behavior can change |
| Beatport API | DJ-oriented supplied BPM, key, genre, and release data | Gated catalog claims are not local calculations | Relevant catalog, weak reproducibility and access | 7.0 | 0.0 | B — live portal, no public changelog | Unknown | 2026-08 portal verified | Yes | No | Approved partners only | REJECT | Initial year and release history unknown |
| AcousticBrainz | Historical shared Essentia descriptors | Frozen comparison corpus only; never ground truth | Heterogeneous files, extractor versions, and duplicate submissions | 5.0 | 1.0 | A — official shutdown/archive | 2014 | 2022-07-06 final status | No | Yes | Archival | BENCHMARK | Archive biases and provenance |

### Rhythm, structure, key, loudness, and deterministic DSP

| Tool | Why people care overall | Purpose for this project | Output-quality summary | Technical quality | Strict fit | Source | First release | Last verified update | Ongoing? | Abandoned? | License / access | Decision | Unknowns |
|---|---|---|---|---:|---:|---|---:|---|---|---|---|---|---|
| all-in-one-mlx | Fast Apple-native BPM, beats, downbeats, and sections in one pass | Candidate generator and parity/throughput benchmark only | Inherits strong but dataset-specific upstream scores; MLX port lacks independent accuracy validation | 8.2 | 4.0 | B — official package; author parity/performance | 2026 | 2026-08-12 v1.0.6 | Yes | No | MIT; audit model/dependencies | BENCHMARK | Independent MLX parity and DJ-genre accuracy |
| Upstream All-In-One | Influential multitask reference model and weights | Reference architecture/weights only | Harmonix beat F1 .958, downbeat .915, boundary HR.5F .660; one dataset is not near-perfect generality | 7.5 | 1.0 | A — official code plus peer-reviewed paper | 2023 | 2023-10-10 | No | Yes | MIT | NOT NEEDED | No release channel |
| all-in-one-infer | Modern portable PyTorch packaging of All-In-One | Comparator to MLX, not independent accuracy evidence | Maintainer reports discrete parity on three songs; not an annotation benchmark | 7.5 | 3.0 | B — official fork and author parity tests | 2025 lineage | 2026-07-21 | Yes | No | MIT; audit dependencies | BENCHMARK | Broad parity and MPS performance |
| Beat This! | Modern public beat/downbeat tracker without mandatory DBN | Independent rhythm challenger and disagreement detector | Held-out GTZAN 89.1 beat and 78.3 downbeat F1; large cross-dataset variation | 8.7 | 5.0 | A — reproducible official code/checkpoints/paper | 2024 | 2026-05-28 code; v1.1.0 | Yes | No | MIT | BENCHMARK | Local MPS/CPU speed and genre coverage |
| Essentia core | Broad optimized MIR and deterministic DSP library | Keep only explicitly approved deterministic descriptors; never treat model estimates as facts | No package-wide accuracy; algorithm-specific validation required | 9.0 | 8.0 | A — institutional docs, code, papers | 2006 | 2026-08-27 code | Yes | No | AGPL-3.0 or commercial | KEEP | Exact algorithm/license set |
| librosa | Transparent Python reference for spectral and temporal DSP | Canonical deterministic feature reference and test oracle | Numerical transforms reproducible; conventional beat tracker is far from perfect | 9.0 | 9.0 | A — official project, paper, stable API | 2012 | 2026-08-22 code; v1.0.0 | Yes | No | ISC | KEEP | Feature-specific tolerances |
| FFmpeg EBU R128 | Production-grade standardized loudness extraction | Authoritative loudness/peak extractor with cross-check | Standards-derived; rare stress signals can differ across implementations by more than 0.5 dB | 9.5 | 10.0 | A — official source/filter docs and standard | 2012 | 2026-08-12 FFmpeg v9.0.1 | Yes | No | LGPL/GPL by build | KEEP | Build configuration and conformance suite |
| pyloudnorm | Inspectable Python BS.1770 implementation | Independent validator for FFmpeg integrated loudness/LRA | Passed cited ITU material within ±0.1 LUFS; not a true-peak replacement | 9.2 | 9.0 | A — official code, AES study, compliance material | 2017 | 2026-01-04 v0.2.0 | Yes | No | MIT | KEEP | Full project-specific conformance set |
| LibKeyFinder | Established global-key detector used in DJ software | Historical key benchmark only | Self-published 1,000-track test had 701 exact matches; not near-perfect | 6.0 | 0.5 | B — official lineage, old/self-curated benchmark | 2011 | 2024-07-09 | No | Yes | GPL-3.0+ | REJECT | Independent current evaluation |
| madmom-infer | Modern compatibility layer for old madmom inference | Parity oracle for transitive research paths only | Numerical parity evidence is not musical accuracy evidence | 5.5 | 1.0 | B — maintainer parity tests | 2026 | 2026-07-17 | Yes | No | BSD code; CC-NC-SA weights | RESEARCH ONLY | Independent tests and commercial path |
| Original madmom | Seminal neural MIR toolkit with MIREX history | Historical provenance only | Old task wins do not establish current universal accuracy | 6.0 | 0.0 | A — official code and research history | 2015 | 2024-08-25 unreleased code | No | Yes | BSD code; CC-NC-SA weights | REJECT | Modern release/support |
| BeatNet / BeatNet+ | Causal beat/downbeat/tempo/meter tracking | Specialist real-time benchmark only | GTZAN at 70 ms: BeatNet+ 80.62 beat and 56.51 downbeat F1 | 7.0 | 2.0 | B — research strong; distribution/license gaps | 2021 / 2024 | 2026-04-13 | Yes | No | CC-BY software; Plus unclear | RESEARCH ONLY | BeatNet+ license and Mac path |
| aubio | Lightweight causal C DSP for onsets/pitch/beats | Embedded latency baseline only | Independent beat F1 around 49–57 in cited studies | 6.0 | 1.0 | A — official long-running implementation and studies | 2003 | 2026-04-10 code; release 2019 | Yes | No | GPL-3.0+ | NOT NEEDED | Current wheel/release cadence |
| MSAF | Framework for comparing structure algorithms and metrics | Evaluation harness if section research resumes | Rankings vary materially by dataset, metric, and tolerance | 6.5 | 2.0 | A — official research framework/paper | 2014 | 2026-03-04 docs | Yes limited | No | MIT; optional GPL algorithms | RESEARCH ONLY | Modern dependency stability |
| Vamp / QM / Sonic Annotator | Stable plugin protocol and reproducible legacy batch extraction | Reproduce old baselines only | Relevant QM analyzers trail modern systems and are stale | 5.0 | 1.0 | B — strong provenance, weak current relevance | 2005–2009 | 2025-05-28 host; QM 2021 | No for QM analyzers | Yes | Mixed BSD/GPL/commercial | NOT NEEDED | Apple architecture/plugin compatibility |
| BTrack | Lightweight causal C++ beat tracker | Latency/embedded baseline only | Independent older evaluation: beat F1 59.5 | 5.5 | 1.0 | A — official implementation and independent paper | 2009 paper | 2026-02-26 code | Yes | No | GPL-3.0 | NOT NEEDED | Modern broad benchmark |
| KeyMyna | Promising 2026 self-supervised key research | Watch-list comparison only; cannot ship or trust as ground truth | Author reports GiantSteps exact 72.02 and Billboard 79.87; preprint and dataset-specific | 6.0 potential | 0.5 | C — preprint, tiny code drop, no license | 2025 repo | 2025-02-25 code | No | Yes | No license; default copyright | RESEARCH ONLY | License, weights, reproducibility, maintenance |

### Semantic tagging, embeddings, and source separation

| Tool | Why people care overall | Purpose for this project | Output-quality summary | Technical quality | Strict fit | Source | First release | Last verified update | Ongoing? | Abandoned? | License / access | Decision | Unknowns |
|---|---|---|---|---:|---:|---|---:|---|---|---|---|---|---|
| Essentia Discogs-EffNet | Compact music-specific style embeddings and classifier heads | No authoritative role; optional future browsing experiment only | Example style baseline 87.7 ROC-AUC but 19.9 PR-AUC; ranking is not exact genre truth | 8.5 | 0.0 | A — official models, paper, licenses | 2022 | 2025-09-15 family repo | Yes | No | AGPL/proprietary code; NC weights | RESEARCH ONLY | Exact artifact license wording conflicts |
| LAION-CLAP music | Popular shared audio/text embedding for prompt search | No strict calculated-feature role | Music checkpoint GTZAN 71% author result; prompt/domain sensitive | 8.0 | 0.0 | A — official code, paper, model card | 2022 | 2025-05-15 repo | Yes | No | CC0 code; checkpoint-specific terms | RESEARCH ONLY | Training-data provenance and MPS parity |
| Microsoft CLAP | Independent CLAP implementation across many tasks | Semantic search only, not objective metadata | ESC-50 93.9 author example is environmental sound, not music-feature accuracy | 7.5 | 0.0 | A — official Microsoft code, paper, PyPI | 2022 | 2025-05-23 v1.3.4 | Yes | No | MIT code; weight metadata differs | RESEARCH ONLY | Exact model license |
| MAEST | Strong transformer music embeddings and style logits | No authoritative role | Strong average tagging metrics, still probabilistic and dataset-dependent | 8.0 | 0.0 | A — official peer-reviewed paper/code/card | 2023 | 2025-06-27 repo | Yes | No | AGPL code; NC weights | RESEARCH ONLY | Mac acceleration |
| MusiCNN via Essentia | Tiny, easy music-specific 50-tag model | None under strict scope | ROC-AUC .88–.91 and PR-AUC .29–.38; official docs call short predictions noisy | 6.5 | 0.0 | A — official release/docs/results | 2020 | 2020-07-08 model | No | Yes | AGPL/proprietary; NC weights | NOT NEEDED | None material |
| MuQ-MuLan | Large bilingual music-text model with strong tag ranking | No objective-feature role | MTT ROC-AUC 79.3 and PR-AUC 29.3; author benchmark, not certainty | 8.0 | 0.0 | A — official paper/code/card | 2025 | 2025-08-21 card | Yes | No | MIT code; CC-BY-NC weights | RESEARCH ONLY | Apple memory/performance |
| CLaMP 3 | Multilingual cross-modal music retrieval | No need in audio-only objective analyzer | Audio retrieval MRR .1985 and .1177 on cited sets | 7.0 | 0.0 | A — peer-reviewed paper and official artifacts | 2025 | 2025-05-11 | Yes | No | MIT | RESEARCH ONLY | Data-leakage/provenance concerns |
| MERT | General self-supervised music representation | Research backbone only; no direct validated fields | Strong downstream averages; authors note weaker key/global tasks | 7.5 | 0.0 | A — official implementation/card/reviewed paper | 2022 | 2025-05-25 | Yes | No | Apache code; CC-BY-NC weights | RESEARCH ONLY | Downstream heads and MPS cost |
| FIGMA | Fine-grained music-text retrieval using richer descriptions | Experimental retrieval only, never extraction | In-domain text-to-audio R@1 26.15%; most top-1 matches still wrong | 8.0 research | 0.0 | A — official 2026 paper/code/card | 2026 | 2026-07-04 code | Yes | No | MIT code; CC-BY-NC checkpoint | RESEARCH ONLY | Generalization and synthetic-caption effects |
| MuQ | Recent self-supervised music encoder | No direct objective output | Strong aggregate benchmarks; public checkpoint may not reproduce paper | 7.5 | 0.0 | A — official paper/repo discloses limitation | 2025 | 2025-08-15 | Yes | No | MIT code; CC-BY-NC weights | RESEARCH ONLY | Reproducible public-model quality |
| MusicFM | Long-context music representation | Historical research comparison only | Useful representation; authors note low inherent key performance | 6.5 | 0.0 | A — official repo/paper/weights | 2023 | 2024-02-14 | No | Yes | MIT/Apache code; unclear weight terms | RESEARCH ONLY | Explicit weight license |
| M2D-CLAP | Strong hybrid general audio-language representation | No purpose and restrictive terms | AudioCaps R@1 up to 37.24; overlap caveats | 6.5 | 0.0 | A — official repository, paper, license | 2024 | 2026-02-23 | Yes | No | Custom internal-evaluation terms | REJECT | Redistribution and commercial path |
| PANNs | Widely used AudioSet event baseline | Coarse events are not authoritative DJ features | AudioSet mAP .439; weak labels and non-music ontology | 6.5 | 0.0 | A — official paper/repo/archived weights | 2019 | 2024-07-25 | No | Yes | MIT | NOT NEEDED | Current maintenance |
| OpenL3 | Historically important audiovisual embeddings | Superseded and non-objective | Downstream-task dependent; no universal model accuracy scalar | 5.5 | 0.0 | A — official package/docs/publication | 2019 | 2023-05-03 | No | Yes | MIT code; CC-BY weights | REJECT | Modern dependency support |
| YAMNet | Small portable 521-class event detector | Optional warning events do not meet current goal | AudioSet balanced mAP .306; broad weak-label ontology | 6.5 | 0.0 | A — official Google release and metrics | 2019 | 2025-02-18 | Yes | No | Apache-2.0 | NOT NEEDED | Keras 3 compatibility |
| Standalone musicnn | Influential simple music tagger | Obsolete duplicate of better-packaged graphs | MTT PR-AUC 38.44; split/software sensitive | 5.0 | 0.0 | A — official author repo/paper/PyPI | 2019 | 2023-12-11 repo; PyPI 2019 | No | Yes | ISC; model terms unclear | REJECT | Separate model license |
| VGGish | Historical 128-D AudioSet/YouTube embedding | Compatibility only; no current objective purpose | No standalone accuracy; old downstream benchmark only | 4.5 | 0.0 | A — official Google code and license clarification | 2017 | 2024-03-01 typo update | No | Yes | Apache code; CC-BY artifacts | REJECT | Modern supported runtime |
| Demucs | High-quality four/six-source separation | Benchmark only if stems prove a downstream need | HTDemucs 9.0–9.2 dB SDR; audible bleed/artifacts remain | 8.5 | 2.0 | A — official maintainer and paper; weight caveat | 2019 | 2026-07-11 v4.1.0 | Yes maintenance | No | MIT code; weight rights unresolved | BENCHMARK | Definitive checkpoint terms and MPS support |
| audio-separator | Active unified runner for many separator families | Best way to compare models, but no wrapper-level quality guarantee | Quality belongs to checkpoint; modern models can exceed 14 dB SDR on specific leaderboards | 8.0 | 3.0 | A — official package and platform docs | 2023 | 2026-08-27 v0.47.0 | Yes | No | MIT wrapper; model-specific | BENCHMARK | Per-checkpoint license, data, and Mac quality |

### Proprietary DJ and desktop products

| Tool | Why people care overall | Purpose for this project | Output-quality summary | Technical quality | Strict fit | Source | First release | Last verified update | Ongoing? | Abandoned? | API / license | Decision | Unknowns |
|---|---|---|---|---:|---:|---|---:|---|---|---|---|---|---|
| Lexicon DJ | Central library conversion across major DJ suites | Interoperability and black-box grid/cue comparison | Vendor-only first-beat claims; vendor acknowledges cue, energy, and dynamic-analysis limits | 8.5 | 3.0 | A lifecycle/API; C accuracy | 2022 | 2026-08-28 v1.11.13 | Yes | No | Commercial; GUI-backed localhost API | BENCHMARK | Independent analyzer dataset |
| Mixed In Key 11 | Long-standing specialist for harmonic mixing and cue prep | Closed key/cue benchmark only | Historical community key test 76.5%; current superiority claim is vendor-only | 8.0 | 3.0 | B — good product history, weak current validation | 2006 family | 2025-09-15 Win; 2025-09-11 Mac | Yes | No | Commercial; no public API/CLI | BENCHMARK | Exact v11 launch day and current independent accuracy |
| rekordbox 7 | Dominant AlphaTheta/CDJ preparation ecosystem | Export compatibility and black-box phrase/grid comparison | Historical key accuracy 69.2%; no public current BPM/phrase validation | 8.0 | 3.0 | A lifecycle/features; historical accuracy | 2009 family | 2026-08-18 v7.2.18 | Yes | No | Commercial; XML import only | BENCHMARK | Stable analyzer schema/API absent |
| Traktor Pro 4 | Mature performance engine with flexible tempo grids | Variable-tempo grid comparison | Historical key accuracy 73.8%; vendor instructs manual beatgrid correction | 8.0 | 3.0 | A — official lifecycle/manual | 2000 family | 2026-07-09 v4.5.1 | Yes | No | Commercial; no analysis API | BENCHMARK | Current-version accuracy |
| Serato DJ Pro | Widely adopted live workflow and hardware integration | Compatibility benchmark; preserve proprietary metadata if files are touched | Historical key accuracy 60.6%; settings expose octave-error/manual-grid needs | 8.0 | 3.0 | B — official features, unclear exact current release date | 2004 lineage | 2026-07-08 v4.0.9 observed | Yes | No | Commercial; no analysis API | BENCHMARK | Exact release date and current validation |
| beaTunes | Broad local analysis and extensible playlist tooling | Feature-taxonomy and plugin-architecture research only | Current algorithms lack rigorous public validation; historical BPM evidence weak | 7.0 | 1.0 | B — strong lifecycle/API, C accuracy | 2006 | 2026-08-22 v6 EA6 | Yes | No | Commercial; Java/Jython scripting | RESEARCH ONLY | Stable v6 behavior and current benchmarks |
| Jaikoz | Detailed interactive metadata repair | No BPM/key/grid/loudness calculation role | Metadata product with unquantified vendor accuracy | 7.0 | 0.0 | A — official product/releases/history | 2005 | 2026-04-14 v12.6 | Yes | No | Commercial; no API/headless | NOT NEEDED | None material |
| Platinum Notes | One-click loudness and audio modification | Wrong category; alters source audio and invalidates reproducibility | No controlled quality evidence; vendor activity counts are not accuracy | 4.0 | 0.0 | C — sparse update provenance and validation | circa 2007 | 2024-06-13 corroborated build | Yes commercially | No | Commercial; no API/CLI | REJECT | Exact first year, maintenance state, objective validation |

## Source-quality interpretation

The sources are good enough to make lifecycle and scope decisions:

- Official package registries provide exact release dates.
- Official repositories establish code activity, licenses, and supported
  interfaces.
- Standards and implementation papers establish what loudness measurements
  mean.
- Peer-reviewed MIR papers establish dataset-level average metrics.
- Product manuals establish available features and lack of APIs.

They are **not** good enough to claim near-perfect general MIR:

- Most MIR numbers are author-reported.
- Datasets often contain Western popular music and underrepresent the target
  collection's edge cases.
- Different beat/key/structure metrics reward different errors.
- Closed-tool comparisons usually test old versions and small private samples.
- ROC-AUC, PR-AUC, mAP, SDR, MRR, and retrieval R@1 are not interchangeable.
- Model cards describe artifacts, not independent replication.
- A high mean can hide catastrophic errors on individual tracks.

The highest-quality sources frequently support rejection. Beat This's own paper
shows downbeat F1 ranging from near-perfect on Candombe to 66.3 on RWC Classical.
FIGMA's large relative retrieval gain still yields only 26.15% top-1 on one
fine-grained benchmark. These are useful research systems, not truth engines.

## Revised production architecture

### Authoritative lane

1. **Pinned FFmpeg build**
   - Decode every MP3 to canonical PCM.
   - Record input/output sample count, decoder version, delay/padding behavior,
     warnings, and exact command.
   - Extract encoded stream facts with ffprobe JSON.
2. **FFmpeg EBU R128**
   - Integrated, momentary, and short-term loudness.
   - Loudness range.
   - Sample peak and true peak where configured.
3. **pyloudnorm validator**
   - Independently calculate integrated loudness and LRA.
   - Quarantine disagreement outside tolerance.
4. **librosa deterministic DSP**
   - Only whitelisted transforms with explicit parameters, units, and test
     vectors.
   - Do not translate them into “energy,” “mood,” or “danceability.”
5. **Selected Essentia deterministic algorithms**
   - Only when they add a measurement not adequately covered above.
   - Audit each algorithm and dependency separately.
   - Resolve AGPL/commercial licensing before product distribution.

### Benchmark lane

- All-In-One MLX.
- all-in-one-infer.
- Beat This.
- MediaInfo.
- Optional Demucs and `audio-separator`.
- Lexicon, Mixed In Key, rekordbox, Traktor, and Serato.

Outputs stay in a separate namespace such as `benchmark_estimates`. They
cannot overwrite authoritative measurements or user corrections.

### Disposed lane

- Chromaprint, pyacoustid, AcoustID, MusicBrainz, Discogs, Last.fm, One Tagger,
  SongKong, Picard, beets, and other identity/enrichment tools.
- Every semantic embedding/tagging model.
- Legacy beat/key/structure analyzers below the modern benchmark bar.
- Spotify and Beatport integrations.
- Destructive audio “improvement” tools.

## Canonical field policy

Each stored output must include:

```json
{
  "field": "loudness_integrated",
  "value": -10.8,
  "unit": "LUFS",
  "truth_class": "standardized_measurement",
  "authority": "accepted",
  "source_tool": "ffmpeg",
  "tool_version": "9.0.1",
  "decoder": "ffmpeg 9.0.1",
  "parameters": {},
  "tolerance": 0.1,
  "validator": "pyloudnorm 0.2.0",
  "validator_value": -10.8,
  "status": "passed",
  "analyzed_at": "ISO-8601"
}
```

Benchmark/model results use:

```json
{
  "field": "tempo_candidate",
  "value": 128.0,
  "unit": "BPM",
  "truth_class": "model_estimate",
  "authority": "benchmark_estimate",
  "source_tool": "all-in-one-mlx",
  "tool_version": "1.0.6",
  "confidence": null,
  "status": "not_validated"
}
```

Never coerce `null`, rejected, or unvalidated output into a value.

## Feature-by-feature decision

### Accept now

- Codec/container/stream facts from ffprobe.
- Decode health and duration under a pinned decoder.
- Sample rate, channel count, and sample count.
- Integrated loudness and LRA after dual-implementation agreement.
- Sample peak and configured true peak.
- Whitelisted deterministic spectral/temporal transforms with tests.

### Benchmark but do not accept yet

- BPM.
- Beat/downbeat timestamps.
- Beat numbers and meter.
- Tempo curves and flexible beatgrids.
- Structural boundaries and labels.
- Key, chords, and pitch classes.
- Stem waveforms.

### Do not make authoritative

- Genre and style.
- Mood and context.
- Energy and valence.
- Danceability.
- Instrument or vocal presence.
- Similarity.
- Natural-language embeddings.
- Automatic transition quality.
- Catalog-supplied BPM/key.

These may return in an explicitly subjective recommendation layer only if the
user later relaxes the nearly-perfect requirement.

## Validation methodology

### Corpus

The workspace file index does not reliably expose the binary MP3 files, but a
direct directory inspection on 2026-08-31 confirmed 10 MP3s in
`test_folder_10_house_tracks`. That folder is the authorized V1 corpus.
`test_tracks_folder_mp3` remains the later, roughly 120-track corpus and must
not be substituted silently.

The 10-track house corpus is intentionally narrow. It can validate V1
compatibility and the basic mixing pipeline, but it cannot justify universal
accuracy claims. Later broad validation should select:

- Straight four-on-the-floor.
- Breakbeat and drum-and-bass.
- Half-time material.
- Beatless intros and breakdowns.
- Ambient or sparse percussion.
- Live drums, disco, rubato, and tempo drift.
- Weak tonality, mode ambiguity, and modulation.
- Instrumental, sparse-vocal, and vocal-dense tracks.
- Extended club mixes and radio edits.
- Deliberately damaged or unusual MP3 encodes.

### Ground truth and tests

1. Create immutable file and PCM hashes.
2. Verify decode/sample counts across reruns.
3. Run official loudness conformance material.
4. Cross-check FFmpeg and pyloudnorm.
5. Create manually verified beat/downbeat annotations for the representative
   set if BPM/beat fields are still desired.
6. Sonify predictions; inspect start, middle, and end.
7. Count half/double-tempo, downbeat-phase, and cumulative-drift failures.
8. Require zero silent catastrophic failures.
9. Keep model predictions quarantined until the strict gate passes.
10. Version every accepted field and rerun the validation suite before upgrades.

## Safe-write policy

The analysis phase remains read-only. If calculated values are eventually
written to MP3 tags:

1. Reintroduce Mutagen only as optional infrastructure.
2. Preserve all unknown ID3 frames, including DJ-private `GEOB`, `PRIV`, and
   `TXXX` payloads.
3. Produce a complete dry-run diff.
4. Write a same-filesystem temporary copy.
5. Re-open and compare raw frames.
6. Confirm the encoded audio payload and decoded PCM did not change.
7. Atomically replace only after validation and keep a recoverable backup.

No benchmark, semantic, catalog, or rejected value may be written as though it
were authoritative.

## Implementation recommendation

### Stage 1 — authoritative harness

- Make the 120 files visible to the workspace.
- Inventory with ffprobe JSON.
- Pin FFmpeg 9.0.1 or the chosen reviewed build.
- Decode a representative 20-track subset to canonical PCM.
- Implement FFmpeg EBU R128 plus pyloudnorm agreement checks.
- Implement deterministic librosa feature fixtures.
- Record provenance and unknown values.

### Stage 2 — challenge the excluded features

Only if BPM/beats remain required:

- Run All-In-One MLX 1.0.6 and Beat This 1.1.0.
- Build manual reference annotations.
- Calculate event metrics and catastrophic-error counts.
- Do not lower the threshold merely because the models are useful.

Only if stems remain required:

- Choose exact checkpoints in `audio-separator` and Demucs.
- Audit each weight license.
- Create a listening and SDR-style local benchmark.
- Keep stems outside the authoritative lane unless the strict bar is met.

### Stage 3 — optional subjective layer

Do not implement while the current requirement stands. If the user later wants
prompt search or mood/genre recommendations, restore semantic models in a
separate subjective namespace with visible uncertainty and no claim of fact.

## Primary source index

- [FFmpeg releases](https://ffmpeg.org/download.html)
- [FFmpeg filter documentation](https://ffmpeg.org/ffmpeg-filters.html)
- [Mutagen changelog](https://mutagen.readthedocs.io/en/latest/changelog.html)
- [MediaInfo changelog](https://mediaarea.net/MediaInfo/ChangeLog)
- [Chromaprint](https://acoustid.org/chromaprint)
- [All-In-One MLX](https://pypi.org/project/all-in-one-mlx/)
- [All-In-One paper](https://doi.org/10.1109/WASPAA58266.2023.10248148)
- [Beat This paper](https://arxiv.org/abs/2407.21658)
- [Essentia documentation](https://essentia.upf.edu/documentation.html)
- [Essentia licensing](https://essentia.upf.edu/licensing_information.html)
- [librosa](https://librosa.org/)
- [pyloudnorm](https://github.com/csteinmetz1/pyloudnorm)
- [KeyMyna](https://arxiv.org/abs/2604.10021)
- [Essentia model zoo](https://essentia.upf.edu/models.html)
- [LAION-CLAP](https://github.com/LAION-AI/CLAP)
- [MAEST paper](https://archives.ismir.net/ismir2023/paper/000098.pdf)
- [MuQ](https://github.com/tencent-ailab/MuQ)
- [MERT](https://github.com/yizhilll/MERT)
- [FIGMA paper](https://aclanthology.org/2026.acl-long.2197.pdf)
- [Demucs](https://github.com/adefossez/demucs)
- [audio-separator](https://pypi.org/project/audio-separator/)
- [Spotify API restriction](https://developer.spotify.com/blog/2024-11-27-changes-to-the-web-api)
- [Lexicon API](https://www.lexicondj.com/docs/developers/api)
- [rekordbox releases](https://rekordbox.com/en/support/releasenote/)
- [Traktor update ledger](https://community.native-instruments.com/discussion/43/official-update-status-traktor-pro-4-current-version-4-5-1)
- [Serato analysis documentation](https://support.serato.com/hc/en-us/articles/14361068095759-Analyzing-Files)

## Maintenance rule

Before adding or upgrading any tool:

1. Re-check release and code activity.
2. Re-check code, model-weight, dataset, and service licenses separately.
3. Re-run conformance and corpus validation.
4. Recalculate technical-quality and strict-fit scores.
5. Preserve old model/tool results under their original version.
6. Record `Unknown` rather than inventing missing lifecycle or accuracy data.

The registry should change when evidence changes—not because a feature would be
convenient to have.
