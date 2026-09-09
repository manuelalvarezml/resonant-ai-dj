from pathlib import Path

from prompt_to_playlist.adapters import load_catalog
from prompt_to_playlist.desktop import describe_run
from prompt_to_playlist.service import build_playlist
from prompt_to_playlist.translators import RulesTranslator
from prompt_to_playlist.vocabulary import load_vocabulary

CATALOG = Path(__file__).parents[1] / "examples/demo-catalog.json"


def test_local_form_evidence_includes_criteria_and_unresolved_requests():
    run = build_playlist("require house; 45 minutes", load_catalog(CATALOG), load_vocabulary(), RulesTranslator())
    text = describe_run(run)
    assert "Required: genre:house" in text
    assert "Please clarify:" in text and "45 minutes" in text
    assert run.result is None


def test_local_form_presents_evidence_without_claiming_mix_readiness():
    run = build_playlist("require house; count 2", load_catalog(CATALOG), load_vocabulary(), RulesTranslator())
    text = describe_run(run)
    assert run.result.matches
    assert run.result.matches[0].track.title in text
    assert "user_verified" in text
    assert "not a validated DJ mix order" in text


def test_ui_cli_passes_same_catalog_and_translator(monkeypatch):
    from prompt_to_playlist import cli, desktop, translators
    calls = []
    class FakeOpenAI:
        def __init__(self):
            self.model = "fictional-model"
    monkeypatch.setattr(cli, "_desktop_project_config", lambda: None)
    monkeypatch.setattr(translators, "OpenAITranslator", FakeOpenAI)
    monkeypatch.setattr(desktop, "launch", lambda *args: calls.append(args))
    assert cli.main(["ui", "--catalog", str(CATALOG)]) == 0
    assert len(calls[0][0].tracks) > 0
    assert isinstance(calls[0][2], FakeOpenAI)
