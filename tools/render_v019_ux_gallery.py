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

PAGES = ("home", "overview", "recon", "networks", "spectrum", "captures", "map", "expedition", "beast", "system")


def render(root: Path, out: Path, theme: str, page: str, state: dict, *, histories=None, aux=None, events=None, physical=(480, 320)) -> None:
    ui = BeastUI(
        root=root,
        output=str(out),
        theme_id=theme,
        physical_size=physical,
        display_mode="fit",
    )
    ui.state = dict(state)
    ui.histories = dict(histories or {})
    ui.aux = dict(aux or {})
    ui.events = list(events or [])
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
    ap.add_argument("--histories", help="Optional captured Beast histories JSON")
    ap.add_argument("--aux", help="Optional captured auxiliary bundle JSON (route/channel history/etc.)")
    ap.add_argument("--events", help="Optional captured Beast events JSON array")
    ap.add_argument("--all-themes", action="store_true", help="Render every primary theme family")
    args = ap.parse_args()

    root = Path(args.root)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    state = json.loads(Path(args.state).read_text())
    histories = json.loads(Path(args.histories).read_text()) if args.histories else {}
    aux = json.loads(Path(args.aux).read_text()) if args.aux else {}
    events = json.loads(Path(args.events).read_text()) if args.events else []
    if not isinstance(histories, dict):
        raise ValueError("histories JSON must be an object")
    if not isinstance(aux, dict):
        raise ValueError("aux JSON must be an object")
    if not isinstance(events, list):
        raise ValueError("events JSON must be an array")

    # The gallery deliberately does not synthesize telemetry. Missing values stay
    # missing. This lets visual review expose both real density and honest
    # unavailable/empty states from the exact device capture supplied.
    themes = THEMES if args.all_themes else ("classic", "blackice", "synthwave", "lcars")
    manifest = {
        "source_state": str(Path(args.state)),
        "state_provenance": state.get("_beast_capture"),
        "histories_source": str(Path(args.histories)) if args.histories else None,
        "aux_source": str(Path(args.aux)) if args.aux else None,
        "events_source": str(Path(args.events)) if args.events else None,
        "themes": list(themes),
        "pages": list(PAGES),
        "frames": [],
    }

    for theme in themes:
        for page in PAGES:
            name = f"v019-{page}-{theme}.png"
            render(root, out / name, theme, page, state, histories=histories, aux=aux, events=events)
            manifest["frames"].append({"theme": theme, "page": page, "file": name})

    # One compatibility-scale proof remains useful during responsive work, but
    # this is not a native-responsive-layout claim.
    render(root, out / "v019-home-classic-800x480-compat.png", "classic", "home", state, histories=histories, aux=aux, events=events, physical=(800, 480))
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
