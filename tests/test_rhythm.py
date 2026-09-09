from dj_collection_set_builder.models import Section
from dj_collection_set_builder.rhythm import (
    bpm_from_intervals,
    build_loop_candidates,
    build_sections,
    event_f1,
    grid_diagnostics,
    is_half_double,
)


def test_half_double_detection():
    assert is_half_double(63.0, 126.0, 0.2)
    assert is_half_double(126.0, 252.0, 0.2)
    assert not is_half_double(126.0, 128.0, 0.2)


def test_bpm_from_intervals_and_grid_diagnostics():
    interval = 60.0 / 126.0
    beats = [0.5 + i * interval for i in range(40)]
    bpm = bpm_from_intervals(beats)
    assert bpm is not None
    assert abs(bpm - 126.0) < 0.05
    diagnostics = grid_diagnostics(beats)
    assert diagnostics.median_interval_s is not None
    assert diagnostics.fixed_grid_residual_ms_p50 is not None
    assert diagnostics.fixed_grid_residual_ms_p50 < 1.0


def test_event_f1_perfect_and_mismatch():
    beats = [0.0, 0.5, 1.0, 1.5]
    assert event_f1(beats, beats) == 1.0
    assert event_f1(beats, [0.0, 0.5, 1.0, 3.0]) < 1.0


def test_loop_candidates_prefer_in_section_windows():
    downbeats = [i * 1.905 for i in range(40)]
    sections = [
        Section(
            section_id="section-01",
            start_s=downbeats[4],
            end_s=downbeats[20],
            source_tool="all-in-one-mlx",
            label="chorus",
        )
    ]
    loops = build_loop_candidates("sha256:x", downbeats, sections, downbeats)
    sixteen = [item for item in loops if item.bars == 16]
    contained = [item for item in sixteen if item.contained_in_section_id == "section-01"]
    assert contained
    assert all(item.status == "passed" for item in contained)
    crossing = [item for item in sixteen if item.crosses_novelty_boundary]
    assert crossing
    rejected = [item for item in loops if item.status == "rejected"]
    assert not rejected


class FakeSegment:
    def __init__(self, start, end, label):
        self.start = start
        self.end = end
        self.label = label


def test_build_sections_accepts_dataclass_segments():
    downbeats = [0.0, 1.9, 3.8, 5.7]
    sections = build_sections(
        [FakeSegment(0.0, 3.8, "intro")],
        downbeats,
        source_tool="all-in-one-mlx",
        tool_version="1.0.6",
    )
    assert len(sections) == 1
    assert sections[0].label == "intro"
    assert sections[0].start_s == 0.0
