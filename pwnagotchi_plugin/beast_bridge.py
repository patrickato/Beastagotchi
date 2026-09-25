"""Beastagotchi read-only telemetry bridge for Pwnagotchi.

Uses supported plugin callbacks and writes a compact atomic state/event file under /run.
No Bettercap commands, radio changes, or Pwnagotchi behavior changes are performed.
"""
import json
import logging
import os
import time
from pathlib import Path

import pwnagotchi.plugins as plugins

class BeastBridge(plugins.Plugin):
    __author__ = "Beastagotchi"
    __version__ = "0.2.0"
    __license__ = "GPL3"
    __description__ = "Read-only local telemetry/event bridge for Beast Core."

    def __init__(self):
        self.state = {"pwnagotchi.mood":"awake", "pwnagotchi.peers":0}
        self.path = Path("/run/beastagotchi/pwnagotchi_bridge.json")
        self.peer_count = 0
        self.seq = 0
        self.events = []

    def _write(self, event=None, data=None):
        try:
            configured = (getattr(self, "options", {}) or {}).get("state_file")
            if configured: self.path = Path(configured)
            self.path.parent.mkdir(parents=True, exist_ok=True)
            now = time.time()
            if event:
                self.seq += 1
                self.events.append({"seq":self.seq, "type":event, "ts":now, "data":data or {}})
                self.events = self.events[-32:]
            obj = {"updated_at":now, "seq":self.seq, "state":self.state, "events":self.events}
            tmp = self.path.with_suffix(".tmp")
            tmp.write_text(json.dumps(obj, separators=(",",":"), default=str))
            os.chmod(tmp, 0o644)
            os.replace(tmp, self.path)
        except Exception as exc:
            logging.debug("BeastBridge write failed: %r", exc)

    def _peer_data(self, peer):
        def call(name, default=None):
            try:
                fn = getattr(peer, name, None)
                return fn() if callable(fn) else default
            except Exception:
                return default
        return {
            "identity": call("identity", "???"),
            "name": call("name", "???"),
            "version": call("version", ""),
            "face": call("face", ""),
            "rssi": getattr(peer, "rssi", None),
            "channel": getattr(peer, "last_channel", None),
            "encounters": getattr(peer, "encounters", None),
            "session_id": getattr(peer, "session_id", ""),
            "pwnd_run": call("pwnd_run", 0),
            "pwnd_total": call("pwnd_total", 0),
            "uptime": call("uptime", 0),
            "epoch": call("epoch", 0),
        }

    def on_loaded(self): self._write("loaded")
    def on_ready(self, agent): self.state["pwnagotchi.mode"] = "ready"; self._write("ready")
    def on_channel_hop(self, agent, channel): self.state["radio.hop.current"] = channel; self._write("channel_hop", {"channel":channel})
    def on_wifi_update(self, agent, access_points):
        aps = access_points or []
        self.state["pwnagotchi.filtered_ap_count"] = len(aps)
        self.state["pwnagotchi.filtered_client_count"] = sum(len(ap.get("clients") or []) for ap in aps if isinstance(ap,dict))
        self._write("wifi_update", {"ap_count":self.state["pwnagotchi.filtered_ap_count"], "client_count":self.state["pwnagotchi.filtered_client_count"]})
    def on_unfiltered_ap_list(self, agent, access_points):
        self.state["pwnagotchi.unfiltered_ap_count"] = len(access_points or [])
        self._write("unfiltered_ap_list", {"ap_count":self.state["pwnagotchi.unfiltered_ap_count"]})
    def on_epoch(self, agent, epoch, epoch_data):
        self.state["pwnagotchi.epoch"] = epoch
        exported = {}
        if isinstance(epoch_data, dict):
            for src,dst in (
                ("active_for_epochs","active"), ("blind_for_epochs","blind"),
                ("sad_for_epochs","sad"), ("bored_for_epochs","bored"),
                ("inactive_for_epochs","inactive"), ("missed_interactions","missed"),
                ("num_deauths","deauths"), ("num_associations","assocs"),
                ("num_handshakes","handshakes"), ("num_peers","peers"),
                ("tot_bond","tot_bond"), ("avg_bond","avg_bond"),
            ):
                if src in epoch_data:
                    self.state[f"pwnagotchi.{dst}"] = epoch_data[src]
                    exported[src] = epoch_data[src]
        self._write("epoch", {"epoch":epoch, "epoch_data":exported})
    def on_handshake(self, agent, filename, access_point, client_station):
        ap = access_point if isinstance(access_point, dict) else {}
        sta = client_station if isinstance(client_station, dict) else {}
        self._write("handshake", {"file":Path(filename).name, "ap":ap.get("mac") or ap.get("hostname"), "client":sta.get("mac")})
    def on_association(self, agent, access_point):
        ap = access_point if isinstance(access_point, dict) else {}
        self._write("association", {"ap":ap.get("mac") or ap.get("hostname")})
    def on_deauthentication(self, agent, access_point, client_station):
        ap = access_point if isinstance(access_point, dict) else {}
        sta = client_station if isinstance(client_station, dict) else {}
        self._write("deauthentication", {"ap":ap.get("mac") or ap.get("hostname"), "client":sta.get("mac")})
    def on_peer_detected(self, agent, peer):
        self.peer_count += 1; self.state["pwnagotchi.peers"] = self.peer_count; self._write("peer_detected", self._peer_data(peer))
    def on_peer_lost(self, agent, peer):
        self.peer_count = max(0,self.peer_count-1); self.state["pwnagotchi.peers"] = self.peer_count; self._write("peer_lost", self._peer_data(peer))
    def on_bored(self, agent): self.state["pwnagotchi.mood"]="bored"; self._write("mood", {"mood":"bored"})
    def on_sad(self, agent): self.state["pwnagotchi.mood"]="sad"; self._write("mood", {"mood":"sad"})
    def on_excited(self, agent): self.state["pwnagotchi.mood"]="excited"; self._write("mood", {"mood":"excited"})
    def on_lonely(self, agent): self.state["pwnagotchi.mood"]="lonely"; self._write("mood", {"mood":"lonely"})
    def on_sleep(self, agent, t): self.state["pwnagotchi.mood"]="sleep"; self._write("mood", {"mood":"sleep","seconds":t})
    def on_wait(self, agent, t): self.state["pwnagotchi.mood"]="waiting"; self._write("mood", {"mood":"waiting","seconds":t})
