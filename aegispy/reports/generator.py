"""Report generation for AegisPy."""

from __future__ import annotations

import csv
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class ReportFormat(Enum):
    """Supported report formats."""

    JSON = "json"
    CSV = "csv"
    TEXT = "text"
    HTML = "html"


@dataclass
class ReportData:
    """Data for report generation.

    Attributes:
        title: Report title
        description: Report description
        timestamp: Report generation timestamp
        metadata: Additional metadata
        sections: Report sections
        execution_results: Execution results
        security_analysis: Security analysis results
    """

    title: str = "AegisPy Report"
    description: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)
    sections: list[dict[str, Any]] = field(default_factory=list)
    execution_results: list[dict[str, Any]] = field(default_factory=list)
    security_analysis: dict[str, Any] = field(default_factory=dict)


class ReportGenerator:
    """Report generator for AegisPy.

    Supports multiple output formats: JSON, CSV, Text, HTML.
    """

    def __init__(self, output_dir: Path | None = None) -> None:
        """Initialize report generator.

        Args:
            output_dir: Directory for report output
        """
        self.output_dir = Path(output_dir) if output_dir else Path.cwd()
        self._report_count = 0

        logger.info("ReportGenerator initialized with output_dir=%s", self.output_dir)

    def generate(
        self,
        data: ReportData,
        format: ReportFormat = ReportFormat.JSON,
        filename: str | None = None,
    ) -> Path:
        """Generate a report.

        Args:
            data: Report data
            format: Output format
            filename: Optional filename (without extension)

        Returns:
            Path to generated report
        """
        self._report_count += 1

        if filename is None:
            filename = f"report_{self._report_count}_{self._timestamp_str()}"

        output_path = self.output_dir / f"{filename}.{format.value}"

        if format == ReportFormat.JSON:
            content = self._generate_json(data)
        elif format == ReportFormat.CSV:
            content = self._generate_csv(data)
        elif format == ReportFormat.TEXT:
            content = self._generate_text(data)
        elif format == ReportFormat.HTML:
            content = self._generate_html(data)
        else:
            raise ValueError(f"Unsupported format: {format}")

        try:
            output_path.write_text(content)
            logger.info("Generated report: %s", output_path)
            return output_path
        except OSError as e:
            logger.error("Failed to write report: %s", e)
            raise

    def _timestamp_str(self) -> str:
        """Get timestamp string."""
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def _generate_json(self, data: ReportData) -> str:
        """Generate JSON report."""
        report_dict = {
            "title": data.title,
            "description": data.description,
            "timestamp": data.timestamp.isoformat(),
            "metadata": data.metadata,
            "sections": data.sections,
            "execution_results": data.execution_results,
            "security_analysis": data.security_analysis,
        }
        return json.dumps(report_dict, indent=2, default=str)

    def _generate_csv(self, data: ReportData) -> str:
        """Generate CSV report."""
        import io

        output = io.StringIO()

        # Write metadata section
        writer = csv.writer(output)
        writer.writerow(["Section", "Key", "Value"])

        for key, value in data.metadata.items():
            writer.writerow(["Metadata", key, str(value)])

        # Write execution results
        for i, result in enumerate(data.execution_results):
            for key, value in result.items():
                writer.writerow([f"Execution {i}", key, str(value)])

        # Write security analysis
        for key, value in data.security_analysis.items():
            writer.writerow(["Security", key, str(value)])

        return output.getvalue()

    def _generate_text(self, data: ReportData) -> str:
        """Generate text report."""
        lines = [
            "=" * 60,
            data.title,
            "=" * 60,
            "",
            f"Generated: {data.timestamp}",
            f"Description: {data.description}",
            "",
        ]

        if data.metadata:
            lines.append("Metadata:")
            for key, value in data.metadata.items():
                lines.append(f"  {key}: {value}")
            lines.append("")

        if data.execution_results:
            lines.append("Execution Results:")
            for i, result in enumerate(data.execution_results, 1):
                lines.append(f"\n  Result {i}:")
                for key, value in result.items():
                    lines.append(f"    {key}: {value}")

        if data.security_analysis:
            lines.append("\nSecurity Analysis:")
            for key, value in data.security_analysis.items():
                lines.append(f"  {key}: {value}")

        lines.append("")
        lines.append("=" * 60)

        return "\n".join(lines)

    def _generate_html(self, data: ReportData) -> str:
        """Generate HTML report."""
        timestamp = data.timestamp.strftime("%Y-%m-%d %H:%M:%S")

        sections_html = ""
        for section in data.sections:
            sections_html += f'<section class="section"><h3>{section.get("title", "Section")}</h3><p>{section.get("content", "")}</p></section>\n'

        results_rows = ""
        for result in data.execution_results:
            cells = "".join(f"<td>{value}</td>" for value in result.values())
            results_rows += f"<tr>{cells}</tr>\n"

        html_parts = [
            "<!DOCTYPE html>",
            '<html lang="en">',
            "<head>",
            '    <meta charset="UTF-8">',
            '    <meta name="viewport" content="width=device-width, initial-scale=1.0">',
            f"    <title>{data.title}</title>",
            "    <style>",
            "        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }",
            "        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }",
            "        h1 { color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }",
            "        h2 { color: #555; margin-top: 30px; }",
            "        h3 { color: #666; }",
            "        table { width: 100%; border-collapse: collapse; margin: 20px 0; }",
            "        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }",
            "        th { background: #007bff; color: white; }",
            "        tr:hover { background: #f5f5f5; }",
            "        .section { margin: 20px 0; padding: 15px; background: #f9f9f9; border-radius: 4px; }",
            "        .metadata { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }",
            "        .metadata-item { padding: 10px; background: #e9ecef; border-radius: 4px; }",
            "        .timestamp { color: #888; font-size: 0.9em; }",
            "    </style>",
            "</head>",
            "<body>",
            '    <div class="container">',
            f"        <h1>{data.title}</h1>",
            f'        <p class="timestamp">Generated: {timestamp}</p>',
        ]

        if data.description:
            html_parts.append(f"        <p>{data.description}</p>")

        html_parts.append(sections_html)

        if data.metadata:
            metadata_items = "".join(
                f'<div class="metadata-item"><strong>{k}</strong>: {v}</div>'
                for k, v in data.metadata.items()
            )
            html_parts.extend(
                [
                    "        <h2>Metadata</h2>",
                    '        <div class="metadata">',
                    f"            {metadata_items}",
                    "        </div>",
                ]
            )

        if data.execution_results:
            headers = "".join(f"<th>{k}</th>" for k in data.execution_results[0])
            html_parts.extend(
                [
                    "        <h2>Execution Results</h2>",
                    "        <table>",
                    "            <thead>",
                    f"                <tr>{headers}</tr>",
                    "            </thead>",
                    "            <tbody>",
                ]
            )
            for result in data.execution_results:
                cells = "".join(f"<td>{value}</td>" for value in result.values())
                html_parts.append(f"                <tr>{cells}</tr>")
            html_parts.extend(["            </tbody>", "        </table>"])

        if data.security_analysis:
            security_items = "".join(
                f"<p><strong>{k}</strong>: {v}</p>" for k, v in data.security_analysis.items()
            )
            html_parts.extend(
                [
                    "        <h2>Security Analysis</h2>",
                    '        <div class="section">',
                    f"            {security_items}",
                    "        </div>",
                ]
            )

        html_parts.extend(["    </div>", "</body>", "</html>"])
        return "\n".join(html_parts)

    def generate_summary(
        self,
        data: ReportData,
        filename: str | None = None,
    ) -> Path:
        """Generate a summary report (text format).

        Args:
            data: Report data
            filename: Optional filename

        Returns:
            Path to summary report
        """
        return self.generate(data, ReportFormat.TEXT, filename)
