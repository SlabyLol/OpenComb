"""OpenComb Problem Scanner – plain Python source (no encoding).

Finds issues that slow down or break a machine. GUI + CLI + zombie helpers.
"""
from __future__ import annotations

import json
import os
import platform
import shutil
import socket
import subprocess
import sys
import time
from collections import Counter
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Callable, Optional

SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
ProgressCb = Callable[[str, float], None]


@dataclass
class Finding:
    severity: str
    category: str
    title: str
    detail: str
    suggestion: str = ""
    path: str = ""
    metric: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ScanReport:
    host: str = ""
    platform: str = ""
    started_at: float = 0.0
    finished_at: float = 0.0
    findings: list = field(default_factory=list)

    def sorted_findings(self) -> list:
        return sorted(self.findings, key=lambda f: SEVERITY_ORDER.get(f.severity, 99))

    def to_dict(self) -> dict[str, Any]:
        return {
            "host": self.host,
            "platform": self.platform,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "findings": [f.to_dict() for f in self.findings],
        }


def _home() -> Path:
    return Path.home()


def _safe_run(cmd: list, timeout: float = 8.0):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=False)
        return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()
    except FileNotFoundError:
        return 127, "", "not found"
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"
    except Exception as e:
        return 1, "", str(e)


def _dir_size_mb(path: Path, max_files: int = 50000) -> float:
    total = 0
    n = 0
    try:
        for root, dirs, files in os.walk(path):
            for name in files:
                try:
                    total += (Path(root) / name).stat().st_size
                except OSError:
                    pass
                n += 1
                if n >= max_files:
                    return total / (1024 * 1024)
    except OSError:
        pass
    return total / (1024 * 1024)


def _human_mb(mb: float) -> str:
    if mb >= 1024:
        return f"{mb / 1024:.1f} GB"
    return f"{mb:.0f} MB"


def scan_load(report: ScanReport) -> None:
    try:
        load1, load5, load15 = os.getloadavg()
        cpus = os.cpu_count() or 1
        if load1 > cpus * 2:
            report.findings.append(Finding(
                severity="high", category="System", title="High system load",
                detail=f"load1={load1:.2f} (cpus={cpus})",
                suggestion="Check top processes; close heavy apps.", metric=str(load1)))
        elif load1 > cpus:
            report.findings.append(Finding(
                severity="medium", category="System", title="Elevated system load",
                detail=f"load1={load1:.2f} (cpus={cpus})",
                suggestion="Monitor CPU usage.", metric=str(load1)))
    except OSError:
        pass


def scan_memory(report: ScanReport) -> None:
    code, out, _ = _safe_run(["free", "-m"])
    if code != 0 or not out:
        return
    for line in out.splitlines():
        if line.lower().startswith("mem:"):
            parts = line.split()
            if len(parts) >= 3:
                try:
                    total, used = int(parts[1]), int(parts[2])
                    pct = (used / total * 100) if total else 0
                    if pct >= 90:
                        report.findings.append(Finding(
                            severity="critical", category="Memory", title="Memory almost full",
                            detail=f"{used}/{total} MB ({pct:.0f}%)",
                            suggestion="Close apps or add swap/RAM.", metric=f"{pct:.0f}%"))
                    elif pct >= 80:
                        report.findings.append(Finding(
                            severity="high", category="Memory", title="High memory usage",
                            detail=f"{used}/{total} MB ({pct:.0f}%)",
                            suggestion="Review memory-heavy processes.", metric=f"{pct:.0f}%"))
                except ValueError:
                    pass


def scan_disk(report: ScanReport) -> None:
    code, out, _ = _safe_run(["df", "-h", "/"])
    if code != 0:
        return
    lines = out.splitlines()
    if len(lines) < 2:
        return
    parts = lines[-1].split()
    if len(parts) >= 5:
        try:
            pct = int(parts[4].rstrip("%"))
            if pct >= 95:
                report.findings.append(Finding(
                    severity="critical", category="Disk", title="Root disk almost full",
                    detail=f"{parts[2]} used of {parts[1]} ({pct}%)",
                    suggestion="Free space: clear caches, old logs, Docker images.", metric=f"{pct}%"))
            elif pct >= 85:
                report.findings.append(Finding(
                    severity="high", category="Disk", title="Root disk filling up",
                    detail=f"{parts[2]} used of {parts[1]} ({pct}%)",
                    suggestion="Clean temp files and package caches.", metric=f"{pct}%"))
        except ValueError:
            pass


def run_zombie_check():
    """Return list of zombie processes with parent info."""
    code, out, _ = _safe_run(["ps", "-eo", "pid,ppid,stat,comm,args"], timeout=6.0)
    if code != 0 or not out:
        return []
    zombies = []
    pid_comm = {}
    for line in out.splitlines()[1:]:
        parts = line.split(None, 4)
        if len(parts) < 4:
            continue
        pid, ppid, stat, comm = parts[0], parts[1], parts[2], parts[3]
        pid_comm[pid] = comm
        if "Z" in stat:
            zombies.append({"pid": pid, "ppid": ppid, "stat": stat, "comm": comm, "parent_comm": ""})
    for z in zombies:
        z["parent_comm"] = pid_comm.get(z["ppid"], "?")
    return zombies


def scan_zombies(report: ScanReport) -> None:
    zombies = run_zombie_check()
    if not zombies:
        return
    parents = Counter((z["ppid"], z["parent_comm"]) for z in zombies)
    detail = f"{len(zombies)} zombie(s). Parents: " + ", ".join(
        f"{p}:{c}" for (_, p), c in parents.most_common(5))
    report.findings.append(Finding(
        severity="high" if len(zombies) >= 5 else "medium",
        category="Processes", title="Zombie processes detected",
        detail=detail,
        suggestion="Restart or kill the parent process so zombies can be reaped.",
        metric=str(len(zombies))))


def scan_temp_cache(report: ScanReport) -> None:
    for p in [Path("/tmp"), _home() / ".cache", Path("/var/tmp")]:
        if not p.is_dir():
            continue
        mb = _dir_size_mb(p, max_files=20000)
        if mb >= 5000:
            report.findings.append(Finding(
                severity="high", category="Disk", title=f"Large cache/temp: {p}",
                detail=_human_mb(mb), suggestion=f"Review and clean {p}",
                path=str(p), metric=_human_mb(mb)))
        elif mb >= 1500:
            report.findings.append(Finding(
                severity="medium", category="Disk", title=f"Growing cache/temp: {p}",
                detail=_human_mb(mb), suggestion=f"Consider cleaning old files in {p}",
                path=str(p), metric=_human_mb(mb)))


def scan_docker(report: ScanReport) -> None:
    code, out, _ = _safe_run(["docker", "system", "df"])
    if code != 0:
        return
    report.findings.append(Finding(
        severity="info", category="Docker", title="Docker present",
        detail=(out[:200] if out else "docker available"),
        suggestion="Run: docker system prune (carefully) to reclaim space."))


def scan_python_env(report: ScanReport) -> None:
    report.findings.append(Finding(
        severity="info", category="Python", title="Python environment",
        detail=f"{sys.version.split()[0]} at {sys.executable}",
        suggestion="Use virtual environments per project."))


SCAN_STEPS = [
    ("System load", scan_load),
    ("Memory", scan_memory),
    ("Disk", scan_disk),
    ("Zombie processes", scan_zombies),
    ("Temp & cache", scan_temp_cache),
    ("Docker", scan_docker),
    ("Python env", scan_python_env),
]


def run_scan(progress=None) -> ScanReport:
    report = ScanReport(
        host=socket.gethostname(),
        platform=f"{platform.system()} {platform.release()}",
        started_at=time.time(),
    )
    total = len(SCAN_STEPS)
    for i, (label, fn) in enumerate(SCAN_STEPS):
        if progress:
            progress(label, (i / total) * 100)
        try:
            fn(report)
        except Exception as e:
            report.findings.append(Finding(
                severity="info", category="Scanner",
                title=f"Check failed: {label}", detail=str(e)[:200]))
    report.finished_at = time.time()
    if progress:
        progress("Done", 100.0)
    return report


PROTECTED_PREFIXES = (
    "/", "/bin", "/boot", "/dev", "/etc", "/lib", "/lib64", "/proc",
    "/root", "/run", "/sbin", "/sys", "/usr", "/var",
)


def _is_protected(path: Path) -> bool:
    try:
        r = path.resolve()
    except OSError:
        r = path
    s = str(r)
    if s == "/" or s == str(_home()):
        return True
    return s in PROTECTED_PREFIXES


def list_shoot_targets(folder: Path, include_dirs: bool = True):
    folder = folder.resolve()
    targets = []
    for root, dirs, files in os.walk(folder, topdown=False):
        rp = Path(root)
        for name in files:
            targets.append(rp / name)
        if include_dirs and rp != folder:
            targets.append(rp)
    return targets


def shoot_folder(folder, *, confirm=True, dry_run=False, include_dirs=True, force=False, yes=False):
    folder = Path(folder).expanduser().resolve()
    if not folder.is_dir():
        raise NotADirectoryError(str(folder))
    if _is_protected(folder) and not force:
        raise PermissionError(f"Protected path: {folder}")
    targets = list_shoot_targets(folder, include_dirs=include_dirs)
    if dry_run:
        return {"deleted": 0, "errors": [], "message": f"dry-run: {len(targets)} targets",
                "targets": [str(t) for t in targets[:50]]}
    errors = []
    deleted = 0
    for p in targets:
        try:
            if p.is_symlink() or p.is_file():
                p.unlink(missing_ok=True)
                deleted += 1
            elif p.is_dir():
                shutil.rmtree(p, ignore_errors=True)
                deleted += 1
        except OSError as e:
            errors.append(f"{p}: {e}")
    return {"deleted": deleted, "errors": errors, "message": f"deleted {deleted} item(s)"}


def report_to_text(report: ScanReport) -> str:
    lines = [
        f"OpenComb Problem Scanner — {report.host}",
        f"Platform: {report.platform}",
        f"Findings: {len(report.findings)}",
        "",
    ]
    for f in report.sorted_findings():
        lines.append(f"[{f.severity.upper()}] {f.category}: {f.title}")
        lines.append(f"  {f.detail}")
        if f.suggestion:
            lines.append(f"  → {f.suggestion}")
        lines.append("")
    return "\n".join(lines)


def report_to_json(report: ScanReport) -> str:
    return json.dumps(report.to_dict(), indent=2)


def main_cli(*, json_out=False, output=None) -> int:
    report = run_scan()
    text = report_to_json(report) if json_out else report_to_text(report)
    if output:
        Path(output).write_text(text, encoding="utf-8")
        print(f"Wrote {output}")
    else:
        print(text)
    crit = sum(1 for f in report.findings if f.severity in ("critical", "high"))
    return 1 if crit else 0


def run_check_loop(*, watch=False, zombies_only=False, json_out=False, output=None, interval=5.0) -> int:
    if zombies_only:
        z = run_zombie_check()
        print(json.dumps(z, indent=2) if json_out else f"Zombies: {len(z)}")
        for item in z:
            print(f"  PID {item['pid']} parent={item['parent_comm']} ({item['ppid']})")
        return 0
    return main_cli(json_out=json_out, output=output)


def launch_gui() -> None:
    try:
        import tkinter as tk
        from tkinter import ttk, scrolledtext
    except ImportError as e:
        raise RuntimeError("tkinter not available — use: opencomb problemscanner --cli") from e

    root = tk.Tk()
    root.title("OpenComb Problem Scanner")
    root.geometry("720x520")
    txt = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Consolas", 10))
    txt.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

    def do_scan():
        txt.delete("1.0", tk.END)
        txt.insert(tk.END, "Scanning…\n")
        root.update()
        report = run_scan()
        txt.delete("1.0", tk.END)
        txt.insert(tk.END, report_to_text(report))

    bar = ttk.Frame(root)
    bar.pack(fill=tk.X, padx=8, pady=4)
    ttk.Button(bar, text="Scan", command=do_scan).pack(side=tk.LEFT)
    ttk.Button(bar, text="Quit", command=root.destroy).pack(side=tk.RIGHT)
    root.mainloop()
