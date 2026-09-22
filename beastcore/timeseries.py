from __future__ import annotations

import time

DEFAULT_KEYS = [
    "system.cpu.total", "system.load.1m", "system.memory.used_pct", "system.temp.cpu_c",
    "storage.root.used_pct", "radio.primary.channel", "radio.primary.rx_bytes", "radio.primary.tx_bytes",
    "wifi.ap_count", "wifi.client_count", "wifi.handshake_ap_count",
    "pwnagotchi.handshakes", "pwnagotchi.deauths", "pwnagotchi.peers",
    "gps.speed_mps", "gps.hdop", "gps.satellites_used", "gps.satellites_visible",
    "context.motion.speed_mph",
    "power.battery.voltage_v", "power.battery.percent_estimate", "power.current_ma", "power.power_w",
]

class TimeSeriesSampler:
    def __init__(self, state, store, interval: float = 30.0, retention_days: int = 7) -> None:
        self.state = state; self.store = store
        self.interval = interval; self.retention_days = retention_days
        self.keys = list(DEFAULT_KEYS)
        self._last_prune = 0.0

    def sample(self) -> int:
        now = time.time(); rows = []
        snap = self.state.snapshot(False)
        for key in self.keys:
            value = snap.get(key)
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                meta = self.state.meta(key) or {}
                rows.append((now, key, value, meta.get("source", "unknown")))
        if rows: self.store.add_samples(rows)
        if now - self._last_prune > 3600:
            self.store.prune_samples(now - self.retention_days * 86400)
            self._last_prune = now
        return len(rows)
