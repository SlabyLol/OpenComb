"""Code formatting helpers."""

from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path


class CodeFormatter:
    """Format Python code. Tries ruff / black if available, otherwise does light cleanup."""

    def format(self, source: str, *, prefer: str = "ruff") -> str:
        if prefer in ("ruff", "auto"):
            formatted = self._try_ruff(source)
            if formatted is not None:
                return formatted

        if prefer in ("black", "auto"):
            formatted = self._try_black(source)
            if formatted is not None:
                return formatted

        return self._basic_cleanup(source)

    def format_file(self, path: str | Path, *, prefer: str = "ruff") -> str:
        source = Path(path).read_text(encoding="utf-8")
        return self.format(source, prefer=prefer)

    def _try_ruff(self, source: str) -> str | None:
        try:
            result = subprocess.run(
                [sys.executable, "-m", "ruff", "format", "--stdin-filename", "tmp.py", "-"],
                input=source, text=True, capture_output=True, timeout=10,
            )
            if result.returncode == 0 and result.stdout:
                return result.stdout
        except Exception:
            pass
        return None

    def _try_black(self, source: str) -> str | None:
        try:
            result = subprocess.run(
                [sys.executable, "-m", "black", "-", "-q"],
                input=source, text=True, capture_output=True, timeout=15,
            )
            if result.returncode == 0 and result.stdout:
                return result.stdout
        except Exception:
            pass
        return None

    def _basic_cleanup(self, source: str) -> str:
        try:
            ast.parse(source)
        except SyntaxError:
            return source

        lines = source.replace("\r\n", "\n").replace("\r", "\n").split("\n")
        lines = [line.rstrip() for line in lines]
        cleaned = []
        blank_count = 0
        for line in lines:
            if line.strip() == "":
                blank_count += 1
                if blank_count <= 2:
                    cleaned.append("")
            else:
                blank_count = 0
                cleaned.append(line)
        return "\n".join(cleaned).strip() + "\n"
