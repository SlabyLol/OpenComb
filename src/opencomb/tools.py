"""Strong developer tools: search, todos, stats, diff, hash, serve, outdated, watch."""

from __future__ import annotations

import hashlib
import http.server
import json
import os
import re
import socketserver
import subprocess
import sys
import time
import urllib.request
from collections import Counter
from difflib import unified_diff
from pathlib import Path
from typing import Any, Callable, Iterator

CODE_EXTS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".java", ".kt",
    ".c", ".cpp", ".h", ".hpp", ".cs", ".rb", ".php", ".swift", ".md",
    ".yaml", ".yml", ".toml", ".json", ".sh", ".bash", ".zsh", ".sql",
}
SKIP_DIRS = {
    ".git", "__pycache__", ".venv", "venv", "node_modules", "dist", "build",
    ".mypy_cache", ".ruff_cache", ".pytest_cache", ".tox", ".nox", ".eggs",
    "htmlcov", ".idea", ".vscode",
}
TODO_RE = re.compile(
    r"(?P<kind>TODO|FIXME|XXX|HACK|NOTE|BUG|OPTIMIZE)[\s:.\x96-]*(?P<text>.*)",
    re.IGNORECASE,
)


def iter_files(root: Path, *, exts: set[str] | None = None, max_files: int = 50_000) -> Iterator[Path]:
    count = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.endswith(".egg-info")]
        for name in filenames:
            p = Path(dirpath) / name
            if exts and p.suffix.lower() not in exts:
                continue
            yield p
            count += 1
            if count >= max_files:
                return


class Searcher:
    def search(self, root: str | Path, pattern: str, *, regex: bool = False, ignore_case: bool = True, exts: set[str] | None = None, max_hits: int = 200) -> list[dict[str, Any]]:
        root = Path(root).resolve()
        flags = re.IGNORECASE if ignore_case else 0
        cre = re.compile(pattern if regex else re.escape(pattern), flags)
        hits: list[dict[str, Any]] = []
        for path in iter_files(root, exts=exts or CODE_EXTS):
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for i, line in enumerate(text.splitlines(), 1):
                if cre.search(line):
                    hits.append({"file": str(path.relative_to(root)), "line": i, "text": line.strip()[:200]})
                    if len(hits) >= max_hits:
                        return hits
        return hits


class TodoExtractor:
    def extract(self, root: str | Path, *, max_items: int = 500) -> list[dict[str, Any]]:
        root = Path(root).resolve()
        items: list[dict[str, Any]] = []
        for path in iter_files(root, exts=CODE_EXTS):
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for i, line in enumerate(text.splitlines(), 1):
                m = TODO_RE.search(line)
                if m:
                    items.append({"kind": m.group("kind").upper(), "file": str(path.relative_to(root)), "line": i, "text": m.group("text").strip()[:160]})
                    if len(items) >= max_items:
                        return items
        return items


class ProjectStats:
    def collect(self, root: str | Path) -> dict[str, Any]:
        root = Path(root).resolve()
        by_ext: Counter[str] = Counter()
        lines_by_ext: Counter[str] = Counter()
        total_bytes = 0
        files = 0
        for path in iter_files(root):
            files += 1
            ext = path.suffix.lower() or "(none)"
            by_ext[ext] += 1
            try:
                data = path.read_bytes()
                total_bytes += len(data)
                if ext in CODE_EXTS or ext == ".py":
                    lines_by_ext[ext] += data.count(b"\n") + (1 if data and not data.endswith(b"\n") else 0)
            except OSError:
                continue
        return {"root": str(root), "files": files, "bytes": total_bytes, "by_extension": dict(by_ext.most_common(30)), "lines_by_extension": dict(lines_by_ext.most_common(20)), "total_code_lines": sum(lines_by_ext.values())}


class Differ:
    def files(self, a: str | Path, b: str | Path, *, context: int = 3) -> str:
        pa, pb = Path(a), Path(b)
        ta = pa.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)
        tb = pb.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)
        return "".join(unified_diff(ta, tb, fromfile=str(pa), tofile=str(pb), n=context))


class Hasher:
    ALGOS = ("md5", "sha1", "sha256", "sha512")

    def hash_file(self, path: str | Path, algo: str = "sha256") -> str:
        h = hashlib.new(algo)
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        return h.hexdigest()

    def hash_tree(self, root: str | Path, algo: str = "sha256") -> list[dict[str, str]]:
        root = Path(root).resolve()
        out = []
        for path in sorted(iter_files(root)):
            try:
                out.append({"file": str(path.relative_to(root)), "hash": self.hash_file(path, algo)})
            except OSError:
                continue
        return out


class OutdatedChecker:
    PYPI = "https://pypi.org/pypi/{name}/json"

    def check(self, names: list[str] | None = None) -> list[dict[str, Any]]:
        if names is None:
            result = subprocess.run([sys.executable, "-m", "pip", "list", "--format=json"], capture_output=True, text=True, check=False)
            if result.returncode != 0:
                return []
            installed = {p["name"].lower(): p["version"] for p in json.loads(result.stdout)}
        else:
            installed = {}
            for n in names:
                r = subprocess.run([sys.executable, "-m", "pip", "show", n], capture_output=True, text=True, check=False)
                ver = None
                for line in r.stdout.splitlines():
                    if line.lower().startswith("version:"):
                        ver = line.split(":", 1)[1].strip()
                if ver:
                    installed[n.lower()] = ver
        rows = []
        for name, current in sorted(installed.items()):
            latest = self._latest(name)
            if not latest:
                continue
            outdated = latest != current and self._is_newer(latest, current)
            rows.append({"name": name, "current": current, "latest": latest, "outdated": outdated})
        return rows

    def _latest(self, name: str) -> str | None:
        try:
            req = urllib.request.Request(self.PYPI.format(name=name), headers={"User-Agent": "OpenComb/0.7"})
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode())
            return data.get("info", {}).get("version")
        except Exception:
            return None

    @staticmethod
    def _is_newer(latest: str, current: str) -> bool:
        def parts(v: str) -> list[int]:
            out = []
            for p in re.split(r"[^\d]+", v):
                if p.isdigit():
                    out.append(int(p))
            return out or [0]
        return parts(latest) > parts(current)


class ReportServer:
    def serve(self, directory: str | Path = ".", port: int = 8765, open_path: str = "") -> None:
        directory = Path(directory).resolve()
        os.chdir(directory)

        class Handler(http.server.SimpleHTTPRequestHandler):
            def log_message(self, fmt: str, *args: Any) -> None:
                sys.stderr.write("[serve] " + (fmt % args) + "\n")

        with socketserver.TCPServer(("", port), Handler) as httpd:
            url = f"http://127.0.0.1:{port}/{open_path.lstrip('/')}"
            print(f"Serving {directory} at {url}", flush=True)
            print("Ctrl+C to stop", flush=True)
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\nStopped.", flush=True)


class Watcher:
    def __init__(self, paths: list[str | Path], interval: float = 1.0):
        self.paths = [Path(p) for p in paths]
        self.interval = interval

    def _snapshot(self) -> dict[str, float]:
        snap: dict[str, float] = {}
        for p in self.paths:
            if p.is_file():
                try:
                    snap[str(p.resolve())] = p.stat().st_mtime
                except OSError:
                    pass
            elif p.is_dir():
                for f in iter_files(p, exts=None):
                    try:
                        snap[str(f.resolve())] = f.stat().st_mtime
                    except OSError:
                        pass
        return snap

    def run(self, on_change: Callable[[], None], *, once_immediately: bool = True) -> None:
        if once_immediately:
            on_change()
        prev = self._snapshot()
        print(f"[watch] watching {len(self.paths)} path(s), interval={self.interval}s", flush=True)
        try:
            while True:
                time.sleep(self.interval)
                cur = self._snapshot()
                if cur != prev:
                    print("[watch] change detected – running…", flush=True)
                    on_change()
                    prev = cur
        except KeyboardInterrupt:
            print("\n[watch] stopped", flush=True)
