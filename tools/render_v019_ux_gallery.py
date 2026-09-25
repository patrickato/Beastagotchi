#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from beastui.engine import BeastUI
from beastcore.capsules import BeastCapsuleCodec


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
PLATFORM_OVERLAYS = (
    "operations",
    "notifications",
    "diagnostics",
    "services",
    "hardware",
    "storage",
    "incidents",
    "connectivity",
)
INTERACTION_SURFACES = ("control_center", "apps", "capsule_share")


def _gallery_capsule(state: dict) -> dict:
    """Build a clearly non-importable visual proof from the sanitized capture.

    This is not a local roster export and is labeled PREVIEW in both payload and
    UI. It exists only so CI can validate a real QR matrix/layout without
    inventing telemetry or pretending the gallery owns a creature record.
    """
    source = {
        "level": state.get("progression.level"),
        "stage": state.get("progression.stage"),
        "lineage": state.get("progression.beast.lineage") or "sanitized",
        "name": state.get("progression.beast.name") or "SANITIZED BEAST",
    }
    sid = hashlib.sha256(json.dumps(source, sort_keys=True).encode()).hexdigest()[:20]
    payload = {
        "format": "lineage_v1",
        "preview": True,
        "creature_id": "creature-gallery-" + sid,
        "name": str(source["name"])[:64],
        "kind": "beast",
        "lineage": str(source["lineage"])[:80],
        "generation": int(state.get("progression.beast.generation") or 0),
        "level": int(state.get("progression.level") or 1),
        "stage": str(state.get("progression.stage") or "--")[:64],
        "legend": False,
        "parents": [],
        "achievement_count": int(state.get("progression.achievements.count") or 0),
        "gallery_source": "sanitized_real_state_fixture",
    }
    envelope = BeastCapsuleCodec.build(
        "lineage",
        payload,
        created_at=0.0,
        capsule_id="capsule-gallery-preview-" + sid,
        producer={"name": "Beastagotchi", "format": "gallery_preview"},
        privacy={
            "local_ids_included": False,
            "credentials_included": False,
            "captures_included": False,
            "network_history_included": False,
            "exact_location_included": False,
            "logs_included": False,
            "name_included": True,
            "gallery_preview": True,
        },
    )
    encoded = BeastCapsuleCodec.encode(envelope)
    frames = BeastCapsuleCodec.qr_frames(encoded, max_frame_chars=220)
    return {
        "ok": True,
        "capsule_type": "lineage",
        "envelope": envelope,
        "encoded": encoded,
        "encoded_chars": len(encoded),
        "qr": {
            "transport": "animated_qr_text_frames",
            "frame_count": len(frames),
            "max_frame_chars": 220,
            "frames": frames,
            "renderer_required": True,
            "renderer_bundled": False,
        },
        "import_performed": False,
        "gallery_preview": True,
    }


def _sha256(path: str | Path | None) -> str | None:
    if not path:
        return None
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def render(root: Path, out: Path, theme: str, page: str, state: dict, *, histories=None, aux=None, events=None, physical=(480, 320), surface: str | None = None) -> None:
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
    if surface == "control_center":
        ui.drawer = True
    elif surface == "apps":
        ui.app_launcher = True
    elif surface == "capsule_share":
        ui.capsule_share_overlay = True
        ui.capsule_share = _gallery_capsule(state)
        ui.capsule_frame_idx = 0
    elif surface in PLATFORM_OVERLAYS:
        ui.platform_overlay = surface
        ui.platform_offset = 0
    elif surface is not None:
        raise ValueError(f"unknown surface: {surface}")
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
        "source_state_sha256": _sha256(args.state),
        "state_provenance": state.get("_beast_capture"),
        "histories_source": str(Path(args.histories)) if args.histories else None,
        "histories_sha256": _sha256(args.histories),
        "aux_source": str(Path(args.aux)) if args.aux else None,
        "aux_sha256": _sha256(args.aux),
        "events_source": str(Path(args.events)) if args.events else None,
        "events_sha256": _sha256(args.events),
        "themes": list(themes),
        "pages": list(PAGES),
        "platform_overlays": list(PLATFORM_OVERLAYS),
        "interaction_surfaces": list(INTERACTION_SURFACES),
        "capsule_gallery_preview": {
            "derived_from_sanitized_state": True,
            "not_a_roster_export": True,
            "importable": False,
            "qr_backend_required_for_render": True,
        },
        "frames": [],
    }

    for theme in themes:
        for page in PAGES:
            name = f"v019-{page}-{theme}.png"
            render(root, out / name, theme, page, state, histories=histories, aux=aux, events=events)
            manifest["frames"].append({"theme": theme, "page": page, "surface": "page", "file": name})

    # Operational and interaction surfaces are rendered once against the same
    # captured state. They are deliberately not multiplied across every theme:
    # this gallery is for hierarchy/touch review, while the page set carries
    # the structural theme comparison.
    for surface in INTERACTION_SURFACES + PLATFORM_OVERLAYS:
        name = f"v019-surface-{surface}-classic.png"
        render(
            root,
            out / name,
            "classic",
            "home",
            state,
            histories=histories,
            aux=aux,
            events=events,
            surface=surface,
        )
        manifest["frames"].append({
            "theme": "classic",
            "page": "home",
            "surface": surface,
            "file": name,
        })

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
