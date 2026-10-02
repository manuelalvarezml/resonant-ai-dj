"""One interpretation call followed by deterministic retrieval."""

from typing import TYPE_CHECKING

from .models import Catalog, ClarificationAnswer, PlaylistRun, Translation, Vocabulary
from .intent import capabilities, compile_plan
from .search import search_tracks, _validate_catalog
from .vocabulary import validate_query

if TYPE_CHECKING:
    from .translators import Translator


def build_playlist(prompt: str, catalog: Catalog, vocabulary: Vocabulary,
                   translator: "Translator", *, clarifications: list[ClarificationAnswer] | None = None, query_encoder=None) -> PlaylistRun:
    if not isinstance(prompt, str) or not prompt.strip() or len(prompt) > 4000:
        raise ValueError("Enter a description between 1 and 4000 characters.")
    vocabulary = Vocabulary.model_validate(vocabulary.model_dump())
    answers = [ClarificationAnswer.model_validate(a.model_dump()) for a in (clarifications or [])]
    if len(answers) > 3:
        raise ValueError("At most three clarification answers are supported")
    if callable(getattr(translator, "translate_intent", None)):
        catalog = _validate_catalog(catalog, vocabulary)
        proposed = translator.translate_intent(prompt, vocabulary, capabilities(catalog), answers)
    else:
        if answers:
            raise ValueError("This translator does not support clarification answers")
        proposed = translator.translate(prompt, vocabulary)
    translation = Translation.model_validate(proposed.model_dump())
    if translation.request_text != prompt or translation.vocabulary_id != vocabulary.vocabulary_id:
        raise ValueError("Translation must identify the original request and active vocabulary")
    if translation.plan:
        previous_warnings = translation.warnings
        translation = compile_plan(prompt, translation.proposed_plan or translation.plan, vocabulary, model=translation.model, clarifications=answers, reasoning_effort=translation.reasoning_effort)
        translation.warnings = list(dict.fromkeys([*translation.warnings, *previous_warnings]))
        if translation.plan.disposition in {"needs_clarification", "unsupported"}:
            return PlaylistRun(translation=translation, result=None,
                               status=translation.plan.disposition, warnings=translation.warnings)
    if translation.request_text != prompt or translation.vocabulary_id != vocabulary.vocabulary_id:
        raise ValueError("Translation must identify the original request and active vocabulary")
    validate_query(translation.query, vocabulary)
    if translation.unresolved:
        return PlaylistRun(translation=translation, result=None, status="needs_clarification",
                           warnings=["Unresolved requirements must be clarified before searching."])
    if query_encoder and translation.query.semantic:
        query, semantic_warnings = query_encoder(translation.query, catalog, vocabulary)
        translation.query = type(translation.query).model_validate(query.model_dump())
        translation.warnings = list(dict.fromkeys([*translation.warnings, *semantic_warnings]))
    result = search_tracks(catalog, translation.query, vocabulary)
    return PlaylistRun(translation=translation, result=result,
                       status=("partial_support" if (translation.plan and translation.plan.disposition == "partial_support") or bool(translation.query.semantic and result.ranking_version != "hybrid-semantic-v1") or any(w.startswith("No usable catalog evidence for soft scoring:") for w in result.warnings) else "matched") if result.matches else "no_matches",
                       warnings=translation.warnings)
