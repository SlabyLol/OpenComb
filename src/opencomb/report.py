"""Report generation for combinations and recipes."""

from __future__ import annotations

import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class ReportGenerator:
    """Generate Markdown and HTML reports."""

    def combinations_markdown(
        self,
        combos: list[dict[str, Any]],
        *,
        title: str = "Combination Report",
        method: str = "unknown",
    ) -> str:
        if not combos:
            return f"# {title}\n\nNo combinations generated.\n"

        keys = list(combos[0].keys())
        lines = [
            f"# {title}",
            f"\n**Method:** {method}  ",
            f"**Total:** {len(combos)}  ",
            f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}\n",
            "| # | " + " | ".join(keys) + " |",
            "|---|" + "|".join(["---"] * len(keys)) + "|",
        ]
        for i, c in enumerate(combos, 1):
            row = " | ".join(str(c.get(k, "")) for k in keys)
            lines.append(f"| {i} | {row} |")
        return "\n".join(lines) + "\n"

    def combinations_html(
        self,
        combos: list[dict[str, Any]],
        *,
        title: str = "OpenComb Report",
        method: str = "unknown",
    ) -> str:
        if not combos:
            body = "<p>No combinations generated.</p>"
        else:
            keys = list(combos[0].keys())
            header = "".join(f"<th>{html.escape(k)}</th>" for k in keys)
            rows = []
            for i, c in enumerate(combos, 1):
                cells = "".join(
                    f"<td>{html.escape(str(c.get(k, '')))}</td>" for k in keys
                )
                rows.append(f"<tr><td>{i}</td>{cells}</tr>")
            body = f"""
            <table>
              <thead><tr><th>#</th>{header}</tr></thead>
              <tbody>
                {''.join(rows)}
              </tbody>
            </table>
            """

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{html.escape(title)}</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 2rem; background: #0f172a; color: #e2e8f0; }}
    h1 {{ color: #22d3ee; }}
    .meta {{ color: #94a3b8; margin-bottom: 1.5rem; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #334155; padding: 0.5rem 0.75rem; text-align: left; }}
    th {{ background: #1e293b; color: #22d3ee; }}
    tr:nth-child(even) {{ background: #1e293b; }}
    tr:hover {{ background: #334155; }}
  </style>
</head>
<body>
  <h1>{html.escape(title)}</h1>
  <div class="meta">
    Method: <strong>{html.escape(method)}</strong> ·
    Total: <strong>{len(combos)}</strong> ·
    Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}
  </div>
  {body}
</body>
</html>
"""

    def save_markdown(self, content: str, path: str | Path) -> None:
        Path(path).write_text(content, encoding="utf-8")

    def save_html(self, content: str, path: str | Path) -> None:
        Path(path).write_text(content, encoding="utf-8")

    def save_jsonl(self, combos: list[dict[str, Any]], path: str | Path) -> None:
        with Path(path).open("w", encoding="utf-8") as f:
            for c in combos:
                f.write(json.dumps(c, ensure_ascii=False) + "\n")
