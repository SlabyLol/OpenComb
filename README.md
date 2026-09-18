# OpenComb

**Developer Swiss Army Knife** – combine, build, search, packages, and a full **`.prt` programming language**.

[![PyPI](https://img.shields.io/pypi/v/opencomb.svg)](https://pypi.org/project/opencomb/)
[![Python](https://img.shields.io/pypi/pyversions/opencomb.svg)](https://pypi.org/project/opencomb/)
[![CI](https://github.com/SlabyLol/OpenComb/actions/workflows/ci.yml/badge.svg)](https://github.com/SlabyLol/OpenComb/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

<p align="center">
  <img src="https://raw.githubusercontent.com/SlabyLol/OpenComb/main/docs/logo.svg" alt="OpenComb Logo" width="160"/>
</p>

```bash
pip install opencomb
pip install "opencomb[format]"
```

## Features (v0.10.0)

| Area | Commands | Description |
|------|----------|-------------|
| **PRT** | `prt` · `run` | Own `.prt` language + REPL |
| **Build** | `build` | Interactive menu, 20 targets, animations |
| **Drill** | `drill` | Shell locked to one directory |
| **Code / Config** | `combine` · `format` · `merge` · `env` | Merge code/configs/env |
| **Generate** | `generate` · `prompt` · `template` · `recipe` | Matrices, LLM prompts, Jinja2, pipelines |
| **Packages** | `pak …` | Install/inspect from PyPI |
| **Project** | `init` · `tree` · `bump` · `ignore` · `check` | Scaffold & quality |
| **Power** | `search` · `todos` · `stats` · `diff` · `hash` · `outdated` · `serve` · `watch` | Everyday tools |
| **DevOps** | `git` · `secrets` · `http` · `bench` · `jq` · `ports` | Git, secret scan, HTTP, bench, JSON/YAML, ports |

## Quick start

```bash
opencomb init my-app && cd my-app
opencomb pak add requests
opencomb build
opencomb drill .
opencomb prt -e 'print(2+3)'
opencomb git
opencomb secrets .
opencomb ports --ports 3000,8000
```

## PRT language

```bash
opencomb prt script.prt
opencomb prt -e 'print("hi", 1+2)'
opencomb prt   # REPL
```

```prt
fn add(a, b) { return a + b }
print(add(2, 3))
write("out.txt", "from PRT")
```

## DevOps helpers

```bash
opencomb git
opencomb secrets .
opencomb http https://httpbin.org/json
opencomb bench "python -c 'print(42)'" -n 5
opencomb jq config.yaml database.host
opencomb ports --ports 80,443,8000
```

## Links

- PyPI: https://pypi.org/project/opencomb/
- Repo: https://github.com/SlabyLol/OpenComb

MIT © DarkFox Co.
