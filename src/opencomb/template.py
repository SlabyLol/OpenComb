"""Jinja2-powered template rendering and combining."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined, Template, select_autoescape


class TemplateRenderer:
    """Render and combine Jinja2 templates with data."""

    def __init__(
        self,
        template_dirs: list[str | Path] | None = None,
        *,
        strict: bool = True,
    ):
        search_paths = [str(p) for p in (template_dirs or ["."])]
        self.env = Environment(
            loader=FileSystemLoader(search_paths),
            autoescape=select_autoescape(enabled_extensions=("html", "xml")),
            undefined=StrictUndefined if strict else None,
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True,
        )

    def render_string(self, template_str: str, **context: Any) -> str:
        """Render a template from a string."""
        tmpl = self.env.from_string(template_str)
        return tmpl.render(**context)

    def render_file(self, template_name: str, **context: Any) -> str:
        """Render a template file (relative to template_dirs)."""
        tmpl = self.env.get_template(template_name)
        return tmpl.render(**context)

    def render_files(
        self,
        template_names: list[str],
        *,
        separator: str = "\n\n",
        **context: Any,
    ) -> str:
        """Render multiple templates and join them."""
        parts = [self.render_file(name, **context) for name in template_names]
        return separator.join(parts)

    def combine_and_render(
        self,
        templates: list[str | Path],
        *,
        data: dict[str, Any] | None = None,
        separator: str = "\n\n# --- template separator ---\n\n",
    ) -> str:
        """
        Load multiple template files, concatenate them, then render once.
        Useful when you want shared macros / blocks across files.
        """
        contents = []
        for t in templates:
            path = Path(t)
            contents.append(path.read_text(encoding="utf-8"))

        combined = separator.join(contents)
        return self.render_string(combined, **(data or {}))
