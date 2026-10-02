"""Versioned probability-aware ranking; hard eligibility precedes soft scoring."""
from .models import Preference, ScoreContribution, SearchResult, TrackMatch
from .taxonomy import VERSION as TAXONOMY_VERSION

VERSION = "maest-intent-v1"
IMPORTANCE = {"primary": 3, "secondary": 2, "optional": 1}
USABLE = {"passed", "warning"}


def evidence(track, tag, scope):
    candidates = []
    for item in track.tags:
        if item.status not in USABLE:
            continue
        if item.tag == tag or (scope == "taxonomy" and tag in item.parent_tags):
            # MAEST sigmoid outputs are independent support scores, not a softmax.
            is_maest = "maest" in item.source.casefold()
            value = item.confidence if is_maest else 1.0
            if value is not None:
                candidates.append((value, item.source + (f" [{item.source_label}]" if item.source_label else "")))
    numeric = track.preference_scores.get(tag)
    if numeric and numeric.status in USABLE and 0 <= numeric.value <= 1:
        candidates.append((numeric.value, numeric.source))
    return max(candidates, key=lambda item: (item[0], item[1])) if candidates else (None, None)


def positive_tags(track, scope):
    tags = set()
    for item in track.tags:
        if item.status in USABLE:
            tags.add(item.tag)
            if scope == "taxonomy":
                tags.update(item.parent_tags)
    return tags


def rank_tracks(catalog, query, vocabulary):
    from .search import digest
    warnings = list(catalog.warnings)
    # Required genre groups contribute independently; an OR group uses max support.
    genres = [([tag], "increase", "explicit", 3) for tag in query.required_tags if tag.startswith("genre:")]
    genres += [(group, "increase", "explicit", 3) for group in query.any_tag_groups]
    preferences = [*query.preferences, *(Preference(tag=t) for t in query.preferred_tags)]
    objectives = [(tags, direction, origin, importance, "genre") for tags, direction, origin, importance in genres]
    for pref in preferences:
        # A required genre already has a scoring objective.
        if pref.tag in query.required_tags and pref.tag.startswith("genre:") and pref.direction == "increase":
            continue
        objectives.append(([pref.tag], pref.direction, pref.origin, IMPORTANCE[pref.importance],
                           "genre" if pref.tag.startswith("genre:") and pref.origin == "explicit" else "preference"))
    available = []
    for objective in objectives:
        if any(evidence(t, tag, query.genre_scope)[0] is not None for t in catalog.tracks for tag in objective[0]):
            available.append(objective)
        else:
            warnings.append("No usable catalog evidence for soft scoring: " + ", ".join(objective[0]))
    totals = {group: sum(o[3] for o in available if o[4] == group) for group in ("genre", "preference")}
    if all(totals.values()):
        blend = {"genre": .65, "preference": .35}
    else:
        blend = {group: 1.0 if total else 0.0 for group, total in totals.items()}
    matches = []
    unknown_negative = unknown_bpm = 0
    banned = set(query.excluded_track_ids)
    if banned - {t.track_id for t in catalog.tracks}:
        warnings.append("Some excluded track IDs are absent from this catalog.")
    for track in catalog.tracks:
        tags = positive_tags(track, query.genre_scope)
        if track.track_id in banned or not set(query.required_tags) <= tags:
            continue
        if any(not tags.intersection(group) for group in query.any_tag_groups):
            continue
        if tags.intersection(query.excluded_tags):
            continue
        axes = {t.split(":", 1)[0] for t in query.excluded_tags}
        invalid = {e.tag.split(":", 1)[0] for e in track.tags if e.status not in USABLE}
        if axes - set(track.complete_tag_axes) or axes & invalid:
            unknown_negative += 1
            continue
        bpm = track.bpm.value if track.bpm and track.bpm.status in USABLE else None
        if query.min_bpm is not None or query.max_bpm is not None:
            if bpm is None:
                unknown_bpm += 1
                continue
            if query.min_bpm is not None and bpm < query.min_bpm or query.max_bpm is not None and bpm > query.max_bpm:
                continue
        contributions, missing, matched = [], [], set(query.required_tags)
        for group_tags, direction, origin, importance, group in available:
            values = [evidence(track, tag, query.genre_scope) for tag in group_tags]
            usable = [(v, s) for v, s in values if v is not None]
            value, source = max(usable, key=lambda x: (x[0], x[1])) if usable else (None, None)
            # Missing is unknown, including for decrease objectives: never reward it.
            utility = 0.0 if value is None else (value if direction == "increase" else 1 - value)
            weight = blend[group] * importance / totals[group]
            contributions.append(ScoreContribution(tags=group_tags, group=group, direction=direction,
                origin=origin, evidence_value=value, utility=utility, weight=weight,
                contribution=utility * weight, source=source))
            if value is None:
                missing.extend(group_tags)
            else:
                matched.update(tag for tag, (v, _) in zip(group_tags, values) if v is not None)
        reasons = [f"{c.direction} {' or '.join(c.tags)}: " +
                   ("unknown evidence; no credit" if c.evidence_value is None else f"support {c.evidence_value:.4f}, weight {c.weight:.4f}, contribution {c.contribution:.4f}")
                   for c in contributions]
        if query.min_bpm is not None or query.max_bpm is not None:
            reasons.append(f"Estimated BPM {bpm:g} satisfies explicit bounds.")
        if query.excluded_tags:
            reasons.append("Excluded descriptors absent on catalog-declared complete axes.")
        if not reasons:
            reasons.append("Eligible candidate; no usable positive scoring evidence. Stable ID order breaks ties.")
        matches.append(TrackMatch(track=track, score=round(min(1.0, sum(c.contribution for c in contributions)), 6),
            matched_tags=sorted(matched), missing_preferred_tags=sorted(set(missing)),
            reasons=reasons, score_contributions=contributions))
    from .semantic_ranking import fuse, gate_expanded_objectives, VERSION as HYBRID_VERSION
    warnings.extend(gate_expanded_objectives(matches))
    hybrid, semantic_warnings = fuse(matches, query)
    warnings.extend(semantic_warnings)
    def sort_key(match):
        bpm = match.track.bpm.value if match.track.bpm and match.track.bpm.status in USABLE else None
        tie = (-match.score, match.track.track_id)
        if query.order == "relevance":
            return tie
        return (bpm is None, (bpm or 0) * (-1 if query.order == "bpm_descending" else 1), *tie)
    for match in matches:
        preserved=[r for r in match.reasons if not r.startswith(('increase ', 'decrease '))]
        match.reasons=[f"{c.direction} {' or '.join(c.tags)}: " + ("unknown evidence; no credit" if c.evidence_value is None else f"evidence {c.evidence_value:.4f}, weight {c.weight:.4f}, contribution {c.contribution:.4f}") for c in match.score_contributions] + preserved
    matches.sort(key=sort_key)
    if unknown_negative:
        warnings.append(f"Excluded {unknown_negative} candidates because negative-tag evidence is incomplete.")
    if unknown_bpm:
        warnings.append(f"Excluded {unknown_bpm} candidates because usable BPM is missing.")
    if len(matches) < query.limit:
        warnings.append(f"Requested up to {query.limit} tracks; only {len(matches)} satisfy all hard constraints.")
    warnings.append("Scores measure estimated musical fit, not calibrated probabilities or listening quality. The 65/35 genre-feature blend and 3/2/1 priorities are provisional. Order is not a DJ mix plan.")
    result = SearchResult(catalog_id=catalog.catalog_id, vocabulary_id=vocabulary.vocabulary_id,
        query=query, ranking_version=HYBRID_VERSION if hybrid else VERSION, taxonomy_version=TAXONOMY_VERSION if query.genre_scope == "taxonomy" else None,
        matches=matches[:query.limit], eligible_count=len(matches), eligible_track_ids=[m.track.track_id for m in matches],
        excluded_count=len(catalog.tracks)-len(matches), warnings=list(dict.fromkeys(warnings)),
        catalog_digest=digest(catalog.model_dump(mode="json", by_alias=True)),
        vocabulary_digest=digest(vocabulary.model_dump(mode="json", by_alias=True)), result_id="pending")
    result.result_id = "sha256:" + digest(result.model_dump(mode="json", by_alias=True, exclude={"result_id"}))
    return result
