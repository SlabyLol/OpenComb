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

@app.command("combine")
def combine_cmd(files: list[str] = typer.Argument(...), output: Optional[Path] = typer.Option(None, "--output", "-o"), no_headers: bool = typer.Option(False, "--no-headers"), no_dedupe: bool = typer.Option(False, "--no-dedupe"), format_code: bool = typer.Option(False, "--format")) -> None:
    """Combine Python files (local or remote URLs)."""
    combiner = CodeCombiner()
    local_files, tmp_files = [], []
    try:
        for f in files:
            if is_url(f):
                tmp = Path(f"/tmp/opencomb_{abs(hash(f))}.py")
                tmp.write_text(load_text(f), encoding="utf-8")
                local_files.append(tmp); tmp_files.append(tmp)
            else:
                local_files.append(Path(f))
        result = combiner.combine_files(local_files, add_headers=not no_headers, deduplicate_imports=not no_dedupe)
        if format_code:
            result = CodeFormatter().format(result)
        if output:
            output.write_text(result, encoding="utf-8")
            console.print(f"[green]✓[/] Combined → [cyan]{output}[/]")
        else:
            console.print(Panel(Syntax(result, "python", theme="monokai", line_numbers=True), title="Combined Code", border_style="cyan"))
    except Exception as e:
        console.print(f"[red]Error:[/] {e}"); raise typer.Exit(1)
    finally:
        for t in tmp_files: t.unlink(missing_ok=True)

@app.command("merge")
def merge_cmd(files: list[Path] = typer.Argument(...), output: Optional[Path] = typer.Option(None, "--output", "-o"), strategy: str = typer.Option("deep", "--strategy", "-s"), format: Optional[str] = typer.Option(None, "--format", "-f")) -> None:
    """Merge YAML/JSON/TOML configs."""
    merger = ConfigMerger()
    try:
        result = merger.merge_files(files, strategy=strategy)
    except Exception as e:
        console.print(f"[red]Error:[/] {e}"); raise typer.Exit(1)
    if output:
        merger.save(result, output, format=format)
        console.print(f"[green]✓[/] Merged → [cyan]{output}[/]")
    else:
        text = yaml.dump(result, default_flow_style=False, allow_unicode=True, sort_keys=False)
        console.print(Panel(Syntax(text, "yaml", theme="monokai", line_numbers=True), title="Merged Config", border_style="green"))

@app.command("env")
def env_cmd(files: list[Path] = typer.Argument(...), output: Optional[Path] = typer.Option(None, "--output", "-o"), include_os: bool = typer.Option(False, "--include-os"), export: bool = typer.Option(False, "--export")) -> None:
    """Merge .env files."""
    merger = EnvMerger()
    result = merger.merge_files(files, include_os=include_os)
    if export:
        script = merger.to_export_script(result)
        if output: output.write_text(script, encoding="utf-8"); console.print(f"[green]✓[/] {output}")
        else: console.print(script)
        return
    if output:
        merger.save(result, output); console.print(f"[green]✓[/] {output}")
    else:
        table = Table(title="Merged Environment"); table.add_column("Key", style="cyan"); table.add_column("Value")
        for k, v in sorted(result.items()): table.add_row(k, v[:80])
        console.print(table)

@app.command("generate")
def generate_cmd(params: Optional[Path] = typer.Option(None, "--params", "-p"), method: str = typer.Option("cartesian", "--method", "-m"), limit: Optional[int] = typer.Option(None, "--limit", "-n"), output: Optional[Path] = typer.Option(None, "--output", "-o"), seed: Optional[int] = typer.Option(None, "--seed"), report: bool = typer.Option(False, "--report"), html: bool = typer.Option(False, "--html")) -> None:
    """Generate combinatorial parameter sets."""
    if params is None:
        parameters = {"learning_rate": [0.001, 0.01, 0.1], "batch_size": [16, 32], "optimizer": ["adam", "sgd"]}
    else:
        text = params.read_text(encoding="utf-8")
        parameters = yaml.safe_load(text) if params.suffix.lower() in (".yaml", ".yml") else json.loads(text)
    gen = CombinatorialGenerator(seed=seed)
    if method == "cartesian": combos = gen.cartesian(parameters, limit=limit)
    elif method == "pairwise": combos = gen.pairwise(parameters, limit=limit)
    else: combos = gen.sample(parameters, n=limit or 10)
    reporter = ReportGenerator()
    if output:
        if str(output).endswith(".html"): reporter.save_html(reporter.combinations_html(combos, method=method), output)
        elif str(output).endswith((".md", ".markdown")): reporter.save_markdown(reporter.combinations_markdown(combos, method=method), output)
        else: reporter.save_jsonl(combos, output)
        console.print(f"[green]✓[/] {len(combos)} combos → [cyan]{output}[/]")
    else:
        table = Table(title=f"Combinations ({method})")
        if combos:
            for key in combos[0]: table.add_column(str(key), style="cyan")
            for c in combos[:40]: table.add_row(*[str(v) for v in c.values()])
        console.print(table); console.print(f"Total: {len(combos)}")
    if report: reporter.save_markdown(reporter.combinations_markdown(combos, method=method), Path("opencomb_report.md")); console.print("[green]✓ report.md[/]")
    if html: reporter.save_html(reporter.combinations_html(combos, method=method), Path("opencomb_report.html")); console.print("[green]✓ report.html[/]")

@app.command("prompt")
def prompt_cmd(system: Optional[list[Path]] = typer.Option(None, "--system", "-s"), instruction: Optional[Path] = typer.Option(None, "--instruction", "-i"), context: Optional[list[Path]] = typer.Option(None, "--context", "-c"), examples: Optional[Path] = typer.Option(None, "--examples", "-e"), user: Optional[Path] = typer.Option(None, "--user", "-u"), output: Optional[Path] = typer.Option(None, "--output", "-o")) -> None:
    """Build structured LLM prompts."""
    result = PromptCombiner().from_files(system_files=system, instruction_file=instruction, context_files=context, examples_file=examples, user_file=user)
    if output: output.write_text(result, encoding="utf-8"); console.print(f"[green]✓[/] {output}")
    else: console.print(Panel(Markdown(result), title="Prompt", border_style="magenta"))

@app.command("template")
def template_cmd(templates: list[Path] = typer.Argument(...), data: Optional[Path] = typer.Option(None, "--data", "-d"), output: Optional[Path] = typer.Option(None, "--output", "-o"), strict: bool = typer.Option(True, "--strict/--no-strict")) -> None:
    """Render Jinja2 templates."""
    context = {}
    if data:
        text = data.read_text(encoding="utf-8")
        context = (yaml.safe_load(text) if data.suffix.lower() in (".yaml", ".yml") else json.loads(text)) or {}
    r = TemplateRenderer(strict=strict)
    result = r.render_string(templates[0].read_text(encoding="utf-8"), **context) if len(templates) == 1 else r.combine_and_render(templates, data=context)
    if output: output.write_text(result, encoding="utf-8"); console.print(f"[green]✓[/] {output}")
    else: console.print(Panel(Syntax(result, "text", theme="monokai"), title="Rendered", border_style="blue"))

@app.command("recipe")
def recipe_cmd(recipe_file: Path = typer.Argument(...), dry_run: bool = typer.Option(False, "--dry-run"), verbose: bool = typer.Option(False, "--verbose", "-v")) -> None:
    """Run declarative recipe."""
    results = RecipeRunner(base_dir=recipe_file.parent).run(recipe_file, dry_run=dry_run)
    console.print(f"[green]✓[/] Recipe [cyan]{results.get('_recipe')}[/]")
    table = Table(title="Steps"); table.add_column("Step", style="cyan"); table.add_column("Output")
    for key in ("packages", "combine", "merge", "template", "prompt", "generate"):
        if key in results: table.add_row(key, str(results.get(f"{key}_output", results.get(key, "—"))[:60]))
    console.print(table)

@app.command("format")
def format_cmd(files: list[Path] = typer.Argument(...), prefer: str = typer.Option("ruff", "--prefer"), inplace: bool = typer.Option(False, "--inplace", "-i")) -> None:
    """Format Python files."""
    fmt = CodeFormatter()
    for f in files:
        formatted = fmt.format(f.read_text(encoding="utf-8"), prefer=prefer)
        if inplace: f.write_text(formatted, encoding="utf-8"); console.print(f"[green]✓[/] {f}")
        else: console.print(Panel(Syntax(formatted, "python", theme="monokai"), title=str(f)))

@app.command("init")
def init_cmd(name: str = typer.Argument(...), path: Optional[Path] = typer.Option(None, "--path", "-p"), description: str = typer.Option("A new project", "--description", "-d"), flat: bool = typer.Option(False, "--flat")) -> None:
    """Scaffold a new Python project."""
    try:
        root = ProjectHelper().init(name, path=path, description=description, src_layout=not flat)
    except Exception as e:
        console.print(f"[red]Error:[/] {e}"); raise typer.Exit(1)
    console.print(f"[green]✓[/] Project at [cyan]{root}[/]")
    console.print(ProjectHelper().tree(root, max_depth=3))

@app.command("tree")
def tree_cmd(path: Path = typer.Argument(Path(".")), depth: int = typer.Option(4, "--depth", "-d")) -> None:
    """Show directory tree."""
    console.print(ProjectHelper().tree(path, max_depth=depth))

@app.command("bump")
def bump_cmd(part: str = typer.Argument("patch"), file: Path = typer.Option(Path("pyproject.toml"), "--file", "-f")) -> None:
    """Bump version in pyproject.toml (major|minor|patch)."""
    h = ProjectHelper()
    old, new = h.current_version(file), h.bump_version(file, part=part)
    console.print(f"[green]✓[/] {old} → [cyan]{new}[/]")

@app.command("check")
def check_cmd(paths: Optional[list[str]] = typer.Option(None, "--path"), skip_tests: bool = typer.Option(False, "--skip-tests")) -> None:
    """Run ruff + format check + pytest."""
    results = Checker().run_all(paths=paths or ["src", "tests"], skip_tests=skip_tests)
    table = Table(title="Check"); table.add_column("Tool"); table.add_column("Status")
    all_ok = True
    for r in results:
        table.add_row(r["tool"], "[green]OK[/]" if r["ok"] else "[red]FAIL[/]")
        if not r["ok"]: all_ok = False
    console.print(table)
    if not all_ok: raise typer.Exit(1)
    console.print("[green]✓ All checks passed[/]")

@app.command("ignore")
def ignore_cmd(output: Path = typer.Option(Path(".gitignore"), "--output", "-o")) -> None:
    """Generate Python .gitignore."""
    path = ProjectHelper().write_gitignore(output)
    console.print(f"[green]✓[/] {path}")

@app.command("drill")
def drill_cmd(path: Path = typer.Argument(Path("."), help="Directory to lock into")) -> None:
    """Enter interactive OpenComb shell locked to a directory (bright-red messages)."""
    try:
        start_drill(path)
    except Exception as e:
        console.print(f"[bold bright_red]Error:[/] {e}")
        raise typer.Exit(1)

@pak_app.command("add")
def pak_add(packages: list[str] = typer.Argument(...), upgrade: bool = typer.Option(False, "--upgrade", "-U"), user: bool = typer.Option(False, "--user")) -> None:
    """Install packages from PyPI."""
    console.print(f"[cyan]Installing:[/] {', '.join(packages)}")
    r = PackageManager().add(packages, upgrade=upgrade, user=user)
    if r.returncode == 0: console.print("[green]✓ installed[/]")
    else: raise typer.Exit(r.returncode)

@pak_app.command("remove")
def pak_remove(packages: list[str] = typer.Argument(...)) -> None:
    """Uninstall packages."""
    r = PackageManager().remove(packages)
    if r.returncode == 0: console.print("[green]✓ removed[/]")
    else: raise typer.Exit(r.returncode)

@pak_app.command("list")
def pak_list() -> None:
    """List installed packages."""
    pkgs = PackageManager().list_installed()
    table = Table(title="Installed"); table.add_column("Name", style="cyan"); table.add_column("Version")
    for p in sorted(pkgs, key=lambda x: x.get("name", "").lower()): table.add_row(p.get("name", ""), p.get("version", ""))
    console.print(table); console.print(f"Total: {len(pkgs)}")

@pak_app.command("show")
def pak_show(name: str = typer.Argument(...)) -> None:
    """Show installed package details."""
    info = PackageManager().show(name)
    if not info: console.print(f"[red]Not found:[/] {name}"); raise typer.Exit(1)
    table = Table(title=name, show_header=False); table.add_column("K", style="cyan"); table.add_column("V")
    for k, v in info.items(): table.add_row(k, v)
    console.print(table)

@pak_app.command("info")
def pak_info(name: str = typer.Argument(...)) -> None:
    """Show package info from PyPI."""
    info = PackageManager().info_summary(name)
    if not info: console.print(f"[red]Not on PyPI:[/] {name}"); raise typer.Exit(1)
    table = Table(title=f"PyPI: {info.get('name')}", show_header=False); table.add_column("F", style="cyan"); table.add_column("V")
    for k, v in info.items():
        if v: table.add_row(k, str(v))
    console.print(table)

@pak_app.command("freeze")
def pak_freeze(output: Optional[Path] = typer.Option(None, "--output", "-o")) -> None:
    """pip freeze."""
    text = PackageManager().freeze(output)
    if output: console.print(f"[green]✓[/] {output}")
    else: console.print(text)

@app.command("doctor")
def doctor_cmd() -> None:
    """Check installation."""
    console.print(Panel.fit(f"[bold cyan]OpenComb Doctor[/] v{__version__}", border_style="cyan"))
    table = Table(); table.add_column("Component"); table.add_column("Status")
    table.add_row("Core", "[green]OK[/]")
    import subprocess, sys
    for mod, label in [("ruff", "ruff"), ("black", "black"), ("jinja2", "Jinja2")]:
        try:
            if mod in ("ruff", "black"):
                subprocess.run([sys.executable, "-m", mod, "--version"], capture_output=True, check=True)
                table.add_row(label, "[green]ok[/]")
            else:
                m = __import__(mod); table.add_row(label, f"[green]{getattr(m, '__version__', 'ok')}[/]")
        except Exception:
            table.add_row(label, "[yellow]missing[/]")
    console.print(table)

@app.command("info")
def info_cmd() -> None:
    """Show OpenComb info."""
    console.print(Panel.fit(f"""[bold cyan]OpenComb[/] v{__version__}

[bold]Main:[/] combine · merge · env · generate · prompt · template · recipe · format
[bold]Project:[/] init · tree · bump · check · ignore · drill
[bold]Packages:[/] pak add · remove · list · show · info · freeze
[bold]Other:[/] doctor · info

Repo: https://github.com/SlabyLol/OpenComb""", title="OpenComb", border_style="cyan"))

if __name__ == "__main__":
    app()
