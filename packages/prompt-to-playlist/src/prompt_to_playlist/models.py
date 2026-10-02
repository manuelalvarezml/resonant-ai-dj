"""Versioned, provider-neutral contracts. See docs/SCHEMAS.md."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

Text = Annotated[str, Field(min_length=1, max_length=500)]
Tag = Annotated[str, Field(pattern=r"^[a-z][a-z0-9_-]*:[a-z][a-z0-9_-]*$", max_length=100)]
Axis = Annotated[str, Field(pattern=r"^[a-z][a-z0-9_-]*$", max_length=40)]
Authority = Literal["encoded_fact", "standardized_measurement", "deterministic_measurement",
                    "benchmark_estimate", "user_verified", "llm_proposal", "executed_action"]
EvidenceAuthority = Literal["encoded_fact", "standardized_measurement", "deterministic_measurement",
                            "benchmark_estimate", "user_verified"]
Status = Literal["passed", "warning", "rejected", "unknown", "failed", "not_run"]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, allow_inf_nan=False,
                              populate_by_name=True, validate_assignment=True)


class NumericEvidence(StrictModel):
    value: float
    authority: EvidenceAuthority
    source: Text
    status: Status = "passed"
    confidence: float | None = Field(default=None, ge=0, le=1)


class TagEvidence(StrictModel):
    tag: Tag
    authority: EvidenceAuthority
    source: Text
    status: Status = "passed"
    confidence: float | None = Field(default=None, ge=0, le=1)
    source_label: Text | None = None
    parent_tags: list[Tag] = Field(default_factory=list, max_length=10)


Embedding = Annotated[list[float], Field(min_length=512, max_length=512)]


class SemanticSegment(StrictModel):
    start_s: float = Field(ge=0)
    end_s: float = Field(gt=0)
    embedding: Embedding

    @model_validator(mode="after")
    def ordered(self):
        if self.end_s <= self.start_s: raise ValueError("Invalid semantic segment interval")
        if not .99 <= sum(x*x for x in self.embedding) <= 1.01: raise ValueError("Semantic embedding must be normalized")
        return self


class SemanticAudio(StrictModel):
    encoder_id: Text
    sampling_policy: Text
    segments: list[SemanticSegment] = Field(min_length=1, max_length=3)


class SemanticQuery(StrictModel):
    description: Text
    avoid: list[Text] = Field(default_factory=list, max_length=3)
    encoder_id: Text | None = None
    embeddings: list[Embedding] = Field(default_factory=list, max_length=4)

    @model_validator(mode="after")
    def complete(self):
        if self.embeddings:
            if not self.encoder_id or len(self.embeddings) != 1 + len(self.avoid): raise ValueError("Incomplete semantic query encoding")
            if any(not .99 <= sum(x*x for x in vector) <= 1.01 for vector in self.embeddings): raise ValueError("Semantic query embeddings must be normalized")
        return self


class CatalogTrack(StrictModel):
    track_id: Text
    title: Text
    artist: Text | None = None
    bpm: NumericEvidence | None = None
    duration_s: NumericEvidence | None = None
    tags: list[TagEvidence] = Field(default_factory=list, max_length=200)
    semantic_audio: SemanticAudio | None = None
    preference_scores: dict[Tag, NumericEvidence] = Field(default_factory=dict)
    complete_tag_axes: list[Axis] = Field(default_factory=list, max_length=50)
    warnings: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def consistent(self):
        if not self.track_id.strip() or not self.title.strip():
            raise ValueError("Track ID and title must not be blank")
        for name in ("bpm", "duration_s"):
            value = getattr(self, name)
            if value is not None and value.value <= 0:
                raise ValueError(f"{name} must be positive")
        if len(self.complete_tag_axes) != len(set(self.complete_tag_axes)):
            raise ValueError("Duplicate complete_tag_axes")
        return self


class Catalog(StrictModel):
    schema_name: Literal["prompt-playlist/catalog"] = Field(default="prompt-playlist/catalog", alias="schema")
    schema_version: Literal["0.1.0", "0.2.0", "0.3.0"] = "0.3.0"
    catalog_id: Text
    tracks: list[CatalogTrack] = Field(max_length=100_000)
    warnings: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def unique_ids(self):
        ids = [track.track_id for track in self.tracks]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate catalog track IDs")
        return self


class Descriptor(StrictModel):
    id: Tag
    description: Text
    aliases: list[Text] = Field(default_factory=list, max_length=30)


class Vocabulary(StrictModel):
    schema_name: Literal["prompt-playlist/vocabulary"] = Field(default="prompt-playlist/vocabulary", alias="schema")
    schema_version: Literal["0.1.0"] = "0.1.0"
    vocabulary_id: Text
    descriptors: list[Descriptor] = Field(min_length=1, max_length=1000)

    @model_validator(mode="after")
    def unambiguous(self):
        known: dict[str, str] = {}
        ids = [item.id for item in self.descriptors]
        if len(set(ids)) != len(ids):
            raise ValueError("Duplicate descriptor IDs")
        for item in self.descriptors:
            for term in [item.id, *item.aliases]:
                key = term.strip().casefold()
                if not key or (key in known and known[key] != item.id):
                    raise ValueError(f"Ambiguous or empty descriptor alias: {term}")
                known[key] = item.id
        return self


class Preference(StrictModel):
    tag: Tag
    direction: Literal["increase", "decrease"] = "increase"
    importance: Literal["primary", "secondary", "optional"] = "secondary"
    origin: Literal["explicit", "inferred"] = "explicit"
    source_span: Text | None = None


class PlaylistQuery(StrictModel):
    semantic: SemanticQuery | None = None
    required_tags: list[Tag] = Field(default_factory=list, max_length=50)
    preferred_tags: list[Tag] = Field(default_factory=list, max_length=50)
    excluded_tags: list[Tag] = Field(default_factory=list, max_length=50)
    min_bpm: float | None = Field(default=None, gt=0, le=400)
    max_bpm: float | None = Field(default=None, gt=0, le=400)
    limit: int = Field(default=10, ge=1, le=100)
    excluded_track_ids: list[Text] = Field(default_factory=list, max_length=1000)
    order: Literal["relevance", "bpm_ascending", "bpm_descending"] = "relevance"
    any_tag_groups: list[list[Tag]] = Field(default_factory=list, max_length=10)
    preferences: list[Preference] = Field(default_factory=list, max_length=30)
    genre_scope: Literal["exact", "taxonomy"] = "exact"

    @model_validator(mode="after")
    def consistent(self):
        if self.min_bpm is not None and self.max_bpm is not None and self.min_bpm > self.max_bpm:
            raise ValueError("min_bpm must not exceed max_bpm")
        for field in ("required_tags", "preferred_tags", "excluded_tags", "excluded_track_ids"):
            values = getattr(self, field)
            if len(values) != len(set(values)):
                raise ValueError(f"Duplicate values in {field}")
        if (set(self.required_tags) | set(self.preferred_tags)) & set(self.excluded_tags):
            raise ValueError("A requested descriptor cannot also be excluded")
        for group in self.any_tag_groups:
            if not 1 <= len(group) <= 20 or len(group) != len(set(group)):
                raise ValueError("Alternative groups need 1–20 unique tags")
            if not all(t.startswith("genre:") for t in group):
                raise ValueError("Alternatives support genre tags only")
            if set(group) <= set(self.excluded_tags):
                raise ValueError("All alternatives are excluded")
        ids = [p.tag for p in self.preferences]
        if len(ids) != len(set(ids)) or set(ids) & set(self.preferred_tags):
            raise ValueError("Duplicate preference objectives")
        if any(p.direction == "increase" and p.tag in self.excluded_tags for p in self.preferences):
            raise ValueError("A preferred descriptor cannot also be excluded")
        return self


class ClarificationAnswer(StrictModel):
    question: Text
    answer: Annotated[str, Field(min_length=1, max_length=1000)]

    @model_validator(mode="after")
    def nonblank(self):
        if not self.question.strip() or not self.answer.strip():
            raise ValueError("Clarification question and answer must not be blank")
        return self


class TagConstraint(StrictModel):
    mode: Literal["all", "any", "exclude"]
    tags: list[Tag] = Field(min_length=1, max_length=20)
    source_span: Text


class BPMConstraint(StrictModel):
    minimum: float | None = Field(gt=0, le=400)
    maximum: float | None = Field(gt=0, le=400)
    source_span: Text


class EvidenceGap(StrictModel):
    concept: Text
    origin: Literal["explicit_requirement", "optional_preference", "inferred_context"] = Field(description="explicit_requirement means a HARD user requirement and MUST have blocking=true. Soft explicit wishes use optional_preference. Contextual caveats use inferred_context.")
    blocking: bool
    explanation: Text


class IntentPlan(StrictModel):
    musical_description: Text | None = Field(default=None, description="MUST be entirely ENGLISH even for Spanish requests. Concise audible musical character only, no titles, artists or unverified lyrics; null without musical direction.")
    avoid_descriptions: list[Text] = Field(default_factory=list, max_length=3, description="English descriptions of explicitly unwanted musical character, as soft contrasts only; empty unless requested.")
    schema_version: Literal["playlist-intent-v1"] = "playlist-intent-v1"
    disposition: Literal["ready", "partial_support", "needs_clarification", "unsupported"]
    interpretation: Text
    occasion: Text | None
    activity: Text | None
    recipient: Text | None
    emotional_goal: Text | None
    constraints: list[TagConstraint] = Field(max_length=30, description="Explicit hard requirements only. EMPTY for ordinary creative mood/activity/occasion prompts. any mode accepts genre alternatives only.")
    bpm: BPMConstraint | None
    preferences: list[Preference] = Field(max_length=30)
    count: int = Field(ge=1, le=100)
    count_source: Text | None
    order: Literal["relevance", "bpm_ascending", "bpm_descending"]
    order_source: Text | None
    excluded_track_ids: list[Text] = Field(max_length=100)
    assumptions: list[Text] = Field(max_length=10)
    evidence_gaps: list[EvidenceGap] = Field(max_length=20)
    clarification: Text | None


class Translation(StrictModel):
    schema_name: Literal["prompt-playlist/translation"] = Field(default="prompt-playlist/translation", alias="schema")
    schema_version: Literal["0.1.0", "0.2.0", "0.3.0"] = "0.3.0"
    request_text: str = Field(min_length=1, max_length=4000)
    query: PlaylistQuery
    provider: Text
    model: Text
    prompt_version: Text
    vocabulary_id: Text
    authority: Literal["llm_proposal"] = "llm_proposal"
    unresolved: list[str] = Field(default_factory=list, max_length=100)
    warnings: list[str] = Field(default_factory=list, max_length=100)
    plan: IntentPlan | None = None
    proposed_plan: IntentPlan | None = None
    clarifications: list[ClarificationAnswer] = Field(default_factory=list, max_length=3)
    compiler_version: str | None = None
    prompt_digest: str | None = None
    reasoning_effort: str | None = None


class ScoreContribution(StrictModel):
    score_kind: Literal["model_support", "relative_similarity"] = "model_support"
    detail: str | None = None
    tags: list[Tag]
    group: Literal["genre", "preference", "semantic"]
    direction: Literal["increase", "decrease"]
    origin: Literal["explicit", "inferred"]
    evidence_value: float | None
    utility: float = Field(ge=0, le=1)
    weight: float = Field(ge=0, le=1)
    contribution: float = Field(ge=0, le=1)
    source: str | None


class TrackMatch(StrictModel):
    track: CatalogTrack
    score: float = Field(ge=0, le=1)
    matched_tags: list[str]
    missing_preferred_tags: list[str]
    reasons: list[str]
    score_contributions: list[ScoreContribution] = Field(default_factory=list)


class SearchResult(StrictModel):
    schema_name: Literal["prompt-playlist/result"] = Field(default="prompt-playlist/result", alias="schema")
    schema_version: Literal["0.1.0", "0.2.0", "0.3.0"] = "0.3.0"
    catalog_id: Text
    vocabulary_id: Text
    query: PlaylistQuery
    ranking_version: Literal["tag-coverage-v1", "scored-preferences-v1", "maest-intent-v1", "hybrid-semantic-v1"] = "tag-coverage-v1"
    matches: list[TrackMatch]
    eligible_count: int = Field(ge=0)
    excluded_count: int = Field(ge=0)
    warnings: list[str]
    catalog_digest: str
    vocabulary_digest: str
    result_id: str
    eligible_track_ids: list[Text] = Field(default_factory=list)
    taxonomy_version: str | None = None


class PlaylistRun(StrictModel):
    schema_name: Literal["prompt-playlist/run"] = Field(default="prompt-playlist/run", alias="schema")
    schema_version: Literal["0.1.0", "0.2.0", "0.3.0"] = "0.3.0"
    translation: Translation
    result: SearchResult | None
    status: Literal["matched", "no_matches", "needs_clarification", "unsupported", "partial_support"]
    warnings: list[str] = Field(default_factory=list)
