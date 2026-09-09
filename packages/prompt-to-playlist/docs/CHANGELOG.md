# Changelog

## Paused — 2026-09-08

Recorded P008: V0.2 and the natural-language UI follow-up remain implemented,
but further playlist development is paused. Reviewed semantic annotations and
broader prompt evaluation stay in the backlog. Parent D042's future cloud
library phase does not authorize hosting or integration changes in this
package. No code, schema, catalog, dependency or test claim changed.

## 0.2.0 follow-up — 2026-09-07

Corrected a user-visible offline launch failure: the desktop now requires
OpenAI, selects the explicit/current-directory/editable-checkout profile and
rejects rules mode. Generic CLI prompt defaults to OpenAI; offline examples
require `--provider rules`. P007 supersedes the earlier default below.

Revised the translation policy to `playlist-query-v3` for short natural
descriptions: a direct single genre is required, mood/energy is preferred
unless mandatory, and “DJ set” alone is context rather than a render command.
The user’s “house dj set energetic” regression is recorded in P-E003: eight
house-tagged matches with unknown energy, all six live cases passing, 363 package
tests and a successful 0.2.0 wheel/source rebuild. Native Tk state/geometry
checks passed without additional API calls; screenshot QA was unavailable.

Refreshed the desktop with a light, modern Tk interface, plain-language
criteria, artist/BPM results, visible missing-preference evidence and detailed
provenance on demand. No new dependency or serialized schema was introduced.

## 0.2.0 — 2026-09-07

Added a read-only local MP3 metadata/hash importer with FFprobe/version capture,
source-preservation gates, provenance, duplicate aliases and coverage. Imported
the authorized 120-file pool; 62 tracks have exactly mapped genre labels and 22
have positive embedded BPM. Added the project-only pool vocabulary.

Added explicit TOML project configuration, safe named-key loading from environment
or a literal shell-file assignment, and `Open Playlist.command`. The configured
desktop/CLI flow now uses OpenAI and the real pool. The generic library remains
offline by default. Desktop shows available catalog evidence and a usable prompt.

The first live check exposed a count interpretation error. `playlist-query-v2`
fixes the instruction; the corrected request and all five live smoke cases pass.
Added the explicit live-check command/report. No engine runtime, audio analyzer,
source audio or `.zshrc` changes.

## 0.1.0 — 2026-09-07

Added the standalone prompt-to-playlist foundation: strict contracts, editable
vocabulary, evidence-aware deterministic tools, offline grammar, bounded OpenAI
adapter, JSON/DJ adapters, CLI, optional local desktop form, synthetic examples,
independent lockfile and tests. Documented architecture, schemas, decisions,
validation and the parallel roadmap. Parent DJ behavior and runtime unchanged.

Review fixed public-boundary handling of caller-mutated catalogs/vocabularies;
duplicate IDs and ambiguous aliases are revalidated before lookup/provider use.
All API tests use mocked HTTP; no live language-quality claim is made.
## 2026-09-08 — Parent cloud research cross-reference

Parent D043 publishes cloud discovery and proposed host contracts. Package
handoff/README/PLAN now point to that research while retaining the pause.
No runtime, schema, catalog, model call, build or test result changed.
