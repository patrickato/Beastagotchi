#!/usr/bin/env python3
"""Focused physical NEXT-button touch probe for Beastagotchi v0.19.

This tool records Linux evdev contact events (including BTN_TOUCH and absolute
coordinates) alongside a tiny operator annotation stream. It is intentionally
read-only with respect to Beastagotchi calibration/preferences. The resulting
bundle is designed to distinguish:

* a physical press that never produced BTN_TOUCH,
* a recognized touch whose calibrated coordinate missed the intended region,
* and a recognized touch that reached the UI but did not produce the expected
  navigation transition.

Run this during a protected Atlas acceptance session. The script writes a
self-contained .tar.gz under /home/pi that can be copied off the Pi for review.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tarfile
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

OUT_ROOT = Path("/home/pi")
DEFAULT_CONFIG = Path("/opt/beast-ui/config/touch.json")
DEFAULT_RUNTIME = Path("/run/beastagotchi")


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def run(cmd: list[str]) -> dict[str, Any]:
    try:
        p = subprocess.run(cmd, text=True, capture_output=True, check=False, timeout=15)
        return {"cmd": cmd, "returncode": p.returncode, "stdout": p.stdout, "stderr": p.stderr}
    except Exception as exc:  # pragma: no cover - target-hardware diagnostic
        return {"cmd": cmd, "error": repr(exc)}


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text())
    except Exception as exc:
        return {"_error": repr(exc), "_path": str(path)}


def discover_touch_device() -> str | None:
    """Prefer the touchscreen node by /proc/bus/input/devices metadata."""
    proc = Path("/proc/bus/input/devices")
    if not proc.exists():
        return None
    text = proc.read_text(errors="replace")
    blocks = re.split(r"\n\s*\n", text)
    preferred = []
    fallback = []
    for block in blocks:
        handlers = re.search(r"^H: Handlers=(.+)$", block, re.M)
        name = re.search(r'^N: Name="([^"]+)"$', block, re.M)
        if not handlers:
            continue
        events = re.findall(r"\bevent\d+\b", handlers.group(1))
        if not events:
            continue
        node = f"/dev/input/{events[0]}"
        title = (name.group(1) if name else "").lower()
        row = (node, block)
        if any(x in title for x in ("ads7846", "xpt2046", "touch")):
            preferred.append(row)
        elif "touch" in handlers.group(1).lower():
            fallback.append(row)
    rows = preferred or fallback
    return rows[0][0] if rows else None


def find_evtest() -> str | None:
    return shutil.which("evtest")


@dataclass
class OperatorTap:
    seq: int
    ts: str
    target: str
    pressure_class: str
    expected: str
    observed: str
    note: str = ""


def prompt_taps(log_path: Path) -> list[OperatorTap]:
    print("\nFocused NEXT test")
    print("---------------")
    print("For each physical tap, press ENTER immediately after the tap, then record whether")
    print("the UI advanced. Keep the stylus centered on the same visual NEXT target.")
    print("Planned order: 3 light, 4 normal, 3 firm.\n")
    target = input("Target label/location (example: Themes > Synthwave > page 3 NEXT): ").strip()
    expected = input("Expected action [advance]: ").strip() or "advance"
    rows: list[OperatorTap] = []
    classes = ["light"] * 3 + ["normal"] * 4 + ["firm"] * 3
    for idx, cls in enumerate(classes, 1):
        input(f"Tap {idx}/10 ({cls}) now, then press ENTER here... ")
        observed = input("Did it advance/register? [y/n/other]: ").strip().lower()
        if observed in {"y", "yes"}:
            observed = "registered"
        elif observed in {"n", "no"}:
            observed = "missed"
        note = input("Optional note (ENTER for none): ").strip()
        row = OperatorTap(idx, utcnow(), target, cls, expected, observed, note)
        rows.append(row)
        with log_path.open("a") as fh:
            fh.write(json.dumps(asdict(row), sort_keys=True) + "\n")
    return rows


def summarize(rows: list[OperatorTap]) -> dict[str, Any]:
    out: dict[str, Any] = {"total": len(rows), "by_pressure": {}}
    for cls in ("light", "normal", "firm"):
        subset = [r for r in rows if r.pressure_class == cls]
        ok = sum(r.observed == "registered" for r in subset)
        out["by_pressure"][cls] = {"registered": ok, "attempted": len(subset)}
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", help="evdev node; auto-detected when omitted")
    ap.add_argument("--name", default="bad-next", help="short target name for bundle metadata")
    ap.add_argument("--seconds", type=int, default=240, help="maximum raw capture duration")
    args = ap.parse_args()

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    work = OUT_ROOT / f"beast-next-touch-probe-{stamp}"
    work.mkdir(parents=True, exist_ok=False)

    device = args.device or discover_touch_device()
    evtest = find_evtest()
    meta: dict[str, Any] = {
        "created_at": utcnow(),
        "probe_version": 1,
        "name": args.name,
        "device": device,
        "evtest": evtest,
        "host": platform.node(),
        "kernel": platform.release(),
        "python": sys.version,
        "uid": os.getuid(),
    }
    (work / "metadata.json").write_text(json.dumps(meta, indent=2) + "\n")

    # Static context useful for matching physical events to Beast's interpretation.
    (work / "proc-input-devices.txt").write_text(Path("/proc/bus/input/devices").read_text(errors="replace") if Path("/proc/bus/input/devices").exists() else "missing\n")
    (work / "touch-config.json").write_text(json.dumps(load_json(DEFAULT_CONFIG), indent=2) + "\n")
    (work / "systemctl-beast-core.json").write_text(json.dumps(run(["systemctl", "status", "beast-core", "--no-pager", "-l"]), indent=2) + "\n")
    (work / "systemctl-beast-ui.json").write_text(json.dumps(run(["systemctl", "status", "beast-ui", "--no-pager", "-l"]), indent=2) + "\n")
    (work / "journal-tail.json").write_text(json.dumps(run(["journalctl", "-u", "beast-ui", "-n", "250", "--no-pager", "-o", "short-precise"]), indent=2) + "\n")

    if DEFAULT_RUNTIME.exists():
        listing = []
        for p in sorted(DEFAULT_RUNTIME.rglob("*")):
            if p.is_file() and p.stat().st_size <= 2_000_000:
                listing.append(str(p))
        (work / "runtime-files.txt").write_text("\n".join(listing) + "\n")

    raw_file = work / "evtest-raw.txt"
    proc = None
    if device and evtest:
        raw_fh = raw_file.open("w")
        proc = subprocess.Popen([evtest, "--grab", device], stdout=raw_fh, stderr=subprocess.STDOUT, text=True)
        time.sleep(0.4)
        print(f"Capturing raw touch events from {device} (PID {proc.pid}).")
    else:
        raw_file.write_text("Raw evdev capture unavailable: evtest or touchscreen device not found.\n")
        print("WARNING: raw evdev capture unavailable; operator annotations will still be bundled.")

    try:
        rows = prompt_taps(work / "operator-taps.jsonl")
    finally:
        if proc is not None:
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill()

    summary = summarize(rows)
    summary["finished_at"] = utcnow()
    (work / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")

    # Capture journal after the taps so navigation/input messages line up with raw timestamps.
    (work / "journal-after.json").write_text(json.dumps(run(["journalctl", "-u", "beast-ui", "--since", "-10 minutes", "--no-pager", "-o", "short-precise"]), indent=2) + "\n")

    bundle = OUT_ROOT / f"beast-next-touch-probe-{stamp}.tar.gz"
    with tarfile.open(bundle, "w:gz") as tf:
        tf.add(work, arcname=work.name)

    print("\nRESULT")
    for cls, data in summary["by_pressure"].items():
        print(f"  {cls:6s}: {data['registered']}/{data['attempted']} registered")
    print(f"\nBundle ready: {bundle}")
    print("Copy that .tar.gz to your PC and upload it for analysis.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
