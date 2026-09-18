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
from opencomb.env import EnvMerger
from opencomb.formatter import CodeFormatter
from opencomb.prompt import PromptCombiner
from opencomb.recipe import RecipeRunner
from opencomb.report import ReportGenerator
from opencomb.template import TemplateRenderer
from opencomb.utils import load_text, is_url

app = typer.Typer(
    name="opencomb",
    help="OpenComb – Smart Combiner for Code, Configs, Prompts, Templates, Recipes, Env & more",
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
        None, "--version", "-V", callback=version_callback, is_eager=True,
        help="Show version and exit.",
    ),
) -> None:
    """OpenComb – combine code, merge configs, build prompts, render templates, run recipes."""
    pass


@app.command("combine")
def combine_cmd(
    files: list[str] = typer.Argument(..., help="Python files or URLs to combine"),
    output: Optional[Path] = typer.Option(None, "--output", "-o"),
    no_headers: bool = typer.Option(False, "--no-headers"),
    no_dedupe: bool = typer.Option(False, "--no-dedupe"),
    format_code: bool = typer.Option(False, "--format", help="Format result with ruff/black"),
) -> None:
    """Combine multiple Python source files (local or remote URLs) into one."""
    combiner = CodeCombiner()
    local_files = []
    tmp_files = []
    try:
        for f in files:
            if is_url(f):
                content = load_text(f)
                tmp = Path(f"/tmp/opencomb_{abs(hash(f))}.py")
                tmp.write_text(content, encoding="utf-8")
                local_files.append(tmp)
                tmp_files.append(tmp)
            else:
                local_files.append(Path(f))

        result = combiner.combine_files(
            local_files,
            add_headers=not no_headers,
            deduplicate_imports=not no_dedupe,
        )

        if format_code:
            formatter = CodeFormatter()
            result = formatter.format(result)

        if output:
            output.write_text(result, encoding="utf-8")
            console.print(f"[green]✓[/] Combined {len(files)} files → [cyan]{output}[/]")
        else:
            syntax = Syntax(result, "python", theme="monokai", line_numbers=True)
            console.print(Panel(syntax, title="Combined Code", border_style="cyan"))
    except Exception as e:
        console.print(f"[red]Error:[/] {e}")
        raise typer.Exit(1)
    finally:
        for t in tmp_files:
            t.unlink(missing_ok=True)


@app.command("merge")
def merge_cmd(
    files: list[Path] = typer.Argument(...),
    output: Optional[Path] = typer.Option(None, "--output", "-o"),
    strategy: str = typer.Option("deep", "--strategy", "-s"),
    format: Optional[str] = typer.Option(None, "--format", "-f"),
) -> None:
    """Intelligently merge YAML / JSON / TOML configuration files."""
    merger = ConfigMerger()
    try:
        result = merger.merge_files(files, strategy=strategy)
    except Exception as e:
        console.print(f"[red]Error:[/] {e}")
        raise typer.Exit(1)

    if output:
        merger.save(result, output, format=format)
        console.print(f"[green]✓[/] Merged {len(files)} configs → [cyan]{output}[/]")
    else:
        text = yaml.dump(result, default_flow_style=False, allow_unicode=True, sort_keys=False)
        syntax = Syntax(text, "yaml", theme="monokai", line_numbers=True)
        console.print(Panel(syntax, title="Merged Config", border_style="green"))


@app.command("env")
def env_cmd(
    files: list[Path] = typer.Argument(..., help=".env files to merge"),
    output: Optional[Path] = typer.Option(None, "--output", "-o"),
    include_os: bool = typer.Option(False, "--include-os", help="Include process environment"),
    export: bool = typer.Option(False, "--export", help="Generate bash export script"),
) -> None:
    """Merge .env files (later files override earlier ones)."""
    merger = EnvMerger()
    try:
        result = merger.merge_files(files, include_os=include_os)
    except Exception as e:
        console.print(f"[red]Error:[/] {e}")
        raise typer.Exit(1)

    if export:
        script = merger.to_export_script(result)
        if output:
            output.write_text(script, encoding="utf-8")
            console.print(f"[green]✓[/] Export script → [cyan]{output}[/]")
        else:
            console.print(script)
        return

    if output:
        merger.save(result, output)
        console.print(f"[green]✓[/] Merged {len(files)} env files → [cyan]{output}[/]")
    else:
        table = Table(title="Merged Environment", show_header=True)
        table.add_column("Key", style="cyan")
        table.add_column("Value")
        for k, v in sorted(result.items()):
            table.add_row(k, v if len(v) < 80 else v[:77] + "...")
        console.print(table)


@app.command("generate")
def generate_cmd(
    params: Optional[Path] = typer.Option(None, "--params", "-p"),
    method: str = typer.Option("cartesian", "--method", "-m"),
    limit: Optional[int] = typer.Option(None, "--limit", "-n"),
    output: Optional[Path] = typer.Option(None, "--output", "-o"),
    seed: Optional[int] = typer.Option(None, "--seed"),
    report: bool = typer.Option(False, "--report", help="Generate Markdown report"),
    html: bool = typer.Option(False, "--html", help="Generate HTML report"),
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

    reporter = ReportGenerator()

    if output:
        if str(output).endswith(".html"):
            html_content = reporter.combinations_html(combos, method=method)
            reporter.save_html(html_content, output)
        elif str(output).endswith((".md", ".markdown")):
            md = reporter.combinations_markdown(combos, method=method)
            reporter.save_markdown(md, output)
        else:
            reporter.save_jsonl(combos, output)
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

    if report:
        md = reporter.combinations_markdown(combos, method=method)
        path = Path("opencomb_report.md")
        reporter.save_markdown(md, path)
        console.print(f"[green]✓[/] Markdown report → [cyan]{path}[/]")

    if html:
        html_content = reporter.combinations_html(combos, method=method)
        path = Path("opencomb_report.html")
        reporter.save_html(html_content, path)
        console.print(f"[green]✓[/] HTML report → [cyan]{path}[/]")


@app.command("prompt")
def prompt_cmd(
    system: Optional[list[Path]] = typer.Option(None, "--system", "-s"),
    instruction: Optional[Path] = typer.Option(None, "--instruction", "-i"),
    context: Optional[list[Path]] = typer.Option(None, "--context", "-c"),
    examples: Optional[Path] = typer.Option(None, "--examples", "-e"),
    user: Optional[Path] = typer.Option(None, "--user", "-u"),
    output: Optional[Path] = typer.Option(None, "--output", "-o"),
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
    templates: list[Path] = typer.Argument(...),
    data: Optional[Path] = typer.Option(None, "--data", "-d"),
    output: Optional[Path] = typer.Option(None, "--output", "-o"),
    strict: bool = typer.Option(True, "--strict/--no-strict"),
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
    recipe_file: Path = typer.Argument(...),
    dry_run: bool = typer.Option(False, "--dry-run"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """Run a declarative OpenComb recipe."""
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
            out = results.get(f"{key}_output", "—")
            table.add_row(key, "[green]done[/]", str(out))
    console.print(table)

    if verbose:
        for key in ("combine", "merge", "template", "prompt"):
            if key in results and isinstance(results[key], str):
                console.print(Panel(
                    Syntax(results[key][:2000], "text", theme="monokai"),
                    title=f"{key} preview", border_style="dim",
                ))


@app.command("format")
def format_cmd(
    files: list[Path] = typer.Argument(...),
    prefer: str = typer.Option("ruff", "--prefer", help="ruff | black | auto"),
    inplace: bool = typer.Option(False, "--inplace", "-i", help="Overwrite files"),
) -> None:
    """Format Python files (uses ruff or black if available)."""
    formatter = CodeFormatter()
    for f in files:
        try:
            original = f.read_text(encoding="utf-8")
            formatted = formatter.format(original, prefer=prefer)
            if inplace:
                f.write_text(formatted, encoding="utf-8")
                console.print(f"[green]✓[/] Formatted [cyan]{f}[/]")
            else:
                syntax = Syntax(formatted, "python", theme="monokai", line_numbers=True)
                console.print(Panel(syntax, title=str(f), border_style="cyan"))
        except Exception as e:
            console.print(f"[red]Error formatting {f}:[/] {e}")


@app.command("doctor")
def doctor_cmd() -> None:
    """Check OpenComb installation and optional tools."""
    console.print(Panel.fit(f"[bold cyan]OpenComb Doctor[/] v{__version__}", border_style="cyan"))

    table = Table(show_header=True)
    table.add_column("Component")
    table.add_column("Status")

    table.add_row("Core package", "[green]OK[/]")

    import subprocess, sys
    try:
        subprocess.run([sys.executable, "-m", "ruff", "--version"], capture_output=True, check=True)
        table.add_row("ruff (formatter)", "[green]available[/]")
    except Exception:
        table.add_row("ruff (formatter)", "[yellow]not found[/] (optional)")

    try:
        subprocess.run([sys.executable, "-m", "black", "--version"], capture_output=True, check=True)
        table.add_row("black (formatter)", "[green]available[/]")
    except Exception:
        table.add_row("black (formatter)", "[yellow]not found[/] (optional)")

    try:
        import jinja2
        table.add_row("Jinja2", f"[green]{jinja2.__version__}[/]")
    except ImportError:
        table.add_row("Jinja2", "[red]missing[/]")

    console.print(table)
    console.print("\n[dim]Tip: pip install 'opencomb[format]' for ruff + black support[/]")


@app.command("info")
def info_cmd() -> None:
    """Show information about OpenComb."""
    console.print(
        Panel.fit(
            f"""[bold cyan]OpenComb[/] v{__version__}

Smart Combiner for developers.

[bold]Commands:[/]
  [cyan]combine[/]    Combine Python files (local + remote URLs)
  [cyan]merge[/]      Deep-merge YAML / JSON / TOML configs
  [cyan]env[/]        Merge .env files + export scripts
  [cyan]generate[/]   Combinatorial generation + reports
  [cyan]prompt[/]     Build structured LLM prompts
  [cyan]template[/]   Render Jinja2 templates
  [cyan]recipe[/]     Run declarative recipes
  [cyan]format[/]     Format Python code
  [cyan]doctor[/]     Check installation
  [cyan]info[/]       Show this information

[bold]Repository:[/] https://github.com/SlabyLol/OpenComb
""",
            title="OpenComb",
            border_style="cyan",
        )
    )


if __name__ == "__main__":
    app()
