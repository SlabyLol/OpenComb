# OpenComb

**Developer Swiss Army Knife** – combine, build, drill, PRT language, **56+ templates**, **PyRunner**, stacks, wizard, OCC SSH, and more.

[![PyPI](https://img.shields.io/pypi/v/opencomb.svg)](https://pypi.org/project/opencomb/)
[![CI](https://github.com/SlabyLol/OpenComb/actions/workflows/ci.yml/badge.svg)](https://github.com/SlabyLol/OpenComb/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

<p align="center">
  <img src="https://raw.githubusercontent.com/SlabyLol/OpenComb/main/docs/logo.svg" alt="OpenComb Logo" width="160"/>
</p>

```bash
pip install opencomb
```

## Highlights (v0.16.0)

| Area | Commands |
|------|----------|
| **Templates** | `templates` · `new` – **56 full scaffolds** (FastAPI, CLI, ML, Discord, PyRunner, …) |
| **Wizard / Stacks** | `wizard` · `stacks` · `stack` · `add` · `components` |
| **PyRunner** | `new pyrunner` – Python in the browser (Pyodide), packages via `packages.json` only |
| **PRT** | `prt` – own lightweight language + REPL |
| **Build / Drill** | `build` (animated) · `drill` |
| **SSH Connect** | `occ` – interactive `user@host` connector with profiles |
| **Clone / Site** | `clone` · `site` |
| **DevOps** | `search` · `todos` · `stats` · `diff` · `hash` · `outdated` · `serve` · `watch` |
| **Packages** | `pak add` · `remove` · `list` · `show` · `info` · `freeze` |
| **Code / Config** | `combine` · `merge` · `env` · `generate` · `recipe` · `format` |
| **Project** | `init` · `tree` · `bump` · `check` · `syscheck` · `structure` · `ignore` |

## Quick start

```bash
# List all 56 templates
opencomb templates

# Create a FastAPI project
opencomb new fastapi my-api
cd my-api && pip install -e .

# Interactive wizard (stacks)
opencomb wizard

# Apply a full stack
opencomb stack api-full ./my-full-api

# Add a component to existing project
opencomb add dockerfile .
opencomb add makefile .

# Project doctor
opencomb syscheck

# SSH connector
opencomb occ user@example.com
# or profile
opencomb occ --profile prod
```

## PyRunner

Run Python **online in the browser** (Pyodide). Package list is **only** `packages.json` – **no GUI**.

```bash
opencomb new pyrunner my-runner
cd my-runner
python -m http.server 8080
# edit packages.json, reload page
```

## Stacks

| Stack | Description |
|-------|-------------|
| `api-full` | FastAPI + JWT + SQLModel + Docker + CI |
| `cli-pro` | Typer + Rich + YAML config + tests |
| `ml-api` | ML model serving API |
| `web-full` | Streamlit + FastAPI |
| `discord-bot` | Discord bot + worker |
| `library` | Publishable library + docs + CI |
| `data-science` | Notebooks + Polars + Streamlit |
| `monorepo` | Multi-package layout |
| `minimal` | Bare package |
| `pyrunner` | Browser Python runner |

## Components

`dockerfile` · `makefile` · `precommit` · `devcontainer` · `gitignore` · `compose` · `pytest` · `github-ci` · `readme`

## PRT language

```bash
opencomb prt                  # REPL
opencomb prt examples/prt/hello.prt
```

## Development

```bash
git clone https://github.com/SlabyLol/OpenComb.git
cd OpenComb
pip install -e ".[dev]"
pytest
```

## License

MIT © DarkFox Co.
