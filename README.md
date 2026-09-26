# OpenComb

**Developer Swiss Army Knife** — **100% plain Python source** (no base64, no obfuscation).

[![PyPI](https://img.shields.io/pypi/v/opencomb.svg)](https://pypi.org/project/opencomb/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

```bash
pip install opencomb
```

## Highlights (v0.19.3)

| Area | CLI |
|------|-----|
| **Sandbox** | `sandbox` · `create` · `run` · `shell` · `gui` · `config` |
| **Zombie** | `zombie run-check` · `shoot` · `list` |
| **Scanner** | `problemscanner` |
| **Custom** | `add` · `add --list` · `add --del` |
| **Templates** | `templates` · `new` |

## Sandbox (isolated build env)

```bash
opencomb sandbox                    # choose GUI or CLI config
opencomb sandbox create mybox --packages requests,rich
opencomb sandbox gui
opencomb sandbox run mybox -- python work/hello.py
opencomb sandbox shell mybox
opencomb sandbox list
opencomb sandbox destroy mybox
```

Sandboxes: `~/.opencomb/sandboxes/<name>/` with `.venv`, `sandbox.yaml`, `work/`.

## Development

```bash
git clone https://github.com/SlabyLol/OpenComb.git
cd OpenComb && pip install -e ".[dev]"
```

## License

MIT © DarkFox Co.
