# OpenComb

**Developer Swiss Army Knife** – combine, build, drill, PRT language, **56+ templates**, **PyRunner**, and more.

[![PyPI](https://img.shields.io/pypi/v/opencomb.svg)](https://pypi.org/project/opencomb/)
[![CI](https://github.com/SlabyLol/OpenComb/actions/workflows/ci.yml/badge.svg)](https://github.com/SlabyLol/OpenComb/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

<p align="center">
  <img src="https://raw.githubusercontent.com/SlabyLol/OpenComb/main/docs/logo.svg" alt="OpenComb Logo" width="160"/>
</p>

```bash
pip install opencomb
```

## Highlights (v0.13.0)

| Area | Commands |
|------|----------|
| **Templates** | `templates` · `new` – 56+ scaffolds |
| **PyRunner** | `new pyrunner` – Python in the browser (Pyodide), packages via JSON only |
| **PRT** | `prt` · `run` |
| **Build / Drill** | `build` · `drill` |
| **Clone / Site** | `clone` · `site` |
| **DevOps** | `git` · `secrets` · `http` · `bench` · `jq` · `ports` |
| **Power** | `search` · `todos` · `stats` · `diff` · `hash` · `outdated` · `serve` · `watch` |
| **Packages** | `pak …` |
| **Code / Config** | `combine` · `merge` · `env` · `generate` · `recipe` |

## PyRunner

Run Python **online in the browser** (Pyodide). Package list is **only** `packages.json` – **no GUI**.

```bash
opencomb new pyrunner my-runner
cd my-runner
python -m http.server 8080
# edit packages.json, reload page
```

## Templates

```bash
opencomb templates
opencomb new
opencomb new fastapi my-api
opencomb new pyrunner web-py
```

## Quick start

```bash
opencomb init my-app
opencomb pak add requests
opencomb build
opencomb drill .
opencomb prt -e 'print(1+2)'
opencomb clone https://github.com/user/repo.git
opencomb site https://example.com -o mirror
```

## Links

- PyPI: https://pypi.org/project/opencomb/
- Repo: https://github.com/SlabyLol/OpenComb

MIT © DarkFox Co.
