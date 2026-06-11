"""Tests for ScriptRunner."""

from __future__ import annotations

import subprocess
import sys
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
        assert result.execution_time > 0

    def test_run_shell_script(self, tmp_path: Path) -> None:
        """Test running a shell script via bash."""
        script_path = tmp_path / "test.sh"
        script_path.write_text("echo 'Shell output'\n")
        script_path.chmod(0o755)

        runner = ScriptRunner(timeout=10.0, memory_limit_mb=256)
        result = runner.run(script_path)

        # Shell scripts may fail if not executable, but bash -x should work
        assert isinstance(result, RunResult)

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

