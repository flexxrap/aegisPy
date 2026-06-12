"""File watching for AegisPy."""

from __future__ import annotations

import logging
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)


class WatchEventType(Enum):
    """Types of file watch events."""

    CREATED = "created"
    MODIFIED = "modified"
    DELETED = "deleted"
    MOVED = "moved"


@dataclass
class WatchEvent:
    """Represents a file watch event.

    Attributes:
        event_type: Type of event that occurred
        path: Path of the affected file
        timestamp: Time when event occurred
    """

    event_type: WatchEventType
    path: Path
    timestamp: float


@dataclass
class WatcherConfig:
    """Configuration for file watcher.

    Attributes:
        poll_interval: Time between polls in seconds
        recursive: Watch directories recursively
        follow_symlinks: Follow symbolic links
        ignore_patterns: Patterns to ignore
    """

    poll_interval: float = 1.0
    recursive: bool = True
    follow_symlinks: bool = False
    ignore_patterns: list[str] | None = None


class FileWatcher:
    """File watcher for monitoring file system changes.

    Provides polling-based file watching with event callbacks.
    """

    def __init__(
        self,
        config: WatcherConfig | None = None,
        callback: Callable[[WatchEvent], None] | None = None,
    ) -> None:
        """Initialize file watcher.

        Args:
            config: Watcher configuration
            callback: Callback function for events
        """
        self.config = config or WatcherConfig()
        self.callback = callback
        self._paths: set[Path] = set()
        self._file_states: dict[Path, float] = {}
        self._running = False
        self._thread: threading.Thread | None = None
        self._lock = threading.Lock()

        logger.info(
            "FileWatcher initialized with poll_interval=%.2fs, recursive=%s",
            self.config.poll_interval,
            self.config.recursive,
        )

    def add_path(self, path: Path | str, recursive: bool | None = None) -> None:
        """Add a path to watch.

        Args:
            path: Path to watch
            recursive: Override recursive setting for this path
        """
        path = Path(path).resolve()
        recursive = recursive if recursive is not None else self.config.recursive

        if recursive and path.is_dir():
            if self.config.follow_symlinks:
                for p in path.rglob("*"):
                    self._paths.add(p)
            else:
                for p in path.rglob("*"):
                    if not p.is_symlink():
                        self._paths.add(p)
            # Also add the directory itself
            self._paths.add(path)
        else:
            self._paths.add(path)

        logger.info("Added path to watch: %s", path)

    def remove_path(self, path: Path | str) -> bool:
        """Remove a path from watching.

        Args:
            path: Path to remove

        Returns:
            True if path was removed, False if not found
        """
        path = Path(path).resolve()

        if path in self._paths:
            self._paths.remove(path)
            logger.info("Removed path from watch: %s", path)
            return True

        logger.warning("Path not found for removal: %s", path)
        return False

    def start(self) -> None:
        """Start watching."""
        if self._running:
            logger.warning("Watcher already running")
            return

        self._running = True
        self._thread = threading.Thread(target=self._watch_loop, daemon=True)
        self._thread.start()
        logger.info("FileWatcher started")

    def stop(self) -> None:
        """Stop watching."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5.0)
            self._thread = None
        logger.info("FileWatcher stopped")

    def is_running(self) -> bool:
        """Check if watcher is running."""
        return self._running

    def _watch_loop(self) -> None:
        """Main watching loop."""
        while self._running:
            try:
                self._check_paths()
            except Exception as e:
                logger.error("Error in watch loop: %s", e)

            time.sleep(self.config.poll_interval)

    def _check_paths(self) -> None:
        """Check all watched paths for changes."""
        current_states: dict[Path, float] = {}

        for path in self._paths:
            try:
                if path.exists():
                    stat = path.stat()
                    mtime = stat.st_mtime

                    if path in self._file_states:
                        if abs(mtime - self._file_states[path]) > 0.1:
                            self._emit_event(WatchEventType.MODIFIED, path, mtime)
                    else:
                        self._emit_event(WatchEventType.CREATED, path, mtime)

                    current_states[path] = mtime
                else:
                    if path in self._file_states:
                        self._emit_event(WatchEventType.DELETED, path, time.time())
                        del current_states[path]
            except OSError as e:
                logger.warning("Error checking path %s: %s", path, e)

        # Check for deleted files
        with self._lock:
            for path in list(self._file_states.keys()):
                if path not in current_states:
                    self._emit_event(WatchEventType.DELETED, path, time.time())

        self._file_states = current_states

    def _emit_event(self, event_type: WatchEventType, path: Path, timestamp: float) -> None:
        """Emit a watch event.

        Args:
            event_type: Type of event
            path: Path that changed
            timestamp: Event timestamp
        """
        # Check ignore patterns
        if self._should_ignore(path):
            return

        event = WatchEvent(event_type, path, timestamp)

        logger.debug("Watch event: %s for %s", event_type.value, path)

        if self.callback:
            try:
                self.callback(event)
            except Exception as e:
                logger.error("Error in callback: %s", e)

    def _should_ignore(self, path: Path) -> bool:
        """Check if path should be ignored."""
        if not self.config.ignore_patterns:
            return False

        path_str = str(path)
        for pattern in self.config.ignore_patterns:
            if pattern.startswith("*."):
                if path.name.endswith(pattern[1:]):
                    return True
            elif pattern in path_str:
                return True

        return False

    def get_state(self, path: Path | str) -> dict | None:
        """Get current state of a watched path.

        Args:
            path: Path to check

        Returns:
            State dictionary or None
        """
        path = Path(path).resolve()

        if path.exists():
            stat = path.stat()
            return {
                "path": str(path),
                "exists": True,
                "size": stat.st_size,
                "modified": stat.st_mtime,
                "created": stat.st_ctime,
            }

        return {"path": str(path), "exists": False}

    def __enter__(self) -> FileWatcher:
        """Enter context manager."""
        self.start()
        return self

    def __exit__(self, *args: object) -> None:
        """Exit context manager."""
        self.stop()
