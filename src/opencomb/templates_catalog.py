"""Large catalog of selectable project templates."""
from __future__ import annotations

from pathlib import Path
from typing import Callable

from opencomb.templates_base import FileSpec, ProjectTemplate, _pkg
from opencomb.templates_a import *  # noqa: F403
from opencomb.templates_b import *  # noqa: F403

BUILDERS: dict[str, Callable[[str], list]] = {}
META: list[tuple] = []


def _register() -> None:
    """Populate BUILDERS/META from imported tpl_* and explicit meta list."""
    import opencomb.templates_a as a
    import opencomb.templates_b as b
    import opencomb.templates_catalog as self_mod

    # explicit ordered registry
    registry = [
        ("minimal", "Minimal package", "Python", "Tiny installable package", ["python"]),
        ("cli", "Typer CLI", "Python", "CLI with Typer + Rich", ["cli"]),
        ("fastapi", "FastAPI API", "Web", "REST API with /health", ["api"]),
        ("flask", "Flask app", "Web", "Lightweight Flask JSON app", ["api"]),
        ("discord", "Discord bot", "Bots", "discord.py bot with !ping", ["bot"]),
        ("telegram", "Telegram bot", "Bots", "python-telegram-bot starter", ["bot"]),
        ("datascience", "Data science", "Data", "pandas/numpy layout", ["data"]),
        ("scraper", "Web scraper", "Data", "httpx + BeautifulSoup", ["scraper"]),
        ("ml-api", "ML API", "ML", "FastAPI /predict skeleton", ["ml"]),
        ("worker", "Background worker", "Backend", "Loop worker skeleton", ["worker"]),
        ("library", "Python library", "Python", "Library with py.typed", ["lib"]),
        ("monorepo", "Mini monorepo", "Structure", "packages/core,api,cli", ["mono"]),
        ("docker-api", "Dockerized API", "Deploy", "FastAPI + Dockerfile", ["docker"]),
        ("pytest", "Pytest only", "Testing", "tests/ + conftest", ["test"]),
        ("github-ci", "GitHub Actions CI", "DevOps", "Ready CI workflow", ["ci"]),
        ("static", "Static website", "Web", "HTML/CSS/JS starter", ["html"]),
        ("prt", "PRT script", "OpenComb", ".prt script project", ["prt"]),
        ("cron", "Cron job", "Backend", "Schedulable job module", ["cron"]),
        ("tools-api", "Tools API", "Backend", "Simple tools HTTP server", ["api"]),
        ("streamlit", "Streamlit app", "Web", "Interactive Streamlit dashboard", ["streamlit"]),
        ("gradio", "Gradio app", "ML", "Gradio UI for ML demos", ["gradio"]),
        ("click", "Click CLI", "Python", "CLI with Click", ["cli"]),
        ("websocket", "WebSocket API", "Web", "FastAPI WebSocket echo", ["ws"]),
        ("notebook", "Jupyter project", "Data", "Notebook + requirements", ["jupyter"]),
        ("fastapi-jwt", "FastAPI JWT", "Web", "Login + JWT /me", ["jwt"]),
        ("django-lite", "Django lite", "Web", "Minimal Django JSON home", ["django"]),
        ("sqlalchemy", "SQLAlchemy SQLite", "Data", "SQLite + SQLAlchemy 2.0", ["db"]),
        ("celery", "Celery worker", "Backend", "Celery + Redis task", ["celery"]),
        ("typer-table", "Typer Rich table", "Python", "CLI printing a Rich table", ["cli"]),
        ("rest-client", "REST client", "Python", "httpx client class", ["http"]),
        ("plugin", "Plugin package", "Python", "register() hook package", ["plugin"]),
        ("argparse", "argparse CLI", "Python", "stdlib argparse CLI", ["cli"]),
        ("fastapi-cors", "FastAPI CORS", "Web", "API with open CORS", ["api"]),
        ("loguru", "Loguru app", "Python", "Logging with loguru", ["log"]),
        ("settings", "Pydantic settings", "Python", "Settings from env/.env", ["config"]),
        ("mkdocs", "MkDocs site", "Docs", "mkdocs-material starter", ["docs"]),
        ("precommit", "pre-commit", "DevOps", "Ruff pre-commit hooks", ["ci"]),
        ("gh-pages", "GitHub Pages", "Web", "Static index + workflow", ["pages"]),
        ("llm-cli", "LLM CLI stub", "AI", "CLI stub for LLM prompts", ["ai"]),
        ("pygame", "Pygame window", "Game", "Minimal pygame loop", ["game"]),
        ("aiohttp", "aiohttp server", "Web", "aiohttp JSON server", ["web"]),
        ("starlette", "Starlette app", "Web", "Starlette + uvicorn", ["web"]),
        ("textual", "Textual TUI", "Python", "Terminal UI with Textual", ["tui"]),
        ("nicegui", "NiceGUI app", "Web", "NiceGUI interactive UI", ["ui"]),
        ("polars", "Polars data", "Data", "Polars DataFrame demo", ["data"]),
        ("typer-async", "Async Typer CLI", "Python", "Typer + asyncio", ["cli"]),
        ("fastapi-sqlmodel", "FastAPI SQLModel", "Web", "CRUD items with SQLite", ["api"]),
        ("pytest-asyncio", "pytest-asyncio", "Testing", "Async test project", ["test"]),
        ("dockerfile", "Dockerfile only", "Deploy", "Minimal Dockerfile", ["docker"]),
        ("compose", "Compose stack", "Deploy", "nginx + redis + postgres", ["docker"]),
        ("gh-release", "GitHub Release CI", "DevOps", "Build on version tags", ["ci"]),
        ("schema", "Pydantic schema", "Python", "JSON schema from model", ["schema"]),
        ("yaml-config", "YAML config", "Python", "Load config.yaml", ["config"]),
        ("stdlib-http", "stdlib HTTP", "Web", "http.server JSON", ["http"]),
        ("rich-dash", "Rich dashboard", "Python", "Live Rich layout", ["tui"]),
        ("pyrunner", "PyRunner (JS+Pyodide)", "Web", "Run Python online; packages.json only, no GUI", ["pyodide"]),
    ]

    builders: dict[str, Callable] = {}
    for mod in (a, b):
        for name in dir(mod):
            if name.startswith("tpl_"):
                tid = name[4:].replace("_", "-")
                # map function names to ids
                builders[name] = getattr(mod, name)

    # explicit id -> function map
    def resolve(tid: str):
        # try common name patterns
        candidates = [
            "tpl_" + tid.replace("-", "_"),
            "tpl_" + tid.replace("-", ""),
        ]
        # special cases
        special = {
            "ml-api": "tpl_ml_api",
            "docker-api": "tpl_docker_api",
            "github-ci": "tpl_github_actions",
            "tools-api": "tpl_mcp_server",
            "fastapi-jwt": "tpl_fastapi_jwt",
            "django-lite": "tpl_django_lite",
            "typer-table": "tpl_typer_rich_table",
            "rest-client": "tpl_rest_client",
            "fastapi-cors": "tpl_fastapi_cors",
            "gh-pages": "tpl_github_pages",
            "llm-cli": "tpl_openai_cli",
            "fastapi-sqlmodel": "tpl_fastapi_sqlmodel",
            "pytest-asyncio": "tpl_pytest_asyncio",
            "dockerfile": "tpl_dockerfile_only",
            "compose": "tpl_compose_stack",
            "gh-release": "tpl_github_release",
            "schema": "tpl_json_schema",
            "yaml-config": "tpl_cli_config_yaml",
            "stdlib-http": "tpl_http_server_stdlib",
            "rich-dash": "tpl_rich_dashboard",
            "typer-async": "tpl_typer_async",
            "click": "tpl_click_cli",
            "plugin": "tpl_cli_plugin",
            "argparse": "tpl_argparse_cli",
            "settings": "tpl_pydantic_settings",
            "pygame": "tpl_game_pygame",
            "prt": "tpl_prt_script",
            "static": "tpl_static_site",
            "pytest": "tpl_pytest_only",
        }
        if tid in special:
            candidates.insert(0, special[tid])
        for c in candidates:
            if hasattr(a, c):
                return getattr(a, c)
            if hasattr(b, c):
                return getattr(b, c)
        return None

    self_mod.META.clear()
    self_mod.BUILDERS.clear()
    for tid, name, cat, desc, tags in registry:
        fn = resolve(tid)
        if fn:
            self_mod.BUILDERS[tid] = fn
            self_mod.META.append((tid, name, cat, desc, tags))


_register()


def list_templates() -> list[ProjectTemplate]:
    out: list[ProjectTemplate] = []
    for tid, name, cat, desc, tags in META:
        out.append(ProjectTemplate(id=tid, name=name, category=cat, description=desc, tags=list(tags)))
    return out


def apply_template(template_id: str, project_name: str, dest: Path) -> Path:
    if template_id not in BUILDERS:
        raise KeyError(f"Unknown template: {template_id}")
    dest = dest.resolve()
    if dest.exists() and any(dest.iterdir()):
        raise FileExistsError(f"Directory not empty: {dest}")
    dest.mkdir(parents=True, exist_ok=True)
    for spec in BUILDERS[template_id](project_name):
        path = dest / spec.path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(spec.content, encoding="utf-8")
    (dest / ".opencomb-template").write_text(template_id + "\n", encoding="utf-8")
    return dest
