"""Render every registered v0.19 Experience page under a matrix of truth/stress states.

Review/evidence tool for BEASTAGOTCHI_VISUAL_REVIEW_RESPONSE_2026-09-27.md. It only
calls the registered first-party renderers; it does not modify runtime code, state,
preferences or display ownership.

CI currently renders one sanitized capture (healthy, no GPS fix, 6 APs). Several
renderer branches -- GPS route, busy 2.4 GHz air, battery telemetry, critical fault,
unknown/cold-boot values -- are never exercised by that single state. This matrix
exercises them. States other than ``baseline_real`` are *synthetic review fixtures*
derived from the sanitized capture and are labelled as such on every sheet.

Usage (repository root):
    PYTHONPATH=. python3 collaboration/claude/tools/experience_state_matrix.py --out /tmp/matrix
"""
from __future__ import annotations

import argparse
import copy
import json
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from beastui.experience_registry import experience_renderer_catalog, render_experience_page
from beastui.scene_runtime import SceneRuntime

ROOT = Path(__file__).resolve().parents[3]
FIXTURE = ROOT / "tests/fixtures/v018_target_sanitized_state.json"
ORDER = ("atlas", "forge", "observatory", "habitat", "monolith")


def _font(size: int):
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except Exception:
        return ImageFont.load_default()


def _busy_aps(n: int = 34, seed: int = 7) -> list[dict]:
    """Synthetic but plausible street: mostly 2.4 GHz on 1/6/11 plus some 5 GHz."""
    rng = random.Random(seed)
    rows = []
    for _ in range(n):
        if rng.random() < 0.72:
            ch = rng.choice([1, 1, 6, 6, 6, 11, 11, 3, 9, 13])
        else:
            ch = rng.choice([36, 40, 44, 48, 52, 100, 108, 112, 132, 149])
        rows.append({"channel": ch, "rssi": rng.randint(-92, -41),
                     "encryption": "WPA2", "handshake": rng.random() < 0.12})
    return rows


def build_states(base: dict) -> dict[str, dict]:
    states: dict[str, dict] = {"baseline_real": copy.deepcopy(base)}

    s = copy.deepcopy(base)
    s.update({"gps.fix": True, "gps.satellites_used": 9, "gps.state": "fixed",
              "expedition.route_points": 42, "expedition.distance_m": 1840.0,
              "expedition.duration_sec": 2730.0, "beast.expression": "hunting"})
    states["synthetic_gps_route_short"] = s

    s = copy.deepcopy(states["synthetic_gps_route_short"])
    s.update({"expedition.route_points": 400, "expedition.distance_m": 12400.0,
              "expedition.duration_sec": 9100.0})
    states["synthetic_gps_route_long"] = s

    s = copy.deepcopy(base)
    aps = _busy_aps()
    s.update({"wifi.aps": aps, "wifi.ap_count": len(aps),
              "wifi.handshake_ap_count": sum(1 for a in aps if a["handshake"]),
              "wifi.hidden_count": 5, "radio.primary.channel": 6, "radio.primary.band": "2.4GHz",
              "expedition.ap_unique": 61, "wifi.encounters.session_unique": 61})
    states["synthetic_busy_2g4"] = s

    s = copy.deepcopy(base)
    s.update({"power.telemetry.available": True, "power.ups.state": "discharging",
              "power.battery.percent_estimate": 23.0, "power.battery.voltage_v": 10.9,
              "power.power_w": 6.8, "power.current_ma": 624, "power.source": "battery",
              "power.discharging": True, "power.external_present": False})
    states["synthetic_battery_low"] = s

    s = copy.deepcopy(base)
    s.update({"health.core.state": "critical", "system.temp.cpu_c": 81.4,
              "governor.mode": "SURVIVAL", "pwnagotchi.service.state": "failed",
              "bettercap.state": "failed", "beast.expression": "fault", "pwnagotchi.mood": "sad",
              "overview.attention": [{"id": "pwnagotchi", "severity": "critical"},
                                     {"id": "thermal", "severity": "critical"}],
              "wifi.aps": [], "wifi.ap_count": 0, "radio.primary.channel": 0})
    states["synthetic_fault_critical"] = s

    # Cold boot / collectors not yet reporting.
    states["synthetic_unknown_empty"] = {"_beast_capture": {"kind": "live"}}
    return states


def render_matrix(out: Path) -> dict[str, dict[str, Path]]:
    base = json.loads(FIXTURE.read_text())
    catalog = sorted(experience_renderer_catalog(),
                     key=lambda r: (ORDER.index(r["experience_id"]), r["page_id"] != "home"))
    frames: dict[str, dict[str, Path]] = {}
    for name, state in build_states(base).items():
        d = out / name
        d.mkdir(parents=True, exist_ok=True)
        frames[name] = {}
        for row in catalog:
            key = f"{row['experience_id']}_{row['page_id']}"
            im = render_experience_page(row["experience_id"], row["page_id"], state,
                                        scene_runtime=SceneRuntime())
            fp = d / f"{key}.png"
            im.save(fp)
            frames[name][key] = fp
    return frames


def contact_sheet(cells: list[tuple[str, Image.Image]], fp: Path, *, cols: int = 2,
                  title: str = "") -> Path:
    """Native-scale (1:1) frames with captions. Never rescales the 480x320 frame."""
    cap_h, pad, head = 22, 6, (30 if title else 0)
    w, h = 480, 320 + cap_h
    rows = (len(cells) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * w + (cols + 1) * pad, head + rows * h + (rows + 1) * pad),
                      (58, 58, 58))
    d = ImageDraw.Draw(sheet)
    if title:
        d.text((pad + 2, 7), title, fill=(255, 255, 255), font=_font(15))
    for i, (caption, im) in enumerate(cells):
        x = pad + (i % cols) * (w + pad)
        y = head + pad + (i // cols) * (h + pad)
        d.rectangle((x, y, x + w - 1, y + cap_h - 1), fill=(20, 20, 20))
        d.text((x + 6, y + 4), caption, fill=(245, 245, 240), font=_font(12))
        sheet.paste(im.convert("RGB"), (x, y + cap_h))
    sheet.save(fp)
    return fp


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    out = Path(args.out)
    frames = render_matrix(out)
    for state, pages in frames.items():
        contact_sheet([(f"{state} :: {k}", Image.open(v)) for k, v in pages.items()],
                      out / f"sheet_{state}.png",
                      title=f"{state} -- all registered Experience pages at native 480x320")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
