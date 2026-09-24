from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps


def mix(a, b, t: float):
    t = max(0.0, min(1.0, float(t)))
    return tuple(int(a[i] * (1.0 - t) + b[i] * t) for i in range(3))


def alpha_panel(image: Image.Image, box, *, fill, outline=None, alpha=150, radius=8, width=1):
    """Composite a translucent panel without forcing the whole scene into card UI."""
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    rgba = tuple(fill[:3]) + (max(0, min(255, int(alpha))),)
    if outline is None:
        outline_rgba = None
    else:
        outline_rgba = tuple(outline[:3]) + (max(0, min(255, int(alpha + 45))),)
    d.rounded_rectangle(box, radius=max(0, int(radius)), fill=rgba, outline=outline_rgba, width=max(1, int(width)))
    image.paste(Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB"))


def ambient_glow(image: Image.Image, center, radius: int, color, *, strength=0.24):
    """Cheap radial light bloom suitable for 480x320 software rendering."""
    radius = max(4, int(radius))
    cx, cy = int(center[0]), int(center[1])
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    steps = 9
    for i in range(steps, 0, -1):
        frac = i / steps
        r = max(1, int(radius * frac))
        alpha = int(255 * float(strength) * (1.0 - frac) ** 1.45)
        d.ellipse((cx-r, cy-r, cx+r, cy+r), fill=tuple(color[:3]) + (alpha,))
    layer = layer.filter(ImageFilter.GaussianBlur(max(2, radius // 16)))
    image.paste(Image.alpha_composite(image.convert("RGBA"), layer).convert("RGB"))


def paste_scene_asset(
    image: Image.Image,
    path: str | Path,
    box,
    *,
    phase: float = 0.0,
    opacity: int = 255,
    brightness_pulse: float = 0.03,
    tint=None,
    tint_strength: float = 0.0,
    edge_fade: int = 0,
) -> bool:
    """Place concept-derived artwork as a true scene layer rather than a framed tile."""
    path = Path(path)
    if not path.is_file():
        return False
    try:
        x1, y1, x2, y2 = [int(v) for v in box]
        size = (max(1, x2-x1), max(1, y2-y1))
        with Image.open(path) as src:
            art = ImageOps.fit(src.convert("RGB"), size, method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
        pulse = 1.0 + float(brightness_pulse) * math.sin(float(phase) * 1.55)
        art = ImageEnhance.Brightness(art).enhance(max(0.5, pulse))
        if tint is not None and tint_strength > 0:
            wash = Image.new("RGB", art.size, tuple(tint[:3]))
            art = Image.blend(art, wash, max(0.0, min(1.0, float(tint_strength))))

        alpha = Image.new("L", art.size, max(0, min(255, int(opacity))))
        fade = max(0, min(int(edge_fade), art.size[0] // 2))
        if fade:
            ad = ImageDraw.Draw(alpha)
            for i in range(fade):
                a = int(255 * (i / max(1, fade-1)))
                ad.line((art.size[0]-fade+i, 0, art.size[0]-fade+i, art.size[1]), fill=min(a, opacity))
        rgba = art.convert("RGBA")
        rgba.putalpha(alpha)
        base = image.convert("RGBA")
        base.alpha_composite(rgba, (x1, y1))
        image.paste(base.convert("RGB"))
        return True
    except Exception:
        return False


def scene_particles(image: Image.Image, phase: float, color, *, count=12, region=(0, 34, 480, 278), alpha=80):
    """Deterministic low-cost ambient motion. Decorative only; never telemetry."""
    x1, y1, x2, y2 = region
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    tick = int(float(phase) * 17)
    for i in range(max(0, int(count))):
        seed = (i * 2654435761 + tick * 2246822519) & 0xFFFFFFFF
        x = x1 + seed % max(1, x2-x1)
        y = y1 + ((seed >> 11) % max(1, y2-y1))
        r = 1 if i % 4 else 2
        d.ellipse((x-r, y-r, x+r, y+r), fill=tuple(color[:3]) + (max(0, min(255, int(alpha))),))
    image.paste(Image.alpha_composite(image.convert("RGBA"), layer).convert("RGB"))
