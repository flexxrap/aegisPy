"""Tests for CLI."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from aegispy.cli import main


class TestCLI:
    """Test CLI commands."""

    def test_version(self) -> None:
        """Test version command."""
        runner = CliRunner()
        result = runner.invoke(main, ["--version"])

        assert result.exit_code == 0
        assert "aegispy, version 0.1.0" in result.output

    def test_run_simple_code(self) -> None:
        """Test running simple code."""
        runner = CliRunner()
        result = runner.invoke(main, ["run", "print('Hello')"])

        assert result.exit_code == 0
        assert "Hello" in result.output

    def test_run_with_file_option(self, tmp_path: Path) -> None:
        """Test running code from file."""
        script_path = tmp_path / "test.py"
        script_path.write_text("print('From file')\n")

        runner = CliRunner()
        result = runner.invoke(main, ["run", "--file", str(script_path)])

        assert result.exit_code == 0
        assert "From file" in result.output

    def test_run_with_memory_option(self) -> None:
        """Test running with memory limit."""
        runner = CliRunner()
        result = runner.invoke(main, ["run", "print('test')", "--memory", "256"])

        assert result.exit_code == 0
        assert "test" in result.output

    def test_run_with_timeout_option(self) -> None:
        """Test running with timeout."""
        runner = CliRunner()
        result = runner.invoke(main, ["run", "print('test')", "--timeout", "30"])

        assert result.exit_code == 0
        assert "test" in result.output

    def test_run_empty_code(self) -> None:
        """Test running empty code."""
        runner = CliRunner()
        result = runner.invoke(main, ["run", ""])

        assert result.exit_code == 1
        assert "Provide code" in result.output

    def test_analyze_safe_code(self, tmp_path: Path) -> None:
        """Test analyzing safe code."""
        script_path = tmp_path / "safe.py"
        script_path.write_text("print('Hello')\n")

        runner = CliRunner()
        result = runner.invoke(main, ["analyze", str(script_path)])

        assert result.exit_code == 0
        assert "Risk Level: LOW" in result.output
        assert "Safe to Execute: Yes" in result.output

    def test_analyze_dangerous_code(self, tmp_path: Path) -> None:
        """Test analyzing dangerous code."""
        script_path = tmp_path / "dangerous.py"
        script_path.write_text("import os\nimport subprocess\neval('x')\n")

        runner = CliRunner()
        result = runner.invoke(main, ["analyze", str(script_path)])

        assert result.exit_code == 0
        assert "Risk Level: MEDIUM" in result.output or "Risk Level: HIGH" in result.output
        assert "Safe to Execute: No" in result.output
        assert "os" in result.output
        assert "subprocess" in result.output
        assert "eval" in result.output

    def test_analyze_with_output_file(self, tmp_path: Path) -> None:
        """Test analyzing with output file."""
        script_path = tmp_path / "safe.py"
        script_path.write_text("print('test')\n")
        output_path = tmp_path / "report.txt"

        runner = CliRunner()
        result = runner.invoke(main, ["analyze", str(script_path), "--output", str(output_path)])

        assert result.exit_code == 0
        assert f"Report saved to: {output_path}" in result.output
        assert output_path.exists()
        assert "Security Analysis Report" in output_path.read_text()

    def test_tui_command(self) -> None:
        """Test TUI command (should not fail to import)."""
        runner = CliRunner()
        # Just test that it doesn't crash on import
        result = runner.invoke(main, ["tui", "--help"])
        # TUI command should be available
        assert result.exit_code == 0
