"""Explicit project settings and non-executing, narrowly scoped key loading.

Configuration contains an environment variable name and an optional key source
path, never the key itself. Shell source files are read as data: only one exact
literal assignment is supported, and no shell code or substitutions are run.
"""

from __future__ import annotations

import os
from pathlib import Path
import re
import tomllib
from typing import Literal

from pydantic import ConfigDict, Field, ValidationError, field_validator, model_validator

from .models import StrictModel


class ConfigurationError(ValueError):
    """A configuration or credential error safe to display without secrets."""


class OpenAISettings(StrictModel):
    model_config = ConfigDict(hide_input_in_errors=True)

    model: str = Field(min_length=1, max_length=200)
    api_key_env: str = Field(
        default="AUTODJ_OPENAI_API_DEV_KEY", pattern=r"^[A-Za-z_][A-Za-z0-9_]*$",
        max_length=200,
    )
    key_source_file: str | None = Field(default=None, min_length=1)
    timeout_s: float = Field(default=30.0, gt=0, le=120)
    intent_reasoning_effort: Literal["none", "low", "medium", "high", "xhigh"] | None = None

    @field_validator("model", "key_source_file")
    @classmethod
    def not_blank(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("Setting must not be blank")
        return value


class ProjectConfig(StrictModel):
    model_config = ConfigDict(hide_input_in_errors=True)

    schema_version: Literal["0.1.0"] = "0.1.0"
    provider: Literal["rules", "openai"]
    catalog: str = Field(min_length=1)
    vocabulary: str | None = Field(default=None, min_length=1)
    openai: OpenAISettings | None = None

    @field_validator("catalog", "vocabulary")
    @classmethod
    def not_blank(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("Setting must not be blank")
        return value

    @model_validator(mode="after")
    def provider_settings(self) -> ProjectConfig:
        if self.provider == "openai" and self.openai is None:
            raise ValueError("OpenAI provider requires an openai settings table")
        return self


def _absolute_path(value: str, parent: Path) -> str:
    path = Path(value).expanduser()
    return str((path if path.is_absolute() else parent / path).resolve())


def load_project_config(path: Path) -> ProjectConfig:
    """Load strict TOML; resolve paths against the config file's directory.

    Neither this function nor model validation reads the credential source.
    Invalid TOML and validation errors intentionally omit their raw input.
    """
    try:
        config_path = path.expanduser().resolve()
        with config_path.open("rb") as handle:
            data = tomllib.load(handle)
        config = ProjectConfig.model_validate(data)
        config.catalog = _absolute_path(config.catalog, config_path.parent)
        if config.vocabulary is not None:
            config.vocabulary = _absolute_path(config.vocabulary, config_path.parent)
        if config.openai is not None and config.openai.key_source_file is not None:
            config.openai.key_source_file = _absolute_path(
                config.openai.key_source_file, config_path.parent,
            )
        return config
    except (OSError, UnicodeError, RuntimeError, ValueError, ValidationError):
        raise ConfigurationError(
            "Could not load project configuration; check the TOML file, supported "
            "fields, provider settings, and paths."
        ) from None


def _usable_key(value: str) -> bool:
    # HTTP authorization values must be a single nonempty printable token.
    # Reject shell substitutions even when quoted: the supported source grammar
    # intentionally permits literals only, with no interpolation or escaping.
    return bool(value) and all(33 <= ord(char) <= 126 for char in value) and not any(
        char in value for char in "$`\\\"'"
    )


def _literal_assignment(rhs: str) -> str:
    rhs = rhs.strip()
    if rhs.startswith(("'", '"')):
        quote = rhs[0]
        end = rhs.find(quote, 1)
        if end < 0:
            raise ConfigurationError("API key assignment must contain one literal value.")
        value = rhs[1:end]
        remainder = rhs[end + 1:].strip()
        if remainder and not remainder.startswith("#"):
            raise ConfigurationError("API key assignment must contain one literal value.")
    else:
        # A shell comment starts after whitespace, not inside an unquoted word.
        parts = rhs.split(maxsplit=1)
        value = parts[0] if parts else ""
        if len(parts) == 2 and not parts[1].startswith("#"):
            raise ConfigurationError("API key assignment must contain one literal value.")
        # Shell control characters may not be interpreted as key characters.
        if any(char in value for char in ";&|<>(){}[]*?!~"):
            raise ConfigurationError("API key assignment must contain one literal value.")
    if not _usable_key(value):
        raise ConfigurationError("API key assignment must contain one literal value.")
    return value


def read_api_key(settings: OpenAISettings) -> str:
    """Read only the configured variable or its explicit literal source.

    The named nonempty environment variable takes precedence. There is no
    generic OPENAI_API_KEY fallback, automatic shell-file discovery, shell
    execution, variable expansion, or modification of the user's files.
    """
    try:
        # Revalidate in case a caller bypassed validation with model_construct.
        settings = OpenAISettings.model_validate(settings.model_dump())
    except (AttributeError, ValidationError):
        raise ConfigurationError("OpenAI settings are invalid.") from None

    value = os.environ.get(settings.api_key_env)
    if value:
        if not _usable_key(value):
            raise ConfigurationError("Configured API key environment value is invalid.")
        return value
    if settings.key_source_file is None:
        raise ConfigurationError(
            "Configured API key is missing; set its environment variable or an "
            "explicit key_source_file."
        )

    pattern = re.compile(
        rf"^[ \t]*(?:export[ \t]+)?{re.escape(settings.api_key_env)}[ \t]*=(.*)$"
    )
    try:
        with Path(settings.key_source_file).expanduser().open(encoding="utf-8") as handle:
            assignments = [match.group(1) for line in handle
                           if (match := pattern.fullmatch(line.rstrip("\r\n")))]
    except (OSError, UnicodeError, RuntimeError, ValueError):
        raise ConfigurationError("Could not read configured API key source file.") from None

    if not assignments:
        raise ConfigurationError("Configured API key assignment was not found in its source file.")
    if len(assignments) != 1:
        raise ConfigurationError("Configured API key source has multiple assignments; use exactly one.")
    return _literal_assignment(assignments[0])
