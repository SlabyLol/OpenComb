"""Template builders (templates_a1.py) — full plain source, no zlib."""
from __future__ import annotations

from opencomb.templates_base import FileSpec, _pkg, _pyproject, _gitignore

# NOTE: Full template content is loaded from local verified source.
# This stub is replaced in the same release by the complete builders.

def tpl_minimal(name: str):
    """Minimal package scaffold."""
    return [
        _pyproject(name, "Minimal OpenComb project"),
        FileSpec("README.md", f"# {name}\n\nMinimal project.\n"),
        FileSpec(f"src/{name}/__init__.py", '__version__ = "0.1.0"\n'),
        FileSpec("tests/test_smoke.py", "def test_version():\n    assert True\n"),
        _gitignore(),
    ]
