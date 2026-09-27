from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from beastui.experience_live import ExperienceBeastUI


EXPERIENCES = ("atlas", "forge", "observatory", "habitat", "monolith")


def _font(size: int):
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except Exception:
        return ImageFont.load_default()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="beastui")
    ap.add_argument("--state", default="tests/fixtures/v018_target_sanitized_state.json")
    ap.add_argument("--out", default="artifacts/v019-experience-live-runtime")
    args = ap.parse_args()

    state = json.loads(Path(args.state).read_text())
    root = Path(args.out)
    root.mkdir(parents=True, exist_ok=True)

    manifest = {
        "purpose": (
            "five Experience Home proofs rendered through the staging ExperienceBeastUI "
            "runtime, DisplayTransform, and FrameBuffer output path"
        ),
        "source_state_kind": (state.get("_beast_capture") or {}).get("kind"),
        "runtime_mode": "staging",
        "writes_preferences": False,
        "experiences": {},
    }

    cards = []
    for experience_id in EXPERIENCES:
        output = root / f"{experience_id}_live_home.png"
        ui = ExperienceBeastUI(
            args.root,
            "/dev/this-must-not-be-opened",
            str(output),
            "classic",
            experience_id=experience_id,
            experience_page="home",
            physical_size=(480, 320),
        )
        ui.state = dict(state)
        ui.phase_override = 0.5
        try:
            image = ui.render().convert("RGB")
            runtime = ui.experience_runtime_snapshot()
            scene = ui.scene_runtime.snapshot()
            framebuffer = ui.fb.telemetry()
        finally:
            ui.fb.close()

        if image.size != (480, 320):
            raise RuntimeError(f"{experience_id}: unexpected live-runtime size {image.size}")
        if scene.get("scene") != f"experience:{experience_id}:home":
            raise RuntimeError(f"{experience_id}: unexpected live-runtime scene {scene.get('scene')}")

        manifest["experiences"][experience_id] = {
            "file": output.name,
            "runtime": runtime,
            "scene": scene,
            "framebuffer": framebuffer,
        }

        card = Image.new("RGB", (480, 350), (10, 10, 10))
        card.paste(image, (0, 30))
        draw = ImageDraw.Draw(card)
        draw.text((10, 7), f"{experience_id.upper()} / LIVE RUNTIME", fill=(232, 232, 226), font=_font(15))
        cards.append(card)

    sheet = Image.new("RGB", (1440, 700), (7, 7, 7))
    for idx, card in enumerate(cards):
        sheet.paste(card, ((idx % 3) * 480, (idx // 3) * 350))
    sheet.save(root / "comparison.png")
    manifest["comparison"] = "comparison.png"

    (root / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
