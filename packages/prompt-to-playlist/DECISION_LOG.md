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
