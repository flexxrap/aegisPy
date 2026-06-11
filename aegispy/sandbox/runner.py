"""Script runner for executing arbitrary scripts in isolated environment."""

from __future__ import annotations

import logging
import os
import signal
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..core.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class RunResult:
    """Result of script execution.

    Attributes:
        exit_code: Process exit code (0 = success)
        stdout: Standard output from the process
        stderr: Standard error from the process
        execution_time: Time taken to execute in seconds
        memory_usage_mb: Peak memory usage in MB
        signal_received: Signal that terminated the process (if any)
        is_timeout: Whether execution timed out
    """
    exit_code: int
    stdout: str = ""
    stderr: str = ""
    execution_time: float = 0.0
    memory_usage_mb: float = 0.0
    signal_received: int | None = None
    is_timeout: bool = False


class ScriptRunner:
    """Runner for executing arbitrary scripts in isolated environment.

    Provides isolated execution with timeout and memory limits using subprocess.

    Example:
        >>> runner = ScriptRunner(timeout=30.0, memory_limit_mb=256)
        >>> result = runner.run("/path/to/script.sh")
        >>> print(result.stdout)
    """

    def __init__(
        self,
        timeout: float = 30.0,
        memory_limit_mb: int = 256,
        working_directory: Path | None = None,
        environment: dict[str, str] | None = None,
    ) -> None:
        """Initialize script runner.

        Args:
            timeout: Maximum execution time in seconds
            memory_limit_mb: Memory limit in megabytes
            working_directory: Working directory for execution
            environment: Additional environment variables
        """
        self.timeout = timeout
        self.memory_limit_mb = memory_limit_mb
        self.working_directory = working_directory or Path.cwd()
        self.environment = environment or {}
        self._pid: int | None = None
        self._start_time: float = 0.0

        logger.info(
            "ScriptRunner initialized with timeout=%.1fs, memory_limit=%dMB",
            timeout, memory_limit_mb
        )

    def run(self, script_path: str | Path) -> RunResult:
        """Execute a script in isolated environment.

        Args:
            script_path: Path to the script to execute

        Returns:
            RunResult containing execution output and metrics

        Raises:
            FileNotFoundError: If script does not exist
            PermissionError: If script is not executable
            RuntimeError: If execution fails
        """
        script_path = Path(script_path).resolve()

        if not script_path.exists():
            logger.error("Script not found: %s", script_path)
            raise FileNotFoundError(f"Script not found: {script_path}")

        if not os.access(script_path, os.X_OK):
            logger.error("Script not executable: %s", script_path)
            raise PermissionError(f"Script not executable: {script_path}")

        self._start_time = time.time()

        env = os.environ.copy()
        env.update(self.environment)

        try:
            return self._run_script(script_path, env)
        except Exception as e:
            logger.error("Script execution failed: %s", e)
            return RunResult(
                exit_code=-1,
                stderr=f"Execution error: {str(e)}",
                execution_time=time.time() - self._start_time,
            )

    def _run_script(self, script_path: Path, env: dict[str, str]) -> RunResult:
        """Run the script with resource limits.

        Args:
            script_path: Path to the script
            env: Environment variables

        Returns:
            RunResult with execution metrics
        """
        import resource

        old_mem_limit = resource.getrlimit(resource.RLIMIT_AS)
        max_memory_bytes = self.memory_limit_mb * 1024 * 1024

        try:
            resource.setrlimit(resource.RLIMIT_AS, (max_memory_bytes, max_memory_bytes))
        except (ValueError, resource.error) as e:
            logger.warning("Could not set memory limit: %s", e)

        try:
            process = subprocess.Popen(
                [str(script_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                cwd=str(self.working_directory),
                preexec_fn=self._set_process_limits,
            )
            self._pid = process.pid
            logger.info("Started script process PID=%d: %s", self._pid, script_path)

            try:
                stdout, stderr = process.communicate(timeout=self.timeout)
                exit_code = process.returncode
            except subprocess.TimeoutExpired:
                logger.warning("Script timed out after %.1fs: %s", self.timeout, script_path)
                process.kill()
                stdout, stderr = process.communicate()
                exit_code = -1
                return RunResult(
                    exit_code=exit_code,
                    stdout=stdout.decode("utf-8", errors="replace"),
                    stderr=stderr.decode("utf-8", errors="replace"),
                    execution_time=time.time() - self._start_time,
                    is_timeout=True,
                )

            memory_mb = self._get_process_memory()

            return RunResult(
                exit_code=exit_code,
                stdout=stdout.decode("utf-8", errors="replace"),
                stderr=stderr.decode("utf-8", errors="replace"),
                execution_time=time.time() - self._start_time,
                memory_usage_mb=memory_mb,
            )

        except Exception as e:
            logger.error("Process execution failed: %s", e)
            return RunResult(
                exit_code=-1,
                stderr=f"Process error: {str(e)}",
                execution_time=time.time() - self._start_time,
            )
        finally:
            try:
                resource.setrlimit(resource.RLIMIT_AS, old_mem_limit)
            except (ValueError, resource.error):
                pass

    def _set_process_limits(self) -> None:
        """Set process resource limits."""
        import resource

        try:
            max_file_size = 100 * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_FSIZE, (max_file_size, max_file_size))
        except (ValueError, resource.error):
            pass

        try:
            resource.setrlimit(resource.RLIMIT_NPROC, (64, 64))
        except (ValueError, resource.error):
            pass

        try:
            os.setpgrp()
        except OSError:
            pass

    def _get_process_memory(self) -> float:
        """Get current process memory usage in MB.

        Returns:
            Memory usage in megabytes
        """
        try:
            import psutil
            process = psutil.Process(self._pid or os.getpid())
            memory_info = process.memory_info()
            return memory_info.rss / (1024 * 1024)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return 0.0

    def kill(self) -> bool:
        """Kill the running script process.

        Returns:
            True if process was killed, False if not running
        """
        if self._pid is None:
            return False

        try:
            import psutil
            process = psutil.Process(self._pid)
            process.terminate()
            process.wait(timeout=5)
            logger.info("Script process killed: PID=%d", self._pid)
            self._pid = None
            return True
        except (psutil.NoSuchProcess, psutil.TimeoutExpired):
            logger.warning("Failed to kill script process: PID=%d", self._pid)
            return False

    def __enter__(self) -> ScriptRunner:
        """Enter runner context."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Exit runner context and cleanup."""
        self.kill()
        logger.debug("Runner context exited")
