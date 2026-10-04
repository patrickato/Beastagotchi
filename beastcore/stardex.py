from __future__ import annotations

import math
import time
from typing import Any


class StarDex:
    """Persistent lifetime record of every satellite PRN the Beast has caught (creature idea 11, increment 2).

    gpsd's SKY message reports each visible satellite; `GPSCollector` already surfaces them as
    ``gps.satellites[]`` (idea 11 increment 1, #59). This turns that live, un-fakeable detail into a
    collectible: every real PRN ever seen is recorded in the Store (``star_catches``), so the collection
    grows over the Beast's life and two Beasts under different skies diverge. A **discovery** is a PRN never
    caught before -- :meth:`observe` returns those so a caller can award discovery XP (increment 3).

    Live-honest (ADR-0008): only PRNs gpsd actually reported are recorded; a satellite's SNR/gnssid are kept
    only when gpsd sent them (never fabricated), and an absent skyview (``gps.satellites`` None) records
    nothing rather than inventing an empty catch. Constellation classification (PRN-range / ``gnssid``
    mapping) is deferred past this increment so it is accurate rather than guessed; the raw ``gnssid`` is
    stored when present for that later work.
    """

    def __init__(self, store, *, clock=time.time) -> None:
        self.store = store
        self.conn = store.conn
        self.clock = clock

    @staticmethod
    def _prn(value: Any) -> int | None:
        # The PRN is the collectible key: a positive *integer* gpsd satellite id. Accept only an integral
        # value -- a bool (int subclass) is never a PRN, and a fractional number (e.g. 5.9) is rejected rather
        # than truncated: truncating would catalog a different satellite (5) and could pre-empt the real
        # PRN 5's later discovery. Record only what gpsd really identified, never a fabricated id (ADR-0008).
        if isinstance(value, bool):
            return None
        if isinstance(value, int):
            prn = value
        elif isinstance(value, float):
            if not (math.isfinite(value) and value.is_integer()):
                return None
            prn = int(value)
        else:
            return None
        return prn if prn > 0 else None

    @staticmethod
    def _int_or_none(value: Any) -> int | None:
        if isinstance(value, bool) or value is None:
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _snr(value: Any) -> float | None:
        # A real, finite SNR (dB-Hz), or None for anything gpsd did not send / that is not a number, so a
        # best-SNR high-water mark is never raised by fabricated data (ADR-0008).
        if isinstance(value, bool) or value is None:
            return None
        try:
            v = float(value)
        except (TypeError, ValueError):
            return None
        return v if math.isfinite(v) else None

    def observe(self, satellites: Any, *, ts: float | None = None) -> dict[str, Any]:
        """Record the currently-visible satellites; return the lifetime-first PRNs caught this call.

        ``satellites`` is the ``gps.satellites[]`` list. A non-list (None -> skyview unknown/unavailable)
        records nothing. Each real PRN is upserted: first_seen is preserved, last_seen/seen_events advance,
        best_snr_dbhz keeps its high-water mark, and gnssid is kept once known.
        """
        if not isinstance(satellites, list):
            # None / non-list -> the skyview is unknown or unavailable (ADR-0008); nothing to catalog.
            return {"accepted": False, "reason": "no skyview", "caught": [], "new_prns": [],
                    "catch_count": 0, "new_count": 0}
        now = float(ts if ts is not None else self.clock())
        caught: list[int] = []
        new_prns: list[int] = []
        seen_this_call: set[int] = set()
        with self.conn:
            for sat in satellites:
                if not isinstance(sat, dict):
                    continue
                prn = self._prn(sat.get("prn"))
                if prn is None or prn in seen_this_call:
                    # Skip malformed entries and a PRN repeated within one skyview (count it once).
                    continue
                seen_this_call.add(prn)
                caught.append(prn)
                gnssid = self._int_or_none(sat.get("gnssid"))
                snr = self._snr(sat.get("snr_dbhz"))
                row = self.conn.execute(
                    "SELECT first_seen, seen_events, best_snr_dbhz, gnssid FROM star_catches WHERE prn=?",
                    (prn,),
                ).fetchone()
                if row is None:
                    new_prns.append(prn)
                    first, seen, best, gid = now, 1, snr, gnssid
                else:
                    first = float(row[0])
                    seen = int(row[1]) + 1
                    best = row[2]
                    if snr is not None and (best is None or snr > float(best)):
                        best = snr
                    gid = gnssid if gnssid is not None else row[3]
                self.conn.execute(
                    """INSERT INTO star_catches(prn,gnssid,first_seen,last_seen,seen_events,best_snr_dbhz)
                         VALUES(?,?,?,?,?,?)
                       ON CONFLICT(prn) DO UPDATE SET
                         gnssid=excluded.gnssid, last_seen=excluded.last_seen,
                         seen_events=excluded.seen_events, best_snr_dbhz=excluded.best_snr_dbhz""",
                    (prn, gid, first, now, seen, best),
                )
        return {"accepted": True, "caught": caught, "new_prns": new_prns,
                "catch_count": len(caught), "new_count": len(new_prns)}

    def recent(self, limit: int = 20) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            """SELECT prn,gnssid,first_seen,last_seen,seen_events,best_snr_dbhz
               FROM star_catches ORDER BY last_seen DESC LIMIT ?""",
            (max(1, min(int(limit), 200)),),
        ).fetchall()
        return [{
            "prn": r[0], "gnssid": r[1], "first_seen": r[2], "last_seen": r[3],
            "seen_events": r[4], "best_snr_dbhz": r[5],
        } for r in rows]

    def summary(self) -> dict[str, Any]:
        row = self.conn.execute(
            "SELECT COUNT(*), MAX(last_seen), MAX(best_snr_dbhz) FROM star_catches"
        ).fetchone()
        last, best = row[1], row[2]
        # last_caught_at / best_snr are *unavailable* (None) until the first catch, never a fabricated 0 that a
        # consumer could not tell apart from a genuine epoch timestamp / signal (ADR-0008). total_prns == 0 is a
        # real count, not unavailable.
        return {
            "stardex.total_prns": int(row[0] or 0),
            "stardex.last_caught_at": float(last) if last is not None else None,
            "stardex.best_snr_dbhz": float(best) if best is not None else None,
            "stardex.recent": self.recent(8),
        }
