import pytest

from prompt_to_playlist.models import Catalog, PlaylistQuery, Translation
from prompt_to_playlist.service import build_playlist
from prompt_to_playlist.vocabulary import load_vocabulary


class StubTranslator:
    def __init__(self, unresolved=None, wrong_vocabulary=False):
        self.calls = 0
        self.unresolved = unresolved or []
        self.wrong_vocabulary = wrong_vocabulary

    def translate(self, prompt, vocabulary):
        self.calls += 1
        return Translation(request_text=prompt, query=PlaylistQuery(), provider="test", model="test",
                           prompt_version="test-v1", vocabulary_id="wrong" if self.wrong_vocabulary else vocabulary.vocabulary_id,
                           unresolved=self.unresolved)


def test_unresolved_requirements_stop_retrieval():
    # Invalid catalog vocabulary would fail if search ran.
    from prompt_to_playlist.models import CatalogTrack, TagEvidence
    catalog = Catalog(catalog_id="test", tracks=[CatalogTrack(track_id="a", title="a", tags=[
        TagEvidence(tag="genre:unknown", authority="user_verified", source="test")])])
    translator = StubTranslator(["45-minute mixed duration is unsupported"])
    run = build_playlist("45 minute mix", catalog, load_vocabulary(), translator)
    assert run.status == "needs_clarification" and run.result is None and translator.calls == 1


def test_empty_result_and_provider_identity_check():
    catalog = Catalog(catalog_id="empty", tracks=[])
    run = build_playlist("anything", catalog, load_vocabulary(), StubTranslator())
    assert run.status == "no_matches" and run.result.matches == []
    with pytest.raises(ValueError, match="active vocabulary"):
        build_playlist("anything", catalog, load_vocabulary(), StubTranslator(wrong_vocabulary=True))


@pytest.mark.parametrize("prompt", ["", "  ", "x" * 4001, None])
def test_invalid_prompt_does_not_call_provider(prompt):
    translator = StubTranslator()
    with pytest.raises(ValueError):
        build_playlist(prompt, Catalog(catalog_id="empty", tracks=[]), load_vocabulary(), translator)
    assert translator.calls == 0
