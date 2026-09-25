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

app = typer.Typer(
    name="opencomb",
    help="OpenComb – Everything developers need",
    add_completion=True,
    no_args_is_help=True,
    rich_markup_mode="rich",
)
console = Console()
pak_app = typer.Typer(help="Install / search packages from PyPI (oc-pak)")
app.add_typer(pak_app, name="pak")

# Zombie toolkit
try:
    from opencomb.zombie import zombie_app
    app.add_typer(zombie_app, name="zombie")
except Exception:
    pass

# Codec
try:
    from opencomb.codec import encode, decode, encode_file, decode_file
    codec_app = typer.Typer(help="OpenComb custom encoder / decoder")
    app.add_typer(codec_app, name="codec")

    @codec_app.command("encode")
    def codec_encode(
        source: Path = typer.Argument(..., help="File or - for stdin"),
        output: Path | None = typer.Option(None, "--output", "-o"),
        chunks: int = typer.Option(0, "--chunks", help="Split into N-char chunks (0=off)"),
    ) -> None:
        """Encode a file (zlib + OpenComb header + base64)."""
        if str(source) == "-":
            import sys
            data = sys.stdin.buffer.read()
            out = encode(data)
            if chunks > 0:
                for i in range(0, len(out), chunks):
                    console.print(out[i : i + chunks])
            else:
                console.print(out)
        else:
            dest = encode_file(source, output)
            console.print(f"[green]✓ encoded →[/] {dest}")

    @codec_app.command("decode")
    def codec_decode(
        source: Path = typer.Argument(..., help="Encoded .oc file or - for stdin"),
        output: Path | None = typer.Option(None, "--output", "-o"),
    ) -> None:
        """Decode an OpenComb payload back to original bytes."""
        if str(source) == "-":
            import sys
            payload = sys.stdin.read()
            data = decode(payload)
            sys.stdout.buffer.write(data)
        else:
            dest = decode_file(source, output)
            console.print(f"[green]✓ decoded →[/] {dest}")
except Exception:
    pass


def version_callback(value: bool) -> None:
    if value:
        console.print(f"[bold cyan]OpenComb[/] version [green]{__version__}[/]")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None, "--version", "-V", callback=version_callback, is_eager=True
    ),
) -> None:
    pass


@app.command("combine")
def combine_cmd(
    files: list[str] = typer.Argument(...),
    output: Optional[Path] = typer.Option(None, "--output", "-o"),
    no_headers: bool = typer.Option(False, "--no-headers"),
    no_dedupe: bool = typer.Option(False, "--no-dedupe"),
    format_code: bool = typer.Option(False, "--format"),
) -> None:
    """Combine Python files (local or remote URLs)."""
    combiner = CodeCombiner()
    local_files, tmp_files = [], []
    try:
        for f in files:
            if is_url(f):
                tmp = Path(f"/tmp/opencomb_{abs(hash(f))}.py")
                tmp.write_text(load_text(f), encoding="utf-8")
                local_files.append(tmp)
                tmp_files.append(tmp)
            else:
                local_files.append(Path(f))
        result = combiner.combine_files(
            local_files, add_headers=not no_headers, deduplicate_imports=not no_dedupe
        )
        if format_code:
            result = CodeFormatter().format(result)
        if output:
            output.write_text(result, encoding="utf-8")
            console.print(f"[green]✓[/] Combined → [cyan]{output}[/]")
        else:
            console.print(
                Panel(
                    Syntax(result, "python", theme="monokai", line_numbers=True),
                    title="Combined Code",
                    border_style="cyan",
                )
            )
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
    """Merge YAML/JSON/TOML configs."""
    merger = ConfigMerger()
    try:
        result = merger.merge_files(files, strategy=strategy)
    except Exception as e:
        console.print(f"[red]Error:[/] {e}")
        raise typer.Exit(1)
    if output:
        merger.save(result, output, format=format)
        console.print(f"[green]✓[/] Merged → [cyan]{output}[/]")
    else:
        text = yaml.dump(result, default_flow_style=False, allow_unicode=True, sort_keys=False)
        console.print(
            Panel(
                Syntax(text, "yaml", theme="monokai", line_numbers=True),
                title="Merged Config",
                border_style="green",
            )
        )


@app.command("env")
def env_cmd(
    files: list[Path] = typer.Argument(...),
    output: Optional[Path] = typer.Option(None, "--output", "-o"),
    include_os: bool = typer.Option(False, "--include-os"),
    export: bool = typer.Option(False, "--export"),
) -> None:
    """Merge .env files."""
    merger = EnvMerger()
    result = merger.merge_files(files, include_os=include_os)
    if export:
        script = merger.to_export_script(result)
        if output:
            output.write_text(script, encoding="utf-8")
            console.print(f"[green]✓[/] {output}")
        else:
            console.print(script)
        return
    if output:
        merger.save(result, output)
        console.print(f"[green]✓[/] {output}")
    else:
        table = Table(title="Merged Environment")
        table.add_column("Key", style="cyan")
        table.add_column("Value")
        for k, v in sorted(result.items()):
            table.add_row(k, v[:80])
        console.print(table)


@app.command("generate")
def generate_cmd(
    params: Optional[Path] = typer.Option(None, "--params", "-p"),
    method: str = typer.Option("cartesian", "--method", "-m"),
    limit: Optional[int] = typer.Option(None, "--limit", "-n"),
    output: Optional[Path] = typer.Option(None, "--output", "-o"),
    seed: Optional[int] = typer.Option(None, "--seed"),
) -> None:
    """Generate combinatorial parameter sets."""
    if params is None:
        parameters = {
            "learning_rate": [0.001, 0.01, 0.1],
            "batch_size": [16, 32],
            "optimizer": ["adam", "sgd"],
        }
    else:
        text = params.read_text(encoding="utf-8")
        parameters = (
            yaml.safe_load(text)
            if params.suffix.lower() in (".yaml", ".yml")
            else json.loads(text)
        )
    gen = CombinatorialGenerator(seed=seed)
    if method == "cartesian":
        combos = gen.cartesian(parameters, limit=limit)
    elif method == "pairwise":
        combos = gen.pairwise(parameters, limit=limit)
    else:
        combos = gen.sample(parameters, n=limit or 10)
    if output:
        ReportGenerator().save_jsonl(combos, output)
        console.print(f"[green]✓[/] {len(combos)} combos → [cyan]{output}[/]")
    else:
        table = Table(title=f"Combinations ({method})")
        if combos:
            for key in combos[0]:
                table.add_column(str(key), style="cyan")
            for c in combos[:40]:
                table.add_row(*[str(v) for v in c.values()])
        console.print(table)
        console.print(f"Total: {len(combos)}")


@app.command("init")
def init_cmd(
    name: str = typer.Argument(...),
    path: Optional[Path] = typer.Option(None, "--path", "-p"),
    description: str = typer.Option("A new project", "--description", "-d"),
    flat: bool = typer.Option(False, "--flat"),
) -> None:
    """Scaffold a new Python project."""
    try:
        root = ProjectHelper().init(name, path=path, description=description, src_layout=not flat)
    except Exception as e:
        console.print(f"[red]Error:[/] {e}")
        raise typer.Exit(1)
    console.print(f"[green]✓[/] Project at [cyan]{root}[/]")
    console.print(ProjectHelper().tree(root, max_depth=3))


@app.command("tree")
def tree_cmd(
    path: Path = typer.Argument(Path(".")),
    depth: int = typer.Option(4, "--depth", "-d"),
) -> None:
    """Show directory tree."""
    console.print(ProjectHelper().tree(path, max_depth=depth))


@app.command("bump")
def bump_cmd(
    part: str = typer.Argument("patch"),
    file: Path = typer.Option(Path("pyproject.toml"), "--file", "-f"),
) -> None:
    """Bump version in pyproject.toml (major|minor|patch)."""
    h = ProjectHelper()
    old, new = h.current_version(file), h.bump_version(file, part=part)
    console.print(f"[green]✓[/] {old} → [cyan]{new}[/]")


@app.command("check")
def check_cmd(
    paths: Optional[list[str]] = typer.Option(None, "--path"),
    skip_tests: bool = typer.Option(False, "--skip-tests"),
) -> None:
    """Run ruff + format check + pytest."""
    results = Checker().run_all(paths=paths or ["src", "tests"], skip_tests=skip_tests)
    table = Table(title="Check")
    table.add_column("Tool")
    table.add_column("Status")
    all_ok = True
    for r in results:
        table.add_row(r["tool"], "[green]OK[/]" if r["ok"] else "[red]FAIL[/]")
        if not r["ok"]:
            all_ok = False
    console.print(table)
    if not all_ok:
        raise typer.Exit(1)
    console.print("[green]✓ All checks passed[/]")


@app.command("drill")
def drill_cmd(path: Path = typer.Argument(Path("."), help="Directory to lock into")) -> None:
    """Enter interactive OpenComb shell locked to a directory."""
    try:
        start_drill(path)
    except Exception as e:
        console.print(f"[bold bright_red]Error:[/] {e}")
        raise typer.Exit(1)


@app.command("templates")
def templates_cmd() -> None:
    """List all available project templates."""
    from opencomb.templates_catalog import list_templates

    names = list_templates()
    table = Table(title=f"Templates ({len(names)})")
    table.add_column("#", style="dim")
    table.add_column("Name", style="cyan")
    for i, n in enumerate(names, 1):
        table.add_row(str(i), n)
    console.print(table)


@app.command("new")
def new_cmd(
    template: str = typer.Argument(..., help="Template name (see: opencomb templates)"),
    name: str = typer.Argument(..., help="Project / package name"),
    path: Optional[Path] = typer.Option(None, "--path", "-p"),
) -> None:
    """Create a new project from a template."""
    from opencomb.templates_catalog import apply_template

    try:
        root = apply_template(template, name, path=path)
    except Exception as e:
        console.print(f"[red]Error:[/] {e}")
        raise typer.Exit(1)
    console.print(f"[green]✓[/] Created [cyan]{root}[/] from template [bold]{template}[/]")


@app.command("problemscanner")
@app.command("problems", hidden=True)
def problemscanner_cmd(
    cli_mode: bool = typer.Option(False, "--cli", help="Text-only scan (no GUI)"),
    json_out: bool = typer.Option(False, "--json", help="Write JSON when using --output"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Save report to file"),
    watch: bool = typer.Option(False, "--watch", "-w", help="Watch mode (zombie run-check)"),
    zombies_only: bool = typer.Option(False, "--zombies", "-z", help="One-shot zombie check"),
) -> None:
    """Scan this computer for problems; zombie run-check with --watch / --zombies."""
    from opencomb.problem_scanner import launch_gui, main_cli

    if watch or zombies_only or cli_mode:
        try:
            from opencomb.problem_scanner import run_check_loop
            raise typer.Exit(
                run_check_loop(
                    watch=watch,
                    zombies_only=zombies_only,
                    json_out=json_out,
                    output=output,
                )
            )
        except ImportError:
            raise typer.Exit(main_cli(json_out=json_out, output=output))
    try:
        launch_gui()
    except RuntimeError as e:
        console.print(f"[yellow]{e}[/]")
        console.print("[dim]Falling back to CLI mode…[/]")
        raise typer.Exit(main_cli(json_out=json_out, output=output))


@app.command("shoot", hidden=True)
def shoot_alias(
    folder: Path = typer.Argument(..., help="Folder to clear"),
    yes: bool = typer.Option(False, "--yes", "-y"),
    dry_run: bool = typer.Option(False, "--dry-run"),
) -> None:
    """Alias → opencomb zombie shoot."""
    from opencomb.zombie import shoot_cmd
    shoot_cmd(folder=folder, yes=yes, dry_run=dry_run)


@app.command("doctor")
def doctor_cmd() -> None:
    """Check installation and environment."""
    console.print(Panel.fit(f"[bold cyan]OpenComb Doctor[/] v{__version__}", border_style="cyan"))
    table = Table()
    table.add_column("Component")
    table.add_column("Status")
    table.add_row("Core", "[green]OK[/]")
    import subprocess
    import sys

    for mod, label in [("ruff", "ruff"), ("black", "black"), ("jinja2", "Jinja2")]:
        try:
            if mod in ("ruff", "black"):
                subprocess.run(
                    [sys.executable, "-m", mod, "--version"], capture_output=True, check=True
                )
                table.add_row(label, "[green]ok[/]")
            else:
                m = __import__(mod)
                table.add_row(label, f"[green]{getattr(m, '__version__', 'ok')}[/]")
        except Exception:
            table.add_row(label, "[yellow]missing[/]")
    console.print(table)


@pak_app.command("add")
def pak_add(
    packages: list[str] = typer.Argument(...),
    upgrade: bool = typer.Option(False, "--upgrade", "-U"),
    user: bool = typer.Option(False, "--user"),
) -> None:
    """Install packages from PyPI."""
    console.print(f"[cyan]Installing:[/] {', '.join(packages)}")
    r = PackageManager().add(packages, upgrade=upgrade, user=user)
    if r.returncode == 0:
        console.print("[green]✓ installed[/]")
    else:
        raise typer.Exit(r.returncode)


@pak_app.command("list")
def pak_list() -> None:
    """List installed packages."""
    pkgs = PackageManager().list_installed()
    table = Table(title="Installed")
    table.add_column("Name", style="cyan")
    table.add_column("Version")
    for p in sorted(pkgs, key=lambda x: x.get("name", "").lower()):
        table.add_row(p.get("name", ""), p.get("version", ""))
    console.print(table)
    console.print(f"Total: {len(pkgs)}")


# ---------------------------------------------------------------------------
# User-defined custom commands
# ---------------------------------------------------------------------------
from opencomb.user_cmds import (
    add_command as _uc_add,
    delete_command as _uc_del,
    list_commands as _uc_list,
    run_command as _uc_run,
    RESERVED as _UC_RESERVED,
)


@app.command("add")
def add_cmd(
    name: Optional[str] = typer.Argument(None, help="Command name (e.g. mycommand)"),
    runner: Optional[str] = typer.Argument(None, help="Runner, e.g. python / bash / node"),
    script: Optional[Path] = typer.Argument(None, help="Path to the script to run"),
    delete: bool = typer.Option(False, "--del", "--delete", help="Delete a user command"),
    list_cmds: bool = typer.Option(False, "--list", "-l", help="List all user commands"),
    extra: Optional[list[str]] = typer.Argument(None, help="Extra fixed args for the script"),
) -> None:
    """Add / list / delete your own OpenComb commands.

    Examples:\n      opencomb add mycommand python hello.py\n      opencomb add --list\n      opencomb add --del mycommand
    """
    if list_cmds or (name is None and not delete):
        cmds = _uc_list()
        if not cmds:
            console.print("[dim]No user commands yet. Add one with:[/]")
            console.print("  opencomb add mycommand python hello.py")
            return
        table = Table(title="User commands", show_header=True)
        table.add_column("Name", style="cyan")
        table.add_column("Runner")
        table.add_column("Script")
        table.add_column("Extra args")
        for n, e in sorted(cmds.items()):
            table.add_row(
                n,
                e.get("original_runner") or e.get("runner", ""),
                e.get("script", ""),
                " ".join(e.get("extra_args") or []) or "—",
            )
        console.print(table)
        return

    if delete:
        if not name:
            console.print("[red]Need a name: opencomb add --del mycommand[/]")
            raise typer.Exit(1)
        if name in _UC_RESERVED:
            console.print(f"[red]'{name}' is built-in – cannot delete[/]")
            raise typer.Exit(1)
        if _uc_del(name):
            console.print(f"[green]✓ removed user command[/] [cyan]{name}[/]")
        else:
            console.print(f"[yellow]No user command named[/] {name}")
            raise typer.Exit(1)
        return

    if not name or not runner or not script:
        console.print("[red]Usage:[/] opencomb add <name> <runner> <script.py>")
        console.print("       opencomb add --list")
        console.print("       opencomb add --del <name>")
        raise typer.Exit(1)

    try:
        entry = _uc_add(name, runner, script, extra_args=extra or [])
    except (ValueError, FileNotFoundError) as e:
        console.print(f"[red]✗[/] {e}")
        raise typer.Exit(1)

    console.print(
        f"[green]✓ added[/] [cyan]opencomb {name}[/] → "
        f"{entry.get('original_runner', runner)} {entry['script']}"
    )
    console.print("[dim]Next invocation will pick it up.[/]")


def _register_user_commands() -> None:
    """Dynamically register user commands as top-level CLI commands."""
    cmds = _uc_list()
    existing = {getattr(c, "name", None) for c in (app.registered_commands or [])}
    for name, entry in cmds.items():
        if name in _UC_RESERVED or name in existing:
            continue

        def _make(n: str, script: str):
            def _runner(
                args: Optional[list[str]] = typer.Argument(
                    None, help="Arguments passed through to the script"
                ),
            ) -> None:
                try:
                    code = _uc_run(n, passthrough=args or [])
                except (KeyError, RuntimeError) as e:
                    console.print(f"[red]✗[/] {e}")
                    raise typer.Exit(1)
                if code:
                    raise typer.Exit(code)

            _runner.__doc__ = f"[user] {script}"
            return _runner

        try:
            app.command(name=name, help=f"[user] {entry.get('script', '')}")(
                _make(name, entry.get("script", ""))
            )
        except Exception:
            pass


_register_user_commands()


@app.command("info")
def info_cmd() -> None:
    """Show OpenComb info."""
    console.print(
        Panel.fit(
            f"""[bold cyan]OpenComb[/] v{__version__}

[bold]Zombie:[/] zombie run-check · shoot · scan · list · help-all\n[bold]Scanner:[/] problemscanner\n[bold]Codec:[/] codec encode · decode\n[bold]Custom:[/] add · add --list · add --del\n[bold]Main:[/] combine · merge · env · generate · templates · new\n[bold]Packages:[/] pak add · list\n[bold]Connect:[/] occ  (SSH user@host)\n
Repo: https://github.com/SlabyLol/OpenComb""",
            title="OpenComb",
            border_style="cyan",
        )
    )


if __name__ == "__main__":
    app()
