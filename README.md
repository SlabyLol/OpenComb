# OpenComb

**Everything developers need** – combine, merge, packages, project tools, checks & more.

[![PyPI](https://img.shields.io/pypi/v/opencomb.svg)](https://pypi.org/project/opencomb/)
[![CI](https://github.com/SlabyLol/OpenComb/actions/workflows/ci.yml/badge.svg)](https://github.com/SlabyLol/OpenComb/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

<p align="center"><img src="docs/logo.svg" alt="OpenComb" width="140"/></p>

## Install

```bash
pip install opencomb
pip install "opencomb[format]"   # optional ruff + black
```

## What you get (v0.5.0)

| Area | Commands | Why devs need it |
|------|----------|------------------|
| **Code** | `combine` | Merge modules + remote URLs + format |
| **Config** | `merge` | Deep-merge YAML/JSON/TOML |
| **Env** | `env` | Merge `.env` + export scripts |
| **Combinatorial** | `generate` | Test matrices, pairwise, HTML reports |
| **Prompts** | `prompt` | Structured LLM prompts |
| **Templates** | `template` | Jinja2 rendering |
| **Recipes** | `recipe` | Full pipelines (incl. package install) |
| **Packages** | `pak add/list/info/...` | Install & inspect from PyPI |
| **Project** | `init` `tree` `bump` `ignore` | Scaffold, version, gitignore |
| **Quality** | `check` `format` `doctor` | ruff + pytest gate |

## Quick start

```bash
# New project in seconds
opencomb init my-app -d "My cool app"
cd my-app

# Add deps
opencomb pak add requests rich

# Quality gate
opencomb check

# Version bump
opencomb bump patch

# Combine / generate / recipe
opencomb combine src/**/*.py -o build/all.py --format
opencomb generate -p params.yaml --method pairwise --html
opencomb recipe recipes/dev.yaml
```

## Package helper (oc-pak)

```bash
opencomb pak add httpx "pydantic>=2"
opencomb pak info httpx
opencomb pak list
opencomb pak freeze -o requirements.txt
```

## Library

```python
from opencomb import (
    ProjectHelper, PackageManager, Checker,
    CodeCombiner, CombinatorialGenerator, RecipeRunner,
)

ProjectHelper().init("demo", description="Demo app")
PackageManager().add(["requests"])
Checker().run_all()
```

## Publish

```bash
git tag v0.5.0 && git push origin v0.5.0
# Create GitHub Release → publish.yml uploads to PyPI
```

**Repo:** https://github.com/SlabyLol/OpenComb  
MIT © DarkFox Co.
