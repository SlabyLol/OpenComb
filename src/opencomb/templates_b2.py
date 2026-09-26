"""Template builders — plain Python source (no encoding)."""
from __future__ import annotations

from opencomb.templates_base import FileSpec, _pkg, _pyproject, _gitignore


def _readme(name: str, body: str) -> FileSpec:
    return FileSpec("README.md", f"# {name}\n\n{body.strip()}\n")


def _init() -> str:
    return '__version__ = "0.1.0"\n'


def _tests_smoke(pkg: str) -> list[FileSpec]:
    return [
        FileSpec("tests/conftest.py", "import pytest\n\n@pytest.fixture\ndef any_data():\n    return {\"ok\": True}\n"),
        FileSpec("tests/test_smoke.py", f"def test_version():\n    import {pkg}\n    assert getattr({pkg}, \"__version__\", \"0.1.0\")\n"),
        FileSpec("pytest.ini", "[pytest]\ntestpaths = tests\npythonpath = src\n"),
    ]


def tpl_openai_cli(name: str) -> list[FileSpec]:
    p = _pkg(name)
    files = [
        FileSpec("pyproject.toml", _pyproject(name, 'OpenAI CLI', ['openai>=1.0', 'typer>=0.12'])),
        FileSpec(".gitignore", _gitignore()),
        _readme(name, f"```bash\npip install -e .\n```"),
        FileSpec(f"src/{p}/__init__.py", _init()),
        FileSpec(f"src/{p}/cli.py", "import os, typer\napp = typer.Typer()\n@app.command()\ndef ask(prompt: str):\n    print('Set OPENAI_API_KEY; prompt:', prompt)\n"),
    ]
    files.extend(_tests_smoke(p))
    return files

def tpl_game_pygame(name: str) -> list[FileSpec]:
    p = _pkg(name)
    files = [
        FileSpec("pyproject.toml", _pyproject(name, 'Pygame', ['pygame>=2.5'])),
        FileSpec(".gitignore", _gitignore()),
        _readme(name, f"```bash\npip install -e .\n```"),
        FileSpec(f"src/{p}/__init__.py", _init()),
        FileSpec(f"src/{p}/game.py", "import pygame\npygame.init()\nscreen = pygame.display.set_mode((640, 480))\nprint('pygame starter')\n"),
    ]
    files.extend(_tests_smoke(p))
    return files

def tpl_aiohttp(name: str) -> list[FileSpec]:
    p = _pkg(name)
    files = [
        FileSpec("pyproject.toml", _pyproject(name, 'aiohttp server', ['aiohttp>=3.9'])),
        FileSpec(".gitignore", _gitignore()),
        _readme(name, f"```bash\npip install -e .\n```"),
        FileSpec(f"src/{p}/__init__.py", _init()),
        FileSpec(f"src/{p}/server.py", "from aiohttp import web\nasync def hello(request):\n    return web.json_response({'ok': True})\napp = web.Application()\napp.router.add_get('/', hello)\n"),
    ]
    files.extend(_tests_smoke(p))
    return files

def tpl_starlette(name: str) -> list[FileSpec]:
    p = _pkg(name)
    files = [
        FileSpec("pyproject.toml", _pyproject(name, 'Starlette', ['starlette>=0.37', 'uvicorn[standard]>=0.27'])),
        FileSpec(".gitignore", _gitignore()),
        _readme(name, f"```bash\npip install -e .\n```"),
        FileSpec(f"src/{p}/__init__.py", _init()),
        FileSpec(f"src/{p}/app.py", "from starlette.applications import Starlette\nfrom starlette.responses import JSONResponse\nfrom starlette.routing import Route\nasync def homepage(request):\n    return JSONResponse({'ok': True})\napp = Starlette(routes=[Route('/', homepage)])\n"),
    ]
    files.extend(_tests_smoke(p))
    return files

def tpl_textual(name: str) -> list[FileSpec]:
    p = _pkg(name)
    files = [
        FileSpec("pyproject.toml", _pyproject(name, 'Textual TUI', ['textual>=0.50'])),
        FileSpec(".gitignore", _gitignore()),
        _readme(name, f"```bash\npip install -e .\n```"),
        FileSpec(f"src/{p}/__init__.py", _init()),
        FileSpec(f"src/{p}/app.py", "from textual.app import App, ComposeResult\nfrom textual.widgets import Label\nclass MyApp(App):\n    def compose(self) -> ComposeResult:\n        yield Label('OpenComb Textual')\n\nif __name__ == '__main__':\n    MyApp().run()\n"),
    ]
    files.extend(_tests_smoke(p))
    return files

def tpl_nicegui(name: str) -> list[FileSpec]:
    p = _pkg(name)
    files = [
        FileSpec("pyproject.toml", _pyproject(name, 'NiceGUI', ['nicegui>=1.4'])),
        FileSpec(".gitignore", _gitignore()),
        _readme(name, f"```bash\npip install -e .\n```"),
        FileSpec(f"src/{p}/__init__.py", _init()),
        FileSpec(f"src/{p}/app.py", "from nicegui import ui\nui.label('OpenComb NiceGUI')\nui.run()\n"),
    ]
    files.extend(_tests_smoke(p))
    return files

def tpl_polars(name: str) -> list[FileSpec]:
    p = _pkg(name)
    files = [
        FileSpec("pyproject.toml", _pyproject(name, 'Polars data', ['polars>=0.20'])),
        FileSpec(".gitignore", _gitignore()),
        _readme(name, f"```bash\npip install -e .\n```"),
        FileSpec(f"src/{p}/__init__.py", _init()),
        FileSpec(f"src/{p}/data.py", "import polars as pl\ndef load(path: str) -> pl.DataFrame:\n    return pl.read_csv(path)\n"),
    ]
    files.extend(_tests_smoke(p))
    return files

def tpl_typer_async(name: str) -> list[FileSpec]:
    p = _pkg(name)
    files = [
        FileSpec("pyproject.toml", _pyproject(name, 'Async Typer', ['typer>=0.12', 'anyio>=4.0'])),
        FileSpec(".gitignore", _gitignore()),
        _readme(name, f"```bash\npip install -e .\n```"),
        FileSpec(f"src/{p}/__init__.py", _init()),
        FileSpec(f"src/{p}/cli.py", "import typer, anyio\napp = typer.Typer()\n@app.command()\ndef run():\n    async def _():\n        print('async ok')\n    anyio.run(_)\n"),
    ]
    files.extend(_tests_smoke(p))
    return files

def tpl_fastapi_sqlmodel(name: str) -> list[FileSpec]:
    p = _pkg(name)
    files = [
        FileSpec("pyproject.toml", _pyproject(name, 'FastAPI + SQLModel', ['fastapi>=0.110', 'sqlmodel>=0.0.16', 'uvicorn[standard]>=0.27'])),
        FileSpec(".gitignore", _gitignore()),
        _readme(name, f"```bash\npip install -e .\n```"),
        FileSpec(f"src/{p}/__init__.py", _init()),
        FileSpec(f"src/{p}/main.py", "from fastapi import FastAPI\nfrom sqlmodel import SQLModel, Field\nclass Item(SQLModel, table=True):\n    id: int | None = Field(default=None, primary_key=True)\n    name: str\napp = FastAPI()\n@app.get('/health')\ndef health():\n    return {'ok': True}\n"),
    ]
    files.extend(_tests_smoke(p))
    return files

def tpl_pytest_asyncio(name: str) -> list[FileSpec]:
    p = _pkg(name)
    files = [
        FileSpec("pyproject.toml", _pyproject(name, 'Pytest asyncio', ['pytest>=8.0', 'pytest-asyncio>=0.23'])),
        FileSpec(".gitignore", _gitignore()),
        _readme(name, f"```bash\npip install -e .\n```"),
        FileSpec(f"src/{p}/__init__.py", _init()),
        FileSpec("tests/test_async.py", "import pytest\n@pytest.mark.asyncio\nasync def test_ok():\n    assert True\n"),
    ]
    files.extend(_tests_smoke(p))
    return files
