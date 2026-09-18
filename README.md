# OpenComb

**Smart Combiner + Package Helper for developers**

[![PyPI](https://img.shields.io/pypi/v/opencomb.svg)](https://pypi.org/project/opencomb/)
[![CI](https://github.com/SlabyLol/OpenComb/actions/workflows/ci.yml/badge.svg)](https://github.com/SlabyLol/OpenComb/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

<p align="center">
  <img src="docs/logo.svg" alt="OpenComb Logo" width="160"/>
</p>

**OpenComb** helps you combine code, merge configs, build prompts, run recipes **and** manage packages from PyPI.

### Features (v0.4.0)

| Feature | CLI | Description |
|---------|-----|-------------|
| Code Combining | `combine` | Local + remote URLs, import dedupe, format |
| Config Merging | `merge` | YAML / JSON / TOML deep & shallow |
| Env Merging | `env` | `.env` files + bash export |
| Combinatorial | `generate` | Cartesian / pairwise / sample + constraints + HTML reports |
| Prompts | `prompt` | Structured LLM prompts |
| Templates | `template` | Jinja2 |
| Recipes | `recipe` | Full declarative pipelines |
| **Packages (oc-pak)** | `pak add/remove/list/show/info/freeze` | Install & inspect packages from PyPI |
| Formatting | `format` | ruff / black |
| Doctor | `doctor` | Health check |

## Installation

```bash
pip install opencomb
# or
pip install "opencomb[format]"
```

## Package commands (oc-pak)

```bash
# Install packages from PyPI
opencomb pak add requests rich
opencomb pak add "httpx>=0.27" --upgrade

# List / show / info
opencomb pak list
opencomb pak show requests
opencomb pak info httpx          # latest version & summary from PyPI

# Freeze
opencomb pak freeze -o requirements.txt

# Remove
opencomb pak remove some-package
```

## Other examples

```bash
opencomb combine a.py b.py https://example.com/c.py -o out.py --format
opencomb merge base.yaml prod.yaml -o final.yaml
opencomb env .env .env.local --export -o load.sh
opencomb generate -p params.yaml --method pairwise --html
opencomb recipe my_pipeline.yaml
opencomb doctor
```

## Library

```python
from opencomb import PackageManager, CombinatorialGenerator, CodeCombiner

pm = PackageManager()
pm.add(["requests", "rich"])
info = pm.info_summary("httpx")
print(info["version"], info["summary"])
```

## Publish

```bash
git tag v0.4.0
git push origin v0.4.0
# then create GitHub Release → auto publish via publish.yml
```

**Repo**: https://github.com/SlabyLol/OpenComb  
MIT © DarkFox Co.
