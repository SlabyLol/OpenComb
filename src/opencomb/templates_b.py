"""Template builders B."""
from __future__ import annotations
from opencomb.templates_base import FileSpec, _pkg, _pyproject, _gitignore
from opencomb.templates_a import tpl_minimal, tpl_fastapi, tpl_cli

def tpl_typer_rich_table(name: str):
    return tpl_cli(name)
def tpl_rest_client(name: str):
    return tpl_minimal(name)
def tpl_cli_plugin(name: str):
    return tpl_minimal(name)
def tpl_argparse_cli(name: str):
    return tpl_minimal(name)
def tpl_fastapi_cors(name: str):
    return tpl_fastapi(name)
def tpl_loguru_app(name: str):
    return tpl_minimal(name)
def tpl_pydantic_settings(name: str):
    return tpl_minimal(name)
def tpl_mkdocs(name: str):
    return [FileSpec("mkdocs.yml", f"site_name: {name}\n"), FileSpec("docs/index.md", f"# {name}\n"), FileSpec("README.md", f"# {name}\n")]
def tpl_precommit(name: str):
    return tpl_minimal(name)
def tpl_github_pages(name: str):
    return [FileSpec("index.html", f"<!doctype html><h1>{name}</h1>\n"), FileSpec("README.md", f"# {name}\n")]
def tpl_openai_cli(name: str):
    return tpl_minimal(name)
def tpl_game_pygame(name: str):
    return tpl_minimal(name)
def tpl_aiohttp(name: str):
    return tpl_minimal(name)
def tpl_starlette(name: str):
    return tpl_fastapi(name)
def tpl_textual(name: str):
    return tpl_minimal(name)
def tpl_nicegui(name: str):
    return tpl_minimal(name)
def tpl_polars(name: str):
    return tpl_minimal(name)
def tpl_typer_async(name: str):
    return tpl_cli(name)
def tpl_fastapi_sqlmodel(name: str):
    return tpl_fastapi(name)
def tpl_pytest_asyncio(name: str):
    return tpl_minimal(name)
def tpl_dockerfile_only(name: str):
    return [FileSpec("Dockerfile", f"FROM python:3.12-slim\nWORKDIR /app\nCMD [\"python\",\"-c\",\"print('{name}')\"]\n"), FileSpec("README.md", f"# {name}\n")]
def tpl_compose_stack(name: str):
    return [FileSpec("docker-compose.yml", "services:\n  web:\n    image: nginx:alpine\n    ports: [\"8080:80\"]\n"), FileSpec("README.md", f"# {name}\n")]
def tpl_github_release(name: str):
    return tpl_minimal(name)
def tpl_json_schema(name: str):
    return tpl_minimal(name)
def tpl_cli_config_yaml(name: str):
    return tpl_minimal(name)
def tpl_http_server_stdlib(name: str):
    return tpl_minimal(name)
def tpl_rich_dashboard(name: str):
    return tpl_minimal(name)
def tpl_pyrunner(name: str):
    return [
        FileSpec("index.html", f"<!doctype html><title>{name} PyRunner</title><h1>{name}</h1><p>Edit packages.json</p>\n"),
        FileSpec("packages.json", '{\n  "packages": ["numpy"],\n  "entry": "main.py"\n}\n'),
        FileSpec("main.py", 'print("PyRunner")\n'),
        FileSpec("pyrunner.js", "console.log('use full PyRunner from opencomb new pyrunner')\n"),
        FileSpec("README.md", f"# {name} – PyRunner\n\npackages.json only, no GUI.\n"),
    ]
