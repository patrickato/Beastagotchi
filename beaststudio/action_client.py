from __future__ import annotations

import json
import socket
from typing import Any


class BeastActionClient:
    def __init__(self, path: str = "/run/beastagotchi/action.sock", timeout: float = 90.0) -> None:
        self.path = path
        self.timeout = float(timeout)

    def request(self, op: str, action: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        req = {"op": str(op), "action": str(action), "payload": dict(payload or {})}
        data = (json.dumps(req, separators=(",", ":")) + "\n").encode()
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
            s.settimeout(self.timeout)
            s.connect(self.path)
            s.sendall(data)
            f = s.makefile("rb")
            raw = f.readline(512_000)
        obj = json.loads(raw.decode("utf-8", errors="replace"))
        return obj if isinstance(obj, dict) else {"ok": False, "error": "invalid action response"}

    def plan(self, action: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        return self.request("plan", action, payload)

    def perform(self, action: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        return self.request("perform", action, payload)
