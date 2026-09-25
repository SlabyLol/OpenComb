"""User-defined custom OpenComb commands.

Storage: ~/.opencomb/user_commands.json

Usage:
  opencomb add mycmd python hello.py
  opencomb add mycmd python hello.py -- --flag value
  opencomb add --list
  opencomb add --del mycmd
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

# Names that must never be overwritten by user commands
RESERVED = frozenset({
    "add", "combine", "merge", "env", "generate", "init", "tree", "bump",
    "check", "drill", "templates", "new", "problemscanner", "problems",
    "shoot", "doctor", "info", "pak", "zombie", "codec", "occ", "prt",
    "wizard", "stack", "stacks", "prompt", "template", "recipe", "format",
    "build", "ignore", "version", "help", "completion",
})

CONFIG_DIR = Path.home() / ".opencomb"
COMMANDS_FILE = CONFIG_DIR / "user_commands.json"


def _ensure_dir() -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_commands() -> dict[str, dict[str, Any]]:
    """Load user command registry."""
    if not COMMANDS_FILE.is_file():
        return {}
    try:
        data = json.loads(COMMANDS_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def save_commands(cmds: dict[str, dict[str, Any]]) -> None:
    """Persist user command registry."""
    _ensure_dir()
    COMMANDS_FILE.write_text(
        json.dumps(cmds, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def add_command(
    name: str,
    runner: str,
    script: str | Path,
    extra_args: list[str] | None = None,
) -> dict[str, Any]:
    """Register a new user command. Returns the entry."""
    name = name.strip().lower().replace(" ", "-")
    if not name or not name.replace("-", "").replace("_", "").isalnum():
        raise ValueError(f"Invalid command name: {name!r} (use letters, digits, - _)")
    if name in RESERVED:
        raise ValueError(f"'{name}' is a built-in OpenComb command and cannot be overwritten")

    script_path = Path(script).expanduser().resolve()
    if not script_path.is_file():
        raise FileNotFoundError(f"Script not found: {script_path}")

    # Resolve runner (python → current interpreter if just "python")
    runner_resolved = runner
    if runner in ("python", "python3"):
        runner_resolved = sys.executable
    elif shutil.which(runner) is None and not Path(runner).is_file():
        raise ValueError(f"Runner not found on PATH: {runner}")

    entry = {
        "runner": runner_resolved,
        "script": str(script_path),
        "extra_args": list(extra_args or []),
        "original_runner": runner,
    }
    cmds = load_commands()
    cmds[name] = entry
    save_commands(cmds)
    return entry


def delete_command(name: str) -> bool:
    """Remove a user command. Returns True if it existed."""
    name = name.strip().lower().replace(" ", "-")
    cmds = load_commands()
    if name not in cmds:
        return False
    del cmds[name]
    save_commands(cmds)
    return True


def list_commands() -> dict[str, dict[str, Any]]:
    """Return all user commands."""
    return load_commands()


def run_command(name: str, passthrough: list[str] | None = None) -> int:
    """Execute a user command. Returns exit code."""
    cmds = load_commands()
    if name not in cmds:
        raise KeyError(f"Unknown user command: {name}")
    entry = cmds[name]
    runner = entry["runner"]
    script = entry["script"]
    extra = list(entry.get("extra_args") or [])
    args = [runner, script] + extra + list(passthrough or [])
    try:
        proc = subprocess.run(args)
        return proc.returncode
    except FileNotFoundError as e:
        raise RuntimeError(f"Failed to run {name}: {e}") from e
