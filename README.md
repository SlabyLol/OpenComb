# OpenComb

**Developer Swiss Army Knife** – combine, build, drill, PRT language, **56+ templates**, **PyRunner**, stacks, wizard, OCC SSH, and a full **Python API**.

[![PyPI](https://img.shields.io/pypi/v/opencomb.svg)](https://pypi.org/project/opencomb/)
[![CI](https://github.com/SlabyLol/OpenComb/actions/workflows/ci.yml/badge.svg)](https://github.com/SlabyLol/OpenComb/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

<p align="center">
  <img src="https://raw.githubusercontent.com/SlabyLol/OpenComb/main/docs/logo.svg" alt="OpenComb Logo" width="160"/>
</p>

```bash
pip install opencomb
```

## Highlights (v0.17.0)

| Area | CLI | Python API |
|------|-----|------------|
| **Templates** | `templates` · `new` | `list_templates()` · `apply_template()` · `new_project()` |
| **Wizard / Stacks** | `wizard` · `stacks` · `stack` · `add` | `run_wizard()` · `apply_stack()` · `add_component()` |
| **Code / Config** | `combine` · `merge` · `env` | `combine()` · `merge_configs()` · `merge_env()` |
| **Combos / Prompts** | `generate` · `prompt` · `template` | `generate_combos()` · `build_prompt()` · `render_template()` |
| **Project** | `init` · `tree` · `bump` · `syscheck` | `ProjectHelper` · `doctor()` |
| **Packages** | `pak add` … | `PackageManager` |
| **Search / Stats** | `search` · `todos` · `stats` | `search()` · `todos()` · `stats()` |
| **SSH** | `occ` | `SSHTarget` · `occ_connect()` |
| **Build / Drill** | `build` · `drill` | `interactive_build()` · `start_drill()` |

Full API docs: **[docs/API.md](docs/API.md)**

---

## Python API – quick start

```python
import opencomb

# Version
print(opencomb.__version__)

# Combine Python sources
code = opencomb.combine(["a.py", "b.py"])
code = opencomb.combine(snippets=["x = 1", "print(x)"])

# Merge configs / env
cfg = opencomb.merge_configs(["base.yaml", "local.yaml"])
env = opencomb.merge_env([".env", ".env.local"])

# Combinatorial parameter sets
rows = opencomb.generate_combos(
    {"lr": [0.001, 0.01], "batch": [16, 32]},
    method="pairwise",
)

# Jinja2 + prompts
html = opencomb.render_template("Hi {{ name }}!", data={"name": "Ada"})
prompt = opencomb.build_prompt(
    system="You are a code reviewer.",
    user="Review this PR.",
)

# Scaffold a project
path = opencomb.new_project("my-api", template="fastapi")

# Search / TODOs / stats / doctor
hits = opencomb.search("TODO", ".", regex=False)
items = opencomb.todos(".")
st = opencomb.stats(".")
report = opencomb.doctor(".")
print(report["score"], report["grade"])
```

### Main classes

```python
from opencomb import (
    CodeCombiner, ConfigMerger, EnvMerger,
    CombinatorialGenerator, PromptCombiner, TemplateRenderer,
    RecipeRunner, PackageManager, ProjectHelper, Checker,
    Searcher, TodoExtractor, ProjectStats,
    list_templates, apply_template, apply_stack, add_component,
)

# Example: class usage
text = CodeCombiner().combine_files(["src/a.py", "src/b.py"])
data = ConfigMerger().merge_files(["cfg/base.yaml", "cfg/prod.yaml"])
PackageManager().add(["requests"])
ProjectHelper().init("demo", description="Demo package")
```

See **[docs/API.md](docs/API.md)** for every function, method, and return type.

---

## CLI quick start

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

# Add a component
opencomb add dockerfile .
opencomb add makefile .

# Project doctor
opencomb syscheck

# SSH connector
opencomb occ user@example.com
```

### PyRunner

Run Python **in the browser** (Pyodide). Packages only via `packages.json` (no GUI).

```bash
opencomb new pyrunner my-runner
cd my-runner && python -m http.server 8080
```

### Stacks

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

### Components

`dockerfile` · `makefile` · `precommit` · `devcontainer` · `gitignore` · `compose` · `pytest` · `github-ci` · `readme`

### PRT language

```bash
opencomb prt                  # REPL
opencomb prt examples/prt/hello.prt
```

---

## Development

```bash
git clone https://github.com/SlabyLol/OpenComb.git
cd OpenComb
pip install -e ".[dev]"
pytest
```

## License

MIT © DarkFox Co.
