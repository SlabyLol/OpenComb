# OpenComb

**Developer Swiss Army Knife** – combine, build, drill, PRT language, **56+ templates**, **PyRunner**, stacks, wizard, OCC SSH, **Problem Scanner**, **Zombie toolkit** (62 commands), and a full **Python API**.

[![PyPI](https://img.shields.io/pypi/v/opencomb.svg)](https://pypi.org/project/opencomb/)
[![CI](https://github.com/SlabyLol/OpenComb/actions/workflows/ci.yml/badge.svg)](https://github.com/SlabyLol/OpenComb/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

<p align="center">
  <img src="https://raw.githubusercontent.com/SlabyLol/OpenComb/main/docs/logo.svg" alt="OpenComb Logo" width="160"/>
</p>

```bash
pip install opencomb
```

## Highlights (v0.19.0)

| Area | CLI | Python API |
|------|-----|------------|
| **Zombie toolkit** | `zombie run-check` · `shoot` · `scan` · `help-all` (62 cmds) | `run_zombie_check()` · `shoot_folder()` |
| **Problem Scanner** | `problemscanner` (GUI) · `--cli` | `run_scan()` · `launch_gui()` |
| **Templates** | `templates` · `new` | `list_templates()` · `apply_template()` · `new_project()` |
| **Wizard / Stacks** | `wizard` · `stacks` · `stack` · `add` | `run_wizard()` · `apply_stack()` · `add_component()` |
| **Code / Config** | `combine` · `merge` · `env` | `combine()` · `merge_configs()` · `merge_env()` |
| **Combos / Prompts** | `generate` · `prompt` · `template` | `generate_combos()` · `build_prompt()` · `render_template()` |
| **Project** | `init` · `tree` · `bump` · `doctor` | `ProjectHelper` · `doctor()` |
| **Packages** | `pak add` … | `PackageManager` |
| **SSH** | `occ` | `SSHTarget` · `occ_connect()` |
| **Build / Drill** | `build` · `drill` | `interactive_build()` · `start_drill()` |
| **Codec** | `codec encode` · `decode` | `encode()` · `decode()` · `encode_file()` |

Full API docs: **[docs/API.md](docs/API.md)**

---

## Zombie toolkit (NEW)

62 subcommands for system health, zombies, and cleanup:

```bash
# Full detail run-check (shows everything every round)
opencomb zombie run-check
opencomb zombie run-check --once
opencomb zombie run-check --rounds 10 --interval 2

# List zombies / parents
opencomb zombie list
opencomb zombie parents

# Clear all files inside a folder (confirmation required)
opencomb zombie shoot ~/Downloads --dry-run
opencomb zombie shoot ~/Downloads          # type path to confirm
opencomb zombie shoot ~/Downloads --yes    # skip prompt

# Full problem scan + GUI
opencomb zombie scan
opencomb zombie gui
opencomb problemscanner              # same GUI
opencomb problemscanner --cli

# Quick checks
opencomb zombie status
opencomb zombie mem
opencomb zombie disk
opencomb zombie cpu
opencomb zombie docker
opencomb zombie help-all             # list all 62 commands
```

### Problem Scanner checks (19)

System load · Memory · Swap · Disk / inodes · Temp & cache · Large logs · Top processes · **Zombie processes** · Duplicate processes · Developer clutter · Network / DNS · Listening ports · Failed services · Security · Python env · Docker · Broken symlinks · Uptime · OOM hints

---

## Codec (custom encoder / decoder)

OpenComb ships its own payload codec (magic `OC01` + zlib + base64):

```bash
# Encode any file
opencomb codec encode mycode.py          # → mycode.py.oc
opencomb codec encode mycode.py -o out.oc

# Decode
opencomb codec decode mycode.py.oc       # → mycode.py
opencomb codec decode out.oc -o restored.py
```

```python
from opencomb import encode, decode, encode_file, decode_file

payload = encode("print('hi')")
original = decode(payload).decode()
encode_file("script.py")
decode_file("script.py.oc")
```

Used internally by the Zombie & Problem Scanner loaders for compact, verifiable payloads.

---

## Python API – quick start

```python
import opencomb

print(opencomb.__version__)

# Combine / merge
code = opencomb.combine(["a.py", "b.py"])
cfg = opencomb.merge_configs(["base.yaml", "local.yaml"])

# Combinatorial sets
rows = opencomb.generate_combos(
    {"lr": [0.001, 0.01], "batch": [16, 32]},
    method="pairwise",
)

# Scaffold
path = opencomb.new_project("my-api", template="fastapi")

# Problem scanner
from opencomb.problem_scanner import run_scan, run_zombie_check, shoot_folder
report = run_scan()
zombies = run_zombie_check()
# shoot_folder(Path("/tmp/junk"), yes=True, dry_run=True)
```

### Main classes

```python
from opencomb import (
    CodeCombiner, ConfigMerger, EnvMerger,
    CombinatorialGenerator, PromptCombiner, TemplateRenderer,
    RecipeRunner, PackageManager, ProjectHelper, Checker,
    list_templates, apply_template, apply_stack, add_component,
)
```

See **[docs/API.md](docs/API.md)** for every function and return type.

---

## CLI quick start

```bash
# Templates
opencomb templates
opencomb new fastapi my-api

# Wizard / stacks
opencomb wizard
opencomb stack api-full ./my-full-api
opencomb add dockerfile .

# Zombie / scanner
opencomb zombie run-check --once
opencomb zombie shoot ./tmp-build --dry-run
opencomb problemscanner --cli

# Codec
opencomb codec encode file.py
opencomb codec decode file.py.oc

# SSH
opencomb occ user@example.com

# Packages
opencomb pak add requests
```

### PyRunner

Run Python **in the browser** (Pyodide). Packages via `packages.json` only.

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
opencomb prt
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
