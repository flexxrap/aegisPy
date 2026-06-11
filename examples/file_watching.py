"""Example: File watching."""

import time
from pathlib import Path

from aegispy.watcher import FileWatcher, WatchEvent

def on_event(event: WatchEvent) -> None:
    """Handle watch events."""
    print(f"Event: {event.event_type.value} - {event.path}")

# Create watcher
watcher = FileWatcher(callback=on_event)

# Add path to watch
watcher.add_path(Path("."))

# Start watching
watcher.start()
print("Watching directory... Press Ctrl+C to stop")

try:
    while watcher.is_running():
        time.sleep(1)
except KeyboardInterrupt:
    print("\nStopping watcher...")
finally:
    watcher.stop()
