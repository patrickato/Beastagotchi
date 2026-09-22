from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, Protocol


class PresentationBrokerError(RuntimeError):
    pass


class PresentationAdapter(Protocol):
    def prepare_release(self) -> dict: ...
    def release(self) -> dict: ...
    def acquire(self) -> dict: ...
    def health(self) -> dict: ...


@dataclass
class PresentationLease:
    owner: str
    acquired_at: float
    generation: int
    status: str = "active"


class PresentationBroker:
    """Transactional ownership broker for framebuffer/touch presentation.

    The broker deliberately does not know how Pwnagotchi, Theme Manager, or
    Beast UI implement display ownership. Concrete adapters own those details.
    This keeps the control plane small, testable, and upstream-friendly.

    A successful switch follows:
      prepare old -> release old -> acquire new -> health new -> persist

    If acquisition/health fails after release, the broker attempts to reacquire
    the previous owner and leaves the persisted lease unchanged unless rollback
    itself succeeds.
    """

    OWNERS = ("pwn-native", "korrie-theme-manager", "beast-ui")

    def __init__(self, path: str = "/var/lib/beastagotchi/presentation.json") -> None:
        self.path = Path(path)
        self.adapters: dict[str, PresentationAdapter] = {}
        self.lease = self._load()

    def register(self, owner: str, adapter: PresentationAdapter) -> None:
        owner = self._validate_owner(owner)
        self.adapters[owner] = adapter

    def status(self) -> dict:
        return {
            "ok": True,
            "lease": asdict(self.lease),
            "available_owners": [o for o in self.OWNERS if o in self.adapters],
            "known_owners": list(self.OWNERS),
        }

    def plan_switch(self, target: str) -> dict:
        target = self._validate_owner(target)
        blockers = []
        if target not in self.adapters:
            blockers.append(f"no adapter registered for {target}")
        if self.lease.owner not in self.adapters:
            blockers.append(f"no adapter registered for current owner {self.lease.owner}")
        return {
            "allowed": not blockers,
            "operation": "presentation.switch",
            "current": self.lease.owner,
            "target": target,
            "noop": target == self.lease.owner,
            "blockers": blockers,
        }

    def switch(self, target: str) -> dict:
        target = self._validate_owner(target)
        if target == self.lease.owner:
            return {"ok": True, "changed": False, "owner": target, "lease": asdict(self.lease)}

        plan = self.plan_switch(target)
        if not plan["allowed"]:
            raise PresentationBrokerError("; ".join(plan["blockers"]))

        previous = self.lease.owner
        old = self.adapters[previous]
        new = self.adapters[target]
        trace: list[dict] = []

        def step(name: str, fn: Callable[[], dict]) -> dict:
            result = dict(fn() or {})
            result.setdefault("ok", False)
            trace.append({"step": name, "result": result})
            if not result.get("ok"):
                raise PresentationBrokerError(f"{name} failed: {result.get('error') or result}")
            return result

        released = False
        try:
            step("prepare_release", old.prepare_release)
            step("release", old.release)
            released = True
            step("acquire", new.acquire)
            step("health", new.health)
        except Exception as exc:
            rollback = {"attempted": released, "ok": not released}
            if released:
                try:
                    reacquire = dict(old.acquire() or {})
                    health = dict(old.health() or {}) if reacquire.get("ok") else {"ok": False}
                    rollback = {
                        "attempted": True,
                        "ok": bool(reacquire.get("ok") and health.get("ok")),
                        "acquire": reacquire,
                        "health": health,
                    }
                except Exception as rollback_exc:
                    rollback = {"attempted": True, "ok": False, "error": str(rollback_exc)}
            return {
                "ok": False,
                "changed": False,
                "owner": previous,
                "target": target,
                "error": str(exc),
                "rollback": rollback,
                "trace": trace,
            }

        self.lease = PresentationLease(
            owner=target,
            acquired_at=time.time(),
            generation=int(self.lease.generation) + 1,
            status="active",
        )
        self._persist()
        return {
            "ok": True,
            "changed": True,
            "owner": target,
            "previous_owner": previous,
            "lease": asdict(self.lease),
            "trace": trace,
        }

    def _validate_owner(self, owner: str) -> str:
        owner = str(owner or "").strip()
        if owner not in self.OWNERS:
            raise PresentationBrokerError(f"unsupported presentation owner: {owner!r}")
        return owner

    def _load(self) -> PresentationLease:
        try:
            obj = json.loads(self.path.read_text())
            owner = self._validate_owner(str(obj.get("owner") or "beast-ui"))
            return PresentationLease(
                owner=owner,
                acquired_at=float(obj.get("acquired_at") or time.time()),
                generation=max(0, int(obj.get("generation") or 0)),
                status=str(obj.get("status") or "active"),
            )
        except FileNotFoundError:
            return PresentationLease("beast-ui", time.time(), 0)
        except Exception:
            # Corrupt state must never invent a third-party owner. Beast UI is
            # the conservative development default until explicit discovery.
            return PresentationLease("beast-ui", time.time(), 0, "recovered")

    def _persist(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        tmp.write_text(json.dumps(asdict(self.lease), indent=2) + "\n")
        tmp.replace(self.path)
