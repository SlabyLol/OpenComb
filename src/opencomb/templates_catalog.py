"""Large catalog of selectable project templates."""
from __future__ import annotations

from pathlib import Path
from typing import Callable

from opencomb.templates_base import FileSpec, ProjectTemplate, _pkg
from opencomb.templates_a import *  # noqa: F403
from opencomb.templates_b import *  # noqa: F403

BUILDERS: dict[str, Callable[[str], list]] = {
    "minimal": tpl_minimal,
    "cli": tpl_cli,
    "fastapi": tpl_fastapi,
    "flask": tpl_flask,
    "discord": tpl_discord,
    "telegram": tpl_bot_telegram,
    "datascience": tpl_datascience,
    "scraper": tpl_scraper,
    "ml-api": tpl_ml_api,
    "worker": tpl_worker,
    "library": tpl_library,
    "monorepo": tpl_monorepo,
    "docker-api": tpl_docker_api,
    "pytest": tpl_pytest_only,
    "github-ci": tpl_github_actions,
    "static": tpl_static_site,
    "prt": tpl_prt_script,
    "cron": tpl_cron_job,
    "tools-api": tpl_mcp_server,
    "streamlit": tpl_streamlit,
    "gradio": tpl_gradio,
    "click": tpl_click_cli,
    "websocket": tpl_websocket,
    "notebook": tpl_notebook,
    "fastapi-jwt": tpl_fastapi_jwt,
    "django-lite": tpl_django_lite,
    "sqlalchemy": tpl_sqlalchemy,
    "celery": tpl_celery,
    "typer-table": tpl_typer_rich_table,
    "rest-client": tpl_rest_client,
    "plugin": tpl_cli_plugin,
    "argparse": tpl_argparse_cli,
    "fastapi-cors": tpl_fastapi_cors,
    "loguru": tpl_loguru_app,
    "settings": tpl_pydantic_settings,
    "mkdocs": tpl_mkdocs,
    "precommit": tpl_precommit,
    "gh-pages": tpl_github_pages,
    "llm-cli": tpl_openai_cli,
    "pygame": tpl_game_pygame,
    "aiohttp": tpl_aiohttp,
    "starlette": tpl_starlette,
    "textual": tpl_textual,
    "nicegui": tpl_nicegui,
    "polars": tpl_polars,
    "typer-async": tpl_typer_async,
    "fastapi-sqlmodel": tpl_fastapi_sqlmodel,
    "pytest-asyncio": tpl_pytest_asyncio,
    "dockerfile": tpl_dockerfile_only,
    "compose": tpl_compose_stack,
    "gh-release": tpl_github_release,
    "schema": tpl_json_schema,
    "yaml-config": tpl_cli_config_yaml,
    "stdlib-http": tpl_http_server_stdlib,
    "rich-dash": tpl_rich_dashboard,
    "pyrunner": tpl_pyrunner,
}

META = [
    (tid, tid.replace("-", " ").title(), "General", f"Template {tid}", [])
    for tid in BUILDERS
]


def list_templates() -> list[ProjectTemplate]:
    return [
        ProjectTemplate(id=tid, name=name, category=cat, description=desc, tags=list(tags))
        for tid, name, cat, desc, tags in META
    ]


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
