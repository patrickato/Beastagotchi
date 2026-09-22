from __future__ import annotations

import threading
import time

from .api_client import BeastAPI


class DataFeed(threading.Thread):
    """Background Beast Core reader with batched localhost requests.

    UI rendering never blocks on the API. State+events are fetched together;
    every history stream plus channel-history and Expedition route data are
    fetched together. This eliminates the old burst of one HTTP connection per
    graph key and is both faster and cooler on the Pi.
    """

    def __init__(self, dirty_event: threading.Event, state_interval: float = 0.5, history_interval: float = 5.0, extra_history_keys=()):
        super().__init__(name='beastui-datafeed', daemon=True)
        self.api = BeastAPI()
        self.dirty = dirty_event
        self.state_interval = max(0.2, float(state_interval))
        self.history_interval = max(1.0, float(history_interval))
        self.stop_event = threading.Event()
        self.lock = threading.RLock()
        self.state: dict = {}
        self.events: list = []
        self.histories: dict[str, list] = {}
        self.aux: dict = {}
        self.last_error: str | None = None
        self.last_state_at = 0.0
        self.last_history_at = 0.0
        self._live_sig = None
        self.base_keys = ('system.cpu.total','system.temp.cpu_c','system.memory.used_pct','wifi.ap_count','wifi.client_count','wifi.handshake_ap_count','pwnagotchi.handshakes','radio.primary.channel','gps.satellites_used','context.motion.speed_mph','power.battery.percent_estimate','power.power_w')
        self.keys = tuple(dict.fromkeys(self.base_keys + tuple(str(x) for x in extra_history_keys if x)))

    def set_extra_history_keys(self, keys):
        with self.lock:
            self.keys = tuple(dict.fromkeys(self.base_keys + tuple(str(x) for x in keys if x)))

    def snapshot(self):
        with self.lock:
            return dict(self.state), list(self.events), {k:list(v) for k,v in self.histories.items()}, dict(self.aux), self.last_error

    def run(self):
        next_state = 0.0
        next_hist = 0.0
        while not self.stop_event.is_set():
            now = time.monotonic()
            if now >= next_state:
                try:
                    live = self.api.live(24)
                    st = live.get('state') if isinstance(live,dict) else {}
                    ev = live.get('events') if isinstance(live,dict) else []
                    stats = live.get('state_stats') if isinstance(live,dict) else {}
                    seq = stats.get('seq') if isinstance(stats,dict) else None
                    last_event = None
                    if isinstance(ev,list) and ev:
                        tail=ev[-1] if isinstance(ev[-1],dict) else {}
                        last_event=(tail.get('id'),tail.get('ts'),tail.get('type'))
                    sig=(seq,last_event)
                    changed = sig != self._live_sig
                    with self.lock:
                        if isinstance(st,dict) and st:self.state = st
                        self.events = ev if isinstance(ev,list) else []
                        self.last_state_at = time.time()
                        self.last_error = self.api.last_error
                        self._live_sig = sig
                    if changed:self.dirty.set()
                except Exception as exc:
                    with self.lock:self.last_error = repr(exc)
                next_state = now + self.state_interval
            if now >= next_hist:
                try:
                    batch = self.api.history_batch(self.keys, 64, channel_limit=90, expedition_points=256)
                    raw_hist = batch.get('histories') if isinstance(batch,dict) else {}
                    new = {}
                    if isinstance(raw_hist,dict):
                        for key,rows in raw_hist.items():
                            if isinstance(rows,list):
                                new[key] = [r.get('value') for r in rows if isinstance(r,dict)]
                    platform = self.api.platform_bundle()
                    aux = {
                        'channel_history': batch.get('channel_history') if isinstance(batch,dict) else [],
                        'expedition': batch.get('expedition') if isinstance(batch,dict) else None,
                        'telemetry': batch.get('telemetry') if isinstance(batch,dict) else [],
                        'library': platform.get('library') if isinstance(platform,dict) else {},
                        'jobs': platform.get('jobs') if isinstance(platform,dict) else {},
                        'incidents': platform.get('incidents') if isinstance(platform,dict) else {},
                        'overview': platform.get('overview') if isinstance(platform,dict) else {},
                        'topology': platform.get('topology') if isinstance(platform,dict) else {},
                    }
                    with self.lock:
                        self.histories.update(new)
                        self.aux.update(aux)
                        self.last_history_at = time.time()
                    self.dirty.set()
                except Exception as exc:
                    with self.lock:self.last_error = repr(exc)
                next_hist = now + self.history_interval
            self.stop_event.wait(0.03)

    def stop(self):
        self.stop_event.set()
