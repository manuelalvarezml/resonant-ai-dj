"""Pydantic models matching docs/SCHEMAS.md."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from dj_collection_set_builder.constants import (
    AUTHORITY_DETERMINISTIC,
    AUTHORITY_ENCODED_FACT,
    AUTHORITY_ESTIMATE,
    AUTHORITY_STANDARDIZED,
    COLLECTION_SCHEMA,
    MIX_BRIEF_SCHEMA,
    MIX_PLAN_SCHEMA,
    RENDER_MANIFEST_SCHEMA,
    SCHEMA_VERSION,
    STATUS_FAILED,
    STATUS_NOT_RUN,
    STATUS_UNKNOWN,
    TRACK_SCHEMA,
)

Authority = Literal[
    "encoded_fact",
    "standardized_measurement",
    "deterministic_measurement",
    "benchmark_estimate",
    "user_verified",
    "llm_proposal",
    "executed_action",
]

Status = Literal["passed", "warning", "rejected", "unknown", "not_run", "failed"]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class FeatureValue(StrictModel):
    value: Any = None
    unit: str | None = None
    authority: Authority
    status: Status
    source_tool: str | None = None
    tool_version: str | None = None
    model_id: str | None = None
    confidence: float | None = None
    parameters: dict[str, Any] = Field(default_factory=dict)
    validator: dict[str, Any] | None = None
    warnings: list[str] = Field(default_factory=list)


class TrackSource(StrictModel):
    track_id: str
    path: str
    filename: str
    size_bytes: int
    sha256_before: str
    sha256_after: str | None = None
    source_unchanged: bool | None = None


class StreamFacts(StrictModel):
    authority: Authority = AUTHORITY_ENCODED_FACT
    status: Status = STATUS_UNKNOWN
    probe_tool: str = "ffprobe"
    probe_version: str | None = None
    codec: str | None = None
    sample_rate_hz: int | None = None
    channels: int | None = None
    channel_layout: str | None = None
    bit_rate_bps: int | None = None
    bit_rate_mode: str | None = None
    duration_s: float | None = None
    decode_health: Status = STATUS_NOT_RUN
    decoder_warnings: list[str] = Field(default_factory=list)


class LoudnessAnalysis(StrictModel):
    integrated: FeatureValue
    range: FeatureValue
    true_peak: FeatureValue
    primary_tool: dict[str, Any]
    validator: dict[str, Any]


class TempoConsensus(StrictModel):
    difference_bpm: float | None = None
    half_double_ambiguity: bool = False
    agrees_within_tolerance: bool | None = None
    tolerance_bpm: float


class GridDiagnostics(StrictModel):
    median_interval_s: float | None = None
    tempo_variability_bpm: float | None = None
    fixed_grid_residual_ms_p50: float | None = None
    fixed_grid_residual_ms_p95: float | None = None
    end_drift_ms: float | None = None


class TempoAnalysis(StrictModel):
    selected_candidate: FeatureValue
    alternates: list[FeatureValue] = Field(default_factory=list)
    consensus: TempoConsensus
    grid_diagnostics: GridDiagnostics


class RhythmChallenger(StrictModel):
    source_tool: str
    tool_version: str | None = None
    beat_match_f1: float | None = None
    downbeat_match_f1: float | None = None
    phase_warning: bool = False


class RhythmGrid(StrictModel):
    authority: Authority = AUTHORITY_ESTIMATE
    status: Status = "warning"
    source_tool: str
    tool_version: str | None = None
    tempo_bpm: float | None = None
    meter_numerator: int = 4
    beats_s: list[float] = Field(default_factory=list)
    downbeats_s: list[float] = Field(default_factory=list)
    beat_count: int = 0
    downbeat_count: int = 0
    challenger: RhythmChallenger | None = None
    warnings: list[str] = Field(default_factory=list)


class KeyAnalysis(StrictModel):
    authority: Authority = AUTHORITY_ESTIMATE
    status: Status = "warning"
    source_tool: str = "essentia-key-extractor"
    tool_version: str | None = None
    model_profile: str | None = None
    tonic: str | None = None
    mode: str | None = None
    standard_name: str | None = None
    camelot: str | None = None
    open_key: str | None = None
    strength: float | None = None
    alternates: list[dict[str, Any]] = Field(default_factory=list)
    user_verified: bool = False
    warnings: list[str] = Field(default_factory=list)
    parameters: dict[str, Any] = Field(default_factory=dict)


class Section(StrictModel):
    section_id: str
    start_s: float
    end_s: float
    start_downbeat_index: int | None = None
    end_downbeat_index: int | None = None
    label: str | None = None
    authority: Authority = AUTHORITY_ESTIMATE
    source_tool: str
    tool_version: str | None = None
    confidence: float | None = None
    warnings: list[str] = Field(default_factory=list)


class LoopCandidate(StrictModel):
    loop_id: str
    track_id: str
    start_downbeat_index: int
    start_s: float
    bars: int
    end_s: float
    contained_in_section_id: str | None = None
    crosses_novelty_boundary: bool = False
    rhythm_sources_agree: bool | None = None
    status: Status
    derived_by: str = "downbeat-window-rule-v1"


class AnalyzerFailure(StrictModel):
    analyzer: str
    error_type: str
    message: str


class TrackAnalysis(StrictModel):
    schema_name: str = Field(default=TRACK_SCHEMA, alias="schema")
    schema_version: str = SCHEMA_VERSION
    analysis_id: str
    analyzed_at: str
    source: TrackSource
    stream: StreamFacts
    loudness: LoudnessAnalysis
    tempo: TempoAnalysis
    rhythm_grids: list[RhythmGrid] = Field(default_factory=list)
    key: KeyAnalysis
    sections: list[Section] = Field(default_factory=list)
    loop_candidates: list[LoopCandidate] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    analyzer_failures: list[AnalyzerFailure] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class HarmonicMatch(StrictModel):
    authority: Authority = AUTHORITY_DETERMINISTIC
    policy: str
    rule_id: str
    from_camelot: str | None = None
    to_camelot: str | None = None
    from_standard_name: str | None = None
    to_standard_name: str | None = None
    relationship: Literal[
        "same",
        "relative",
        "adjacent_same_mode",
        "related_3",
        "energy_plus_minus_2",
        "incompatible",
        "unknown",
    ]
    compatible: bool
    score: float
    confidence_adjusted_score: float
    warnings: list[str] = Field(default_factory=list)


class TempoMatch(StrictModel):
    authority: Authority = AUTHORITY_DETERMINISTIC
    from_bpm: float | None = None
    to_bpm: float | None = None
    shared_bpm: float | None = None
    incoming_stretch_percent: float | None = None
    midpoint_stretch_percent: float | None = None
    half_double_ambiguity: bool = False
    story_direction: Literal["up", "down", "flat", "unknown"] = "unknown"
    story_target: Literal["up", "down", "flat"] | None = None
    story_agreement: Literal["up", "down", "flat", "conflict", "unknown"] = "unknown"
    feasible: bool
    score: float
    warnings: list[str] = Field(default_factory=list)


class TransitionScore(StrictModel):
    authority: Authority = AUTHORITY_DETERMINISTIC
    from_track_id: str | None = None
    to_track_id: str | None = None
    harmonic: HarmonicMatch
    tempo: TempoMatch
    phrase_score: float
    loudness_score: float
    score: float
    weights: dict[str, float]
    warnings: list[str] = Field(default_factory=list)


class ToolDefinition(StrictModel):
    name: str
    version: str
    purpose: str
    arguments_schema: dict[str, Any] = Field(default_factory=dict)
    hard_limits: dict[str, Any] = Field(default_factory=dict)
    availability: Literal["implemented", "planned"] = "planned"
    requires: list[str] = Field(default_factory=list)


class TrackSummary(StrictModel):
    track_id: str
    filename: str
    duration_s: float | None = None
    bpm: float | None = None
    bpm_authority: Authority = AUTHORITY_ESTIMATE
    standard_name: str | None = None
    camelot: str | None = None
    key_strength: float | None = None
    loudness_lufs: float | None = None
    loudness_authority: Authority = AUTHORITY_STANDARDIZED
    section_count: int = 0
    preferred_loop_count: int = 0
    beat_count: int = 0
    downbeat_count: int = 0
    analyzer_failure_count: int = 0
    note: str = "Tempo, key, beats, and sections are benchmark_estimate values."


class TransitionWindows(StrictModel):
    track_id: str
    filename: str
    primary_grid_tool: str | None = None
    downbeat_count: int = 0
    downbeat_anchors_s: list[float] = Field(default_factory=list)
    sections: list[dict[str, Any]] = Field(default_factory=list)
    preferred_loops: list[dict[str, Any]] = Field(default_factory=list)


class RenderArtifact(StrictModel):
    artifact_id: str
    path: str
    duration_s: float | None = None
    sha256: str | None = None
    tool: str
    warnings: list[str] = Field(default_factory=list)


class MixHardConstraints(StrictModel):
    allowed_track_ids: list[str] = Field(default_factory=list)
    excluded_track_ids: list[str] = Field(default_factory=list)
    max_time_stretch_percent: float = Field(default=4.0, ge=0.0, le=4.0)
    harmonic_policy: str = "rekordbox-related-2"


class MixBrief(StrictModel):
    schema_name: str = Field(default=MIX_BRIEF_SCHEMA, alias="schema")
    schema_version: str = SCHEMA_VERSION
    request_text: str = ""
    target_duration_minutes: float = Field(gt=0)
    style_terms: list[str] = Field(default_factory=list)
    story_template: str | None = None
    hard_constraints: MixHardConstraints = Field(default_factory=MixHardConstraints)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class PlannerIdentity(StrictModel):
    provider: str = "manual"
    model: str = "manual"
    prompt_version: str = "manual-v1"


class PlannedTrackSegment(StrictModel):
    segment_id: str
    track_id: str
    start_downbeat_index: int = Field(ge=0)
    end_downbeat_index: int = Field(gt=0)
    target_bpm: float | None = Field(default=None, gt=0)
    gain_db: float = 0.0
    reason: str = ""


class PlannedTransition(StrictModel):
    transition_id: str
    from_track_id: str
    to_track_id: str
    duration_bars: Literal[4, 8, 16] = 8
    style: Literal["linear_crossfade", "house_eq_v1"] = "linear_crossfade"
    curve: Literal["tri"] = "tri"
    reason: str = ""


class MixPlan(StrictModel):
    schema_name: str = Field(default=MIX_PLAN_SCHEMA, alias="schema")
    schema_version: str = SCHEMA_VERSION
    plan_id: str
    planner: PlannerIdentity = Field(default_factory=PlannerIdentity)
    brief: MixBrief
    ordered_track_ids: list[str]
    segments: list[PlannedTrackSegment]
    transitions: list[PlannedTransition]
    requested_duration_s: float = Field(gt=0)
    estimated_duration_s: float | None = Field(default=None, gt=0)
    validation_status: Status = STATUS_NOT_RUN
    warnings: list[str] = Field(default_factory=list)
    explanation: str = ""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class RenderManifest(StrictModel):
    schema_name: str = Field(default=RENDER_MANIFEST_SCHEMA, alias="schema")
    schema_version: str = SCHEMA_VERSION
    render_id: str
    plan_id: str
    renderer: dict[str, str]
    source_track_hashes: list[dict[str, Any]] = Field(default_factory=list)
    executed_operations: list[dict[str, Any]] = Field(default_factory=list)
    requested_duration_s: float
    planned_duration_s: float
    rendered_duration_s: float | None = None
    output_path: str | None = None
    output_sha256: str | None = None
    output_measurements: dict[str, Any] = Field(default_factory=dict)
    status: Status = STATUS_NOT_RUN
    warnings: list[str] = Field(default_factory=list)
    failures: list[str] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class CollectionAnalysis(StrictModel):
    schema_name: str = Field(default=COLLECTION_SCHEMA, alias="schema")
    schema_version: str = SCHEMA_VERSION
    collection_id: str
    input_folder: str
    created_at: str
    platform: dict[str, str]
    expected_audio_count: int | None = None
    discovered_audio_count: int
    tracks: list[TrackAnalysis] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    failures: list[AnalyzerFailure] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)


def failed_feature(
    *,
    unit: str | None,
    source_tool: str,
    tool_version: str | None = None,
    message: str,
) -> FeatureValue:
    return FeatureValue(
        value=None,
        unit=unit,
        authority=AUTHORITY_ESTIMATE,
        status=STATUS_FAILED,
        source_tool=source_tool,
        tool_version=tool_version,
        warnings=[message],
    )
