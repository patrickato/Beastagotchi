from __future__ import annotations

import math
import time
import uuid
from typing import Any, Callable


class ExpeditionEngine:
    """Persistent field-session recorder with crash recovery and GPS route capture."""

    def __init__(self, state, store, *, clock: Callable[[], float] = time.time,
                 mono: Callable[[], float] = time.monotonic,
                 recovery_window_sec: float = 1800.0) -> None:
        self.state = state
        self.store = store
        self.clock = clock
        self.mono = mono
        self.recovery_window_sec = float(recovery_window_sec)
        self.active: dict[str, Any] | None = None
        self.known_aps: set[str] = set()
        self.last_point: dict[str, Any] | None = None
        self._last_checkpoint_mono = 0.0
        self._last_point_mono = 0.0
        self._events: list[tuple[str, str, dict[str, Any], str]] = []

    @staticmethod
    def _num(v: Any) -> float | None:
        try: return float(v) if v is not None else None
        except (TypeError, ValueError): return None

    @staticmethod
    def _haversine_m(a_lat: float, a_lon: float, b_lat: float, b_lon: float) -> float:
        r = 6371008.8
        p1 = math.radians(a_lat); p2 = math.radians(b_lat)
        dp = math.radians(b_lat-a_lat); dl = math.radians(b_lon-a_lon)
        h = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
        return 2*r*math.asin(min(1.0, math.sqrt(h)))

    def _capture_total(self) -> int:
        for key in ("captures.total", "pwnagotchi.cache.handshake_ap_count", "pwnagotchi.handshakes"):
            v = self.state.get(key)
            try:
                if v is not None: return int(v)
            except Exception: pass
        return 0

    def _xp_total(self) -> int:
        try: return int(self.state.get("progression.xp", 0) or 0)
        except Exception: return 0

    def _new_id(self, now: float) -> str:
        stamp = time.strftime("%Y%m%d-%H%M%S", time.localtime(now))
        return f"exp-{stamp}-{uuid.uuid4().hex[:6]}"

    def _ensure_active(self) -> None:
        if self.active is not None:
            return
        now = self.clock()
        row = self.store.active_expedition()
        if row and now - float(row.get("last_update") or row.get("started_at") or 0) <= self.recovery_window_sec:
            self.active = row
            self.active["recovered"] = 1
            self.store.update_expedition(row["id"], recovered=1, last_update=now)
            self.known_aps = set(self.store.expedition_ap_bssids(row["id"]))
            self.last_point = self.store.last_expedition_point(row["id"])
            self._events.append(("expedition.recovered", "expedition", {"id": row["id"]}, "info"))
            return
        if row:
            self.store.end_expedition(row["id"], now, "recovery_timeout", status="interrupted")
        eid = self._new_id(now)
        self.store.begin_expedition(eid, now, self._capture_total(), self._xp_total())
        self.active = self.store.get_expedition(eid)
        self.known_aps = set()
        self.last_point = None
        self._events.append(("expedition.started", "expedition", {"id": eid}, "info"))

    def _record_aps(self, now: float) -> int:
        if not self.active:
            return 0
        aps = self.state.get("wifi.aps", []) or []
        new_rows = []
        for ap in aps:
            if not isinstance(ap, dict):
                continue
            bssid = str(ap.get("bssid") or ap.get("mac") or "").strip().lower()
            if not bssid or bssid in self.known_aps:
                continue
            self.known_aps.add(bssid)
            new_rows.append({
                "bssid": bssid,
                "ssid": str(ap.get("ssid") or ap.get("hostname") or "<hidden>"),
                "vendor": str(ap.get("vendor") or ""),
                "channel": ap.get("channel"),
                "rssi": ap.get("rssi"),
                "ts": now,
            })
        if new_rows:
            self.store.record_expedition_aps(self.active["id"], new_rows)
        return len(self.known_aps)

    def _record_route(self, now: float, now_mono: float) -> tuple[int, float]:
        if not self.active or not bool(self.state.get("gps.fix", False)):
            return int(self.active.get("route_points") or 0) if self.active else 0, float(self.active.get("distance_m") or 0.0) if self.active else 0.0
        lat = self._num(self.state.get("gps.latitude")); lon = self._num(self.state.get("gps.longitude"))
        if lat is None or lon is None or not (-90 <= lat <= 90 and -180 <= lon <= 180):
            return int(self.active.get("route_points") or 0), float(self.active.get("distance_m") or 0.0)
        acc = self._num(self.state.get("gps.accuracy_m"))
        candidate = {"ts": now, "latitude": lat, "longitude": lon}
        dist = 0.0
        elapsed = 999.0
        if self.last_point:
            try:
                dist = self._haversine_m(float(self.last_point["latitude"]), float(self.last_point["longitude"]), lat, lon)
                elapsed = max(0.001, now - float(self.last_point["ts"]))
            except Exception:
                dist = 0.0
        # Save when movement is meaningful, or at least every 30 seconds while fixed.
        should_save = self.last_point is None or dist >= 3.0 or (now_mono - self._last_point_mono) >= 30.0
        if not should_save:
            return int(self.active.get("route_points") or 0), float(self.active.get("distance_m") or 0.0)
        # Reject impossible jump distance from totals but still preserve the raw point for diagnostics.
        add_dist = dist if (self.last_point is not None and (dist / elapsed) <= 90.0 and (acc is None or acc <= 150.0)) else 0.0
        self.store.add_expedition_point(
            self.active["id"], now, lat, lon,
            altitude_m=self._num(self.state.get("gps.altitude_m")),
            accuracy_m=acc,
            speed_mps=self._num(self.state.get("gps.speed_mps")),
            heading_deg=self._num(self.state.get("gps.heading_deg")),
            temp_c=self._num(self.state.get("system.temp.cpu_c")),
            cpu_pct=self._num(self.state.get("system.cpu.total")),
            governor=str(self.state.get("governor.mode", "FULL")),
        )
        self.last_point = candidate
        self._last_point_mono = now_mono
        points = int(self.active.get("route_points") or 0) + 1
        distance = float(self.active.get("distance_m") or 0.0) + add_dist
        self.active["route_points"] = points
        self.active["distance_m"] = distance
        self.active["gps_fix_samples"] = int(self.active.get("gps_fix_samples") or 0) + 1
        return points, distance

    def _summary_patch(self, now: float) -> dict[str, Any]:
        assert self.active is not None
        cur_caps = self._capture_total(); cur_xp = self._xp_total()
        start_caps = int(self.active.get("start_captures") or 0); start_xp = int(self.active.get("start_xp") or 0)
        temp = self._num(self.state.get("system.temp.cpu_c")); cpu = self._num(self.state.get("system.cpu.total")); bat = self._num(self.state.get("power.battery.percent_estimate"))
        max_temp = self._num(self.active.get("max_temp_c")); max_cpu = self._num(self.active.get("max_cpu_pct")); min_bat = self._num(self.active.get("min_battery_pct"))
        if temp is not None: max_temp = temp if max_temp is None else max(max_temp, temp)
        if cpu is not None: max_cpu = cpu if max_cpu is None else max(max_cpu, cpu)
        if bat is not None: min_bat = bat if min_bat is None else min(min_bat, bat)
        patch = {
            "last_update": now,
            "ap_unique": len(self.known_aps),
            "captures_delta": max(0, cur_caps-start_caps),
            "xp_delta": max(0, cur_xp-start_xp),
            "max_temp_c": max_temp,
            "max_cpu_pct": max_cpu,
            "min_battery_pct": min_bat,
        }
        self.active.update(patch)
        return patch

    def tick(self) -> tuple[dict[str, Any], list[tuple[str, str, dict[str, Any], str]]]:
        self._ensure_active()
        assert self.active is not None
        now = self.clock(); now_mono = self.mono()
        self._record_aps(now)
        self._record_route(now, now_mono)
        patch = self._summary_patch(now)
        if now_mono - self._last_checkpoint_mono >= 15.0:
            self.store.update_expedition(self.active["id"], **patch,
                                         distance_m=self.active.get("distance_m", 0.0),
                                         route_points=self.active.get("route_points", 0),
                                         gps_fix_samples=self.active.get("gps_fix_samples", 0))
            self._last_checkpoint_mono = now_mono
        events, self._events = self._events, []
        duration = max(0.0, now - float(self.active.get("started_at") or now))
        state_patch = {
            "expedition.active": True,
            "expedition.id": self.active["id"],
            "expedition.started_at": self.active.get("started_at"),
            "expedition.duration_sec": round(duration, 1),
            "expedition.recovered": bool(self.active.get("recovered")),
            "expedition.distance_m": round(float(self.active.get("distance_m") or 0.0), 1),
            "expedition.route_points": int(self.active.get("route_points") or 0),
            "expedition.ap_unique": len(self.known_aps),
            "expedition.captures_delta": int(self.active.get("captures_delta") or 0),
            "expedition.xp_delta": int(self.active.get("xp_delta") or 0),
            "expedition.max_temp_c": self.active.get("max_temp_c"),
            "expedition.max_cpu_pct": self.active.get("max_cpu_pct"),
            "expedition.min_battery_pct": self.active.get("min_battery_pct"),
        }
        return state_patch, events

    def checkpoint(self) -> tuple[str, dict[str, Any]] | None:
        """Durably flush the active Expedition without ending it.

        Beast Core service restarts and short device reboots are implementation
        details, not Expedition boundaries.  Keeping the row active lets the
        next Core instance recover the same trip inside ``recovery_window_sec``.
        """
        if self.active is None:
            return None
        now = self.clock()
        patch = self._summary_patch(now)
        patch.update({
            "distance_m": self.active.get("distance_m", 0.0),
            "route_points": self.active.get("route_points", 0),
            "gps_fix_samples": self.active.get("gps_fix_samples", 0),
        })
        self.store.update_expedition(self.active["id"], **patch)
        return self.active["id"], dict(self.active)

    def finish(self, reason: str = "core_stop") -> tuple[str, dict[str, Any]] | None:
        if self.active is None:
            return None
        now = self.clock()
        patch = self._summary_patch(now)
        patch.update({
            "distance_m": self.active.get("distance_m", 0.0),
            "route_points": self.active.get("route_points", 0),
            "gps_fix_samples": self.active.get("gps_fix_samples", 0),
        })
        self.store.end_expedition(self.active["id"], now, reason, status="complete", **patch)
        eid = self.active["id"]
        summary = self.store.get_expedition(eid) or dict(self.active)
        self.active = None
        return eid, summary
