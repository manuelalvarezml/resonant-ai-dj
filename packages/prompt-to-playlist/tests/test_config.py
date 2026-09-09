"""Configuration tests use temporary files and fake credentials only."""

from __future__ import annotations

from pathlib import Path

from pydantic import ValidationError
import pytest

from prompt_to_playlist.config import (
    ConfigurationError, OpenAISettings, ProjectConfig, load_project_config, read_api_key,
)


KEY_ENV = "AUTODJ_OPENAI_API_DEV_KEY"
FAKE_KEY = "sk-test-only-not-a-credential_123"


@pytest.fixture(autouse=True)
def isolate_environment(monkeypatch):
    monkeypatch.delenv(KEY_ENV, raising=False)
    monkeypatch.delenv("PLAYLIST_TEST_KEY", raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "unrelated-generic-key")


def settings(source: Path | None = None, **kwargs) -> OpenAISettings:
    return OpenAISettings(model="explicit-test-model", key_source_file=str(source) if source else None, **kwargs)


def write_source(tmp_path: Path, content: str) -> Path:
    source = tmp_path / "fake-zshrc"
    source.write_text(content, encoding="utf-8")
    return source


@pytest.mark.parametrize("prefix", ["", "export ", " \texport\t"])
@pytest.mark.parametrize("rhs", [FAKE_KEY, f"'{FAKE_KEY}'", f'"{FAKE_KEY}"'])
@pytest.mark.parametrize("comment", ["", " # explanatory comment; $UNRELATED `ignored`"])
def test_literal_key_assignment(tmp_path, prefix, rhs, comment):
    source = write_source(tmp_path, f"{prefix}{KEY_ENV} = {rhs}{comment}\r\n")
    before = source.read_bytes()
    assert read_api_key(settings(source)) == FAKE_KEY
    assert source.read_bytes() == before


def test_quoted_key_can_have_adjacent_comment(tmp_path):
    source = write_source(tmp_path, f'{KEY_ENV}="{FAKE_KEY}"#comment\n')
    assert read_api_key(settings(source)) == FAKE_KEY


def test_only_exact_named_assignment_is_read(tmp_path):
    source = write_source(tmp_path, (
        f"# {KEY_ENV}=ignored-comment\n"
        "OPENAI_API_KEY=unrelated-source-key\n"
        f"OTHER_{KEY_ENV}=ignored-prefix\n"
        f"{KEY_ENV}_OTHER=ignored-suffix\n"
        "alias demo='nothing to execute'\n"
        f"{KEY_ENV}={FAKE_KEY}\n"
    ))
    assert read_api_key(settings(source)) == FAKE_KEY


def test_named_environment_precedes_even_invalid_source(monkeypatch, tmp_path):
    source = write_source(tmp_path, f"{KEY_ENV}=$(dangerous-command)\n")
    monkeypatch.setenv(KEY_ENV, FAKE_KEY)
    assert read_api_key(settings(source)) == FAKE_KEY
    assert read_api_key(settings(tmp_path / "nonexistent")) == FAKE_KEY


def test_custom_environment_is_explicit(monkeypatch, tmp_path):
    monkeypatch.setenv(KEY_ENV, "wrong-project-key")
    monkeypatch.setenv("PLAYLIST_TEST_KEY", FAKE_KEY)
    assert read_api_key(settings(api_key_env="PLAYLIST_TEST_KEY")) == FAKE_KEY


def test_empty_environment_can_use_explicit_file(monkeypatch, tmp_path):
    monkeypatch.setenv(KEY_ENV, "")
    source = write_source(tmp_path, f"{KEY_ENV}={FAKE_KEY}\n")
    assert read_api_key(settings(source)) == FAKE_KEY


@pytest.mark.parametrize("value", [" ", "key\nheader", "${OTHER}", "$(command)"])
def test_invalid_nonempty_environment_is_not_silently_overridden(monkeypatch, tmp_path, value):
    source = write_source(tmp_path, f"{KEY_ENV}={FAKE_KEY}\n")
    monkeypatch.setenv(KEY_ENV, value)
    with pytest.raises(ConfigurationError, match="environment value is invalid") as error:
        read_api_key(settings(source))
    assert value not in str(error.value) or value == " "


def test_missing_project_key_has_no_generic_environment_fallback():
    with pytest.raises(ConfigurationError, match="missing"):
        read_api_key(settings())


@pytest.mark.parametrize("body", ["", "OPENAI_API_KEY=unrelated\n", f"# {KEY_ENV}=commented\n"])
def test_missing_literal_assignment(tmp_path, body):
    with pytest.raises(ConfigurationError, match="not found"):
        read_api_key(settings(write_source(tmp_path, body)))


@pytest.mark.parametrize("other", [FAKE_KEY, "different-fake-key", "$(command)"])
def test_multiple_assignments_rejected_even_if_identical(tmp_path, other):
    source = write_source(tmp_path, f"{KEY_ENV}={FAKE_KEY}\nexport {KEY_ENV}={other}\n")
    with pytest.raises(ConfigurationError, match="multiple assignments") as error:
        read_api_key(settings(source))
    assert FAKE_KEY not in str(error.value)
    assert other not in str(error.value)


@pytest.mark.parametrize("rhs", [
    "", "''", '""', "${OTHER}", '"${OTHER}"', "'$OTHER'", "$(touch MARKER)",
    '"$(touch MARKER)"', "`touch MARKER`", "'`touch MARKER`'", "key;touch MARKER",
    "key && touch MARKER", "key | command", "key > MARKER", "key<file", "key;",
    '"key"; touch MARKER', "'key' EXTRA=other", "key other", "'unterminated",
    '"unterminated', "key\\", "key\\ value", '"key\\value"', "'key with space'",
    "key$(command)", "key\x00value", "key\x1fvalue", "key*", "key?", "~key",
])
def test_nonliteral_values_rejected_without_execution_or_leaks(tmp_path, rhs):
    marker = tmp_path / "would-exist-if-executed"
    rhs = rhs.replace("MARKER", str(marker))
    source = write_source(tmp_path, f"{KEY_ENV}={rhs}\n")
    with pytest.raises(ConfigurationError, match="literal value") as error:
        read_api_key(settings(source))
    assert not marker.exists()
    if rhs:
        assert rhs not in str(error.value)
    assert str(marker) not in str(error.value)


def test_unrelated_shell_commands_are_never_executed(tmp_path):
    marker = tmp_path / "unrelated-command-marker"
    source = write_source(tmp_path, f"touch '{marker}'\n{KEY_ENV}={FAKE_KEY}\n")
    assert read_api_key(settings(source)) == FAKE_KEY
    assert not marker.exists()


def test_unreadable_or_non_utf8_source_is_redacted(tmp_path):
    missing = tmp_path / "sensitive-source-name"
    with pytest.raises(ConfigurationError, match="Could not read") as error:
        read_api_key(settings(missing))
    assert str(missing) not in str(error.value)
    source = write_source(tmp_path, "")
    source.write_bytes(b"\xff")
    with pytest.raises(ConfigurationError, match="Could not read"):
        read_api_key(settings(source))


@pytest.mark.parametrize("name", ["", "NAME WITH SPACE", "1NAME", "NAME;CMD", "NAME\n", "NAME$(command)"])
def test_key_environment_name_is_a_strict_identifier(name):
    with pytest.raises(ValidationError):
        settings(api_key_env=name)


@pytest.mark.parametrize("timeout", [0.0, -1.0, 120.1, float("inf"), float("nan"), "30"])
def test_timeout_is_strict_and_bounded(timeout):
    with pytest.raises(ValidationError):
        settings(timeout_s=timeout)


@pytest.mark.parametrize("model", ["", " ", 123])
def test_model_must_be_explicit_and_nonblank(model):
    with pytest.raises(ValidationError):
        OpenAISettings(model=model)


def test_project_requires_openai_settings_for_openai_provider():
    with pytest.raises(ValidationError, match="requires an openai settings table"):
        ProjectConfig(provider="openai", catalog="catalog.json")
    assert ProjectConfig(provider="rules", catalog="catalog.json").openai is None


def test_config_path_resolution_and_explicit_values(tmp_path):
    config_dir = tmp_path / "project"
    config_dir.mkdir()
    source = config_dir / "playlist.toml"
    source.write_text('''schema_version = "0.1.0"
provider = "openai"
catalog = "output/pool.json"
vocabulary = "../vocabulary.json"
[openai]
model = "configured-test-model"
key_source_file = "~/.fake-zshrc"
timeout_s = 45.0
''', encoding="utf-8")
    config = load_project_config(source)
    assert config.catalog == str(config_dir / "output" / "pool.json")
    assert config.vocabulary == str(tmp_path / "vocabulary.json")
    assert config.openai.key_source_file == str(Path("~/.fake-zshrc").expanduser())
    assert config.openai.model == "configured-test-model"
    assert config.openai.api_key_env == KEY_ENV
    assert config.openai.timeout_s == 45.0
    assert FAKE_KEY not in repr(config)


def test_relative_key_source_is_config_relative(tmp_path):
    source = tmp_path / "playlist.toml"
    source.write_text('''provider = "openai"
catalog = "catalog.json"
[openai]
model = "configured-test-model"
key_source_file = "secrets/fake-zshrc"
''', encoding="utf-8")
    config = load_project_config(source)
    assert config.openai.key_source_file == str(tmp_path / "secrets" / "fake-zshrc")


def test_config_loader_never_reads_secret_source(tmp_path):
    source = tmp_path / "playlist.toml"
    source.write_text('''provider = "openai"
catalog = "catalog.json"
[openai]
model = "configured-test-model"
key_source_file = "missing-source"
''', encoding="utf-8")
    assert load_project_config(source).openai.key_source_file.endswith("missing-source")


@pytest.mark.parametrize("content", [
    f'provider = "rules"\ncatalog = "catalog.json"\napi_key = "{FAKE_KEY}"\n',
    f'provider = "rules"\ncatalog = "catalog.json"\n[openai]\nmodel = "test"\napi_key = "{FAKE_KEY}"\n',
    f'provider = "{FAKE_KEY}"\ncatalog = "catalog.json"\n',
    f'provider = "rules"\ncatalog = "{FAKE_KEY}',
    'provider = "openai"\ncatalog = "catalog.json"\n',
    'schema_version = "9.0"\nprovider = "rules"\ncatalog = "catalog.json"\n',
    'provider = "rules"\n',
    'provider = "rules"\ncatalog = " "\n',
])
def test_config_errors_are_redacted_and_strict(tmp_path, content):
    source = tmp_path / "playlist.toml"
    source.write_text(content, encoding="utf-8")
    with pytest.raises(ConfigurationError, match="Could not load project configuration") as error:
        load_project_config(source)
    assert FAKE_KEY not in str(error.value)
    assert error.value.__suppress_context__ is True


def test_missing_config_is_redacted(tmp_path):
    source = tmp_path / "sensitive-config-name"
    with pytest.raises(ConfigurationError) as error:
        load_project_config(source)
    assert str(source) not in str(error.value)


def test_direct_settings_validation_errors_hide_raw_values():
    with pytest.raises(ValidationError) as error:
        OpenAISettings(model="test", api_key=FAKE_KEY)
    assert FAKE_KEY not in str(error.value)
