"""Project scaffolding, structure and developer helpers."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any


PYTHON_GITIGNORE = """# Byte-compiled / cache
__pycache__/
*.py[cod]
*$py.class
*.so

# Distribution / packaging
.Python
build/
dist/
*.egg-info/
.eggs/
*.egg

# Virtual environments
.venv/
venv/
ENV/
env/

# Testing / coverage / type
.coverage
htmlcov/
.pytest_cache/
.mypy_cache/
.ruff_cache/
.tox/
.nox/

# IDE / OS
.idea/
.vscode/
*.swp
.DS_Store
Thumbs.db

# Local / secrets
.env
.env.*
!.env.example
*.local

# OpenComb build outputs
build/
opencomb_report.*
"""

BASIC_README = """# {name}

{description}

## Install

```bash
pip install -e .
```

## Usage

```bash
python -m {package}
```

## License

MIT
"""

BASIC_PYPROJECT = """[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "{name}"
version = "0.1.0"
description = "{description}"
readme = "README.md"
requires-python = ">=3.10"
license = "MIT"
dependencies = []

[project.optional-dependencies]
dev = ["pytest>=8.0", "ruff>=0.5"]

[tool.hatch.build.targets.wheel]
packages = ["src/{package}"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
"""


class ProjectHelper:
    """Scaffold projects, show trees, bump versions, generate ignores."""

    def init(
        self,
        name: str,
        *,
        path: str | Path | None = None,
        description: str = "A new project",
        src_layout: bool = True,
    ) -> Path:
        root = Path(path) if path else Path.cwd() / name
        root = root.resolve()
        package = re.sub(r"[^a-z0-9_]", "_", name.lower().replace("-", "_"))

        if root.exists() and any(root.iterdir()):
            raise FileExistsError(f"Directory not empty: {root}")

        root.mkdir(parents=True, exist_ok=True)

        if src_layout:
            pkg_dir = root / "src" / package
            pkg_dir.mkdir(parents=True)
            (pkg_dir / "__init__.py").write_text(
                f'"""{name}"""\n\n__version__ = "0.1.0"\n', encoding="utf-8"
            )
            (pkg_dir / "__main__.py").write_text(
                f'"""Entry point for {name}."""\n\ndef main() -> None:\n'
                f'    print("Hello from {name}!")\n\n\nif __name__ == "__main__":\n'
                f"    main()\n",
                encoding="utf-8",
            )
        else:
            pkg_dir = root / package
            pkg_dir.mkdir(parents=True)
            (pkg_dir / "__init__.py").write_text(
                f'"""{name}"""\n\n__version__ = "0.1.0"\n', encoding="utf-8"
            )

        tests = root / "tests"
        tests.mkdir(exist_ok=True)
        (tests / "__init__.py").write_text("", encoding="utf-8")
        (tests / "test_smoke.py").write_text(
            f"def test_import():\n    import {package}\n    assert {package}.__version__\n",
            encoding="utf-8",
        )

        (root / "pyproject.toml").write_text(
            BASIC_PYPROJECT.format(name=name, package=package, description=description),
            encoding="utf-8",
        )
        (root / "README.md").write_text(
            BASIC_README.format(name=name, package=package, description=description),
            encoding="utf-8",
        )
        (root / ".gitignore").write_text(PYTHON_GITIGNORE, encoding="utf-8")
        (root / ".env.example").write_text("# Example environment\nDEBUG=false\n", encoding="utf-8")

        recipes = root / "recipes"
        recipes.mkdir(exist_ok=True)
        (recipes / "dev.yaml").write_text(
            f"""# OpenComb dev recipe for {name}
name: {name}-dev

generate:
  method: pairwise
  params:
    python: ["3.10", "3.11", "3.12"]
    os: ["linux", "macos"]
  output: build/matrix.jsonl
""",
            encoding="utf-8",
        )

        return root

    def tree(
        self,
        path: str | Path = ".",
        *,
        max_depth: int = 4,
        ignore: set[str] | None = None,
    ) -> str:
        root = Path(path).resolve()
        ignore = ignore or {
            ".git", "__pycache__", ".venv", "venv", "node_modules",
            ".mypy_cache", ".ruff_cache", ".pytest_cache", "dist", "build",
        }

        lines: list[str] = [str(root.name) + "/"]

        def _walk(current: Path, prefix: str, depth: int) -> None:
            if depth > max_depth:
                return
            try:
                entries = sorted(current.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
            except PermissionError:
                return

            filtered = []
            for e in entries:
                if e.name in ignore or e.name.endswith(".egg-info"):
                    continue
                if e.name.startswith(".") and e.name not in {".github", ".gitignore", ".env.example"}:
                    if e.name not in {".gitignore", ".env.example"}:
                        continue
                filtered.append(e)

            for i, entry in enumerate(filtered):
                is_last = i == len(filtered) - 1
                connector = "└── " if is_last else "├── "
                lines.append(prefix + connector + entry.name + ("/" if entry.is_dir() else ""))
                if entry.is_dir():
                    extension = "    " if is_last else "│   "
                    _walk(entry, prefix + extension, depth + 1)

        _walk(root, "", 1)
        return "\n".join(lines) + "\n"

    def write_gitignore(self, path: str | Path = ".gitignore") -> Path:
        p = Path(path)
        p.write_text(PYTHON_GITIGNORE, encoding="utf-8")
        return p

    def bump_version(self, path: str | Path = "pyproject.toml", *, part: str = "patch") -> str:
        p = Path(path)
        text = p.read_text(encoding="utf-8")
        m = re.search(r'^version\s*=\s*["\']([^"\']+)["\']', text, re.MULTILINE)
        if not m:
            raise ValueError('No version = "..." found in pyproject.toml')

        old = m.group(1)
        parts = [int(x) for x in old.split(".")]
        while len(parts) < 3:
            parts.append(0)

        if part == "major":
            parts[0] += 1
            parts[1] = 0
            parts[2] = 0
        elif part == "minor":
            parts[1] += 1
            parts[2] = 0
        else:
            parts[2] += 1

        new = ".".join(str(x) for x in parts[:3])
        new_text = re.sub(
            r'^version\s*=\s*["\'][^"\']+["\']',
            f'version = "{new}"',
            text,
            count=1,
            flags=re.MULTILINE,
        )
        p.write_text(new_text, encoding="utf-8")
        return new

    def current_version(self, path: str | Path = "pyproject.toml") -> str | None:
        p = Path(path)
        if not p.exists():
            return None
        text = p.read_text(encoding="utf-8")
        m = re.search(r'^version\s*=\s*["\']([^"\']+)["\']', text, re.MULTILINE)
        return m.group(1) if m else None
