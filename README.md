# OpenComb

**Developer Swiss Army Knife** — **100% plain Python source** (no base64, no obfuscation, no hidden loaders).

Combine, build, drill, PRT language, **56+ templates**, **PyRunner**, stacks, wizard, OCC SSH, **Problem Scanner**, **Zombie toolkit**, **custom commands**, and a full **Python API**.

[![PyPI](https://img.shields.io/pypi/v/opencomb.svg)](https://pypi.org/project/opencomb/)
[![CI](https://github.com/SlabyLol/OpenComb/actions/workflows/ci.yml/badge.svg)](https://github.com/SlabyLol/OpenComb/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

<p align="center">
  <img src="https://raw.githubusercontent.com/SlabyLol/OpenComb/main/docs/logo.svg" alt="OpenComb Logo" width="160"/>
</p>

```bash
pip install opencomb
```

## Transparency

Every module under `src/opencomb/` is normal, readable Python.  
There are **no** compressed payload files, **no** `exec(compile(...))` loaders, **no** base64 blobs in the package.

## Highlights (v0.19.1)

| Area | CLI | Python API |
|------|-----|------------|
| **Zombie toolkit** | `zombie run-check` · `shoot` · `list` · `parents` | `run_zombie_check()` · `shoot_folder()` |
| **Problem Scanner** | `problemscanner` (GUI) · `--cli` | `run_scan()` · `launch_gui()` |
| **Custom commands** | `add` · `add --list` · `add --del` | user command registry |
| **Codec** (optional) | `codec encode` · `decode` | `encode()` · `decode()` |
| **Templates** | `templates` · `new` | `list_templates()` · `apply_template()` |
| **Code / Config** | `combine` · `merge` · `env` | `combine()` · `merge_configs()` |
| **Packages** | `pak add` … | `PackageManager` |
| **SSH** | `occ` | `SSHTarget` · `occ_connect()` |

---

## Custom commands

```bash
opencomb add mycommand python hello.py
opencomb mycommand
opencomb add --list
opencomb add --del mycommand
```

## Zombie / Scanner

```bash
opencomb zombie run-check --once
opencomb zombie shoot ~/Downloads --dry-run
opencomb problemscanner --cli
```

## Codec (optional utility)

Optional encode/decode for your own files — **not** used to hide package source:

```bash
opencomb codec encode mycode.py
opencomb codec decode mycode.py.oc
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
