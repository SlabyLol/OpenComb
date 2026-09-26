"""OpenComb Build Sandbox – isolated project sandboxes with GUI or CLI config.

Creates a fully working isolated environment:
  - own directory tree
  - Python virtualenv (.venv)
  - config file (sandbox.yaml)
  - optional packages
  - run / shell / status / destroy

Usage:
  opencomb sandbox                    # interactive: choose GUI or CLI
  opencomb sandbox create mybox
  opencomb sandbox config mybox
  opencomb sandbox run mybox -- python app.py
  opencomb sandbox shell mybox
  opencomb sandbox status
  opencomb sandbox destroy mybox
"""

from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import sys
import time
import venv
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Optional

import typer
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

sandbox_app = typer.Typer(
    name="sandbox",
    help="Build & manage isolated sandboxes (GUI or CLI config).",
    no_args_is_help=False,
    rich_markup_mode="rich",
)

DEFAULT_ROOT = Path.home() / ".opencomb" / "sandboxes"
CONFIG_NAME = "sandbox.yaml"


@dataclass
class SandboxConfig:
    """Configuration for one isolated sandbox."""

    name: str = "sandbox"
    root: str = ""
    python: str = ""
    packages: list[str] = field(default_factory=list)
    env: dict[str, str] = field(default_factory=dict)
    network: bool = True
    description: str = ""
    interface: str = "cli"
    created_at: float = 0.0
    workdir: str = "work"
    isolated: bool = True

    def abs_root(self) -> Path:
        return Path(self.root).expanduser().resolve()

    def venv_dir(self) -> Path:
        return self.abs_root() / ".venv"

    def work_dir(self) -> Path:
        return self.abs_root() / self.workdir

    def config_path(self) -> Path:
        return self.abs_root() / CONFIG_NAME

    def python_bin(self) -> Path:
        base = self.venv_dir()
        if platform.system() == "Windows":
            return base / "Scripts" / "python.exe"
        return base / "bin" / "python"

    def pip_bin(self) -> Path:
        base = self.venv_dir()
        if platform.system() == "Windows":
            return base / "Scripts" / "pip.exe"
        return base / "bin" / "pip"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SandboxConfig:
        known = {f.name for f in cls.__dataclass_fields__.values()}  # type: ignore[attr-defined]
        filtered = {k: v for k, v in data.items() if k in known}
        return cls(**filtered)


def ensure_root(root: Path | None = None) -> Path:
    r = (root or DEFAULT_ROOT).expanduser().resolve()
    r.mkdir(parents=True, exist_ok=True)
    return r


def list_sandboxes(root: Path | None = None) -> list[SandboxConfig]:
    base = ensure_root(root)
    found: list[SandboxConfig] = []
    if not base.is_dir():
        return found
    for child in sorted(base.iterdir()):
        cfg = child / CONFIG_NAME
        if child.is_dir() and cfg.is_file():
            try:
                found.append(load_config(cfg))
            except Exception:
                continue
    return found


def load_config(path: Path) -> SandboxConfig:
    path = path.expanduser().resolve()
    text = path.read_text(encoding="utf-8")
    if path.suffix in (".yaml", ".yml") or path.name == CONFIG_NAME:
        data = yaml.safe_load(text) or {}
    else:
        data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError(f"Invalid sandbox config: {path}")
    cfg = SandboxConfig.from_dict(data)
    if not cfg.root:
        cfg.root = str(path.parent)
    return cfg


def save_config(cfg: SandboxConfig) -> Path:
    root = cfg.abs_root()
    root.mkdir(parents=True, exist_ok=True)
    path = root / CONFIG_NAME
    path.write_text(
        yaml.safe_dump(cfg.to_dict(), sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    return path


def resolve_sandbox(name_or_path: str, root: Path | None = None) -> SandboxConfig:
    p = Path(name_or_path).expanduser()
    if p.is_dir() and (p / CONFIG_NAME).is_file():
        return load_config(p / CONFIG_NAME)
    if p.is_file() and p.name == CONFIG_NAME:
        return load_config(p)
    base = ensure_root(root)
    candidate = base / name_or_path
    if (candidate / CONFIG_NAME).is_file():
        return load_config(candidate / CONFIG_NAME)
    raise FileNotFoundError(
        f"Sandbox '{name_or_path}' not found under {base}. "
        f"Create it with: opencomb sandbox create {name_or_path}"
    )


def _run(cmd: list[str], *, cwd: Path | None = None, env: dict[str, str] | None = None,
         timeout: float | None = 600) -> tuple[int, str, str]:
    try:
        p = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()
    except FileNotFoundError:
        return 127, "", "not found"
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"


def build_sandbox(cfg: SandboxConfig, *, progress: bool = True) -> SandboxConfig:
    """Create directory, venv, install packages, write config – fully working."""
    root = cfg.abs_root()
    if progress:
        console.print(Panel.fit(
            f"[bold cyan]Building sandbox[/] [yellow]{cfg.name}[/]\n{root}",
            border_style="cyan",
        ))

    root.mkdir(parents=True, exist_ok=True)
    cfg.work_dir().mkdir(parents=True, exist_ok=True)

    vdir = cfg.venv_dir()
    if not vdir.is_dir():
        if progress:
            console.print("[dim]Creating virtualenv…[/]")
        if cfg.python:
            code, out, err = _run([cfg.python, "-m", "venv", str(vdir)])
            if code != 0:
                raise RuntimeError(f"venv failed: {err or out}")
        else:
            builder = venv.EnvBuilder(with_pip=True, clear=False, symlinks=True)
            builder.create(str(vdir))
    else:
        if progress:
            console.print("[dim]Virtualenv already exists – reusing.[/]")

    py = cfg.python_bin()
    if not py.is_file():
        raise RuntimeError(f"Python binary missing in venv: {py}")

    if progress:
        console.print("[dim]Upgrading pip…[/]")
    _run([str(py), "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"], timeout=300)

    pkgs = list(cfg.packages or [])
    if pkgs:
        if progress:
            console.print(f"[dim]Installing packages: {', '.join(pkgs)}[/]")
        code, out, err = _run([str(py), "-m", "pip", "install", *pkgs], timeout=600)
        if code != 0:
            console.print(f"[yellow]pip install warnings/errors:[/]\n{err or out}")

    if not cfg.created_at:
        cfg.created_at = time.time()
    cfg.root = str(root)
    save_config(cfg)
    _write_helpers(cfg)

    if progress:
        console.print(f"[green]✓ sandbox ready[/]  [cyan]{cfg.name}[/]")
        console.print(f"  root:    {root}")
        console.print(f"  python:  {py}")
        console.print(f"  work:    {cfg.work_dir()}")
        console.print(f"  config:  {cfg.config_path()}")
        console.print(f"  run:     opencomb sandbox run {cfg.name} -- python")
        console.print(f"  shell:   opencomb sandbox shell {cfg.name}")
    return cfg


def _write_helpers(cfg: SandboxConfig) -> None:
    root = cfg.abs_root()
    py = cfg.python_bin()
    activate = cfg.venv_dir() / ("Scripts/activate" if platform.system() == "Windows" else "bin/activate")
    readme = f"""# Sandbox: {cfg.name}

Isolated OpenComb sandbox.

## Activate

```bash
source {activate}
```

## Run

```bash
opencomb sandbox run {cfg.name} -- python script.py
opencomb sandbox shell {cfg.name}
```

Description: {cfg.description or '(none)'}
Packages: {', '.join(cfg.packages) if cfg.packages else '(none)'}
"""
    (root / "README.md").write_text(readme, encoding="utf-8")
    run_sh = root / "run.sh"
    run_sh.write_text(
        f"""#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
export VIRTUAL_ENV="$ROOT/.venv"
export PATH="$VIRTUAL_ENV/bin:$PATH"
cd "$ROOT/{cfg.workdir}"
exec "$@"
""",
        encoding="utf-8",
    )
    try:
        run_sh.chmod(run_sh.stat().st_mode | 0o111)
    except OSError:
        pass
    sample = cfg.work_dir() / "hello.py"
    if not sample.exists():
        sample.write_text(
            'print("Hello from sandbox:", __import__("sys").executable)\n',
            encoding="utf-8",
        )


def destroy_sandbox(cfg: SandboxConfig, *, yes: bool = False) -> None:
    root = cfg.abs_root()
    if not root.is_dir():
        console.print(f"[yellow]Nothing to remove:[/] {root}")
        return
    if not yes:
        console.print(f"[bold red]Delete sandbox[/] {cfg.name} at {root} ?")
        answer = typer.prompt("Type the sandbox name to confirm", default="")
        if answer.strip() != cfg.name:
            console.print("[red]Aborted.[/]")
            raise typer.Exit(1)
    shutil.rmtree(root, ignore_errors=True)
    console.print(f"[green]✓ destroyed[/] {cfg.name}")


def sandbox_env(cfg: SandboxConfig) -> dict[str, str]:
    env = os.environ.copy()
    vbin = cfg.venv_dir() / ("Scripts" if platform.system() == "Windows" else "bin")
    env["VIRTUAL_ENV"] = str(cfg.venv_dir())
    env["PATH"] = str(vbin) + os.pathsep + env.get("PATH", "")
    env["OPENCOMB_SANDBOX"] = cfg.name
    env["OPENCOMB_SANDBOX_ROOT"] = str(cfg.abs_root())
    if cfg.isolated:
        env.pop("PYTHONPATH", None)
        env["PYTHONNOUSERSITE"] = "1"
    for k, v in (cfg.env or {}).items():
        env[str(k)] = str(v)
    if not cfg.network:
        env["OPENCOMB_SANDBOX_NETWORK"] = "0"
    return env


def run_in_sandbox(cfg: SandboxConfig, argv: list[str], *, cwd: Path | None = None) -> int:
    if not argv:
        raise ValueError("No command given")
    env = sandbox_env(cfg)
    work = cwd or cfg.work_dir()
    work.mkdir(parents=True, exist_ok=True)
    if argv[0] in ("python", "python3"):
        argv = [str(cfg.python_bin())] + argv[1:]
    elif argv[0] == "pip":
        argv = [str(cfg.python_bin()), "-m", "pip"] + argv[1:]
    console.print(f"[dim]$ {' '.join(argv)}[/]  [cyan]({cfg.name})[/]")
    try:
        p = subprocess.run(argv, cwd=str(work), env=env, check=False)
        return int(p.returncode)
    except FileNotFoundError:
        console.print(f"[red]Command not found:[/] {argv[0]}")
        return 127


def shell_in_sandbox(cfg: SandboxConfig) -> int:
    env = sandbox_env(cfg)
    work = cfg.work_dir()
    work.mkdir(parents=True, exist_ok=True)
    shell = env.get("SHELL") or ("/bin/bash" if Path("/bin/bash").exists() else "/bin/sh")
    console.print(Panel.fit(
        f"[bold]Sandbox shell[/] [cyan]{cfg.name}[/]\n{work}\nExit with Ctrl-D or exit",
        border_style="cyan",
    ))
    try:
        p = subprocess.run([shell], cwd=str(work), env=env, check=False)
        return int(p.returncode)
    except FileNotFoundError:
        console.print(f"[red]Shell not found:[/] {shell}")
        return 127


def interactive_cli_config(defaults: SandboxConfig | None = None) -> SandboxConfig:
    d = defaults or SandboxConfig()
    console.print(Panel.fit("[bold]Sandbox configuration (CLI)[/]", border_style="cyan"))
    name = typer.prompt("Name", default=d.name or "sandbox")
    name = "".join(c if c.isalnum() or c in "-_" else "_" for c in name.strip()) or "sandbox"
    base = ensure_root()
    default_root = str(base / name)
    root = typer.prompt("Root directory", default=d.root or default_root)
    desc = typer.prompt("Description", default=d.description or "")
    py = typer.prompt("Python executable (empty = current)", default=d.python or "")
    pkgs_raw = typer.prompt(
        "Packages (comma-separated, e.g. requests,rich)",
        default=",".join(d.packages) if d.packages else "",
    )
    packages = [p.strip() for p in pkgs_raw.split(",") if p.strip()]
    network = typer.confirm("Allow network inside sandbox?", default=d.network)
    isolated = typer.confirm("Isolate from user site-packages?", default=d.isolated)
    return SandboxConfig(
        name=name,
        root=str(Path(root).expanduser()),
        python=py.strip(),
        packages=packages,
        description=desc,
        network=network,
        isolated=isolated,
        interface="cli",
        env=dict(d.env or {}),
        workdir=d.workdir or "work",
    )


def interactive_gui_config(defaults: SandboxConfig | None = None) -> SandboxConfig | None:
    try:
        import tkinter as tk
        from tkinter import ttk, filedialog
    except ImportError as e:
        raise RuntimeError("tkinter not available – use CLI mode") from e

    d = defaults or SandboxConfig()
    result: dict[str, Any] = {"ok": False}
    root_win = tk.Tk()
    root_win.title("OpenComb – Sandbox Builder")
    root_win.geometry("520x480")
    root_win.minsize(480, 420)
    frm = ttk.Frame(root_win, padding=12)
    frm.pack(fill=tk.BOTH, expand=True)
    ttk.Label(frm, text="Build isolated sandbox", font=("", 12, "bold")).grid(
        row=0, column=0, columnspan=3, sticky="w", pady=(0, 10)
    )

    def row_label(r: int, text: str) -> None:
        ttk.Label(frm, text=text).grid(row=r, column=0, sticky="w", pady=4)

    name_var = tk.StringVar(value=d.name or "sandbox")
    root_var = tk.StringVar(value=d.root or str(DEFAULT_ROOT / (d.name or "sandbox")))
    desc_var = tk.StringVar(value=d.description or "")
    py_var = tk.StringVar(value=d.python or "")
    pkgs_var = tk.StringVar(value=", ".join(d.packages) if d.packages else "")
    network_var = tk.BooleanVar(value=d.network)
    isolated_var = tk.BooleanVar(value=d.isolated)

    row_label(1, "Name")
    ttk.Entry(frm, textvariable=name_var, width=40).grid(row=1, column=1, sticky="ew", pady=4)
    row_label(2, "Root path")
    ttk.Entry(frm, textvariable=root_var, width=40).grid(row=2, column=1, sticky="ew", pady=4)

    def browse() -> None:
        p = filedialog.askdirectory(initialdir=str(DEFAULT_ROOT))
        if p:
            root_var.set(p)

    ttk.Button(frm, text="…", width=3, command=browse).grid(row=2, column=2, padx=4)
    row_label(3, "Description")
    ttk.Entry(frm, textvariable=desc_var, width=40).grid(row=3, column=1, sticky="ew", pady=4)
    row_label(4, "Python (optional)")
    ttk.Entry(frm, textvariable=py_var, width=40).grid(row=4, column=1, sticky="ew", pady=4)
    row_label(5, "Packages")
    ttk.Entry(frm, textvariable=pkgs_var, width=40).grid(row=5, column=1, sticky="ew", pady=4)
    ttk.Label(frm, text="comma-separated", foreground="#666").grid(row=6, column=1, sticky="w")
    ttk.Checkbutton(frm, text="Allow network", variable=network_var).grid(row=7, column=1, sticky="w", pady=4)
    ttk.Checkbutton(frm, text="Isolate (no user site-packages)", variable=isolated_var).grid(
        row=8, column=1, sticky="w", pady=4
    )
    frm.columnconfigure(1, weight=1)

    def on_build() -> None:
        name = "".join(c if c.isalnum() or c in "-_" else "_" for c in name_var.get().strip()) or "sandbox"
        r = root_var.get().strip() or str(DEFAULT_ROOT / name)
        pkgs = [p.strip() for p in pkgs_var.get().split(",") if p.strip()]
        result["ok"] = True
        result["cfg"] = SandboxConfig(
            name=name,
            root=str(Path(r).expanduser()),
            description=desc_var.get().strip(),
            python=py_var.get().strip(),
            packages=pkgs,
            network=bool(network_var.get()),
            isolated=bool(isolated_var.get()),
            interface="gui",
        )
        root_win.destroy()

    def on_cancel() -> None:
        result["ok"] = False
        root_win.destroy()

    btns = ttk.Frame(frm)
    btns.grid(row=9, column=0, columnspan=3, sticky="e", pady=16)
    ttk.Button(btns, text="Cancel", command=on_cancel).pack(side=tk.RIGHT, padx=4)
    ttk.Button(btns, text="Build sandbox", command=on_build).pack(side=tk.RIGHT, padx=4)
    root_win.protocol("WM_DELETE_WINDOW", on_cancel)
    root_win.mainloop()
    if result.get("ok"):
        return result["cfg"]  # type: ignore[return-value]
    return None


def choose_interface() -> str:
    console.print(Panel.fit(
        "[bold]OpenComb Sandbox Builder[/]\nChoose how to configure the sandbox:",
        border_style="cyan",
    ))
    console.print("  [cyan]1[/]  CLI  (terminal prompts)")
    console.print("  [cyan]2[/]  GUI  (window)")
    choice = typer.prompt("Choice", default="1")
    if str(choice).strip() in ("2", "gui", "g", "GUI"):
        return "gui"
    return "cli"


@sandbox_app.callback(invoke_without_command=True)
def sandbox_root(ctx: typer.Context) -> None:
    """Interactive sandbox builder (GUI or CLI), or subcommands."""
    if ctx.invoked_subcommand is not None:
        return
    mode = choose_interface()
    try:
        if mode == "gui":
            cfg = interactive_gui_config()
            if cfg is None:
                console.print("[dim]Cancelled.[/]")
                raise typer.Exit(0)
        else:
            cfg = interactive_cli_config()
    except RuntimeError as e:
        console.print(f"[yellow]{e}[/] – falling back to CLI")
        cfg = interactive_cli_config()
    if not Path(cfg.root).is_absolute() and cfg.name and cfg.name not in cfg.root:
        cfg.root = str(ensure_root() / cfg.name)
    build_sandbox(cfg)


@sandbox_app.command("create")
def create_cmd(
    name: str = typer.Argument(..., help="Sandbox name"),
    path: Optional[Path] = typer.Option(None, "--path", "-p", help="Root directory"),
    packages: Optional[str] = typer.Option(None, "--packages", "-k", help="Comma-separated packages"),
    python: Optional[str] = typer.Option(None, "--python", help="Python executable for venv"),
    description: str = typer.Option("", "--description", "-d"),
    network: bool = typer.Option(True, "--network/--no-network"),
    isolated: bool = typer.Option(True, "--isolated/--no-isolated"),
    gui: bool = typer.Option(False, "--gui", help="Open GUI configurator first"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="CLI prompts"),
) -> None:
    """Create a new isolated sandbox."""
    base = ensure_root()
    root = path or (base / name)
    cfg = SandboxConfig(
        name=name,
        root=str(root.expanduser()),
        packages=[p.strip() for p in (packages or "").split(",") if p.strip()],
        python=python or "",
        description=description,
        network=network,
        isolated=isolated,
        interface="gui" if gui else "cli",
    )
    if gui:
        try:
            edited = interactive_gui_config(cfg)
            if edited is None:
                console.print("[dim]Cancelled.[/]")
                raise typer.Exit(0)
            cfg = edited
        except RuntimeError as e:
            console.print(f"[yellow]{e}[/]")
            raise typer.Exit(1)
    elif interactive:
        cfg = interactive_cli_config(cfg)
    if (cfg.abs_root() / CONFIG_NAME).is_file():
        console.print(f"[yellow]Sandbox already exists:[/] {cfg.abs_root()}")
        if not typer.confirm("Rebuild / update?", default=False):
            raise typer.Exit(0)
    build_sandbox(cfg)


@sandbox_app.command("config")
def config_cmd(
    name: str = typer.Argument(..., help="Sandbox name or path"),
    gui: bool = typer.Option(False, "--gui"),
) -> None:
    """Edit sandbox configuration (then optionally rebuild)."""
    cfg = resolve_sandbox(name)
    if gui:
        try:
            edited = interactive_gui_config(cfg)
        except RuntimeError as e:
            console.print(f"[red]{e}[/]")
            raise typer.Exit(1)
        if edited is None:
            console.print("[dim]Cancelled.[/]")
            raise typer.Exit(0)
        edited.root = cfg.root
        edited.name = cfg.name
        edited.created_at = cfg.created_at
        cfg = edited
    else:
        cfg = interactive_cli_config(cfg)
        cfg.root = str(Path(cfg.root).expanduser())
    save_config(cfg)
    console.print(f"[green]✓ config saved[/] {cfg.config_path()}")
    if typer.confirm("Rebuild venv / install packages now?", default=True):
        build_sandbox(cfg)


@sandbox_app.command("rebuild")
def rebuild_cmd(name: str = typer.Argument(..., help="Sandbox name or path")) -> None:
    """Recreate venv and reinstall packages from config."""
    cfg = resolve_sandbox(name)
    vdir = cfg.venv_dir()
    if vdir.is_dir():
        console.print("[dim]Removing old virtualenv…[/]")
        shutil.rmtree(vdir, ignore_errors=True)
    build_sandbox(cfg)


@sandbox_app.command("run")
def run_cmd(
    name: str = typer.Argument(..., help="Sandbox name or path"),
    command: list[str] = typer.Argument(None, help="Command after --"),
) -> None:
    """Run a command inside the sandbox (use -- before the command)."""
    cfg = resolve_sandbox(name)
    if not command:
        console.print("[red]Usage:[/] opencomb sandbox run NAME -- python app.py")
        raise typer.Exit(1)
    code = run_in_sandbox(cfg, list(command))
    raise typer.Exit(code)


@sandbox_app.command("shell")
def shell_cmd(name: str = typer.Argument(..., help="Sandbox name or path")) -> None:
    """Open an interactive shell inside the sandbox."""
    cfg = resolve_sandbox(name)
    code = shell_in_sandbox(cfg)
    raise typer.Exit(code)


@sandbox_app.command("list")
@sandbox_app.command("status", hidden=True)
def list_cmd(
    root: Optional[Path] = typer.Option(None, "--root", help="Sandboxes root"),
) -> None:
    """List all sandboxes and their status."""
    items = list_sandboxes(root)
    if not items:
        console.print(f"[dim]No sandboxes under {ensure_root(root)}[/]")
        console.print("Create one: [cyan]opencomb sandbox create mybox[/]")
        return
    table = Table(title=f"Sandboxes ({len(items)})")
    table.add_column("Name", style="cyan")
    table.add_column("Python")
    table.add_column("Packages")
    table.add_column("Root")
    table.add_column("OK")
    for cfg in items:
        py = cfg.python_bin()
        ok = "✓" if py.is_file() else "✗"
        table.add_row(
            cfg.name,
            f"{py.name}" if py.is_file() else "missing venv",
            ",".join(cfg.packages[:4]) + ("…" if len(cfg.packages) > 4 else "") or "—",
            str(cfg.abs_root()),
            ok,
        )
    console.print(table)


@sandbox_app.command("destroy")
@sandbox_app.command("rm", hidden=True)
def destroy_cmd(
    name: str = typer.Argument(..., help="Sandbox name or path"),
    yes: bool = typer.Option(False, "--yes", "-y"),
) -> None:
    """Delete a sandbox directory completely."""
    cfg = resolve_sandbox(name)
    destroy_sandbox(cfg, yes=yes)


@sandbox_app.command("show")
def show_cmd(name: str = typer.Argument(..., help="Sandbox name or path")) -> None:
    """Show sandbox config."""
    cfg = resolve_sandbox(name)
    console.print(Panel.fit(
        yaml.safe_dump(cfg.to_dict(), sort_keys=False, allow_unicode=True),
        title=f"sandbox:{cfg.name}",
        border_style="cyan",
    ))
    py = cfg.python_bin()
    console.print(f"python binary: {'[green]OK[/]' if py.is_file() else '[red]missing[/]'}  {py}")


@sandbox_app.command("gui")
def gui_cmd() -> None:
    """Open the sandbox builder GUI."""
    try:
        cfg = interactive_gui_config()
    except RuntimeError as e:
        console.print(f"[red]{e}[/]")
        raise typer.Exit(1)
    if cfg is None:
        console.print("[dim]Cancelled.[/]")
        raise typer.Exit(0)
    if not Path(cfg.root).is_absolute():
        cfg.root = str(ensure_root() / cfg.name)
    build_sandbox(cfg)
