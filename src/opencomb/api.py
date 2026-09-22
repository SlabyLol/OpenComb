"""OpenComb high-level convenience functions (used by ``import opencomb``)."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Sequence, Union

from opencomb.combiner import CodeCombiner, ConfigMerger
from opencomb.combinatorial import CombinatorialGenerator
from opencomb.env import EnvMerger
from opencomb.formatter import CodeFormatter
from opencomb.prompt import PromptCombiner
from opencomb.recipe import RecipeRunner
from opencomb.template import TemplateRenderer
from opencomb.templates_catalog import apply_template
from opencomb.scaffold import project_doctor
from opencomb.tools import Searcher, TodoExtractor, ProjectStats

PathLike = Union[str, Path]
PathList = Sequence[PathLike]


def combine(
    files: PathList | None = None,
    *,
    snippets: Sequence[str] | None = None,
    add_headers: bool = True,
    deduplicate_imports: bool = True,
    format_code: bool = False,
) -> str:
    """Combine Python source files and/or snippets into one string."""
    combiner = CodeCombiner()
    parts: list[str] = []
    if files:
        paths = [Path(f) for f in files]
        parts.append(
            combiner.combine_files(
                paths,
                add_headers=add_headers,
                deduplicate_imports=deduplicate_imports,
            )
        )
    if snippets:
        parts.append(combiner.combine_snippets(list(snippets)))
    result = "\n".join(p for p in parts if p)
    if format_code:
        result = CodeFormatter().format(result)
    return result


def merge_configs(
    files: PathList,
    *,
    strategy: str = "deep",
    output: PathLike | None = None,
    format: str | None = None,
) -> dict[str, Any]:
    """Deep-merge YAML / JSON / TOML config files."""
    merger = ConfigMerger()
    result = merger.merge_files([Path(f) for f in files], strategy=strategy)
    if output:
        merger.save(result, Path(output), format=format)
    return result


def merge_env(
    files: PathList,
    *,
    include_os: bool = False,
    output: PathLike | None = None,
) -> dict[str, str]:
    """Merge ``.env`` files into a single mapping."""
    merger = EnvMerger()
    result = merger.merge_files([Path(f) for f in files], include_os=include_os)
    if output:
        merger.save(result, Path(output))
    return result


def generate_combos(
    parameters: Mapping[str, Sequence[Any]],
    *,
    method: str = "cartesian",
    limit: int | None = None,
    seed: int | None = None,
) -> list[dict[str, Any]]:
    """Generate combinatorial parameter sets (cartesian / pairwise / sample)."""
    gen = CombinatorialGenerator(seed=seed)
    if method == "cartesian":
        return gen.cartesian(dict(parameters), limit=limit)
    if method == "pairwise":
        return gen.pairwise(dict(parameters), limit=limit)
    return gen.sample(dict(parameters), n=limit or 10)


def render_template(
    template: str | Path,
    *,
    data: Mapping[str, Any] | None = None,
    strict: bool = True,
) -> str:
    """Render a Jinja2 template string or file."""
    ctx = dict(data or {})
    r = TemplateRenderer(strict=strict)
    p = Path(template)
    if p.exists() and p.is_file():
        return r.render_file(p, **ctx)
    return r.render_string(str(template), **ctx)


def build_prompt(
    *,
    system: Sequence[str] | str | None = None,
    instruction: str | None = None,
    context: Sequence[str] | str | None = None,
    examples: Any = None,
    user: str | None = None,
) -> str:
    """Build a structured LLM prompt from parts."""
    return PromptCombiner().combine(
        system=system,
        instruction=instruction,
        context=context,
        examples=examples,
        user=user,
    )


def run_recipe(recipe_file: PathLike, *, dry_run: bool = False) -> dict[str, Any]:
    """Execute a declarative OpenComb recipe YAML/JSON file."""
    path = Path(recipe_file)
    return RecipeRunner(base_dir=path.parent).run(path, dry_run=dry_run)


def new_project(
    name: str,
    *,
    template: str = "minimal",
    path: PathLike | None = None,
    force: bool = False,
) -> Path:
    """Scaffold a new project from a template. Returns project root path."""
    target = (Path(path) if path else Path.cwd()) / name
    if target.exists() and any(target.iterdir()) and not force:
        raise FileExistsError(f"Target not empty: {target}")
    target.mkdir(parents=True, exist_ok=True)
    apply_template(template, name, target)
    return target.resolve()


def search(
    pattern: str,
    root: PathLike = ".",
    *,
    regex: bool = False,
    max_hits: int = 200,
) -> list[dict[str, Any]]:
    """Search files under *root* for *pattern*. Returns list of hit dicts."""
    return Searcher().search(Path(root), pattern, regex=regex, max_hits=max_hits)


def todos(root: PathLike = ".") -> list[dict[str, Any]]:
    """Extract TODO / FIXME / HACK comments from a tree."""
    return TodoExtractor().extract(Path(root))


def stats(root: PathLike = ".") -> dict[str, Any]:
    """Collect file / line statistics for a project tree."""
    return ProjectStats().collect(Path(root))


def doctor(root: PathLike = ".") -> dict[str, Any]:
    """Score a project for completeness. Keys: path, score, max, findings, grade."""
    return project_doctor(Path(root))
