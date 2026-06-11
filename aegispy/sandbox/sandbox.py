"""Sandbox execution engine for secure code execution."""

from __future__ import annotations

import logging
import os
import signal
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ..core.security import DangerousPatternDetector, SecurityConfig
from ..core.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class ExecutionResult:
    """Result of sandboxed code execution.
    
    Attributes:
        exit_code: Process exit code (0 = success)
        stdout: Standard output from the process
        stderr: Standard error from the process
        execution_time: Time taken to execute in seconds
        memory_usage_mb: Peak memory usage in MB
        signal_received: Signal that terminated the process (if any)
        is_timeout: Whether execution timed out
        is_terminated: Whether execution was terminated due to security violation
    """
    exit_code: int
    stdout: str = ""
    stderr: str = ""
    execution_time: float = 0.0
    memory_usage_mb: float = 0.0
    signal_received: int | None = None
    is_timeout: bool = False
    is_terminated: bool = False


@dataclass
class SandboxConfig:
    """Configuration for sandbox execution.
    
    Attributes:
        security_config: Security constraints configuration
        working_directory: Working directory for execution
        environment: Additional environment variables
        timeout: Execution timeout in seconds
    """
    security_config: SecurityConfig = field(default_factory=SecurityConfig)
    working_directory: Path = field(default_factory=lambda: Path(tempfile.mkdtemp(prefix="aegispy_")))
    environment: dict[str, str] = field(default_factory=dict)
    timeout: float = 30.0


class SecureSandbox:
    """Secure sandbox for executing untrusted Python code.
    
    Provides isolated execution environment with resource limits,
    security analysis, and comprehensive monitoring.
    
    Example:
        >>> sandbox = SecureSandbox()
        >>> result = sandbox.execute("print('Hello, World!')")
        >>> print(result.stdout)
        Hello, World!
    """
    
    def __init__(self, config: SandboxConfig | None = None) -> None:
        """Initialize secure sandbox.
        
        Args:
            config: Sandbox configuration. If None, uses default configuration.
        """
        self.config = config or SandboxConfig()
        self.detector = DangerousPatternDetector()
        self._pid: int | None = None
        self._start_time: float = 0.0
        
        logger.info("SecureSandbox initialized with timeout=%.1fs, memory_limit=%dMB",
                   self.config.timeout, self.config.security_config.max_memory_mb)
    
    def execute(self, code: str, timeout: float | None = None) -> ExecutionResult:
        """Execute Python code in secure sandbox.
        
        Args:
            code: Python source code to execute
            timeout: Optional execution timeout override in seconds
            
        Returns:
            ExecutionResult containing execution output and metrics
            
        Raises:
            ValueError: If code fails security analysis
            RuntimeError: If execution fails
        """
        if not code.strip():
            logger.warning("Empty code provided")
            return ExecutionResult(exit_code=1, stderr="Empty code provided")
        
        # Security analysis
        analysis = self.detector.analyze(code)
        if not analysis["is_safe"]:
            logger.warning("Security analysis failed: risk_level=%s, score=%d",
                         analysis["risk_level"], analysis["risk_score"])
            raise ValueError(
                f"Code failed security analysis: risk_level={analysis['risk_level']}, "
                f"score={analysis['risk_score']}"
            )
        
        # Create temporary file for code
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            dir=self.config.working_directory,
        ) as f:
            f.write(code)
            script_path = f.name
        
        try:
            return self._execute_script(script_path, timeout or self.config.timeout)
        finally:
            try:
                Path(script_path).unlink()
            except OSError:
                pass
    
    def _execute_script(self, script_path: str, timeout: float) -> ExecutionResult:
        """Execute a Python script in sandbox.
        
        Args:
            script_path: Path to the script to execute
            timeout: Maximum execution time in seconds
            
        Returns:
            ExecutionResult with execution metrics
        """
        self._start_time = time.time()
        
        # Prepare environment
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        env.update(self.config.environment)
        
        # Limit memory using ulimit
        import resource
        old_mem_limit = resource.getrlimit(resource.RLIMIT_AS)
        max_memory_bytes = self.config.security_config.max_memory_mb * 1024 * 1024
        try:
            resource.setrlimit(resource.RLIMIT_AS, (max_memory_bytes, max_memory_bytes))
        except (ValueError, resource.error) as e:
            logger.warning("Could not set memory limit: %s", e)
        
        # Execute script
        try:
            process = subprocess.Popen(
                [sys.executable, script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                cwd=self.config.security_config.working_directory,
                preexec_fn=self._set_process_limits,
            )
            self._pid = process.pid
            logger.info("Started sandbox process PID=%d", self._pid)
            
            try:
                stdout, stderr = process.communicate(timeout=timeout)
                exit_code = process.returncode
            except subprocess.TimeoutExpired:
                logger.warning("Process timed out after %.1fs", timeout)
                process.kill()
                stdout, stderr = process.communicate()
                exit_code = -1
                return ExecutionResult(
                    exit_code=exit_code,
                    stdout=stdout.decode("utf-8", errors="replace"),
                    stderr=stderr.decode("utf-8", errors="replace"),
                    execution_time=time.time() - self._start_time,
                    is_timeout=True,
                )
            
            # Get memory usage
            memory_mb = self._get_process_memory()
            
            return ExecutionResult(
                exit_code=exit_code,
                stdout=stdout.decode("utf-8", errors="replace"),
                stderr=stderr.decode("utf-8", errors="replace"),
                execution_time=time.time() - self._start_time,
                memory_usage_mb=memory_mb,
            )
            
        except Exception as e:
            logger.error("Execution failed: %s", e)
            return ExecutionResult(
                exit_code=-1,
                stderr=f"Execution error: {str(e)}",
                execution_time=time.time() - self._start_time,
            )
        finally:
            try:
                resource.setrlimit(resource.RLIMIT_AS, old_mem_limit)
            except (ValueError, resource.error):
                pass
    
    def _set_process_limits(self) -> None:
        """Set process resource limits."""
        # Set file size limit
        import resource
        max_file_size = self.config.security_config.max_file_size_mb * 1024 * 1024
        try:
            resource.setrlimit(resource.RLIMIT_FSIZE, (max_file_size, max_file_size))
        except (ValueError, resource.error):
            pass
        
        # Set max processes
        try:
            resource.setrlimit(resource.RLIMIT_NPROC, (self.config.security_config.max_processes, self.config.security_config.max_processes))
        except (ValueError, resource.error):
            pass
        
        # Set CPU time limit
        try:
            cpu_time = int(self.config.security_config.max_cpu_time * 1000000)
            resource.setrlimit(resource.RLIMIT_CPU, (cpu_time, cpu_time))
        except (ValueError, resource.error):
            pass
        
        # Set no new processes
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
        """Kill the running sandbox process.
        
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
            logger.info("Sandbox process killed: PID=%d", self._pid)
            self._pid = None
            return True
        except (psutil.NoSuchProcess, psutil.TimeoutExpired):
            logger.warning("Failed to kill sandbox process: PID=%d", self._pid)
            return False
    
    def __enter__(self) -> "SecureSandbox":
        """Enter sandbox context."""
        return self
    
    def __exit__(self, *args: Any) -> None:
        """Exit sandbox context and cleanup."""
        self.kill()
        logger.debug("Sandbox context exited")
