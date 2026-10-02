"""Explicit deterministic tool allowlist, shared by any future agent host."""

from typing import Annotated

from pydantic import Field

from .models import Catalog, PlaylistQuery, StrictModel, Vocabulary
from .search import get_tracks, search_tracks
from .vocabulary import normalize_descriptors


class NormalizeArguments(StrictModel):
    terms: list[Annotated[str, Field(min_length=1, max_length=100)]] = Field(max_length=50)


class SearchArguments(StrictModel):
    query: PlaylistQuery


class GetArguments(StrictModel):
    track_ids: list[Annotated[str, Field(min_length=1, max_length=500)]] = Field(max_length=100)


TOOLS = {
    "normalize_descriptors": (NormalizeArguments, "Resolve exact vocabulary aliases; this does not interpret free text."),
    "search_tracks": (SearchArguments, "Filter and rank only supplied catalog tracks using validated criteria."),
    "get_tracks": (GetArguments, "Return existing catalog tracks in the requested ID order."),
}


def list_tools() -> list[dict]:
    return [{"name": name, "version": "2" if name == "search_tracks" else "1", "description": description,
             "parameters": model.model_json_schema(), "read_only": True}
            for name, (model, description) in TOOLS.items()]


def dispatch_tool(name: str, args: dict, catalog: Catalog, vocabulary: Vocabulary) -> dict:
    if name not in TOOLS:
        raise ValueError(f"Unknown tool: {name}")
    arguments = TOOLS[name][0].model_validate(args)
    if name == "normalize_descriptors":
        return {"tags": normalize_descriptors(arguments.terms, vocabulary), "vocabulary_id": vocabulary.vocabulary_id}
    if name == "search_tracks":
        return search_tracks(catalog, arguments.query, vocabulary).model_dump(mode="json", by_alias=True)
    return {"tracks": [track.model_dump(mode="json") for track in get_tracks(catalog, arguments.track_ids)]}
