"""Interactive OpenComb drill mode – work only inside a fixed directory."""

from __future__ import annotations

import os
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Callable

from rich.console import Console
from rich.panel import Panel
from rich.theme import Theme

DRILL_THEME = Theme({
    "drill": "bold bright_red",
    "drill.dim": "bright_red",
    "drill.ok": "bold bright_red",
    "drill.err": "bold red",
    "drill.prompt": "bold bright_red",
    "drill.path": "bold bright_red underline",
})


class DrillShell:
    """Interactive shell locked to a directory."""

    def __init__(self, root: str | Path):
        self.root = Path(root).resolve()
        if not self.root.is_dir():
            raise NotADirectoryError(f"Not a directory: {self.root}")
        self.console = Console(theme=DRILL_THEME)
        self._builtin: dict[str, Callable[..., None]] = {
            "help": self._cmd_help,
            "?": self._cmd_help,
            "exit": self._cmd_exit,
            "quit": self._cmd_exit,
            "q": self._cmd_exit,
            "cd": self._cmd_cd,
            "pwd": self._cmd_pwd,
            "ls": self._cmd_ls,
            "tree": self._cmd_tree,
            "clear": self._cmd_clear,
            "status": self._cmd_status,
        }
        self._running = False
        self._cwd = self.root

    def _rel(self, path: Path | None = None) -> str:
        p = path or self._cwd
        try:
            return str(p.relative_to(self.root)) or "."
        except ValueError:
            return str(p)

    def _resolve_inside(self, user_path: str) -> Path:
        if user_path in (".", ""):
            return self._cwd
        p = Path(user_path)
        target = p.resolve() if p.is_absolute() else (self._cwd / p).resolve()
        try:
            target.relative_to(self.root)
        except ValueError:
            raise PermissionError(f"Path outside drill root: {user_path}")
        return target

    def _print(self, msg: str, style: str = "drill") -> None:
        self.console.print(f"[{style}]{msg}[/]")

    def _banner(self) -> None:
        self.console.print(
            Panel.fit(
                f"[drill]OPENCOMB DRILL MODE[/]\n"
                f"[drill.dim]Root locked:[/] [drill.path]{self.root}[/]\n"
                f"[drill.dim]Type[/] [drill]help[/] [drill.dim]for commands ·[/] "
                f"[drill]exit[/] [drill.dim]to leave[/]",
                border_style="bright_red",
                title="[drill]drill[/]",
            )
        )

    def _prompt(self) -> str:
        return f"opencomb:{self._rel()}> "

    def run(self) -> None:
        old_cwd = Path.cwd()
        try:
            os.chdir(self.root)
            self._cwd = self.root
            self._running = True
            self._banner()
            while self._running:
                try:
                    line = self.console.input("[drill.prompt]" + self._prompt() + "[/]")
                except (EOFError, KeyboardInterrupt):
                    self.console.print()
                    self._print("Leaving drill mode.")
                    break
                line = line.strip()
                if not line:
                    continue
                self._dispatch(line)
        finally:
            os.chdir(old_cwd)

    def _dispatch(self, line: str) -> None:
        try:
            parts = shlex.split(line)
        except ValueError as e:
            self._print(f"Parse error: {e}", "drill.err")
            return
        if not parts:
            return
        cmd = parts[0].lower()

        if cmd in self._builtin:
            try:
                self._builtin[cmd](*parts[1:])
            except Exception as e:
                self._print(f"Error: {e}", "drill.err")
            return

        if cmd in {
            "combine", "merge", "env", "generate", "prompt", "template",
            "recipe", "format", "pak", "init", "tree", "bump", "check",
            "ignore", "doctor", "info",
        }:
            self._run_opencomb([cmd, *parts[1:]])
            return

        if cmd == "opencomb":
            self._run_opencomb(parts[1:])
            return

        self._run_system(parts)

    def _run_opencomb(self, args: list[str]) -> None:
        from opencomb.cli import app
        old = Path.cwd()
        try:
            os.chdir(self._cwd)
            old_argv = sys.argv
            sys.argv = ["opencomb", *args]
            try:
                app(standalone_mode=False)
            except SystemExit as e:
                if e.code not in (0, None):
                    self._print(f"exit code {e.code}", "drill.err")
            except Exception as e:
                self._print(f"Error: {e}", "drill.err")
            finally:
                sys.argv = old_argv
        finally:
            os.chdir(old)

    def _run_system(self, parts: list[str]) -> None:
        try:
            result = subprocess.run(parts, cwd=str(self._cwd), check=False)
            if result.returncode != 0:
                self._print(f"exit {result.returncode}", "drill.err")
        except FileNotFoundError:
            self._print(f"Unknown command: {parts[0]}", "drill.err")
        except Exception as e:
            self._print(f"Error: {e}", "drill.err")

    def _cmd_help(self, *args: str) -> None:
        self.console.print(
            Panel(
                "[drill]Builtins[/]\n"
                "  help, ?          this help\n"
                "  exit, quit, q    leave drill mode\n"
                "  cd <path>        change dir (only inside root)\n"
                "  pwd              print current path\n"
                "  ls [path]        list directory\n"
                "  tree [depth]     show tree\n"
                "  status           show drill status\n"
                "  clear            clear screen\n\n"
                "[drill]OpenComb commands[/] (scoped to this dir)\n"
                "  combine, merge, env, generate, prompt, template\n"
                "  recipe, format, pak, init, tree, bump, check, ignore\n"
                "  doctor, info\n\n"
                "[drill.dim]Example:[/] [drill]pak add requests[/]\n"
                "[drill.dim]Example:[/] [drill]combine a.py b.py -o out.py[/]",
                title="[drill]drill help[/]",
                border_style="bright_red",
            )
        )

    def _cmd_exit(self, *args: str) -> None:
        self._print("Leaving drill mode.")
        self._running = False

    def _cmd_cd(self, *args: str) -> None:
        target = self._resolve_inside(args[0] if args else ".")
        if not target.is_dir():
            raise NotADirectoryError(str(target))
        self._cwd = target
        os.chdir(self._cwd)
        self._print(self._rel())

    def _cmd_pwd(self, *args: str) -> None:
        self._print(f"{self._rel()}  →  {self._cwd}")

    def _cmd_ls(self, *args: str) -> None:
        target = self._resolve_inside(args[0] if args else ".")
        if not target.is_dir():
            self._print(str(target.name))
            return
        entries = sorted(target.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
        for e in entries:
            self._print(f"  {e.name}{'/' if e.is_dir() else ''}")

    def _cmd_tree(self, *args: str) -> None:
        depth = 3
        if args:
            try:
                depth = int(args[0])
            except ValueError:
                pass
        from opencomb.project import ProjectHelper
        self.console.print(f"[drill]{ProjectHelper().tree(self._cwd, max_depth=depth)}[/]")

    def _cmd_clear(self, *args: str) -> None:
        self.console.clear()

    def _cmd_status(self, *args: str) -> None:
        self.console.print(
            Panel(
                f"[drill]Root[/]   [drill.path]{self.root}[/]\n"
                f"[drill]CWD[/]    [drill.path]{self._cwd}[/]\n"
                f"[drill]Rel[/]    [drill]{self._rel()}[/]",
                title="[drill]status[/]",
                border_style="bright_red",
            )
        )


def start_drill(path: str | Path) -> None:
    DrillShell(path).run()
