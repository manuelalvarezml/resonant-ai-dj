# Implementation coordination contract — 2026-09-07

Historical build coordination. Implementation is complete; use `AGENTS.md`,
`docs/SCHEMAS.md` and the code for current contracts. In particular, the final
run envelope is versioned `prompt-playlist/run`, and `ui` launches an optional
native Tkinter desktop form.

Standalone Python distribution, runtime dependency Pydantic v2 only. No imports
from the DJ engine, no audio IO, no automatic MixPlan. Root owns models.py,
vocabulary.py, search.py, tools.py, service.py, tests for those, package setup
and local interface. Provider agent owns translators.py and its tests.
Adapter agent owns adapters.py, cli.py, examples and their tests. Documentation
agent owns parent DJ/workspace documentation only.

## Python contract (root implements these)

All models use extra=forbid, strict validation and finite floats; defaults are
provided except where stated required. Models are under prompt_to_playlist.models.

- NumericEvidence: value:float required, authority:Authority required,
  source:str required, status: Literal[passed,warning,rejected,unknown,failed,
  not_run] default passed, confidence:float|None=None. Units determined by
  containing field (bpm, duration_s).
- TagEvidence: tag:str required, authority required, source:str required,
  status same, confidence=None.
- CatalogTrack: track_id:str required, title:str required, artist:str|None=None,
  bpm:NumericEvidence|None=None, duration_s:NumericEvidence|None=None,
  tags:list[TagEvidence]=[], complete_tag_axes:list[str]=[], warnings:list[str]=[].
- Catalog: schema_name alias schema literal prompt-playlist/catalog,
  schema_version literal 0.1.0, catalog_id:str required, tracks:list[CatalogTrack]
  required, warnings:list[str]=[]. Duplicate IDs rejected.
- Descriptor: id:str required in axis:value form, description:str required,
  aliases:list[str]=[].
- Vocabulary: schema_name alias schema literal prompt-playlist/vocabulary,
  schema_version literal 0.1.0, vocabulary_id:str required,
  descriptors:list[Descriptor] required. Duplicate IDs/ambiguous aliases rejected.
- PlaylistQuery: required_tags:list[str]=[], preferred_tags:list[str]=[],
  excluded_tags:list[str]=[], min_bpm:float|None=None, max_bpm:float|None=None,
  limit:int=10 (1..100), excluded_track_ids:list[str]=[],
  order:Literal[relevance,bpm_ascending,bpm_descending]=relevance.
  Contradictions, duplicates, min>max, unsupported tags rejected by validate_query.
- Translation: schema_name alias schema literal prompt-playlist/translation,
  schema_version literal 0.1.0, request_text:str required (1..4000 chars),
  query:PlaylistQuery required, provider:str required, model:str required,
  prompt_version:str required, vocabulary_id:str required,
  authority literal llm_proposal default, unresolved:list[str]=[],
  warnings:list[str]=[]. Unresolved constraints block search in service.
- TrackMatch: track:CatalogTrack, score:float, matched_tags:list[str],
  missing_preferred_tags:list[str], reasons:list[str].
- SearchResult: schema_name alias schema literal prompt-playlist/result,
  schema_version literal 0.1.0, catalog_id, vocabulary_id, query,
  ranking_version literal tag-coverage-v1, matches:list[TrackMatch],
  eligible_count:int, excluded_count:int, warnings:list[str],
  catalog_digest:str, vocabulary_digest:str, result_id:str (content digest).
- PlaylistRun: translation:Translation, result:SearchResult|None,
  status:Literal[matched,no_matches,needs_clarification], warnings:list[str]=[].

vocabulary.py: load_vocabulary(path:Path|None=None)->Vocabulary;
validate_query(query:PlaylistQuery,vocabulary:Vocabulary)->PlaylistQuery;
normalize_descriptors(terms:list[str],vocabulary:Vocabulary)->list[str] errors
on unknown values; canonical IDs otherwise. Default JSON packaged beside code.

search.py: search_tracks(catalog:Catalog,query:PlaylistQuery,vocabulary:Vocabulary)
->SearchResult; get_tracks(catalog:Catalog,track_ids:list[str])->list[CatalogTrack]
preserves requested order, rejects unknown/duplicate IDs; validates catalog tags.

translators.py (provider agent): Translator Protocol.translate(prompt:str,
vocabulary:Vocabulary)->Translation; RulesTranslator limited offline grammar,
OpenAITranslator(api_key:str|None=None,model:str|None=None,timeout_s:float=30)
env OPENAI_API_KEY and OPENAI_MODEL, explicit provider selection, no silent fallback.
One Responses structured-output call, only user prompt + vocabulary sent.
validate_query after parsing; provider output cannot set provenance. Provider
errors raise TranslationError(ValueError). Local validation too. Unsupported
constraints -> unresolved (no search). Rules mode must advertise limited grammar
(e.g. 'require house; prefer dark; exclude vocal; bpm 120-130; count 5'), accept
only clauses it fully parses, never silently ignore residual text or negation.
Provider response wire schema should be a required-fields DTO for query +
unresolved + warnings; root defaults need conversion for strict JSON Schema.

adapters.py (adapter agent): load_catalog(path:Path)->Catalog;
from_dj_collection(data:dict)->Catalog (only reads JSON, validates known DJ
schema/version, IDs/hash, preserves BPM estimate/status/source; never fabricates
semantic tags). save_json(value:BaseModel,path:Path)->None output safety checks:
refuse existing files by default; no writes to music folders or audio suffixes.
CLI supports vocabulary, tools, import-dj --analysis --out, search --catalog
--query JSON_FILE, prompt --catalog --text ... --provider rules|openai(default
rules), --vocabulary optional, --out optional(default stdout), and interactive
prompt when --text missing. No credentials in CLI arguments; errors stderr,
exit 2. Entry point prompt-playlist = prompt_to_playlist.cli:main.

service.py: build_playlist(prompt:str,catalog:Catalog,vocabulary:Vocabulary,
translator:Translator)->PlaylistRun. Root implements after provider arrives.
tools.py: list_tools()->list[dict]; tool schemas for normalize_descriptors,
search_tracks, get_tracks; dispatch_tool(name,args,catalog,vocabulary)->JSON dict.
Providers receive no renderer tools. CLI can import functions inside main to
avoid integration timing problems.

Validation commands while developing: DJ .venv/bin/python -m pytest with
PYTHONPATH pointing at standalone src. Root will create independent uv env and
lockfile and run full suites. No real API calls, no corpus renders/reanalysis.
