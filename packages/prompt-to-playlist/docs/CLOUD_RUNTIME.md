# First-release cloud planner preparation — 2026-10-02

The first release now has a separate planner runtime for the immutable shared
library. It preserves the existing local planner, estimator selections, weights,
and result schema. Nothing in this preparation deployed resources, called a paid
provider, decoded owner audio, or ran a model.

## Prepared artifacts

Project-relative paths:

- `output/cloud-releases/first-release/private/planner.json`: 187 published MP3
  identities, source-feature fingerprints, recorded model/sampling identities,
  pure planner feature projections, and full catalog/vocabulary snapshots for
  `reference`, `music2emo`, `musicnn-dance`, `supervised`, and `quality`.
- `output/cloud-releases/first-release/private/planner-parity.json`: 60 fixed
  profile/scope/query checks, including real cached character-bank text vectors.
- `output/cloud-models/first-release`: six verified pinned semantic-model assets
  (2,663,055,739 bytes) plus the original manifest. All copied hashes and the
  source's hashes match. No download occurred.
- `output/cloud-preparation/planner-verification.json`, `planner-evidence.json`,
  and `model-copy.json`: machine-readable verification and artifact hashes.

These artifacts remain outside Git and the public static tree. The release
exporter inventories the private files too; the server does not expose them.

| Artifact identity | SHA-256 |
| --- | --- |
| Final release ID | `4a4bb92196ed75cc95ac19ec6a25bd5062ed31cdabb0eb30ebca0f83d5b5ff57` |
| Planner payload | `83661eaf9612df8895272d364752964fc1447e8c3bb2f2ec10f09df504460852` |
| Planner file, 67,479,998 bytes | `c1e37b04f3c5d85a34fe3241ba4fc9a5a217c237b58c84b1ba3029b990d11f32` |
| Parity file, 906,070 bytes | `4480c79fee0f6c35cba0750768ed68ebd2eddfda54978b5455af112c8849c2a0` |
| Model manifest | `290d4489a8cf56321485950f838125b4d374c9dff50d78c106a8185850360070` |

## Runtime contract

The production Node worker invokes:

```sh
python -m prompt_to_playlist.cloud_bridge prompt \
  --release-dir /release --state-dir /state --model-dir /models \
  --input /state/jobs/request.json --out /state/jobs/response.json
```

The input retains the existing `prompt`, `tracks`, `clarifications`, and
`estimator_profile` fields. Each selected track must identify an exact published
`id` and `sha256`. Unknown, duplicate, or changed identities fail. Titles and
feature values sent by a browser cannot override published evidence. Success is
`{"result": <existing PlaylistRun>}`; client errors are generic and never include
provider/configuration contents, local paths, or secrets.

Release, state, model, and Python paths come from the production server's
`RESONANT_RELEASE_ROOT`, `RESONANT_STATE_ROOT`, `RESONANT_MODEL_ROOT`, and
`RESONANT_PYTHON` configuration. The Python CLI itself uses explicit arguments.
The frozen OpenAI settings retain `gpt-5.4-mini-2026-03-17`, low reasoning,
30-second provider timeout, and `AUTODJ_OPENAI_API_DEV_KEY`. Export removes the
local `key_source_file`; cloud serving reads only the configured environment
variable. Export and verification do not read a credential.

## Preserving profile and scope behavior

The specialist identity contains installed analyzer package versions. Comparing
it to the serving host would discard valid local evidence on a slim Linux
installation. Export now validates all eleven required stages on the source
machine, then records the accepted specialist identities in the immutable
snapshot. Serving uses those published identities explicitly. Existing local
calls still use their installed-runtime identity checks.

Whole-library requests load their frozen catalog/vocabulary pair. Subsets and
reordered scopes use the same catalog builder with the immutable projected
features and published identities. This matters because genre vocabulary aliases,
Music2Emo valence/arousal range gates, and uniform coverage decisions can change
with scope. Slicing a whole-library quality catalog would change existing
behavior. The export checks that its projections reproduce every full-profile
catalog and vocabulary exactly, and portable replay also verifies subset and
order behavior.

The snapshot validates its payload digest and fingerprints of the serving
source files and descriptor definitions. A source change requires a new export;
the runtime fails closed on a stale snapshot. Source raw-feature fingerprints
and model identities remain in private provenance. Local source paths, metadata
probe output, and analysis telemetry are excluded from planner projections.

## Text encoding and persistent state

Cached semantic text reads use the original normalization and encoder identity.
They do not import the ML stack. A missing vector starts the pinned offline MuQ
text path in a bounded child: 300 seconds, 6,000 MB process-tree RSS, and a
1,024 MB minimum available-memory floor. The child retains the parent process
group so the Node supervisor can reap the whole tree. Model roots and the text
cache are explicit; the cache persists at `/state/text-cache`.

The runtime imports no analyzer stack for catalog selection or structured
ranking. Uncached text still needs the pinned MuQ/Torch/Transformers semantic
dependencies and complete semantic-model bundle. It does not execute acoustic
analysis. Linux cold-text memory/performance has not yet been measured.

Every completed prompt saves the full result, exact selected catalog/vocabulary,
request identities, and snapshot digest under `/state/audits`. Retention is at
most 200 request pairs and seven days. Pruning recognizes only regular files
with the expected UUID audit names, ignores unrelated files and symlinks, and
does not follow an audit-directory symlink. Each visitor's saved playlists remain
the web edition's browser-local state.

The text cache grows as new descriptions are requested; the production server's
30-request daily cap bounds the request rate, not total lifetime cache size.
The last uncached text worker writes timing/RSS telemetry to
`/state/last-text-worker.json` without saving provider secrets.

## Verification performed

- Final Python suite: **551 passed in 5.37 seconds**. Two existing mocked
  analysis-worker tests needed a sandbox escalation to read macOS memory
  telemetry; their initial sandbox-only `psutil.swap_memory()` failures were
  environmental. No owner audio inference was used by those tests.
- **35 new cloud tests** cover integrity failures, exact published identity
  selection, profile/subset/reordered parity, out-of-range VA behavior,
  independent coverage fallback, real cached audio vectors, real cached text
  vectors and scores, audit replay/retention, and imports without the ML stack.
- Actual 187-track export reproduced all five local full-profile
  catalog/vocabulary pairs exactly.
- Actual portable verification passed **60/60** catalog, vocabulary, and full
  search-result hash checks after reading the serialized frozen artifact.
- The release exporter finalized and passed `verify-ready` after both planner
  artifacts were frozen. No subsequent release mutation was made by this task.

## Prepared deployment acceptance commands

Replay the portable cases inside the built Linux image, with no network or model
inference required:

```sh
python -m prompt_to_playlist.cloud_bridge verify \
  --release-dir /release --out /state/planner-verification.json
```

The result must report `tracks: 187` and `parity_cases_passed: 60`. The deployment
kit's Linux text acceptance driver calls `cloud_text.bounded_encode` with one
fresh text description and then the same text again, recording cold and cached
latency, peak RSS, and identical vectors. It should run with network disabled;
all model files are supplied locally. A later live planner smoke requires the
intended personal OpenAI credential and is separate from these deterministic
checks.

Linux image execution, uncached Linux text performance, a real provider request,
remote HTTPS playback, access control, and owner device acceptance remain
deployment checks. Local passing tests do not establish those results.

For release regeneration, run `cloud_bridge export --release-dir <release>
--out <release>/private/planner.json` in the authorized local analysis environment,
then rerun the release exporter's finalizer and `verify-ready`. The export also
writes `planner-parity.json`; it uses compatible existing text caches only.
