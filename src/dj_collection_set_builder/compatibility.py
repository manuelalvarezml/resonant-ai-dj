"""Deterministic harmonic, tempo, and transition scoring (Step 2A).

Scores are deterministic given their inputs. Key and tempo inputs remain
`benchmark_estimate` values from Step 1.
"""

from __future__ import annotations

from dj_collection_set_builder.constants import (
    AUTHORITY_DETERMINISTIC,
    HARMONIC_POLICY_DEFAULT,
    HARMONIC_POLICY_RELATED_1,
    HARMONIC_POLICY_RELATED_2,
    HARMONIC_POLICY_RELATED_3,
    HARMONIC_RULE_ID,
    HALF_DOUBLE_RATIO_TOLERANCE,
    LOOP_BAR_SIZES,
    STRETCH_MAX_PERCENT,
    STRETCH_PREFERRED_PERCENT,
    TRANSITION_WEIGHT_HARMONIC,
    TRANSITION_WEIGHT_LOUDNESS,
    TRANSITION_WEIGHT_PHRASE,
    TRANSITION_WEIGHT_TEMPO,
    WEAK_KEY_STRENGTH,
)
from dj_collection_set_builder.keys import camelot_code, normalize_mode, normalize_tonic
from dj_collection_set_builder.models import (
    HarmonicMatch,
    KeyAnalysis,
    TempoMatch,
    TrackAnalysis,
    TransitionScore,
)

Relationship = str

_COMPATIBLE_BY_POLICY = {
    HARMONIC_POLICY_RELATED_1: {"same", "relative"},
    HARMONIC_POLICY_RELATED_2: {"same", "relative", "adjacent_same_mode"},
    HARMONIC_POLICY_RELATED_3: {
        "same",
        "relative",
        "adjacent_same_mode",
        "related_3",
    },
}

_RAW_SCORES = {
    "same": 1.0,
    "relative": 0.9,
    "adjacent_same_mode": 0.85,
    "related_3": 0.55,
    "energy_plus_minus_2": 0.35,
    "incompatible": 0.0,
    "unknown": 0.0,
}


def parse_camelot(code: str | None) -> tuple[int, str] | None:
    if not code:
        return None
    token = code.strip().upper()
    if len(token) < 2 or token[-1] not in {"A", "B"}:
        return None
    try:
        number = int(token[:-1])
    except ValueError:
        return None
    if not 1 <= number <= 12:
        return None
    return number, token[-1]


def camelot_wheel_distance(left: int, right: int) -> int:
    raw = abs(left - right)
    return min(raw, 12 - raw)


def camelot_relationship(from_code: str, to_code: str) -> Relationship:
    parsed_from = parse_camelot(from_code)
    parsed_to = parse_camelot(to_code)
    if parsed_from is None or parsed_to is None:
        return "unknown"
    n1, l1 = parsed_from
    n2, l2 = parsed_to
    if n1 == n2 and l1 == l2:
        return "same"
    if n1 == n2:
        return "relative"
    distance = camelot_wheel_distance(n1, n2)
    if l1 == l2 and distance == 1:
        return "adjacent_same_mode"
    if l1 != l2 and distance == 1:
        return "related_3"
    if l1 == l2 and distance == 2:
        return "energy_plus_minus_2"
    return "incompatible"


def _camelot_from_key(value: KeyAnalysis | str | None) -> tuple[str | None, str | None, float | None]:
    if value is None:
        return None, None, None
    if isinstance(value, str):
        parsed = parse_camelot(value)
        if parsed:
            return f"{parsed[0]}{parsed[1]}", None, None
        parts = value.replace("_", " ").strip().split()
        if len(parts) >= 2:
            tonic = normalize_tonic(parts[0])
            mode = normalize_mode(parts[-1])
            if tonic and mode:
                return camelot_code(tonic, mode), f"{parts[0]} {parts[-1]}", None
        return None, value, None
    return value.camelot, value.standard_name, value.strength


def score_harmonic_match(
    from_key: KeyAnalysis | str | None,
    to_key: KeyAnalysis | str | None,
    *,
    policy: str = HARMONIC_POLICY_DEFAULT,
) -> HarmonicMatch:
    from_camelot, from_name, from_strength = _camelot_from_key(from_key)
    to_camelot, to_name, to_strength = _camelot_from_key(to_key)
    warnings: list[str] = [
        "Harmonic score is deterministic; source keys remain benchmark_estimate."
    ]
    if from_camelot is None or to_camelot is None:
        return HarmonicMatch(
            policy=policy,
            rule_id=HARMONIC_RULE_ID,
            from_camelot=from_camelot,
            to_camelot=to_camelot,
            from_standard_name=from_name,
            to_standard_name=to_name,
            relationship="unknown",
            compatible=False,
            score=0.0,
            confidence_adjusted_score=0.0,
            warnings=warnings + ["Missing Camelot code; cannot score a harmonic match."],
        )
    relationship = camelot_relationship(from_camelot, to_camelot)
    allowed = _COMPATIBLE_BY_POLICY.get(policy, _COMPATIBLE_BY_POLICY[HARMONIC_POLICY_DEFAULT])
    compatible = relationship in allowed
    score = _RAW_SCORES[relationship] if compatible else 0.0
    strengths = [item for item in (from_strength, to_strength) if item is not None]
    adjusted = score
    if strengths:
        weakest = min(strengths)
        if weakest < WEAK_KEY_STRENGTH:
            factor = max(0.3, weakest / WEAK_KEY_STRENGTH)
            adjusted = score * factor
            warnings.append(
                f"Weak key strength {weakest:.2f} reduced the confidence-adjusted score."
            )
    return HarmonicMatch(
        authority=AUTHORITY_DETERMINISTIC,
        policy=policy,
        rule_id=HARMONIC_RULE_ID,
        from_camelot=from_camelot,
        to_camelot=to_camelot,
        from_standard_name=from_name,
        to_standard_name=to_name,
        relationship=relationship,  # type: ignore[arg-type]
        compatible=compatible,
        score=score,
        confidence_adjusted_score=adjusted,
        warnings=warnings,
    )


def _bpm_of(track: TrackAnalysis | float | None) -> float | None:
    if track is None:
        return None
    if isinstance(track, (int, float)):
        value = float(track)
        return value if value > 0 else None
    value = track.tempo.selected_candidate.value
    if value is None:
        return None
    bpm = float(value)
    return bpm if bpm > 0 else None


def _story_direction(from_bpm: float, to_bpm: float) -> str:
    delta = to_bpm - from_bpm
    if abs(delta) < 0.2:
        return "flat"
    return "up" if delta > 0 else "down"


def score_tempo_match(
    from_bpm: TrackAnalysis | float | None,
    to_bpm: TrackAnalysis | float | None,
    *,
    stretch_policy: str = "prefer-2-allow-4",
    story_target: str | None = None,
) -> TempoMatch:
    source = _bpm_of(from_bpm)
    dest = _bpm_of(to_bpm)
    warnings = [
        "Tempo score is deterministic; BPM inputs remain benchmark_estimate."
    ]
    if source is None or dest is None:
        return TempoMatch(
            feasible=False,
            score=0.0,
            warnings=warnings + ["Missing BPM candidate; cannot score tempo."],
        )
    incoming_stretch = abs(source - dest) / dest * 100.0
    midpoint = (source + dest) / 2.0
    midpoint_stretch = max(
        abs(midpoint - source) / source * 100.0,
        abs(midpoint - dest) / dest * 100.0,
    )
    ratio = max(source, dest) / min(source, dest)
    half_double = abs(ratio - 2.0) <= HALF_DOUBLE_RATIO_TOLERANCE
    if half_double:
        warnings.append("Half/double tempo ambiguity detected; not auto-reinterpreted.")
    direction = _story_direction(source, dest)
    agreement: str = "unknown"
    if story_target in {"up", "down", "flat"}:
        agreement = direction if direction == story_target else "conflict"
        if agreement == "conflict":
            warnings.append(
                f"Story target {story_target} conflicts with tempo direction {direction}."
            )
    preferred = STRETCH_PREFERRED_PERCENT
    maximum = STRETCH_MAX_PERCENT
    if stretch_policy == "prefer-2-only":
        maximum = preferred
    feasible = incoming_stretch <= maximum + 1e-9 and not half_double
    if incoming_stretch <= preferred + 1e-9:
        score = 1.0
    elif incoming_stretch <= maximum + 1e-9:
        span = maximum - preferred
        score = 0.4 + 0.6 * (1.0 - (incoming_stretch - preferred) / span)
        warnings.append(
            f"Incoming stretch {incoming_stretch:.2f}% exceeds the preferred {preferred:g}%."
        )
    else:
        score = 0.0
        warnings.append(
            f"Incoming stretch {incoming_stretch:.2f}% exceeds the v1 maximum {maximum:g}%."
        )
    if half_double:
        feasible = False
        score = 0.0
    if agreement == "conflict":
        score *= 0.4
    return TempoMatch(
        from_bpm=source,
        to_bpm=dest,
        shared_bpm=source,
        incoming_stretch_percent=incoming_stretch,
        midpoint_stretch_percent=midpoint_stretch,
        half_double_ambiguity=half_double,
        story_direction=direction,  # type: ignore[arg-type]
        story_target=story_target,  # type: ignore[arg-type]
        story_agreement=agreement,  # type: ignore[arg-type]
        feasible=feasible,
        score=score,
        warnings=warnings,
    )


def _phrase_score(from_track: TrackAnalysis, to_track: TrackAnalysis) -> float:
    def usable_loops(track: TrackAnalysis) -> set[int]:
        usable = set()
        for loop in track.loop_candidates:
            if loop.bars in LOOP_BAR_SIZES and loop.status in {"passed", "warning"}:
                if not loop.crosses_novelty_boundary:
                    usable.add(loop.bars)
        return usable

    shared = usable_loops(from_track) & usable_loops(to_track)
    if 8 in shared or 16 in shared:
        return 1.0
    if shared:
        return 0.8
    if from_track.sections and to_track.sections:
        return 0.55
    return 0.3


def _loudness_score(from_track: TrackAnalysis, to_track: TrackAnalysis) -> float:
    left = from_track.loudness.integrated.value
    right = to_track.loudness.integrated.value
    if left is None or right is None:
        return 0.5
    delta = abs(float(left) - float(right))
    if delta <= 3:
        return 1.0
    if delta <= 6:
        return 0.75
    if delta <= 10:
        return 0.45
    return 0.2


def score_transition(
    from_track: TrackAnalysis,
    to_track: TrackAnalysis,
    *,
    policy: str = HARMONIC_POLICY_DEFAULT,
    stretch_policy: str = "prefer-2-allow-4",
    story_target: str | None = None,
) -> TransitionScore:
    harmonic = score_harmonic_match(from_track.key, to_track.key, policy=policy)
    tempo = score_tempo_match(
        from_track,
        to_track,
        stretch_policy=stretch_policy,
        story_target=story_target,
    )
    phrase = _phrase_score(from_track, to_track)
    loudness = _loudness_score(from_track, to_track)
    weights = {
        "harmonic": TRANSITION_WEIGHT_HARMONIC,
        "tempo": TRANSITION_WEIGHT_TEMPO,
        "phrase": TRANSITION_WEIGHT_PHRASE,
        "loudness": TRANSITION_WEIGHT_LOUDNESS,
    }
    harmonic_component = harmonic.confidence_adjusted_score
    score = (
        weights["harmonic"] * harmonic_component
        + weights["tempo"] * tempo.score
        + weights["phrase"] * phrase
        + weights["loudness"] * loudness
    )
    warnings = list(harmonic.warnings) + list(tempo.warnings)
    warnings.append(
        "Transition weights are an initial v1 choice (D033), not a listening-validated mix law."
    )
    if not harmonic.compatible:
        score = min(score, 0.15)
        warnings.append("Harmonic relationship is outside the active policy; transition capped.")
    return TransitionScore(
        from_track_id=from_track.source.track_id,
        to_track_id=to_track.source.track_id,
        harmonic=harmonic,
        tempo=tempo,
        phrase_score=phrase,
        loudness_score=loudness,
        score=round(score, 6),
        weights=weights,
        warnings=warnings,
    )
