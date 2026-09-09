"""CLI for Step 2B clip renders. Never writes into the source music folder."""

from __future__ import annotations

import json
from pathlib import Path

import typer

from dj_collection_set_builder.downbeat_diagnostics import render_downbeat_diagnostics
from dj_collection_set_builder.models import CollectionAnalysis
from dj_collection_set_builder.render import (
    RenderError,
    crossfade,
    ensure_output_path,
    eq_band,
    load_track,
    loop_audio,
    low_cut,
    render_segment,
    set_gain,
    time_stretch,
)
from dj_collection_set_builder.set_renderer import (
    load_mix_plan,
    render_set,
    write_render_manifest,
)


def _echo_artifact(artifact) -> None:
    typer.echo(json.dumps(artifact.model_dump(mode="json"), indent=2))


def _fail(exc: RenderError) -> None:
    typer.echo(str(exc), err=True)
    raise typer.Exit(code=1) from exc


app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help="Render bounded DJ operations to PCM outside the music folder.",
)


@app.command("load-track")
def load_track_cmd(
    source: Path = typer.Argument(..., exists=True, dir_okay=False, readable=True),
    out: Path = typer.Option(..., "--out", help="WAV path outside the music folder."),
    start_s: float = typer.Option(..., "--start"),
    end_s: float = typer.Option(..., "--end"),
    source_folder: Path | None = typer.Option(
        None,
        "--source-folder",
        help="Refuse writes under this folder. Defaults to the source file's parent.",
    ),
) -> None:
    try:
        _echo_artifact(
            load_track(
                source,
                start_s=start_s,
                end_s=end_s,
                out_path=out,
                source_folder=source_folder or source.parent,
            )
        )
    except RenderError as exc:
        _fail(exc)


@app.command("set-gain")
def set_gain_cmd(
    source: Path = typer.Argument(..., exists=True, dir_okay=False, readable=True),
    out: Path = typer.Option(..., "--out"),
    gain_db: float = typer.Option(..., "--gain-db"),
    source_folder: Path | None = typer.Option(None, "--source-folder"),
) -> None:
    try:
        _echo_artifact(
            set_gain(
                source,
                gain_db=gain_db,
                out_path=out,
                source_folder=source_folder or source.parent,
            )
        )
    except RenderError as exc:
        _fail(exc)


@app.command("time-stretch")
def time_stretch_cmd(
    source: Path = typer.Argument(..., exists=True, dir_okay=False, readable=True),
    out: Path = typer.Option(..., "--out"),
    from_bpm: float = typer.Option(..., "--from-bpm"),
    target_bpm: float = typer.Option(..., "--target-bpm"),
    source_folder: Path | None = typer.Option(None, "--source-folder"),
) -> None:
    try:
        _echo_artifact(
            time_stretch(
                source,
                from_bpm=from_bpm,
                target_bpm=target_bpm,
                out_path=out,
                source_folder=source_folder or source.parent,
            )
        )
    except RenderError as exc:
        _fail(exc)


@app.command("loop")
def loop_cmd(
    source: Path = typer.Argument(..., exists=True, dir_okay=False, readable=True),
    out: Path = typer.Option(..., "--out"),
    repetitions: int = typer.Option(..., "--repetitions"),
    source_folder: Path | None = typer.Option(None, "--source-folder"),
) -> None:
    try:
        _echo_artifact(
            loop_audio(
                source,
                repetitions=repetitions,
                out_path=out,
                source_folder=source_folder or source.parent,
            )
        )
    except RenderError as exc:
        _fail(exc)


@app.command("crossfade")
def crossfade_cmd(
    outgoing: Path = typer.Argument(..., exists=True, dir_okay=False, readable=True),
    incoming: Path = typer.Argument(..., exists=True, dir_okay=False, readable=True),
    out: Path = typer.Option(..., "--out"),
    duration_s: float = typer.Option(..., "--duration"),
    source_folder: Path | None = typer.Option(None, "--source-folder"),
) -> None:
    try:
        guard = source_folder or outgoing.parent
        if source_folder is None:
            ensure_output_path(out, source_folder=incoming.parent, create_parent=False)
        _echo_artifact(
            crossfade(
                outgoing,
                incoming,
                duration_s=duration_s,
                out_path=out,
                source_folder=guard,
            )
        )
    except RenderError as exc:
        _fail(exc)


@app.command("eq-band")
def eq_band_cmd(
    source: Path = typer.Argument(..., exists=True, dir_okay=False, readable=True),
    out: Path = typer.Option(..., "--out"),
    band: str = typer.Option(..., "--band", help="low, mid, or high"),
    gain_db: float = typer.Option(..., "--gain-db"),
    source_folder: Path | None = typer.Option(None, "--source-folder"),
) -> None:
    try:
        _echo_artifact(
            eq_band(
                source,
                band=band,
                gain_db=gain_db,
                out_path=out,
                source_folder=source_folder or source.parent,
            )
        )
    except RenderError as exc:
        _fail(exc)


@app.command("low-cut")
def low_cut_cmd(
    source: Path = typer.Argument(..., exists=True, dir_okay=False, readable=True),
    out: Path = typer.Option(..., "--out"),
    cutoff_hz: float = typer.Option(180.0, "--cutoff-hz"),
    source_folder: Path | None = typer.Option(None, "--source-folder"),
) -> None:
    try:
        _echo_artifact(
            low_cut(
                source,
                cutoff_hz=cutoff_hz,
                out_path=out,
                source_folder=source_folder or source.parent,
            )
        )
    except RenderError as exc:
        _fail(exc)


@app.command("segment")
def segment_cmd(
    source: Path = typer.Argument(..., exists=True, dir_okay=False, readable=True),
    operations: Path = typer.Option(
        ...,
        "--operations",
        exists=True,
        dir_okay=False,
        readable=True,
        help="JSON list of {op, ...} single-source operations.",
    ),
    out: Path = typer.Option(..., "--out"),
    source_folder: Path | None = typer.Option(None, "--source-folder"),
) -> None:
    payload = json.loads(operations.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        typer.echo("Operations JSON must be a list.", err=True)
        raise typer.Exit(code=1)
    try:
        _echo_artifact(
            render_segment(
                source,
                operations=payload,
                out_path=out,
                source_folder=source_folder or source.parent,
            )
        )
    except RenderError as exc:
        _fail(exc)


@app.command("set")
def set_cmd(
    analysis: Path = typer.Option(
        ...,
        "--analysis",
        exists=True,
        dir_okay=False,
        readable=True,
        help="CollectionAnalysis JSON from dj-analyze.",
    ),
    plan: Path = typer.Option(
        ...,
        "--plan",
        exists=True,
        dir_okay=False,
        readable=True,
        help="Strict declarative MixPlan JSON.",
    ),
    out: Path = typer.Option(..., "--out", help="Final 32-bit float PCM WAV."),
    manifest: Path | None = typer.Option(
        None,
        "--manifest",
        help="RenderManifest JSON. Defaults to OUT with .manifest.json.",
    ),
) -> None:
    """Validate and render a multi-track set without invoking an LLM."""
    try:
        collection = CollectionAnalysis.model_validate_json(
            analysis.read_text(encoding="utf-8")
        )
        mix_plan = load_mix_plan(plan)
        manifest_path = manifest or out.with_suffix(".manifest.json")
        resolved_manifest = ensure_output_path(
            manifest_path,
            source_folder=Path(collection.input_folder),
            create_parent=False,
        )
        if resolved_manifest == out.resolve():
            raise RenderError("Audio output and manifest output must be different paths")
        render_manifest = render_set(collection, mix_plan, out_path=out)
        write_render_manifest(
            render_manifest,
            resolved_manifest,
            source_folder=Path(collection.input_folder),
        )
        _echo_artifact(render_manifest)
        typer.echo(f"Wrote manifest {resolved_manifest}", err=True)
    except (OSError, ValueError, RenderError) as exc:
        if isinstance(exc, RenderError):
            _fail(exc)
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc


@app.command("downbeat-clicks")
def downbeat_clicks_cmd(
    analysis: Path = typer.Option(
        ...,
        "--analysis",
        exists=True,
        dir_okay=False,
        readable=True,
        help="CollectionAnalysis JSON containing the stored downbeat grids.",
    ),
    plan: Path = typer.Option(
        ...,
        "--plan",
        exists=True,
        dir_okay=False,
        readable=True,
        help="MixPlan whose ordered tracks should be checked.",
    ),
    out_dir: Path = typer.Option(
        ...,
        "--out-dir",
        help="Directory outside the source collection for diagnostic WAVs.",
    ),
    duration_s: float = typer.Option(
        30.0,
        "--duration",
        help="Centered excerpt duration for each track, in seconds.",
    ),
    source_tool: str = typer.Option(
        "all-in-one-mlx",
        "--source-tool",
        help="Stored rhythm grid to audition (all-in-one-mlx or beat-this).",
    ),
) -> None:
    """Render centered track excerpts with clicks on detected downbeats only."""
    try:
        collection = CollectionAnalysis.model_validate_json(
            analysis.read_text(encoding="utf-8")
        )
        mix_plan = load_mix_plan(plan)
        results = render_downbeat_diagnostics(
            collection,
            mix_plan.ordered_track_ids,
            out_dir=out_dir,
            duration_s=duration_s,
            source_tool=source_tool,
        )
        typer.echo(json.dumps(results, indent=2))
    except (OSError, ValueError, RenderError) as exc:
        if isinstance(exc, RenderError):
            _fail(exc)
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc


if __name__ == "__main__":
    app()
