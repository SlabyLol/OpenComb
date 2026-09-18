"""OpenComb command-line interface."""

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

from opencomb import __version__
from opencomb.combiner import CodeCombiner, ConfigMerger
from opencomb.combinatorial import CombinatorialGenerator

app = typer.Typer(
    name="opencomb",
    help="OpenComb – Smart Combiner for Code, Configs, Prompts & Combinatorial Generation",
    add_completion=False,
    no_args_is_help=True,
)
console = Console()


def version_callback(value: bool) -> None:
    if value:
        console.print(f"[bold cyan]OpenComb[/] version [green]{__version__}[/]")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-V",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit.",
    ),
) -> None:
    """OpenComb – combine code, merge configs, generate combinations."""
    pass


@app.command("combine")
def combine_cmd(
    files: list[Path] = typer.Argument(..., help="Python files to combine"),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Write result to this file"
    ),
    no_headers: bool = typer.Option(
        False, "--no-headers", help="Do not add source file headers"
    ),
    no_dedupe: bool = typer.Option(
        False, "--no-dedupe", help="Do not deduplicate imports"
    ),
) -> None:
    """Combine multiple Python source files into one."""
    combiner = CodeCombiner()
    try:
        result = combiner.combine_files(
            files,
            add_headers=not no_headers,
            deduplicate_imports=not no_dedupe,
        )
    except Exception as e:
        console.print(f"[red]Error:[/] {e}")
        raise typer.Exit(1)

    if output:
        output.write_text(result, encoding="utf-8")
        console.print(f"[green]✓[/] Combined {len(files)} files → [cyan]{output}[/]")
    else:
        syntax = Syntax(result, "python", theme="monokai", line_numbers=True)
        console.print(Panel(syntax, title="Combined Code", border_style="cyan"))


@app.command("merge")
def merge_cmd(
    files: list[Path] = typer.Argument(..., help="Config files to merge (order matters)"),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Write merged config to this file"
    ),
    strategy: str = typer.Option(
        "deep", "--strategy", "-s", help="Merge strategy: deep or shallow"
    ),
    format: Optional[str] = typer.Option(
        None, "--format", "-f", help="Output format: yaml, json, toml (auto-detected from -o)"
    ),
) -> None:
    """Intelligently merge YAML / JSON / TOML configuration files."""
    merger = ConfigMerger()
    try:
        result = merger.merge_files(files, strategy=strategy)
    except Exception as e:
        console.print(f"[red]Error:[/] {e}")
        raise typer.Exit(1)

    if output:
        try:
            merger.save(result, output, format=format)
            console.print(f"[green]✓[/] Merged {len(files)} configs → [cyan]{output}[/]")
        except Exception as e:
            console.print(f"[red]Error saving:[/] {e}")
            raise typer.Exit(1)
    else:
        # Pretty print as YAML by default
        text = yaml.dump(result, default_flow_style=False, allow_unicode=True, sort_keys=False)
        syntax = Syntax(text, "yaml", theme="monokai", line_numbers=True)
        console.print(Panel(syntax, title="Merged Config", border_style="green"))


@app.command("generate")
def generate_cmd(
    params: Optional[Path] = typer.Option(
        None,
        "--params",
        "-p",
        help="JSON/YAML file describing parameters (name → list of values)",
    ),
    method: str = typer.Option(
        "cartesian",
        "--method",
        "-m",
        help="Generation method: cartesian, pairwise, sample",
    ),
    limit: Optional[int] = typer.Option(
        None, "--limit", "-n", help="Maximum number of combinations"
    ),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Write combinations as JSON lines"
    ),
    seed: Optional[int] = typer.Option(None, "--seed", help="Random seed"),
) -> None:
    """
    Generate parameter combinations for testing or experiments.

    Example params file (YAML):
        learning_rate: [0.001, 0.01, 0.1]
        batch_size: [16, 32, 64]
        optimizer: [adam, sgd]
    """
    if params is None:
        console.print(
            "[yellow]No --params file given.[/] Showing a small demo instead.\n"
        )
        demo = {
            "learning_rate": [0.001, 0.01, 0.1],
            "batch_size": [16, 32],
            "optimizer": ["adam", "sgd"],
        }
        parameters = demo
    else:
        text = params.read_text(encoding="utf-8")
        if params.suffix.lower() in (".yaml", ".yml"):
            parameters = yaml.safe_load(text)
        else:
            parameters = json.loads(text)

    if not isinstance(parameters, dict):
        console.print("[red]Parameters file must contain a mapping of name → list[/]")
        raise typer.Exit(1)

    gen = CombinatorialGenerator(seed=seed)

    if method == "cartesian":
        combos = gen.cartesian(parameters, limit=limit)
    elif method == "pairwise":
        combos = gen.pairwise(parameters, limit=limit)
    elif method == "sample":
        n = limit or 10
        combos = gen.sample(parameters, n)
    else:
        console.print(f"[red]Unknown method:[/] {method}")
        raise typer.Exit(1)

    if output:
        with output.open("w", encoding="utf-8") as f:
            for c in combos:
                f.write(json.dumps(c, ensure_ascii=False) + "\n")
        console.print(
            f"[green]✓[/] Generated [cyan]{len(combos)}[/] combinations → [cyan]{output}[/]"
        )
    else:
        table = Table(title=f"Generated Combinations ({method})", show_header=True)
        if combos:
            for key in combos[0].keys():
                table.add_column(str(key), style="cyan")
            for combo in combos[:50]:  # safety limit for display
                table.add_row(*[str(v) for v in combo.values()])
            if len(combos) > 50:
                console.print(f"[dim]… and {len(combos) - 50} more[/]")
        console.print(table)
        console.print(f"\n[bold]Total:[/] {len(combos)} combinations")


@app.command("info")
def info_cmd() -> None:
    """Show information about OpenComb."""
    console.print(
        Panel.fit(
            f"""[bold cyan]OpenComb[/] v{__version__}

Smart Combiner for developers.

[bold]Commands:[/]
  combine   Combine multiple Python files into one
  merge     Deep-merge YAML / JSON / TOML configs
  generate  Generate combinatorial parameter sets
  info      Show this information

[bold]Repository:[/] https://github.com/SlabyLol/OpenComb
""",
            title="OpenComb",
            border_style="cyan",
        )
    )


if __name__ == "__main__":
    app()
