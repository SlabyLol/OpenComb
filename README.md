# OpenComb

**Developer Swiss Army Knife** – combine, build, search, packages, and a full **`.prt` programming language**.

[![PyPI](https://img.shields.io/pypi/v/opencomb.svg)](https://pypi.org/project/opencomb/)
[![Python](https://img.shields.io/pypi/pyversions/opencomb.svg)](https://pypi.org/project/opencomb/)
[![CI](https://github.com/SlabyLol/OpenComb/actions/workflows/ci.yml/badge.svg)](https://github.com/SlabyLol/OpenComb/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

<p align="center">
  <img src="docs/logo.svg" alt="OpenComb Logo" width="160"/>
</p>

```bash
pip install opencomb
# optional formatters
pip install "opencomb[format]"
```

---

## Features (v0.9.0)

| Area | Commands | Description |
|------|----------|-------------|
| **PRT language** | `prt` · `run` | Own `.prt` language + REPL |
| **Build** | `build` | Interactive menu, 20 targets, terminal animations |
| **Drill** | `drill` | Interactive shell locked to one directory (bright red) |
| **Code** | `combine` · `format` | Merge Python files (local + URLs), format |
| **Config** | `merge` · `env` | YAML/JSON/TOML deep-merge, `.env` + export |
| **Generate** | `generate` | Cartesian / pairwise / sample + HTML reports |
| **AI** | `prompt` · `template` | LLM prompts, Jinja2 |
| **Recipes** | `recipe` | Declarative pipelines |
| **Packages** | `pak add/list/info/…` | Install & inspect from PyPI (oc-pak) |
| **Project** | `init` · `tree` · `bump` · `ignore` | Scaffold, tree, version bump, gitignore |
| **Quality** | `check` · `doctor` | ruff + pytest gate |
| **Power** | `search` · `todos` · `stats` · `diff` · `hash` · `outdated` · `serve` · `watch` | Search, TODOs, LOC, diff, checksums, outdated deps, HTTP serve, file watch |

---

## Quick start

```bash
# Scaffold a project
opencomb init my-app -d "My cool app"
cd my-app

# Packages
opencomb pak add requests rich

# Quality
opencomb check
opencomb bump patch

# Interactive build (animations + menu)
opencomb build
opencomb build wheel sdist
opencomb build --list

# Drill into a directory
opencomb drill .

# PRT language
opencomb prt examples/prt/hello.prt
opencomb prt                          # REPL
opencomb prt -e 'print(2 + 3)'
```

---

## OpenComb PRT (`.prt`)

OpenComb ships its **own programming language** with files ending in **`.prt`**.

### Run

```bash
opencomb prt script.prt
opencomb run script.prt
opencomb prt -e 'print("hello", 1+2)'
opencomb prt                  # interactive REPL
```

### Example

```prt
# hello.prt
let name = "OpenComb"
print("Hello from", name, "!")

fn add(a, b) {
    return a + b
}
print("2+3 =", add(2, 3))

var sum = 0
for n in [1, 2, 3, 4, 5] {
    sum += n
}
print("sum =", sum)

if sum > 10 {
    print("big")
} else {
    print("small")
}

write("out.txt", "saved by PRT")
# Call OpenComb from PRT:
# oc("stats", ".")
```

### Language highlights

- Variables: `let`, `var`
- Types: numbers, strings, bools, `null`, lists, dicts
- Control: `if` / `elif` / `else`, `while`, `for … in`, `break`, `continue`
- Functions: `fn name(args) { … return x }`
- Operators: `+ - * / % == != < > <= >= and or not += -= *= /=`
- Builtins: `print`, `len`, `str`, `int`, `read`, `write`, `shell`, `range`, `listdir`, `exists`, `cwd`, `oc` / `opencomb`, …

See `examples/prt/`.

---

## Build system

```bash
opencomb build              # interactive menu + animations
opencomb build --list       # list all targets
opencomb build wheel sdist  # non-interactive
opencomb build release      # clean → format → check → package
```

**Targets include:** `wheel`, `sdist`, `package`, `editable`, `install`, `clean`, `format`, `check`, `test`, `typecheck`, `coverage`, `docs`, `docker`, `reqs`, `lock`, `release`, `ci`, `tree`, `stats`, `combine`.

---

## Drill mode

Lock the terminal to one project directory (bright-red UI):

```bash
opencomb drill path/to/project
opencomb drill .
```

Inside drill:

```text
opencomb:.> ls
opencomb:.> cd src
opencomb:src> pak add httpx
opencomb:src> combine a.py b.py -o out.py
opencomb:src> status
opencomb:src> exit
```

---

## Packages (oc-pak)

```bash
opencomb pak add requests "httpx>=0.27"
opencomb pak list
opencomb pak show requests
opencomb pak info httpx
opencomb pak freeze -o requirements.txt
opencomb pak remove some-package
```

---

## Power tools

```bash
opencomb search "TODO" .
opencomb search -E "def \\w+" src/
opencomb todos .
opencomb stats .
opencomb diff a.py b.py
opencomb hash src/ --tree
opencomb outdated
opencomb serve . -p 8765 --open report.html
opencomb watch src/ -r "pytest -q"
opencomb watch . --recipe recipes/dev.yaml
```

---

## Combine, merge, generate

```bash
opencomb combine a.py b.py https://example.com/c.py -o out.py --format
opencomb merge base.yaml prod.yaml -o final.yaml
opencomb env .env .env.local --export -o load.sh
opencomb generate -p params.yaml --method pairwise --html
opencomb prompt -s system.txt -i task.txt -o prompt.txt
opencomb template page.j2 -d data.yaml -o out.html
opencomb recipe pipeline.yaml
```

---

## Library usage

```python
from opencomb import (
    CodeCombiner,
    ConfigMerger,
    CombinatorialGenerator,
    PackageManager,
    ProjectHelper,
    Checker,
    RecipeRunner,
)
from opencomb.prt import run_source, run_file, start_repl

# PRT
run_source('print("hi", 1+2)')
run_file("script.prt")

# Project
ProjectHelper().init("demo", description="Demo")

# Packages
PackageManager().add(["requests"])

# Checks
Checker().run_all()
```

---

## Project layout (this repo)

```text
src/opencomb/
  cli.py           # CLI entry
  prt/             # .prt language (lexer, parser, interpreter, REPL)
  builder.py       # interactive build
  drill.py         # drill shell
  combiner.py      # code combine
  tools.py         # search, todos, stats, …
  …
examples/prt/      # PRT samples
.github/workflows/ # CI + PyPI publish
```

---

## Publishing

```bash
git tag v0.9.0
git push origin v0.9.0
# Create a GitHub Release → publish.yml uploads to PyPI (Trusted Publishing)
```

---

## Links

- **PyPI:** https://pypi.org/project/opencomb/
- **Repo:** https://github.com/SlabyLol/OpenComb
- **Issues:** https://github.com/SlabyLol/OpenComb/issues

MIT © DarkFox Co.
