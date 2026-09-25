from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
import time
from typing import Iterable


_ALLOWED_UPDATE_CLASSES = {"static", "ambient", "live", "interaction", "protected"}
_ALLOWED_RESOURCE_CLASSES = {"tiny", "light", "moderate", "heavy"}


@dataclass(frozen=True)
class SceneLayerSpec:
    """Semantic metadata for one visual layer."""

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
    """Semantic layer registry/performance lens for the current rendered scene.

    The runtime does not poll telemetry or draw pixels. Renderers publish layer
    meaning, bounds, signal bindings and cost so Studio/Inspect/Exact-Mirror
    tooling can reason about a scene without scraping screenshots.
    """

    def __init__(self) -> None:
        self.page_id: str | None = None
        self.scene_id: str | None = None
        self.theme_id: str | None = None
        self.started_at: float | None = None
        self.completed_at: float | None = None
        self._layers: dict[str, SceneLayerRecord] = {}
        self._order: list[str] = []
        self._signal_values: dict[str, object] = {}
        self._changed_signals: set[str] = set()

    def begin(self, *, page_id: str, scene_id: str | None = None,
              theme_id: str | None = None) -> None:
        self.page_id = str(page_id)
        self.scene_id = str(scene_id or f"page:{page_id}")
        self.theme_id = None if theme_id is None else str(theme_id)
        self.started_at = time.perf_counter()
        self.completed_at = None
        self._layers = {}
        self._order = []
        self._changed_signals = set()

    def set_scene(self, scene_id: str) -> None:
        self.scene_id = str(scene_id)

    def update_signals(self, values: dict[str, object]) -> set[str]:
        """Record a canonical signal snapshot and return keys whose values changed.

        Missing keys are not treated as changes: callers may publish partial state
        snapshots without accidentally dirtying unrelated layers.
        """
        changed: set[str] = set()
        for key, value in (values or {}).items():
            key = str(key)
            if key not in self._signal_values or self._signal_values[key] != value:
                changed.add(key)
            self._signal_values[key] = value
        self._changed_signals = changed
        return set(changed)

    def dirty_layer_ids(self, *, include_ambient: bool = True,
                        include_interaction: bool = True) -> list[str]:
        """Return semantic layers that need repaint under the current change set."""
        dirty: list[str] = []
        for layer_id in self._order:
            rec = self._layers[layer_id]
            spec = rec.spec
            if spec.update_class in {"static", "protected"}:
                continue
            if spec.update_class == "ambient":
                if include_ambient:
                    dirty.append(layer_id)
                continue
            if spec.update_class == "interaction":
                if include_interaction:
                    dirty.append(layer_id)
                continue
            if any(sig in self._changed_signals for sig in spec.signals):
                dirty.append(layer_id)
        return dirty

    def dirty_bounds(self, *, include_ambient: bool = True,
                     include_interaction: bool = True) -> list[tuple[int, int, int, int]]:
        """Return de-duplicated dirty rectangles in z/order sequence."""
        seen = set()
        out = []
        ids = set(self.dirty_layer_ids(
            include_ambient=include_ambient,
            include_interaction=include_interaction,
        ))
        for layer_id in self._order:
            if layer_id not in ids:
                continue
            bounds = tuple(int(v) for v in self._layers[layer_id].spec.bounds)
            if bounds not in seen:
                seen.add(bounds)
                out.append(bounds)
        return out

    def end(self) -> None:
        self.completed_at = time.perf_counter()

    def register(self, spec: SceneLayerSpec, *, render_ms: float = 0.0) -> SceneLayerRecord:
        rec = self._layers.get(spec.id)
        if rec is None:
            rec = SceneLayerRecord(spec=spec)
            self._layers[spec.id] = rec
            self._order.append(spec.id)
        elif rec.spec != spec:
            raise ValueError(f"scene layer id reused with different metadata: {spec.id}")
        rec.record(render_ms)
        return rec

    @contextmanager
    def layer(self, layer_id: str, kind: str, bounds,
              *, z: int = 0, signals: Iterable[str] = (),
              update_class: str = "live", cacheable: bool = False,
              resource_class: str = "light", privacy: str = "normal",
              touch: str | None = None, reduced_motion: str = "static",
              decorative: bool = False):
        spec = SceneLayerSpec(
            id=str(layer_id),
            kind=str(kind),
            bounds=tuple(int(v) for v in bounds),
            z=int(z),
            signals=tuple(str(x) for x in signals),
            update_class=str(update_class),
            cacheable=bool(cacheable),
            resource_class=str(resource_class),
            privacy=str(privacy),
            touch=None if touch is None else str(touch),
            reduced_motion=str(reduced_motion),
            decorative=bool(decorative),
        )
        started = time.perf_counter()
        try:
            yield spec
        finally:
            self.register(spec, render_ms=(time.perf_counter() - started) * 1000.0)

    def snapshot(self) -> dict:
        rows = [self._layers[k].as_dict() for k in self._order]
        total_ms = sum(float(row["render_ms"]) for row in rows)
        elapsed_ms = None
        if self.started_at is not None and self.completed_at is not None:
            elapsed_ms = max(0.0, (self.completed_at - self.started_at) * 1000.0)
        return {
            "page": self.page_id,
            "scene": self.scene_id,
            "theme": self.theme_id,
            "layer_count": len(rows),
            "layer_render_ms": round(total_ms, 3),
            "scene_elapsed_ms": None if elapsed_ms is None else round(elapsed_ms, 3),
            "changed_signals": sorted(self._changed_signals),
            "dirty_layers": self.dirty_layer_ids(),
            "dirty_bounds": [list(x) for x in self.dirty_bounds()],
            "layers": rows,
        }
