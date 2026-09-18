"""Package helper – install / search packages from PyPI."""

from __future__ import annotations

import json
import subprocess
import sys
import urllib.request
from pathlib import Path
from typing import Any


class PackageManager:
    """Lightweight helper to install and inspect packages from PyPI."""

    PYPI_JSON = "https://pypi.org/pypi/{name}/json"
    USER_AGENT = "OpenComb/0.4"

    def __init__(self, python: str | None = None):
        self.python = python or sys.executable

    def add(
        self,
        packages: list[str],
        *,
        upgrade: bool = False,
        user: bool = False,
        quiet: bool = False,
    ) -> subprocess.CompletedProcess:
        """Install packages with pip."""
        cmd = [self.python, "-m", "pip", "install"]
        if upgrade:
            cmd.append("--upgrade")
        if user:
            cmd.append("--user")
        if quiet:
            cmd.append("-q")
        cmd.extend(packages)
        return subprocess.run(cmd, check=False, capture_output=False)

    def remove(self, packages: list[str], *, quiet: bool = False) -> subprocess.CompletedProcess:
        """Uninstall packages."""
        cmd = [self.python, "-m", "pip", "uninstall", "-y"]
        if quiet:
            cmd.append("-q")
        cmd.extend(packages)
        return subprocess.run(cmd, check=False, capture_output=False)

    def list_installed(self) -> list[dict[str, str]]:
        """Return list of installed packages (name + version)."""
        result = subprocess.run(
            [self.python, "-m", "pip", "list", "--format=json"],
            capture_output=True, text=True, check=False,
        )
        if result.returncode != 0:
            return []
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return []

    def show(self, name: str) -> dict[str, Any] | None:
        """Show details of an installed package."""
        result = subprocess.run(
            [self.python, "-m", "pip", "show", name],
            capture_output=True, text=True, check=False,
        )
        if result.returncode != 0:
            return None
        info: dict[str, str] = {}
        for line in result.stdout.splitlines():
            if ":" in line:
                key, _, value = line.partition(":")
                info[key.strip().lower().replace("-", "_")] = value.strip()
        return info

    def search_pypi(self, name: str) -> dict[str, Any] | None:
        """Fetch package metadata from PyPI JSON API."""
        url = self.PYPI_JSON.format(name=name)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": self.USER_AGENT})
            with urllib.request.urlopen(req, timeout=12) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception:
            return None

    def latest_version(self, name: str) -> str | None:
        data = self.search_pypi(name)
        if not data:
            return None
        return data.get("info", {}).get("version")

    def info_summary(self, name: str) -> dict[str, Any] | None:
        """Nice summary of a package from PyPI."""
        data = self.search_pypi(name)
        if not data:
            return None
        info = data.get("info", {})
        return {
            "name": info.get("name"),
            "version": info.get("version"),
            "summary": info.get("summary"),
            "author": info.get("author"),
            "license": info.get("license"),
            "home_page": info.get("home_page") or info.get("project_url"),
            "requires_python": info.get("requires_python"),
        }

    def freeze(self, path: str | Path | None = None) -> str:
        """Return or write a requirements-style freeze."""
        result = subprocess.run(
            [self.python, "-m", "pip", "freeze"],
            capture_output=True, text=True, check=False,
        )
        text = result.stdout
        if path:
            Path(path).write_text(text, encoding="utf-8")
        return text
