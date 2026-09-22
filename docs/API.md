# OpenComb Python API Reference

**Version 0.17.0**

```bash
pip install opencomb
```

```python
import opencomb
from opencomb import CodeCombiner, ConfigMerger, apply_template, combine, doctor
```

---

## Table of contents

1. [Quick start](#1-quick-start)
2. [Convenience functions](#2-convenience-functions)
3. [Code combination](#3-code-combination)
4. [Config & env merging](#4-config--env-merging)
5. [Combinatorial generation](#5-combinatorial-generation)
6. [Prompts & templates](#6-prompts--templates)
7. [Recipes](#7-recipes)
8. [Project scaffolding](#8-project-scaffolding)
9. [Package management](#9-package-management)
10. [Search, todos, stats](#10-search-todos-stats)
11. [Doctor & structure](#11-doctor--structure)
12. [Build system](#12-build-system)
13. [Drill shell](#13-drill-shell)
14. [OCC (SSH)](#14-occ-ssh)
15. [Devtools](#15-devtools)
16. [Formatting & reports](#16-formatting--reports)

---

## 1. Quick start

```python
import opencomb

print(opencomb.__version__)

code = opencomb.combine(["a.py", "b.py"])
cfg = opencomb.merge_configs(["base.yaml", "local.yaml"])
path = opencomb.new_project("my-api", template="fastapi")
report = opencomb.doctor(".")
print(report["score"], report["grade"])
```

---

## 2. Convenience functions

Top-level helpers from `opencomb`:

| Function | Description |
|----------|-------------|
| `combine(files=None, *, snippets=None, add_headers=True, deduplicate_imports=True, format_code=False) -> str` | Combine `.py` files and/or snippets |
| `merge_configs(files, *, strategy="deep", output=None, format=None) -> dict` | Merge YAML/JSON/TOML |
| `merge_env(files, *, include_os=False, output=None) -> dict[str, str]` | Merge `.env` files |
| `generate_combos(parameters, *, method="cartesian", limit=None, seed=None) -> list[dict]` | Combinatorial sets |
| `render_template(template, *, data=None, strict=True) -> str` | Jinja2 string or file |
| `build_prompt(*, system=None, instruction=None, context=None, examples=None, user=None) -> str` | Structured LLM prompt |
| `run_recipe(recipe_file, *, dry_run=False) -> dict` | Run recipe YAML/JSON |
| `new_project(name, *, template="minimal", path=None, force=False) -> Path` | Scaffold from template |
| `search(pattern, root=".", *, regex=False, max_hits=200) -> list[dict]` | Code search |
| `todos(root=".") -> list[dict]` | TODO/FIXME extractor |
| `stats(root=".") -> dict` | Project statistics |
| `doctor(root=".") -> dict` | Project quality score |

### Examples

```python
import opencomb

src = opencomb.combine(snippets=["import os", "print(os.getcwd())"])
rows = opencomb.generate_combos({"lr": [0.001, 0.01], "batch": [16, 32]}, method="pairwise")
html = opencomb.render_template("Hello {{ name }}!", data={"name": "World"})
opencomb.new_project("demo-api", template="fastapi")
```

---

## 3. Code combination

### `CodeCombiner`

```python
from opencomb import CodeCombiner

c = CodeCombiner()
text = c.combine_files(["lib/a.py", "lib/b.py"], add_headers=True, deduplicate_imports=True)
text = c.combine_snippets(["x = 1", "y = 2"], names=["a.py", "b.py"])
```

| Method | Description |
|--------|-------------|
| `combine_files(files, *, add_headers=True, deduplicate_imports=True) -> str` | Merge files on disk |
| `combine_snippets(snippets, *, names=None) -> str` | Merge in-memory strings |

---

## 4. Config & env merging

### `ConfigMerger`

```python
from opencomb import ConfigMerger

m = ConfigMerger()
data = m.merge_files(["base.yaml", "prod.yaml"], strategy="deep")
data = m.merge_dicts({"a": 1}, {"a": 2, "b": 3})
m.save(data, "out.yaml", format="yaml")
```

### `EnvMerger`

```python
from opencomb import EnvMerger

e = EnvMerger()
env = e.merge_files([".env", ".env.local"], include_os=False)
e.save(env, ".env.merged")
script = e.to_export_script(env)
```

---

## 5. Combinatorial generation

### `CombinatorialGenerator`

```python
from opencomb import CombinatorialGenerator

g = CombinatorialGenerator(seed=42)
params = {"lr": [0.001, 0.01, 0.1], "opt": ["adam", "sgd"]}
all_rows = g.cartesian(params)
pair_rows = g.pairwise(params, limit=20)
sample_rows = g.sample(params, n=5)
```

| Method | Description |
|--------|-------------|
| `cartesian(parameters, limit=None)` | Full product |
| `pairwise(parameters, limit=None)` | Pairwise covering |
| `sample(parameters, n=10)` | Random sample |
| `iterate(parameters, method=...)` | Lazy iterator |

---

## 6. Prompts & templates

### `PromptCombiner`

```python
from opencomb import PromptCombiner

p = PromptCombiner()
text = p.combine(system="You are helpful.", instruction="Summarize.", user="...")
text = p.from_files(system_files=["sys.md"], instruction_file="task.md")
```

### `TemplateRenderer`

```python
from opencomb import TemplateRenderer

r = TemplateRenderer(strict=True)
print(r.render_string("Hi {{ name }}", name="Ada"))
print(r.render_file("tpl.j2", name="Ada"))
```

---

## 7. Recipes

### `RecipeRunner`

```python
from opencomb import RecipeRunner

rr = RecipeRunner(base_dir=".")
result = rr.run("recipe.yaml", dry_run=False)
```

---

## 8. Project scaffolding

```python
from opencomb import list_templates, apply_template, BUILDERS
from opencomb import list_stacks, list_components, apply_stack, add_component, run_wizard

for t in list_templates():
    print(t.id, t.name, t.description)

apply_template("fastapi", "my_api", Path("./my-api"))
apply_stack("api-full", Path("./svc"), project_name="svc")
add_component("dockerfile", Path("./svc"))
run_wizard()
```

**Stacks:** `api-full`, `cli-pro`, `ml-api`, `web-full`, `discord-bot`, `library`, `data-science`, `monorepo`, `minimal`, `pyrunner`

**Components:** `dockerfile`, `makefile`, `precommit`, `devcontainer`, `gitignore`, `compose`, `pytest`, `github-ci`, `readme`

### `ProjectHelper`

```python
from opencomb import ProjectHelper

h = ProjectHelper()
root = h.init("myproj", description="Demo", src_layout=True)
print(h.tree(root, max_depth=3))
h.bump_version("pyproject.toml", part="patch")
```

---

## 9. Package management

### `PackageManager`

```python
from opencomb import PackageManager

pm = PackageManager()
pm.add(["requests", "httpx"])
pm.remove(["httpx"])
print(pm.list_installed())
print(pm.show("requests"))
print(pm.info_summary("numpy"))
print(pm.freeze())
```

---

## 10. Search, todos, stats

```python
import opencomb
from opencomb import Searcher, TodoExtractor, ProjectStats

hits = opencomb.search(r"TODO|FIXME", ".", regex=True)
items = opencomb.todos(".")
st = opencomb.stats(".")
```

| Class | Method | Returns |
|-------|--------|--------|
| `Searcher` | `search(root, pattern, *, regex=False, ...)` | `list[dict]` |
| `TodoExtractor` | `extract(root, ...)` | `list[dict]` |
| `ProjectStats` | `collect(root)` | `dict` |
| `Differ` | `files(a, b)` | unified diff |
| `Hasher` | `hash_file` / `hash_tree` | digests |
| `OutdatedChecker` | `check()` | outdated pkgs |
| `ReportServer` | `serve(path, port)` | HTTP server |
| `Watcher` | `run(path, command)` | file watcher |

---

## 11. Doctor & structure

```python
from opencomb import doctor, print_doctor_report, suggest_structure

report = doctor(".")
print_doctor_report(report)
print(suggest_structure("api"))  # also: cli, lib, data
```

Report keys: `path`, `score` (0-100), `max`, `findings`, `grade` (A-F).

---

## 12. Build system

```python
from opencomb import interactive_build, run_build_ids, all_targets

for t in all_targets():
    print(t.id, t.label)
run_build_ids(["wheel", "test", "check"])
interactive_build()
```

---

## 13. Drill shell

```python
from opencomb import start_drill, DrillShell

start_drill(".")
```

---

## 14. OCC (SSH)

```python
from opencomb import SSHTarget, parse_target_string, occ_connect, occ_interactive

user, host, port = parse_target_string("alice@example.com:2222")
target = SSHTarget(host=host, user=user, port=port or 22)
occ_connect(target)
occ_interactive()
```

Profiles: `~/.opencomb/occ_profiles/`.

---

## 15. Devtools

```python
from opencomb import GitHelper, SecretScanner, HttpClient, Bench
from opencomb import JsonYamlQuery, PortProbe, GitClone, SiteCloner

GitHelper().status()
SecretScanner().scan(".")
HttpClient().get("https://example.com")
Bench().run("python -c 'print(1)'", runs=5)
GitClone().clone("https://github.com/org/repo.git", dest="repo", depth=1)
SiteCloner().clone_page("https://example.com", "site_download")
```

---

## 16. Formatting & reports

```python
from opencomb import CodeFormatter, ReportGenerator, Checker

print(CodeFormatter().format("x=1", prefer="ruff"))
rg = ReportGenerator()
md = rg.combinations_markdown(rows, method="pairwise")
results = Checker().run_all(paths=["src", "tests"])
```

---

## Version

```python
import opencomb
opencomb.__version__  # "0.17.0"
opencomb.__all__
```

CLI: `opencomb templates`, `opencomb new fastapi my-api`, `opencomb combine a.py b.py`, `opencomb syscheck`, `opencomb occ user@host`.

See [README.md](../README.md) for CLI details.
