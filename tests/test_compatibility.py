from pathlib import Path

from dj_collection_set_builder.catalog import list_available_dj_tools
from dj_collection_set_builder.compatibility import score_harmonic_match, score_tempo_match, score_transition
from dj_collection_set_builder.constants import AUTHORITY_ESTIMATE
from dj_collection_set_builder.models import (
    CollectionAnalysis,
    FeatureValue,
    GridDiagnostics,
    KeyAnalysis,
    LoudnessAnalysis,
    StreamFacts,
    TempoAnalysis,
    TempoConsensus,
    TrackAnalysis,
    TrackSource,
)
from dj_collection_set_builder.story import propose_tempo_wave_order, tempo_wave_climb_count


def test_rekordbox_2a_related_2_matches_alphatheta_example():
    same = score_harmonic_match("2A", "2A")
    relative = score_harmonic_match("2A", "2B")
    adjacent_left = score_harmonic_match("2A", "1A")
    adjacent_right = score_harmonic_match("2A", "3A")
    related_3 = score_harmonic_match("2A", "1B")
    assert same.relationship == "same" and same.compatible
    assert relative.relationship == "relative" and relative.compatible
    assert adjacent_left.relationship == "adjacent_same_mode" and adjacent_left.compatible
    assert adjacent_right.compatible
    assert related_3.relationship == "related_3"
    assert related_3.compatible is False
    assert score_harmonic_match("2A", "1B", policy="rekordbox-related-3").compatible is True


def test_camelot_wheel_wraps_between_12_and_1():
    match = score_harmonic_match("1A", "12A")
    assert match.relationship == "adjacent_same_mode"
    assert match.compatible is True


def test_unknown_key_is_not_a_match():
    match = score_harmonic_match(None, "8A")
    assert match.relationship == "unknown"
    assert match.compatible is False
    assert match.score == 0.0


def test_tempo_prefers_under_two_percent_and_rejects_over_four():
    easy = score_tempo_match(128.0, 130.0)
    assert easy.feasible is True
    assert easy.incoming_stretch_percent < 2.0
    assert easy.score == 1.0
    hard = score_tempo_match(120.0, 126.0)
    assert hard.incoming_stretch_percent > 4.0
    assert hard.feasible is False
    assert hard.score == 0.0


def test_tempo_does_not_reinterpret_half_or_double():
    match = score_tempo_match(120.0, 240.0)
    assert match.half_double_ambiguity is True
    assert match.feasible is False
    assert match.score == 0.0


def test_story_conflict_penalizes_tempo_score():
    match = score_tempo_match(130.0, 128.0, story_target="up")
    assert match.story_agreement == "conflict"
    assert match.score < 1.0


def _track(*, filename: str, bpm: float, camelot: str, lufs: float = -10.0) -> TrackAnalysis:
    letter = camelot[-1]
    mode = "minor" if letter == "A" else "major"
    return TrackAnalysis(
        analysis_id=filename,
        analyzed_at="2026-09-04T00:00:00Z",
        source=TrackSource(
            track_id=f"sha256:{filename}",
            path=filename,
            filename=filename,
            size_bytes=1,
            sha256_before=filename,
            sha256_after=filename,
            source_unchanged=True,
        ),
        stream=StreamFacts(status="passed"),
        loudness=LoudnessAnalysis(
            integrated=FeatureValue(
                value=lufs,
                unit="LUFS",
                authority="standardized_measurement",
                status="passed",
                source_tool="ffmpeg",
            ),
            range=FeatureValue(
                value=6.0,
                unit="LU",
                authority="standardized_measurement",
                status="passed",
                source_tool="ffmpeg",
            ),
            true_peak=FeatureValue(
                value=-1.0,
                unit="dBTP",
                authority="standardized_measurement",
                status="passed",
                source_tool="ffmpeg",
            ),
            primary_tool={"name": "ffmpeg"},
            validator={"name": "pyloudnorm", "passed": True},
        ),
        tempo=TempoAnalysis(
            selected_candidate=FeatureValue(
                value=bpm,
                unit="BPM",
                authority=AUTHORITY_ESTIMATE,
                status="warning",
                source_tool="all-in-one-mlx",
            ),
            consensus=TempoConsensus(tolerance_bpm=0.2),
            grid_diagnostics=GridDiagnostics(),
        ),
        key=KeyAnalysis(
            tonic="X",
            mode=mode,
            standard_name=f"test {mode}",
            camelot=camelot,
            strength=0.8,
        ),
        warnings=[],
    )


def test_transition_caps_incompatible_harmonics():
    left = _track(filename="a.mp3", bpm=128, camelot="2A")
    right = _track(filename="b.mp3", bpm=128, camelot="8A")
    score = score_transition(left, right)
    assert score.harmonic.compatible is False
    assert score.score <= 0.15


def test_tempo_wave_starts_at_lowest_bpm_and_keeps_every_track():
    tracks = [
        _track(filename="high.mp3", bpm=130, camelot="8A"),
        _track(filename="low.mp3", bpm=120, camelot="8A"),
        _track(filename="mid.mp3", bpm=125, camelot="8B"),
        _track(filename="peak.mp3", bpm=128, camelot="9A"),
    ]
    ordered = propose_tempo_wave_order(tracks)
    assert [item.source.filename for item in ordered][0] == "low.mp3"
    assert {item.source.filename for item in ordered} == {item.source.filename for item in tracks}
    assert tempo_wave_climb_count(10) == 6


def test_catalog_marks_lookups_and_clip_render_implemented():
    catalog = {item.name: item for item in list_available_dj_tools()}
    assert catalog["score_harmonic_match"].availability == "implemented"
    assert catalog["get_track_summary"].availability == "implemented"
    assert catalog["load_track"].availability == "implemented"
    assert catalog["time_stretch"].availability == "implemented"
    assert catalog["render_segment"].availability == "implemented"
    assert catalog["render_set"].availability == "implemented"
    assert catalog["set_volume_envelope"].availability == "planned"
    assert catalog["eq_band"].hard_limits["gain_db_min"] == -18.0


def test_corpus_collection_can_be_scored():
    path = Path("output/step1-collection.json")
    if not path.exists():
        return
    collection = CollectionAnalysis.model_validate_json(path.read_text(encoding="utf-8"))
    ordered = propose_tempo_wave_order(collection.tracks)
    assert len(ordered) == 10
    first = score_transition(ordered[0], ordered[1])
    assert 0.0 <= first.score <= 1.0
