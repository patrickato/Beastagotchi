from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from PIL import Image


@dataclass(frozen=True)
class Viewport:
    x: int
    y: int
    width: int
    height: int


class DisplayTransform:
    """Map Beast's logical canvas to a physical display and back.

    Beast's current reference canvas remains 480x320.  A different physical
    display can already be used in compatibility mode without distorting the
    UI: the logical frame is aspect-preserving scaled into a centered viewport
    and unused pixels become letter/pillar bars.  Later responsive layouts can
    opt into the full physical canvas without changing the display/touch
    boundary again.
    """

    def __init__(self, logical_size=(480, 320), physical_size=(480, 320), *,
                 mode: str = "fit", resample: str = "bilinear",
                 background=(0, 0, 0)) -> None:
        self.logical_width = max(1, int(logical_size[0]))
        self.logical_height = max(1, int(logical_size[1]))
        self.physical_width = max(1, int(physical_size[0]))
        self.physical_height = max(1, int(physical_size[1]))
        self.mode = str(mode or "fit").lower()
        if self.mode not in {"fit", "stretch", "native"}:
            raise ValueError(f"unsupported display transform mode: {self.mode}")
        self.resample = str(resample or "bilinear").lower()
        if self.resample not in {"nearest", "bilinear", "bicubic", "lanczos"}:
            raise ValueError(f"unsupported resample mode: {self.resample}")
        self.background = tuple(background)
        self.viewport = self._viewport()

    def _viewport(self) -> Viewport:
        lw, lh = self.logical_width, self.logical_height
        pw, ph = self.physical_width, self.physical_height
        if self.mode == "stretch":
            return Viewport(0, 0, pw, ph)
        if self.mode == "native":
            w, h = min(lw, pw), min(lh, ph)
            return Viewport((pw - w) // 2, (ph - h) // 2, w, h)
        scale = min(pw / lw, ph / lh)
        w = max(1, int(round(lw * scale)))
        h = max(1, int(round(lh * scale)))
        return Viewport((pw - w) // 2, (ph - h) // 2, w, h)

    def _pil_resample(self):
        table = {
            "nearest": Image.Resampling.NEAREST,
            "bilinear": Image.Resampling.BILINEAR,
            "bicubic": Image.Resampling.BICUBIC,
            "lanczos": Image.Resampling.LANCZOS,
        }
        return table[self.resample]

    @property
    def identity(self) -> bool:
        v = self.viewport
        return (
            self.logical_width == self.physical_width
            and self.logical_height == self.physical_height
            and v.x == 0 and v.y == 0
            and v.width == self.logical_width and v.height == self.logical_height
        )

    def to_physical(self, image: Image.Image) -> Image.Image:
        expected = (self.logical_width, self.logical_height)
        if image.size != expected:
            raise ValueError(f"expected logical image {expected}, got {image.size}")
        if self.identity:
            return image
        v = self.viewport
        canvas = Image.new("RGB", (self.physical_width, self.physical_height), self.background)
        if self.mode == "native":
            crop = image.crop((0, 0, v.width, v.height))
            canvas.paste(crop, (v.x, v.y))
            return canvas
        scaled = image.resize((v.width, v.height), self._pil_resample())
        canvas.paste(scaled, (v.x, v.y))
        return canvas

    def to_logical_point(self, x: float, y: float) -> tuple[int, int] | None:
        v = self.viewport
        if x < v.x or y < v.y or x >= v.x + v.width or y >= v.y + v.height:
            return None
        lx = (float(x) - v.x) * self.logical_width / max(1, v.width)
        ly = (float(y) - v.y) * self.logical_height / max(1, v.height)
        return (
            max(0, min(self.logical_width - 1, int(lx))),
            max(0, min(self.logical_height - 1, int(ly))),
        )

    def to_physical_point(self, x: float, y: float) -> tuple[int, int]:
        v = self.viewport
        px = v.x + float(x) * v.width / self.logical_width
        py = v.y + float(y) * v.height / self.logical_height
        return (
            max(0, min(self.physical_width - 1, int(round(px)))),
            max(0, min(self.physical_height - 1, int(round(py)))),
        )

    def metadata(self) -> dict[str, Any]:
        v = self.viewport
        return {
            "logical": {"width": self.logical_width, "height": self.logical_height},
            "physical": {"width": self.physical_width, "height": self.physical_height},
            "mode": self.mode,
            "resample": self.resample,
            "identity": self.identity,
            "viewport": {"x": v.x, "y": v.y, "width": v.width, "height": v.height},
            "responsive_layout": False,
            "compatibility_scaling": not self.identity,
        }
