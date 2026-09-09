from pathlib import Path

import pytest
from typer.testing import CliRunner

from dj_collection_set_builder.cli import app
from dj_collection_set_builder.ingest import EmptyCorpusError, discover_audio_files


def test_empty_folder_raises(tmp_path: Path):
    with pytest.raises(EmptyCorpusError):
        discover_audio_files(tmp_path)


def test_skips_hidden_and_unsupported_files(tmp_path: Path):
    (tmp_path / ".DS_Store").write_bytes(b"x")
    (tmp_path / "notes.txt").write_text("hi")
    (tmp_path / "track.MP3").write_bytes(b"not-really-mp3")
    files, warnings = discover_audio_files(tmp_path)
    assert [path.name for path in files] == ["track.MP3"]
    assert any("notes.txt" in item for item in warnings)


def test_cli_empty_folder_nonzero_exit(tmp_path: Path):
    empty = tmp_path / "music"
    empty.mkdir()
    out = tmp_path / "analysis" / "out.json"
    runner = CliRunner()
    result = runner.invoke(app, [str(empty), "--out", str(out)])
    assert result.exit_code != 0
    assert "No supported audio files" in result.output


def test_cli_help_lists_max_tracks():
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "--max-tracks" in result.output
