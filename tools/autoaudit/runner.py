"""Opt-in, read-only capture auditing companion for preapproved Wi-Fi labs.

No live radio controls, target discovery, deauthentication or Bettercap commands.
Runs on a separate Linux/WSL GPU host against locally mirrored capture files.
"""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import re
import sqlite3
import subprocess
import tempfile
import time
from pathlib import Path

CAPTURE_EXT = {".pcapng", ".pcap", ".cap"}
CAPTURE_MAGIC = {
    bytes.fromhex("0a0d0d0a"),  # pcapng
    bytes.fromhex("d4c3b2a1"), bytes.fromhex("a1b2c3d4"),
    bytes.fromhex("4d3cb2a1"), bytes.fromhex("a1b23c4d"),
}
MAC = re.compile(r"^(?:[0-9a-f]{2}:){5}[0-9a-f]{2}$")
HEX12 = re.compile(r"^[0-9a-fA-F]{12}$")
MAX_CAPTURE_BYTES = 96 * 1024 * 1024


def load_config(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    root = path.resolve().parent
    for key in ("inbox", "workdir", "wordlist"):
        if data.get(key):
            p = Path(data[key]).expanduser()
            data[key] = str(p if p.is_absolute() else root / p)
    raw = data.get("approved_bssids", [])
    if not isinstance(raw, list) or not all(isinstance(v, str) and MAC.fullmatch(v.lower()) for v in raw):
        raise ValueError("approved_bssids must contain valid colon-delimited MAC addresses")
    data["approved_bssids"] = frozenset(v.lower().replace(":", "") for v in raw)
    if not data.get("acknowledged_authorized", False) or not data["approved_bssids"]:
        raise ValueError("explicit authorization acknowledgment and nonempty BSSID allowlist required")
    if data.get("auto_run_hashcat", False) and not data.get("wordlist"):
        raise ValueError("auto_run_hashcat requires an explicit local wordlist")
    return data


def _db(path: Path) -> sqlite3.Connection:
    c = sqlite3.connect(str(path), timeout=30)
    c.execute("CREATE TABLE IF NOT EXISTS captures (digest TEXT PRIMARY KEY, status TEXT NOT NULL, eligible_count INTEGER NOT NULL, updated_at INTEGER NOT NULL)")
    c.commit()
    return c


def _digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _allowed_lines(path: Path, permitted: frozenset[str]) -> tuple[list[str], int]:
    filtered, seen = [], 0
    if not path.exists():
        return filtered, seen
    with path.open("r", encoding="ascii", errors="replace") as stream:
        for line in stream:
            if len(line) > 65536:
                continue
            parts = line.rstrip("\r\n").split("*")
            if len(parts) != 9 or parts[0] != "WPA" or parts[1] not in {"01", "02"} or not HEX12.fullmatch(parts[3]):
                continue
            seen += 1
            if parts[3].lower() in permitted:
                filtered.append(line.rstrip("\r\n") + "\n")
    return sorted(set(filtered)), seen


def _snapshot(c: sqlite3.Connection, workdir: Path) -> dict:
    counts = {status: count for status, count in c.execute("SELECT status, COUNT(*) FROM captures GROUP BY status")}
    recent = [{"id": digest[:12], "state": status, "eligible_hashes": count}
              for digest, status, count in c.execute(
                  "SELECT digest, status, eligible_count FROM captures ORDER BY updated_at DESC LIMIT 20")]
    state = {"updated_at": int(time.time()), "counts": counts, "recent": recent}
    tmp = workdir / ".status.json.tmp"
    tmp.write_text(json.dumps(state, indent=2), encoding="utf-8")
    os.chmod(tmp, 0o600)
    os.replace(tmp, workdir / "status.json")
    return state


def scan(cfg: dict) -> dict:
    inbox = Path(cfg["inbox"]).resolve()
    workdir = Path(cfg["workdir"]).resolve()
    if workdir == Path(workdir.anchor) or workdir == inbox:
        raise ValueError("workdir must be a dedicated directory separate from inbox")
    newly_created = not workdir.exists()
    workdir.mkdir(parents=True, exist_ok=True)
    if newly_created:
        os.chmod(workdir, 0o700)
    lock = workdir / ".worker.lock"
    with lock.open("w") as held:
        fcntl.flock(held.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        conn = _db(workdir / "audit.sqlite3")
        try:
            approved_dir = workdir / "approved"
            approved_dir.mkdir(exist_ok=True)
            os.chmod(approved_dir, 0o700)
            processed = 0
            if not inbox.is_dir():
                raise FileNotFoundError("capture inbox unavailable")
            for path in sorted(inbox.iterdir()):
                if processed >= int(cfg.get("max_per_scan", 3)):
                    break
                if path.is_symlink() or not path.is_file() or path.suffix.lower() not in CAPTURE_EXT:
                    continue
                stat = path.stat()
                if stat.st_size < 24 or stat.st_size > MAX_CAPTURE_BYTES:
                    continue
                if time.time() - stat.st_mtime < int(cfg.get("settle_seconds", 30)):
                    continue
                with path.open("rb") as f:
                    if f.read(4) not in CAPTURE_MAGIC:
                        continue
                fingerprint = _digest(path)
                old = conn.execute("SELECT status FROM captures WHERE digest=?", (fingerprint,)).fetchone()
                audit = bool(cfg.get("auto_run_hashcat", False))
                if old and (old[0] in {"audited", "no_usable_hash", "not_approved"} or
                            old[0] == "verified" and not audit):
                    continue
                processed += 1
                state, eligible_count = "conversion_error", 0
                output = approved_dir / (fingerprint + ".hc22000")
                try:
                    if not output.exists():
                        with tempfile.TemporaryDirectory(prefix="convert-", dir=workdir) as td:
                            raw = Path(td) / "raw.hc22000"
                            result = subprocess.run(
                                [cfg.get("converter", "hcxpcapngtool"), "-o", str(raw), str(path)],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                timeout=int(cfg.get("convert_timeout_seconds", 90)), check=False)
                            if result.returncode != 0 and not raw.exists():
                                raise RuntimeError("converter failed")
                            selected, seen = _allowed_lines(raw, cfg["approved_bssids"])
                            if selected:
                                output.write_text("".join(selected), encoding="ascii")
                                os.chmod(output, 0o600)
                                eligible_count = len(selected)
                                state = "verified"
                            else:
                                state = "not_approved" if seen else "no_usable_hash"
                    else:
                        selected, _ = _allowed_lines(output, cfg["approved_bssids"])
                        if selected:
                            eligible_count = len(selected)
                            state = "verified"
                        else:
                            state = "not_approved"
                            output.unlink()
                    if state == "verified" and audit:
                        wordlist = Path(cfg["wordlist"])
                        if not wordlist.is_file():
                            raise FileNotFoundError("configured wordlist unavailable")
                        result = subprocess.run(
                            [cfg.get("hashcat", "hashcat"), "-m", "22000", "-a", "0",
                             "--quiet", "--session", "beast-" + fingerprint[:16],
                             "--potfile-path", str(workdir / "audit.potfile"),
                             str(output), str(wordlist)],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                            timeout=int(cfg.get("hashcat_timeout_seconds", 3600)), check=False,
                            cwd=str(workdir))
                        if result.returncode in (0, 1):
                            state = "audited"
                        else:
                            state = "audit_error"
                except (OSError, RuntimeError, subprocess.TimeoutExpired):
                    state = "audit_error" if eligible_count else "conversion_error"
                conn.execute("INSERT INTO captures(digest, status, eligible_count, updated_at) VALUES (?, ?, ?, ?) "
                             "ON CONFLICT(digest) DO UPDATE SET status=excluded.status, "
                             "eligible_count=excluded.eligible_count, updated_at=excluded.updated_at",
                             (fingerprint, state, eligible_count, int(time.time())))
                conn.commit()
            return _snapshot(conn, workdir)
        finally:
            conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Read-only, approved-network capture audit companion")
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()
    os.umask(0o077)
    report = scan(load_config(args.config))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
