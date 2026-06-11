"""CLI interface for AegisPy."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import click

from .config import Config, ConfigLoader
from .core.logging_config import setup_logging
from .sandbox import SecureSandbox, SandboxConfig
from .core.security import SecurityConfig

logger = logging.getLogger(__name__)

# Global config storage
_ctx_config: Config | None = None


@click.group()
@click.version_option(version="0.1.0", prog_name="aegispy")
@click.option(
    "--verbose", "-v",
    count=True,
    help="Increase verbosity (can be used multiple times)"
)
@click.option(
    "--log-file",
    type=click.Path(),
    help="Path to log file"
)
@click.option(
    "--config", "-c",
    type=click.Path(),
    help="Path to configuration file"
)
@click.pass_context
def main(ctx: click.Context, verbose: int, log_file: str | None, config: str | None) -> None:
    """AegisPy - Secure code sandbox with TUI."""
    global _ctx_config
    
    level = logging.WARNING
    if verbose == 1:
        level = logging.INFO
    elif verbose >= 2:
        level = logging.DEBUG
    
    log_path = Path(log_file) if log_file else None
    setup_logging(level, log_path)
    
    # Load configuration
    if config:
        loader = ConfigLoader(Path(config))
        _ctx_config = loader.load()
        logger.info("Loaded configuration from: %s", config)
    else:
        loader = ConfigLoader()
        _ctx_config = loader.load()
    
    logger.info("AegisPy started with verbosity=%d", verbose)
    ctx.obj = _ctx_config


@main.command()
@click.argument("code", required=False)
@click.option(
    "--file", "-f",
    type=click.Path(exists=True),
    help="Path to Python file to execute"
)
@click.option(
    "--memory", "-m",
    type=int,
    default=None,
    help="Maximum memory in MB (default: from config)"
)
@click.option(
    "--timeout", "-t",
    type=float,
    default=None,
    help="Execution timeout in seconds (default: from config)"
)
@click.option(
    "--no-security-check",
    is_flag=True,
    help="Disable security analysis (NOT RECOMMENDED)"
)
@click.pass_context
def run(ctx: click.Context, code: str | None, file: str | None, memory: int | None, timeout: float | None, no_security_check: bool) -> None:
    """Execute Python code in secure sandbox.
    
    Either provide code as argument or use --file to specify a Python file.
    """
    global _ctx_config
    cfg = ctx.obj or _ctx_config or Config()
    
    if not code and not file:
        click.echo("Error: Provide code or use --file option", err=True)
        sys.exit(1)
    
    if file:
        try:
            code = Path(file).read_text()
        except OSError as e:
            click.echo(f"Error reading file: {e}", err=True)
            sys.exit(1)
    
    try:
        # Use config values or command line overrides
        mem = memory if memory is not None else cfg.sandbox.security_config.max_memory_mb
        tout = timeout if timeout is not None else cfg.sandbox.timeout
        
        security_config = SecurityConfig(max_memory_mb=mem)
        sandbox_config = SandboxConfig(
            security_config=security_config,
            timeout=tout,
        )
        
        sandbox = SecureSandbox(sandbox_config)
        
        if not no_security_check:
            click.echo("Running security analysis...", err=True)
        
        result = sandbox.execute(code)
        
        if result.stdout:
            click.echo(result.stdout)
        
        if result.stderr:
            click.echo(result.stderr, err=True)
        
        click.echo(f"\nExecution time: {result.execution_time:.3f}s", err=True)
        click.echo(f"Memory usage: {result.memory_usage_mb:.2f} MB", err=True)
        click.echo(f"Exit code: {result.exit_code}", err=True)
        
        if result.is_timeout:
            click.echo("WARNING: Execution timed out", err=True)
        
        sys.exit(result.exit_code)
        
    except ValueError as e:
        click.echo(f"Security error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Execution error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument("file", type=click.Path(exists=True))
@click.option(
    "--output", "-o",
    type=click.Path(),
    help="Output file for report (default: stdout)"
)
def analyze(file: str, output: str | None) -> None:
    """Analyze Python file for security issues.
    
    Performs static analysis to detect dangerous patterns and imports.
    """
    from .core.security import DangerousPatternDetector
    
    try:
        code = Path(file).read_text()
    except OSError as e:
        click.echo(f"Error reading file: {e}", err=True)
        sys.exit(1)
    
    detector = DangerousPatternDetector()
    result = detector.analyze(code)
    
    output_lines = []
    output_lines.append("=" * 60)
    output_lines.append("Security Analysis Report")
    output_lines.append("=" * 60)
    output_lines.append(f"File: {file}")
    output_lines.append(f"Risk Level: {result['risk_level'].upper()}")
    output_lines.append(f"Risk Score: {result['risk_score']}")
    output_lines.append(f"Safe to Execute: {'Yes' if result['is_safe'] else 'No'}")
    output_lines.append("")
    
    if result["imports"]:
        output_lines.append("Dangerous Imports:")
        for imp in result["imports"]:
            output_lines.append(f"  - {imp}")
        output_lines.append("")
    
    if result["functions"]:
        output_lines.append("Dangerous Function Calls:")
        for func in result["functions"]:
            output_lines.append(f"  - {func}")
        output_lines.append("")
    
    if result["patterns"]:
        output_lines.append("Dangerous Patterns:")
        for pattern in result["patterns"][:10]:
            output_lines.append(f"  - {pattern}")
        if len(result["patterns"]) > 10:
            output_lines.append(f"  ... and {len(result['patterns']) - 10} more")
        output_lines.append("")
    
    report = "\n".join(output_lines)
    
    if output:
        try:
            Path(output).write_text(report)
            click.echo(f"Report saved to: {output}")
        except OSError as e:
            click.echo(f"Error writing report: {e}", err=True)
            sys.exit(1)
    else:
        click.echo(report)


@main.command()
def tui() -> None:
    """Start interactive TUI mode."""
    try:
        from .ui.tui import main as tui_main
        tui_main()
    except ImportError as e:
        click.echo(f"TUI module not available: {e}", err=True)
        click.echo("Install with: pip install aegispy[tui]", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
