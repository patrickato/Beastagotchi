from __future__ import annotations

import os
from pathlib import Path


class PackFileError(ValueError):
    pass


class PackFileManager:
    """Bounded local upload sink for Beast Pack archives.

    Browser uploads can land only in the pack inbox. Validation/staging remains
    a separate privileged Beast Core transaction.
    """

    ALLOWED = (".tar.gz", ".tgz", ".zip")

    def __init__(self, root: str | Path = "/var/lib/beastagotchi/packs/inbox", max_bytes: int = 128 * 1024 * 1024) -> None:
        self.root = Path(root)
        self.max_bytes = int(max_bytes)

    @classmethod
    def _safe_name(cls, name: str) -> str:
        value = Path(str(name or "").strip()).name
        if not value or value in {".", ".."}:
            raise PackFileError("invalid pack filename")
        if not value.lower().endswith(cls.ALLOWED):
            raise PackFileError("Beast Pack must be .tar.gz, .tgz, or .zip")
        return value[:180]

    def save(self, name: str, data: bytes) -> dict:
        safe = self._safe_name(name)
        if not data or len(data) > self.max_bytes:
            raise PackFileError("empty or oversized Beast Pack upload")
        self.root.mkdir(parents=True, exist_ok=True)
        target = self.root / safe
        tmp = self.root / f".{safe}.upload"
        tmp.write_bytes(data)
        os.chmod(tmp, 0o640)
        tmp.replace(target)
        return {"ok": True, "name": safe, "size_bytes": len(data), "path": str(target)}
