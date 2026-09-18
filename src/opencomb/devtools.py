"""Developer tools: git, secrets, http, bench, jq, ports, clone, site."""

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
SKIP = {".git", "__pycache__", ".venv", "venv", "node_modules", "dist", "build"}


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
                if name.endswith((".png", ".jpg", ".zip", ".whl")):
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
        req = urllib.request.Request(url, headers={"User-Agent": "OpenComb/0.11"})
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
        times, codes = [], []
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
            cur = cur[int(part)] if isinstance(cur, list) else cur[part]
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


class GitClone:
    def clone(self, url: str, dest: str | Path | None = None, *, branch: str | None = None, depth: int | None = None, recursive: bool = False) -> Path:
        cmd = ["git", "clone"]
        if branch:
            cmd.extend(["--branch", branch, "--single-branch"])
        if depth:
            cmd.extend(["--depth", str(depth)])
        if recursive:
            cmd.append("--recurse-submodules")
        cmd.append(url)
        if dest:
            cmd.append(str(dest))
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError(r.stderr.strip() or r.stdout.strip() or "git clone failed")
        if dest:
            return Path(dest).resolve()
        name = url.rstrip("/").split("/")[-1]
        if name.endswith(".git"):
            name = name[:-4]
        return Path(name).resolve()


class SiteCloner:
    def __init__(self, user_agent: str = "OpenComb/0.11 (site-cloner)"):
        self.user_agent = user_agent

    def fetch(self, url: str, timeout: float = 30.0) -> tuple[bytes, str]:
        req = urllib.request.Request(url, headers={"User-Agent": self.user_agent})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read(), resp.headers.get("Content-Type", "application/octet-stream")

    def clone_page(self, url: str, out_dir: str | Path = "site_download", *, assets: bool = True, max_assets: int = 50, timeout: float = 30.0) -> Path:
        from html.parser import HTMLParser
        from urllib.parse import urljoin, urlparse

        out = Path(out_dir)
        out.mkdir(parents=True, exist_ok=True)
        data, ctype = self.fetch(url, timeout=timeout)
        parsed = urlparse(url)
        host = parsed.netloc
        main_name = "index.html"
        path = parsed.path.rstrip("/")
        if path and not path.endswith("/"):
            base = Path(path).name
            if "." in base:
                main_name = base
        (out / main_name).write_bytes(data)
        saved = [str(out / main_name)]
        if not assets or "html" not in ctype.lower():
            return out

        class LinkCollector(HTMLParser):
            def __init__(self):
                super().__init__()
                self.links: list[str] = []

            def handle_starttag(self, tag, attrs):
                ad = dict(attrs)
                for key in ("href", "src"):
                    if key in ad and ad[key]:
                        self.links.append(ad[key])

        parser = LinkCollector()
        try:
            parser.feed(data.decode("utf-8", errors="ignore"))
        except Exception:
            return out

        asset_dir = out / "assets"
        asset_dir.mkdir(exist_ok=True)
        count = 0
        seen: set[str] = set()
        for link in parser.links:
            if count >= max_assets:
                break
            full = urljoin(url, link)
            p = urlparse(full)
            if p.scheme not in ("http", "https") or (p.netloc and p.netloc != host):
                continue
            if full in seen:
                continue
            seen.add(full)
            lower = full.lower().split("?")[0]
            if not any(lower.endswith(ext) for ext in (".css", ".js", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".ico", ".woff", ".woff2", ".ttf", ".json")):
                if "/static/" not in lower and "/assets/" not in lower:
                    continue
            try:
                blob, _ = self.fetch(full, timeout=timeout)
                name = Path(p.path).name or f"asset_{count}"
                target = asset_dir / name
                if target.exists():
                    target = asset_dir / f"{count}_{name}"
                target.write_bytes(blob)
                saved.append(str(target))
                count += 1
            except Exception:
                continue
        (out / "download_report.txt").write_text(f"URL: {url}\nFiles: {len(saved)}\n" + "\n".join(saved), encoding="utf-8")
        return out
