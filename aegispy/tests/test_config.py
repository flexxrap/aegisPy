"""Tests for configuration module."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest
import yaml

from aegispy.config import Config, ConfigLoader


class TestConfig:
    """Test Config class."""

    def test_default_config(self) -> None:
        """Test default configuration."""
        config = Config()

        assert config.sandbox.timeout == 30.0
        assert config.sandbox.security_config.max_memory_mb == 512
        assert config.sandbox.security_config.max_cpu_time == 30
        assert config.logging == {}
        assert config.ui == {}
        assert config.runtime == {}

    def test_from_dict(self) -> None:
        """Test creating Config from dictionary."""
        data = {
            "sandbox": {
                "timeout": 60.0,
                "max_memory_mb": 1024,
                "max_cpu_time": 60,
            },
            "logging": {
                "level": "DEBUG",
            },
        }

        config = Config.from_dict(data)

        assert config.sandbox.timeout == 60.0
        assert config.sandbox.security_config.max_memory_mb == 1024
        assert config.sandbox.security_config.max_cpu_time == 60
        assert config.logging["level"] == "DEBUG"

    def test_to_dict(self) -> None:
        """Test converting Config to dictionary."""
        config = Config()
        config.sandbox.timeout = 60.0
        config.logging = {"level": "DEBUG"}

        data = config.to_dict()

        assert data["sandbox"]["timeout"] == 60.0
        assert data["logging"]["level"] == "DEBUG"

    def test_to_yaml(self) -> None:
        """Test converting Config to YAML."""
        config = Config()
        config.sandbox.timeout = 60.0

        yaml_str = config.to_yaml()

        assert "sandbox:" in yaml_str
        assert "timeout: 60.0" in yaml_str

    def test_to_json(self) -> None:
        """Test converting Config to JSON."""
        config = Config()
        config.sandbox.timeout = 60.0

        json_str = config.to_json()

        assert '"sandbox"' in json_str
        assert '"timeout": 60.0' in json_str


class TestConfigLoader:
    """Test ConfigLoader class."""

    def test_load_default_config(self) -> None:
        """Test loading default configuration."""
        loader = ConfigLoader()
        config = loader.load()

        assert isinstance(config, Config)
        assert config.sandbox.timeout == 30.0

    def test_load_yaml_config(self, tmp_path: Path) -> None:
        """Test loading YAML configuration."""
        config_path = tmp_path / "config.yaml"
        config_path.write_text("""
sandbox:
  timeout: 60.0
  max_memory_mb: 1024
logging:
  level: DEBUG
""")

        loader = ConfigLoader(config_path)
        config = loader.load()

        assert config.sandbox.timeout == 60.0
        assert config.sandbox.security_config.max_memory_mb == 1024
        assert config.logging["level"] == "DEBUG"

    def test_load_json_config(self, tmp_path: Path) -> None:
        """Test loading JSON configuration."""
        config_path = tmp_path / "config.json"
        config_path.write_text("""
{
    "sandbox": {
        "timeout": 45.0,
        "max_memory_mb": 768
    },
    "logging": {
        "level": "WARNING"
    }
}
""")

        loader = ConfigLoader(config_path)
        config = loader.load()

        assert config.sandbox.timeout == 45.0
        assert config.sandbox.security_config.max_memory_mb == 768
        assert config.logging["level"] == "WARNING"

    def test_save_yaml_config(self, tmp_path: Path) -> None:
        """Test saving YAML configuration."""
        config_path = tmp_path / "config.yaml"
        config = Config()
        config.sandbox.timeout = 60.0
        config.sandbox.security_config.max_memory_mb = 1024

        loader = ConfigLoader(config_path)
        loader.save(config)

        assert config_path.exists()
        content = config_path.read_text()
        assert "timeout: 60.0" in content
        assert "max_memory_mb: 1024" in content

    def test_save_json_config(self, tmp_path: Path) -> None:
        """Test saving JSON configuration."""
        config_path = tmp_path / "config.json"
        config = Config()
        config.sandbox.timeout = 60.0

        loader = ConfigLoader(config_path)
        loader.save(config)

        assert config_path.exists()
        content = config_path.read_text()
        data = json.loads(content)
        assert data["sandbox"]["timeout"] == 60.0

    def test_create_default_config(self, tmp_path: Path) -> None:
        """Test creating default configuration."""
        config_path = tmp_path / "default.yaml"
        config = ConfigLoader.create_default(config_path)

        assert config.sandbox.timeout == 30.0
        assert config.sandbox.security_config.max_memory_mb == 512
        assert config.runtime.get("environment", {}).get("PYTHONUNBUFFERED") == "1"
        assert config_path.exists()

    def test_load_nonexistent_config(self) -> None:
        """Test loading nonexistent configuration."""
        loader = ConfigLoader(Path("/nonexistent/config.yaml"))
        config = loader.load()

        assert isinstance(config, Config)
