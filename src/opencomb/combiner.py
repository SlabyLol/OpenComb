"""Core combining logic for code and configuration files."""

from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any

import yaml

try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # type: ignore

import tomli_w


class CodeCombiner:
    """Combine multiple Python source files / snippets into one coherent module."""

    def __init__(self, separator: str = "\n\n# --- OpenComb separator ---\n\n"):
        self.separator = separator

    def combine_files(
        self,
        files: list[str | Path],
        *,
        add_headers: bool = True,
        deduplicate_imports: bool = True,
    ) -> str:
        """
        Combine multiple Python files into a single source string.

        Args:
            files: List of file paths to combine.
            add_headers: Whether to add a comment header for each file.
            deduplicate_imports: Try to keep only unique import statements at the top.

        Returns:
            Combined Python source code as a string.
        """
        contents: list[str] = []
        all_imports: list[str] = []
        seen_imports: set[str] = set()

        for file_path in files:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"File not found: {path}")

            source = path.read_text(encoding="utf-8")

            if deduplicate_imports:
                imports, body = self._split_imports(source)
                for imp in imports:
                    normalized = imp.strip()
                    if normalized and normalized not in seen_imports:
                        seen_imports.add(normalized)
                        all_imports.append(normalized)
                source_body = body
            else:
                source_body = source

            if add_headers:
                header = f"# === Source: {path.name} ===\n"
                contents.append(header + source_body.strip())
            else:
                contents.append(source_body.strip())

        result_parts: list[str] = []
        if all_imports:
            result_parts.append("\n".join(all_imports))
            result_parts.append("")

        result_parts.append(self.separator.join(contents))
        return "\n".join(result_parts).strip() + "\n"

    def combine_snippets(
        self,
        snippets: list[str],
        *,
        names: list[str] | None = None,
    ) -> str:
        """Combine in-memory code snippets."""
        if names is None:
            names = [f"snippet_{i}" for i in range(len(snippets))]

        if len(names) != len(snippets):
            raise ValueError("names and snippets must have the same length")

        parts = []
        for name, snippet in zip(names, snippets):
            parts.append(f"# === {name} ===\n{snippet.strip()}")

        return self.separator.join(parts) + "\n"

    @staticmethod
    def _split_imports(source: str) -> tuple[list[str], str]:
        """Naive but useful import splitter using AST when possible."""
        try:
            tree = ast.parse(source)
        except SyntaxError:
            # Fallback: treat everything as body
            return [], source

        imports: list[str] = []
        lines = source.splitlines(keepends=True)

        import_end = 0
        for node in tree.body:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                # Collect the original source lines for this import
                start = node.lineno - 1
                end = getattr(node, "end_lineno", node.lineno)
                import_text = "".join(lines[start:end]).rstrip()
                imports.append(import_text)
                import_end = max(import_end, end)
            else:
                break

        body = "".join(lines[import_end:]).lstrip("\n")
        return imports, body


class ConfigMerger:
    """Intelligently merge configuration files (YAML, JSON, TOML)."""

    SUPPORTED = {".yaml", ".yml", ".json", ".toml"}

    def merge_files(
        self,
        files: list[str | Path],
        *,
        strategy: str = "deep",
    ) -> dict[str, Any]:
        """
        Merge multiple config files.

        Args:
            files: Config files in order (later files override earlier ones).
            strategy: "deep" (recursive merge) or "shallow" (top-level only).

        Returns:
            Merged dictionary.
        """
        result: dict[str, Any] = {}

        for file_path in files:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"Config file not found: {path}")

            data = self._load(path)
            if not isinstance(data, dict):
                raise ValueError(f"Config must be a mapping/object: {path}")

            if strategy == "deep":
                result = self._deep_merge(result, data)
            else:
                result.update(data)

        return result

    def merge_dicts(
        self,
        *dicts: dict[str, Any],
        strategy: str = "deep",
    ) -> dict[str, Any]:
        """Merge multiple dictionaries."""
        result: dict[str, Any] = {}
        for d in dicts:
            if strategy == "deep":
                result = self._deep_merge(result, d)
            else:
                result.update(d)
        return result

    def save(
        self,
        data: dict[str, Any],
        path: str | Path,
        *,
        format: str | None = None,
    ) -> None:
        """Save merged config to a file."""
        path = Path(path)
        fmt = format or path.suffix.lower().lstrip(".")

        if fmt in ("yaml", "yml"):
            path.write_text(
                yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False),
                encoding="utf-8",
            )
        elif fmt == "json":
            path.write_text(
                json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
        elif fmt == "toml":
            path.write_bytes(tomli_w.dumps(data).encode("utf-8"))
        else:
            raise ValueError(f"Unsupported format: {fmt}. Use yaml, json or toml.")

    def _load(self, path: Path) -> Any:
        suffix = path.suffix.lower()
        content = path.read_text(encoding="utf-8")

        if suffix in (".yaml", ".yml"):
            return yaml.safe_load(content) or {}
        if suffix == ".json":
            return json.loads(content)
        if suffix == ".toml":
            return tomllib.loads(content)

        raise ValueError(f"Unsupported config format: {suffix}")

    @staticmethod
    def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
        """Recursively merge two dictionaries. Lists are replaced, not merged."""
        result = base.copy()
        for key, value in override.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = ConfigMerger._deep_merge(result[key], value)
            else:
                result[key] = value
        return result
