from __future__ import annotations

import json
import math
import time
from typing import Any


class PeerDex:
    """Persistent social memory layered on top of Pwnagotchi peer callbacks.

    Ordinary Pwnagotchi peers are valid entries. Beast-specific metadata is an
    optional future extension and is never required for a local encounter.
    """

    def __init__(self, store, *, clock=time.time) -> None:
        self.store = store
        self.conn = store.conn
        self.clock = clock

    @staticmethod
    def _int(value: Any, default: int = 0) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _clean_identity(value: Any) -> str:
        s = str(value or "").strip()
        if not s or s == "???":
            return ""
        return s[:160]

    def observe(self, data: dict[str, Any], *, ts: float | None = None) -> dict[str, Any]:
        if not isinstance(data, dict):
            return {"accepted": False, "reason": "invalid peer payload"}
        fp = self._clean_identity(data.get("identity"))
        if not fp:
            return {"accepted": False, "reason": "peer identity unavailable"}
        now = float(ts if ts is not None else self.clock())
        name = str(data.get("name") or "???")[:96]
        rssi = data.get("rssi")
        try: rssi = int(rssi) if rssi is not None else None
        except (TypeError, ValueError): rssi = None
        channel = data.get("channel")
        try: channel = int(channel) if channel is not None else None
        except (TypeError, ValueError): channel = None
        old = self.conn.execute(
            "SELECT first_seen,seen_events,best_rssi FROM peer_encounters WHERE fingerprint=?",
            (fp,),
        ).fetchone()
        first = float(old[0]) if old else now
        seen_events = int(old[1]) + 1 if old else 1
        best = old[2] if old else None
        if rssi is not None and (best is None or rssi > int(best)):
            best = rssi
        payload = {
            "uptime": data.get("uptime"),
            "epoch": data.get("epoch"),
        }
        with self.conn:
            self.conn.execute(
                """INSERT INTO peer_encounters(
                     fingerprint,display_name,first_seen,last_seen,seen_events,advertised_encounters,
                     last_rssi,best_rssi,last_channel,version,last_face,pwnd_run,pwnd_total,session_id,
                     beast_capable,public_beast_json,data_json
                   ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                   ON CONFLICT(fingerprint) DO UPDATE SET
                     display_name=excluded.display_name,last_seen=excluded.last_seen,
                     seen_events=excluded.seen_events,advertised_encounters=excluded.advertised_encounters,
                     last_rssi=excluded.last_rssi,best_rssi=excluded.best_rssi,last_channel=excluded.last_channel,
                     version=excluded.version,last_face=excluded.last_face,pwnd_run=excluded.pwnd_run,
                     pwnd_total=excluded.pwnd_total,session_id=excluded.session_id,data_json=excluded.data_json""",
                (
                    fp,name,first,now,seen_events,max(0,self._int(data.get("encounters"))),
                    rssi,best,channel,str(data.get("version") or "")[:48],str(data.get("face") or "")[:32],
                    max(0,self._int(data.get("pwnd_run"))),max(0,self._int(data.get("pwnd_total"))),
                    str(data.get("session_id") or "")[:160],0,"{}",
                    json.dumps(payload,separators=(",",":")),
                ),
            )
        return {
            "accepted": True,
            "fingerprint": fp,
            "name": name,
            "first_seen": first,
            "last_seen": now,
            "seen_events": seen_events,
            "advertised_encounters": max(0,self._int(data.get("encounters"))),
            "first_local_encounter": seen_events == 1,
            "rssi": rssi,
            "best_rssi": best,
            "channel": channel,
        }

    def mark_lost(self, data: dict[str, Any], *, ts: float | None = None) -> dict[str, Any]:
        fp = self._clean_identity((data or {}).get("identity"))
        if not fp:
            return {"accepted": False, "reason": "peer identity unavailable"}
        now = float(ts if ts is not None else self.clock())
        with self.conn:
            self.conn.execute("UPDATE peer_encounters SET last_seen=? WHERE fingerprint=?", (now, fp))
        return {"accepted": True, "fingerprint": fp, "last_seen": now}

    def recent(self, limit: int = 20) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            """SELECT fingerprint,display_name,first_seen,last_seen,seen_events,advertised_encounters,
                      last_rssi,best_rssi,last_channel,version,last_face,pwnd_run,pwnd_total,
                      beast_capable,public_beast_json
               FROM peer_encounters ORDER BY last_seen DESC LIMIT ?""",
            (max(1,min(int(limit),200)),),
        ).fetchall()
        out=[]
        for r in rows:
            out.append({
                "fingerprint":r[0],"name":r[1],"first_seen":r[2],"last_seen":r[3],
                "seen_events":r[4],"advertised_encounters":r[5],"last_rssi":r[6],
                "best_rssi":r[7],"last_channel":r[8],"version":r[9],"face":r[10],
                "pwnd_run":r[11],"pwnd_total":r[12],"beast_capable":bool(r[13]),
                "public_beast":json.loads(r[14] or "{}"),
            })
        return out

    def summary(self) -> dict[str, Any]:
        row=self.conn.execute(
            "SELECT COUNT(*),COALESCE(MAX(last_seen),0),COALESCE(MAX(seen_events),0) FROM peer_encounters"
        ).fetchone()
        return {
            "peerdex.total_peers":int(row[0] or 0),
            "peerdex.last_seen_at":float(row[1] or 0),
            "peerdex.max_local_encounters":int(row[2] or 0),
            "peerdex.recent":self.recent(8),
        }
