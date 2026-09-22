from __future__ import annotations

import time
from typing import Any


class SemanticEngine:
    """Turns noisy state into low-volume meaningful events.

    It is deliberately observational. It never changes radio behavior or arms Lab Mode.
    GPS lock events are debounced here because consumer GPS receivers can briefly toggle
    between 2D/no-fix while satellites are being reacquired.
    """

    def __init__(self, state, store=None) -> None:
        self.state = state
        self.store = store
        self.prev: dict[str, Any] = {}
        self.seen_bssids: set[str] = set()
        self._last_ap_event = 0.0
        self._gps_reported: bool | None = None
        self._gps_candidate: bool | None = None
        self._gps_candidate_since = 0.0
        self.gps_acquire_confirm_sec = 3.0
        self.gps_loss_confirm_sec = 5.0

    @staticmethod
    def _temp_band(value: Any) -> str:
        try:
            v = float(value)
        except Exception:
            return "unknown"
        if v >= 80.0:
            return "critical"
        if v >= 75.0:
            return "hot"
        if v >= 65.0:
            return "warm"
        return "normal"

    def _gps_tick(self, snap: dict[str, Any], out: list[tuple[str, str, dict[str, Any], str]]) -> None:
        raw = bool(snap.get("gps.fix"))
        now = time.monotonic()
        if self._gps_reported is None:
            self._gps_reported = raw
            self._gps_candidate = None
            self._gps_candidate_since = 0.0
        elif raw == self._gps_reported:
            self._gps_candidate = None
            self._gps_candidate_since = 0.0
        else:
            if self._gps_candidate != raw:
                self._gps_candidate = raw
                self._gps_candidate_since = now
            threshold = self.gps_acquire_confirm_sec if raw else self.gps_loss_confirm_sec
            if now - self._gps_candidate_since >= threshold:
                old = self._gps_reported
                self._gps_reported = raw
                self._gps_candidate = None
                self._gps_candidate_since = 0.0
                if raw:
                    out.append(("gps.lock_acquired", "gps", {
                        "satellites": snap.get("gps.satellites_used"),
                        "accuracy_m": snap.get("gps.accuracy_m"),
                        "confirm_sec": threshold,
                    }, "info"))
                elif old:
                    out.append(("gps.lock_lost", "gps", {"confirm_sec": threshold}, "warning"))

        pending = None if self._gps_candidate is None else ("acquire" if self._gps_candidate else "loss")
        self.state.update_many("semantic", {
            "gps.fix.debounced": bool(self._gps_reported),
            "gps.fix.transition_pending": pending,
        }, priority=85)

    def tick(self) -> list[tuple[str, str, dict[str, Any], str]]:
        snap = self.state.snapshot(False)
        out: list[tuple[str, str, dict[str, Any], str]] = []

        def changed(key: str) -> tuple[bool, Any, Any]:
            new = snap.get(key)
            if key not in self.prev:
                self.prev[key] = new
                return False, None, new
            old = self.prev.get(key)
            self.prev[key] = new
            return old != new, old, new

        # Context transitions are presentation-only and safe.
        did, old, new = changed("context.mode.effective")
        if did and new:
            out.append(("context.mode_changed", "context", {"from": old, "to": new}, "info"))

        self._gps_tick(snap, out)

        did, old, new = changed("health.core.state")
        if did and new:
            sev = "warning" if new != "healthy" else "info"
            out.append(("system.health_changed", "health", {"from": old, "to": new}, sev))

        # Temperature bands generate transitions only, not repeated alerts.
        band = self._temp_band(snap.get("system.temp.cpu_c"))
        old_band = self.prev.get("_semantic.temp_band")
        self.prev["_semantic.temp_band"] = band
        if old_band is not None and band != old_band:
            sev = "warning" if band in {"hot", "critical"} else "info"
            out.append(("system.thermal_band", "system", {
                "from": old_band,
                "to": band,
                "temp_c": snap.get("system.temp.cpu_c"),
            }, sev))

        # Bettercap AP list is ephemeral, but BSSID first-seen-in-this-core-session is useful.
        aps = snap.get("wifi.aps") or []
        newly_seen = []
        if isinstance(aps, list):
            for ap in aps:
                if not isinstance(ap, dict):
                    continue
                bssid = str(ap.get("mac") or ap.get("bssid") or "").lower()
                if not bssid:
                    continue
                if bssid not in self.seen_bssids:
                    self.seen_bssids.add(bssid)
                    newly_seen.append({
                        "bssid": bssid,
                        "ssid": ap.get("hostname") or ap.get("ssid") or "<hidden>",
                        "vendor": ap.get("vendor") or "",
                        "channel": ap.get("channel"),
                        "rssi": ap.get("rssi"),
                        "encryption": ap.get("encryption") or "",
                    })
        # Batch discoveries so event feed does not explode on startup.
        now = time.time()
        lifetime = {"new_count": 0, "total": None, "new_bssids": []}
        if newly_seen and self.store is not None:
            try:
                lifetime = self.store.record_wifi_encounters(newly_seen, now)
            except Exception:
                lifetime = {"new_count": 0, "total": None, "new_bssids": []}
        if newly_seen and now - self._last_ap_event >= 1.0:
            self._last_ap_event = now
            out.append(("wifi.ap_discovered", "bettercap", {
                "count": len(newly_seen),
                "aps": newly_seen[:12],
                "session_unique": len(self.seen_bssids),
                "lifetime_new_count": int(lifetime.get("new_count") or 0),
                "lifetime_total": lifetime.get("total"),
            }, "info"))

        values = {
            "wifi.encounters.session_unique": len(self.seen_bssids),
            "system.thermal.band": band,
        }
        if lifetime.get("total") is not None:
            values["wifi.encounters.lifetime_unique"] = int(lifetime["total"])
        elif self.store is not None:
            try: values["wifi.encounters.lifetime_unique"] = self.store.count_wifi_encounters()
            except Exception: pass
        if self.store is not None:
            try:
                summary = self.store.encounter_summary(1)
                values["wifi.encounters.lifetime_vendors"] = int(summary.get("vendor_count") or 0)
            except Exception:
                pass
        self.state.update_many("semantic", values, priority=85)
        return out
