"""End-to-end CLI checks against the explicitly fictional demo catalog."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from prompt_to_playlist.cli import main

EXAMPLES = Path(__file__).resolve().parents[1] / "examples"
CATALOG = EXAMPLES / "demo-catalog.json"
QUERY = EXAMPLES / "house-query.json"


def test_search_cli_returns_real_ids_from_synthetic_catalog(capsys):
    assert main(["search", "--catalog", str(CATALOG), "--query", str(QUERY)]) == 0
    captured = capsys.readouterr()
    output = json.loads(captured.out)
    assert output["schema"] == "prompt-playlist/result"
    assert {match["track"]["track_id"] for match in output["matches"]} == {
        "synthetic:night-grid", "synthetic:warehouse-lantern"
    }
    assert captured.err == ""


def test_rules_prompt_cli_does_not_need_credentials(monkeypatch, capsys):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    assert main([
        "prompt", "--catalog", str(CATALOG), "--provider", "rules",
        "--text", "require house; prefer dark; exclude vocal; bpm 120-130; count 5",
    ]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["status"] == "matched"
    assert len(output["result"]["matches"]) == 2


def test_interactive_prompt_does_not_pollute_stdout(monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda: "require house; count 2")
    assert main(["prompt", "--catalog", str(CATALOG), "--provider", "rules"]) == 0
    captured = capsys.readouterr()
    assert json.loads(captured.out)["status"] == "matched"
    assert "Describe your set" in captured.err
    assert "Rules grammar" in captured.err


def test_unresolved_prompt_returns_explanation_without_a_search(capsys):
    assert main(["prompt", "--catalog", str(CATALOG), "--provider", "rules", "--text", "Only songs released last week"]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["status"] == "needs_clarification"
    assert output["result"] is None
    assert output["translation"]["unresolved"]


def test_output_file_refuses_overwrite(tmp_path, capsys):
    destination = tmp_path / "result.json"
    command = ["search", "--catalog", str(CATALOG), "--query", str(QUERY), "--out", str(destination)]
    assert main(command) == 0
    assert capsys.readouterr().out == ""
    original = destination.read_bytes()
    assert main(command) == 2
    assert "already exists" in capsys.readouterr().err
    assert destination.read_bytes() == original


@pytest.mark.parametrize("content", ["{invalid", '{"limit":0}', '{"limit":3,"unknown":true}'])
def test_query_errors_are_stderr_and_exit_two(tmp_path, capsys, content):
    query = tmp_path / "bad-query.json"
    query.write_text(content)
    assert main(["search", "--catalog", str(CATALOG), "--query", str(query)]) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err.startswith("prompt-playlist:")


def test_missing_catalog_is_a_clean_error(tmp_path, capsys):
    assert main(["prompt", "--catalog", str(tmp_path / "missing.json"), "--text", "require house"]) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "prompt-playlist:" in captured.err


@pytest.mark.parametrize("provider_args", [[], ["--provider", "openai"]])
def test_missing_openai_credentials_do_not_silently_switch_provider(monkeypatch, capsys, provider_args):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_MODEL", raising=False)
    assert main(["prompt", "--catalog", str(CATALOG), "--text", "house", *provider_args]) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "prompt-playlist:" in captured.err


def test_vocabulary_and_tools_are_json(capsys):
    assert main(["vocabulary"]) == 0
    assert json.loads(capsys.readouterr().out)["vocabulary_id"] == "descriptors-v1"
    assert main(["tools"]) == 0
    tools = json.loads(capsys.readouterr().out)
    assert len(tools) == 3


def test_explicit_native_import_and_reject_wrong_input(tmp_path, capsys):
    data = {
        "schema": "dj-engine/collection-analysis",
        "schema_version": "0.1.0",
        "collection_id": "fictional-empty-collection",
        "tracks": [],
    }
    analysis = tmp_path / "analysis.json"
    analysis.write_text(json.dumps(data))
    output = tmp_path / "import.json"
    assert main(["import-dj", "--analysis", str(analysis), "--out", str(output)]) == 0
    assert json.loads(output.read_text())["tracks"] == []
    assert capsys.readouterr().out == ""
    analysis.write_text("[]")
    assert main(["import-dj", "--analysis", str(analysis), "--out", str(tmp_path / "invalid.json")]) == 2
    assert "must be a JSON object" in capsys.readouterr().err
