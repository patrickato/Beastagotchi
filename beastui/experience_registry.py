from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from PIL import Image

from .beast_shell import build_shell_model
from .experience_atlas import render_atlas_home, render_atlas_recon
from .experience_forge import render_forge_home, render_forge_system
from .experience_habitat import render_habitat_home, render_habitat_beast
from .experience_monolith import render_monolith_home, render_monolith_overview
from .experience_observatory import render_observatory_home, render_observatory_spectrum
from .scene_runtime import SceneRuntime


Renderer = Callable[..., Image.Image]


@dataclass(frozen=True)
class ExperiencePageRenderer:
    experience_id: str
    page_id: str
    renderer: Renderer
    status: str = "prototype"
    reference_size: tuple[int, int] = (480, 320)


_REGISTRY: dict[tuple[str, str], ExperiencePageRenderer] = {}


def _register(experience_id: str, page_id: str, renderer: Renderer, *, status="prototype") -> None:
    key = (str(experience_id).strip().lower(), str(page_id).strip().lower())
    if key in _REGISTRY:
        raise ValueError(f"duplicate Experience renderer: {key[0]}:{key[1]}")
    _REGISTRY[key] = ExperiencePageRenderer(
        experience_id=key[0],
        page_id=key[1],
        renderer=renderer,
        status=status,
    )


_register("atlas", "home", render_atlas_home)
_register("atlas", "recon", render_atlas_recon)
_register("forge", "home", render_forge_home)
_register("forge", "system", render_forge_system)
_register("observatory", "home", render_observatory_home)
_register("observatory", "spectrum", render_observatory_spectrum)
_register("habitat", "home", render_habitat_home)
_register("habitat", "beast", render_habitat_beast)
_register("monolith", "home", render_monolith_home)
_register("monolith", "overview", render_monolith_overview)


def get_experience_renderer(experience_id: str, page_id: str) -> ExperiencePageRenderer | None:
    return _REGISTRY.get((
        str(experience_id or "").strip().lower(),
        str(page_id or "").strip().lower(),
    ))


def available_experience_pages(experience_id: str) -> tuple[str, ...]:
    """Return pages in authored/registration order, not alphabetical order.

    Navigation order is part of Experience grammar. Sorting accidentally made
    Habitat start at Beast before Home; registry insertion order preserves the
    deliberate Home -> secondary-page sequence for every built-in Experience.
    """
    eid = str(experience_id or "").strip().lower()
    return tuple(
        row.page_id
        for key, row in _REGISTRY.items()
        if key[0] == eid
    )


def render_experience_page(
    experience_id: str,
    page_id: str,
    state: dict[str, Any],
    *,
    scene_runtime: SceneRuntime | None = None,
    **kwargs,
) -> Image.Image:
    row = get_experience_renderer(experience_id, page_id)
    if row is None:
        raise KeyError(f"Experience page renderer unavailable: {experience_id}:{page_id}")

    # Every Experience receives the same semantic shell model before it paints
    # its own visual grammar. Renderers may adopt shell pieces incrementally,
    # but truth/attention/navigation semantics no longer need to be re-invented.
    render_state = dict(state or {})
    render_state["_beast_shell"] = build_shell_model(
        row.experience_id,
        row.page_id,
        render_state,
        available_experience_pages(row.experience_id),
    )
    return row.renderer(render_state, scene_runtime=scene_runtime, **kwargs)


def experience_renderer_catalog() -> list[dict[str, Any]]:
    return [
        {
            "experience_id": row.experience_id,
            "page_id": row.page_id,
            "status": row.status,
            "reference_size": list(row.reference_size),
        }
        for _, row in sorted(_REGISTRY.items())
    ]


def experience_renderer_summary() -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for row in experience_renderer_catalog():
        out.setdefault(row["experience_id"], []).append(row["page_id"])
    return out
