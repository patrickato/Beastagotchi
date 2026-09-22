from __future__ import annotations

import io
import os
import time
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from PIL import Image, ImageFilter


@dataclass
class NativeFrameInfo:
    path: str
    available: bool = False
    width: int = 0
    height: int = 0
    age_sec: float | None = None
    mtime_ns: int = 0
    error: str | None = None
    rotation: int = 0


class NativePwnFrameSource:
    """Read the exact canvas that Jayofelony Pwnagotchi writes for its Web UI.

    Pwnagotchi's View always writes the composed UI canvas to
    /var/tmp/pwnagotchi/pwnagotchi.png via pwnagotchi.ui.web.update_frame().
    Beastagotchi can therefore keep Pwnagotchi's physical display renderer
    disabled while still presenting the *real* stock Pwnagotchi UI canvas.

    Reads are cached by mtime and decode failures keep the last known-good
    frame so a coincident write cannot blank the physical display.
    """

    DEFAULT_PATH = "/var/tmp/pwnagotchi/pwnagotchi.png"

    def __init__(self, path: str | os.PathLike[str] = DEFAULT_PATH, config_path: str | os.PathLike[str] = "/etc/pwnagotchi/config.toml"):
        self.path = Path(path)
        self.config_path = Path(config_path)
        self._mtime_ns = -1
        self._frame: Optional[Image.Image] = None
        self._error: str | None = None

    def _read_if_changed(self) -> Optional[Image.Image]:
        try:
            st = self.path.stat()
            if self._frame is not None and st.st_mtime_ns == self._mtime_ns:
                return self._frame
            # Read bytes first so Pillow never sees a file changing under it.
            data = self.path.read_bytes()
            with Image.open(io.BytesIO(data)) as src:
                frame = src.convert("L")
                frame.load()
            self._frame = frame
            self._mtime_ns = st.st_mtime_ns
            self._error = None
            return frame
        except Exception as exc:
            self._error = f"{type(exc).__name__}: {exc}"
            return self._frame


    def rotation(self) -> int:
        """Read the configured Pwnagotchi physical display rotation.

        The Web-UI PNG is written before Display applies its hardware rotation,
        so reproducing the original physical Pwnagotchi view also means applying
        the same configured 0/90/180/270 rotation here.
        """
        try:
            text=self.config_path.read_text(errors='replace')
            m=re.search(r'(?ms)^\[ui\.display\]\s*$.*?(?=^\[|\Z)', text)
            if not m: return 0
            r=re.search(r'(?m)^\s*rotation\s*=\s*([0-9]+)', m.group(0))
            if not r: return 0
            val=int(r.group(1)) % 360
            return val if val in {0,90,180,270} else 0
        except Exception:
            return 0

    def info(self) -> NativeFrameInfo:
        frame = self._read_if_changed()
        try:
            st = self.path.stat()
            age = max(0.0, time.time() - st.st_mtime)
            mt = st.st_mtime_ns
        except Exception:
            age = None
            mt = 0
        return NativeFrameInfo(
            path=str(self.path),
            available=frame is not None,
            width=frame.width if frame is not None else 0,
            height=frame.height if frame is not None else 0,
            age_sec=age,
            mtime_ns=mt,
            error=self._error,
            rotation=self.rotation(),
        )

    @staticmethod
    def _foreground_mask(frame: Image.Image) -> Image.Image:
        """Return 0/255 mask where 255 is Pwnagotchi ink/foreground.

        Stock Pwnagotchi can be configured inverted or non-inverted. Instead
        of assuming either polarity, use the dominant binary tone as the
        background. This preserves the exact glyphs/layout while letting Beast
        offer native Light and Dark views without restarting Pwnagotchi.
        """
        gray = frame.convert("L")
        bw = gray.point(lambda p: 255 if p >= 128 else 0, mode="1").convert("L")
        hist = bw.histogram()
        black = sum(hist[:128])
        white = sum(hist[128:])
        background_white = white >= black
        if background_white:
            return bw.point(lambda p: 255 - p)
        return bw

    @staticmethod
    def _fit_nearest(im: Image.Image, size: tuple[int, int]) -> Image.Image:
        if im.size == size:
            return im
        target_w, target_h = size
        src_w, src_h = im.size
        if src_w <= 0 or src_h <= 0:
            return Image.new("RGB", size, (0, 0, 0))
        scale = min(target_w / src_w, target_h / src_h)
        nw = max(1, int(round(src_w * scale)))
        nh = max(1, int(round(src_h * scale)))
        resized = im.resize((nw, nh), Image.Resampling.NEAREST)
        bg = resized.getpixel((0, 0))
        canvas = Image.new("RGB", size, bg)
        canvas.paste(resized, ((target_w - nw) // 2, (target_h - nh) // 2))
        return canvas

    def render(
        self,
        mode: str = "dark",
        size: tuple[int, int] = (480, 320),
        ink_color: tuple[int, int, int] = (255, 255, 255),
        background_color: tuple[int, int, int] | None = None,
        glow: bool | float = False,
    ) -> Optional[Image.Image]:
        frame = self._read_if_changed()
        if frame is None:
            return None
        mask = self._foreground_mask(frame)

        if mode == "raw":
            out = frame.convert("RGB")
        else:
            if mode == "light":
                bg = (255, 255, 255) if background_color is None else background_color
                ink = (0, 0, 0)
            elif mode == "chroma":
                bg = (0, 0, 0) if background_color is None else background_color
                ink = tuple(int(max(0, min(255, x))) for x in ink_color)
            else:
                bg = (0, 0, 0) if background_color is None else background_color
                ink = (255, 255, 255)

            out = Image.new("RGB", frame.size, bg)
            if mode == "chroma" and glow:
                strength=1.0 if glow is True else max(0.0,float(glow))
                soft = mask.filter(ImageFilter.GaussianBlur(radius=1.4+0.8*strength))
                glow_layer = Image.new("RGB", frame.size, tuple(max(0, int(c * min(0.60,0.24+0.14*strength))) for c in ink))
                out.paste(glow_layer, (0, 0), soft)
            ink_layer = Image.new("RGB", frame.size, ink)
            out.paste(ink_layer, (0, 0), mask)

        rotation=self.rotation()
        if rotation:
            out=out.rotate(rotation, expand=True)
        return self._fit_nearest(out, size)
