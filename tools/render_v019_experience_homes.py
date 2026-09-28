from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from beastui.experience_registry import render_experience_page
from beastui.scene_runtime import SceneRuntime


EXPERIENCES = ("atlas", "forge", "observatory", "habitat", "monolith")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", default="tests/fixtures/v018_target_sanitized_state.json")
    ap.add_argument("--out", default="artifacts/v019-experience-homes")
    args = ap.parse_args()

    state = json.loads(Path(args.state).read_text())
    root = Path(args.out)
    root.mkdir(parents=True, exist_ok=True)

    manifest = {
        "purpose": "first five active-registry Experience-DNA Home proofs from sanitized real target state",
        "source_state_kind": (state.get("_beast_capture") or {}).get("kind"),
        "experiences": {},
    }
    for experience_id in EXPERIENCES:
        rt = SceneRuntime()
        im = render_experience_page(experience_id, "home", state, scene_runtime=rt)
        name = f"{experience_id}_home.png"
        im.save(root / name)
        manifest["experiences"][experience_id] = {
            "file": name,
            "scene": rt.snapshot(),
        }

    # Side-by-side comparison is intentionally a review artifact, not a runtime UI.
    cards = []
    for experience_id in EXPERIENCES:
        im = Image.open(root / f"{experience_id}_home.png").convert("RGB")
        card = Image.new("RGB", (480, 350), (12, 12, 12))
        card.paste(im, (0, 30))
        dd = ImageDraw.Draw(card)
        try:
            font = ImageFont.truetype("DejaVuSans.ttf", 16)
        except Exception:
            font = ImageFont.load_default()
        dd.text((10, 7), experience_id.upper(), fill=(230, 230, 225), font=font)
        cards.append(card)
    sheet = Image.new("RGB", (1440, 700), (8, 8, 8))
    for idx, card in enumerate(cards):
        col = idx % 3
        row = idx // 3
        sheet.paste(card, (col * 480, row * 350))
    sheet.save(root / "comparison.png")
    manifest["comparison"] = "comparison.png"
    (root / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
