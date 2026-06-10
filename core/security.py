"""Core security utilities for AegisPy sandbox."""

from __future__ import annotations

import logging
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class SecurityConfig:
    """Configuration for security constraints and sandbox settings.
    
    Attributes:
        max_memory_mb: Maximum memory in MB allowed for sandboxed processes
        max_cpu_time: Maximum CPU time in seconds
        max_file_size_mb: Maximum file size in MB that can be created
        max_processes: Maximum number of child processes
        network_enabled: Whether network access is allowed
        allowed_syscalls: List of allowed system calls (None = all allowed)
        working_directory: Working directory for sandboxed execution
    """
    
    def __init__(
        self,
        max_memory_mb: int = 512,
        max_cpu_time: int = 30,
        max_file_size_mb: int = 10,
        max_processes: int = 10,
        network_enabled: bool = False,
        allowed_syscalls: list[str] | None = None,
        working_directory: Path | None = None,
    ) -> None:
        """Initialize security configuration.
        
        Args:
            max_memory_mb: Maximum memory in MB for sandboxed processes
            max_cpu_time: Maximum CPU time in seconds
            max_file_size_mb: Maximum file size in MB
            max_processes: Maximum number of child processes
            network_enabled: Whether network access is allowed
            allowed_syscalls: List of allowed system calls
            working_directory: Working directory for execution
        """
        self.max_memory_mb = max_memory_mb
        self.max_cpu_time = max_cpu_time
        self.max_file_size_mb = max_file_size_mb
        self.max_processes = max_processes
        self.network_enabled = network_enabled
        self.allowed_syscalls = allowed_syscalls
        self.working_directory = working_directory or Path(tempfile.mkdtemp(prefix="aegispy_"))
        
        logger.info("SecurityConfig initialized with memory_limit=%dMB, cpu_time=%ds",
                   max_memory_mb, max_cpu_time)
    
    def create_cgroup_config(self) -> dict[str, Any]:
        """Create cgroup configuration for resource limits.
        
        Returns:
            Dictionary containing cgroup configuration parameters
        """
        return {
            "memory_limit": f"{self.max_memory_mb * 1024 * 1024}B",
            "cpu_quota": f"{self.max_cpu_time * 1000}us",
            "pids_max": self.max_processes,
        }
    
    def validate_working_directory(self) -> bool:
        """Validate that working directory exists and is writable.
        
        Returns:
            True if directory is valid, False otherwise
        """
        try:
            self.working_directory.mkdir(parents=True, exist_ok=True)
            test_file = self.working_directory / ".test_write"
            test_file.write_text("test")
            test_file.unlink()
            logger.debug("Working directory validated: %s", self.working_directory)
            return True
        except OSError as e:
            logger.error("Failed to validate working directory: %s", e)
            return False


class DangerousPatternDetector:
    """Detect dangerous patterns in Python code.
    
    Attributes:
        dangerous_imports: Set of dangerous module names
        dangerous_functions: Set of dangerous function names
    """
    
    DANGEROUS_IMPORTS = {
        "os", "subprocess", "sys", "platform", "socket", "ctypes",
        "pickle", "marshal", "shelve", "dbm", "code", "compileall",
        "importlib", "pkgutil", "runpy", "zipimport", "imp",
    }
    
    DANGEROUS_FUNCTIONS = {
        "eval", "exec", "compile", "__import__", "getattr", "setattr",
        "delattr", "globals", "locals", "vars", "dir", "open",
        "input", "breakpoint", "exit", "quit", "help",
    }
    
    DANGEROUS_PATTERNS = [
        r"__class__", r"__mro__", r"__subclasses__", r"__globals__",
        r"__builtins__", r"os\.system", r"os\.popen", r"subprocess\.",
        r"socket\.", r"ctypes\.", r"ctypes\.CDLL", r"importlib\.",
    ]
    
    def __init__(self) -> None:
        """Initialize dangerous pattern detector."""
        self._compiled_patterns = [
            __import__("re").compile(p) for p in self.DANGEROUS_PATTERNS
        ]
        logger.debug("DangerousPatternDetector initialized with %d patterns",
                   len(self._compiled_patterns))
    
    def check_imports(self, code: str) -> list[str]:
        """Check for dangerous imports in code.
        
        Args:
            code: Python source code to analyze
            
        Returns:
            List of dangerous imports found
        """
        imports_found = []
        try:
            import ast
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if any(alias.name.startswith(mod) for mod in self.DANGEROUS_IMPORTS):
                            imports_found.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module and any(node.module.startswith(mod) for mod in self.DANGEROUS_IMPORTS):
                        imports_found.append(node.module)
        except SyntaxError as e:
            logger.warning("Syntax error while checking imports: %s", e)
        
        if imports_found:
            logger.warning("Found dangerous imports: %s", imports_found)
        
        return imports_found
    
    def check_functions(self, code: str) -> list[str]:
        """Check for dangerous function calls.
        
        Args:
            code: Python source code to analyze
            
        Returns:
            List of dangerous functions found
        """
        functions_found = []
        try:
            import ast
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in self.DANGEROUS_FUNCTIONS:
                            functions_found.append(node.func.id)
                    elif isinstance(node.func, ast.Attribute):
                        if node.func.attr in self.DANGEROUS_FUNCTIONS:
                            functions_found.append(node.func.attr)
        except SyntaxError as e:
            logger.warning("Syntax error while checking functions: %s", e)
        
        if functions_found:
            logger.warning("Found dangerous function calls: %s", functions_found)
        
        return functions_found
    
    def check_patterns(self, code: str) -> list[str]:
        """Check for dangerous code patterns.
        
        Args:
            code: Python source code to analyze
            
        Returns:
            List of dangerous patterns found
        """
        patterns_found = []
        for pattern in self._compiled_patterns:
            matches = pattern.findall(code)
            if matches:
                patterns_found.extend(matches)
        
        if patterns_found:
            logger.warning("Found dangerous patterns: %s", patterns_found[:5])
        
        return patterns_found
    
    def analyze(self, code: str) -> dict[str, Any]:
        """Perform comprehensive security analysis.
        
        Args:
            code: Python source code to analyze
            
        Returns:
            Dictionary with analysis results
        """
        imports = self.check_imports(code)
        functions = self.check_functions(code)
        patterns = self.check_patterns(code)
        
        risk_score = len(imports) * 3 + len(functions) * 2 + len(patterns)
        risk_level = "low" if risk_score < 5 else "medium" if risk_score < 15 else "high"
        
        return {
            "imports": imports,
            "functions": functions,
            "patterns": patterns,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "is_safe": risk_score == 0,
        }
