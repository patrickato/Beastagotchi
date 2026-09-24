from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
import time
from typing import Iterable


_ALLOWED_UPDATE_CLASSES = {"static", "ambient", "live", "interaction", "protected"}
_ALLOWED_RESOURCE_CLASSES = {"tiny", "light", "moderate", "heavy"}


@dataclass(frozen=True)
class SceneLayerSpec:
    """Semantic metadata for one visual layer.

    This is deliberately renderer-agnostic. A layer describes *what it means*
    and what truth/cost/touch contracts it owns; PIL remains an implementation
    detail of the current 480x320 Visual Runtime.
    """

    id: str
    kind: str
    bounds: tuple[int, int, int, int]
    z: int = 0
    signals: tuple[str, ...] = ()
    update_class: str = "live"
    cacheable: bool = False
    resource_class: str = "light"
    privacy: str = "normal"
    touch: str | None = None
    reduced_motion: str = "static"
    decorative: bool = False

    def __post_init__(self):
        if not self.id:
            raise ValueError("scene layer id is required")
        if not self.kind:
            raise ValueError("scene layer kind is required")
        if len(tuple(self.bounds)) != 4:
            raise ValueError("scene layer bounds must be x1,y1,x2,y2")
        x1, y1, x2, y2 = (int(v) for v in self.bounds)
        if x2 <= x1 or y2 <= y1:
            raise ValueError("scene layer bounds must have positive area")
        if self.update_class not in _ALLOWED_UPDATE_CLASSES:
            raise ValueError(f"invalid update class: {self.update_class}")
        if self.resource_class not in _ALLOWED_RESOURCE_CLASSES:
            raise ValueError(f"invalid resource class: {self.resource_class}")


@dataclass
class SceneLayerRecord:
    spec: SceneLayerSpec
    render_ms: float = 0.0
    renders: int = 0
    last_render_at: float | None = None

    def record(self, elapsed_ms: float, now: float | None = None) -> None:
        self.render_ms = float(elapsed_ms)
        self.renders += 1
        self.last_render_at = float(time.time() if now is None else now)

    def as_dict(self) -> dict:
        s = self.spec
        return {
            "id": s.id,
            "kind": s.kind,
            "bounds": list(s.bounds),
            "z": int(s.z),
            "signals": list(s.signals),
            "update_class": s.update_class,
            "cacheable": bool(s.cacheable),
            "resource_class": s.resource_class,
            "privacy": s.privacy,
            "touch": s.touch,
            "reduced_motion": s.reduced_motion,
            "decorative": bool(s.decorative),
            "render_ms": round(float(self.render_ms), 3),
            "renders": int(self.renders),
            "last_render_at": self.last_render_at,
        }


class SceneRuntime:
    """Small semantic registry/performance lens for the current rendered scene.

    It does not own telemetry polling or draw pixels. Renderers register their
    layers here so Studio/Doctor/Exact-Mirror/performance tooling can reason
    about the composition without scraping a screenshot.
    """

    def __init__(self) -> None:
        self.page_id: str | None = None
        self.scene_id: str | None = None
        self.theme_id: str | None = None
        self.started_at: float | None = None
        self.completed_at: float | None = None
        self._layers: dict[str, SceneLayerRecord] = {}
        self._order: list[str] = []

    def begin(self, *, page_id: str, scene_id: str | None = None,
              theme_id: str | None = None) -> None:
        self.page_id = str(page_id)
        self.scene_id = str(scene_id or f"page:{page_id}")
        self.theme_id = None if theme_id is None else str(theme_id)
        self.started_at = time.perf_counter()
        self.completed_at = None
        self._layers = {}
        self._order = []

    def set_scene(self, scene_id: str) -> None:
        self.scene_id = str(scene_id)

    def end(self) -> None:
        self.completed_at = time.perf_counter()

    def register(self, spec: SceneLayerSpec, *, render_ms: float = 0.0) -> SceneLayerRecord:
        rec = self._layers.get(spec.id)
        if rec is None:
            rec = SceneLayerRecord(spec=spec)
            self._layers[spec.id] = rec
            self._order.append(spec.id)
        elif rec.spec != spec:
            # A semantic id must mean one thing within a scene. Replacing it
            # silently would make Studio/Inspect bounds and bindings untruthful.
            raise ValueError(f"scene layer id reused with different metadata: {spec.id}")
        rec.record(render_ms)
        return rec

    @contextmanager
