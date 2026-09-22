"""OpenComb CLI – everything developers need."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.markdown import Markdown

from opencomb import __version__
from opencomb.check import Checker
from opencomb.combiner import CodeCombiner, ConfigMerger
from opencomb.combinatorial import CombinatorialGenerator
from opencomb.drill import start_drill
from opencomb.env import EnvMerger
from opencomb.formatter import CodeFormatter
from opencomb.pak import PackageManager
from opencomb.project import ProjectHelper
from opencomb.prompt import PromptCombiner
from opencomb.recipe import RecipeRunner
from opencomb.report import ReportGenerator
from opencomb.template import TemplateRenderer
from opencomb.utils import load_text, is_url

app = typer.Typer(name="opencomb", help="OpenComb – Everything developers need", add_completion=True, no_args_is_help=True, rich_markup_mode="rich")
console = Console()
pak_app = typer.Typer(help="Install / search packages from PyPI (oc-pak)")
app.add_typer(pak_app, name="pak")

def version_callback(value: bool) -> None:
    if value:
        console.print(f"[bold cyan]OpenComb[/] version [green]{__version__}[/]")
        raise typer.Exit()

@app.callback()
def main(version: Optional[bool] = typer.Option(None, "--version", "-V", callback=version_callback, is_eager=True)) -> None:
    pass

# NOTE: Full implementation continues - this is a placeholder update.
# The complete cli.py with problemscanner will be pushed next.

@app.command("problemscanner")
def problemscanner_cmd(
    cli_mode: bool = typer.Option(False, "--cli", help="Run headless CLI scan instead of GUI"),
    json_out: bool = typer.Option(False, "--json", help="Output JSON (CLI mode)"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Write report to file"),
) -> None:
    """Scan this computer for problems that cause slowdowns or breakage (GUI or --cli)."""
    from opencomb.problem_scanner import launch_gui, main_cli
    if cli_mode:
        raise typer.Exit(main_cli(json_out=json_out, output=output))
    try:
        launch_gui()
    except RuntimeError as e:
        console.print(f"[yellow]{e}[/]")
        console.print("[dim]Falling back to CLI mode…[/]")
        raise typer.Exit(main_cli(json_out=json_out, output=output))

@app.command("info")
def info_cmd() -> None:
    """Show OpenComb info."""
    console.print(Panel.fit(f"""[bold cyan]OpenComb[/] v{__version__}

[bold]Scanner:[/] problemscanner  (GUI system problem scanner)
[bold]Main:[/] combine · merge · env · generate · prompt · template · recipe · format
[bold]Project:[/] init · tree · bump · check · ignore · drill · doctor · wizard · stacks
[bold]Packages:[/] pak add · remove · list · show · info · freeze
[bold]Connect:[/] occ  (SSH user@host)
[bold]PRT:[/] prt  (.prt language + REPL)

Repo: https://github.com/SlabyLol/OpenComb""", title="OpenComb", border_style="cyan"))

if __name__ == "__main__":
    app()
