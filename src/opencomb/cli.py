"""OpenComb command-line interface – powerful and beautiful."""

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
from opencomb.combiner import CodeCombiner, ConfigMerger
from opencomb.combinatorial import CombinatorialGenerator
from opencomb.prompt import PromptCombiner
from opencomb.recipe import RecipeRunner
from opencomb.template import TemplateRenderer

app = typer.Typer(
    name="opencomb",
    help="OpenComb – Smart Combiner for Code, Configs, Prompts, Templates, Recipes & more",
    add_completion=True,
    no_args_is_help=True,
    rich_markup_mode="rich",
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
    """OpenComb – combine code, merge configs, build prompts, render templates, run recipes."""
    pass


@app.command("combine")
def combine_cmd(
    files: list[Path] = typer.Argument(..., help="Python files to combine"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Write result to file"),
    no_headers: bool = typer.Option(False, "--no-headers", help="Do not add source headers"),
    no_dedupe: bool = typer.Option(False, "--no-dedupe", help="Do not deduplicate imports"),
) -> None:
    """Combine multiple Python source files into one clean module."""
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
    files: list[Path] = typer.Argument(..., help="Config files to merge (later override earlier)"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Write merged config"),
    strategy: str = typer.Option("deep", "--strategy", "-s", help="deep or shallow"),
    format: Optional[str] = typer.Option(None, "--format", "-f", help="yaml | json | toml"),
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
        text = yaml.dump(result, default_flow_style=False, allow_unicode=True, sort_keys=False)
        syntax = Syntax(text, "yaml", theme="monokai", line_numbers=True)
        console.print(Panel(syntax, title="Merged Config", border_style="green"))


@app.command("generate")
def generate_cmd(
    params: Optional[Path] = typer.Option(None, "--params", "-p", help="YAML/JSON params file"),
    method: str = typer.Option("cartesian", "--method", "-m", help="cartesian | pairwise | sample"),
    limit: Optional[int] = typer.Option(None, "--limit", "-n", help="Max combinations"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Write as JSON Lines"),
    seed: Optional[int] = typer.Option(None, "--seed", help="Random seed"),
    report: bool = typer.Option(False, "--report", help="Generate Markdown report"),
) -> None:
    """Generate parameter combinations (cartesian / pairwise / sample)."""
    if params is None:
        console.print("[yellow]No --params given.[/] Using demo parameters.\n")
        parameters = {
            "learning_rate": [0.001, 0.01, 0.1],
            "batch_size": [16, 32],
            "optimizer": ["adam", "sgd"],
        }
    else:
        text = params.read_text(encoding="utf-8")
        if params.suffix.lower() in (".yaml", ".yml"):
            parameters = yaml.safe_load(text)
        else:
            parameters = json.loads(text)

    if not isinstance(parameters, dict):
        console.print("[red]Parameters must be a mapping of name → list[/]")
        raise typer.Exit(1)

    gen = CombinatorialGenerator(seed=seed)

    if method == "cartesian":
        combos = gen.cartesian(parameters, limit=limit)
    elif method == "pairwise":
        combos = gen.pairwise(parameters, limit=limit)
    elif method == "sample":
        combos = gen.sample(parameters, n=limit or 10)
    else:
        console.print(f"[red]Unknown method:[/] {method}")
        raise typer.Exit(1)

    if output:
        with output.open("w", encoding="utf-8") as f:
            for c in combos:
                f.write(json.dumps(c, ensure_ascii=False) + "\n")
        console.print(f"[green]✓[/] Generated [cyan]{len(combos)}[/] combinations → [cyan]{output}[/]")
    else:
        table = Table(title=f"Generated Combinations ({method})", show_header=True)
        if combos:
            for key in combos[0].keys():
                table.add_column(str(key), style="cyan")
            for combo in combos[:40]:
                table.add_row(*[str(v) for v in combo.values()])
            if len(combos) > 40:
                console.print(f"[dim]… and {len(combos) - 40} more[/]")
        console.print(table)
        console.print(f"\n[bold]Total:[/] {len(combos)} combinations")

    if report and combos:
        md_lines = [
            f"# Combination Report ({method})",
            f"\nTotal combinations: **{len(combos)}**\n",
            "| # | " + " | ".join(combos[0].keys()) + " |",
            "|---|" + "|".join(["---"] * len(combos[0])) + "|",
        ]
        for i, c in enumerate(combos, 1):
            md_lines.append(f"| {i} | " + " | ".join(str(v) for v in c.values()) + " |")
        report_path = Path("opencomb_report.md")
        report_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")
        console.print(f"[green]✓[/] Markdown report → [cyan]{report_path}[/]")


@app.command("prompt")
def prompt_cmd(
    system: Optional[list[Path]] = typer.Option(None, "--system", "-s", help="System prompt file(s)"),
    instruction: Optional[Path] = typer.Option(None, "--instruction", "-i", help="Instruction file"),
    context: Optional[list[Path]] = typer.Option(None, "--context", "-c", help="Context file(s)"),
    examples: Optional[Path] = typer.Option(None, "--examples", "-e", help="YAML examples file"),
    user: Optional[Path] = typer.Option(None, "--user", "-u", help="User query file"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Write final prompt"),
) -> None:
    """Build a structured LLM prompt from components."""
    combiner = PromptCombiner()

    try:
        result = combiner.from_files(
            system_files=system,
            instruction_file=instruction,
            context_files=context,
            examples_file=examples,
            user_file=user,
        )
    except Exception as e:
        console.print(f"[red]Error:[/] {e}")
        raise typer.Exit(1)

    if not result.strip():
        console.print("[yellow]Nothing to combine. Provide at least one component.[/]")
        raise typer.Exit(1)

    if output:
        output.write_text(result, encoding="utf-8")
        console.print(f"[green]✓[/] Prompt written → [cyan]{output}[/]")
    else:
        console.print(Panel(Markdown(result), title="Combined Prompt", border_style="magenta"))


@app.command("template")
def template_cmd(
    templates: list[Path] = typer.Argument(..., help="Jinja2 template file(s)"),
    data: Optional[Path] = typer.Option(None, "--data", "-d", help="YAML/JSON data file"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Write rendered result"),
    strict: bool = typer.Option(True, "--strict/--no-strict", help="Strict undefined variables"),
) -> None:
    """Render one or more Jinja2 templates with data."""
    context: dict = {}
    if data:
        text = data.read_text(encoding="utf-8")
        if data.suffix.lower() in (".yaml", ".yml"):
            context = yaml.safe_load(text) or {}
        else:
            context = json.loads(text)

    renderer = TemplateRenderer(strict=strict)

    try:
        if len(templates) == 1:
            content = templates[0].read_text(encoding="utf-8")
            result = renderer.render_string(content, **context)
        else:
            result = renderer.combine_and_render(templates, data=context)
    except Exception as e:
        console.print(f"[red]Template error:[/] {e}")
        raise typer.Exit(1)

    if output:
        output.write_text(result, encoding="utf-8")
        console.print(f"[green]✓[/] Rendered → [cyan]{output}[/]")
    else:
        syntax = Syntax(result, "text", theme="monokai", line_numbers=True)
        console.print(Panel(syntax, title="Rendered Template", border_style="blue"))


@app.command("recipe")
def recipe_cmd(
    recipe_file: Path = typer.Argument(..., help="Path to recipe YAML"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be done"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show intermediate results"),
) -> None:
    """Run a declarative OpenComb recipe (combine + merge + template + prompt + generate)."""
    runner = RecipeRunner(base_dir=recipe_file.parent)

    try:
        results = runner.run(recipe_file, dry_run=dry_run)
    except Exception as e:
        console.print(f"[red]Recipe error:[/] {e}")
        raise typer.Exit(1)

    name = results.get("_recipe", "recipe")
    console.print(f"[green]✓[/] Recipe [cyan]{name}[/] executed successfully")

    if dry_run:
        console.print("[yellow]Dry-run mode – no files written[/]")

    table = Table(title="Recipe Steps", show_header=True)
    table.add_column("Step", style="cyan")
    table.add_column("Status")
    table.add_column("Output")

    for key in ("combine", "merge", "template", "prompt", "generate"):
        if key in results:
            out_key = f"{key}_output"
            out = results.get(out_key, "—")
            table.add_row(key, "[green]done[/]", str(out))

    console.print(table)

    if verbose:
        for key in ("combine", "merge", "template", "prompt"):
            if key in results and isinstance(results[key], str):
                console.print(Panel(
                    Syntax(results[key][:2000], "text", theme="monokai"),
                    title=f"{key} preview",
                    border_style="dim",
                ))


@app.command("info")
def info_cmd() -> None:
    """Show information about OpenComb."""
    console.print(
        Panel.fit(
            f"""[bold cyan]OpenComb[/] v{__version__}

Smart Combiner for developers – code, configs, prompts, templates & recipes.

[bold]Commands:[/]
  [cyan]combine[/]    Combine multiple Python files into one
  [cyan]merge[/]      Deep-merge YAML / JSON / TOML configs
  [cyan]generate[/]   Generate combinatorial parameter sets
  [cyan]prompt[/]     Build structured LLM prompts
  [cyan]template[/]   Render Jinja2 templates
  [cyan]recipe[/]     Run a full declarative recipe
  [cyan]info[/]       Show this information

[bold]Repository:[/] https://github.com/SlabyLol/OpenComb
""",
            title="OpenComb",
            border_style="cyan",
        )
    )


if __name__ == "__main__":
    app()
