"""OpenComb custom encoder / decoder.

Simple, reliable payload codec used by the zombie & problem-scanner loaders
and available as CLI: ``opencomb codec encode|decode``.

Format (version 1):
  magic (4 bytes) + version (1) + original_len (4, big-endian) + zlib data
Then the whole thing is base64-encoded for text-safe transport.
"""
from __future__ import annotations

import base64
import struct
import zlib
from pathlib import Path
from typing import Union

MAGIC = b"OC01"
VERSION = 1

PathLike = Union[str, Path]


def encode(data: bytes | str, *, level: int = 9) -> str:
    """Compress + wrap + base64-encode. Returns ASCII string."""
    if isinstance(data, str):
        data = data.encode("utf-8")
    compressed = zlib.compress(data, level=level)
    header = MAGIC + bytes([VERSION]) + struct.pack(">I", len(data))
    return base64.b64encode(header + compressed).decode("ascii")


def decode(payload: str | bytes) -> bytes:
    """Decode a payload produced by :func:`encode`. Returns raw bytes."""
    if isinstance(payload, str):
        payload = payload.encode("ascii")
    raw = base64.b64decode(payload)
    if len(raw) < 9 or raw[:4] != MAGIC:
        raise ValueError("Not an OpenComb codec payload (bad magic)")
    ver = raw[4]
    if ver != VERSION:
        raise ValueError(f"Unsupported codec version: {ver}")
    orig_len = struct.unpack(">I", raw[5:9])[0]
    data = zlib.decompress(raw[9:])
    if len(data) != orig_len:
        raise ValueError(f"Length mismatch: expected {orig_len}, got {len(data)}")
    return data


def encode_file(src: PathLike, dest: PathLike | None = None) -> Path:
    """Encode a file. Writes ``.oc`` next to source if dest is None."""
    src = Path(src)
    data = src.read_bytes()
    encoded = encode(data)
    if dest is None:
        dest = src.with_suffix(src.suffix + ".oc")
    else:
        dest = Path(dest)
    dest.write_text(encoded, encoding="ascii")
    return dest


def decode_file(src: PathLike, dest: PathLike | None = None) -> Path:
    """Decode a ``.oc`` file. Writes original next to source if dest is None."""
    src = Path(src)
    payload = src.read_text(encoding="ascii")
    data = decode(payload)
    if dest is None:
        # strip trailing .oc
        name = src.name
        if name.endswith(".oc"):
            name = name[:-3]
        dest = src.with_name(name)
    else:
        dest = Path(dest)
    dest.write_bytes(data)
    return dest


def encode_chunks(data: bytes | str, chunk_size: int = 3000) -> list[str]:
    """Encode and split into fixed-size base64 chunks (for GitHub size limits)."""
    encoded = encode(data)
    return [encoded[i : i + chunk_size] for i in range(0, len(encoded), chunk_size)]


def decode_chunks(chunks: list[str]) -> bytes:
    """Join chunks and decode."""
    return decode("".join(chunks))
