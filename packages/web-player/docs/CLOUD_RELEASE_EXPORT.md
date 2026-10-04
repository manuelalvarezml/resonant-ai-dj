# Portable cloud-library release

Implemented and locally exercised on 2026-10-02. No cloud calls, uploads,
audio inference or conversion occur in this exporter.

## Inputs and behavior

[`export-release.mjs`](../scripts/export-release.mjs) freezes the saved
`output/web-release/catalog.json` selection and its private `sources.json`
mapping. It does not regenerate the preview, scan another music folder, or
change the owner's original files. Every selected row must have an exact
SHA-256 identity, current `selected-estimators-v3-character120` features,
`maest-top6-v1` policy, complete status, all eleven required stages
passed/warning, and MP3 metadata/source extension.

The exporter hashes each source, copies it without overwriting, verifies the
copy, then hashes the original again. Raw feature JSON is copied byte for byte
into the private directory, retaining the original audio embeddings. The
public catalog removes embeddings, process metrics, implementations, opaque
encoded tags, private paths and secret-like strings. Static assets must match
the existing web build's checksum manifest.

The single existing completed mix is copied and verified against its recorded
SHA-256. Both transition starts and durations come from the saved filter graph;
the exporter does not render a mix. Current intervals are **203.65–232.74** and
**407.29–436.38 seconds**.

## Portable layout and contract

```text
release.json                     # resonant/cloud-release/1; source-path-free
public/                          # verified web build plus catalog.json/mix.json
media/<audio-sha256>.mp3           # API-only music, outside public static files
media/mix.m4a                     # API-only completed mix
private/features/<sha256>.json    # exact original cached feature evidence
private/mix/                     # original manifest and transition graph
private/exclusions.json          # omitted hashes and reasons; no source paths
private/planner.json             # added by the separate frozen-planner export
```

The manifest uses `schema`, `releaseId`, `trackCount`, `audioBytes`,
`catalogPath`, `mixPath`, `mixAudioPath`, `featureDirectory`, `plannerPath`, and
`files` entries containing `path`, `sha256`, `bytes`, and `visibility`.
`releaseId` is SHA-256 of `JSON.stringify(manifestWithoutReleaseId)`.
Re-finalizing unchanged contents produces the same ID. Paths use relative
POSIX syntax; symlinks, path traversal and unlisted files are rejected.

From `packages/web-player`:

```sh
node scripts/export-release.mjs
node scripts/export-release.mjs --verify ../../output/cloud-releases/first-release
```

The default destination is Git-ignored `output/cloud-releases/first-release`.
An existing release with the same saved selection is verified and reused;
it is never silently replaced. For a new selection or refreshed assets, pass
`--output` with a new directory beneath `output/cloud-releases`.

After the Python planner exporter adds `private/planner.json`:

```sh
node scripts/export-release.mjs --finalize ../../output/cloud-releases/first-release
node scripts/export-release.mjs --verify-ready ../../output/cloud-releases/first-release
```

`--verify-ready` requires the frozen planner file and verifies every bundle
checksum. Model installation, planner code/provenance validation, Linux
inference, and remote acceptance belong to the deployment workflow.

## Measured local export

The real export copied and verified **187 MP3s / 1,910,985,140 audio bytes**.
The pre-planner bundle contains 413 files totaling 2,007,063,342 bytes.
Of 316 hash-named feature caches, 129 are excluded: 69 incomplete, 54 older
feature-version records, three non-MP3 records, and three eligible records
absent from the frozen published-source selection. This last group is not a
claim that no audio exists elsewhere; no broader source discovery ran.

After the frozen planner and its 60-case parity fixture were added, final
`--verify-ready` passed with **415 files / 2,075,449,410 inventoried bytes**.
The final release ID is
`4a4bb92196ed75cc95ac19ec6a25bd5062ed31cdabb0eb30ebca0f83d5b5ff57`;
the `release.json` file SHA-256 is
`56cd5c8558e80ca4564c7cf07e32f8d60349738b72baa7cbcc6802b79df4f4c3`.

Six focused tests cover exact byte/vector preservation, public sanitization,
exclusion accounting, graph-derived transition intervals, repeated export and
finalization, changed-source rejection, incomplete/mismatched cache rejection,
tampered/unlisted files, symlinks, traversal, and corrupt static assets.
Run `node --test tests/export-release.test.mjs` from the player package.

The accompanying `cloud-release-validation.test.mjs` adds four production-loader
tests for valid exporter input, internally consistent but mismatched audio,
incomplete features, wrong catalog revision/locations and symlinks.
`cloud-process.test.mjs` adds three real process-group tests: cancellation,
orphan cleanup, and a timed-out worker that ignores TERM while the next request
remains blocked. All thirteen focused tests passed individually; they make no
network or inference calls.

The [first-release deployment package](../../../docs/cloud-library/first-release/README.md)
owns current readiness, final release digest, provider decisions and remaining
launch checks. This document records the exporter and its bounded local proof.
