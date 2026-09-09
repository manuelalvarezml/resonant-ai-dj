"""CLI for Step 2A scoring and compact track lookups. Does not modify source MP3s."""

from __future__ import annotations

import json
from pathlib import Path

import typer

from dj_collection_set_builder.compatibility import score_transition
from dj_collection_set_builder.models import CollectionAnalysis
from dj_collection_set_builder.story import propose_tempo_wave_order, tempo_wave_climb_count
from dj_collection_set_builder.summaries import (
    UnknownTrackError,
    find_track,
    get_track_summary,
    get_transition_windows,
)


def main(
    analysis: Path = typer.Argument(
        ...,
        exists=True,
        dir_okay=False,
        readable=True,
        help="CollectionAnalysis JSON from dj-analyze.",
    ),
    json_out: Path | None = typer.Option(
        None,
        "--json-out",
        help="Optional JSON path for the proposed order and consecutive scores.",
    ),
    summary: str | None = typer.Option(
        None,
        "--summary",
        help="Print a compact TrackSummary for this track_id, filename, or sha256.",
    ),
    windows: str | None = typer.Option(
        None,
        "--windows",
        help="Print TransitionWindows for this track_id, filename, or sha256.",
    ),
) -> None:
    """Propose a tempo-wave order, or look up one track without dumping beat arrays."""
    collection = CollectionAnalysis.model_validate_json(analysis.read_text(encoding="utf-8"))
    if summary is not None or windows is not None:
        try:
            if summary is not None:
                payload = get_track_summary(find_track(collection, summary)).model_dump(mode="json")
                typer.echo(json.dumps(payload, indent=2))
            if windows is not None:
                payload = get_transition_windows(find_track(collection, windows)).model_dump(
                    mode="json"
                )
                typer.echo(json.dumps(payload, indent=2))
        except UnknownTrackError as exc:
            typer.echo(str(exc), err=True)
            raise typer.Exit(code=1) from exc
        return
    ordered = propose_tempo_wave_order(collection.tracks)
    climb = tempo_wave_climb_count(len(ordered))
    rows = []
    typer.echo("Proposed tempo_wave order:")
    for index, track in enumerate(ordered, start=1):
        bpm = track.tempo.selected_candidate.value
        typer.echo(
            f"  {index:02d}. {track.source.filename}  "
            f"{bpm} BPM  {track.key.standard_name or '?'} {track.key.camelot or '?'}"
        )
    typer.echo("")
    typer.echo("Consecutive transitions:")
    for position, (left, right) in enumerate(zip(ordered, ordered[1:]), start=2):
        target = "up" if position <= climb else "down"
        score = score_transition(left, right, story_target=target)
        rows.append(score.model_dump(mode="json"))
        typer.echo(
            f"  {left.source.filename} -> {right.source.filename}  "
            f"score={score.score:.3f}  "
            f"harmonic={score.harmonic.relationship}  "
            f"stretch={score.tempo.incoming_stretch_percent:.2f}%  "
            f"feasible={score.tempo.feasible}"
        )
    if json_out is not None:
        payload = {
            "ordered_filenames": [track.source.filename for track in ordered],
            "ordered_track_ids": [track.source.track_id for track in ordered],
            "transitions": rows,
        }
        json_out.parent.mkdir(parents=True, exist_ok=True)
        json_out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        typer.echo(f"Wrote {json_out}")


app = typer.Typer(add_completion=False, no_args_is_help=True)
app.command()(main)


if __name__ == "__main__":
    app()
