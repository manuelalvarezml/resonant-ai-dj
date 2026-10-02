import numpy as np
import pytest

from prompt_to_playlist.cli import _parser
from prompt_to_playlist.genre_maest import summarize_predictions
from prompt_to_playlist.model_assets import required_assets


def test_maest_is_default_and_replaces_only_the_genre_head():
    args = _parser().parse_args(["analyze-folder", "--folder", "music", "--output-dir", "out"])
    assert "genre_maest" in args.algorithms
    assert "genre_pb" not in required_assets(args.algorithms)
    assert "mood_happy_pb" in required_assets(args.algorithms)
    assert required_assets(["genre_maest"]) == ("maest_pb", "maest_json")


def test_probabilities_are_averaged_before_ranking_and_not_normalized():
    labels = [f"genre-{i:03d}" for i in range(519)]
    values = np.zeros((2, 1, 1, 519))
    values[0, 0, 0, 0] = 1
    values[:, 0, 0, 1] = .8
    values[:, 0, 0, 2] = .7
    result = summarize_predictions(values, labels)
    assert result["patch_count"] == 2
    assert len(result["top_10"]) == 10
    assert result["top_10"][0] == {"genre": "genre-001", "probability": pytest.approx(.8)}
    assert result["scores"]["genre-000"] == .5
    assert sum(result["scores"].values()) == pytest.approx(2)


@pytest.mark.parametrize("values", [np.zeros((1, 87)), np.zeros((0, 519)),
                                     np.full((1, 519), np.nan), np.full((1, 519), 1.1)])
def test_reject_wrong_model_empty_nonfinite_and_logits(values):
    with pytest.raises(ValueError):
        summarize_predictions(values, [str(i) for i in range(519)])


def test_review_document_exports_six_without_scope_error():
    from types import SimpleNamespace as NS
    from prompt_to_playlist.genre_maest import review_document
    labels=[{'genre':f'Electronic---Style {i}','probability':1-i/20} for i in range(10)]
    result=NS(algorithm_id='genre_maest',status='warning',values={'top_10':labels},error=None)
    run=NS(tracks=[NS(source=NS(relative_path='track.mp3',sha256_before='a'*64),algorithms=[result])],source_hashes_unchanged=True,source_inventory_unchanged=True)
    output=review_document(run)
    assert output['tracks'][0]['top_6']==labels[:6]
    assert output['tracks'][0]['top_10']==labels
    result.values={};result.status='failed';result.error='Memory limit'
    assert review_document(run)['tracks'][0]['top_6']==[]
