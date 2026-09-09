"""One interpretation call followed by deterministic retrieval."""

from typing import TYPE_CHECKING

from .models import Catalog, PlaylistRun, Translation, Vocabulary
from .search import search_tracks
from .vocabulary import validate_query

if TYPE_CHECKING:
    from .translators import Translator


def build_playlist(prompt: str, catalog: Catalog, vocabulary: Vocabulary,
                   translator: "Translator") -> PlaylistRun:
    if not isinstance(prompt, str) or not prompt.strip() or len(prompt) > 4000:
        raise ValueError("Enter a description between 1 and 4000 characters.")
    vocabulary = Vocabulary.model_validate(vocabulary.model_dump())
    translation = Translation.model_validate(translator.translate(prompt, vocabulary).model_dump())
    if translation.request_text != prompt or translation.vocabulary_id != vocabulary.vocabulary_id:
        raise ValueError("Translation must identify the original request and active vocabulary")
    validate_query(translation.query, vocabulary)
    if translation.unresolved:
        return PlaylistRun(translation=translation, result=None, status="needs_clarification",
                           warnings=["Unresolved requirements must be clarified before searching."])
    result = search_tracks(catalog, translation.query, vocabulary)
    return PlaylistRun(translation=translation, result=result,
                       status="matched" if result.matches else "no_matches",
                       warnings=translation.warnings)
