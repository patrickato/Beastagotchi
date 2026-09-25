from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any


POLICIES = ("manual", "notify", "auto_stage", "auto_install")
_COMPONENT_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9:._-]{0,127}$")


class UpdatePolicyError(ValueError):
    pass


class UpdatePolicyStore:
    """Unprivileged user intent for the future Update Center.

    This store can never install software. It only records policy choices that
    Beast Core exposes back to the UI.
    """

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def load(self) -> dict[str, Any]:
        try:
            obj = json.loads(self.path.read_text())
            raw = obj.get("policies") if isinstance(obj, dict) else {}
            if not isinstance(raw, dict):
                raw = {}
        except Exception:
            raw = {}
        clean = {
            str(k): str(v)
            for k, v in raw.items()
            if _COMPONENT_RE.fullmatch(str(k)) and str(v) in POLICIES
        }
        return {"schema": 1, "policies": clean, "allowed_policies": list(POLICIES)}

    def set_policy(self, component: str, policy: str) -> dict[str, Any]:
        component = str(component or "").strip()
        policy = str(policy or "").strip()
        if not _COMPONENT_RE.fullmatch(component):
            raise UpdatePolicyError("invalid component id")
        if policy not in POLICIES:
            raise UpdatePolicyError("invalid update policy")
        obj = self.load()
        obj["policies"][component] = policy
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        tmp.write_text(json.dumps({"schema": 1, "policies": obj["policies"]}, indent=2, sort_keys=True) + "\n")
        os.chmod(tmp, 0o600)
        tmp.replace(self.path)
        return self.load()
