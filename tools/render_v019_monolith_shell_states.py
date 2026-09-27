from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from beastui.experience_registry import render_experience_page
from beastui.scene_runtime import SceneRuntime


STATE_ORDER = ("healthy", "unknown", "degraded", "radio_offline", "critical_thermal")


def _font(size: int):
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except Exception:
        return ImageFont.load_default()


def _states(base: dict) -> dict[str, dict]:
    healthy = dict(base)
    healthy.update({
        "health.core.state": "healthy",
        "system.temp.cpu_c": 58.0,
        "system.cpu.total": 22.0,
        "wifi.ap_count": 18,
        "radio.primary.channel": 11,
        "radio.primary.band": "2.4GHz",
        "pwnagotchi.service.state": "active",
        "bettercap.service.state": "active",
        "radio.monitor.state": "active",
        "dock.state": "field",
        "governor.mode": "FULL",
    })

    unknown = dict(base)
    for key in (
        "health.core.state",
        "system.temp.cpu_c",
        "system.cpu.total",
        "wifi.ap_count",
        "radio.primary.channel",
        "pwnagotchi.service.state",
        "bettercap.service.state",
        "radio.monitor.state",
        "dock.state",
        "governor.mode",
        "progression.level",
    ):
        unknown.pop(key, None)

    degraded = dict(healthy)
    degraded.update({
        "health.core.state": "degraded",
        "system.temp.cpu_c": 76.0,
        "system.cpu.total": 73.0,
        "wifi.ap_count": 7,
    })

    radio_offline = dict(healthy)
    radio_offline.update({
        "pwnagotchi.service.state": "failed",
        "bettercap.service.state": "inactive",
        "radio.monitor.state": "offline",
    })
    radio_offline.pop("wifi.ap_count", None)
    radio_offline.pop("radio.primary.channel", None)

    critical_thermal = dict(healthy)
    critical_thermal.update({
        "health.core.state": "critical",
        "system.temp.cpu_c": 81.0,
        "system.cpu.total": 91.0,
    })

    return {
        "healthy": healthy,
        "unknown": unknown,
        "degraded": degraded,
        "radio_offline": radio_offline,
        "critical_thermal": critical_thermal,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", default="tests/fixtures/v018_target_sanitized_state.json")
    ap.add_argument("--out", default="artifacts/v019-monolith-shell-states")
    args = ap.parse_args()

    base = json.loads(Path(args.state).read_text())
    root = Path(args.out)
    root.mkdir(parents=True, exist_ok=True)
    states = _states(base)

    manifest = {
        "purpose": "shared Beast shell semantic proof using Monolith as first consumer",
        "synthetic_review_states": True,
        "states": {},
    }

    rows = []
    for state_id in STATE_ORDER:
        state = states[state_id]
        row = Image.new("RGB", (960, 354), (8, 8, 8))
        rd = ImageDraw.Draw(row)
        rd.text((12, 7), state_id.upper().replace("_", " "), fill=(235, 232, 222), font=_font(16))
        manifest["states"][state_id] = {"files": {}}

        for col, page_id in enumerate(("home", "overview")):
            rt = SceneRuntime()
            im = render_experience_page("monolith", page_id, state, scene_runtime=rt)
            name = f"monolith_{page_id}_{state_id}.png"
            im.save(root / name)
            row.paste(im, (col * 480, 34))
            manifest["states"][state_id]["files"][page_id] = name
            manifest["states"][state_id][f"{page_id}_scene"] = rt.snapshot()
        rows.append(row)

    sheet = Image.new("RGB", (960, 354 * len(rows)), (8, 8, 8))
    for idx, row in enumerate(rows):
        sheet.paste(row, (0, idx * 354))
    sheet.save(root / "comparison.png")
    manifest["comparison"] = "comparison.png"
    (root / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
