from __future__ import annotations

from typing import Any


class OverviewEngine:
    """Derive a compact, truthful whole-device overview from canonical state.

    The overview never invents values. Missing inputs remain unavailable and
    attention items are driven by concrete service/health/storage/thermal state.
    """

    def __init__(self, state) -> None:
        self.state = state

    def _service(self, key: str, default: str = "unknown") -> str:
        value = self.state.get(key)
        return str(value if value is not None else default).lower()

    @staticmethod
    def _fmt_temp(v: Any) -> str:
        return f"{float(v):.0f}C" if isinstance(v, (int, float)) else "--"

    @staticmethod
    def _fmt_pct(v: Any) -> str:
        return f"{float(v):.0f}%" if isinstance(v, (int, float)) else "--"

    def tick(self) -> dict[str, Any]:
        health = str(self.state.get("health.core.state") or "starting").lower()
        pwn = self._service("pwnagotchi.service.state")
        better = self._service("bettercap.state")
        bridge = self._service("pwnagotchi.bridge.state", "missing")
        gps_state = str(self.state.get("gps.state") or ("fix" if self.state.get("gps.fix") else "unknown"))
        expedition = str(self.state.get("expedition.id") or "")
        root_ro = bool(self.state.get("storage.root.readonly"))
        root_used = self.state.get("storage.root.used_pct")
        temp = self.state.get("system.temp.cpu_c")
        governor = str(self.state.get("governor.mode") or "--")
        ap = self.state.get("wifi.ap_count")
        hs = self.state.get("pwnagotchi.handshakes")
        captures = self.state.get("captures.indexed_files", self.state.get("captures.total"))

        attention: list[dict[str, Any]] = []
        def add(code: str, title: str, detail: str, severity: str = "warning") -> None:
            attention.append({"code": code, "title": title, "detail": detail, "severity": severity})

        if pwn not in {"active", "running"}:
            add("pwnagotchi", "Pwnagotchi unavailable", f"service state: {pwn}", "critical")
        if better not in {"active", "running", "ready"}:
            add("bettercap", "Bettercap unavailable", f"service state: {better}", "critical")
        if bridge not in {"available", "active", "ready"}:
            add("bridge", "Beast bridge unavailable", f"bridge state: {bridge}")
        if root_ro:
            add("root_ro", "Root filesystem read-only", "persistent writes may fail", "critical")
        if isinstance(root_used, (int, float)) and float(root_used) >= 90:
            add("storage", "Storage nearly full", f"root filesystem {float(root_used):.1f}% used")
        if isinstance(temp, (int, float)) and float(temp) >= 80:
            add("thermal", "CPU temperature high", f"{float(temp):.1f} C")
        elif governor.upper() in {"REDUCED", "SURVIVAL"}:
            add("governor", "Resource governor active", governor.upper(), "attention")

        cards = [
            {"id":"radio","title":"RADIO","value":f"{ap if ap is not None else '--'} AP", "detail":f"CH {self.state.get('radio.primary.channel') or '--'} / {better.upper()}", "status":"ok" if better in {"active","running","ready"} else "critical"},
            {"id":"beast","title":"BEAST","value":f"LV {self.state.get('progression.level') or 1}", "detail":str(self.state.get('progression.stage') or 'Hatchling').upper(), "status":"ok" if health == "healthy" else health},
            {"id":"field","title":"FIELD","value":"EXP ACTIVE" if expedition else "NO EXP", "detail":f"GPS {gps_state.upper()[:14]}", "status":"ok" if self.state.get('gps.fix') else "info"},
            {"id":"captures","title":"CAPTURES","value":str(captures if captures is not None else '--'), "detail":f"HS {hs if hs is not None else '--'}", "status":"ok"},
            {"id":"system","title":"SYSTEM","value":self._fmt_temp(temp), "detail":f"CPU {self._fmt_pct(self.state.get('system.cpu.total'))} / {governor}", "status":"ok" if health == "healthy" else health},
            {"id":"storage","title":"STORAGE","value":self._fmt_pct(root_used), "detail":"READ ONLY" if root_ro else "ROOT", "status":"critical" if root_ro else "warning" if isinstance(root_used,(int,float)) and float(root_used)>=90 else "ok"},
        ]

        overall = "critical" if any(x["severity"] == "critical" for x in attention) else "attention" if attention else "healthy"
        return {
            "overview.state": overall,
            "overview.attention_count": len(attention),
            "overview.attention": attention,
            "overview.cards": cards,
            "overview.summary": {
                "health": health,
                "pwnagotchi": pwn,
                "bettercap": better,
                "bridge": bridge,
                "gps": gps_state,
                "governor": governor,
                "expedition_active": bool(expedition),
            },
        }
