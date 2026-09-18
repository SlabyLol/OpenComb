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
from opencomb.pak import PackageManager
from opencomb.prompt import PromptCombiner
from opencomb.recipe import RecipeRunner
from opencomb.report import ReportGenerator
from opencomb.template import TemplateRenderer
from opencomb.utils import load_text, is_url

app = typer.Typer(
    name="opencomb",
    help="OpenComb – Smart Combiner + Package Helper for developers",
    add_completion=True,
    no_args_is_help=True,
    rich_markup_mode="rich",
)
console = Console()

# Sub-app for package management (oc-pak)
pak_app = typer.Typer(help="Install / search / manage packages from PyPI (oc-pak)")
app.add_typer(pak_app, name="pak")


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
    """OpenComb – combine, merge, generate, prompt, template, recipe, pak."""
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
        result = combiner.combine_files(local_files, add_headers=not no_headers, deduplicate_imports=not no_dedupe)
        if format_code:
            result = CodeFormatter().format(result)
        if output:
            output.write_text(result, encoding="utf-8")
            console.print(f"[green]✓[/] Combined {len(files)} files → [cyan]{output}[/]")
        else:
            console.print(Panel(Syntax(result, "python", theme="monokai", line_numbers=True), title="Combined Code", border_style="cyan"))
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
        console.print(Panel(Syntax(text, "yaml", theme="monokai", line_numbers=True), title="Merged Config", border_style="green"))


@app.command("env")
def env_cmd(
    files: list[Path] = typer.Argument(..., help=".env files to merge"),
    output: Optional[Path] = typer.Option(None, "--output", "-o"),
    include_os: bool = typer.Option(False, "--include-os"),
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
    report: bool = typer.Option(False, "--report"),
    html: bool = typer.Option(False, "--html"),
) -> None:
    """Generate parameter combinations (cartesian / pairwise / sample)."""
    if params is None:
        console.print("[yellow]No --params given.[/] Using demo parameters.\n")
        parameters = {"learning_rate": [0.001, 0.01, 0.1], "batch_size": [16, 32], "optimizer": ["adam", "sgd"]}
    else:
        text = params.read_text(encoding="utf-8")
        parameters = yaml.safe_load(text) if params.suffix.lower() in (".yaml", ".yml") else json.loads(text)
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
            reporter.save_html(reporter.combinations_html(combos, method=method), output)
        elif str(output).endswith((".md", ".markdown")):
            reporter.save_markdown(reporter.combinations_markdown(combos, method=method), output)
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
        path = Path("opencomb_report.md")
        reporter.save_markdown(reporter.combinations_markdown(combos, method=method), path)
        console.print(f"[green]✓[/] Markdown report → [cyan]{path}[/]")
    if html:
        path = Path("opencomb_report.html")
        reporter.save_html(reporter.combinations_html(combos, method=method), path)
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
        result = combiner.from_files(system_files=system, instruction_file=instruction, context_files=context, examples_file=examples, user_file=user)
    except Exception as e:
        console.print(f"[red]Error:[/] {e}")
        raise typer.Exit(1)
    if not result.strip():
        console.print("[yellow]Nothing to combine.[/]")
        raise typer.Exit(1)
    if output:
        output.write_text(result, encoding="utf-8")
        console.print(f"[green]✓[/] Prompt → [cyan]{output}[/]")
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
        context = (yaml.safe_load(text) if data.suffix.lower() in (".yaml", ".yml") else json.loads(text)) or {}
    renderer = TemplateRenderer(strict=strict)
    try:
        if len(templates) == 1:
            result = renderer.render_string(templates[0].read_text(encoding="utf-8"), **context)
        else:
            result = renderer.combine_and_render(templates, data=context)
    except Exception as e:
        console.print(f"[red]Template error:[/] {e}")
        raise typer.Exit(1)
    if output:
        output.write_text(result, encoding="utf-8")
        console.print(f"[green]✓[/] Rendered → [cyan]{output}[/]")
    else:
        console.print(Panel(Syntax(result, "text", theme="monokai", line_numbers=True), title="Rendered", border_style="blue"))


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
    console.print(f"[green]✓[/] Recipe [cyan]{results.get('_recipe', 'recipe')}[/] executed")
    if dry_run:
        console.print("[yellow]Dry-run – no files written[/]")
    table = Table(title="Recipe Steps")
    table.add_column("Step", style="cyan")
    table.add_column("Status")
    table.add_column("Output")
    for key in ("combine", "merge", "template", "prompt", "generate"):
        if key in results:
            table.add_row(key, "[green]done[/]", str(results.get(f"{key}_output", "—")))
    console.print(table)


@app.command("format")
def format_cmd(
    files: list[Path] = typer.Argument(...),
    prefer: str = typer.Option("ruff", "--prefer"),
    inplace: bool = typer.Option(False, "--inplace", "-i"),
) -> None:
    """Format Python files (ruff / black / basic)."""
    formatter = CodeFormatter()
    for f in files:
        try:
            formatted = formatter.format(f.read_text(encoding="utf-8"), prefer=prefer)
            if inplace:
                f.write_text(formatted, encoding="utf-8")
                console.print(f"[green]✓[/] Formatted [cyan]{f}[/]")
            else:
                console.print(Panel(Syntax(formatted, "python", theme="monokai", line_numbers=True), title=str(f)))
        except Exception as e:
            console.print(f"[red]Error {f}:[/] {e}")


# ─── PAK (oc-pak) ──────────────────────────────────────────
@pak_app.command("add")
def pak_add(
    packages: list[str] = typer.Argument(..., help="Package names (e.g. requests rich>=13)"),
    upgrade: bool = typer.Option(False, "--upgrade", "-U"),
    user: bool = typer.Option(False, "--user"),
) -> None:
    """Install packages from PyPI (like pip install)."""
    pm = PackageManager()
    console.print(f"[cyan]Installing:[/] {', '.join(packages)}")
    result = pm.add(packages, upgrade=upgrade, user=user)
    if result.returncode == 0:
        console.print("[green]✓[/] Packages installed successfully")
    else:
        console.print("[red]Installation finished with errors[/]")
        raise typer.Exit(result.returncode)


@pak_app.command("remove")
def pak_remove(packages: list[str] = typer.Argument(...)) -> None:
    """Uninstall packages."""
    pm = PackageManager()
    result = pm.remove(packages)
    if result.returncode == 0:
        console.print("[green]✓[/] Packages removed")
    else:
        raise typer.Exit(result.returncode)


@pak_app.command("list")
def pak_list() -> None:
    """List installed packages."""
    pm = PackageManager()
    pkgs = pm.list_installed()
    table = Table(title="Installed Packages", show_header=True)
    table.add_column("Name", style="cyan")
    table.add_column("Version")
    for p in sorted(pkgs, key=lambda x: x.get("name", "").lower()):
        table.add_row(p.get("name", ""), p.get("version", ""))
    console.print(table)
    console.print(f"\n[bold]Total:[/] {len(pkgs)}")


@pak_app.command("show")
def pak_show(name: str = typer.Argument(...)) -> None:
    """Show details of an installed package."""
    pm = PackageManager()
    info = pm.show(name)
    if not info:
        console.print(f"[red]Package not found:[/] {name}")
        raise typer.Exit(1)
    table = Table(title=f"Package: {name}", show_header=False)
    table.add_column("Key", style="cyan")
    table.add_column("Value")
    for k, v in info.items():
        table.add_row(k, v)
    console.print(table)


@pak_app.command("info")
def pak_info(name: str = typer.Argument(..., help="Package name on PyPI")) -> None:
    """Show package info from PyPI (latest version, summary, etc.)."""
    pm = PackageManager()
    info = pm.info_summary(name)
    if not info:
        console.print(f"[red]Package not found on PyPI:[/] {name}")
        raise typer.Exit(1)
    table = Table(title=f"PyPI: {info.get('name')}", show_header=False)
    table.add_column("Field", style="cyan")
    table.add_column("Value")
    for k, v in info.items():
        if v:
            table.add_row(k, str(v))
    console.print(table)


@pak_app.command("freeze")
def pak_freeze(output: Optional[Path] = typer.Option(None, "--output", "-o")) -> None:
    """Freeze installed packages (pip freeze)."""
    pm = PackageManager()
    text = pm.freeze(output)
    if output:
        console.print(f"[green]✓[/] Wrote [cyan]{output}[/]")
    else:
        console.print(text)


@app.command("doctor")
def doctor_cmd() -> None:
    """Check OpenComb installation and optional tools."""
    console.print(Panel.fit(f"[bold cyan]OpenComb Doctor[/] v{__version__}", border_style="cyan"))
    table = Table(show_header=True)
    table.add_column("Component")
    table.add_column("Status")
    table.add_row("Core package", "[green]OK[/]")
    import subprocess, sys
    for mod, label in [("ruff", "ruff"), ("black", "black"), ("jinja2", "Jinja2")]:
        try:
            if mod in ("ruff", "black"):
                subprocess.run([sys.executable, "-m", mod, "--version"], capture_output=True, check=True)
                table.add_row(label, "[green]available[/]")
            else:
                m = __import__(mod)
                table.add_row(label, f"[green]{getattr(m, '__version__', 'ok')}[/]")
        except Exception:
            table.add_row(label, "[yellow]not found[/]" if mod != "jinja2" else "[red]missing[/]")
    console.print(table)


@app.command("info")
def info_cmd() -> None:
    """Show information about OpenComb."""
    console.print(
        Panel.fit(
            f"""[bold cyan]OpenComb[/] v{__version__}

Smart Combiner + Package helper for developers.

[bold]Main commands:[/]
  combine · merge · env · generate · prompt · template · recipe · format

[bold]Package (oc-pak):[/]
  [cyan]pak add[/]      Install packages from PyPI
  [cyan]pak remove[/]   Uninstall packages
  [cyan]pak list[/]     List installed packages
  [cyan]pak show[/]     Show installed package details
  [cyan]pak info[/]     Show PyPI package info
  [cyan]pak freeze[/]   pip freeze

[bold]Other:[/] doctor · info

[bold]Repo:[/] https://github.com/SlabyLol/OpenComb
""",
            title="OpenComb",
            border_style="cyan",
        )
    )


if __name__ == "__main__":
    app()
