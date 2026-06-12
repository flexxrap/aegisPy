"""CLI command for report generation."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import click

from aegispy.reports import ReportData, ReportFormat, ReportGenerator

logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "--execution-id", "-e", type=str, default=None, help="Execution ID to generate report for"
)
@click.option("--output", "-o", type=click.Path(), default=None, help="Output file path")
@click.option(
    "--format",
    "-f",
    type=click.Choice([f.value for f in ReportFormat]),
    default="json",
    help="Report format (default: json)",
)
@click.option("--title", "-t", type=str, default="AegisPy Report", help="Report title")
@click.option("--description", "-d", type=str, default="", help="Report description")
@click.option("--json-data", "-j", type=str, default=None, help="JSON data to include in report")
def report(
    execution_id: str | None,
    output: str | None,
    format: str,
    title: str,
    description: str,
    json_data: str | None,
) -> None:
    """Generate execution reports in various formats.

    GENERATES reports for code execution sessions with security analysis.
    """
    # Parse format
    report_format = ReportFormat(format)

    # Create report data
    report_data = ReportData(
        title=title,
        description=description,
        metadata={
            "execution_id": execution_id or "unknown",
            "generator": "aegispy",
        },
    )

    # Add JSON data if provided
    if json_data:
        import json

        try:
            data = json.loads(json_data)
            report_data.metadata.update(data)
        except json.JSONDecodeError as e:
            click.echo(f"Warning: Failed to parse JSON data: {e}", err=True)

    # Create generator
    output_path = Path(output) if output else None
    generator = ReportGenerator(output_dir=output_path and output_path.parent)

    # Generate report
    try:
        report_file = generator.generate(report_data, report_format)
        click.echo(f"Report generated: {report_file}")
    except Exception as e:
        click.echo(f"Error generating report: {e}", err=True)
        sys.exit(1)
