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


def tpl_dockerfile_only(name: str) -> list[FileSpec]:
    p = _pkg(name)
    files = [
        FileSpec("pyproject.toml", _pyproject(name, 'Dockerfile only', [])),
        FileSpec(".gitignore", _gitignore()),
        _readme(name, f"```bash\npip install -e .\n```"),
        FileSpec(f"src/{p}/__init__.py", _init()),
        FileSpec("Dockerfile", "FROM python:3.12-slim\nWORKDIR /app\nCOPY . .\nRUN pip install .\nCMD [\"python\", \"-m\", \"%s\"]\n" % p),
    ]
    files.extend(_tests_smoke(p))
    return files

def tpl_compose_stack(name: str) -> list[FileSpec]:
    p = _pkg(name)
    files = [
        FileSpec("pyproject.toml", _pyproject(name, 'Docker Compose', [])),
        FileSpec(".gitignore", _gitignore()),
        _readme(name, f"```bash\npip install -e .\n```"),
        FileSpec(f"src/{p}/__init__.py", _init()),
        FileSpec("docker-compose.yml", "services:\n  app:\n    build: .\n    ports: [\"8000:8000\"]\n"),
    ]
    files.extend(_tests_smoke(p))
    return files

def tpl_github_release(name: str) -> list[FileSpec]:
    p = _pkg(name)
    files = [
        FileSpec("pyproject.toml", _pyproject(name, 'GitHub release workflow', [])),
        FileSpec(".gitignore", _gitignore()),
        _readme(name, f"```bash\npip install -e .\n```"),
        FileSpec(f"src/{p}/__init__.py", _init()),
        FileSpec(".github/workflows/release.yml", "name: Release\non:\n  push:\n    tags: ['v*']\njobs:\n  build:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v4\n      - run: pip install build && python -m build\n"),
    ]
    files.extend(_tests_smoke(p))
    return files

def tpl_json_schema(name: str) -> list[FileSpec]:
    p = _pkg(name)
    files = [
        FileSpec("pyproject.toml", _pyproject(name, 'JSON Schema', [])),
        FileSpec(".gitignore", _gitignore()),
        _readme(name, f"```bash\npip install -e .\n```"),
        FileSpec(f"src/{p}/__init__.py", _init()),
        FileSpec("schema.json", "{\"$schema\": \"http://json-schema.org/draft-07/schema#\", \"type\": \"object\"}\n"),
    ]
    files.extend(_tests_smoke(p))
    return files

def tpl_cli_config_yaml(name: str) -> list[FileSpec]:
    p = _pkg(name)
    files = [
        FileSpec("pyproject.toml", _pyproject(name, 'CLI + YAML config', ['pyyaml>=6.0', 'typer>=0.12'])),
        FileSpec(".gitignore", _gitignore()),
        _readme(name, f"```bash\npip install -e .\n```"),
        FileSpec(f"src/{p}/__init__.py", _init()),
        FileSpec("config.yaml", "app:\n  name: %s\n" % name),
        FileSpec(f"src/{p}/cli.py", "import yaml, typer\napp = typer.Typer()\n@app.command()\ndef show():\n    print(yaml.safe_load(open('config.yaml')))\n"),
    ]
    files.extend(_tests_smoke(p))
    return files

def tpl_http_server_stdlib(name: str) -> list[FileSpec]:
    p = _pkg(name)
    files = [
        FileSpec("pyproject.toml", _pyproject(name, 'stdlib HTTP server', [])),
        FileSpec(".gitignore", _gitignore()),
        _readme(name, f"```bash\npip install -e .\n```"),
        FileSpec(f"src/{p}/__init__.py", _init()),
        FileSpec(f"src/{p}/server.py", "from http.server import HTTPServer, SimpleHTTPRequestHandler\ndef main():\n    HTTPServer(('', 8000), SimpleHTTPRequestHandler).serve_forever()\n\nif __name__ == '__main__':\n    main()\n"),
    ]
    files.extend(_tests_smoke(p))
    return files

def tpl_rich_dashboard(name: str) -> list[FileSpec]:
    p = _pkg(name)
    files = [
        FileSpec("pyproject.toml", _pyproject(name, 'Rich dashboard', ['rich>=13'])),
        FileSpec(".gitignore", _gitignore()),
        _readme(name, f"```bash\npip install -e .\n```"),
        FileSpec(f"src/{p}/__init__.py", _init()),
        FileSpec(f"src/{p}/dash.py", "from rich.console import Console\nfrom rich.table import Table\ndef main():\n    t = Table(title='Dashboard')\n    t.add_column('Metric')\n    t.add_row('ok')\n    Console().print(t)\n\nif __name__ == '__main__':\n    main()\n"),
    ]
    files.extend(_tests_smoke(p))
    return files

def tpl_pyrunner(name: str) -> list[FileSpec]:
    p = _pkg(name)
    files = [
        FileSpec("pyproject.toml", _pyproject(name, 'PyRunner (browser Python)', [])),
        FileSpec(".gitignore", _gitignore()),
        _readme(name, f"```bash\npip install -e .\n```"),
        FileSpec(f"src/{p}/__init__.py", _init()),
        FileSpec("index.html", "<!doctype html><script src=\"https://cdn.jsdelivr.net/pyodide/v0.26.2/full/pyodide.js\"></script><script>async function main(){const pyodide=await loadPyodide();console.log(pyodide.runPython('1+1'));}main()</script>\n"),
        FileSpec("README.md", f"# {name}\n\nPyRunner: run Python in the browser via Pyodide.\n"),
    ]
    files.extend(_tests_smoke(p))
    return files
