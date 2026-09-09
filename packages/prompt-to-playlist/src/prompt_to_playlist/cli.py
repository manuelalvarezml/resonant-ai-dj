"""Small JSON-first command line interface for the reusable playlist module."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from pydantic import BaseModel, RootModel


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Translate a set description into a validated catalog playlist.")
    commands = parser.add_subparsers(dest="command", required=True)
    vocab = commands.add_parser("vocabulary", help="Print the supported descriptors")
    vocab.add_argument("--vocabulary", type=Path)
    tool = commands.add_parser("tools", help="Print deterministic tool definitions")
    importer = commands.add_parser("import-dj", help="Import stored DJ JSON without reading audio")
    importer.add_argument("--analysis", required=True, type=Path)
    importer.add_argument("--out", required=True, type=Path)
    folder = commands.add_parser("import-folder", help="Read MP3 folder metadata and hashes without running audio analysis")
    folder.add_argument("--folder", required=True, type=Path)
    folder.add_argument("--out", required=True, type=Path)
    folder.add_argument("--manifest", required=True, type=Path)
    folder.add_argument("--vocabulary", type=Path)
    search = commands.add_parser("search", help="Search a catalog with a validated JSON query")
    search.add_argument("--catalog", type=Path)
    search.add_argument("--query", required=True, type=Path, help="Path to a PlaylistQuery JSON file")
    search.add_argument("--vocabulary", type=Path)
    prompt = commands.add_parser("prompt", help="Build a playlist from a text description")
    prompt.add_argument("--catalog", type=Path)
    prompt.add_argument("--text", help="Description; when omitted, ask interactively")
    prompt.add_argument("--provider", choices=("rules", "openai"),
                        help="Default: OpenAI. Select rules only for the offline developer clause grammar.")
    prompt.add_argument("--vocabulary", type=Path)
    desktop = commands.add_parser("ui", help="Open the OpenAI natural-language playlist form")
    desktop.add_argument("--catalog", type=Path)
    desktop.add_argument("--provider", metavar="openai", help="The desktop form supports OpenAI natural language only.")
    desktop.add_argument("--vocabulary", type=Path)
    for command in (search, prompt, desktop):
        command.add_argument(
            "--config", type=Path,
            help=("TOML project profile; UI defaults to playlist.toml in the current directory "
                  "or this editable package checkout. Other commands require an explicit profile."),
        )
    for command in (vocab, tool, search, prompt):
        command.add_argument("--out", type=Path, help="Write a new JSON file; default is standard output")
    return parser


def _emit(value: BaseModel | list[dict], path: Path | None) -> None:
    from .adapters import save_json

    model = value if isinstance(value, BaseModel) else RootModel[list[dict]](value)
    if path is None:
        print(model.model_dump_json(by_alias=True, indent=2))
    else:
        save_json(model, path)


def _desktop_project_config() -> Path | None:
    """Find only an immediate local profile or this editable checkout's profile.

    A wheel installation has no implicit project profile. Never scan ancestors
    or the user's home directory, and never skip an invalid selected profile.
    """
    local = Path.cwd() / "playlist.toml"
    if local.is_file():
        return local
    source = Path(__file__).resolve()
    checkout = source.parents[2]
    editable_source = checkout / "src" / "prompt_to_playlist" / "cli.py"
    candidate = checkout / "playlist.toml"
    if editable_source == source and (checkout / "pyproject.toml").is_file() and candidate.is_file():
        return candidate
    return None


def main(argv: Sequence[str] | None = None) -> int:
    """Return 0 for valid results (including no matches), or 2 for bad input."""
    args = _parser().parse_args(argv)
    try:
        from .adapters import from_dj_collection, load_catalog
        from .models import PlaylistQuery
        from .search import search_tracks
        from .service import build_playlist
        from .tools import list_tools
        from .translators import OpenAITranslator, RulesTranslator
        from .vocabulary import load_vocabulary

        if args.command == "prompt" and args.out is not None:
            from .adapters import _safe_output_path
            _safe_output_path(args.out)

        config = None
        config_path = getattr(args, "config", None)
        if args.command == "ui":
            if args.provider is not None and args.provider != "openai":
                raise ValueError("The playlist interface uses OpenAI for natural language. "
                                 "Offline developer parsing is available with prompt --provider rules.")
            config_path = config_path or _desktop_project_config()
        if config_path is not None:
            from .config import load_project_config
            config = load_project_config(config_path)
        if args.command in {"search", "prompt", "ui"}:
            args.catalog = args.catalog or (Path(config.catalog) if config else None)
            if args.catalog is None:
                raise ValueError("Provide --catalog or --config with a catalog path.")
            args.vocabulary = args.vocabulary or (Path(config.vocabulary) if config and config.vocabulary else None)
        if args.command in {"prompt", "ui"}:
            args.provider = args.provider or (config.provider if config else "openai")
            if args.command == "ui" and args.provider != "openai":
                raise ValueError("The playlist interface needs an OpenAI profile. "
                                 "Offline developer parsing is available with prompt --provider rules.")

        def make_translator():
            if args.provider == "rules":
                return RulesTranslator()
            if config is not None:
                from .config import read_api_key
                if config.openai is None:
                    raise ValueError("The selected profile has no OpenAI settings.")
                return OpenAITranslator(api_key=read_api_key(config.openai), model=config.openai.model,
                                        timeout_s=config.openai.timeout_s)
            return OpenAITranslator()

        if args.command == "import-dj":
            data = json.loads(args.analysis.read_text(encoding="utf-8"))
            _emit(from_dj_collection(data), args.out)
        elif args.command == "import-folder":
            from .adapters import _safe_output_path
            from .folder_catalog import import_mp3_folder
            if args.out.resolve() == args.manifest.resolve():
                raise ValueError("Catalog and manifest need different output paths.")
            for output in (args.out, args.manifest):
                if output.resolve().is_relative_to(args.folder.resolve()):
                    raise ValueError("Output must be outside the selected music folder.")
                _safe_output_path(output)
            catalog, manifest = import_mp3_folder(args.folder, load_vocabulary(args.vocabulary))
            _emit(manifest, args.manifest)
            if not manifest.source_hashes_unchanged or not manifest.source_inventory_unchanged:
                raise ValueError("Source files changed during import. A diagnostic manifest was saved; no catalog was published.")
            _emit(catalog, args.out)
        elif args.command == "tools":
            _emit(list_tools(), args.out)
        else:
            vocabulary = load_vocabulary(args.vocabulary)
            if args.command == "vocabulary":
                _emit(vocabulary, args.out)
            else:
                catalog = load_catalog(args.catalog)
                if args.command == "search":
                    query = PlaylistQuery.model_validate_json(args.query.read_text(encoding="utf-8"))
                    result = search_tracks(catalog, query, vocabulary)
                elif args.command == "ui":
                    from .desktop import launch
                    translator = make_translator()
                    launch(catalog, vocabulary, translator)
                    return 0
                else:
                    prompt = args.text
                    if prompt is None:
                        if args.provider == "rules":
                            print(
                                "Rules grammar: require house; prefer dark; exclude vocal; bpm 120-130; count 5",
                                file=sys.stderr,
                            )
                        print("Describe your set: ", end="", file=sys.stderr, flush=True)
                        prompt = input()
                    translator = make_translator()
                    result = build_playlist(prompt, catalog, vocabulary, translator)
                _emit(result, args.out)
    except (ValueError, OSError, EOFError) as exc:
        print(f"prompt-playlist: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
