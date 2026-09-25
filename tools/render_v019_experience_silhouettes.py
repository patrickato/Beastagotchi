from __future__ import annotations

import json
from pathlib import Path

from beastui.experience_prototype_silhouettes import (
    PROTOTYPE_SILHOUETTES,
    occupancy_signature,
    render_all_silhouettes,
)


def main() -> int:
    root = Path("artifacts/v019-experience-silhouettes")
    paths = render_all_silhouettes(root)
    meta = {
        "purpose": "structural diversity proof only; not final UI art",
        "size": [480, 320],
        "experiences": {
            key: {
                "signature": list(occupancy_signature(key)),
                "regions": [
                    {
                        "id": region.id,
                        "kind": region.kind,
                        "bounds": list(region.bounds),
                        "weight": region.weight,
                    }
                    for region in spec.regions
                ],
            }
            for key, spec in PROTOTYPE_SILHOUETTES.items()
        },
        "files": [p.name for p in paths],
    }
    (root / "manifest.json").write_text(json.dumps(meta, indent=2) + "\n")
    print(root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
