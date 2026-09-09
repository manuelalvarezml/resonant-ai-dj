"""Project profile integration uses fake keys and never calls the network."""

import json
from pathlib import Path

import pytest

from prompt_to_playlist.cli import main
from prompt_to_playlist.models import PlaylistQuery, Translation

CATALOG = Path(__file__).parents[1] / "examples/demo-catalog.json"


def profile(tmp_path):
    (tmp_path / "catalog.json").write_bytes(CATALOG.read_bytes())
    (tmp_path / "fake.zshrc").write_text("export PROJECT_TEST_KEY='fictional-test-key'\n")
    path = tmp_path / "playlist.toml"
    path.write_text('schema_version="0.1.0"\nprovider="openai"\ncatalog="catalog.json"\n'
                    '[openai]\nmodel="fictional-model"\napi_key_env="PROJECT_TEST_KEY"\n'
                    'key_source_file="fake.zshrc"\n')
    return path


def test_configured_prompt_selects_specific_key_model_and_catalog(tmp_path, monkeypatch, capsys):
    from prompt_to_playlist import translators
    config = profile(tmp_path)
    calls = []
    class FakeOpenAI:
        def __init__(self, **kwargs):
            calls.append(kwargs)
        def translate(self, prompt, vocabulary):
            return Translation(request_text=prompt, query=PlaylistQuery(required_tags=["genre:house"], limit=2),
                               provider="openai", model="fictional-model", prompt_version="test",
                               vocabulary_id=vocabulary.vocabulary_id)
    monkeypatch.setattr(translators, "OpenAITranslator", FakeOpenAI)
    monkeypatch.setenv("OPENAI_API_KEY", "unrelated-generic-key")
    monkeypatch.delenv("PROJECT_TEST_KEY", raising=False)
    assert main(["prompt", "--config", str(config), "--text", "Two house tracks"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "matched" and len(result["result"]["matches"]) == 2
    assert calls == [{"api_key": "fictional-test-key", "model": "fictional-model", "timeout_s": 30.0}]


def test_rules_override_does_not_read_configured_secret(tmp_path, monkeypatch, capsys):
    from prompt_to_playlist import config as settings
    monkeypatch.setattr(settings, "read_api_key", lambda *args: pytest.fail("Rules must not read credentials"))
    assert main(["prompt", "--config", str(profile(tmp_path)), "--provider", "rules", "--text", "count 2"]) == 0
    assert json.loads(capsys.readouterr().out)["translation"]["provider"] == "rules"


def test_config_is_explicit_and_missing_catalog_is_clear(tmp_path, monkeypatch, capsys):
    profile(tmp_path)
    monkeypatch.chdir(tmp_path)
    assert main(["prompt", "--text", "house"]) == 2
    assert "Provide --catalog or --config" in capsys.readouterr().err


def test_import_refuses_source_destination_before_reading_audio(tmp_path, monkeypatch, capsys):
    from prompt_to_playlist import folder_catalog
    monkeypatch.setattr(folder_catalog, "import_mp3_folder", lambda *args: pytest.fail("Import should not run"))
    folder = tmp_path / "collection"
    folder.mkdir()
    assert main(["import-folder", "--folder", str(folder), "--out", str(folder / "catalog.json"),
                 "--manifest", str(tmp_path / "manifest.json")]) == 2
    assert "outside the selected music folder" in capsys.readouterr().err


def test_desktop_uses_configured_openai_profile(tmp_path, monkeypatch):
    from prompt_to_playlist import desktop, translators
    calls = []
    class FakeOpenAI:
        def __init__(self, **kwargs):
            self.model = kwargs["model"]
    monkeypatch.setattr(translators, "OpenAITranslator", FakeOpenAI)
    monkeypatch.setattr(desktop, "launch", lambda *args: calls.append(args))
    monkeypatch.delenv("PROJECT_TEST_KEY", raising=False)
    assert main(["ui", "--config", str(profile(tmp_path))]) == 0
    assert calls[0][2].model == "fictional-model"


def test_desktop_discovers_current_profile_and_honors_catalog_override(tmp_path, monkeypatch):
    from prompt_to_playlist import desktop, translators
    profile(tmp_path)
    override = tmp_path / "override.json"
    contents = json.loads(CATALOG.read_text())
    contents["tracks"] = contents["tracks"][:1]
    override.write_text(json.dumps(contents))
    calls = []
    class FakeOpenAI:
        def __init__(self, **kwargs):
            self.model = kwargs["model"]
    monkeypatch.setattr(translators, "OpenAITranslator", FakeOpenAI)
    monkeypatch.setattr(desktop, "launch", lambda *args: calls.append(args))
    monkeypatch.delenv("PROJECT_TEST_KEY", raising=False)
    monkeypatch.chdir(tmp_path)
    assert main(["ui", "--catalog", str(override)]) == 0
    assert calls[0][2].model == "fictional-model"
    assert len(calls[0][0].tracks) == 1


def test_desktop_explicit_profile_wins_over_current_directory(tmp_path, monkeypatch):
    from prompt_to_playlist import desktop, translators
    explicit_dir = tmp_path / "explicit"
    explicit_dir.mkdir()
    selected = profile(explicit_dir)
    (tmp_path / "playlist.toml").write_text("invalid TOML")
    calls = []
    class FakeOpenAI:
        def __init__(self, **kwargs):
            calls.append(kwargs)
    monkeypatch.setattr(translators, "OpenAITranslator", FakeOpenAI)
    monkeypatch.setattr(desktop, "launch", lambda *args: None)
    monkeypatch.delenv("PROJECT_TEST_KEY", raising=False)
    monkeypatch.chdir(tmp_path)
    assert main(["ui", "--config", str(selected)]) == 0
    assert calls[0]["model"] == "fictional-model"


def test_invalid_discovered_profile_is_not_silently_skipped(tmp_path, monkeypatch, capsys):
    from prompt_to_playlist import config as settings
    (tmp_path / "playlist.toml").write_text("invalid TOML")
    monkeypatch.setattr(settings, "read_api_key", lambda *args: pytest.fail("Invalid config must stop before credentials"))
    monkeypatch.chdir(tmp_path)
    assert main(["ui", "--catalog", str(CATALOG)]) == 2
    assert "TOML" in capsys.readouterr().err


def test_desktop_discovery_uses_only_editable_checkout_or_immediate_directory(tmp_path, monkeypatch):
    from prompt_to_playlist import cli
    checkout = tmp_path / "checkout"
    source = checkout / "src" / "prompt_to_playlist" / "cli.py"
    source.parent.mkdir(parents=True)
    source.touch()
    (checkout / "pyproject.toml").write_text('[project]\nname="prompt-to-playlist"\n')
    selected = checkout / "playlist.toml"
    selected.write_text("checkout profile")
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    (tmp_path / "playlist.toml").write_text("ancestor must not be discovered")
    monkeypatch.setattr(cli, "__file__", str(source))
    monkeypatch.chdir(elsewhere)
    assert cli._desktop_project_config() == selected
    immediate = elsewhere / "playlist.toml"
    immediate.write_text("local profile")
    assert cli._desktop_project_config() == immediate
    immediate.unlink()
    installed = tmp_path / "site-packages" / "prompt_to_playlist" / "cli.py"
    monkeypatch.setattr(cli, "__file__", str(installed))
    assert cli._desktop_project_config() is None


@pytest.mark.parametrize("use_profile", [False, True])
def test_desktop_refuses_rules_before_reading_credentials(tmp_path, monkeypatch, capsys, use_profile):
    from prompt_to_playlist import config as settings
    monkeypatch.setattr(settings, "read_api_key", lambda *args: pytest.fail("Rules UI must not read credentials"))
    if use_profile:
        selected = tmp_path / "rules.toml"
        selected.write_text('schema_version="0.1.0"\nprovider="rules"\ncatalog="catalog.json"\n')
        arguments = ["--config", str(selected)]
    else:
        arguments = ["--provider", "rules"]
    assert main(["ui", "--catalog", str(CATALOG), *arguments]) == 2
    assert "prompt --provider rules" in capsys.readouterr().err


def test_generic_desktop_does_not_fall_back_without_openai_credentials(tmp_path, monkeypatch, capsys):
    from prompt_to_playlist import cli, desktop
    monkeypatch.setattr(cli, "_desktop_project_config", lambda: None)
    monkeypatch.setattr(desktop, "launch", lambda *args: pytest.fail("Misconfigured UI must not open"))
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_MODEL", raising=False)
    assert main(["ui", "--catalog", str(CATALOG)]) == 2
    assert "OpenAI requires" in capsys.readouterr().err


def test_catalog_coverage_and_initial_prompt_use_available_evidence():
    from prompt_to_playlist.adapters import load_catalog
    from prompt_to_playlist.desktop import catalog_coverage, initial_prompt
    catalog = load_catalog(CATALOG)
    assert "genre tags" in catalog_coverage(catalog)
    assert initial_prompt(catalog, rules=False) == "Find up to five tracks. Only include tracks tagged as house."


def test_existing_output_rejected_before_key_or_api_use(tmp_path, monkeypatch, capsys):
    from prompt_to_playlist import config as settings
    monkeypatch.setattr(settings, "read_api_key", lambda *args: pytest.fail("Should reject output before reading key"))
    destination = tmp_path / "existing.json"
    destination.write_text("preserve")
    assert main(["prompt", "--config", str(profile(tmp_path)), "--text", "house", "--out", str(destination)]) == 2
    assert destination.read_text() == "preserve"
    assert "already exists" in capsys.readouterr().err


@pytest.mark.parametrize("changed", ["source_hashes_unchanged", "source_inventory_unchanged"])
def test_changed_source_keeps_diagnostic_manifest_without_catalog(tmp_path, monkeypatch, capsys, changed):
    from pydantic import BaseModel
    from prompt_to_playlist import folder_catalog
    from prompt_to_playlist.models import Catalog
    class Manifest(BaseModel):
        source_hashes_unchanged: bool = True
        source_inventory_unchanged: bool = True
    manifest = Manifest(**{changed: False})
    monkeypatch.setattr(folder_catalog, "import_mp3_folder", lambda *args: (Catalog(catalog_id="test", tracks=[]), manifest))
    source = tmp_path / "collection"
    source.mkdir()
    target = tmp_path / "catalog.json"
    report = tmp_path / "manifest.json"
    assert main(["import-folder", "--folder", str(source), "--out", str(target), "--manifest", str(report)]) == 2
    assert not target.exists() and report.exists()
    assert "no catalog was published" in capsys.readouterr().err


def test_hidden_mp3_is_not_a_catalog_source(tmp_path, monkeypatch):
    from prompt_to_playlist import folder_catalog
    from prompt_to_playlist.vocabulary import load_vocabulary
    (tmp_path / ".hidden.mp3").write_bytes(b"not music")
    monkeypatch.setattr(folder_catalog, "_probe_file", lambda *args: pytest.fail("Hidden files must not be probed"))
    monkeypatch.setattr(folder_catalog.shutil, "which", lambda *args: "/fictional/ffprobe")
    with pytest.raises(ValueError):
        folder_catalog.import_mp3_folder(tmp_path, load_vocabulary())
