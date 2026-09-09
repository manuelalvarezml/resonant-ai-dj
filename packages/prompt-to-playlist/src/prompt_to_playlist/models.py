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


class CatalogTrack(StrictModel):
    track_id: Text
    title: Text
    artist: Text | None = None
    bpm: NumericEvidence | None = None
    duration_s: NumericEvidence | None = None
    tags: list[TagEvidence] = Field(default_factory=list, max_length=200)
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
    schema_version: Literal["0.1.0"] = "0.1.0"
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
    descriptors: list[Descriptor] = Field(min_length=1, max_length=500)

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


class PlaylistQuery(StrictModel):
    required_tags: list[Tag] = Field(default_factory=list, max_length=50)
    preferred_tags: list[Tag] = Field(default_factory=list, max_length=50)
    excluded_tags: list[Tag] = Field(default_factory=list, max_length=50)
    min_bpm: float | None = Field(default=None, gt=0, le=400)
    max_bpm: float | None = Field(default=None, gt=0, le=400)
    limit: int = Field(default=10, ge=1, le=100)
    excluded_track_ids: list[Text] = Field(default_factory=list, max_length=1000)
    order: Literal["relevance", "bpm_ascending", "bpm_descending"] = "relevance"

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
        return self


class Translation(StrictModel):
    schema_name: Literal["prompt-playlist/translation"] = Field(default="prompt-playlist/translation", alias="schema")
    schema_version: Literal["0.1.0"] = "0.1.0"
    request_text: str = Field(min_length=1, max_length=4000)
    query: PlaylistQuery
    provider: Text
    model: Text
    prompt_version: Text
    vocabulary_id: Text
    authority: Literal["llm_proposal"] = "llm_proposal"
    unresolved: list[str] = Field(default_factory=list, max_length=100)
    warnings: list[str] = Field(default_factory=list, max_length=100)


class TrackMatch(StrictModel):
    track: CatalogTrack
    score: float = Field(ge=0, le=1)
    matched_tags: list[str]
    missing_preferred_tags: list[str]
    reasons: list[str]


class SearchResult(StrictModel):
    schema_name: Literal["prompt-playlist/result"] = Field(default="prompt-playlist/result", alias="schema")
    schema_version: Literal["0.1.0"] = "0.1.0"
    catalog_id: Text
    vocabulary_id: Text
    query: PlaylistQuery
    ranking_version: Literal["tag-coverage-v1"] = "tag-coverage-v1"
    matches: list[TrackMatch]
    eligible_count: int = Field(ge=0)
    excluded_count: int = Field(ge=0)
    warnings: list[str]
    catalog_digest: str
    vocabulary_digest: str
    result_id: str


class PlaylistRun(StrictModel):
    schema_name: Literal["prompt-playlist/run"] = Field(default="prompt-playlist/run", alias="schema")
    schema_version: Literal["0.1.0"] = "0.1.0"
    translation: Translation
    result: SearchResult | None
    status: Literal["matched", "no_matches", "needs_clarification"]
    warnings: list[str] = Field(default_factory=list)
