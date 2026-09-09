import subprocess
from pathlib import Path

import pytest
from typer.testing import CliRunner

from dj_collection_set_builder.ingest import sha256_file
from dj_collection_set_builder.render import (
    RenderError,
    crossfade,
    eq_band,
    house_transition,
    load_track,
    loop_audio,
    low_cut,
    probe_duration_s,
    render_segment,
    set_gain,
    time_stretch,
)
from dj_collection_set_builder.render_cli import app


def _write_sine(path: Path, *, duration_s: float = 2.0, codec: str = "pcm_f32le") -> Path:
    command = [
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-f",
        "lavfi",
        "-i",
        f"sine=frequency=440:sample_rate=44100:duration={duration_s}",
        "-ac",
        "2",
        "-c:a",
        codec,
        str(path),
    ]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        raise AssertionError(completed.stderr)
    return path


def test_load_track_copies_range_and_leaves_source_hash_unchanged(tmp_path: Path):
    music = tmp_path / "music"
    music.mkdir()
    source = _write_sine(music / "tone.mp3", codec="libmp3lame")
    before = sha256_file(source)
    out = tmp_path / "clip.wav"
    artifact = load_track(source, start_s=0.25, end_s=1.25, out_path=out, source_folder=music)
    assert artifact.tool == "load_track"
    assert out.exists()
    assert sha256_file(source) == before
    assert artifact.duration_s == pytest.approx(1.0, abs=0.05)


def test_load_track_refuses_writes_into_source_folder(tmp_path: Path):
    music = tmp_path / "music"
    music.mkdir()
    source = _write_sine(music / "tone.wav")
    with pytest.raises(RenderError, match="outside the source music folder"):
        load_track(
            source,
            start_s=0.0,
            end_s=1.0,
            out_path=music / "illegal.wav",
            source_folder=music,
        )


def test_gain_and_eq_bounds(tmp_path: Path):
    source = _write_sine(tmp_path / "tone.wav")
    with pytest.raises(RenderError, match="gain_db"):
        set_gain(source, gain_db=12.0, out_path=tmp_path / "hot.wav")
    with pytest.raises(RenderError, match="EQ gain"):
        eq_band(source, band="low", gain_db=9.0, out_path=tmp_path / "eq.wav")
    artifact = set_gain(source, gain_db=-3.0, out_path=tmp_path / "quiet.wav")
    assert artifact.duration_s == pytest.approx(2.0, abs=0.05)
    eq = eq_band(source, band="low", gain_db=-6.0, out_path=tmp_path / "eq-ok.wav")
    assert eq.warnings


def test_time_stretch_rejects_over_four_percent(tmp_path: Path):
    source = _write_sine(tmp_path / "tone.wav")
    with pytest.raises(RenderError, match="exceeds v1 maximum"):
        time_stretch(
            source,
            from_bpm=120.0,
            target_bpm=126.0,
            out_path=tmp_path / "too-far.wav",
        )
    stretched = time_stretch(
        source,
        from_bpm=128.0,
        target_bpm=130.0,
        out_path=tmp_path / "nudge.wav",
    )
    assert stretched.duration_s == pytest.approx(2.0 * 128.0 / 130.0, abs=0.08)
    assert "atempo" in stretched.warnings[0]


def test_loop_crossfade_and_low_cut(tmp_path: Path):
    source = _write_sine(tmp_path / "tone.wav", duration_s=1.0)
    looped = loop_audio(source, repetitions=2, out_path=tmp_path / "loop.wav")
    assert looped.duration_s == pytest.approx(2.0 - 0.012, abs=0.05)
    cut = low_cut(source, cutoff_hz=180.0, out_path=tmp_path / "cut.wav")
    assert cut.duration_s == pytest.approx(1.0, abs=0.05)


def test_crossfade_two_clips(tmp_path: Path):
    left = _write_sine(tmp_path / "left.wav", duration_s=2.0)
    right = _write_sine(tmp_path / "right.wav", duration_s=2.0)
    mixed = crossfade(left, right, duration_s=0.5, out_path=tmp_path / "xfade.wav")
    assert mixed.duration_s == pytest.approx(3.5, abs=0.08)


def test_house_transition_preserves_overlap_duration(tmp_path: Path):
    left = _write_sine(tmp_path / "left.wav", duration_s=6.0)
    right = _write_sine(tmp_path / "right.wav", duration_s=6.0)
    mixed = house_transition(
        left,
        right,
        duration_s=4.0,
        out_path=tmp_path / "house-transition.wav",
    )
    assert mixed.tool == "house_transition"
    assert mixed.duration_s == pytest.approx(8.0, abs=0.08)
    assert "house-eq-v1" in mixed.warnings[0]


def test_render_segment_chains_gain_and_low_cut(tmp_path: Path):
    source = _write_sine(tmp_path / "tone.wav")
    artifact = render_segment(
        source,
        operations=[
            {"op": "set_gain", "gain_db": -3.0},
            {"op": "low_cut", "cutoff_hz": 180.0},
        ],
        out_path=tmp_path / "segment.wav",
        work_dir=tmp_path / "work",
    )
    assert artifact.tool == "render_segment"
    assert artifact.duration_s == pytest.approx(2.0, abs=0.05)
    assert probe_duration_s(tmp_path / "segment.wav") == pytest.approx(2.0, abs=0.05)


def test_render_cli_protects_source_parent_by_default(tmp_path: Path):
    music = tmp_path / "music"
    music.mkdir()
    source = _write_sine(music / "tone.wav")
    out = music / "must-not-exist.wav"
    result = CliRunner().invoke(
        app,
        ["set-gain", str(source), "--out", str(out), "--gain-db", "-3"],
    )
    assert result.exit_code == 1
    assert "outside the source music folder" in result.output
    assert not out.exists()


def test_load_track_refusal_does_not_create_forbidden_parent(tmp_path: Path):
    music = tmp_path / "music"
    music.mkdir()
    source = _write_sine(music / "tone.wav")
    forbidden_parent = music / "created-before-refusal"
    with pytest.raises(RenderError, match="outside the source music folder"):
        load_track(
            source,
            start_s=0.0,
            end_s=1.0,
            out_path=forbidden_parent / "illegal.wav",
            source_folder=music,
        )
    assert not forbidden_parent.exists()
