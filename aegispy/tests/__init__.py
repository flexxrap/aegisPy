"""Tests for AegisPy."""

from __future__ import annotations

import pytest


class TestSecurityConfig:
    """Tests for SecurityConfig."""

    def test_default_values(self) -> None:
        from aegispy.core.security import SecurityConfig

        config = SecurityConfig()

        assert config.max_memory_mb == 512
        assert config.max_cpu_time == 30
        assert config.max_file_size_mb == 10
        assert config.max_processes == 10
        assert config.network_enabled is False

    def test_custom_values(self) -> None:
        from aegispy.core.security import SecurityConfig

        config = SecurityConfig(
            max_memory_mb=1024,
            max_cpu_time=60,
            max_processes=20,
        )

        assert config.max_memory_mb == 1024
        assert config.max_cpu_time == 60
        assert config.max_processes == 20


class TestDangerousPatternDetector:
    """Tests for DangerousPatternDetector."""

    def test_safe_code(self) -> None:
        from aegispy.core.security import DangerousPatternDetector

        detector = DangerousPatternDetector()
        code = "print('Hello, World!')"
        result = detector.analyze(code)

        assert result["is_safe"] is True
        assert result["risk_score"] == 0

    def test_dangerous_import(self) -> None:
        from aegispy.core.security import DangerousPatternDetector

        detector = DangerousPatternDetector()
        code = "import os\nimport subprocess"
        result = detector.analyze(code)

        assert result["is_safe"] is False
        assert "os" in result["imports"]
        assert "subprocess" in result["imports"]

    def test_dangerous_function(self) -> None:
        from aegispy.core.security import DangerousPatternDetector

        detector = DangerousPatternDetector()
        code = "eval('1+1')"
        result = detector.analyze(code)

        assert result["is_safe"] is False
        assert "eval" in result["functions"]

    def test_dangerous_pattern(self) -> None:
        from aegispy.core.security import DangerousPatternDetector

        detector = DangerousPatternDetector()
        code = "__class__.__mro__"
        result = detector.analyze(code)

        assert result["is_safe"] is False
        assert len(result["patterns"]) > 0


class TestSecureSandbox:
    """Tests for SecureSandbox."""

    def test_execute_simple_code(self) -> None:
        from aegispy.sandbox import SecureSandbox

        sandbox = SecureSandbox()
        result = sandbox.execute("print('Hello')")

        assert result.exit_code == 0
        assert "Hello" in result.stdout

    def test_execute_with_output(self) -> None:
        from aegispy.sandbox import SecureSandbox

        sandbox = SecureSandbox()
        result = sandbox.execute("x = 2 + 2\nprint(x)")

        assert result.exit_code == 0
        assert "4" in result.stdout

    def test_empty_code(self) -> None:
        from aegispy.sandbox import SecureSandbox

        sandbox = SecureSandbox()
        result = sandbox.execute("")

        assert result.exit_code == 1
        assert "Empty code" in result.stderr

    def test_security_violation(self) -> None:
        from aegispy.sandbox import SecureSandbox

        sandbox = SecureSandbox()

        with pytest.raises(ValueError, match="security analysis"):
            sandbox.execute("import os")

    def test_execution_timeout(self) -> None:
        from aegispy.core.security import SecurityConfig
        from aegispy.sandbox import SandboxConfig, SecureSandbox

        config = SandboxConfig(
            security_config=SecurityConfig(),
            timeout=0.1,
        )
        sandbox = SecureSandbox(config)

        result = sandbox.execute("import time; time.sleep(1)")

        assert result.is_timeout is True


class TestSandboxConfig:
    """Tests for SandboxConfig."""

    def test_default_config(self) -> None:
        from aegispy.sandbox import SandboxConfig

        config = SandboxConfig()

        assert config.timeout == 30.0
        assert config.security_config is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
