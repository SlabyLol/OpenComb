"""Shared utilities for OpenComb."""

from __future__ import annotations

import re
import urllib.request
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


def is_url(path: str) -> bool:
    """Return True if the string looks like an HTTP/HTTPS URL."""
    try:
        result = urlparse(path)
        return result.scheme in ("http", "https") and bool(result.netloc)
    except Exception:
        return False


def load_text(source: str | Path, *, encoding: str = "utf-8", timeout: int = 15) -> str:
    """Load text from a local file or a remote URL."""
    source_str = str(source)
    if is_url(source_str):
        req = urllib.request.Request(
            source_str,
            headers={"User-Agent": "OpenComb/0.3"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode(encoding)
    path = Path(source_str)
    return path.read_text(encoding=encoding)


def load_lines(source: str | Path) -> list[str]:
    """Load lines from file or URL."""
    return load_text(source).splitlines()


def ensure_dir(path: str | Path) -> Path:
    """Create parent directories if needed and return Path."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def slugify(text: str) -> str:
    """Simple slugify for filenames."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "-", text)
    return text.strip("-")
