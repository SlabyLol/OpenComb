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


def tpl_library(name: str) -> list[FileSpec]:
    p = _pkg(name)
    files = [
        FileSpec("pyproject.toml", _pyproject(name, 'Python library', [])),
        FileSpec(".gitignore", _gitignore()),
        _readme(name, f"```bash\npip install -e .\n```"),
        FileSpec(f"src/{p}/__init__.py", _init()),
        FileSpec(f"src/{p}/mathops.py", "def add(a, b):\n    return a + b\n"),
    ]
    files.extend(_tests_smoke(p))
    return files

def tpl_monorepo(name: str) -> list[FileSpec]:
    p = _pkg(name)
    files = [
        FileSpec("pyproject.toml", _pyproject(name, 'Monorepo', [])),
        FileSpec(".gitignore", _gitignore()),
        _readme(name, f"```bash\npip install -e .\n```"),
        FileSpec(f"src/{p}/__init__.py", _init()),
        FileSpec("packages/core/src/core/__init__.py", "__version__ = '0.1.0'\n"),
    ]
    files.extend(_tests_smoke(p))
    return files

def tpl_docker_api(name: str) -> list[FileSpec]:
    p = _pkg(name)
    files = [
        FileSpec("pyproject.toml", _pyproject(name, 'Dockerized API', ['fastapi>=0.110', 'uvicorn[standard]>=0.27'])),
        FileSpec(".gitignore", _gitignore()),
        _readme(name, f"```bash\npip install -e .\n```"),
        FileSpec(f"src/{p}/__init__.py", _init()),
        FileSpec(f"src/{p}/main.py", "from fastapi import FastAPI\napp = FastAPI()\n@app.get('/health')\ndef health():\n    return {'ok': True}\n"),
        FileSpec("Dockerfile", "FROM python:3.12-slim\nWORKDIR /app\nCOPY . .\nRUN pip install .\nCMD [\"uvicorn\", \"%s.main:app\", \"--host\", \"0.0.0.0\"]\n" % p),
    ]
    files.extend(_tests_smoke(p))
    return files

def tpl_pytest_only(name: str) -> list[FileSpec]:
    p = _pkg(name)
    files = [
        FileSpec("pyproject.toml", _pyproject(name, 'Pytest project', ['pytest>=8.0'])),
        FileSpec(".gitignore", _gitignore()),
        _readme(name, f"```bash\npip install -e .\n```"),
        FileSpec(f"src/{p}/__init__.py", _init()),
        FileSpec(f"src/{p}/calc.py", "def answer():\n    return 42\n"),
    ]
    files.extend(_tests_smoke(p))
    return files

def tpl_github_actions(name: str) -> list[FileSpec]:
    p = _pkg(name)
    files = [
        FileSpec("pyproject.toml", _pyproject(name, 'GitHub Actions CI', [])),
        FileSpec(".gitignore", _gitignore()),
        _readme(name, f"```bash\npip install -e .\n```"),
        FileSpec(f"src/{p}/__init__.py", _init()),
        FileSpec(".github/workflows/ci.yml", "name: CI\non: [push]\njobs:\n  test:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v4\n      - uses: actions/setup-python@v5\n        with: {python-version: '3.12'}\n      - run: pip install -e .[dev]\n      - run: pytest -q\n"),
    ]
    files.extend(_tests_smoke(p))
    return files

def tpl_static_site(name: str) -> list[FileSpec]:
    p = _pkg(name)
    files = [
        FileSpec("pyproject.toml", _pyproject(name, 'Static site', [])),
        FileSpec(".gitignore", _gitignore()),
        _readme(name, f"```bash\npip install -e .\n```"),
        FileSpec(f"src/{p}/__init__.py", _init()),
        FileSpec("index.html", "<!doctype html><title>%s</title><h1>%s</h1>\n" % (name, name)),
    ]
    files.extend(_tests_smoke(p))
    return files

def tpl_prt_script(name: str) -> list[FileSpec]:
    p = _pkg(name)
    files = [
        FileSpec("pyproject.toml", _pyproject(name, 'OpenComb PRT script', [])),
        FileSpec(".gitignore", _gitignore()),
        _readme(name, f"```bash\npip install -e .\n```"),
        FileSpec(f"src/{p}/__init__.py", _init()),
        FileSpec(f"{name}.prt", "# PRT starter\nprint \"hello from PRT\"\n"),
    ]
    files.extend(_tests_smoke(p))
    return files

def tpl_cron_job(name: str) -> list[FileSpec]:
    p = _pkg(name)
    files = [
        FileSpec("pyproject.toml", _pyproject(name, 'Cron job', [])),
        FileSpec(".gitignore", _gitignore()),
        _readme(name, f"```bash\npip install -e .\n```"),
        FileSpec(f"src/{p}/__init__.py", _init()),
        FileSpec(f"src/{p}/job.py", "def main():\n    print('cron job ran')\n\nif __name__ == '__main__':\n    main()\n"),
    ]
    files.extend(_tests_smoke(p))
    return files

def tpl_mcp_server(name: str) -> list[FileSpec]:
    p = _pkg(name)
    files = [
        FileSpec("pyproject.toml", _pyproject(name, 'Tools API', ['fastapi>=0.110', 'uvicorn[standard]>=0.27'])),
        FileSpec(".gitignore", _gitignore()),
        _readme(name, f"```bash\npip install -e .\n```"),
        FileSpec(f"src/{p}/__init__.py", _init()),
        FileSpec(f"src/{p}/main.py", "from fastapi import FastAPI\napp = FastAPI()\n@app.get('/tools')\ndef tools():\n    return {'tools': ['echo']}\n"),
    ]
    files.extend(_tests_smoke(p))
    return files

def tpl_streamlit(name: str) -> list[FileSpec]:
    p = _pkg(name)
    files = [
        FileSpec("pyproject.toml", _pyproject(name, 'Streamlit app', ['streamlit>=1.32'])),
        FileSpec(".gitignore", _gitignore()),
        _readme(name, f"```bash\npip install -e .\n```"),
        FileSpec(f"src/{p}/__init__.py", _init()),
        FileSpec(f"src/{p}/app.py", "import streamlit as st\nst.title('App')\nst.write('OpenComb streamlit starter')\n"),
    ]
    files.extend(_tests_smoke(p))
    return files
