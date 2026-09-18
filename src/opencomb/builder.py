"""Interactive build system with terminal animations and many targets."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.prompt import Confirm
from rich.table import Table

console = Console()


@dataclass
class BuildTarget:
    id: str
    name: str
    description: str
    category: str
    run: Callable
    requires_confirm: bool = False


@dataclass
class BuildContext:
    root: Path
    python: str = field(default_factory=lambda: sys.executable)
    verbose: bool = False

    def run(self, cmd: list[str], *, cwd: Path | None = None, env: dict[str, str] | None = None) -> subprocess.CompletedProcess:
        full_env = os.environ.copy()
        if env:
            full_env.update(env)
        return subprocess.run(cmd, cwd=str(cwd or self.root), env=full_env, capture_output=not self.verbose, text=True)


def _ok(msg: str) -> None:
    console.print(f"[bold green]\u2713[/] {msg}")


def _fail(msg: str) -> None:
    console.print(f"[bold red]\u2717[/] {msg}")


def _info(msg: str) -> None:
    console.print(f"[bold cyan]\u2192[/] {msg}")


def build_wheel(ctx: BuildContext) -> bool:
    _info("Building wheel \u2026")
    r = ctx.run([ctx.python, "-m", "build", "--wheel", "--outdir", "dist"])
    if r.returncode != 0:
        r = ctx.run([ctx.python, "-m", "pip", "wheel", ".", "-w", "dist", "--no-deps"])
    if r.returncode == 0:
        _ok("Wheel in dist/")
        return True
    _fail(r.stderr or r.stdout or "wheel failed")
    return False


def build_sdist(ctx: BuildContext) -> bool:
    _info("Building source distribution \u2026")
    r = ctx.run([ctx.python, "-m", "build", "--sdist", "--outdir", "dist"])
    if r.returncode != 0:
        ctx.run([ctx.python, "-m", "pip", "install", "build", "-q"])
        r = ctx.run([ctx.python, "-m", "build", "--sdist", "--outdir", "dist"])
    if r.returncode == 0:
        _ok("sdist in dist/")
        return True
    _fail(r.stderr or "sdist failed")
    return False


def build_all_pkg(ctx: BuildContext) -> bool:
    _info("Building wheel + sdist \u2026")
    ctx.run([ctx.python, "-m", "pip", "install", "build", "-q"])
    r = ctx.run([ctx.python, "-m", "build", "--outdir", "dist"])
    if r.returncode == 0:
        _ok("Artifacts in dist/")
        return True
    return build_wheel(ctx) and build_sdist(ctx)


def build_editable(ctx: BuildContext) -> bool:
    _info("Editable install \u2026")
    r = ctx.run([ctx.python, "-m", "pip", "install", "-e", ".", "-q"])
    if r.returncode == 0:
        _ok("Installed editable")
        return True
    _fail(r.stderr or "editable install failed")
    return False


def build_install(ctx: BuildContext) -> bool:
    _info("Installing package \u2026")
    r = ctx.run([ctx.python, "-m", "pip", "install", ".", "-q"])
    if r.returncode == 0:
        _ok("Installed")
        return True
    _fail(r.stderr or "install failed")
    return False


def build_clean(ctx: BuildContext) -> bool:
    _info("Cleaning build artifacts \u2026")
    removed = []
    for name in ("dist", "build", ".eggs"):
        p = ctx.root / name
        if p.exists():
            shutil.rmtree(p, ignore_errors=True)
            removed.append(name)
    for p in ctx.root.rglob("*.egg-info"):
        shutil.rmtree(p, ignore_errors=True)
        removed.append(str(p.relative_to(ctx.root)))
    for p in ctx.root.rglob("__pycache__"):
        shutil.rmtree(p, ignore_errors=True)
    _ok(f"Cleaned: {', '.join(removed) or 'nothing extra'}")
    return True


def build_check(ctx: BuildContext) -> bool:
    _info("Running checks (ruff + pytest) \u2026")
    ok = True
    r = ctx.run([ctx.python, "-m", "ruff", "check", "src", "tests"])
    if r.returncode != 0:
        _fail("ruff check failed")
        ok = False
    else:
        _ok("ruff ok")
    r = ctx.run([ctx.python, "-m", "pytest", "-q", "--tb=line"])
    if r.returncode != 0:
        _fail("pytest failed")
        ok = False
    else:
        _ok("pytest ok")
    return ok


def build_format(ctx: BuildContext) -> bool:
    _info("Formatting with ruff \u2026")
    r = ctx.run([ctx.python, "-m", "ruff", "format", "src", "tests"])
    if r.returncode == 0:
        _ok("Formatted")
        return True
    r = ctx.run([ctx.python, "-m", "black", "src", "tests", "-q"])
    if r.returncode == 0:
        _ok("Formatted with black")
        return True
    _fail("No formatter available")
    return False


def build_docs(ctx: BuildContext) -> bool:
    _info("Building docs \u2026")
    if (ctx.root / "mkdocs.yml").exists():
        r = ctx.run([ctx.python, "-m", "mkdocs", "build"])
        if r.returncode == 0:
            _ok("MkDocs \u2192 site/")
            return True
    if (ctx.root / "docs").is_dir() and (ctx.root / "docs" / "conf.py").exists():
        r = ctx.run([ctx.python, "-m", "sphinx.cmd.build", "-b", "html", "docs", "docs/_build/html"])
        if r.returncode == 0:
            _ok("Sphinx \u2192 docs/_build/html")
            return True
    readme = ctx.root / "README.md"
    out = ctx.root / "build" / "docs"
    out.mkdir(parents=True, exist_ok=True)
    if readme.exists():
        shutil.copy(readme, out / "index.md")
        _ok(f"Copied README \u2192 {out}")
        return True
    _fail("No docs config found")
    return False


def build_docker(ctx: BuildContext) -> bool:
    _info("Docker image build \u2026")
    df = None
    for name in ("Dockerfile", "docker/Dockerfile"):
        if (ctx.root / name).exists():
            df = name
            break
    if not df:
        name = ctx.root.name.replace(" ", "-").lower()
        content = f"""FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir .
CMD ["python", "-m", "{name.replace('-', '_')}"]
"""
        (ctx.root / "Dockerfile").write_text(content, encoding="utf-8")
        df = "Dockerfile"
        _info("Generated Dockerfile")
    tag = ctx.root.name.lower().replace(" ", "-")
    r = ctx.run(["docker", "build", "-t", tag, "-f", df, "."])
    if r.returncode == 0:
        _ok(f"Image tagged: {tag}")
        return True
    _fail(r.stderr or "docker build failed")
    return False


def build_requirements(ctx: BuildContext) -> bool:
    _info("Freezing requirements \u2026")
    r = ctx.run([ctx.python, "-m", "pip", "freeze"])
    out = ctx.root / "requirements.txt"
    if r.returncode == 0 and r.stdout:
        out.write_text(r.stdout, encoding="utf-8")
        _ok(f"Wrote {out.name}")
        return True
    _fail("freeze failed")
    return False


def build_lock(ctx: BuildContext) -> bool:
    _info("Generating lock \u2026")
    r = ctx.run([ctx.python, "-m", "pip", "freeze"])
    out = ctx.root / "requirements.lock"
    if r.returncode == 0 and r.stdout:
        out.write_text(r.stdout, encoding="utf-8")
        _ok(f"Wrote {out.name}")
        return True
    _fail("lock failed")
    return False


def build_test(ctx: BuildContext) -> bool:
    _info("Running tests \u2026")
    r = ctx.run([ctx.python, "-m", "pytest", "-v", "--tb=short"])
    if r.returncode == 0:
        _ok("All tests passed")
        return True
    _fail("Tests failed")
    return False


def build_typecheck(ctx: BuildContext) -> bool:
    _info("Type checking with mypy \u2026")
    r = ctx.run([ctx.python, "-m", "mypy", "src", "--ignore-missing-imports"])
    if r.returncode == 0:
        _ok("mypy clean")
        return True
    _fail(r.stdout or r.stderr or "mypy failed")
    return False


def build_coverage(ctx: BuildContext) -> bool:
    _info("Coverage run \u2026")
    r = ctx.run([ctx.python, "-m", "pytest", "--cov=src", "--cov-report=term-missing", "-q"])
    if r.returncode == 0:
        _ok("Coverage done")
        return True
    _fail("Coverage failed")
    return False


def build_release_check(ctx: BuildContext) -> bool:
    for step in (build_clean, build_format, build_check, build_all_pkg):
        if not step(ctx):
            return False
        time.sleep(0.15)
    _ok("Release check passed")
    return True


def build_ci_local(ctx: BuildContext) -> bool:
    _info("Local CI pipeline \u2026")
    ok = True
    for label, fn in [("format", build_format), ("check", build_check), ("wheel", build_wheel)]:
        console.print(f"[dim]\u2500\u2500 {label} \u2500\u2500[/]")
        if not fn(ctx):
            ok = False
    return ok


def build_tree_artifact(ctx: BuildContext) -> bool:
    from opencomb.project import ProjectHelper
    out = ctx.root / "build"
    out.mkdir(parents=True, exist_ok=True)
    (out / "tree.txt").write_text(ProjectHelper().tree(ctx.root, max_depth=5), encoding="utf-8")
    _ok("build/tree.txt")
    return True


def build_stats_artifact(ctx: BuildContext) -> bool:
    import json
    from opencomb.tools import ProjectStats
    out = ctx.root / "build"
    out.mkdir(parents=True, exist_ok=True)
    (out / "stats.json").write_text(json.dumps(ProjectStats().collect(ctx.root), indent=2), encoding="utf-8")
    _ok("build/stats.json")
    return True


def build_combine_src(ctx: BuildContext) -> bool:
    from opencomb.combiner import CodeCombiner
    src = ctx.root / "src" if (ctx.root / "src").is_dir() else ctx.root
    files = [f for f in sorted(src.rglob("*.py")) if "__pycache__" not in f.parts]
    if not files:
        _fail("No .py files")
        return False
    out = ctx.root / "build"
    out.mkdir(parents=True, exist_ok=True)
    (out / "combined.py").write_text(CodeCombiner().combine_files(files), encoding="utf-8")
    _ok(f"build/combined.py ({len(files)} files)")
    return True


def all_targets() -> list[BuildTarget]:
    return [
        BuildTarget("wheel", "Wheel (.whl)", "Build binary wheel into dist/", "Package", lambda c: build_wheel(c)),
        BuildTarget("sdist", "Source dist", "Build source tarball into dist/", "Package", lambda c: build_sdist(c)),
        BuildTarget("package", "Full package", "Wheel + sdist together", "Package", lambda c: build_all_pkg(c)),
        BuildTarget("editable", "Editable install", "pip install -e .", "Package", lambda c: build_editable(c)),
        BuildTarget("install", "Install", "pip install .", "Package", lambda c: build_install(c)),
        BuildTarget("clean", "Clean", "Remove dist/, build/, caches", "Maintain", lambda c: build_clean(c)),
        BuildTarget("format", "Format", "Ruff/black format src & tests", "Quality", lambda c: build_format(c)),
        BuildTarget("check", "Lint + test", "Ruff check + pytest", "Quality", lambda c: build_check(c)),
        BuildTarget("test", "Tests only", "pytest -v", "Quality", lambda c: build_test(c)),
        BuildTarget("typecheck", "Typecheck", "mypy on src/", "Quality", lambda c: build_typecheck(c)),
        BuildTarget("coverage", "Coverage", "pytest --cov", "Quality", lambda c: build_coverage(c)),
        BuildTarget("docs", "Documentation", "MkDocs / Sphinx / README copy", "Docs", lambda c: build_docs(c)),
        BuildTarget("docker", "Docker image", "docker build (generates Dockerfile if missing)", "Deploy", lambda c: build_docker(c), requires_confirm=True),
        BuildTarget("reqs", "requirements.txt", "pip freeze \u2192 requirements.txt", "Deps", lambda c: build_requirements(c)),
        BuildTarget("lock", "Lock file", "pip freeze \u2192 requirements.lock", "Deps", lambda c: build_lock(c)),
        BuildTarget("release", "Release gate", "clean \u2192 format \u2192 check \u2192 package", "Release", lambda c: build_release_check(c)),
        BuildTarget("ci", "Local CI", "format + check + wheel", "Release", lambda c: build_ci_local(c)),
        BuildTarget("tree", "Tree artifact", "Write build/tree.txt", "Artifacts", lambda c: build_tree_artifact(c)),
        BuildTarget("stats", "Stats artifact", "Write build/stats.json", "Artifacts", lambda c: build_stats_artifact(c)),
        BuildTarget("combine", "Combine sources", "All .py \u2192 build/combined.py", "Artifacts", lambda c: build_combine_src(c)),
    ]


FRAMES = ["\u280b", "\u2819", "\u2839", "\u2838", "\u283c", "\u2834", "\u2826", "\u2827", "\u2807", "\u280f"]
BAR_COLORS = ["red", "bright_red", "yellow", "green", "cyan", "blue", "magenta"]


def animated_banner() -> None:
    title = "OPENCOMB BUILD"
    with Live(console=console, refresh_per_second=18) as live:
        for i in range(18):
            spin = FRAMES[i % len(FRAMES)]
            color = BAR_COLORS[i % len(BAR_COLORS)]
            bar = "\u2588" * (i + 1) + "\u2591" * (18 - i)
            live.update(Panel(f"[{color}]{spin}[/{color}] [bold {color}]{title}[/]\n[{color}]{bar}[/{color}]", border_style=color, title="[bold]build[/]"))
            time.sleep(0.04)
    console.print()


def show_menu(targets: list[BuildTarget]) -> None:
    table = Table(title="[bold bright_red]Select what to build[/]", show_header=True, header_style="bold bright_red", border_style="bright_red")
    table.add_column("#", style="bold bright_red", width=4)
    table.add_column("Target", style="bold cyan")
    table.add_column("Category", style="dim")
    table.add_column("Description")
    for i, t in enumerate(targets, 1):
        table.add_row(str(i), t.name, t.category, t.description)
    table.add_row("0", "[bold]All safe targets[/]", "Meta", "clean \u2192 format \u2192 check \u2192 package \u2192 artifacts")
    table.add_row("q", "[bold]Quit[/]", "\u2014", "Leave build menu")
    console.print(table)


def run_with_spinner(label: str, fn: Callable[[], bool]) -> bool:
    import threading
    progress = Progress(SpinnerColumn(spinner_name="dots"), TextColumn("[bold bright_red]{task.description}[/]"), BarColumn(bar_width=28, complete_style="bright_red", finished_style="green"), TimeElapsedColumn(), console=console, transient=False)
    with progress:
        task = progress.add_task(label, total=None)
        result_box: list[bool] = []
        start = time.time()
        th = threading.Thread(target=lambda: result_box.append(fn()), daemon=True)
        th.start()
        i = 0
        while th.is_alive():
            progress.update(task, description=f"{FRAMES[i % len(FRAMES)]} {label}")
            time.sleep(0.08)
            i += 1
        th.join()
        elapsed = time.time() - start
        ok = bool(result_box and result_box[0])
        progress.update(task, description=f"{'\u2713' if ok else '\u2717'} {label} ({elapsed:.1f}s)", total=1, completed=1)
    return bool(result_box and result_box[0])


def run_targets(selected: list[BuildTarget], ctx: BuildContext) -> None:
    console.print()
    overall = Progress(SpinnerColumn(), TextColumn("[bold]{task.description}[/]"), BarColumn(bar_width=40, complete_style="bright_red", finished_style="green"), TextColumn("[progress.percentage]{task.percentage:>3.0f}%"), TimeElapsedColumn(), console=console)
    results: list[tuple[str, bool]] = []
    with overall:
        task = overall.add_task("Building\u2026", total=len(selected))
        for t in selected:
            overall.update(task, description=f"[bright_red]{t.name}[/]")
            if t.requires_confirm and not Confirm.ask(f"[yellow]Run '{t.name}'?[/]", default=True):
                results.append((t.name, False))
                overall.advance(task)
                continue
            ok = run_with_spinner(t.name, lambda tt=t: tt.run(ctx))
            results.append((t.name, ok))
            overall.advance(task)
            time.sleep(0.1)
    console.print()
    table = Table(title="[bold]Build summary[/]", border_style="bright_red")
    table.add_column("Target")
    table.add_column("Result")
    passed = 0
    for name, ok in results:
        table.add_row(name, "[green]OK[/]" if ok else "[red]FAIL[/]")
        if ok:
            passed += 1
    console.print(table)
    with Live(console=console, refresh_per_second=12) as live:
        for i in range(10):
            color = "green" if passed == len(results) else "bright_red"
            live.update(Panel(f"[{color}]{FRAMES[i % len(FRAMES)]} {passed}/{len(results)} succeeded[/{color}]", border_style=color))
            time.sleep(0.05)
    if passed == len(results):
        _ok("All selected builds finished successfully")
    else:
        _fail(f"{len(results) - passed} target(s) failed")


def interactive_build(root: Path | None = None, *, verbose: bool = False) -> None:
    root = (root or Path.cwd()).resolve()
    ctx = BuildContext(root=root, verbose=verbose)
    targets = all_targets()
    animated_banner()
    console.print(f"[dim]Project root:[/] [bold]{root}[/]\n")
    while True:
        show_menu(targets)
        console.print()
        choice = console.input("[bold bright_red]Build number(s)[/] (e.g. 1 3 5 or 0=all safe, q=quit): ").strip()
        if not choice or choice.lower() in {"q", "quit", "exit"}:
            console.print("[dim]Bye.[/]")
            return
        selected: list[BuildTarget] = []
        if choice == "0":
            want = {"clean", "format", "check", "package", "tree", "stats", "combine"}
            selected = [t for t in targets if t.id in want]
        else:
            by_id = {t.id: t for t in targets}
            by_num = {str(i): t for i, t in enumerate(targets, 1)}
            for token in choice.replace(",", " ").split():
                token = token.strip().lower()
                if token in by_num:
                    selected.append(by_num[token])
                elif token in by_id:
                    selected.append(by_id[token])
                else:
                    console.print(f"[yellow]Unknown:[/] {token}")
        if not selected:
            console.print("[yellow]Nothing selected[/]")
            continue
        seen, uniq = set(), []
        for t in selected:
            if t.id not in seen:
                seen.add(t.id)
                uniq.append(t)
        console.print(f"[bright_red]Selected:[/] {', '.join(t.name for t in uniq)}")
        run_targets(uniq, ctx)
        if not Confirm.ask("\n[bold]Build more?[/]", default=False):
            break


def run_build_ids(ids: list[str], root: Path | None = None, *, verbose: bool = False) -> bool:
    root = (root or Path.cwd()).resolve()
    ctx = BuildContext(root=root, verbose=verbose)
    by_id = {t.id: t for t in all_targets()}
    selected = []
    for i in ids:
        if i not in by_id:
            _fail(f"Unknown target: {i}")
            return False
        selected.append(by_id[i])
    animated_banner()
    run_targets(selected, ctx)
    return True
