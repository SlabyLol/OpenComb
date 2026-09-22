"""Project building helpers: wizard, stacks, components, doctor, structure."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from opencomb.templates_catalog import apply_template

console = Console()

STACKS: dict[str, dict[str, Any]] = {
    "api-full": {
        "desc": "FastAPI + JWT + SQLModel + Docker + CI + tests",
        "templates": ["fastapi-jwt", "fastapi-sqlmodel", "docker-api", "github-ci", "pytest-asyncio"],
        "components": ["dockerfile", "makefile", "precommit", "devcontainer"],
    },
    "cli-pro": {
        "desc": "Typer + Rich + config YAML + tests + pre-commit",
        "templates": ["typer-table", "yaml-config", "pytest-only"],
        "components": ["makefile", "precommit", "gitignore"],
    },
    "ml-api": {
        "desc": "ML model serving API (FastAPI + toy model + Docker)",
        "templates": ["ml-api", "docker-api", "github-ci"],
        "components": ["dockerfile", "makefile"],
    },
    "web-full": {
        "desc": "Streamlit / Gradio dashboard + FastAPI backend",
        "templates": ["streamlit", "fastapi", "docker-api"],
        "components": ["dockerfile", "compose"],
    },
    "discord-bot": {
        "desc": "Discord bot + worker + Dockerfile",
        "templates": ["discord", "worker"],
        "components": ["dockerfile", "makefile"],
    },
    "library": {
        "desc": "Publishable Python library (src layout + tests + CI + docs)",
        "templates": ["library", "pytest-only", "mkdocs", "github-ci", "gh-release"],
        "components": ["precommit", "makefile"],
    },
    "data-science": {
        "desc": "Data science notebook + Polars/Pandas + Streamlit",
        "templates": ["datascience", "polars", "streamlit", "notebook"],
        "components": ["makefile"],
    },
    "monorepo": {
        "desc": "Monorepo with packages + shared tools",
        "templates": ["monorepo", "cli", "fastapi"],
        "components": ["makefile", "precommit"],
    },
    "minimal": {
        "desc": "Bare minimal package",
        "templates": ["minimal"],
        "components": ["gitignore"],
    },
    "pyrunner": {
        "desc": "Browser Python runner (Pyodide) – packages via packages.json only",
        "templates": ["pyrunner"],
        "components": [],
    },
}

COMPONENTS: dict[str, dict[str, Any]] = {
    "dockerfile": {
        "desc": "Multi-stage Dockerfile for Python apps",
        "files": {
            "Dockerfile": "# Multi-stage Python Dockerfile (OpenComb)\nFROM python:3.12-slim AS builder\nWORKDIR /app\nCOPY pyproject.toml README.md ./\nCOPY src/ ./src/\nRUN pip install --no-cache-dir build && python -m build --wheel\n\nFROM python:3.12-slim\nWORKDIR /app\nCOPY --from=builder /app/dist/*.whl /tmp/\nRUN pip install --no-cache-dir /tmp/*.whl && rm /tmp/*.whl\nEXPOSE 8000\nCMD [\"python\", \"-m\", \"uvicorn\", \"app.main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8000\"]\n",
        },
    },
    "makefile": {
        "desc": "Developer Makefile (install, test, lint, run)",
        "files": {
            "Makefile": ".PHONY: install test lint format run clean\ninstall:\n\tpip install -e \".[dev]\"\ntest:\n\tpytest -q\nlint:\n\truff check src tests\nformat:\n\truff format src tests\nrun:\n\tpython -m app\nclean:\n\trm -rf dist build *.egg-info .pytest_cache .ruff_cache\n\tfind . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true\n",
        },
    },
    "precommit": {
        "desc": "pre-commit config (ruff + basic hooks)",
        "files": {
            ".pre-commit-config.yaml": "repos:\n  - repo: https://github.com/astral-sh/ruff-pre-commit\n    rev: v0.6.9\n    hooks:\n      - id: ruff\n        args: [--fix]\n      - id: ruff-format\n  - repo: https://github.com/pre-commit/pre-commit-hooks\n    rev: v4.6.0\n    hooks:\n      - id: trailing-whitespace\n      - id: end-of-file-fixer\n      - id: check-yaml\n      - id: check-added-large-files\n",
        },
    },
    "devcontainer": {
        "desc": "VS Code / Codespaces devcontainer",
        "files": {
            ".devcontainer/devcontainer.json": "{\n  \"name\": \"OpenComb Project\",\n  \"image\": \"mcr.microsoft.com/devcontainers/python:3.12\",\n  \"postCreateCommand\": \"pip install -e \\\".[dev]\\\"\",\n  \"customizations\": {\n    \"vscode\": {\n      \"extensions\": [\"ms-python.python\", \"charliermarsh.ruff\"]\n    }\n  }\n}\n",
        },
    },
    "gitignore": {
        "desc": "Python .gitignore",
        "files": {
            ".gitignore": "__pycache__/\n*.py[cod]\n*$py.class\n*.so\n.Python\nbuild/\ndist/\n*.egg-info/\n.eggs/\n.venv/\nvenv/\n.env\n.env.*\n!.env.example\n.pytest_cache/\n.ruff_cache/\n.mypy_cache/\n.coverage\nhtmlcov/\n.DS_Store\n*.log\n",
        },
    },
    "compose": {
        "desc": "docker-compose.yml with app + redis",
        "files": {
            "docker-compose.yml": "services:\n  app:\n    build: .\n    ports:\n      - \"8000:8000\"\n    environment:\n      - REDIS_URL=redis://redis:6379/0\n    depends_on:\n      - redis\n  redis:\n    image: redis:7-alpine\n    ports:\n      - \"6379:6379\"\n",
        },
    },
    "pytest": {
        "desc": "pytest.ini + conftest skeleton",
        "files": {
            "pytest.ini": "[pytest]\ntestpaths = tests\nasyncio_mode = auto\naddopts = -q --tb=short\n",
            "tests/conftest.py": "import pytest\n\n@pytest.fixture\ndef any_data():\n    return {\"ok\": True}\n",
        },
    },
    "github-ci": {
        "desc": "GitHub Actions CI workflow",
        "files": {
            ".github/workflows/ci.yml": "name: CI\non:\n  push:\n    branches: [main, master]\n  pull_request:\njobs:\n  test:\n    runs-on: ubuntu-latest\n    strategy:\n      matrix:\n        python-version: [\"3.10\", \"3.11\", \"3.12\", \"3.13\"]\n    steps:\n      - uses: actions/checkout@v4\n      - uses: actions/setup-python@v5\n        with:\n          python-version: ${{ matrix.python-version }}\n      - run: pip install -e \".[dev]\"\n      - run: ruff check src tests || true\n      - run: pytest -q\n",
        },
    },
    "readme": {
        "desc": "Basic README.md",
        "files": {
            "README.md": "# Project\n\nGenerated with OpenComb.\n\n```bash\npip install -e .\n```\n",
        },
    },
}


def list_stacks() -> list[tuple[str, str]]:
    return [(k, v["desc"]) for k, v in STACKS.items()]


def list_components() -> list[tuple[str, str]]:
    return [(k, v["desc"]) for k, v in COMPONENTS.items()]


def apply_stack(name: str, target: Path, project_name: str | None = None) -> list[Path]:
    if name not in STACKS:
        raise ValueError(f"Unknown stack: {name}. Available: {', '.join(STACKS)}")
    stack = STACKS[name]
    target = target.resolve()
    target.mkdir(parents=True, exist_ok=True)
    created: list[Path] = []
    pname = project_name or target.name
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        task = progress.add_task(f"Applying stack [cyan]{name}[/]…", total=None)
        for tpl in stack.get("templates", []):
            progress.update(task, description=f"Template [cyan]{tpl}[/]…")
            try:
                files = apply_template(tpl, target, name=pname)
                created.extend(files)
            except Exception as e:
                console.print(f"[yellow]⚠ template {tpl}: {e}[/]")
        for comp in stack.get("components", []):
            progress.update(task, description=f"Component [cyan]{comp}[/]…")
            try:
                files = add_component(comp, target)
                created.extend(files)
            except Exception as e:
                console.print(f"[yellow]⚠ component {comp}: {e}[/]")
    return created


def add_component(name: str, target: Path) -> list[Path]:
    if name not in COMPONENTS:
        raise ValueError(f"Unknown component: {name}. Available: {', '.join(COMPONENTS)}")
    target = target.resolve()
    target.mkdir(parents=True, exist_ok=True)
    created: list[Path] = []
    for rel, content in COMPONENTS[name]["files"].items():
        path = target / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            console.print(f"[dim]skip existing {rel}[/]")
            continue
        path.write_text(content, encoding="utf-8")
        created.append(path)
        console.print(f"[green]✓[/] {rel}")
    return created


def run_wizard(target: Path | None = None) -> Path:
    console.print(Panel.fit("[bold cyan]OpenComb Project Wizard[/]", border_style="cyan"))
    name = Prompt.ask("Project name", default="my-project")
    target = (target or Path.cwd() / name).resolve()
    if target.exists() and any(target.iterdir()):
        if not Confirm.ask(f"[yellow]{target}[/] is not empty. Continue?", default=False):
            raise SystemExit(0)
    console.print("\n[bold]Choose a stack:[/]")
    stacks = list_stacks()
    table = Table(show_header=True, header_style="bold")
    table.add_column("#", style="dim", width=4)
    table.add_column("Stack", style="cyan")
    table.add_column("Description")
    for i, (k, d) in enumerate(stacks, 1):
        table.add_row(str(i), k, d)
    console.print(table)
    choice = Prompt.ask("Stack number or name", default="1")
    if choice.isdigit() and 1 <= int(choice) <= len(stacks):
        stack_name = stacks[int(choice) - 1][0]
    else:
        stack_name = choice if choice in STACKS else "minimal"
    console.print(f"\n[bold]Creating[/] [cyan]{name}[/] with stack [green]{stack_name}[/] → {target}")
    created = apply_stack(stack_name, target, project_name=name)
    console.print(f"\n[green]✓ Done![/] {len(created)} files written.")
    console.print(f"  cd {target}")
    console.print("  pip install -e .")
    return target


def project_doctor(path: Path | None = None) -> dict[str, Any]:
    root = (path or Path.cwd()).resolve()
    score = 0
    max_score = 100
    findings: list[tuple[str, str, int]] = []
    def ok(msg: str, pts: int = 5) -> None:
        nonlocal score
        score += pts
        findings.append(("ok", msg, pts))
    def warn(msg: str, pts: int = 0) -> None:
        findings.append(("warn", msg, pts))
    def fail(msg: str, pts: int = 0) -> None:
        findings.append(("fail", msg, pts))
    if (root / "pyproject.toml").exists() or (root / "setup.py").exists() or (root / "setup.cfg").exists():
        ok("Package metadata (pyproject/setup)", 10)
    else:
        fail("No pyproject.toml / setup.py")
    if (root / "README.md").exists() or (root / "README.rst").exists():
        ok("README present", 8)
    else:
        warn("No README")
    if (root / "LICENSE").exists() or (root / "LICENSE.md").exists():
        ok("LICENSE present", 5)
    else:
        warn("No LICENSE")
    if (root / ".gitignore").exists():
        ok(".gitignore present", 5)
    else:
        warn("No .gitignore")
    if (root / "src").is_dir():
        ok("src/ layout", 8)
    elif any((root / d).is_dir() for d in ("app", "lib", root.name.replace("-", "_"))):
        ok("package directory found", 5)
    else:
        warn("No clear package layout")
    tests_dir = root / "tests" if (root / "tests").is_dir() else root / "test"
    if tests_dir.is_dir() and any(tests_dir.rglob("test_*.py")):
        ok("Tests found", 12)
    else:
        warn("No tests detected")
    gh = root / ".github" / "workflows"
    if gh.is_dir() and any(gh.glob("*.yml")):
        ok("GitHub Actions CI", 10)
    else:
        warn("No CI workflows")
    if (root / "Dockerfile").exists() or (root / "docker-compose.yml").exists():
        ok("Docker support", 6)
    else:
        warn("No Dockerfile / compose")
    if (root / ".pre-commit-config.yaml").exists():
        ok("pre-commit config", 5)
    if (root / "Makefile").exists() or (root / "justfile").exists():
        ok("Task runner (Makefile/just)", 4)
    if (root / "pytest.ini").exists() or (root / "pyproject.toml").exists():
        ok("pytest config possible", 3)
    if (root / ".env.example").exists() or (root / ".env.sample").exists():
        ok(".env.example present", 4)
    score = min(score, max_score)
    return {"path": str(root), "score": score, "max": max_score, "findings": findings, "grade": _grade(score)}


def _grade(score: int) -> str:
    if score >= 85: return "A"
    if score >= 70: return "B"
    if score >= 55: return "C"
    if score >= 40: return "D"
    return "F"


def print_doctor_report(report: dict[str, Any]) -> None:
    grade = report["grade"]
    color = {"A": "green", "B": "cyan", "C": "yellow", "D": "orange1", "F": "red"}.get(grade, "white")
    console.print(Panel.fit(
        f"[bold]Project Doctor[/]  score [bold {color}]{report['score']}/{report['max']}[/]  grade [{color}]{grade}[/]\n"
        f"[dim]{report['path']}[/]",
        border_style=color,
    ))
    table = Table(show_header=True, header_style="bold")
    table.add_column("Status", width=8)
    table.add_column("Finding")
    table.add_column("Pts", justify="right")
    for level, msg, pts in report["findings"]:
        icon = {"ok": "[green]✓[/]", "warn": "[yellow]![/]", "fail": "[red]✗[/]"}.get(level, "?")
        table.add_row(icon, msg, str(pts) if pts else "")
    console.print(table)


def suggest_structure(kind: str = "api") -> str:
    trees = {
        "api": "my-api/\n├── src/\n│   └── my_api/\n│       ├── __init__.py\n│       ├── main.py\n│       ├── routers/\n│       ├── models/\n│       └── settings.py\n├── tests/\n│   ├── conftest.py\n│   └── test_main.py\n├── Dockerfile\n├── docker-compose.yml\n├── pyproject.toml\n├── README.md\n└── .github/workflows/ci.yml\n",
        "cli": "my-cli/\n├── src/\n│   └── my_cli/\n│       ├── __init__.py\n│       ├── cli.py\n│       └── __main__.py\n├── tests/\n├── pyproject.toml\n├── README.md\n└── Makefile\n",
        "lib": "my-lib/\n├── src/\n│   └── my_lib/\n│       └── __init__.py\n├── tests/\n├── docs/\n├── pyproject.toml\n├── README.md\n├── LICENSE\n└── .github/workflows/\n",
        "data": "my-analysis/\n├── notebooks/\n├── data/\n│   ├── raw/\n│   └── processed/\n├── src/\n├── reports/\n├── pyproject.toml\n└── README.md\n",
    }
    return trees.get(kind, trees["api"])
