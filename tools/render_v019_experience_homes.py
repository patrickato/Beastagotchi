from __future__ import annotations

import argparse
import json
from pathlib import Path

from beastui.experience_atlas import render_atlas_home
from beastui.experience_forge import render_forge_home
from beastui.experience_observatory import render_observatory_home
from beastui.scene_runtime import SceneRuntime


RENDERERS = {
    "atlas": render_atlas_home,
    "forge": render_forge_home,
    "observatory": render_observatory_home,
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", default="tests/fixtures/v018_target_sanitized_state.json")
    ap.add_argument("--out", default="artifacts/v019-experience-homes")
    args = ap.parse_args()

    state = json.loads(Path(args.state).read_text())
    root = Path(args.out)
    root.mkdir(parents=True, exist_ok=True)

    manifest = {
        "purpose": "first three non-legacy Experience-DNA Home proofs from sanitized real target state",
        "source_state_kind": (state.get("_beast_capture") or {}).get("kind"),
        "experiences": {},
    }
    for experience_id, renderer in RENDERERS.items():
        rt = SceneRuntime()
        im = renderer(state, scene_runtime=rt)
        name = f"{experience_id}_home.png"
        im.save(root / name)
        manifest["experiences"][experience_id] = {
            "file": name,
            "scene": rt.snapshot(),
        }

    (root / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
