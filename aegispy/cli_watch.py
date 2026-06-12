"""CLI command for file watching."""

from __future__ import annotations

import logging
import time
from pathlib import Path

import click

from aegispy.watcher import FileWatcher, WatchEvent

logger = logging.getLogger(__name__)


@click.command()
@click.argument("paths", nargs=-1, required=True)
@click.option(
    "--interval", "-i", type=float, default=1.0, help="Polling interval in seconds (default: 1.0)"
)
@click.option("--recursive", "-r", is_flag=True, default=True, help="Watch directories recursively")
@click.option("--no-recursive", is_flag=True, help="Do not watch directories recursively")
@click.option("--follow-symlinks", is_flag=True, help="Follow symbolic links")
@click.option(
    "--ignore", "-x", multiple=True, help="Patterns to ignore (can be used multiple times)"
)
@click.option("--output", "-o", type=click.Path(), help="Write events to file instead of stdout")
def watch(
    paths: tuple[str],
    interval: float,
    recursive: bool,
    no_recursive: bool,
    follow_symlinks: bool,
    ignore: tuple[str],
    output: str | None,
) -> None:
    """Watch files and directories for changes.

    MONITORS file system changes in real-time and outputs events to stdout.
    """
    if no_recursive:
        recursive = False

    # Convert paths to Path objects
    watch_paths = [Path(p).resolve() for p in paths]
    for p in watch_paths:
        if not p.exists():
            click.echo(f"Warning: Path does not exist: {p}", err=True)

    # Build config
    from aegispy.watcher import WatcherConfig

    config = WatcherConfig(
        poll_interval=interval,
        recursive=recursive,
        follow_symlinks=follow_symlinks,
        ignore_patterns=list(ignore) if ignore else None,
    )

    # Setup output
    output_file = Path(output).open("a") if output else None  # noqa: SIM115

    def event_handler(event: WatchEvent) -> None:
        """Handle watch events."""
        if output_file:
            line = f"{event.timestamp:.3f} {event.event_type.value:12} {event.path}\n"
            output_file.write(line)
        else:
            click.echo(f"{event.timestamp:.3f} {event.event_type.value:12} {event.path}", err=True)

    # Create and start watcher
    watcher = FileWatcher(config=config, callback=event_handler)

    for path in watch_paths:
        watcher.add_path(path)

    try:
        watcher.start()
        click.echo(f"Watching {len(watch_paths)} path(s)...", err=True)
        click.echo("Press Ctrl+C to stop", err=True)

        while watcher.is_running():
            time.sleep(0.1)

    except KeyboardInterrupt:
        click.echo("\nStopping watcher...", err=True)
    finally:
        watcher.stop()
        click.echo("Watcher stopped", err=True)
