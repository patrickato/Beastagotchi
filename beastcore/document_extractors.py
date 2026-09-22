from __future__ import annotations

import importlib.util
import re
import zipfile
from pathlib import Path
from typing import Any

_TAG_RE = re.compile(r"<[^>]+>")
_SPACE_RE = re.compile(r"\s+")


def _clean(text: str, limit: int) -> str:
    return _SPACE_RE.sub(" ", str(text or "")).strip()[:limit]


def capabilities() -> dict[str, Any]:
    return {
        "text": True,
        "html": True,
        "epub": True,
        "pdf_pymupdf": bool(importlib.util.find_spec("fitz")),
        "pdf_pypdf": bool(importlib.util.find_spec("pypdf")),
        "zim": False,
    }


def extract_pdf(path: Path, limit: int) -> tuple[str, str]:
    if importlib.util.find_spec("fitz"):
        try:
            import fitz  # type: ignore
            parts=[];used=0
            with fitz.open(str(path)) as doc:
                for page in doc:
                    text=page.get_text("text") or ""
                    if text:
                        parts.append(text);used+=len(text)
                    if used>=limit:
                        break
            return _clean("\n".join(parts),limit), "pymupdf"
        except Exception:
            pass
    if importlib.util.find_spec("pypdf"):
        try:
            from pypdf import PdfReader  # type: ignore
            parts=[];used=0
            for page in PdfReader(str(path)).pages:
                text=page.extract_text() or ""
                if text:
                    parts.append(text);used+=len(text)
                if used>=limit:
                    break
            return _clean("\n".join(parts),limit), "pypdf"
        except Exception:
            pass
    return "", "metadata_only"


def extract_epub(path: Path, limit: int) -> tuple[str, str]:
    """Dependency-free EPUB text extraction from XHTML/HTML members.

    This deliberately ignores styling/scripts and does not try to implement an
    EPUB reader.  It provides searchable offline text while the original file
    remains available for a richer desktop/web reader later.
    """
    try:
        parts=[];used=0
        with zipfile.ZipFile(path) as zf:
            names=[n for n in zf.namelist() if n.lower().endswith((".xhtml",".html",".htm"))]
            for name in names:
                raw=zf.read(name)
                text=raw.decode("utf-8",errors="replace")
                text=_TAG_RE.sub(" ",text)
                text=_clean(text,max(0,limit-used))
                if text:
                    parts.append(text);used+=len(text)
                if used>=limit:
                    break
        return _clean(" ".join(parts),limit), "epub_zip"
    except Exception:
        return "", "metadata_only"


def extract(path: Path, limit: int, text_exts: set[str]) -> tuple[str, str]:
    ext=path.suffix.lower()
    if ext in text_exts:
        try:
            raw=path.read_bytes()[:limit]
            text=raw.decode("utf-8",errors="replace")
            if ext in {".html",".htm"}:
                text=_TAG_RE.sub(" ",text)
            return _clean(text,limit), "text"
        except Exception:
            return "", "metadata_only"
    if ext==".pdf":
        return extract_pdf(path,limit)
    if ext==".epub":
        return extract_epub(path,limit)
    return "", "metadata_only"
