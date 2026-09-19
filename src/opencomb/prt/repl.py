"""Interactive PRT REPL."""

from __future__ import annotations

from pathlib import Path

from rich.console import Console
from rich.panel import Panel

from opencomb.prt.interpreter import PRTInterpreter

console = Console()


def start_repl(cwd: Path | None = None) -> None:
    interp = PRTInterpreter(cwd=cwd)
    console.print(
        Panel.fit(
            "[bold bright_red]OpenComb PRT[/] interactive shell\n"
            "[dim].prt language · type[/] [bright_red]exit[/] [dim]to quit[/]",
            border_style="bright_red",
        )
    )
    buf: list[str] = []
    while True:
        try:
            prompt = "... " if buf else "prt> "
            line = console.input(f"[bold bright_red]{prompt}[/]")
        except (EOFError, KeyboardInterrupt):
            console.print()
            break
        if not buf and line.strip() in {"exit", "quit"}:
            break
        buf.append(line)
        src = "\n".join(buf)
        if src.count("{") > src.count("}") or src.count("(") > src.count(")"):
            continue
        buf.clear()
        if not src.strip():
            continue
        try:
            result = interp.run_source(src)
            if result is not None:
                console.print(f"[cyan]=>[/] {result!r}")
        except Exception as e:
            console.print(f"[red]Error:[/] {e}")
