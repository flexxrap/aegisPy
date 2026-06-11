"""Configuration management for AegisPy."""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml

from ..core.security import SecurityConfig
from ..sandbox import SandboxConfig

logger = logging.getLogger(__name__)


@dataclass
class Config:
    """Main configuration class for AegisPy.
    
    Attributes:
        sandbox: Sandbox configuration
        security: Security configuration
        logging: Logging configuration
        ui: UI configuration
        runtime: Runtime configuration
    """
    sandbox: SandboxConfig = field(default_factory=SandboxConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    logging: dict[str, Any] = field(default_factory=dict)
    ui: dict[str, Any] = field(default_factory=dict)
    runtime: dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Config":
        """Create Config from dictionary.
        
        Args:
            data: Configuration dictionary
            
        Returns:
            Config instance
        """
        config = cls()
        
        if "sandbox" in data:
            sandbox_data = data["sandbox"]
            config.sandbox = SandboxConfig(
                security_config=SecurityConfig(
                    max_memory_mb=sandbox_data.get("max_memory_mb", 512),
                    max_cpu_time=sandbox_data.get("max_cpu_time", 30),
                    max_file_size_mb=sandbox_data.get("max_file_size_mb", 10),
                    max_processes=sandbox_data.get("max_processes", 10),
                    network_enabled=sandbox_data.get("network_enabled", False),
                ),
                timeout=sandbox_data.get("timeout", 30.0),
            )
        
        if "security" in data:
            security_data = data["security"]
            config.security = SecurityConfig(
                max_memory_mb=security_data.get("max_memory_mb", 512),
                max_cpu_time=security_data.get("max_cpu_time", 30),
                max_file_size_mb=security_data.get("max_file_size_mb", 10),
                max_processes=security_data.get("max_processes", 10),
                network_enabled=security_data.get("network_enabled", False),
            )
        
        if "logging" in data:
            config.logging = data["logging"]
        
        if "ui" in data:
            config.ui = data["ui"]
        
        if "runtime" in data:
            config.runtime = data["runtime"]
        
        return config
    
    def to_dict(self) -> dict[str, Any]:
        """Convert Config to dictionary.
        
        Returns:
            Configuration dictionary
        """
        return {
            "sandbox": {
                "timeout": self.sandbox.timeout,
                "max_memory_mb": self.sandbox.security_config.max_memory_mb,
                "max_cpu_time": self.sandbox.security_config.max_cpu_time,
                "max_file_size_mb": self.sandbox.security_config.max_file_size_mb,
                "max_processes": self.sandbox.security_config.max_processes,
                "network_enabled": self.sandbox.security_config.network_enabled,
            },
            "security": {
                "max_memory_mb": self.security.max_memory_mb,
                "max_cpu_time": self.security.max_cpu_time,
                "max_file_size_mb": self.security.max_file_size_mb,
                "max_processes": self.security.max_processes,
                "network_enabled": self.security.network_enabled,
            },
            "logging": self.logging,
            "ui": self.ui,
            "runtime": self.runtime,
        }
    
    def to_yaml(self) -> str:
        """Convert Config to YAML string.
        
        Returns:
            YAML formatted string
        """
        return yaml.dump(self.to_dict(), default_flow_style=False, sort_keys=False)
    
    def to_json(self, indent: int = 2) -> str:
        """Convert Config to JSON string.
        
        Args:
            indent: JSON indentation level
            
        Returns:
            JSON formatted string
        """
        return json.dumps(self.to_dict(), indent=indent)


class ConfigLoader:
    """Configuration loader for AegisPy.
    
    Supports loading configurations from YAML and JSON files.
    """
    
    DEFAULT_CONFIG_PATH = Path("config.yaml")
    
    def __init__(self, config_path: Path | None = None):
        """Initialize config loader.
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path or self.DEFAULT_CONFIG_PATH
        self._config: Config | None = None
    
    def load(self) -> Config:
        """Load configuration from file.
        
        Returns:
            Config instance
            
        Raises:
            FileNotFoundError: If configuration file doesn't exist
            ValueError: If file format is unsupported
        """
        if not self.config_path.exists():
            logger.info("No config file found, using defaults")
            return Config()
        
        try:
            content = self.config_path.read_text()
            
            if self.config_path.suffix in (".yaml", ".yml"):
                data = yaml.safe_load(content)
            elif self.config_path.suffix == ".json":
                data = json.loads(content)
            else:
                raise ValueError(f"Unsupported config format: {self.config_path.suffix}")
            
            self._config = Config.from_dict(data or {})
            logger.info("Loaded config from: %s", self.config_path)
            
            return self._config
            
        except yaml.YAMLError as e:
            logger.error("Failed to parse YAML config: %s", e)
            raise
        except json.JSONDecodeError as e:
            logger.error("Failed to parse JSON config: %s", e)
            raise
    
    def save(self, config: Config | None = None) -> None:
        """Save configuration to file.
        
        Args:
            config: Config to save. If None, saves current config.
        """
        config = config or self._config or Config()
        
        try:
            if self.config_path.suffix in (".yaml", ".yml"):
                content = config.to_yaml()
            elif self.config_path.suffix == ".json":
                content = config.to_json()
            else:
                raise ValueError(f"Unsupported config format: {self.config_path.suffix}")
            
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            self.config_path.write_text(content)
            logger.info("Saved config to: %s", self.config_path)
            
        except OSError as e:
            logger.error("Failed to save config: %s", e)
            raise
    
    @classmethod
    def create_default(cls, path: Path | None = None) -> Config:
        """Create default configuration.
        
        Args:
            path: Optional path to save default config
            
        Returns:
            Config instance with default values
        """
        config = Config()
        
        # Set sensible defaults
        config.sandbox.timeout = 30.0
        config.sandbox.security_config.max_memory_mb = 512
        config.sandbox.security_config.max_cpu_time = 30
        config.sandbox.security_config.max_file_size_mb = 10
        config.sandbox.security_config.max_processes = 10
        config.sandbox.security_config.network_enabled = False
        
        config.logging = {
            "level": "INFO",
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        }
        
        config.ui = {
            "theme": "default",
            "show_timings": True,
            "show_memory": True,
        }
        
        config.runtime = {
            "working_directory": None,
            "environment": {"PYTHONUNBUFFERED": "1"},
        }
        
        if path:
            cls(path).save(config)
        
        return config
