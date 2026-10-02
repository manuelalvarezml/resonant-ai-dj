"""Small, editable descriptor vocabulary; never derives tags from audio."""

from importlib.resources import files
from pathlib import Path

from .models import PlaylistQuery, Vocabulary


def load_vocabulary(path: Path | None = None) -> Vocabulary:
    source = path if path is not None else files("prompt_to_playlist").joinpath("descriptors.json")
    return Vocabulary.model_validate_json(source.read_text(encoding="utf-8"))


def normalize_descriptors(terms: list[str], vocabulary: Vocabulary) -> list[str]:
    """Resolve exact aliases (case-insensitive), rejecting unknown terms."""
    vocabulary = Vocabulary.model_validate(vocabulary.model_dump())
    lookup = {term.strip().casefold(): item.id for item in vocabulary.descriptors
              for term in [item.id, *item.aliases]}
    result = []
    for term in terms:
        key = term.strip().casefold()
        if key not in lookup:
            raise ValueError(f"Unknown descriptor: {term}")
        if lookup[key] not in result:
            result.append(lookup[key])
    return result


def validate_query(query: PlaylistQuery, vocabulary: Vocabulary) -> PlaylistQuery:
    # Revalidate at the tool boundary, including models mutated by callers.
    vocabulary = Vocabulary.model_validate(vocabulary.model_dump())
    query = PlaylistQuery.model_validate(query.model_dump())
    known = {item.id for item in vocabulary.descriptors}
    requested = set(query.required_tags + query.preferred_tags + query.excluded_tags)
    requested.update(t for group in query.any_tag_groups for t in group)
    requested.update(p.tag for p in query.preferences)
    if requested - known:
        raise ValueError(f"Unknown descriptor IDs: {', '.join(sorted(requested - known))}")
    return query
