"""Template builders A (core)."""
from __future__ import annotations
from opencomb.templates_base import FileSpec, _pkg, _pyproject, _gitignore

def tpl_minimal(name: str) -> list[FileSpec]:
    p = _pkg(name)
    return [
        FileSpec("pyproject.toml", _pyproject(name, "Minimal package")),
        FileSpec(".gitignore", _gitignore()),
        FileSpec("README.md", f"# {name}\n\nMinimal package.\n"),
        FileSpec(f"src/{p}/__init__.py", '__version__ = "0.1.0"\n'),
        FileSpec(f"src/{p}/__main__.py", f'print("Hello from {name}")\n'),
        FileSpec("tests/test_smoke.py", "def test_ok():\n    assert True\n"),
    ]

def tpl_cli(name: str) -> list[FileSpec]:
    p = _pkg(name)
    return [
        FileSpec("pyproject.toml", _pyproject(name, "CLI app", ["typer>=0.12", "rich>=13"], {name: f"{p}.cli:app"})),
        FileSpec(".gitignore", _gitignore()),
        FileSpec("README.md", f"# {name}\n"),
        FileSpec(f"src/{p}/__init__.py", '__version__ = "0.1.0"\n'),
        FileSpec(f"src/{p}/cli.py", f'import typer\napp = typer.Typer()\n@app.command()\ndef hello(name: str = "world"):\n    print(f"Hello {{name}}")\nif __name__ == "__main__":\n    app()\n'),
    ]

def tpl_fastapi(name: str) -> list[FileSpec]:
    p = _pkg(name)
    return [
        FileSpec("pyproject.toml", _pyproject(name, "FastAPI service", ["fastapi>=0.110", "uvicorn[standard]>=0.27"])),
        FileSpec(".gitignore", _gitignore()),
        FileSpec("README.md", f"# {name}\n"),
        FileSpec(f"src/{p}/__init__.py", '__version__ = "0.1.0"\n'),
        FileSpec(f"src/{p}/main.py", f'from fastapi import FastAPI\napp = FastAPI(title="{name}")\n@app.get("/")\ndef root():\n    return {{"app": "{name}", "status": "ok"}}\n'),
    ]

def tpl_flask(name: str):
    return tpl_minimal(name)
def tpl_discord(name: str):
    return tpl_minimal(name)
def tpl_bot_telegram(name: str):
    return tpl_minimal(name)
def tpl_datascience(name: str):
    return tpl_minimal(name)
def tpl_scraper(name: str):
    return tpl_minimal(name)
def tpl_ml_api(name: str):
    return tpl_fastapi(name)
def tpl_worker(name: str):
    return tpl_minimal(name)
def tpl_library(name: str):
    return tpl_minimal(name)
def tpl_monorepo(name: str):
    return tpl_minimal(name)
def tpl_docker_api(name: str):
    return tpl_fastapi(name)
def tpl_pytest_only(name: str):
    return tpl_minimal(name)
def tpl_github_actions(name: str):
    return tpl_minimal(name)
def tpl_static_site(name: str):
    return [FileSpec("index.html", f"<!doctype html><title>{name}</title><h1>{name}</h1>\n"), FileSpec("README.md", f"# {name}\n")]
def tpl_prt_script(name: str):
    return [FileSpec(f"{_pkg(name)}.prt", f'print("hello {name}")\n'), FileSpec("README.md", f"# {name}\n")]
def tpl_cron_job(name: str):
    return tpl_minimal(name)
def tpl_mcp_server(name: str):
    return tpl_fastapi(name)
def tpl_streamlit(name: str):
    return tpl_minimal(name)
def tpl_gradio(name: str):
    return tpl_minimal(name)
def tpl_click_cli(name: str):
    return tpl_cli(name)
def tpl_websocket(name: str):
    return tpl_fastapi(name)
def tpl_notebook(name: str):
    return tpl_minimal(name)
def tpl_fastapi_jwt(name: str):
    return tpl_fastapi(name)
def tpl_django_lite(name: str):
    return tpl_minimal(name)
def tpl_sqlalchemy(name: str):
    return tpl_minimal(name)
def tpl_celery(name: str):
    return tpl_minimal(name)
