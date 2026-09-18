"""Quality checks: format, lint, tests."""

from __future__ import annotations

import subprocess
import sys
from typing import Any


class Checker:
    """Run common developer checks in one place."""

    def __init__(self, python: str | None = None):
        self.python = python or sys.executable

    def run_ruff(self, paths: list[str] | None = None) -> dict[str, Any]:
        paths = paths or ["src", "tests"]
        cmd = [self.python, "-m", "ruff", "check", *paths]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return {
            "ok": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "tool": "ruff",
        }

    def run_format_check(self, paths: list[str] | None = None) -> dict[str, Any]:
        paths = paths or ["src", "tests"]
        cmd = [self.python, "-m", "ruff", "format", "--check", *paths]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return {
            "ok": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "tool": "ruff-format",
        }

    def run_pytest(self, extra_args: list[str] | None = None) -> dict[str, Any]:
        cmd = [self.python, "-m", "pytest", "-q", "--tb=short"]
        if extra_args:
            cmd.extend(extra_args)
        result = subprocess.run(cmd, capture_output=True, text=True)
        return {
            "ok": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "tool": "pytest",
        }

    def run_all(
        self,
        *,
        paths: list[str] | None = None,
        skip_tests: bool = False,
    ) -> list[dict[str, Any]]:
        results = [
            self.run_ruff(paths),
            self.run_format_check(paths),
        ]
        if not skip_tests:
            results.append(self.run_pytest())
        return results
