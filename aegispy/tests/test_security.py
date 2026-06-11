"""Tests for security module."""

from __future__ import annotations

from aegispy.core.security import DangerousPatternDetector, SecurityConfig


class TestSecurityConfig:
    """Test SecurityConfig class."""

    def test_default_config(self) -> None:
        """Test default security configuration."""
        config = SecurityConfig()

        assert config.max_memory_mb == 512
        assert config.max_cpu_time == 30
        assert config.max_file_size_mb == 10
        assert config.max_processes == 10
        assert config.network_enabled is False
        assert config.allowed_syscalls is None

    def test_custom_config(self) -> None:
        """Test custom security configuration."""
        config = SecurityConfig(
            max_memory_mb=1024,
            max_cpu_time=60,
            max_file_size_mb=20,
            max_processes=20,
            network_enabled=True,
        )

        assert config.max_memory_mb == 1024
        assert config.max_cpu_time == 60
        assert config.max_file_size_mb == 20
        assert config.max_processes == 20
        assert config.network_enabled is True

    def test_create_cgroup_config(self) -> None:
        """Test cgroup configuration creation."""
        config = SecurityConfig(max_memory_mb=512, max_cpu_time=30, max_processes=10)
        cgroup = config.create_cgroup_config()

        assert cgroup["memory_limit"] == "536870912B"
        assert cgroup["cpu_quota"] == "30000us"
        assert cgroup["pids_max"] == 10

    def test_validate_working_directory(self) -> None:
        """Test working directory validation."""
        config = SecurityConfig()
        assert config.validate_working_directory() is True


class TestDangerousPatternDetector:
    """Test DangerousPatternDetector class."""

    def test_safe_code(self) -> None:
        """Test detection on safe code."""
        detector = DangerousPatternDetector()
        code = """
        def hello():
            print("Hello, World!")
            return 42

        hello()
        """
        result = detector.analyze(code)

        assert result["is_safe"] is True
        assert result["risk_score"] == 0
        assert result["risk_level"] == "low"
        assert len(result["imports"]) == 0
        assert len(result["functions"]) == 0
        assert len(result["patterns"]) == 0

    def test_dangerous_imports(self) -> None:
        """Test detection of dangerous imports."""
        detector = DangerousPatternDetector()
        code = "import os\nimport subprocess\nimport pickle\n"
        result = detector.analyze(code)

        assert result["is_safe"] is False
        assert result["risk_score"] > 0
        assert "os" in result["imports"]
        assert "subprocess" in result["imports"]
        assert "pickle" in result["imports"]

    def test_dangerous_functions(self) -> None:
        """Test detection of dangerous function calls."""
        detector = DangerousPatternDetector()
        code = 'eval("1+1")\nexec("print(\'test\')")\n'
        result = detector.analyze(code)

        assert result["is_safe"] is False
        assert "eval" in result["functions"]
        assert "exec" in result["functions"]

    def test_dangerous_patterns(self) -> None:
        """Test detection of dangerous patterns."""
        detector = DangerousPatternDetector()
        code = 'x.__class__.__mro__\nos.system("ls")\nsocket.socket()\n'
        result = detector.analyze(code)

        assert result["is_safe"] is False
        assert "__class__" in result["patterns"]
        assert "__mro__" in result["patterns"]
        assert "os.system" in result["patterns"]
        assert "socket." in result["patterns"]

    def test_risk_scoring(self) -> None:
        """Test risk score calculation."""
        detector = DangerousPatternDetector()

        # Low risk (score < 5)
        code1 = "import os"
        result1 = detector.analyze(code1)
        assert result1["risk_level"] == "low"
        assert result1["risk_score"] == 3

        # Medium risk (5 <= score < 15)
        code2 = "import os\nimport subprocess\nimport pickle\n"
        result2 = detector.analyze(code2)
        assert result2["risk_level"] == "medium"
        assert result2["risk_score"] == 9

        # High risk (score >= 15)
        code3 = (
            "import os\nimport subprocess\nimport pickle\n"
            "import sys\nimport socket\nimport ctypes\n"
        )
        result3 = detector.analyze(code3)
        assert result3["risk_level"] == "high"
        assert result3["risk_score"] == 18

    def test_complex_code_analysis(self) -> None:
        """Test analysis of complex code."""
        detector = DangerousPatternDetector()
        code = (
            "import json\nimport math\n"
            "\ndef calculate(x, y):\n    return x + y\n"
            "\ndef dangerous():\n    eval('malicious code')\n    os.system('rm -rf /')\n"
            "\nresult = calculate(1, 2)\nprint(result)\n"
        )
        result = detector.analyze(code)

        assert result["is_safe"] is False
        assert "eval" in result["functions"]
        assert "os.system" in result["patterns"]
        assert "json" not in result["imports"]
        assert "math" not in result["imports"]
