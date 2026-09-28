#!/usr/bin/env python3
"""Focused physical NEXT-button touch probe for Beastagotchi v0.19.

Purpose
=======
Correlate what the operator physically does with what the Linux touchscreen
actually reports and what the Beast UI appears to do.  The probe is read-only:
it never changes touch calibration, Beast preferences, display ownership, or
Pwnagotchi state.

The probe runs two 10-tap blocks:
  1. a troublesome NEXT target;
  2. a known-good NEXT target used as a control.

Each block uses the same pressure pattern: 3 light, 4 normal, 3 firm taps.  The
operator arms each attempt immediately before touching the screen and records
whether the intended UI action happened.  Raw evdev traffic is captured in
parallel *without grabbing the device*, so Beast UI continues receiving the
same input.

The final /home/pi/beast-next-touch-probe-*.tar.gz contains raw events,
per-attempt timing/observations, parsed BTN_TOUCH contacts, current calibration,
selected Beast runtime evidence, service/journal context, a JSON analysis and a
human-readable report.
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
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

OUT_ROOT = Path("/home/pi")
TOUCH_CONFIG = Path("/opt/beast-ui/config/touch.json")
RUNTIME_ROOT = Path("/run/beastagotchi")
RUNTIME_HINTS = (
    "touch",
    "gesture",
    "telemetry",
    "render",
    "frame",
    "accept",
    "deployment",
    "provenance",
)
EVENT_RE = re.compile(
    r"Event: time (?P<ts>\d+(?:\.\d+)?), type \d+ \([^)]*\), "
    r"code \d+ \((?P<code>[^)]+)\), value (?P<value>-?\d+)"
)


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def epoch() -> float:
    return time.time()


def run(cmd: list[str], timeout: int = 15) -> dict[str, Any]:
    try:
        p = subprocess.run(cmd, text=True, capture_output=True, check=False, timeout=timeout)
        return {
            "cmd": cmd,
            "returncode": p.returncode,
            "stdout": p.stdout,
            "stderr": p.stderr,
        }
    except Exception as exc:  # pragma: no cover - target-hardware diagnostic
        return {"cmd": cmd, "error": repr(exc)}


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text())
    except Exception as exc:
        return {"_error": repr(exc), "_path": str(path)}


def discover_touch_device() -> str | None:
    """Prefer ADS7846/XPT2046/touch-named event nodes."""
    proc = Path("/proc/bus/input/devices")
    if not proc.exists():
        return None
    text = proc.read_text(errors="replace")
    blocks = re.split(r"\n\s*\n", text)
    preferred: list[str] = []
    fallback: list[str] = []
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
        if any(x in title for x in ("ads7846", "xpt2046", "touch")):
            preferred.append(node)
        elif "touch" in handlers.group(1).lower():
            fallback.append(node)
    rows = preferred or fallback
    return rows[0] if rows else None


@dataclass
class Attempt:
    seq: int
    block: str
    target: str
    pressure_class: str
    expected: str
    armed_at: str
    armed_epoch: float
    completed_at: str
    completed_epoch: float
    observed: str
    note: str = ""


@dataclass
class Contact:
    start_epoch: float
    end_epoch: float | None
    raw_x: int | None
    raw_y: int | None
    max_pressure: int | None


def normalize_observed(value: str) -> str:
    value = value.strip().lower()
    if value in {"y", "yes", "r", "registered", "worked", "ok"}:
        return "registered"
    if value in {"n", "no", "m", "missed", "failed", "fail"}:
        return "missed"
    return value or "unknown"


def run_block(block: str, start_seq: int, log_path: Path) -> list[Attempt]:
    print("\n" + "=" * 72)
    if block == "troublesome":
        print("BLOCK A — TROUBLESOME NEXT")
        print("Navigate to the NEXT control that has been unreliable.")
    else:
        print("BLOCK B — KNOWN-GOOD NEXT CONTROL")
        print("Navigate to a NEXT control that normally works on the first tap.")
    print("Aim at the visual center every time; do not hunt around the hitbox.")
    print("If a successful tap moves away from the target, navigate back to the")
    print("exact same target BEFORE arming the next attempt. Those navigation taps")
    print("are outside the armed timing window and will not contaminate the test.\n")

    target = input("Describe this exact target/location: ").strip() or f"{block}-next"
    expected = input("Expected action [advance]: ").strip() or "advance"
    input("When that exact target is visible and ready, press ENTER to begin... ")

    classes = ["light"] * 3 + ["normal"] * 4 + ["firm"] * 3
    rows: list[Attempt] = []
    for local_idx, cls in enumerate(classes, 1):
        seq = start_seq + local_idx - 1
        print(f"\n{block.upper()} {local_idx}/10 — {cls.upper()} pressure")
        input("Put the stylus just above the visual center. Press ENTER to ARM this attempt... ")
        arm_ep = epoch()
        arm_iso = utcnow()
        input("TAP NOW, then immediately press ENTER here after the physical tap... ")
        done_ep = epoch()
        done_iso = utcnow()
        observed = normalize_observed(input("Did the intended NEXT action register? [y/n]: "))
        note = input("Optional note (ENTER for none): ").strip()
        row = Attempt(
            seq=seq,
            block=block,
            target=target,
            pressure_class=cls,
            expected=expected,
            armed_at=arm_iso,
            armed_epoch=arm_ep,
            completed_at=done_iso,
            completed_epoch=done_ep,
            observed=observed,
            note=note,
        )
        rows.append(row)
        with log_path.open("a") as fh:
            fh.write(json.dumps(asdict(row), sort_keys=True) + "\n")

    return rows


def parse_contacts(path: Path) -> list[Contact]:
    """Parse BTN_TOUCH contact intervals plus most recent ABS_X/Y/pressure."""
    if not path.exists():
        return []
    last_x: int | None = None
    last_y: int | None = None
    pressure: int | None = None
    active: dict[str, Any] | None = None
    contacts: list[Contact] = []

    for line in path.read_text(errors="replace").splitlines():
        match = EVENT_RE.search(line)
        if not match:
            continue
        ts = float(match.group("ts"))
        code = match.group("code")
        value = int(match.group("value"))
        if code == "ABS_X":
            last_x = value
            if active is not None:
                active["raw_x"] = value
        elif code == "ABS_Y":
            last_y = value
            if active is not None:
                active["raw_y"] = value
        elif code in {"ABS_PRESSURE", "ABS_Z"}:
            pressure = value
            if active is not None:
                prior = active.get("max_pressure")
                active["max_pressure"] = value if prior is None else max(prior, value)
        elif code == "BTN_TOUCH" and value == 1 and active is None:
            active = {
                "start_epoch": ts,
                "end_epoch": None,
                "raw_x": last_x,
                "raw_y": last_y,
                "max_pressure": pressure,
            }
        elif code == "BTN_TOUCH" and value == 0 and active is not None:
            active["end_epoch"] = ts
            contacts.append(Contact(**active))
            active = None

    if active is not None:
        contacts.append(Contact(**active))
    return contacts


def contacts_for_attempt(attempt: Attempt, contacts: list[Contact]) -> list[Contact]:
    # A small margin tolerates the operator moving from stylus to SSH keyboard.
    start = attempt.armed_epoch - 0.20
    end = attempt.completed_epoch + 0.20
    out = []
    for contact in contacts:
        c_end = contact.end_epoch if contact.end_epoch is not None else contact.start_epoch
        if contact.start_epoch <= end and c_end >= start:
            out.append(contact)
    return out


def build_analysis(attempts: list[Attempt], contacts: list[Contact]) -> dict[str, Any]:
    enriched = []
    for row in attempts:
        matched = contacts_for_attempt(row, contacts)
        enriched.append(
            {
                **asdict(row),
                "kernel_contact_count": len(matched),
                "kernel_contacts": [asdict(c) for c in matched],
                "classification": (
                    "no-kernel-contact"
                    if not matched
                    else "kernel-contact-ui-miss"
                    if row.observed == "missed"
                    else "kernel-contact-ui-registered"
                    if row.observed == "registered"
                    else "kernel-contact-observation-unknown"
                ),
            }
        )

    blocks: dict[str, Any] = {}
    for block in ("troublesome", "control"):
        block_rows = [r for r in enriched if r["block"] == block]
        pressure: dict[str, Any] = {}
        for cls in ("light", "normal", "firm"):
            subset = [r for r in block_rows if r["pressure_class"] == cls]
            pressure[cls] = {
                "attempted": len(subset),
                "ui_registered": sum(r["observed"] == "registered" for r in subset),
                "kernel_contact_seen": sum(r["kernel_contact_count"] > 0 for r in subset),
                "kernel_contact_ui_miss": sum(
                    r["kernel_contact_count"] > 0 and r["observed"] == "missed" for r in subset
                ),
                "no_kernel_contact": sum(r["kernel_contact_count"] == 0 for r in subset),
            }
        blocks[block] = {
            "attempted": len(block_rows),
            "ui_registered": sum(r["observed"] == "registered" for r in block_rows),
            "kernel_contact_seen": sum(r["kernel_contact_count"] > 0 for r in block_rows),
            "kernel_contact_ui_miss": sum(
                r["kernel_contact_count"] > 0 and r["observed"] == "missed" for r in block_rows
            ),
            "no_kernel_contact": sum(r["kernel_contact_count"] == 0 for r in block_rows),
            "by_pressure": pressure,
        }

    return {
        "created_at": utcnow(),
        "attempts": enriched,
        "blocks": blocks,
        "interpretation_key": {
            "no-kernel-contact": "Physical attempt window contained no BTN_TOUCH contact; investigate controller/contact detection first.",
            "kernel-contact-ui-miss": "Linux reported BTN_TOUCH but intended UI action did not occur; investigate hitbox/routing/state handling.",
            "kernel-contact-ui-registered": "Linux contact and intended UI action both occurred.",
        },
    }


def report_text(analysis: dict[str, Any]) -> str:
    lines = [
        "Beastagotchi v0.19 focused NEXT touch probe",
        "============================================",
        f"Generated: {analysis['created_at']}",
        "",
    ]
    for block, title in (("troublesome", "TROUBLESOME NEXT"), ("control", "KNOWN-GOOD CONTROL NEXT")):
        data = analysis["blocks"].get(block, {})
        lines.extend(
            [
                title,
                "-" * len(title),
                f"Attempts:               {data.get('attempted', 0)}",
                f"UI registered:          {data.get('ui_registered', 0)}",
                f"Kernel contact seen:    {data.get('kernel_contact_seen', 0)}",
                f"Kernel-contact UI miss: {data.get('kernel_contact_ui_miss', 0)}",
                f"No kernel contact:      {data.get('no_kernel_contact', 0)}",
            ]
        )
        for cls in ("light", "normal", "firm"):
            p = data.get("by_pressure", {}).get(cls, {})
            lines.append(
                f"  {cls:6s}: UI {p.get('ui_registered', 0)}/{p.get('attempted', 0)} | "
                f"BTN_TOUCH {p.get('kernel_contact_seen', 0)}/{p.get('attempted', 0)} | "
                f"contact-but-UI-miss {p.get('kernel_contact_ui_miss', 0)}"
            )
        lines.append("")

    lines.extend(
        [
            "Interpretation",
            "--------------",
            "no-kernel-contact: physical attempt produced no BTN_TOUCH in the armed window.",
            "kernel-contact-ui-miss: BTN_TOUCH happened but NEXT did not register; hitbox/input routing becomes primary suspect.",
            "kernel-contact-ui-registered: both layers behaved normally.",
            "",
            "See analysis.json and evtest-raw.txt for per-attempt coordinates/timing.",
        ]
    )
    return "\n".join(lines) + "\n"


def copy_selected_runtime(work: Path) -> None:
    if not RUNTIME_ROOT.exists():
        return
    dest = work / "runtime-evidence"
    dest.mkdir(exist_ok=True)
    manifest = []
    for src in sorted(RUNTIME_ROOT.rglob("*")):
        try:
            if not src.is_file() or src.stat().st_size > 2_000_000:
                continue
            rel_text = str(src.relative_to(RUNTIME_ROOT)).lower()
            if not any(hint in rel_text for hint in RUNTIME_HINTS):
                continue
            rel = src.relative_to(RUNTIME_ROOT)
            out = dest / rel
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, out)
            manifest.append(str(rel))
        except OSError:
            continue
    (work / "runtime-evidence-manifest.txt").write_text("\n".join(manifest) + ("\n" if manifest else ""))


def main() -> int:
    ap = argparse.ArgumentParser(description="Compare troublesome and good NEXT touch behavior")
    ap.add_argument("--device", help="evdev node; auto-detected when omitted")
    args = ap.parse_args()

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    work = OUT_ROOT / f"beast-next-touch-probe-{stamp}"
    work.mkdir(parents=True, exist_ok=False)

    device = args.device or discover_touch_device()
    evtest = shutil.which("evtest")
    stdbuf = shutil.which("stdbuf")
    meta: dict[str, Any] = {
        "created_at": utcnow(),
        "probe_version": 2,
        "device": device,
        "evtest": evtest,
        "host": platform.node(),
        "kernel": platform.release(),
        "python": sys.version,
        "uid": os.getuid(),
        "euid": os.geteuid(),
    }
    (work / "metadata.json").write_text(json.dumps(meta, indent=2) + "\n")

    proc_inputs = Path("/proc/bus/input/devices")
    (work / "proc-input-devices.txt").write_text(
        proc_inputs.read_text(errors="replace") if proc_inputs.exists() else "missing\n"
    )
    (work / "touch-config.json").write_text(json.dumps(load_json(TOUCH_CONFIG), indent=2) + "\n")
    (work / "systemctl-beast-core.json").write_text(
        json.dumps(run(["systemctl", "status", "beast-core", "--no-pager", "-l"]), indent=2) + "\n"
    )
    (work / "systemctl-beast-ui.json").write_text(
        json.dumps(run(["systemctl", "status", "beast-ui", "--no-pager", "-l"]), indent=2) + "\n"
    )
    (work / "journal-before.json").write_text(
        json.dumps(run(["journalctl", "-u", "beast-ui", "-n", "250", "--no-pager", "-o", "short-precise"]), indent=2) + "\n"
    )

    raw_file = work / "evtest-raw.txt"
    proc: subprocess.Popen[str] | None = None
    raw_fh = None
    if device and evtest:
        raw_fh = raw_file.open("w")
        cmd = ([stdbuf, "-oL", evtest, device] if stdbuf else [evtest, device])
        # Deliberately NO --grab: Beast UI must receive the same events concurrently.
        proc = subprocess.Popen(cmd, stdout=raw_fh, stderr=subprocess.STDOUT, text=True)
        time.sleep(0.5)
        if proc.poll() is not None:
            print("WARNING: evtest exited immediately; raw capture may be unavailable.")
        else:
            print(f"Raw touchscreen capture active on {device} (PID {proc.pid}); UI input is NOT grabbed.")
    else:
        raw_file.write_text("Raw evdev capture unavailable: evtest or touchscreen device not found.\n")
        print("WARNING: raw evdev capture unavailable; operator observations will still be bundled.")

    attempts: list[Attempt] = []
    try:
        attempts.extend(run_block("troublesome", 1, work / "operator-attempts.jsonl"))
        attempts.extend(run_block("control", 11, work / "operator-attempts.jsonl"))
    finally:
        if proc is not None:
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=3)
        if raw_fh is not None:
            raw_fh.flush()
            raw_fh.close()

    contacts = parse_contacts(raw_file)
    (work / "parsed-contacts.json").write_text(
        json.dumps([asdict(c) for c in contacts], indent=2) + "\n"
    )
    analysis = build_analysis(attempts, contacts)
    (work / "analysis.json").write_text(json.dumps(analysis, indent=2) + "\n")
    (work / "REPORT.txt").write_text(report_text(analysis))

    copy_selected_runtime(work)
    (work / "journal-after.json").write_text(
        json.dumps(
            run(["journalctl", "-u", "beast-ui", "--since", "-20 minutes", "--no-pager", "-o", "short-precise"]),
            indent=2,
        )
        + "\n"
    )

    bundle = OUT_ROOT / f"beast-next-touch-probe-{stamp}.tar.gz"
    with tarfile.open(bundle, "w:gz") as tf:
        tf.add(work, arcname=work.name)

    print("\n" + report_text(analysis))
    print(f"Bundle ready: {bundle}")
    print("Copy this single .tar.gz to your PC and upload it for analysis.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
