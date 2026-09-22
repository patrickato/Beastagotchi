from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from .base import Collector


class AICapabilityCollector(Collector):
    """Read-only local AI capability discovery.

    Beast never installs or launches a model merely because it discovers one.
    This collector only exposes what is already present so the App Registry can
    remain capability-driven and uncluttered.
    """

    name = "ai"
    interval = 60.0
    priority = 30

    LLAMA_BINS = ("llama-server", "llama-cli", "main")
    WHISPER_BINS = ("whisper-cli", "whisper-server", "main")
    MODEL_ROOTS = (
        Path("/var/lib/beastagotchi/models"),
        Path("/home/pi/models"),
    )

    @staticmethod
    def _first_binary(names: tuple[str, ...]) -> str | None:
        for name in names:
            p = shutil.which(name)
            if p:
                return p
        return None

    def collect(self) -> dict[str, Any]:
        llama = self._first_binary(self.LLAMA_BINS)
        whisper = self._first_binary(self.WHISPER_BINS)
        models: list[dict[str, Any]] = []
        seen: set[str] = set()
        for root in self.MODEL_ROOTS:
            if not root.is_dir():
                continue
            for fp in root.rglob("*"):
                if not fp.is_file() or fp.suffix.lower() not in {".gguf", ".bin"}:
                    continue
                try:
                    rp = str(fp.resolve())
                    if rp in seen:
                        continue
                    seen.add(rp)
                    st = fp.stat()
                    models.append({
                        "name": fp.name,
                        "path": str(fp),
                        "size_bytes": int(st.st_size),
                        "kind": "gguf" if fp.suffix.lower() == ".gguf" else "model",
                    })
                except OSError:
                    continue
        models.sort(key=lambda x: x["name"].lower())
        return {
            "ai.local.available": bool(llama or whisper or models),
            "ai.llama.available": bool(llama),
            "ai.llama.binary": llama,
            "ai.whisper.available": bool(whisper),
            "ai.whisper.binary": whisper,
            "ai.models.count": len(models),
            "ai.models.items": models[:64],
            "ai.operator.backend": "unconfigured",
        }
