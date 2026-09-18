# OpenComb

**Smart Combiner for Code, Configs, Prompts & Combinatorial Generation**

[![PyPI](https://img.shields.io/pypi/v/opencomb.svg)](https://pypi.org/project/opencomb/)
[![Python](https://img.shields.io/pypi/pyversions/opencomb.svg)](https://pypi.org/project/opencomb/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

<p align="center">
  <img src="docs/logo.svg" alt="OpenComb Logo" width="160"/>
</p>

OpenComb is a practical developer toolkit that helps you:

- **Combine** multiple Python source files / snippets into one clean module (with import deduplication)
- **Merge** YAML, JSON and TOML configuration files intelligently (deep or shallow)
- **Generate** combinatorial parameter sets (full cartesian product, pairwise testing, or random sampling)

Perfect for rapid prototyping, test matrix generation, config management and AI/prompt workflows.

## Installation

```bash
pip install opencomb
```

Or with uv:

```bash
uv add opencomb
```

## Quick Start

### CLI

```bash
# Combine Python files
opencomb combine module_a.py module_b.py utils.py -o combined.py

# Merge config files (later files override earlier ones)
opencomb merge base.yaml local.yaml secrets.toml -o final.yaml

# Generate all parameter combinations
opencomb generate -p params.yaml --method cartesian -o combos.jsonl

# Efficient pairwise combinations (great for testing)
opencomb generate -p params.yaml --method pairwise

# Show info
opencomb info
```

### Library

```python
from opencomb import CodeCombiner, ConfigMerger, CombinatorialGenerator

# Combine code
combiner = CodeCombiner()
combined = combiner.combine_files(["a.py", "b.py", "c.py"])

# Merge configs
merger = ConfigMerger()
config = merger.merge_files(["base.yaml", "override.yaml"])
merger.save(config, "result.yaml")

# Generate combinations
gen = CombinatorialGenerator(seed=42)
params = {
    "lr": [0.001, 0.01, 0.1],
    "batch_size": [16, 32, 64],
    "optimizer": ["adam", "sgd"],
}
all_combos = gen.cartesian(params)
pairwise = gen.pairwise(params)          # much smaller set
sample = gen.sample(params, n=10)
```

## Features

| Feature              | Description                                      |
|----------------------|--------------------------------------------------|
| Code Combining       | Merge Python files, optional import deduplication |
| Config Merging       | Deep / shallow merge of YAML, JSON, TOML         |
| Cartesian Product    | Full combinatorial explosion                     |
| Pairwise Testing     | Efficient covering of all pairs                  |
| Random Sampling      | Quick exploration of the space                   |
| Beautiful CLI        | Powered by Typer + Rich                          |
| Pure Python          | Minimal dependencies                             |

## Example Parameter File

```yaml
# params.yaml
learning_rate: [0.001, 0.01, 0.1]
batch_size: [16, 32, 64]
optimizer: [adam, sgd, rmsprop]
dropout: [0.1, 0.3, 0.5]
```

```bash
opencomb generate -p params.yaml --method pairwise --limit 30
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

## Links

- Repository: https://github.com/SlabyLol/OpenComb
- Issues: https://github.com/SlabyLol/OpenComb/issues
