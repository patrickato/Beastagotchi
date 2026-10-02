from __future__ import annotations

from copy import deepcopy
from typing import Any


class ExperienceDraftError(ValueError):
    pass


def _find(
    value: Any,
    rows: list[dict[str, Any]],
    *,
    source_pack: str = "",
) -> dict[str, Any] | None:
    value = str(value or "").strip()
    if not value:
        return None
    exact = [r for r in rows if str(r.get("id") or "") == value]
    if exact:
        return exact[0]
    local = [
        r for r in rows
        if str(r.get("local_id") or "") == value
        and (not source_pack or str(r.get("source_pack") or "") == source_pack)
    ]
    return local[0] if len(local) == 1 else None


def compose_experience_draft(
    base: dict[str, Any],
    mission: dict[str, Any],
    schema: dict[str, Any],
) -> dict[str, Any]:
    """Compose a non-mutating Beast Studio draft from an Experience profile.

    This function never writes preferences. It resolves only content already
    visible to the current Studio schema. Board/Layout widgets are copied into
    the draft so downloaded Pack content remains read-only.
    """
    if not isinstance(base, dict) or not isinstance(mission, dict) or not isinstance(schema, dict):
        raise ExperienceDraftError("experience inputs must be objects")
    if not bool(mission.get("experience")):
        raise ExperienceDraftError("selected Mission does not define an Experience")
    if mission.get("requirements_met") is False:
        missing = mission.get("missing_capabilities") or []
        raise ExperienceDraftError(
            "Experience requirements are not met"
            + (": " + ", ".join(map(str, missing)) if missing else "")
        )

    draft = deepcopy(base)
    source_pack = str(mission.get("source_pack") or "")
    resolution: dict[str, Any] = {}
    warnings: list[str] = []

    theme = str(mission.get("theme") or "").strip()
    if theme:
        row = _find(theme, list(schema.get("themes") or []), source_pack=source_pack)
        if row:
            draft["theme"] = row["id"]
            resolution["theme"] = row["id"]
        else:
            warnings.append(f"theme unavailable: {theme}")

    face = str(mission.get("face_profile") or "").strip()
    if face:
        row = _find(face, list(schema.get("face_profiles") or []), source_pack=source_pack)
        if row:
            draft["face_profile"] = row["id"]
            resolution["face_profile"] = row["id"]
        else:
            warnings.append(f"face unavailable: {face}")

    animation = str(mission.get("animation_profile") or "").strip()
    if animation:
        row = _find(animation, list(schema.get("animation_profiles") or []), source_pack=source_pack)
        if row:
            draft["animation_profile"] = row["id"]
            resolution["animation_profile"] = row["id"]
        else:
            warnings.append(f"animation unavailable: {animation}")

    # An Experience Board/Layout becomes the editable Dashboard composition in
    # the draft. The source Pack remains read-only and can later be disabled
    # without destroying the user's applied copy.
    board_ref = str(mission.get("board") or "").strip()
    layout_ref = str(mission.get("layout") or "").strip()
    composition = None
    if board_ref:
        composition = _find(board_ref, list(schema.get("pack_boards") or []), source_pack=source_pack)
        if composition:
            resolution["board"] = composition["id"]
        else:
            warnings.append(f"board unavailable: {board_ref}")
    elif layout_ref:
        composition = _find(layout_ref, list(schema.get("pack_layouts") or []), source_pack=source_pack)
        if composition:
            resolution["layout"] = composition["id"]
        else:
            warnings.append(f"layout unavailable: {layout_ref}")

    if composition:
        draft["dashboard_widgets"] = deepcopy(list(composition.get("widgets") or []))
        draft["preview_board_id"] = ""
        draft["page"] = "dashboard"

    deck = str(mission.get("deck") or "").strip()
    if deck:
        decks = list(draft.get("context_decks") or schema.get("default_context_decks") or [])
        match = next((d for d in decks if str(d.get("id") or "") == deck), None)
        if match:
            draft["active_context_deck"] = deck
            resolution["deck"] = deck
        else:
            warnings.append(f"context deck unavailable: {deck}")

    return {
        "ok": True,
        "experience_id": str(mission.get("id") or ""),
        "experience_label": str(mission.get("label") or mission.get("id") or "Experience"),
        "draft": draft,
        "resolution": resolution,
        "warnings": warnings,
        "writes_preferences": False,
        "requires_explicit_apply": True,
        "source_pack": source_pack or None,
    }
