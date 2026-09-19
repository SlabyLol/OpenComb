"""Shared helpers for OpenComb project templates."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable


@dataclass
class FileSpec:
    path: str
    content: str


@dataclass
class ProjectTemplate:
    id: str
    name: str
    category: str
    description: str
    tags: list[str] = field(default_factory=list)
    files: list[FileSpec] = field(default_factory=list)


def _pkg(name: str) -> str:
    return re.sub(r"[^a-z0-9_]", "_", name.lower().replace("-", "_"))


def _pyproject(name: str, desc: str, deps: list[str] | None = None, scripts: dict[str, str] | None = None) -> str:
    deps = deps or []
    dep_lines = ",\n    ".join(f'"{d}"' for d in deps)
    script_block = ""
    if scripts:
        lines = "\n".join(f'{k} = "{v}"' for k, v in scripts.items())
        script_block = f"\n[project.scripts]\n{lines}\n"
    return f'''[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "{name}"
version = "0.1.0"
description = "{desc}"
requires-python = ">=3.10"
dependencies = [
    {dep_lines}
]
{script_block}
[tool.hatch.build.targets.wheel]
packages = ["src/{_pkg(name)}"]
'''


def _gitignore() -> str:
    return """__pycache__/
*.py[cod]
.venv/
venv/
dist/
build/
*.egg-info/
.env
.mypy_cache/
.ruff_cache/
.pytest_cache/
node_modules/
.DS_Store
"""
