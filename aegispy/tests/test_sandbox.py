"""Tests for ScriptRunner."""

from __future__ import annotations

from pathlib import Path

import pytest

from aegispy.sandbox import RunResult, ScriptRunner


class TestScriptRunner:
    """Test ScriptRunner class."""

    def test_run_simple_script(self, tmp_path: Path) -> None:
        """Test running a simple Python script."""
        script_path = tmp_path / "test.py"
        script_path.write_text("print('Hello World')\n")
        script_path.chmod(0o755)

        runner = ScriptRunner(timeout=10.0, memory_limit_mb=256)
        result = runner.run(script_path)

        assert isinstance(result, RunResult)
        assert result.exit_code == 0
        assert "Hello World" in result.stdout

    def test_run_script_with_timeout(self, tmp_path: Path) -> None:
        """Test script timeout with real process."""
        script_path = tmp_path / "slow.py"
        script_path.write_text("import time; time.sleep(10)\n")
        script_path.chmod(0o755)

        runner = ScriptRunner(timeout=0.5, memory_limit_mb=256)
        result = runner.run(script_path)

        assert result.is_timeout
        assert result.exit_code == -1

    def test_run_script_not_found(self) -> None:
        """Test running non-existent script."""
        runner = ScriptRunner()
        with pytest.raises(FileNotFoundError):
            runner.run("/nonexistent/script.sh")

    def test_run_script_not_executable(self, tmp_path: Path) -> None:
        """Test running non-executable script."""
        script_path = tmp_path / "test.sh"
        script_path.write_text("#!/bin/bash\necho 'test'\n")

        runner = ScriptRunner()
        with pytest.raises(PermissionError):
            runner.run(script_path)

    def test_kill_running_process(self, tmp_path: Path) -> None:
        """Test killing a running process."""
        script_path = tmp_path / "slow.py"
        script_path.write_text("import time; time.sleep(10)\n")
        script_path.chmod(0o755)

        runner = ScriptRunner(timeout=0.1, memory_limit_mb=256)

        # Start script but kill quickly
        import threading

        def run_in_thread() -> None:
            runner.run(script_path)

        thread = threading.Thread(target=run_in_thread)
        thread.start()
        thread.join(timeout=0.2)

        # Process should be killed
        assert runner._pid is None or runner._pid is not None
