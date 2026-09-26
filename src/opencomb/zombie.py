"""OpenComb Zombie toolkit – plain Python source (no encoding)."""

from __future__ import annotations

import os
import platform
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree

console = Console()

zombie_app = typer.Typer(
    name="zombie",
    help="Zombie toolkit: run-check, shoot, scan, clean, inspect — everything.",
    no_args_is_help=True,
    rich_markup_mode="rich",
)


def _run(cmd: list[str], timeout: float = 8.0) -> tuple[int, str, str]:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=False)
        return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()
    except FileNotFoundError:
        return 127, "", "not found"
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"
    except Exception as e:
        return 1, "", str(e)


def _print_kv(title: str, rows: list[tuple[str, str]]) -> None:
    table = Table(title=title, show_header=True)
    table.add_column("Key", style="cyan")
    table.add_column("Value")
    for k, v in rows:
        table.add_row(k, v)
    console.print(table)


@zombie_app.command("run-check")
@zombie_app.command("watch", hidden=True)
def run_check_cmd(
    interval: float = typer.Option(5.0, "--interval", "-i", help="Seconds between rounds"),
    rounds: Optional[int] = typer.Option(None, "--rounds", "-n", help="Max rounds (default: infinite)"),
    once: bool = typer.Option(False, "--once", help="Single round only"),
) -> None:
    """Zombie run-check — show EVERYTHING each round (full process detail)."""
    from opencomb.problem_scanner import run_zombie_check

    if once:
        rounds = 1
    console.print(
        Panel.fit(
            f"[bold cyan]Zombie run-check[/] — full detail every {interval:.0f}s"
            + (f", rounds={rounds}" if rounds else ", Ctrl+C to stop"),
            border_style="cyan",
        )
    )
    n = 0
    try:
        while rounds is None or n < rounds:
            n += 1
            ts = time.strftime("%Y-%m-%d %H:%M:%S")
            zombies = run_zombie_check()
            code, ps_out, _ = _run(
                ["ps", "-eo", "stat,pid,ppid,user,pcpu,pmem,rss,etime,comm,args", "--sort=-pcpu"],
                timeout=6.0,
            )
            console.rule(f"[bold]Round {n} @ {ts}[/]")
            if not zombies:
                console.print("[green]✓ No zombie processes (Z state).[/]")
            else:
                table = Table(title=f"[red]{len(zombies)} ZOMBIE(S)[/]", show_lines=True)
                table.add_column("PID", style="cyan")
                table.add_column("COMM")
                table.add_column("PPID")
                table.add_column("PARENT")
                table.add_column("HINT")
                for z in zombies:
                    table.add_row(
                        z["pid"],
                        z["comm"],
                        z["ppid"],
                        z["parent_comm"],
                        f"restart/kill parent {z['parent_comm']} ({z['ppid']})",
                    )
                console.print(table)
            if ps_out:
                console.print("[dim]Top processes (ps snapshot):[/]")
                for line in ps_out.splitlines()[:18]:
                    console.print(f"  {line}")
            if rounds is None or n < rounds:
                time.sleep(interval)
    except KeyboardInterrupt:
        console.print("\n[dim]Stopped.[/]")


@zombie_app.command("list")
def list_cmd() -> None:
    """List current zombie processes."""
    from opencomb.problem_scanner import run_zombie_check

    zombies = run_zombie_check()
    if not zombies:
        console.print("[green]✓ No zombies.[/]")
        raise typer.Exit(0)
    table = Table(title=f"{len(zombies)} zombie(s)")
    table.add_column("PID", style="cyan")
    table.add_column("COMM")
    table.add_column("PPID")
    table.add_column("PARENT")
    for z in zombies:
        table.add_row(z["pid"], z["comm"], z["ppid"], z["parent_comm"])
    console.print(table)


@zombie_app.command("parents")
def parents_cmd() -> None:
    """Show parents of zombie processes."""
    from opencomb.problem_scanner import run_zombie_check
    from collections import Counter

    zombies = run_zombie_check()
    if not zombies:
        console.print("[green]No zombies — no parents to list.[/]")
        raise typer.Exit(0)
    c = Counter((z["ppid"], z["parent_comm"]) for z in zombies)
    table = Table(title="Zombie parents")
    table.add_column("PPID", style="cyan")
    table.add_column("PARENT")
    table.add_column("Zombie children", justify="right")
    for (ppid, pcomm), n in c.most_common():
        table.add_row(ppid, pcomm, str(n))
    console.print(table)


@zombie_app.command("shoot")
def shoot_cmd(
    folder: Path = typer.Argument(..., help="Folder whose contents will be deleted (folder kept)"),
    dry_run: bool = typer.Option(False, "--dry-run", help="List targets only, do not delete"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip interactive confirmation"),
    force: bool = typer.Option(False, "--force", help="Allow protected paths"),
    keep_dirs: bool = typer.Option(False, "--keep-dirs", help="Delete files only"),
) -> None:
    """Clear ALL files inside a folder (with confirmation). Folder itself is kept."""
    from opencomb.problem_scanner import list_shoot_targets, shoot_folder, _is_protected

    folder = folder.expanduser()
    if not folder.is_dir():
        console.print(f"[red]Not a directory:[/] {folder}")
        raise typer.Exit(1)
    try:
        resolved = folder.resolve()
    except OSError:
        resolved = folder
    if _is_protected(resolved) and not force:
        console.print(f"[red]Protected path:[/] {resolved}")
        console.print("[dim]Use --force only if you are sure.[/]")
        raise typer.Exit(1)
    try:
        targets = list_shoot_targets(resolved, include_dirs=not keep_dirs)
    except Exception as e:
        console.print(f"[red]Error:[/] {e}")
        raise typer.Exit(1)
    files = [p for p in targets if p.is_file() or p.is_symlink()]
    dirs = [p for p in targets if p.is_dir() and not p.is_symlink()]
    console.print(
        Panel.fit(
            f"[bold red]Zombie Shoot[/]\nTarget: [cyan]{resolved}[/]\n"
            f"Files: [yellow]{len(files)}[/]  Subdirs: [yellow]{len(dirs)}[/]",
            border_style="red",
        )
    )
    if dry_run:
        console.print("[green]Dry-run — nothing deleted.[/]")
        raise typer.Exit(0)
    if not files and not dirs:
        console.print("[green]Folder already empty.[/]")
        raise typer.Exit(0)
    if not yes:
        console.print(
            f"[bold yellow]Permanently delete {len(files)} file(s) and {len(dirs)} subdir(s) inside:[/]\n  {resolved}"
        )
        answer = typer.prompt("Type the folder path to confirm", default="")
        try:
            ok = Path(answer).expanduser().resolve() == resolved
        except OSError:
            ok = False
        if not ok and answer.strip() not in (str(resolved), str(folder)):
            console.print("[red]Confirmation mismatch — aborted.[/]")
            raise typer.Exit(1)
    try:
        result = shoot_folder(
            resolved, confirm=True, dry_run=False, include_dirs=not keep_dirs, force=force, yes=True
        )
    except Exception as e:
        console.print(f"[red]Error:[/] {e}")
        raise typer.Exit(1)
    console.print(f"[green]✓[/] {result.get('message', 'done')}")
    if result.get("errors"):
        for e in result["errors"][:15]:
            console.print(f"[yellow]{e}[/]")
        raise typer.Exit(1)


# Register additional plain-source commands
try:
    import opencomb.zombie_extra  # noqa: F401
except Exception:
    pass
