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


def tpl_minimal(name: str) -> list[FileSpec]:
    p = _pkg(name)
    files = [
        FileSpec("pyproject.toml", _pyproject(name, 'Minimal installable package', [])),
        FileSpec(".gitignore", _gitignore()),
        _readme(name, f"```bash\npip install -e .\n```"),
        FileSpec(f"src/{p}/__init__.py", _init()),
        FileSpec(f"src/{p}/__main__.py", f"from {p} import __version__\nprint({name!r}, __version__)\n"),
        FileSpec(f"src/{p}/core.py", "def greet(who='world'):\n    return f'Hello, {who}!'\n"),
    ]
    files.extend(_tests_smoke(p))
    return files

def tpl_cli(name: str) -> list[FileSpec]:
    p = _pkg(name)
    files = [
        FileSpec("pyproject.toml", _pyproject(name, 'Typer CLI', ['typer>=0.12'])),
        FileSpec(".gitignore", _gitignore()),
        _readme(name, f"```bash\npip install -e .\n```"),
        FileSpec(f"src/{p}/__init__.py", _init()),
        FileSpec(f"src/{p}/cli.py", f"import typer\napp = typer.Typer()\n@app.command()\ndef hello(name: str = 'world'):\n    print(f'Hello {{name}}')\n\nif __name__ == '__main__':\n    app()\n"),
    ]
    files.extend(_tests_smoke(p))
    return files

def tpl_fastapi(name: str) -> list[FileSpec]:
    p = _pkg(name)
    files = [
        FileSpec("pyproject.toml", _pyproject(name, 'FastAPI app', ['fastapi>=0.110', 'uvicorn[standard]>=0.27'])),
        FileSpec(".gitignore", _gitignore()),
        _readme(name, f"```bash\npip install -e .\n```"),
        FileSpec(f"src/{p}/__init__.py", _init()),
        FileSpec(f"src/{p}/main.py", f"from fastapi import FastAPI\napp = FastAPI(title={name!r})\n@app.get('/health')\ndef health():\n    return {{'ok': True}}\n"),
    ]
    files.extend(_tests_smoke(p))
    return files

def tpl_flask(name: str) -> list[FileSpec]:
    p = _pkg(name)
    files = [
        FileSpec("pyproject.toml", _pyproject(name, 'Flask app', ['flask>=3.0'])),
        FileSpec(".gitignore", _gitignore()),
        _readme(name, f"```bash\npip install -e .\n```"),
        FileSpec(f"src/{p}/__init__.py", _init()),
        FileSpec(f"src/{p}/app.py", f"from flask import Flask\napp = Flask({name!r})\n@app.get('/')\ndef index():\n    return {{'ok': True}}\n"),
    ]
    files.extend(_tests_smoke(p))
    return files

def tpl_discord(name: str) -> list[FileSpec]:
    p = _pkg(name)
    files = [
        FileSpec("pyproject.toml", _pyproject(name, 'Discord bot', ['discord.py>=2.3'])),
        FileSpec(".gitignore", _gitignore()),
        _readme(name, f"```bash\npip install -e .\n```"),
        FileSpec(f"src/{p}/__init__.py", _init()),
        FileSpec(f"src/{p}/bot.py", "import discord\nfrom discord.ext import commands\nbot = commands.Bot(command_prefix='!', intents=discord.Intents.default())\n@bot.event\nasync def on_ready():\n    print('ready', bot.user)\n"),
    ]
    files.extend(_tests_smoke(p))
    return files

def tpl_bot_telegram(name: str) -> list[FileSpec]:
    p = _pkg(name)
    files = [
        FileSpec("pyproject.toml", _pyproject(name, 'Telegram bot', ['python-telegram-bot>=21.0'])),
        FileSpec(".gitignore", _gitignore()),
        _readme(name, f"```bash\npip install -e .\n```"),
        FileSpec(f"src/{p}/__init__.py", _init()),
        FileSpec(f"src/{p}/bot.py", "from telegram.ext import Application\n# set TOKEN via env\ndef main():\n    print('telegram bot starter')\n"),
    ]
    files.extend(_tests_smoke(p))
    return files

def tpl_datascience(name: str) -> list[FileSpec]:
    p = _pkg(name)
    files = [
        FileSpec("pyproject.toml", _pyproject(name, 'Data science', ['pandas>=2.0', 'numpy>=1.26'])),
        FileSpec(".gitignore", _gitignore()),
        _readme(name, f"```bash\npip install -e .\n```"),
        FileSpec(f"src/{p}/__init__.py", _init()),
        FileSpec(f"src/{p}/analysis.py", "import pandas as pd\nimport numpy as np\ndef summary(df: pd.DataFrame) -> dict:\n    return {'rows': len(df), 'cols': list(df.columns)}\n"),
    ]
    files.extend(_tests_smoke(p))
    return files

def tpl_scraper(name: str) -> list[FileSpec]:
    p = _pkg(name)
    files = [
        FileSpec("pyproject.toml", _pyproject(name, 'Web scraper', ['httpx>=0.27', 'beautifulsoup4>=4.12'])),
        FileSpec(".gitignore", _gitignore()),
        _readme(name, f"```bash\npip install -e .\n```"),
        FileSpec(f"src/{p}/__init__.py", _init()),
        FileSpec(f"src/{p}/scrape.py", "import httpx\nfrom bs4 import BeautifulSoup\ndef fetch(url: str) -> str:\n    r = httpx.get(url, timeout=20)\n    r.raise_for_status()\n    return BeautifulSoup(r.text, 'html.parser').get_text(' ', strip=True)[:500]\n"),
    ]
    files.extend(_tests_smoke(p))
    return files

def tpl_ml_api(name: str) -> list[FileSpec]:
    p = _pkg(name)
    files = [
        FileSpec("pyproject.toml", _pyproject(name, 'ML API', ['fastapi>=0.110', 'uvicorn[standard]>=0.27', 'scikit-learn>=1.4'])),
        FileSpec(".gitignore", _gitignore()),
        _readme(name, f"```bash\npip install -e .\n```"),
        FileSpec(f"src/{p}/__init__.py", _init()),
        FileSpec(f"src/{p}/main.py", "from fastapi import FastAPI\napp = FastAPI()\n@app.get('/predict')\ndef predict(x: float = 0.0):\n    return {'y': x * 2}\n"),
    ]
    files.extend(_tests_smoke(p))
    return files

def tpl_worker(name: str) -> list[FileSpec]:
    p = _pkg(name)
    files = [
        FileSpec("pyproject.toml", _pyproject(name, 'Background worker', [])),
        FileSpec(".gitignore", _gitignore()),
        _readme(name, f"```bash\npip install -e .\n```"),
        FileSpec(f"src/{p}/__init__.py", _init()),
        FileSpec(f"src/{p}/worker.py", "import time\ndef run():\n    print('worker tick')\n    time.sleep(1)\n\nif __name__ == '__main__':\n    while True:\n        run()\n"),
    ]
    files.extend(_tests_smoke(p))
    return files
