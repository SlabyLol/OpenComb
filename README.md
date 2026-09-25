# OpenComb

**Developer Swiss Army Knife** – combine, build, drill, PRT language, **56+ templates**, **PyRunner**, stacks, wizard, OCC SSH, **Problem Scanner**, **Zombie toolkit** (62 commands), **custom commands**, and a full **Python API**.

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
| **Custom commands** | `add` · `add --list` · `add --del` | `add_command()` · `run_command()` |
| **Codec** | `codec encode` · `decode` | `encode()` · `decode()` · `encode_file()` |
| **Templates** | `templates` · `new` | `list_templates()` · `apply_template()` · `new_project()` |
| **Code / Config** | `combine` · `merge` · `env` | `combine()` · `merge_configs()` · `merge_env()` |
| **Project** | `init` · `tree` · `bump` · `doctor` | `ProjectHelper` · `doctor()` |
| **Packages** | `pak add` … | `PackageManager` |
| **SSH** | `occ` | `SSHTarget` · `occ_connect()` |

---

## Custom commands (`opencomb add`)

Register your own scripts as first-class OpenComb commands:

```bash
# Add a command (python / bash / node / any runner)
opencomb add mycommand python hello.py
opencomb add greet bash ./greet.sh

# Run it
opencomb mycommand
opencomb mycommand -- extra args

# List / delete (only user commands – built-ins are protected)
opencomb add --list
opencomb add --del mycommand
```

Stored in `~/.opencomb/user_commands.json`.

---

## Zombie toolkit

```bash
opencomb zombie run-check --once
opencomb zombie shoot ~/Downloads --dry-run
opencomb zombie help-all
```

## Codec

```bash
opencomb codec encode mycode.py
opencomb codec decode mycode.py.oc
```

```python
from opencomb import encode, decode
payload = encode("print('hi')")
print(decode(payload).decode())
```

---

## CLI quick start

```bash
opencomb templates
opencomb new fastapi my-api
opencomb add mycommand python hello.py
opencomb zombie run-check --once
opencomb codec encode file.py
opencomb pak add requests
opencomb occ user@example.com
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
