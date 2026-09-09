# Repository versioning and recovery

The private GitHub repository `manuelalvarezml/resonant-ai-dj` is the durable
history for the local DJ engine, its paused
prompt-to-playlist package, and the cloud-library discovery documents. It
exists so an accepted musical baseline, a working package, research decisions,
and failures can be recovered without reconstructing chat or rerunning costly
audio analysis.

## Why this project needs version control

The maintained handoffs and recent summaries establish four reasons:

1. The accepted v2 mix behavior is evidence-backed: 16-bar exact-grid timing
   and `house_eq_v1` were heard and accepted in D038/E026. Future DSP work must
   be comparable with that checkpoint.
2. The completed ten-track analysis was expensive and stressed the 16 GB Mac.
   Its compact JSON, source hashes, environment pins, and experiment history
   allow work to continue without repeating the heavy corpus run.
3. Decisions, failed experiments, rejected routes, and research revisions are
   part of the product record. The logs are append-only so later conclusions
   supersede earlier ones without erasing why a path changed.
4. The engine and prompt-to-playlist package evolve independently but share
   stable track IDs and future integration contracts. Keeping them in one
   repository provides coordinated history while each keeps its own package
   version, dependencies, tests, schemas, and roadmap.

## What Git tracks

Commit source code, tests, documentation, schemas, configuration templates,
dependency lockfiles, compact analysis/catalog JSON, render manifests, and
research workbooks or verification records. These are the materials needed to
understand and reproduce a checkpoint.

Do not commit source MP3s, rendered WAVs, virtual environments, caches,
temporary analyzer directories, credentials, or `.env` files. Audio remains
local because it is large, may be rights-restricted, and GitHub rejects normal
Git files over 100 MiB. The repository records audio identity with SHA-256 and
retains compact manifests instead. Git LFS may be considered later only for an
authorized, rights-cleared artifact that truly needs remote binary versioning.

The repository is private because current evidence includes collection
metadata, filenames, local path history, and product research. Private status
does not make secrets safe to commit; credentials must remain in the named
environment variable or local shell configuration described in D040.

## Version namespaces

These versions describe different things and must not be forced into one
number:

| Namespace | Current baseline | Meaning |
|---|---:|---|
| Repository checkpoint | `checkpoint-2026-09-09` | Complete recoverable Git snapshot in `resonant-ai-dj` |
| DJ engine package | `0.1.0` | Python distribution version in the root `pyproject.toml` |
| Prompt-to-playlist package | `0.2.0` | Independent distribution version in its `pyproject.toml` |
| Engine JSON schemas | `0.1.0` | Serialized contract versions documented in `docs/SCHEMAS.md` |
| Translator policy | `playlist-query-v3` | Natural-language interpretation behavior from D041/E029 |
| Cloud discovery | revision `1.0` | Research and planning record; it is not a software release |

Package and schema versions follow semantic versioning: patch for compatible
fixes, minor for backward-compatible capability, and major for incompatible
behavior or data. Research revisions use a dated revision recorded in their
changelog and append-only events. Repository checkpoints use annotated tags
named `checkpoint-YYYY-MM-DD`; add `-2`, `-3`, and so on only when more than
one accepted checkpoint is intentionally created on the same day.

## Current checkpoint

### `checkpoint-2026-09-09`

- First Git and GitHub baseline of the existing project.
- Engine Step 1, scoring, clip tools, manual MixPlan validation/rendering,
  exact-grid transition timing, `house_eq_v1`, and downbeat diagnostics are
  present.
- The user-accepted v2 listening result is represented by its plan, manifest,
  D038/E026 record, and source hashes. The 205 MiB WAV remains local.
- Prompt-to-playlist `0.2.0`, its 120-track metadata catalog, and recorded
  natural-language checks are preserved; development remains paused.
- Cloud discovery revision 1.0 and its evidence/registers are preserved; no
  cloud implementation is authorized.
- Known next engine issue remains final-bus headroom: the accepted v2 render
  measured +1.04 dBTP.

## Working practice

Use `main` as the stable, recoverable line. Make one commit per coherent slice
and use a short-lived branch when a change needs experimentation or review.
Before merging or tagging, run the tests relevant to the changed component,
confirm generated contracts still validate, review the staged file list, and
scan it for credentials and unexpected large files. Do not rewrite or
force-push shared history. Record material behavior changes in the appropriate
decision, experiment, and changelog files in the same commit.

Create an annotated checkpoint tag only after the documented validation is
complete. Push the commit and tag together. GitHub releases are optional and
should summarize an accepted milestone; they must not attach source audio or
rendered music without a separate rights and storage decision.

## Recovery

To inspect an earlier state without disturbing current work, create a new
branch from its checkpoint tag. Restore local audio separately, keep the exact
filenames, and verify it against `docs/CORPUS.md` or the saved import manifest.
The excluded accepted render can be regenerated from its tracked analysis,
plan, manifested tool versions, and unchanged source files; do not rerun the
heavy ten-track analyzer merely to restore the repository.

If a secret is ever committed, rotate it first, then remove it from the full
Git history before relying on deletion from the latest revision. If a local
audio artifact is lost, Git cannot restore it; the checksum proves identity,
not possession. Keep a separate rights-appropriate backup for irreplaceable
audio and large renders.
