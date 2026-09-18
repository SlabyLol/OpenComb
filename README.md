# OpenComb

**Smart Combiner for Code, Configs, Prompts, Templates, Recipes & Combinatorial Generation**

[![PyPI](https://img.shields.io/pypi/v/opencomb.svg)](https://pypi.org/project/opencomb/)
[![Python](https://img.shields.io/pypi/pyversions/opencomb.svg)](https://pypi.org/project/opencomb/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/SlabyLol/OpenComb/actions/workflows/ci.yml/badge.svg)](https://github.com/SlabyLol/OpenComb/actions/workflows/ci.yml)

<p align="center">
  <img src="[https://github.com/SlabyLol/OpenComb/blob/main/docs/logo.svg](https://github.com/SlabyLol/OpenComb/blob/main/docs/logo.svg)" alt="OpenComb Logo" width="160"/>
</p>

**OpenComb** is a powerful, practical toolkit for developers that helps you:

- **Combine** multiple Python source files into one clean module (with smart import deduplication)
- **Merge** YAML, JSON and TOML configs intelligently (deep or shallow)
- **Generate** combinatorial parameter sets (cartesian, pairwise testing, sampling)
- **Build** structured LLM prompts from system / instruction / context / few-shot / user parts
- **Render** Jinja2 templates (single or multi-file)
- **Run declarative recipes** that orchestrate all of the above in one YAML file

Perfect for rapid prototyping, test matrix generation, config management, AI/prompt engineering and automation pipelines.

## Installation

```bash
pip install opencomb
```

Or with uv:

```bash
uv add opencomb
```

## Features at a Glance

| Feature              | CLI Command     | Library Class            | Description                                      |
|----------------------|-----------------|--------------------------|--------------------------------------------------|
| Code Combining       | `combine`       | `CodeCombiner`           | Merge Python files + import dedupe               |
| Config Merging       | `merge`         | `ConfigMerger`           | Deep / shallow YAML·JSON·TOML                    |
| Combinatorial Gen    | `generate`      | `CombinatorialGenerator` | Cartesian · Pairwise · Sample                    |
| Prompt Building      | `prompt`        | `PromptCombiner`         | Structured LLM prompts                           |
| Template Rendering   | `template`      | `TemplateRenderer`       | Jinja2 power                                     |
| Recipe Runner        | `recipe`        | `RecipeRunner`           | Full pipelines in one YAML                       |

## Quick Start – CLI

```bash
# Combine Python files
opencomb combine module_a.py module_b.py utils.py -o combined.py

# Merge configs (later files win)
opencomb merge base.yaml local.yaml secrets.toml -o final.yaml

# Generate combinations
opencomb generate -p params.yaml --method pairwise --report

# Build an LLM prompt
opencomb prompt \
  --system system.txt \
  --instruction task.txt \
  --examples fewshot.yaml \
  --user query.txt \
  -o final_prompt.txt

# Render Jinja2 templates
opencomb template template.j2 --data data.yaml -o output.md

# Run a full recipe
opencomb recipe examples/sample_recipe.yaml
opencomb recipe examples/sample_recipe.yaml --dry-run --verbose
```

## Quick Start – Library

```python
from opencomb import (
    CodeCombiner,
    ConfigMerger,
    CombinatorialGenerator,
    PromptCombiner,
    TemplateRenderer,
    RecipeRunner,
)

# Code
combiner = CodeCombiner()
code = combiner.combine_files(["a.py", "b.py"])

# Config
merger = ConfigMerger()
config = merger.merge_files(["base.yaml", "override.yaml"])
merger.save(config, "result.yaml")

# Combinations
gen = CombinatorialGenerator(seed=42)
params = {"lr": [0.001, 0.01], "batch": [16, 32], "opt": ["adam", "sgd"]}
all_combos = gen.cartesian(params)
pairwise   = gen.pairwise(params)   # much smaller & efficient

# Prompts
pc = PromptCombiner()
prompt = pc.combine(
    system="You are a senior Python engineer.",
    instruction="Review the following code.",
    examples=[{"input": "x=1", "output": "Looks fine."}],
    user="def foo(): pass",
)

# Templates
renderer = TemplateRenderer()
html = renderer.render_string("<h1>{{ title }}</h1>", title="OpenComb")

# Recipes
runner = RecipeRunner()
results = runner.run("my_recipe.yaml")
```

## Recipe Example

```yaml
# my_pipeline.yaml
name: full-pipeline

combine:
  files: [src/a.py, src/b.py, src/utils.py]
  output: build/combined.py

merge:
  files: [config/base.yaml, config/prod.yaml]
  output: build/config.yaml
  strategy: deep

generate:
  method: pairwise
  params:
    python: ["3.10", "3.11", "3.12"]
    os: ["linux", "macos", "windows"]
  output: build/matrix.jsonl
  seed: 42

prompt:
  system: |
    You are an expert code reviewer.
  instruction: |
    Review the combined module and suggest improvements.
  output: build/review_prompt.txt

template:
  file: templates/report.md.j2
  data:
    project: OpenComb
    version: "0.2.0"
  output: build/report.md
```

```bash
opencomb recipe my_pipeline.yaml
```

## Publishing to PyPI

This repository includes ready-to-use GitHub Actions:

- **CI** (`.github/workflows/ci.yml`) – runs tests on Python 3.10–3.13 + builds the package
- **Publish** (`.github/workflows/publish.yml`) – publishes to PyPI when you create a GitHub Release

### How to release

1. Make sure the version in `pyproject.toml` is correct (currently `0.2.0`)
2. Create a new GitHub Release (or tag):
   ```bash
   git tag v0.2.0
   git push origin v0.2.0
   ```
   Then create a Release on GitHub from that tag.
3. The `publish.yml` workflow will automatically build and upload to PyPI.

### Trusted Publishing (recommended)

1. Go to https://pypi.org/manage/account/publishing/
2. Add a new pending publisher:
   - **PyPI Project Name**: `opencomb`
   - **Owner**: `SlabyLol`
   - **Repository name**: `OpenComb`
   - **Workflow name**: `publish.yml`
   - **Environment name**: `pypi`
3. Create the project on PyPI if it doesn’t exist yet (first upload will create it).

Alternatively you can use a classic API token:
- Create a token on PyPI → add it as repository secret `PYPI_TOKEN`
- Uncomment the token-based step in `publish.yml`

## Development

```bash
git clone https://github.com/SlabyLol/OpenComb.git
cd OpenComb
pip install -e ".[dev]"
pytest
ruff check src tests
```

## License

MIT © DarkFox Co. / SlabyLol

## Links

- **Repository**: https://github.com/SlabyLol/OpenComb
- **Issues**: https://github.com/SlabyLol/OpenComb/issues
- **PyPI**: https://pypi.org/project/opencomb/
