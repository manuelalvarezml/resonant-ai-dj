"""CLI for Step 1 folder analysis.

Usage:
  dj-analyze FOLDER --out FILE
  dj-collection-set-builder FOLDER --out FILE
"""

from __future__ import annotations

from pathlib import Path

import typer

from dj_collection_set_builder.analyze import DEFAULT_MAX_WORKER_RSS_MB, SourceModifiedError, analyze_folder
from dj_collection_set_builder.ingest import EmptyCorpusError, MissingFFmpegError


def _run_analysis(
    folder: Path,
    out: Path,
    expected_count: int | None,
    recursive: bool,
    keep_work: bool,
    resume: bool,
    retry_failed: bool,
    max_tracks: int,
    max_worker_rss_mb: float,
    min_reclaimable_ram_mb: float,
) -> None:
    try:
        collection = analyze_folder(
            folder,
            out,
            expected_count=expected_count,
            recursive=recursive,
            keep_work=keep_work,
            resume=resume,
            retry_failed=retry_failed,
            max_tracks=max_tracks,
            max_worker_rss_mb=max_worker_rss_mb,
            min_reclaimable_ram_mb=min_reclaimable_ram_mb,
            progress=lambda message: typer.echo(message, err=True),
        )
    except EmptyCorpusError as exc:
        typer.secho(str(exc), err=True, fg=typer.colors.RED)
        raise typer.Exit(code=1) from exc
    except MissingFFmpegError as exc:
        typer.secho(str(exc), err=True, fg=typer.colors.RED)
        raise typer.Exit(code=1) from exc
    except SourceModifiedError as exc:
        typer.secho(str(exc), err=True, fg=typer.colors.RED)
        raise typer.Exit(code=2) from exc
    except ValueError as exc:
        typer.secho(str(exc), err=True, fg=typer.colors.RED)
        raise typer.Exit(code=1) from exc

    typer.echo(f"Wrote {out} ({collection.discovered_audio_count} tracks)")
    if collection.failures:
        typer.secho(
            f"{len(collection.failures)} analyzer failure(s) recorded in the JSON.",
            err=True,
            fg=typer.colors.YELLOW,
        )


def main(
    folder: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        help="Folder of owned MP3s. Files are never modified.",
    ),
    out: Path = typer.Option(
        ...,
        "--out",
        help="CollectionAnalysis JSON path. Must be outside the source folder.",
    ),
    expected_count: int | None = typer.Option(
        None,
        "--expected-count",
        help="Warn if the discovered MP3 count differs.",
    ),
    recursive: bool = typer.Option(False, "--recursive", help="Recurse into subfolders."),
    keep_work: bool = typer.Option(
        False,
        "--keep-work",
        help="Keep temporary demix/PCM work files next to the output.",
    ),
    resume: bool = typer.Option(
        False,
        "--resume",
        help="Skip tracks whose SHA-256 is already in the output JSON.",
    ),
    retry_failed: bool = typer.Option(
        True,
        "--retry-failed/--no-retry-failed",
        help="Re-run tracks that exist in the JSON but have analyzer failures.",
    ),
    max_tracks: int = typer.Option(
        1,
        "--max-tracks",
        help="Analyze at most this many new tracks, then exit. 0 means no limit.",
    ),
    max_worker_rss_mb: float = typer.Option(
        DEFAULT_MAX_WORKER_RSS_MB,
        "--max-worker-rss-mb",
        help="Kill a track worker if its process tree RSS exceeds this many MB.",
    ),
    min_reclaimable_ram_mb: float = typer.Option(
        2048,
        "--min-reclaimable-ram-mb",
        help="Do not start a worker unless this much RAM looks reclaimable.",
    ),
) -> None:
    """Extract mixing features from a folder of MP3s."""
    _run_analysis(
        folder,
        out,
        expected_count,
        recursive,
        keep_work,
        resume,
        retry_failed,
        max_tracks,
        max_worker_rss_mb,
        min_reclaimable_ram_mb,
    )


app = typer.Typer(add_completion=False, no_args_is_help=True)
app.command()(main)


if __name__ == "__main__":
    app()
