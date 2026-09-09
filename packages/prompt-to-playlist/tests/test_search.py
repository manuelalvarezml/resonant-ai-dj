import pytest
from pydantic import ValidationError

from prompt_to_playlist.models import Catalog, CatalogTrack, NumericEvidence, PlaylistQuery, TagEvidence
from prompt_to_playlist.search import get_tracks, search_tracks
from prompt_to_playlist.tools import dispatch_tool, list_tools
from prompt_to_playlist.vocabulary import load_vocabulary, normalize_descriptors


def track(track_id, tags=(), bpm=128.0, complete=(), status="passed"):
    return CatalogTrack(track_id=track_id, title=track_id,
        tags=[TagEvidence(tag=tag, authority="user_verified", source="synthetic-test", status=status) for tag in tags],
        bpm=NumericEvidence(value=bpm, authority="benchmark_estimate", source="synthetic-test") if bpm else None,
        complete_tag_axes=list(complete))


def search(tracks, **kwargs):
    return search_tracks(Catalog(catalog_id="synthetic", tracks=tracks), PlaylistQuery(**kwargs), load_vocabulary())


def test_hard_filters_and_preference_ranking_are_separate():
    result = search([track("b", ["genre:house"]), track("c", ["genre:techno", "mood:dark"]),
                     track("a", ["genre:house", "mood:dark"])],
                    required_tags=["genre:house"], preferred_tags=["mood:dark"], limit=3)
    assert [m.track.track_id for m in result.matches] == ["a", "b"]
    assert [m.score for m in result.matches] == [1, 0]
    assert result.matches[1].missing_preferred_tags == ["mood:dark"]
    assert result.eligible_count == 2 and result.excluded_count == 1


def test_negative_filter_requires_complete_axis_and_usable_evidence():
    result = search([track("unknown"), track("vocal", ["vocals:vocal"], complete=["vocals"]),
                    track("instrumental", ["vocals:instrumental"], complete=["vocals"]),
                    track("failed", ["vocals:instrumental"], complete=["vocals"], status="failed")],
                    excluded_tags=["vocals:vocal"])
    assert [m.track.track_id for m in result.matches] == ["instrumental"]
    assert any("negative-tag evidence" in warning for warning in result.warnings)


def test_unknown_semantics_never_inferred_from_bpm():
    result = search([track("fast", bpm=160.0)], required_tags=["energy:high"])
    assert not result.matches
    assert any("No usable catalog evidence for: energy:high" == warning for warning in result.warnings)


def test_bpm_filters_are_inclusive_and_missing_is_not_zero():
    result = search([track("lower", bpm=120.0), track("upper", bpm=130.0),
                     track("outside", bpm=130.1), track("unknown", bpm=None)], min_bpm=120.0, max_bpm=130.0)
    assert {m.track.track_id for m in result.matches} == {"lower", "upper"}
    assert all(m.track.bpm.authority == "benchmark_estimate" for m in result.matches)


@pytest.mark.parametrize("status", ["failed", "rejected", "unknown", "not_run"])
def test_unusable_tags_and_bpm_do_not_match(status):
    t = track("failed", ["genre:house"], status=status)
    t.bpm.status = status
    assert search([t], required_tags=["genre:house"]).eligible_count == 0
    assert search([t], min_bpm=120.0).eligible_count == 0


@pytest.mark.parametrize("order,expected", [("bpm_ascending", ["slow", "fast", "unknown"]),
                                            ("bpm_descending", ["fast", "slow", "unknown"])])
def test_bpm_order_keeps_unknown_last(order, expected):
    result = search([track("unknown", bpm=None), track("fast", bpm=135.0), track("slow", bpm=120.0)], order=order)
    assert [m.track.track_id for m in result.matches] == expected


def test_replay_is_identical_and_ties_use_stable_ids():
    tracks = [track("b"), track("a")]
    first = search(tracks, limit=1)
    second = search(tracks, limit=1)
    assert first.model_dump_json() == second.model_dump_json()
    assert first.matches[0].track.track_id == "a"
    assert search(list(reversed(tracks)), limit=1).matches == first.matches
    assert first.result_id != search(tracks, limit=2).result_id


def test_excluded_ids_and_empty_catalog():
    result = search([track("a"), track("b")], excluded_track_ids=["a"])
    assert [m.track.track_id for m in result.matches] == ["b"]
    assert search([]).matches == []


@pytest.mark.parametrize("kwargs", [
    {"min_bpm": 130.0, "max_bpm": 120.0}, {"limit": 0}, {"limit": 101}, {"limit": True},
    {"min_bpm": float("nan")}, {"max_bpm": float("inf")}, {"limit": "3"},
    {"required_tags": ["genre:house"], "excluded_tags": ["genre:house"]},
    {"preferred_tags": ["mood:dark", "mood:dark"]}, {"shell": "execute"},
])
def test_invalid_queries_rejected(kwargs):
    with pytest.raises(ValidationError):
        PlaylistQuery(**kwargs)


def test_unknown_tags_rejected_on_query_and_catalog():
    with pytest.raises(ValueError, match="Unknown descriptor"):
        search([], required_tags=["genre:invented"])
    with pytest.raises(ValueError, match="unknown descriptors"):
        search([track("a", ["genre:invented"])])


def test_model_proposals_cannot_become_track_evidence():
    with pytest.raises(ValidationError):
        TagEvidence(tag="mood:dark", authority="llm_proposal", source="test")


def test_catalog_ids_must_be_unique():
    with pytest.raises(ValidationError, match="Duplicate catalog"):
        Catalog(catalog_id="test", tracks=[track("a"), track("a")])


def test_lookup_preserves_order_and_rejects_invented_ids():
    catalog = Catalog(catalog_id="test", tracks=[track("a"), track("b")])
    assert [t.track_id for t in get_tracks(catalog, ["b", "a"])] == ["b", "a"]
    for ids in (["a", "a"], ["fake"]):
        with pytest.raises(ValueError):
            get_tracks(catalog, ids)


def test_tool_allowlist_rejects_arbitrary_operations_and_extra_fields():
    catalog = Catalog(catalog_id="test", tracks=[track("a", ["genre:house"])])
    vocab = load_vocabulary()
    assert {tool["name"] for tool in list_tools()} == {"normalize_descriptors", "search_tracks", "get_tracks"}
    with pytest.raises(ValueError):
        dispatch_tool("render_set", {}, catalog, vocab)
    with pytest.raises(ValueError):
        dispatch_tool("get_tracks", {"track_ids": ["a"], "path": "/tmp/music"}, catalog, vocab)
    assert dispatch_tool("normalize_descriptors", {"terms": ["HOUSE"]}, catalog, vocab)["tags"] == ["genre:house"]
    result = dispatch_tool("search_tracks", {"query": {"required_tags": ["genre:house"]}}, catalog, vocab)
    assert result["matches"][0]["track"]["track_id"] == "a"


def test_vocabulary_can_be_replaced_and_ambiguous_aliases_rejected():
    from prompt_to_playlist.models import Descriptor, Vocabulary
    vocab = Vocabulary(vocabulary_id="custom-v1", descriptors=[Descriptor(id="texture:airy", description="User annotation", aliases=["airy"])])
    assert normalize_descriptors(["AIRY"], vocab) == ["texture:airy"]
    with pytest.raises(ValueError):
        normalize_descriptors(["house"], vocab)
    with pytest.raises(ValidationError, match="Ambiguous"):
        Vocabulary(vocabulary_id="bad", descriptors=[Descriptor(id="texture:airy", description="a", aliases=["air"]),
                                                      Descriptor(id="mood:airy", description="b", aliases=["AIR"])])


def test_mutated_catalog_and_vocabulary_revalidated_at_public_boundaries():
    from prompt_to_playlist.models import Descriptor
    catalog = Catalog(catalog_id="test", tracks=[track("a")])
    catalog.tracks.append(track("a", ["genre:house"]))
    with pytest.raises(ValueError, match="Duplicate catalog"):
        get_tracks(catalog, ["a"])
    vocab = load_vocabulary()
    vocab.descriptors.append(Descriptor(id="genre:other", description="ambiguous", aliases=["house"]))
    with pytest.raises(ValueError, match="Ambiguous"):
        normalize_descriptors(["house"], vocab)
    with pytest.raises(ValueError, match="Ambiguous"):
        search_tracks(Catalog(catalog_id="empty", tracks=[]), PlaylistQuery(), vocab)
