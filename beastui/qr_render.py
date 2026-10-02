from __future__ import annotations

from typing import Any


def qr_backend_status() -> dict[str, Any]:
    """Report optional QR renderer availability without making it a Core dependency."""
    try:
        import qrcode  # type: ignore
        version = getattr(qrcode, "__version__", None)
        return {
            "available": True,
            "backend": "python-qrcode",
            "version": str(version) if version is not None else None,
        }
    except Exception as exc:
        return {
            "available": False,
            "backend": None,
            "version": None,
            "error": type(exc).__name__,
        }


def qr_matrix(text: str, *, error_correction: str = "M") -> list[list[bool]]:
    """Return a real QR module matrix using an optional lightweight backend.

    The Beast base UI remains able to run without this dependency. Callers must
    show an explicit unavailable state rather than substituting decorative QR-like
    art when the encoder is absent.
    """
    raw = str(text or "")
    if not raw:
        raise ValueError("QR payload is empty")
    try:
        import qrcode  # type: ignore
        from qrcode.constants import (
            ERROR_CORRECT_L,
            ERROR_CORRECT_M,
            ERROR_CORRECT_Q,
            ERROR_CORRECT_H,
        )
    except Exception as exc:
        raise RuntimeError("QR renderer dependency is not installed") from exc

    level = str(error_correction or "M").upper()
    ec = {
        "L": ERROR_CORRECT_L,
        "M": ERROR_CORRECT_M,
        "Q": ERROR_CORRECT_Q,
        "H": ERROR_CORRECT_H,
    }.get(level, ERROR_CORRECT_M)
    qr = qrcode.QRCode(
        version=None,
        error_correction=ec,
        box_size=1,
        border=4,
    )
    qr.add_data(raw)
    qr.make(fit=True)
    return [[bool(cell) for cell in row] for row in qr.get_matrix()]


def draw_qr(draw, box: tuple[int, int, int, int], text: str, *, error_correction: str = "M") -> dict[str, Any]:
    """Draw a high-contrast QR into a Pillow ImageDraw target.

    QR modules intentionally use black/white rather than theme colors; scan
    reliability outranks visual theming for this transport surface.
    """
    matrix = qr_matrix(text, error_correction=error_correction)
    rows = len(matrix)
    cols = len(matrix[0]) if rows else 0
    if rows <= 0 or cols <= 0:
        raise RuntimeError("QR backend returned an empty matrix")

    x1, y1, x2, y2 = [int(x) for x in box]
    width = max(1, x2 - x1 + 1)
    height = max(1, y2 - y1 + 1)
    scale = min(width // cols, height // rows)
    if scale < 2:
        raise RuntimeError(f"QR frame is too dense for this display ({cols} modules, {width}x{height}px)")
    qr_w = cols * scale
    qr_h = rows * scale
    ox = x1 + (width - qr_w) // 2
    oy = y1 + (height - qr_h) // 2

    draw.rectangle((x1, y1, x2, y2), fill=(255, 255, 255))
    for yy, row in enumerate(matrix):
        for xx, on in enumerate(row):
            if on:
                px = ox + xx * scale
                py = oy + yy * scale
                draw.rectangle((px, py, px + scale - 1, py + scale - 1), fill=(0, 0, 0))
    return {
        "backend": "python-qrcode",
        "modules": cols,
        "scale_px": scale,
        "rendered_px": [qr_w, qr_h],
        "error_correction": str(error_correction or "M").upper(),
    }
