"""Example plugins for AegisPy."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from aegispy.plugins import Plugin

logger = logging.getLogger(__name__)


class ReportGeneratorPlugin(Plugin):
    """Plugin for generating execution reports."""
    
    @property
    def name(self) -> str:
        return "report_generator"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "Generates execution reports in various formats"
    
    @property
    def author(self) -> str:
        return "AegisPy Team"
    
    def initialize(self, config: dict[str, Any] | None = None) -> None:
        """Initialize report generator."""
        self.format = config.get("format", "json") if config else "json"
        self.output_dir = config.get("output_dir", Path.cwd()) if config else Path.cwd()
        logger.info("ReportGeneratorPlugin initialized with format=%s", self.format)
    
    def execute(self, data: dict[str, Any], filename: str = "report") -> str:
        """Execute report generation."""
        output_path = self.output_dir / f"{filename}.{self.format}"
        
        if self.format == "json":
            content = json.dumps(data, indent=2)
            output_path.write_text(content)
        elif self.format == "text":
            lines = [f"{k}: {v}" for k, v in data.items()]
            content = "\n".join(lines)
            output_path.write_text(content)
        else:
            raise ValueError(f"Unsupported format: {self.format}")
        
        logger.info("Generated report: %s", output_path)
        return str(output_path)
    
    def cleanup(self) -> None:
        """Clean up report generator."""
        pass


class LoggerPlugin(Plugin):
    """Plugin for enhanced logging."""
    
    @property
    def name(self) -> str:
        return "logger"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "Provides enhanced logging capabilities"
    
    @property
    def author(self) -> str:
        return "AegisPy Team"
    
    def initialize(self, config: dict[str, Any] | None = None) -> None:
        """Initialize logger plugin."""
        self.level = config.get("level", "INFO") if config else "INFO"
        self.file = config.get("file") if config else None
        logger.info("LoggerPlugin initialized with level=%s", self.level)
    
    def execute(self, message: str, level: str = "INFO") -> None:
        """Execute logging."""
        log_level = getattr(logging, level.upper(), logging.INFO)
        logger.log(log_level, "[LoggerPlugin] %s", message)
    
    def cleanup(self) -> None:
        """Clean up logger plugin."""
        pass


class ValidatorPlugin(Plugin):
    """Plugin for input validation."""
    
    @property
    def name(self) -> str:
        return "validator"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "Validates input data against schemas"
    
    @property
    def author(self) -> str:
        return "AegisPy Team"
    
    def initialize(self, config: dict[str, Any] | None = None) -> None:
        """Initialize validator plugin."""
        self.schemas = config.get("schemas", {}) if config else {}
        logger.info("ValidatorPlugin initialized with %d schemas", len(self.schemas))
    
    def execute(self, data: Any, schema_name: str | None = None) -> bool:
        """Execute validation."""
        if schema_name and schema_name in self.schemas:
            schema = self.schemas[schema_name]
            if isinstance(schema, dict):
                if isinstance(data, dict):
                    for key in schema:
                        if key not in data:
                            logger.warning("Missing key: %s", key)
                            return False
            return True
        
        return data is not None
    
    def cleanup(self) -> None:
        """Clean up validator plugin."""
        pass
