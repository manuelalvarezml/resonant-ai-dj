"""Versioned contracts for PlaylistIQ's local descriptor pipeline."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import Field

from .models import StrictModel


class HostProfile(StrictModel):
    platform: str
    platform_release: str
    machine: str
    processor: str
    python_version: str
    logical_cpu_count: int = Field(ge=1)
    physical_cpu_count: int | None = Field(default=None, ge=1)
    total_ram_mb: float = Field(gt=0)


class ModelAssetRecord(StrictModel):
    asset_id: str
    filename: str
    url: str
    sha256: str
    size_bytes: int = Field(ge=0)
    downloaded: bool
    preparation_wall_time_s: float = Field(ge=0)


class StageMetrics(StrictModel):
    algorithm_id: str
    implementation: str
    device: str
    status: Literal["passed", "failed", "timeout", "memory_exceeded", "reused"]
    started_at: str
    finished_at: str
    wall_time_s: float = Field(ge=0)
    cpu_user_time_s: float = Field(ge=0)
    cpu_system_time_s: float = Field(ge=0)
    cpu_total_time_s: float = Field(ge=0)
    cpu_utilization_percent: float = Field(ge=0)
    normalized_cpu_utilization_percent: float = Field(ge=0)
    peak_rss_mb: float = Field(ge=0)
    peak_vms_mb: float = Field(ge=0)
    peak_thread_count: int = Field(ge=0)
    peak_child_process_count: int = Field(ge=0)
    io_read_bytes: int | None = Field(default=None, ge=0)
    io_write_bytes: int | None = Field(default=None, ge=0)
    host_available_ram_start_mb: float = Field(ge=0)
    host_available_ram_min_mb: float = Field(ge=0)
    host_swap_used_start_mb: float = Field(ge=0)
    host_swap_used_peak_mb: float = Field(ge=0)
    audio_duration_s: float | None = Field(default=None, gt=0)
    realtime_factor: float | None = Field(default=None, ge=0)
    audio_seconds_per_wall_second: float | None = Field(default=None, ge=0)
    exit_code: int | None = None
    telemetry_interval_s: float = Field(gt=0)
    sample_count: int = Field(ge=0)
    error: str | None = None


class AlgorithmResult(StrictModel):
    algorithm_id: str
    implementation: str
    implementation_version: str
    authority: Literal[
        "encoded_fact",
        "standardized_measurement",
        "deterministic_measurement",
        "benchmark_estimate",
    ]
    status: Literal["passed", "warning", "failed"]
    values: dict[str, Any] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
    error: str | None = None
    metrics: StageMetrics | None = None


class SourceRecord(StrictModel):
    relative_path: str
    filename: str
    size_bytes: int = Field(ge=0)
    sha256_before: str = Field(pattern=r"^[0-9a-f]{64}$")
    sha256_after: str = Field(pattern=r"^[0-9a-f]{64}$")
    source_unchanged: bool


class DescriptorTrack(StrictModel):
    track_id: str
    source: SourceRecord
    duration_s: float | None = Field(default=None, gt=0)
    algorithms: list[AlgorithmResult]
    descriptor_document: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class AlgorithmProjection(StrictModel):
    algorithm_id: str
    measured_tracks: int = Field(ge=0)
    passed_tracks: int = Field(ge=0)
    failed_tracks: int = Field(ge=0)
    total_audio_duration_s: float = Field(ge=0)
    total_wall_time_s: float = Field(ge=0)
    mean_wall_time_s_per_track: float | None = Field(default=None, ge=0)
    median_wall_time_s_per_track: float | None = Field(default=None, ge=0)
    max_wall_time_s_per_track: float | None = Field(default=None, ge=0)
    total_cpu_time_s: float = Field(ge=0)
    mean_cpu_utilization_percent: float | None = Field(default=None, ge=0)
    max_cpu_utilization_percent: float | None = Field(default=None, ge=0)
    mean_normalized_cpu_utilization_percent: float | None = Field(default=None, ge=0)
    max_peak_rss_mb: float = Field(ge=0)
    max_peak_thread_count: int = Field(ge=0)
    wall_minutes_per_audio_hour: float | None = Field(default=None, ge=0)
    cpu_core_hours_per_audio_hour: float | None = Field(default=None, ge=0)
    projected_serial_minutes_per_100_tracks: float | None = Field(default=None, ge=0)
    projected_ram_gb_per_worker_with_35pct_headroom: float = Field(ge=0)
    memory_limited_workers_8gb: int = Field(ge=0)
    memory_limited_workers_16gb: int = Field(ge=0)
    memory_limited_workers_32gb: int = Field(ge=0)
    projection_warning: str


class PipelineProjection(StrictModel):
    measured_tracks: int = Field(ge=0)
    total_audio_duration_s: float = Field(ge=0)
    total_sequential_stage_wall_time_s: float = Field(ge=0)
    total_cpu_time_s: float = Field(ge=0)
    mean_sequential_wall_time_s_per_track: float | None = Field(default=None, ge=0)
    median_sequential_wall_time_s_per_track: float | None = Field(default=None, ge=0)
    max_sequential_wall_time_s_per_track: float | None = Field(default=None, ge=0)
    mean_cpu_utilization_percent: float | None = Field(default=None, ge=0)
    max_observed_stage_rss_mb: float = Field(ge=0)
    wall_minutes_per_audio_hour: float | None = Field(default=None, ge=0)
    cpu_core_hours_per_audio_hour: float | None = Field(default=None, ge=0)
    projected_serial_minutes_per_100_tracks: float | None = Field(default=None, ge=0)
    projected_ram_gb_per_sequential_worker_with_35pct_headroom: float = Field(ge=0)
    memory_limited_workers_8gb: int = Field(ge=0)
    memory_limited_workers_16gb: int = Field(ge=0)
    memory_limited_workers_32gb: int = Field(ge=0)
    model_asset_cache_bytes: int = Field(ge=0)
    projection_warning: str


class DescriptorRun(StrictModel):
    schema_name: Literal["prompt-playlist/descriptor-run"] = Field(
        default="prompt-playlist/descriptor-run", alias="schema"
    )
    schema_version: Literal["0.1.0"] = "0.1.0"
    pipeline_version: Literal["playlistiq-descriptors-v1"] = "playlistiq-descriptors-v1"
    run_id: str
    started_at: str
    finished_at: str
    source_folder: str
    recursive: bool
    selected_track_count: int = Field(ge=0)
    discovered_track_count: int = Field(ge=0)
    selection_limit: int | None = Field(default=None, ge=1)
    algorithms_requested: list[str]
    cpu_threads_per_worker: int = Field(ge=1)
    max_worker_rss_mb: float = Field(gt=0)
    worker_timeout_s: float = Field(gt=0)
    host: HostProfile
    tool_versions: dict[str, str]
    model_assets: list[ModelAssetRecord]
    tracks: list[DescriptorTrack]
    algorithm_projections: list[AlgorithmProjection]
    pipeline_projection: PipelineProjection
    source_inventory_unchanged: bool
    source_hashes_unchanged: bool
    failure_count: int = Field(ge=0)
    warnings: list[str] = Field(default_factory=list)
