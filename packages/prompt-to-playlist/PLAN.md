# Parallel roadmap

Updated 2026-09-08. The implemented package remains independent of DJ render
work, but further playlist development is paused by the user. Preserve the
backlog below until work is explicitly resumed.

Parent D043 publishes [cloud discovery](../../docs/cloud-library/README.md)
with a proposed future playlist host boundary. Its contracts are planning
material only; this package remains paused and independently versioned.

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

## Next — Broader evidence and language evaluation

1. Define a small annotation guide for the descriptors the user actually needs.
   Record tags and axis completeness in a separate native catalog or sidecar;
   retain source hashes/IDs and human verification scope. Do not edit audio or
   silently overwrite analysis. Start with reviewed examples before model tagging.
2. Broaden the configured model's fixed prompt set: genre/mood,
   positive/negative constraints, unknown tags, ambiguity, contradictory bounds,
   mixed supported/unsupported requests, and languages the user wants supported.
   Grade intent preservation separately from deterministic retrieval correctness.
   The initial five live checks are a baseline, not a comprehensive benchmark.
3. Record missed constraints and expected IDs before modifying prompts/weights.
   Do not call mocked tests a live evaluation or establish a blanket injection claim.
4. Consider an edit-before-search query review flow if evaluation demonstrates
   a need. The current form shows the interpretation with results; it is read-only.

## Later, driven by concrete consumers

- Dedicated catalog-tag enrichment adapter and incremental snapshots.
- Additional numeric/era/history filters with explicit source semantics.
- Another LLM provider/local model via `Translator`.
- More capable retrieval/indexing only when catalog scale requires it.
- Spotify or another application's catalog/export adapter after access research.
- Explicit downstream playlist-candidate → DJ planning integration with the
  existing renderer's separate validations. No automatic MixPlan in this slice.

No scheduling, embeddings, vector database, remote publication, automatic
rendering, transition optimization, or set-duration promise is required to
finish this foundation.
