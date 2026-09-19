"""OpenComb Connect (occ) – interactive SSH connector console."""

from __future__ import annotations

import getpass
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table

console = Console()

PROFILES_DIR = Path.home() / ".opencomb" / "occ_profiles"


def parse_target_string(s: str) -> tuple[str, str, int | None]:
    """Parse user@host, user@host:port, host, host:port."""
    s = s.strip()
    user = ""
    port: int | None = None
    if "@" in s:
        user, rest = s.split("@", 1)
        user = user.strip()
        s = rest.strip()
    if s.startswith("[") and "]" in s:
        bracket, _, maybe_port = s[1:].partition("]")
        host = bracket
        if maybe_port.startswith(":"):
            try:
                port = int(maybe_port[1:])
            except ValueError:
                port = None
        return user, host, port
    if s.count(":") == 1:
        host, _, p = s.partition(":")
        try:
            return user, host.strip(), int(p)
        except ValueError:
            pass
    return user, s, port


@dataclass
class SSHTarget:
    host: str
    user: str = ""
    port: int = 22
    identity: str = ""
    password: str = ""
    extra: list[str] = field(default_factory=list)
    name: str = ""

    def dest(self) -> str:
        return f"{self.user}@{self.host}" if self.user else self.host

    def ssh_argv(self) -> list[str]:
        cmd = ["ssh"]
        if self.port and self.port != 22:
            cmd.extend(["-p", str(self.port)])
        if self.identity:
            cmd.extend(["-i", self.identity])
        cmd.extend(self.extra)
        cmd.append(self.dest())
        return cmd

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name or self.host,
            "host": self.host,
            "user": self.user,
            "port": self.port,
            "identity": self.identity,
            "extra": self.extra,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "SSHTarget":
        return cls(
            host=str(d.get("host", "")),
            user=str(d.get("user", "")),
            port=int(d.get("port") or 22),
            identity=str(d.get("identity") or ""),
            password="",
            extra=list(d.get("extra") or []),
            name=str(d.get("name") or ""),
        )


def _ensure_ssh() -> None:
    if not shutil.which("ssh"):
        console.print("[red]ssh client not found on PATH. Install OpenSSH.[/]")
        raise SystemExit(1)


def prompt_target(
    *,
    host: str | None = None,
    user: str | None = None,
    port: int | None = None,
    identity: str | None = None,
) -> SSHTarget:
    console.print(
        Panel.fit(
            "[bold bright_red]OpenComb Connect (occ)[/]\n"
            "[dim]Style:[/] [cyan]user@host[/]  or  [cyan]user@host:port[/]",
            border_style="bright_red",
        )
    )
    if not host and user is None:
        line = Prompt.ask("[cyan]Target[/] (user@host or user@host:port)")
        if line.strip():
            u, h, p = parse_target_string(line)
            user = user or u or None
            host = host or h or None
            if port is None and p is not None:
                port = p
    h = host or Prompt.ask("[cyan]Host[/]")
    while not str(h).strip():
        h = Prompt.ask("[cyan]Host[/] (required)")
    u = user if user is not None else Prompt.ask("[cyan]User[/]", default=os.environ.get("USER", ""))
    if port is None:
        try:
            p = int(Prompt.ask("[cyan]Port[/]", default="22"))
        except ValueError:
            p = 22
    else:
        p = port
    ident = identity if identity is not None else Prompt.ask("[cyan]Identity file[/] (optional)", default="")
    if ident:
        ident = str(Path(ident).expanduser())
    force_pw = os.environ.get("OPENCOMB_OCC_ASK_PASSWORD") == "1"
    default_pw = "y" if force_pw or not ident else "n"
    need_pw = force_pw or Prompt.ask("[cyan]Password needed?[/] (y/n)", default=default_pw).strip().lower() in {
        "y", "yes", "j", "ja", "1", "true",
    }
    password = getpass.getpass("Password (hidden): ") if need_pw else ""
    extra_s = Prompt.ask("[cyan]Extra ssh flags[/] (optional)", default="")
    extra = extra_s.split() if extra_s.strip() else []
    name = Prompt.ask("[cyan]Profile name[/] (optional)", default="")
    return SSHTarget(
        host=str(h).strip(), user=str(u).strip(), port=int(p),
        identity=str(ident).strip(), password=password, extra=extra, name=name.strip(),
    )


def save_profile(target: SSHTarget) -> Path:
    import json
    PROFILES_DIR.mkdir(parents=True, exist_ok=True)
    name = target.name or target.host
    safe = "".join(c if c.isalnum() or c in "-_." else "_" for c in name)
    path = PROFILES_DIR / f"{safe}.json"
    path.write_text(json.dumps(target.to_dict(), indent=2), encoding="utf-8")
    return path


def list_profiles() -> list[SSHTarget]:
    import json
    if not PROFILES_DIR.exists():
        return []
    out: list[SSHTarget] = []
    for f in sorted(PROFILES_DIR.glob("*.json")):
        try:
            out.append(SSHTarget.from_dict(json.loads(f.read_text(encoding="utf-8"))))
        except Exception:
            continue
    return out


def load_profile(name: str) -> SSHTarget | None:
    for t in list_profiles():
        if t.name == name or t.host == name:
            return t
    path = PROFILES_DIR / f"{name}.json"
    if path.exists():
        import json
        return SSHTarget.from_dict(json.loads(path.read_text(encoding="utf-8")))
    return None


def _write_askpass(password: str) -> Path:
    import tempfile, stat
    fd, name = tempfile.mkstemp(prefix="occ_askpass_", suffix=".sh")
    os.close(fd)
    path = Path(name)
    path.write_text("#!/bin/sh\necho \"%s\"\n" % password.replace("\\", "\\\\").replace('"', '\\"').replace("$", "\\$").replace("`", "\\`"), encoding="utf-8")
    path.chmod(stat.S_IRWXU)
    return path


def connect(target: SSHTarget, *, dry_run: bool = False) -> int:
    _ensure_ssh()
    argv = target.ssh_argv()
    if target.password:
        argv = argv[:-1] + ["-o", "PreferredAuthentications=publickey,password,keyboard-interactive", "-o", "NumberOfPasswordPrompts=1", argv[-1]]
    console.print(f"[dim]$ {' '.join(argv)}{'  (password)' if target.password else ''}[/]")
    if dry_run:
        return 0
    console.print(f"[green]Connecting[/] to [cyan]{target.dest()}[/] port [cyan]{target.port}[/] …")
    askpass_path = None
    env = os.environ.copy()
    if target.password:
        if shutil.which("sshpass"):
            argv = ["sshpass", "-p", target.password] + argv
        else:
            askpass_path = _write_askpass(target.password)
            env["SSH_ASKPASS"] = str(askpass_path)
            env["SSH_ASKPASS_REQUIRE"] = "force"
            env.setdefault("DISPLAY", ":0")
    try:
        return subprocess.call(argv, env=env)
    finally:
        if askpass_path and askpass_path.exists():
            try:
                askpass_path.unlink()
            except OSError:
                pass


def run_interactive(
    *,
    host: str | None = None,
    user: str | None = None,
    port: int | None = None,
    identity: str | None = None,
    profile: str | None = None,
    save: bool = False,
    dry_run: bool = False,
) -> None:
    if profile:
        t = load_profile(profile)
        if not t:
            console.print(f"[red]Profile not found:[/] {profile}")
            raise SystemExit(1)
    else:
        t = prompt_target(host=host, user=user, port=port, identity=identity)
    table = Table(title="Connection", border_style="bright_red")
    table.add_column("Field", style="cyan")
    table.add_column("Value")
    table.add_row("host", t.host)
    table.add_row("user", t.user or "(default)")
    table.add_row("port", str(t.port))
    table.add_row("identity", t.identity or "(agent/default)")
    console.print(table)
    if save or t.name:
        if not t.name:
            t.name = t.host
        console.print(f"[dim]Saved profile → {save_profile(t)}[/]")
    if not dry_run and not Confirm.ask("Connect now?", default=True):
        console.print("[yellow]Aborted[/]")
        return
    raise SystemExit(connect(t, dry_run=dry_run))


def show_profiles() -> None:
    rows = list_profiles()
    if not rows:
        console.print("[dim]No saved profiles in ~/.opencomb/occ_profiles/[/]")
        return
    table = Table(title="occ profiles", border_style="bright_red")
    table.add_column("Name", style="cyan")
    table.add_column("User@Host")
    table.add_column("Port")
    for t in rows:
        table.add_row(t.name or t.host, t.dest(), str(t.port))
    console.print(table)


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(prog="occ", description="OpenComb Connect – SSH (user@host)")
    parser.add_argument("target", nargs="?", help="user@host or user@host:port or profile")
    parser.add_argument("--host", "-H")
    parser.add_argument("--user", "-u")
    parser.add_argument("--port", "-p", type=int)
    parser.add_argument("--identity", "-i")
    parser.add_argument("--list", "-l", action="store_true")
    parser.add_argument("--save", "-s", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--password", "-P", action="store_true")
    args = parser.parse_args()
    if args.list:
        show_profiles()
        return
    if args.password:
        os.environ["OPENCOMB_OCC_ASK_PASSWORD"] = "1"
    host, user, port, profile = args.host, args.user, args.port, None
    if args.target:
        if "@" in args.target:
            u, h, p = parse_target_string(args.target)
            user = user or u or None
            host = host or h or None
            port = port if port is not None else p
        elif load_profile(args.target):
            profile = args.target
        else:
            host = host or args.target
    run_interactive(host=host, user=user, port=port, identity=args.identity, profile=profile, save=args.save, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
