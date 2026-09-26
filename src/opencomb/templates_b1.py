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


def tpl_typer_rich_table(name: str) -> list[FileSpec]:
    p = _pkg(name)
    files = [
        FileSpec("pyproject.toml", _pyproject(name, 'Typer + Rich table', ['typer>=0.12', 'rich>=13'])),
        FileSpec(".gitignore", _gitignore()),
        _readme(name, f"```bash\npip install -e .\n```"),
        FileSpec(f"src/{p}/__init__.py", _init()),
        FileSpec(f"src/{p}/cli.py", "import typer\nfrom rich.table import Table\nfrom rich.console import Console\napp = typer.Typer()\n@app.command()\ndef show():\n    t = Table(title='Demo')\n    t.add_column('A')\n    t.add_row('1')\n    Console().print(t)\n"),
    ]
    files.extend(_tests_smoke(p))
    return files

def tpl_rest_client(name: str) -> list[FileSpec]:
    p = _pkg(name)
    files = [
        FileSpec("pyproject.toml", _pyproject(name, 'REST client', ['httpx>=0.27'])),
        FileSpec(".gitignore", _gitignore()),
        _readme(name, f"```bash\npip install -e .\n```"),
        FileSpec(f"src/{p}/__init__.py", _init()),
        FileSpec(f"src/{p}/client.py", "import httpx\ndef get_json(url: str) -> dict:\n    return httpx.get(url, timeout=20).json()\n"),
    ]
    files.extend(_tests_smoke(p))
    return files

def tpl_cli_plugin(name: str) -> list[FileSpec]:
    p = _pkg(name)
    files = [
        FileSpec("pyproject.toml", _pyproject(name, 'CLI plugin', ['typer>=0.12'])),
        FileSpec(".gitignore", _gitignore()),
        _readme(name, f"```bash\npip install -e .\n```"),
        FileSpec(f"src/{p}/__init__.py", _init()),
        FileSpec(f"src/{p}/plugin.py", "import typer\napp = typer.Typer()\n@app.command()\ndef ping():\n    print('pong')\n"),
    ]
    files.extend(_tests_smoke(p))
    return files

def tpl_argparse_cli(name: str) -> list[FileSpec]:
    p = _pkg(name)
    files = [
        FileSpec("pyproject.toml", _pyproject(name, 'Argparse CLI', [])),
        FileSpec(".gitignore", _gitignore()),
        _readme(name, f"```bash\npip install -e .\n```"),
        FileSpec(f"src/{p}/__init__.py", _init()),
        FileSpec(f"src/{p}/cli.py", "import argparse\ndef main():\n    p = argparse.ArgumentParser()\n    p.add_argument('--name', default='world')\n    args = p.parse_args()\n    print('Hello', args.name)\n\nif __name__ == '__main__':\n    main()\n"),
    ]
    files.extend(_tests_smoke(p))
    return files

def tpl_fastapi_cors(name: str) -> list[FileSpec]:
    p = _pkg(name)
    files = [
        FileSpec("pyproject.toml", _pyproject(name, 'FastAPI CORS', ['fastapi>=0.110', 'uvicorn[standard]>=0.27'])),
        FileSpec(".gitignore", _gitignore()),
        _readme(name, f"```bash\npip install -e .\n```"),
        FileSpec(f"src/{p}/__init__.py", _init()),
        FileSpec(f"src/{p}/main.py", "from fastapi import FastAPI\nfrom fastapi.middleware.cors import CORSMiddleware\napp = FastAPI()\napp.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])\n@app.get('/')\ndef root():\n    return {'ok': True}\n"),
    ]
    files.extend(_tests_smoke(p))
    return files

def tpl_loguru_app(name: str) -> list[FileSpec]:
    p = _pkg(name)
    files = [
        FileSpec("pyproject.toml", _pyproject(name, 'Loguru app', ['loguru>=0.7'])),
        FileSpec(".gitignore", _gitignore()),
        _readme(name, f"```bash\npip install -e .\n```"),
        FileSpec(f"src/{p}/__init__.py", _init()),
        FileSpec(f"src/{p}/app.py", "from loguru import logger\ndef main():\n    logger.info('hello')\n\nif __name__ == '__main__':\n    main()\n"),
    ]
    files.extend(_tests_smoke(p))
    return files

def tpl_pydantic_settings(name: str) -> list[FileSpec]:
    p = _pkg(name)
    files = [
        FileSpec("pyproject.toml", _pyproject(name, 'Pydantic settings', ['pydantic-settings>=2.0'])),
        FileSpec(".gitignore", _gitignore()),
        _readme(name, f"```bash\npip install -e .\n```"),
        FileSpec(f"src/{p}/__init__.py", _init()),
        FileSpec(f"src/{p}/settings.py", "from pydantic_settings import BaseSettings\nclass Settings(BaseSettings):\n    app_name: str = 'app'\n    class Config:\n        env_file = '.env'\n"),
    ]
    files.extend(_tests_smoke(p))
    return files

def tpl_mkdocs(name: str) -> list[FileSpec]:
    p = _pkg(name)
    files = [
        FileSpec("pyproject.toml", _pyproject(name, 'MkDocs', ['mkdocs>=1.5'])),
        FileSpec(".gitignore", _gitignore()),
        _readme(name, f"```bash\npip install -e .\n```"),
        FileSpec(f"src/{p}/__init__.py", _init()),
        FileSpec("mkdocs.yml", "site_name: %s\nnav:\n  - Home: index.md\n" % name),
        FileSpec("docs/index.md", f"# {name}\n"),
    ]
    files.extend(_tests_smoke(p))
    return files

def tpl_precommit(name: str) -> list[FileSpec]:
    p = _pkg(name)
    files = [
        FileSpec("pyproject.toml", _pyproject(name, 'Pre-commit', [])),
        FileSpec(".gitignore", _gitignore()),
        _readme(name, f"```bash\npip install -e .\n```"),
        FileSpec(f"src/{p}/__init__.py", _init()),
        FileSpec(".pre-commit-config.yaml", "repos:\n  - repo: https://github.com/astral-sh/ruff-pre-commit\n    rev: v0.5.0\n    hooks:\n      - id: ruff\n"),
    ]
    files.extend(_tests_smoke(p))
    return files

def tpl_github_pages(name: str) -> list[FileSpec]:
    p = _pkg(name)
    files = [
        FileSpec("pyproject.toml", _pyproject(name, 'GitHub Pages', [])),
        FileSpec(".gitignore", _gitignore()),
        _readme(name, f"```bash\npip install -e .\n```"),
        FileSpec(f"src/{p}/__init__.py", _init()),
        FileSpec("docs/index.html", f"<!doctype html><title>{name}</title><h1>{name}</h1>\n"),
    ]
    files.extend(_tests_smoke(p))
    return files
