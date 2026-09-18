"""Extra developer tools: git summary, secrets scan, http, bench, jsonq, ports."""

from __future__ import annotations

import json
import os
import re
import socket
import subprocess
import time
import urllib.request
from pathlib import Path
from typing import Any

import yaml

SECRET_PATTERNS = [
    (re.compile(r"(?i)(api[_-]?key|apikey|secret|token|password|passwd)\s*[=:]\s*['\"][^'\"]{8,}['\"]"), "credential assignment"),
    (re.compile(r"AKIA[0-9A-Z]{16}"), "AWS access key id"),
    (re.compile(r"-----BEGIN (RSA |OPENSSH |EC )?PRIVATE KEY-----"), "private key block"),
    (re.compile(r"ghp_[A-Za-z0-9]{20,}"), "GitHub PAT"),
    (re.compile(r"sk-[A-Za-z0-9]{20,}"), "OpenAI-style key"),
    (re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"), "Slack token"),
]

SKIP = {".git", "__pycache__", ".venv", "venv", "node_modules", "dist", "build", ".mypy_cache", ".ruff_cache"}


class GitHelper:
    def status(self, root: Path | None = None) -> dict[str, Any]:
        root = root or Path.cwd()

        def run(args: list[str]) -> str:
            r = subprocess.run(["git", *args], cwd=str(root), capture_output=True, text=True)
            return r.stdout.strip() if r.returncode == 0 else ""

        return {
            "branch": run(["rev-parse", "--abbrev-ref", "HEAD"]),
            "commit": run(["rev-parse", "--short", "HEAD"]),
            "status": run(["status", "-sb"]),
            "dirty": bool(run(["status", "--porcelain"])),
            "remotes": run(["remote", "-v"]),
            "log": run(["log", "-5", "--oneline"]),
        }


class SecretScanner:
    def scan(self, root: Path | None = None, max_hits: int = 100) -> list[dict[str, Any]]:
        root = (root or Path.cwd()).resolve()
        hits: list[dict[str, Any]] = []
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in SKIP]
            for name in filenames:
                if name.endswith((".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".pdf", ".zip", ".whl")):
                    continue
                path = Path(dirpath) / name
                try:
                    text = path.read_text(encoding="utf-8", errors="ignore")
                except OSError:
                    continue
                for i, line in enumerate(text.splitlines(), 1):
                    for cre, label in SECRET_PATTERNS:
                        if cre.search(line):
                            hits.append({"file": str(path.relative_to(root)), "line": i, "kind": label, "text": line.strip()[:120]})
                            if len(hits) >= max_hits:
                                return hits
        return hits


class HttpClient:
    def get(self, url: str, timeout: float = 15.0) -> dict[str, Any]:
        req = urllib.request.Request(url, headers={"User-Agent": "OpenComb/0.10"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read()
            ctype = resp.headers.get("Content-Type", "")
            text = body.decode("utf-8", errors="replace")
            data: Any = text
            if "json" in ctype:
                try:
                    data = json.loads(text)
                except json.JSONDecodeError:
                    pass
            return {"status": resp.status, "headers": dict(resp.headers.items()), "body": data, "bytes": len(body)}


class Bench:
    def run(self, command: str, runs: int = 3) -> dict[str, Any]:
        times: list[float] = []
        codes: list[int] = []
        for _ in range(max(1, runs)):
            start = time.perf_counter()
            r = subprocess.run(command, shell=True)
            times.append(time.perf_counter() - start)
            codes.append(r.returncode)
        return {"command": command, "runs": runs, "times": times, "mean": sum(times) / len(times), "min": min(times), "max": max(times), "codes": codes}


class JsonYamlQuery:
    def load(self, path: Path) -> Any:
        text = path.read_text(encoding="utf-8")
        if path.suffix.lower() in {".yaml", ".yml"}:
            return yaml.safe_load(text)
        return json.loads(text)

    def get(self, data: Any, path: str) -> Any:
        cur = data
        if not path or path == ".":
            return cur
        for part in path.split("."):
            if isinstance(cur, list):
                cur = cur[int(part)]
            elif isinstance(cur, dict):
                cur = cur[part]
            else:
                raise KeyError(path)
        return cur


class PortProbe:
    def check(self, host: str = "127.0.0.1", ports: list[int] | None = None) -> list[dict[str, Any]]:
        ports = ports or [22, 80, 443, 3000, 5000, 5432, 6379, 8000, 8080, 8765, 27017]
        out = []
        for p in ports:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.25)
            try:
                open_ = s.connect_ex((host, p)) == 0
            except OSError:
                open_ = False
            finally:
                s.close()
            out.append({"port": p, "open": open_})
        return out
