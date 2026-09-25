from __future__ import annotations

from typing import Any


# Neutral, non-renderer-specific record of currently implemented first-party
# Experience surfaces. Core and UI both consume this catalog so neither invents
# page availability independently.
BUILTIN_EXPERIENCE_SURFACES: dict[str, dict[str, str]] = {
    "atlas": {
        "home": "prototype",
        "recon": "prototype",
    },
    "forge": {
        "home": "prototype",
    },
    "observatory": {
        "home": "prototype",
        "spectrum": "prototype",
    },
    "habitat": {
        "home": "prototype",
        "beast": "prototype",
    },
    "monolith": {
        "home": "prototype",
    },
}


def experience_surface_status(experience_id: str, page_id: str) -> str | None:
    return (BUILTIN_EXPERIENCE_SURFACES.get(str(experience_id or "").strip().lower()) or {}).get(
        str(page_id or "").strip().lower()
    )


def experience_surface_coverage() -> dict[str, list[str]]:
    return {
        experience_id: sorted(pages)
        for experience_id, pages in sorted(BUILTIN_EXPERIENCE_SURFACES.items())
    }


def experience_surface_catalog() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for experience_id, pages in sorted(BUILTIN_EXPERIENCE_SURFACES.items()):
        for page_id, status in sorted(pages.items()):
            rows.append({
                "experience_id": experience_id,
                "page_id": page_id,
                "status": status,
                "reference_size": [480, 320],
            })
    return rows
