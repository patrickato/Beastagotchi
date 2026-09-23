#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from beastui.engine import BeastUI


THEMES = (
    "classic",
    "blackice",
    "hunter",
    "synthwave",
    "amber_tactical",
    "ghost_minimal",
    "cyberpunk",
    "wopr_norad",
    "lcars",
    "retro_crt",
)

PAGES = ("home", "overview", "networks", "system", "beast")


def render(root: Path, out: Path, theme: str, page: str, state: dict, *, physical=(480, 320)) -> None:
    ui = BeastUI(
        root=root,
        output=str(out),
        theme_id=theme,
        physical_size=physical,
        display_mode="fit",
    )
    ui.state = dict(state)
    ui.histories = {}
    ui.aux = {}
    ui.events = []
    if page not in ui.pages.IDS:
        raise ValueError(f"unknown page: {page}")
    ui.page = ui.pages.IDS.index(page)
    ui.render()


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Render a comparable v0.19 UX gallery from a captured Beast state JSON."
    )
    ap.add_argument("--root", default="/opt/beast-ui")
    ap.add_argument("--state", required=True, help="Captured canonical Beast state JSON")
    ap.add_argument("--out", required=True)
    ap.add_argument("--all-themes", action="store_true", help="Render every primary theme family")
    args = ap.parse_args()

    root = Path(args.root)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    state = json.loads(Path(args.state).read_text())

    # The gallery deliberately does not synthesize telemetry. Missing values stay
    # missing. This lets visual review expose both real density and honest
    # unavailable/empty states from the exact device capture supplied.
    themes = THEMES if args.all_themes else ("classic", "blackice", "synthwave", "lcars")
    manifest = {
        "source_state": str(Path(args.state)),
        "themes": list(themes),
        "pages": list(PAGES),
        "frames": [],
    }

    for theme in themes:
        for page in PAGES:
            name = f"v019-{page}-{theme}.png"
            render(root, out / name, theme, page, state)
            manifest["frames"].append({"theme": theme, "page": page, "file": name})

    # One compatibility-scale proof remains useful during responsive work, but
    # this is not a native-responsive-layout claim.
    render(root, out / "v019-home-classic-800x480-compat.png", "classic", "home", state, physical=(800, 480))
    manifest["frames"].append({
        "theme": "classic",
        "page": "home",
        "file": "v019-home-classic-800x480-compat.png",
        "physical_size": [800, 480],
        "mode": "compatibility-scale",
    })

    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
