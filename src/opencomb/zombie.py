"""OpenComb Zombie toolkit (chunked compressed loader with full fallback)."""
from __future__ import annotations

import base64
import sys
import zlib
from pathlib import Path

_dir = Path(__file__).resolve().parent

def _collect(prefix: str) -> str:
    parts = []
    n = 0
    while True:
        plain = _dir / f"{prefix}_{n}.txt"
        a = _dir / f"{prefix}_{n}a.txt"
        b = _dir / f"{prefix}_{n}b.txt"
        if plain.is_file():
            parts.append(plain.read_text(encoding="ascii"))
        elif a.is_file() or b.is_file():
            parts.append(
                (a.read_text(encoding="ascii") if a.is_file() else "")
                + (b.read_text(encoding="ascii") if b.is_file() else "")
            )
        else:
            break
        n += 1
    return "".join(parts)

def _load():
    full = _dir / "zombie_full.py"
    if full.is_file():
        # Prefer plain full source when present (dev / incomplete chunks)
        code = full.read_text(encoding="utf-8")
        ns = globals()
        ns.setdefault("__name__", __name__)
        ns.setdefault("__file__", str(full))
        sys.modules.setdefault(__name__, sys.modules.get(__name__))
        exec(compile(code, str(full), "exec"), ns)
        return
    b64 = _collect("_zombie_b64")
    if not b64:
        raise ImportError("OpenComb zombie: no payload chunks and no zombie_full.py")
    code = zlib.decompress(base64.b64decode(b64)).decode("utf-8")
    ns = globals()
    ns.setdefault("__name__", __name__)
    ns.setdefault("__file__", __file__)
    sys.modules.setdefault(__name__, sys.modules.get(__name__))
    exec(compile(code, __file__, "exec"), ns)

_load()
