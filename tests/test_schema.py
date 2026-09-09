from dj_collection_set_builder.constants import AUTHORITY_ESTIMATE, SCHEMA_VERSION
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


def _loudness() -> LoudnessAnalysis:
    shared = dict(
        authority="standardized_measurement",
        status="passed",
        source_tool="ffmpeg",
        tool_version="8.0.1",
    )
    return LoudnessAnalysis(
        integrated=FeatureValue(value=-10.8, unit="LUFS", **shared),
        range=FeatureValue(value=6.2, unit="LU", **shared),
        true_peak=FeatureValue(value=-0.4, unit="dBTP", **shared),
        primary_tool={"name": "ffmpeg", "version": "8.0.1", "filter": "loudnorm"},
        validator={"name": "pyloudnorm", "version": "0.2.0", "passed": True},
    )


def test_track_and_collection_json_use_schema_alias():
    track = TrackAnalysis(
        analysis_id="track-1",
        analyzed_at="2026-09-03T00:00:00Z",
        source=TrackSource(
            track_id="sha256:abc",
            path="test_folder_10_house_tracks/example.mp3",
            filename="example.mp3",
            size_bytes=1,
            sha256_before="abc",
            sha256_after="abc",
            source_unchanged=True,
        ),
        stream=StreamFacts(status="passed", probe_version="8.0.1"),
        loudness=_loudness(),
        tempo=TempoAnalysis(
            selected_candidate=FeatureValue(
                value=126.0,
                unit="BPM",
                authority=AUTHORITY_ESTIMATE,
                status="warning",
                source_tool="all-in-one-mlx",
            ),
            consensus=TempoConsensus(tolerance_bpm=0.2),
            grid_diagnostics=GridDiagnostics(),
        ),
        key=KeyAnalysis(
            tonic="A",
            mode="minor",
            standard_name="A minor",
            camelot="8A",
            open_key="1m",
        ),
    )
    collection = CollectionAnalysis(
        collection_id="col-1",
        input_folder="test_folder_10_house_tracks",
        created_at="2026-09-03T00:00:00Z",
        platform={"os": "macOS", "architecture": "arm64", "python": "3.12.10", "ffmpeg": "8.0.1"},
        expected_audio_count=10,
        discovered_audio_count=1,
        tracks=[track],
    )
    payload = collection.model_dump(mode="json", by_alias=True)
    assert payload["schema"] == "dj-engine/collection-analysis"
    assert payload["schema_version"] == SCHEMA_VERSION
    assert payload["tracks"][0]["schema"] == "dj-engine/track-analysis"
    assert payload["tracks"][0]["tempo"]["selected_candidate"]["authority"] == "benchmark_estimate"
    assert payload["tracks"][0]["key"]["authority"] == "benchmark_estimate"
