"""OpenComb Problem Scanner (chunked compressed loader with full fallback)."""
from __future__ import annotations

import base64
import sys
import zlib
from pathlib import Path

_dir = Path(__file__).resolve().parent

def _load():
    full = _dir / "problem_scanner_full.py"
    if full.is_file():
        code = full.read_text(encoding="utf-8")
        ns = globals()
        ns.setdefault("__name__", __name__)
        ns.setdefault("__file__", str(full))
        sys.modules.setdefault(__name__, sys.modules.get(__name__))
        exec(compile(code, str(full), "exec"), ns)
        return
    parts = sorted(_dir.glob("_scanner_b64_*.txt"), key=lambda p: int(p.stem.split("_")[-1]))
    b64 = "".join(p.read_text(encoding="ascii") for p in parts)
    if not b64:
        raise ImportError("OpenComb problem_scanner: no payload chunks and no problem_scanner_full.py")
    code = zlib.decompress(base64.b64decode(b64)).decode("utf-8")
    ns = globals()
    ns.setdefault("__name__", __name__)
    ns.setdefault("__file__", __file__)
    sys.modules.setdefault(__name__, sys.modules.get(__name__))
    exec(compile(code, __file__, "exec"), ns)

_load()
