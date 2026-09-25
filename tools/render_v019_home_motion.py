#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageStat

from beastui.engine import BeastUI
from beastui.scene_compositor import clear_compositor_caches, compositor_cache_telemetry


DEFAULT_THEMES = ("classic", "cyberpunk", "blackice", "wopr_norad")


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fp:
        for chunk in iter(lambda: fp.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _delta(previous: Image.Image | None, current: Image.Image) -> dict:
    if previous is None:
        return {"bbox": None, "mean_abs_rgb": 0.0}
    diff = ImageChops.difference(previous.convert("RGB"), current.convert("RGB"))
    stat = ImageStat.Stat(diff)
    return {
        "bbox": list(diff.getbbox()) if diff.getbbox() else None,
        "mean_abs_rgb": round(sum(stat.mean) / 3.0, 3),
    }


def _truth_dirtiness(scene: dict) -> dict:
    layers = {row.get("id"): row for row in (scene.get("layers") or [])}
    live, ambient, interaction = [], [], []
    for layer_id in scene.get("dirty_layers") or []:
        update_class = ((layers.get(layer_id) or {}).get("update_class") or "")
        if update_class == "live":
            live.append(layer_id)
        elif update_class == "ambient":
            ambient.append(layer_id)
        elif update_class == "interaction":
            interaction.append(layer_id)
    return {
        "changed_signals": list(scene.get("changed_signals") or []),
        "live_dirty_layers": live,
        "ambient_dirty_layers": ambient,
        "interaction_dirty_layers": interaction,
    }


def _contact_sheet(frames: list[Image.Image], *, columns: int = 4) -> Image.Image:
    if not frames:
        raise ValueError("at least one frame is required")
    w, h = frames[0].size
    columns = max(1, min(int(columns), len(frames)))
    rows = (len(frames) + columns - 1) // columns
    sheet = Image.new("RGB", (w * columns, h * rows), (0, 0, 0))
    for idx, frame in enumerate(frames):
        x = (idx % columns) * w
        y = (idx // columns) * h
        sheet.paste(frame, (x, y))
        d = ImageDraw.Draw(sheet)
        d.rectangle((x + 4, y + 4, x + 62, y + 21), fill=(0, 0, 0))
        d.text((x + 8, y + 7), f"F{idx:02d}", fill=(255, 255, 255))
    return sheet


def render_theme(root: Path, out: Path, state: dict, theme: str,
                 *, frames: int, duration: float, fps: int) -> dict:
    theme_out = out / theme
    theme_out.mkdir(parents=True, exist_ok=True)
    ui = BeastUI(root=root, output=str(theme_out / "_unused.png"), theme_id=theme)
    ui.state = dict(state)
    ui.page = ui.pages.IDS.index("home")

    clear_compositor_caches()
    rendered: list[Image.Image] = []
    rows = []
    previous = None
    for idx in range(frames):
        phase = 0.0 if frames <= 1 else duration * idx / (frames - 1)
        ui.phase_override = phase
        # Force phase-aware theme backgrounds to refresh while keeping the
        # scene compositor's reusable glow/asset caches warm.
        ui._bg_cache = None
        image = ui._compose(ui.page).convert("RGB")
        frame_name = f"frame-{idx:02d}.png"
        image.save(theme_out / frame_name)
        rendered.append(image.copy())
        scene = ui.scene_runtime.snapshot()
        rows.append({
            "frame": idx,
            "phase": round(phase, 4),
            "file": f"{theme}/{frame_name}",
            "delta": _delta(previous, image),
            "scene": scene,
            "truth_dirtiness": _truth_dirtiness(scene),
            "compositor_cache": compositor_cache_telemetry(),
        })
        previous = image.copy()

    frame_ms = max(1, int(round(1000 / max(1, fps))))
    gif = theme_out / f"home-{theme}.gif"
    rendered[0].save(
        gif,
        save_all=True,
        append_images=rendered[1:],
        duration=frame_ms,
        loop=0,
        optimize=False,
    )
    sheet = _contact_sheet(rendered)
    contact = theme_out / f"home-{theme}-contact.png"
    sheet.save(contact)
    ui.fb.close()
    return {
        "theme": theme,
        "gif": str(gif.relative_to(out)),
        "contact_sheet": str(contact.relative_to(out)),
        "frames": rows,
        "truth_summary": {
            "initial_changed_signal_count": len(rows[0]["truth_dirtiness"]["changed_signals"]),
            "later_live_dirty_frames": sum(
                1 for row in rows[1:] if row["truth_dirtiness"]["live_dirty_layers"]
            ),
            "later_ambient_dirty_frames": sum(
                1 for row in rows[1:] if row["truth_dirtiness"]["ambient_dirty_layers"]
            ),
            "synthetic_telemetry_injected": False,
        },
        "final_cache": compositor_cache_telemetry(),
    }


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Render deterministic multi-frame Home proofs from captured Beast state."
    )
    ap.add_argument("--root", default="beastui")
    ap.add_argument("--state", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--themes", default=",".join(DEFAULT_THEMES))
    ap.add_argument("--frames", type=int, default=8)
    ap.add_argument("--duration", type=float, default=2.0)
    ap.add_argument("--fps", type=int, default=6)
    args = ap.parse_args()

    root = Path(args.root)
    state_path = Path(args.state)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    state = json.loads(state_path.read_text())
    if not isinstance(state, dict):
        raise ValueError("state JSON must be an object")
    themes = tuple(x.strip() for x in args.themes.split(",") if x.strip())
    if not themes:
        raise ValueError("at least one theme is required")

    manifest = {
        "kind": "v019_home_motion_proof",
        "truth_source": "captured_state_only",
        "source_state": str(state_path),
        "source_state_sha256": _sha256(state_path),
        "state_provenance": state.get("_beast_capture"),
        "frames_per_theme": max(2, int(args.frames)),
        "duration_seconds": float(args.duration),
        "fps": max(1, int(args.fps)),
        "themes": [],
    }
    for theme in themes:
        manifest["themes"].append(
            render_theme(
                root, out, state, theme,
                frames=max(2, int(args.frames)),
                duration=max(0.1, float(args.duration)),
                fps=max(1, int(args.fps)),
            )
        )
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
