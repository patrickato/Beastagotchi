#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import statistics
from collections import Counter
from pathlib import Path
from typing import Any


def _read_json(path: Path) -> dict[str, Any]:
    try:
        obj = json.loads(path.read_text())
        return obj if isinstance(obj, dict) else {}
    except Exception:
        return {}


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        for line in path.read_text().splitlines():
            try:
                obj = json.loads(line)
            except Exception:
                continue
            if isinstance(obj, dict):
                rows.append(obj)
    except Exception:
        pass
    return rows


def _nums(values):
    out = []
    for value in values:
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            out.append(float(value))
    return out


def _metric(values) -> dict[str, float | int | None]:
    vals = _nums(values)
    if not vals:
        return {"samples": 0, "min": None, "avg": None, "max": None}
    return {
        "samples": len(vals),
        "min": round(min(vals), 3),
        "avg": round(statistics.fmean(vals), 3),
        "max": round(max(vals), 3),
    }


def _nested(row: dict[str, Any], *path: str):
    cur: Any = row
    for part in path:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(part)
    return cur


def summarize_session(root: str | Path) -> dict[str, Any]:
    root = Path(root)
    samples = _read_jsonl(root / "runtime-samples.jsonl")
    preflight = _read_json(root / "preflight.json")
    capsule = _read_json(root / "capsule-export.json")
    final_state_raw = _read_json(root / "state-final.json")
    final_state = final_state_raw.get("state") if isinstance(final_state_raw.get("state"), dict) else final_state_raw
    runtime_final = _read_json(root / "ui-runtime-final.json")

    temp = _metric(_nested(r, "state", "system.temp.cpu_c") for r in samples)
    cpu = _metric(_nested(r, "state", "system.cpu.total") for r in samples)
    render = _metric(_nested(r, "runtime", "avg_render_ms") for r in samples)
    compose = _metric(_nested(r, "runtime", "avg_compose_ms") for r in samples)
    fb_write = _metric(_nested(r, "runtime", "avg_fb_write_ms") for r in samples)
    dirty_rows = _metric(_nested(r, "runtime", "framebuffer", "changed_rows") for r in samples)
    bytes_written = _metric(_nested(r, "runtime", "framebuffer", "bytes_written") for r in samples)
    target_fps = _metric(_nested(r, "runtime", "target_fps") for r in samples)
    lifetime_fps = _metric(_nested(r, "runtime", "lifetime_fps") for r in samples)

    frame_bytes = None
    write_ratios = []
    full_writes = 0
    for row in samples:
        fb = _nested(row, "runtime", "framebuffer")
        if not isinstance(fb, dict):
            continue
        frame_bytes = fb.get("frame_bytes") if isinstance(fb.get("frame_bytes"), (int, float)) else frame_bytes
        bw = fb.get("bytes_written")
        if isinstance(frame_bytes, (int, float)) and frame_bytes > 0 and isinstance(bw, (int, float)):
            write_ratios.append(100.0 * float(bw) / float(frame_bytes))
        if fb.get("full_write") is True:
            full_writes += 1

    first_totals = None
    last_totals = None
    for row in samples:
        totals = _nested(row, "runtime", "framebuffer", "totals")
        if isinstance(totals, dict):
            if first_totals is None:
                first_totals = dict(totals)
            last_totals = dict(totals)

    delta = {}
    if first_totals and last_totals:
        for key in ("frames", "bytes_written", "full_writes", "saved_bytes"):
            a = first_totals.get(key)
            b = last_totals.get(key)
            if isinstance(a, (int, float)) and isinstance(b, (int, float)):
                delta[key] = int(b - a)

    touch_rows = _read_jsonl(root / "touch-gestures.jsonl")
    touch_kinds = Counter()
    for row in touch_rows:
        kind = str(row.get("kind") or row.get("gesture") or row.get("type") or "unknown")
        touch_kinds[kind] += 1

    qr = preflight.get("qr_renderer") if isinstance(preflight.get("qr_renderer"), dict) else {}
    qr_frames = _nested(capsule, "qr", "frame_count")
    capsule_ok = capsule.get("ok") is True

    warnings = []
    if not samples:
        warnings.append("No runtime sample window was captured.")
    if qr and qr.get("available") is False:
        warnings.append("Optional QR renderer is unavailable on this target.")
    if not capsule_ok:
        warnings.append("A real Lineage Capsule export was not captured.")
    if temp["max"] is not None and float(temp["max"]) >= 80.0:
        warnings.append("CPU temperature reached at least 80C during the sample window.")
    if runtime_final and str(runtime_final.get("version") or "").startswith("0.18"):
        warnings.append("UI runtime still reports an older v0.18 identity.")

    return {
        "schema": 1,
        "session_dir": str(root),
        "evidence_class": "target_physical_session",
        "physical_user_judgment": "required",
        "sample_count": len(samples),
        "metrics": {
            "cpu_temp_c": temp,
            "cpu_pct": cpu,
            "avg_render_ms": render,
            "avg_compose_ms": compose,
            "avg_fb_write_ms": fb_write,
            "framebuffer_changed_rows": dirty_rows,
            "framebuffer_bytes_written": bytes_written,
            "framebuffer_write_ratio_pct": _metric(write_ratios),
            "target_fps": target_fps,
            "lifetime_fps": lifetime_fps,
            "full_write_sample_count": full_writes,
            "framebuffer_totals_delta": delta,
        },
        "touch": {
            "record_count": len(touch_rows),
            "kinds": dict(sorted(touch_kinds.items())),
        },
        "capsule": {
            "export_ok": capsule_ok,
            "frame_count": qr_frames if isinstance(qr_frames, int) else None,
            "renderer_available": qr.get("available") if qr else None,
            "renderer_backend": qr.get("backend") if qr else None,
        },
        "final": {
            "ui_version": runtime_final.get("version"),
            "theme": runtime_final.get("theme"),
            "page": runtime_final.get("page"),
            "core_health": final_state.get("health.core.state"),
            "governor_mode": final_state.get("governor.mode"),
        },
        "warnings": warnings,
    }


def write_text_report(summary: dict[str, Any]) -> str:
    m = summary.get("metrics") or {}
    lines = [
        "Beastagotchi v0.19 Physical Acceptance Evidence",
        "=" * 47,
        f"Session: {summary.get('session_dir')}",
        f"Samples: {summary.get('sample_count')}",
        "",
        "Objective telemetry",
    ]
    labels = (
        ("CPU temp C", "cpu_temp_c"),
        ("CPU %", "cpu_pct"),
        ("Render ms", "avg_render_ms"),
        ("Compose ms", "avg_compose_ms"),
        ("FB write ms", "avg_fb_write_ms"),
        ("Changed rows", "framebuffer_changed_rows"),
        ("Bytes written", "framebuffer_bytes_written"),
        ("FB write ratio %", "framebuffer_write_ratio_pct"),
        ("Target FPS", "target_fps"),
        ("Lifetime FPS", "lifetime_fps"),
    )
    for label, key in labels:
        row = m.get(key) or {}
        lines.append(
            f"- {label}: min={row.get('min')} avg={row.get('avg')} max={row.get('max')} n={row.get('samples')}"
        )
    lines.extend([
        f"- full-write samples: {m.get('full_write_sample_count')}",
        f"- framebuffer totals delta: {json.dumps(m.get('framebuffer_totals_delta') or {}, sort_keys=True)}",
        "",
        "Touch evidence",
        f"- records: {(summary.get('touch') or {}).get('record_count')}",
        f"- kinds: {json.dumps((summary.get('touch') or {}).get('kinds') or {}, sort_keys=True)}",
        "",
        "Capsule / QR",
        f"- export ok: {(summary.get('capsule') or {}).get('export_ok')}",
        f"- frame count: {(summary.get('capsule') or {}).get('frame_count')}",
        f"- renderer available: {(summary.get('capsule') or {}).get('renderer_available')}",
        f"- renderer backend: {(summary.get('capsule') or {}).get('renderer_backend')}",
        "",
        "Final state",
        f"- UI version: {(summary.get('final') or {}).get('ui_version')}",
        f"- theme/page: {(summary.get('final') or {}).get('theme')} / {(summary.get('final') or {}).get('page')}",
        f"- Core health: {(summary.get('final') or {}).get('core_health')}",
        f"- Governor: {(summary.get('final') or {}).get('governor_mode')}",
        "",
        "Warnings",
    ])
    warnings = summary.get("warnings") or []
    lines.extend([f"- {x}" for x in warnings] or ["- none from automated evidence"])
    lines.extend([
        "",
        "IMPORTANT: This report does not decide physical acceptance.",
        "Readability, touch feel, camera QR scanning, glare/brightness, animation",
        "smoothness and perceived polish require the user's real TFT judgment.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Summarize a Beastagotchi v0.19 physical acceptance session.")
    ap.add_argument("session_dir")
    ap.add_argument("--json", dest="json_path")
    ap.add_argument("--text", dest="text_path")
    args = ap.parse_args()

    summary = summarize_session(args.session_dir)
    raw = json.dumps(summary, indent=2, sort_keys=True) + "\n"
    txt = write_text_report(summary)
    if args.json_path:
        Path(args.json_path).write_text(raw)
    else:
        print(raw, end="")
    if args.text_path:
        Path(args.text_path).write_text(txt)
    elif args.json_path:
        print(txt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
