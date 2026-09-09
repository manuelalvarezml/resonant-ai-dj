"""Pure, bounded candidate retrieval. No music IO or model calls."""

import hashlib
import json

from .models import Catalog, CatalogTrack, PlaylistQuery, SearchResult, TrackMatch, Vocabulary
from .vocabulary import validate_query

USABLE = {"passed", "warning"}


def digest(value: dict) -> str:
    serialized = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def _validate_catalog(catalog: Catalog, vocabulary: Vocabulary) -> Catalog:
    catalog = Catalog.model_validate(catalog.model_dump())
    known = {item.id for item in vocabulary.descriptors}
    axes = {tag.split(":", 1)[0] for tag in known}
    for track in catalog.tracks:
        unknown = {item.tag for item in track.tags} - known
        if unknown:
            raise ValueError(f"Catalog contains unknown descriptors: {', '.join(sorted(unknown))}")
        if set(track.complete_tag_axes) - axes:
            raise ValueError("Catalog contains unknown complete_tag_axes")
    return catalog


def get_tracks(catalog: Catalog, track_ids: list[str]) -> list[CatalogTrack]:
    catalog = Catalog.model_validate(catalog.model_dump())
    if len(track_ids) > 100 or len(track_ids) != len(set(track_ids)):
        raise ValueError("Request up to 100 unique track IDs")
    indexed = {track.track_id: track for track in catalog.tracks}
    missing = set(track_ids) - indexed.keys()
    if missing:
        raise ValueError(f"Unknown track IDs: {', '.join(sorted(missing))}")
    return [indexed[track_id].model_copy(deep=True) for track_id in track_ids]


def search_tracks(catalog: Catalog, query: PlaylistQuery, vocabulary: Vocabulary) -> SearchResult:
    """All required constraints must be evidenced; never relax a hard filter."""
    query = validate_query(query, vocabulary)
    catalog = _validate_catalog(catalog, vocabulary)
    required = set(query.required_tags)
    preferred = set(query.preferred_tags)
    excluded = set(query.excluded_tags)
    requested = required | preferred
    banned_ids = set(query.excluded_track_ids)
    available_ids = {track.track_id for track in catalog.tracks}
    warnings = list(catalog.warnings)
    if banned_ids - available_ids:
        warnings.append("Some excluded track IDs are absent from this catalog.")
    usable_catalog_tags = {item.tag for track in catalog.tracks for item in track.tags if item.status in USABLE}
    missing_tags = requested - usable_catalog_tags
    if missing_tags:
        warnings.append("No usable catalog evidence for: " + ", ".join(sorted(missing_tags)))

    matches = []
    unknown_exclusion_count = 0
    unknown_bpm_count = 0
    for track in catalog.tracks:
        if track.track_id in banned_ids:
            continue
        tags = {item.tag for item in track.tags if item.status in USABLE}
        if required - tags or excluded & tags:
            continue
        # Absence of a label cannot prove a negative unless coverage is complete.
        excluded_axes = {tag.split(":", 1)[0] for tag in excluded}
        if excluded_axes - set(track.complete_tag_axes):
            unknown_exclusion_count += 1
            continue
        # A rejected annotation makes an asserted complete axis unusable.
        unusable_axes = {item.tag.split(":", 1)[0] for item in track.tags if item.status not in USABLE}
        if excluded_axes & unusable_axes:
            unknown_exclusion_count += 1
            continue
        bpm = track.bpm.value if track.bpm and track.bpm.status in USABLE else None
        if query.min_bpm is not None or query.max_bpm is not None:
            if bpm is None:
                unknown_bpm_count += 1
                continue
            if query.min_bpm is not None and bpm < query.min_bpm:
                continue
            if query.max_bpm is not None and bpm > query.max_bpm:
                continue
        matched = sorted(tags & requested)
        missing = sorted(preferred - tags)
        score = len(preferred & tags) / len(preferred) if preferred else (1.0 if required else 0.0)
        reasons = [f"Descriptor evidence: {tag}" for tag in matched]
        if query.min_bpm is not None or query.max_bpm is not None:
            reasons.append(f"BPM {bpm:g} within requested bounds ({track.bpm.authority}).")
        if excluded:
            reasons.append("Excluded descriptors absent on catalog-declared complete tag axes.")
        if missing:
            reasons.append("Preferred descriptors without usable evidence: " + ", ".join(missing))
        if not reasons:
            reasons.append("Eligible catalog candidate; no positive descriptor preference was requested.")
        if track.bpm and track.bpm.status == "warning":
            reasons.append("Tempo source reports a warning; BPM remains an estimate or supplied annotation.")
        matches.append(TrackMatch(track=track, score=round(score, 6), matched_tags=matched,
                                  missing_preferred_tags=missing, reasons=reasons))

    def sort_key(match: TrackMatch):
        track = match.track
        bpm = track.bpm.value if track.bpm and track.bpm.status in USABLE else None
        tie = (-match.score, track.track_id)
        if query.order == "relevance":
            return tie
        value = bpm if bpm is not None else 0.0
        if query.order == "bpm_descending":
            value = -value
        return (bpm is None, value, *tie)

    matches.sort(key=sort_key)
    eligible_count = len(matches)
    if unknown_exclusion_count:
        warnings.append(f"Excluded {unknown_exclusion_count} candidates because negative-tag evidence is incomplete.")
    if unknown_bpm_count:
        warnings.append(f"Excluded {unknown_bpm_count} candidates because usable BPM is missing.")
    if eligible_count < query.limit:
        warnings.append(f"Requested up to {query.limit} tracks; only {eligible_count} satisfy all hard constraints.")
    warnings.append("Scores measure descriptor coverage, not musical quality. Candidate order is not a validated DJ mix order.")
    if any(m.missing_preferred_tags for m in matches[:query.limit]):
        warnings.append("Some candidates do not satisfy every soft preference; inspect missing_preferred_tags.")
    data = dict(catalog_id=catalog.catalog_id, vocabulary_id=vocabulary.vocabulary_id,
                query=query, matches=matches[:query.limit], eligible_count=eligible_count,
                excluded_count=len(catalog.tracks) - eligible_count,
                warnings=list(dict.fromkeys(warnings)),
                catalog_digest=digest(catalog.model_dump(mode="json", by_alias=True)),
                vocabulary_digest=digest(vocabulary.model_dump(mode="json", by_alias=True)), result_id="pending")
    result = SearchResult(**data)
    hash_data = result.model_dump(mode="json", by_alias=True, exclude={"result_id"})
    result.result_id = "sha256:" + digest(hash_data)
    return result
