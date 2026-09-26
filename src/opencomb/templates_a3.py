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


def tpl_gradio(name: str) -> list[FileSpec]:
    p = _pkg(name)
    files = [
        FileSpec("pyproject.toml", _pyproject(name, 'Gradio app', ['gradio>=4.0'])),
        FileSpec(".gitignore", _gitignore()),
        _readme(name, f"```bash\npip install -e .\n```"),
        FileSpec(f"src/{p}/__init__.py", _init()),
        FileSpec(f"src/{p}/app.py", "import gradio as gr\ndef greet(n):\n    return f'Hello {n}'\ngr.Interface(fn=greet, inputs='text', outputs='text').launch()\n"),
    ]
    files.extend(_tests_smoke(p))
    return files

def tpl_click_cli(name: str) -> list[FileSpec]:
    p = _pkg(name)
    files = [
        FileSpec("pyproject.toml", _pyproject(name, 'Click CLI', ['click>=8.0'])),
        FileSpec(".gitignore", _gitignore()),
        _readme(name, f"```bash\npip install -e .\n```"),
        FileSpec(f"src/{p}/__init__.py", _init()),
        FileSpec(f"src/{p}/cli.py", "import click\n@click.command()\n@click.option('--name', default='world')\ndef main(name):\n    click.echo(f'Hello {name}')\n\nif __name__ == '__main__':\n    main()\n"),
    ]
    files.extend(_tests_smoke(p))
    return files

def tpl_websocket(name: str) -> list[FileSpec]:
    p = _pkg(name)
    files = [
        FileSpec("pyproject.toml", _pyproject(name, 'WebSocket server', ['fastapi>=0.110', 'uvicorn[standard]>=0.27'])),
        FileSpec(".gitignore", _gitignore()),
        _readme(name, f"```bash\npip install -e .\n```"),
        FileSpec(f"src/{p}/__init__.py", _init()),
        FileSpec(f"src/{p}/main.py", "from fastapi import FastAPI, WebSocket\napp = FastAPI()\n@app.websocket('/ws')\nasync def ws(websocket: WebSocket):\n    await websocket.accept()\n    await websocket.send_text('hi')\n"),
    ]
    files.extend(_tests_smoke(p))
    return files

def tpl_notebook(name: str) -> list[FileSpec]:
    p = _pkg(name)
    files = [
        FileSpec("pyproject.toml", _pyproject(name, 'Notebook project', ['jupyter>=1.0'])),
        FileSpec(".gitignore", _gitignore()),
        _readme(name, f"```bash\npip install -e .\n```"),
        FileSpec(f"src/{p}/__init__.py", _init()),
        FileSpec("notebooks/starter.ipynb", "{\"cells\": [], \"metadata\": {}, \"nbformat\": 4, \"nbformat_minor\": 5}\n"),
    ]
    files.extend(_tests_smoke(p))
    return files

def tpl_fastapi_jwt(name: str) -> list[FileSpec]:
    p = _pkg(name)
    files = [
        FileSpec("pyproject.toml", _pyproject(name, 'FastAPI + JWT', ['fastapi>=0.110', 'uvicorn[standard]>=0.27', 'pyjwt>=2.8'])),
        FileSpec(".gitignore", _gitignore()),
        _readme(name, f"```bash\npip install -e .\n```"),
        FileSpec(f"src/{p}/__init__.py", _init()),
        FileSpec(f"src/{p}/main.py", "from fastapi import FastAPI\napp = FastAPI()\n@app.get('/health')\ndef health():\n    return {'ok': True}\n"),
    ]
    files.extend(_tests_smoke(p))
    return files

def tpl_django_lite(name: str) -> list[FileSpec]:
    p = _pkg(name)
    files = [
        FileSpec("pyproject.toml", _pyproject(name, 'Django lite', ['django>=5.0'])),
        FileSpec(".gitignore", _gitignore()),
        _readme(name, f"```bash\npip install -e .\n```"),
        FileSpec(f"src/{p}/__init__.py", _init()),
        FileSpec("manage.py", "#!/usr/bin/env python\nimport django\nprint('django lite starter')\n"),
    ]
    files.extend(_tests_smoke(p))
    return files

def tpl_sqlalchemy(name: str) -> list[FileSpec]:
    p = _pkg(name)
    files = [
        FileSpec("pyproject.toml", _pyproject(name, 'SQLAlchemy', ['sqlalchemy>=2.0'])),
        FileSpec(".gitignore", _gitignore()),
        _readme(name, f"```bash\npip install -e .\n```"),
        FileSpec(f"src/{p}/__init__.py", _init()),
        FileSpec(f"src/{p}/db.py", "from sqlalchemy import create_engine\nengine = create_engine('sqlite:///./app.db')\n"),
    ]
    files.extend(_tests_smoke(p))
    return files

def tpl_celery(name: str) -> list[FileSpec]:
    p = _pkg(name)
    files = [
        FileSpec("pyproject.toml", _pyproject(name, 'Celery worker', ['celery>=5.3'])),
        FileSpec(".gitignore", _gitignore()),
        _readme(name, f"```bash\npip install -e .\n```"),
        FileSpec(f"src/{p}/__init__.py", _init()),
        FileSpec(f"src/{p}/tasks.py", "from celery import Celery\napp = Celery('tasks', broker='redis://localhost:6379/0')\n@app.task\ndef add(x, y):\n    return x + y\n"),
    ]
    files.extend(_tests_smoke(p))
    return files
