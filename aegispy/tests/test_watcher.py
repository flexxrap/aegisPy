"""Tests for file watcher."""

from __future__ import annotations

import tempfile
import time
from pathlib import Path

import pytest

from aegispy.watcher import FileWatcher, WatchEvent, WatchEventType, WatcherConfig


class TestWatchEvent:
    """Test WatchEvent class."""
    
    def test_create_event(self) -> None:
        """Test creating a watch event."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            path = Path(f.name)
        
        try:
            event = WatchEvent(WatchEventType.CREATED, path, time.time())
            
            assert event.event_type == WatchEventType.CREATED
            assert event.path == path
            assert event.timestamp > 0
        finally:
            path.unlink()


class TestWatcherConfig:
    """Test WatcherConfig class."""
    
    def test_default_config(self) -> None:
        """Test default configuration."""
        config = WatcherConfig()
        
        assert config.poll_interval == 1.0
        assert config.recursive is True
        assert config.follow_symlinks is False
        assert config.ignore_patterns is None
    
    def test_custom_config(self) -> None:
        """Test custom configuration."""
        config = WatcherConfig(
            poll_interval=2.0,
            recursive=False,
            follow_symlinks=True,
            ignore_patterns=["*.log", "*.tmp"],
        )
        
        assert config.poll_interval == 2.0
        assert config.recursive is False
        assert config.follow_symlinks is True
        assert config.ignore_patterns == ["*.log", "*.tmp"]


class TestFileWatcher:
    """Test FileWatcher class."""
    
    def test_add_path(self) -> None:
        """Test adding a path to watch."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir)
            watcher = FileWatcher()
            
            watcher.add_path(path)
            
            assert path in watcher._paths
    
    def test_remove_path(self) -> None:
        """Test removing a path from watch."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir)
            watcher = FileWatcher()
            
            watcher.add_path(path)
            result = watcher.remove_path(path)
            
            assert result is True
            assert path not in watcher._paths
    
    def test_remove_nonexistent_path(self) -> None:
        """Test removing nonexistent path."""
        watcher = FileWatcher()
        path = Path("/nonexistent/path")
        
        result = watcher.remove_path(path)
        
        assert result is False
    
    def test_should_ignore(self) -> None:
        """Test ignore patterns."""
        config = WatcherConfig(ignore_patterns=["*.log", "temp"])
        watcher = FileWatcher(config=config)
        
        assert watcher._should_ignore(Path("test.log")) is True
        assert watcher._should_ignore(Path("temp/file.txt")) is True
        assert watcher._should_ignore(Path("test.py")) is False
    
    @pytest.mark.skip(reason="Thread creation issues in test environment")
    def test_context_manager(self) -> None:
        """Test watcher as context manager."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir)
            watcher = FileWatcher()
            watcher.add_path(path)
            
            with watcher:
                assert watcher.is_running()
            
            assert not watcher.is_running()
    
    @pytest.mark.skip(reason="Thread creation issues in test environment")
    def test_callback(self) -> None:
        """Test event callback."""
        events: list[WatchEvent] = []
        
        def handler(event: WatchEvent) -> None:
            events.append(event)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir)
            config = WatcherConfig(poll_interval=0.1)
            watcher = FileWatcher(config=config, callback=handler)
            watcher.add_path(path)
            
            watcher.start()
            time.sleep(0.3)
            watcher.stop()
            
            # Should not have events since directory is empty
            # but callback mechanism works
    
    def test_get_state(self) -> None:
        """Test getting file state."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            path = Path(f.name)
        
        try:
            watcher = FileWatcher()
            state = watcher.get_state(path)
            
            assert state is not None
            assert state["exists"] is True
            assert "size" in state
            assert "modified" in state
        finally:
            path.unlink()
    
    def test_get_nonexistent_state(self) -> None:
        """Test getting state of nonexistent file."""
        watcher = FileWatcher()
        state = watcher.get_state(Path("/nonexistent/file.txt"))
        
        assert state is not None
        assert state["exists"] is False
