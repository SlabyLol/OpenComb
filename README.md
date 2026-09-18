# OpenComb

**Smart Combiner for Code, Configs, Prompts, Templates, Recipes, Env Files & Combinatorial Generation**

[![PyPI](https://img.shields.io/pypi/v/opencomb.svg)](https://pypi.org/project/opencomb/)
[![Python](https://img.shields.io/pypi/pyversions/opencomb.svg)](https://pypi.org/project/opencomb/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/SlabyLol/OpenComb/actions/workflows/ci.yml/badge.svg)](https://github.com/SlabyLol/OpenComb/actions/workflows/ci.yml)

<p align="center">
  <img src="docs/logo.svg" alt="OpenComb Logo" width="160"/>
</p>

**OpenComb** is a powerful developer toolkit that helps you combine, merge, generate and orchestrate almost everything you need while coding.

### Features (v0.3.0)

| Feature | CLI | Library | Description |
|---------|-----|---------|-------------|
| Code Combining | `combine` | `CodeCombiner` | Merge Python files + import dedupe + **remote URLs** |
| Config Merging | `merge` | `ConfigMerger` | Deep / shallow YAML · JSON · TOML |
| Env Merging | `env` | `EnvMerger` | Merge `.env` files + bash export scripts |
| Combinatorial | `generate` | `CombinatorialGenerator` | Cartesian · Pairwise · Sample + **constraints** |
| Prompt Building | `prompt` | `PromptCombiner` | Structured LLM prompts |
| Templates | `template` | `TemplateRenderer` | Full Jinja2 support |
| Recipes | `recipe` | `RecipeRunner` | Declarative multi-step pipelines |
| Formatting | `format` | `CodeFormatter` | ruff / black / basic cleanup |
| Reports | `--report` / `--html` | `ReportGenerator` | Markdown + beautiful HTML reports |
| Doctor | `doctor` | – | Check installation & optional tools |

## Installation

```bash
pip install opencomb

# Optional extras
pip install "opencomb[format]"   # ruff + black
```

## Quick Examples

```bash
# Combine local + remote files
opencomb combine a.py b.py https://raw.githubusercontent.com/.../utils.py -o combined.py --format

# Merge configs
opencomb merge base.yaml prod.yaml -o final.yaml

# Merge .env files
opencomb env .env .env.local --export -o load_env.sh

# Generate + HTML report
opencomb generate -p params.yaml --method pairwise --html

# Build LLM prompt
opencomb prompt -s system.txt -i task.txt -u query.txt -o prompt.txt

# Run full recipe
opencomb recipe my_pipeline.yaml

# Format code
opencomb format src/**/*.py --inplace

# Check health
opencomb doctor
```

## Library Usage

```python
from opencomb import (
    CodeCombiner, ConfigMerger, CombinatorialGenerator,
    PromptCombiner, TemplateRenderer, RecipeRunner,
    EnvMerger, CodeFormatter, ReportGenerator,
)

# Constraints example
gen = CombinatorialGenerator(seed=42)
params = {
    "os": ["linux", "windows", "macos"],
    "python": ["3.10", "3.11", "3.12"],
    "arch": ["x64", "arm64"],
}
# Only allow arm64 on macos
constraints = [
    lambda c: not (c["arch"] == "arm64" and c["os"] != "macos")
]
combos = gen.pairwise(params, constraints=constraints)
```

## Publishing to PyPI

This repository includes full CI + PyPI publish workflows.

1. Configure **Trusted Publishing** on PyPI for `SlabyLol/OpenComb` → workflow `publish.yml`
2. Tag a release:
   ```bash
   git tag v0.3.0
   git push origin v0.3.0
   ```
3. Create a GitHub Release → automatic upload to PyPI

## License

MIT © DarkFox Co. / SlabyLol

**Repo**: https://github.com/SlabyLol/OpenComb
