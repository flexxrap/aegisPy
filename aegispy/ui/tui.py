"""Terminal User Interface for AegisPy."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.live import Live
from rich.layout import Layout
from rich import box

from .sandbox import SecureSandbox, SandboxConfig
from .core.security import SecurityConfig, DangerousPatternDetector

logger = logging.getLogger(__name__)

console = Console()


def main() -> None:
    """Main entry point for TUI."""
    console.print(
        Panel(
            "[bold blue]AegisPy[/bold blue] - Secure Code Sandbox\n"
            "[dim]Press Ctrl+C to exit[/dim]",
            title="[bold]Welcome[/bold]",
            box=box.DOUBLE,
        )
    )
    
    # Initialize sandbox
    security_config = SecurityConfig(max_memory_mb=512, max_cpu_time=30)
    sandbox_config = SandboxConfig(security_config=security_config, timeout=30.0)
    sandbox = SecureSandbox(sandbox_config)
    detector = DangerousPatternDetector()
    
    while True:
        try:
            show_main_menu()
            choice = Prompt.ask("[bold]Choose an option[/bold]", choices=["1", "2", "3", "4"])
            
            if choice == "1":
                execute_code(sandbox)
            elif choice == "2":
                analyze_code()
            elif choice == "3":
                show_stats(sandbox)
            elif choice == "4":
                console.print("[green]Goodbye![/green]")
                break
                
        except KeyboardInterrupt:
            console.print("\n[yellow]Interrupted by user[/yellow]")
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            logger.exception("TUI error")


def show_main_menu() -> None:
    """Display main menu."""
    menu = Table(show_header=False, box=None, padding=(0, 1))
    menu.add_column("Option", style="cyan")
    menu.add_column("Description", style="dim")
    
    menu.add_row("1", "Execute Code")
    menu.add_row("2", "Analyze Code")
    menu.add_row("3", "Show Statistics")
    menu.add_row("4", "Exit")
    
    console.print(Panel(menu, title="[bold]Main Menu[/bold]", box=box.ROUNDED))


def execute_code(sandbox: SecureSandbox) -> None:
    """Execute code in interactive mode."""
    console.print("\n[bold cyan]Execute Code[/bold cyan]")
    console.print("[dim]Enter your Python code (type 'END' on a new line to finish):[/dim]")
    
    lines = []
    while True:
        try:
            line = Prompt.ask("")
            if line.strip() == "END":
                break
            lines.append(line)
        except KeyboardInterrupt:
            console.print("\n[dim]Execution cancelled[/dim]")
            return
    
    code = "\n".join(lines)
    if not code.strip():
        console.print("[yellow]Empty code provided[/yellow]")
        return
    
    # Security check
    console.print("[dim]Running security analysis...[/dim]")
    analysis = detector.analyze(code)
    
    if not analysis["is_safe"]:
        console.print(
            Panel(
                f"[red]Security Warning![/red]\n\n"
                f"Risk Level: [bold red]{analysis['risk_level'].upper()}[/bold red]\n"
                f"Risk Score: [bold red]{analysis['risk_score']}[/bold red]\n\n"
                "Dangerous items found:\n"
                f"  • Imports: {len(analysis['imports'])}\n"
                f"  • Functions: {len(analysis['functions'])}\n"
                f"  • Patterns: {len(analysis['patterns'])}",
                title="[bold red]Security Analysis Failed[/bold red]",
                border_style="red",
            )
        )
        
        if not Confirm.ask("[yellow]Continue anyway?[/yellow]", default=False):
            return
    
    # Execute
    console.print("\n[dim]Executing...[/dim]")
    try:
        result = sandbox.execute(code)
        
        output_table = Table(show_header=False, box=box.SIMPLE)
        output_table.add_column("Label", style="cyan", width=12)
        output_table.add_column("Value", style="white")
        
        output_table.add_row("Exit Code:", str(result.exit_code))
        output_table.add_row("Time:", f"{result.execution_time:.3f}s")
        output_table.add_row("Memory:", f"{result.memory_usage_mb:.2f} MB")
        
        if result.stdout:
            console.print(Panel(result.stdout, title="[green]Output[/green]", border_style="green"))
        
        if result.stderr:
            console.print(Panel(result.stderr, title="[yellow]Errors[/yellow]", border_style="yellow"))
        
        console.print(Panel(output_table, box=box.ROUNDED))
        
    except ValueError as e:
        console.print(f"[red]Execution failed: {e}[/red]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def analyze_code() -> None:
    """Analyze code for security issues."""
    console.print("\n[bold cyan]Code Analysis[/bold cyan]")
    console.print("[dim]Enter code to analyze (type 'END' on a new line to finish):[/dim]")
    
    lines = []
    while True:
        try:
            line = Prompt.ask("")
            if line.strip() == "END":
                break
            lines.append(line)
        except KeyboardInterrupt:
            console.print("\n[dim]Analysis cancelled[/dim]")
            return
    
    code = "\n".join(lines)
    if not code.strip():
        console.print("[yellow]Empty code provided[/yellow]")
        return
    
    analysis = detector.analyze(code)
    
    # Create analysis report
    report = Table(show_header=False, box=box.ROUNDED)
    report.add_column("Metric", style="cyan", width=20)
    report.add_column("Value", style="white")
    
    risk_color = "green" if analysis["is_safe"] else "yellow" if analysis["risk_score"] < 15 else "red"
    report.add_row("Risk Level:", f"[{risk_color}]{analysis['risk_level'].upper()}[/{risk_color}]")
    report.add_row("Risk Score:", f"[{risk_color}]{analysis['risk_score']}[/{risk_color}]")
    report.add_row("Safe:", f"[{'green' if analysis['is_safe'] else 'red'}]{'Yes' if analysis['is_safe'] else 'No'}[/{'green' if analysis['is_safe'] else 'red'}]")
    report.add_row("Imports Found:", str(len(analysis["imports"])))
    report.add_row("Functions Found:", str(len(analysis["functions"])))
    report.add_row("Patterns Found:", str(len(analysis["patterns"])))
    
    console.print(Panel(report, title="[bold]Analysis Results[/bold]"))
    
    if analysis["imports"]:
        console.print("\n[dim]Dangerous Imports:[/dim]")
        for imp in analysis["imports"]:
            console.print(f"  • [red]{imp}[/red]")
    
    if analysis["functions"]:
        console.print("\n[dim]Dangerous Functions:[/dim]")
        for func in analysis["functions"]:
            console.print(f"  • [red]{func}[/red]")


def show_stats(sandbox: SecureSandbox) -> None:
    """Show sandbox statistics."""
    console.print("\n[bold cyan]Sandbox Statistics[/bold cyan]")
    
    stats_table = Table(box=box.ROUNDED)
    stats_table.add_column("Setting", style="cyan")
    stats_table.add_column("Value", style="white")
    
    stats_table.add_row("Memory Limit:", f"{sandbox.config.security_config.max_memory_mb} MB")
    stats_table.add_row("CPU Time Limit:", f"{sandbox.config.security_config.max_cpu_time}s")
    stats_table.add_row("Max Processes:", str(sandbox.config.security_config.max_processes))
    stats_table.add_row("Network Access:", str(sandbox.config.security_config.network_enabled))
    stats_table.add_row("Timeout:", f"{sandbox.config.timeout}s")
    
    console.print(stats_table)


if __name__ == "__main__":
    main()
