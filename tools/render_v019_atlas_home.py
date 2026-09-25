from __future__ import annotations

import argparse
import json
from pathlib import Path

from beastui.experience_atlas import atlas_home_metadata, render_atlas_home
from beastui.scene_runtime import SceneRuntime


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", default="tests/fixtures/v018_target_sanitized_state.json")
    ap.add_argument("--out", default="artifacts/v019-atlas-home")
    ap.add_argument("--frames", type=int, default=6)
    args = ap.parse_args()

    state = json.loads(Path(args.state).read_text())
    root = Path(args.out)
    root.mkdir(parents=True, exist_ok=True)

    frames = max(1, min(24, int(args.frames)))
    scene_rows = []
    for i in range(frames):
        phase = i / max(1, frames - 1) * 3.0
        rt = SceneRuntime()
        im = render_atlas_home(state, phase=phase, scene_runtime=rt)
        name = f"atlas_home_{i:02d}.png"
        im.save(root / name)
        row = rt.snapshot()
        row["frame"] = i
        row["phase"] = phase
        scene_rows.append(row)

    manifest = {
        "experience": "atlas",
        "purpose": "first non-legacy Experience-DNA Home proof from sanitized real target state",
        "source_state_kind": (state.get("_beast_capture") or {}).get("kind"),
        "truth": atlas_home_metadata(state),
        "frames": scene_rows,
    }
    (root / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
