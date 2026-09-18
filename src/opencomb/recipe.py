"""Recipe system – declarative combining of code, configs, prompts and templates."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from opencomb.combiner import CodeCombiner, ConfigMerger
from opencomb.combinatorial import CombinatorialGenerator
from opencomb.prompt import PromptCombiner
from opencomb.template import TemplateRenderer


class RecipeRunner:
    """
    Execute OpenComb recipes defined in YAML.

    A recipe can combine code, merge configs, render templates,
    build prompts and generate combinatorial sets in one go.
    """

    def __init__(self, base_dir: str | Path | None = None):
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()

    def load(self, recipe_path: str | Path) -> dict[str, Any]:
        """Load a recipe YAML file."""
        path = Path(recipe_path)
        if not path.is_absolute():
            path = self.base_dir / path
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("Recipe must be a YAML mapping")
        return data

    def run(self, recipe: dict[str, Any] | str | Path, *, dry_run: bool = False) -> dict[str, Any]:
        """
        Execute a recipe.

        Returns a dict with results of each step.
        """
        if not isinstance(recipe, dict):
            recipe = self.load(recipe)

        results: dict[str, Any] = {}
        name = recipe.get("name", "unnamed")
        results["_recipe"] = name

        # 1. Code combining
        if "combine" in recipe:
            step = recipe["combine"]
            files = [self._resolve(f) for f in step.get("files", [])]
            output = step.get("output")
            combiner = CodeCombiner()
            combined = combiner.combine_files(
                files,
                add_headers=step.get("headers", True),
                deduplicate_imports=step.get("dedupe_imports", True),
            )
            results["combine"] = combined
            if output and not dry_run:
                out_path = self._resolve(output)
                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_path.write_text(combined, encoding="utf-8")
                results["combine_output"] = str(out_path)

        # 2. Config merging
        if "merge" in recipe:
            step = recipe["merge"]
            files = [self._resolve(f) for f in step.get("files", [])]
            output = step.get("output")
            strategy = step.get("strategy", "deep")
            merger = ConfigMerger()
            merged = merger.merge_files(files, strategy=strategy)
            results["merge"] = merged
            if output and not dry_run:
                out_path = self._resolve(output)
                out_path.parent.mkdir(parents=True, exist_ok=True)
                fmt = step.get("format")
                merger.save(merged, out_path, format=fmt)
                results["merge_output"] = str(out_path)

        # 3. Template rendering
        if "template" in recipe:
            step = recipe["template"]
            template_dirs = step.get("dirs", ["."])
            renderer = TemplateRenderer(
                [self._resolve(d) for d in template_dirs],
                strict=step.get("strict", True),
            )
            data = step.get("data", {})
            if "file" in step:
                rendered = renderer.render_file(step["file"], **data)
            elif "files" in step:
                rendered = renderer.render_files(
                    step["files"],
                    separator=step.get("separator", "\n\n"),
                    **data,
                )
            elif "string" in step:
                rendered = renderer.render_string(step["string"], **data)
            else:
                raise ValueError("template step needs 'file', 'files' or 'string'")
            results["template"] = rendered
            if "output" in step and not dry_run:
                out_path = self._resolve(step["output"])
                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_path.write_text(rendered, encoding="utf-8")
                results["template_output"] = str(out_path)

        # 4. Prompt building
        if "prompt" in recipe:
            step = recipe["prompt"]
            combiner = PromptCombiner()
            prompt = combiner.combine(
                system=step.get("system"),
                instruction=step.get("instruction"),
                context=step.get("context"),
                examples=step.get("examples"),
                user=step.get("user"),
                extra_sections=step.get("extra_sections"),
            )
            results["prompt"] = prompt
            if "output" in step and not dry_run:
                out_path = self._resolve(step["output"])
                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_path.write_text(prompt, encoding="utf-8")
                results["prompt_output"] = str(out_path)

        # 5. Combinatorial generation
        if "generate" in recipe:
            step = recipe["generate"]
            params = step.get("params", {})
            method = step.get("method", "cartesian")
            limit = step.get("limit")
            seed = step.get("seed")
            gen = CombinatorialGenerator(seed=seed)

            if method == "cartesian":
                combos = gen.cartesian(params, limit=limit)
            elif method == "pairwise":
                combos = gen.pairwise(params, limit=limit)
            elif method == "sample":
                combos = gen.sample(params, n=limit or 10)
            else:
                raise ValueError(f"Unknown generate method: {method}")

            results["generate"] = combos
            if "output" in step and not dry_run:
                import json
                out_path = self._resolve(step["output"])
                out_path.parent.mkdir(parents=True, exist_ok=True)
                with out_path.open("w", encoding="utf-8") as f:
                    for c in combos:
                        f.write(json.dumps(c, ensure_ascii=False) + "\n")
                results["generate_output"] = str(out_path)

        return results

    def _resolve(self, path: str | Path) -> Path:
        p = Path(path)
        if p.is_absolute():
            return p
        return self.base_dir / p
