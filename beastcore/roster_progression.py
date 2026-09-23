from __future__ import annotations

import json
import os
import tempfile
import time
from pathlib import Path
from typing import Any

from .roster import BeastRoster


class ActiveBeastProgressionStore:
    """SQLite-backed progression storage bound to the currently active roster creature.

    The legacy profile.json is imported by BeastRoster as the Founder and then kept
    as a Founder-only compatibility mirror. Other Beasts/Monsters never overwrite it.
    """

    def __init__(
        self,
        store,
        *,
        legacy_profile_path: str | Path = "/var/lib/beastagotchi/profile.json",
        clock=time.time,
    ) -> None:
        self.store = store
        self.conn = store.conn
        self.clock = clock
        self.legacy_profile_path = Path(legacy_profile_path)
        self._legacy_last_achievement = self._read_legacy_last_achievement()
        self.roster = BeastRoster(store, legacy_profile_path=self.legacy_profile_path, clock=clock)
        self.roster.bootstrap_founder()

    def _read_legacy_last_achievement(self) -> str | None:
        try:
            obj = json.loads(self.legacy_profile_path.read_text())
            value = str(obj.get("last_achievement") or "").strip()
            return value or None
        except Exception:
            return None

    def _meta_get(self, key: str) -> str | None:
        row = self.conn.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
        return str(row[0]) if row else None

    def _meta_set(self, key: str, value: str) -> None:
        self.conn.execute(
            "INSERT INTO meta(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, str(value)),
        )

    def current_id(self) -> str:
        return str(self.roster.active()["id"])

    def active_identity(self) -> dict[str, Any]:
        b = self.roster.active()
        return {
            "id": b["id"],
            "name": b["name"],
            "kind": b["kind"],
            "lineage_id": b["lineage_id"],
            "generation": int(b.get("generation") or 0),
            "status": b.get("status"),
            "active": bool(b.get("active")),
            "level": int(b.get("level") or 1),
            "stage": b.get("stage"),
        }

    def roster_summary(self) -> dict[str, Any]:
        row = self.conn.execute(
            """SELECT COUNT(*),
                      SUM(CASE WHEN kind='beast' THEN 1 ELSE 0 END),
                      SUM(CASE WHEN kind='monster' THEN 1 ELSE 0 END),
                      SUM(CASE WHEN status='legend' THEN 1 ELSE 0 END)
               FROM beasts"""
        ).fetchone()
        return {
            "total": int((row or [0])[0] or 0),
            "beasts": int((row or [0, 0])[1] or 0),
            "monsters": int((row or [0, 0, 0])[2] or 0),
            "legends": int((row or [0, 0, 0, 0])[3] or 0),
        }

    def load_profile(self, beast_id: str | None = None) -> dict[str, Any]:
        beast = self.roster.get(str(beast_id)) if beast_id else self.roster.active()
        last = self._meta_get(f"progression.last_achievement.{beast['id']}")
        if not last and beast["id"] == "founder":
            last = self._legacy_last_achievement
        return {
            "schema": 1,
            "created_at": float(beast.get("created_at") or self.clock()),
            "updated_at": float(beast.get("updated_at") or self.clock()),
            "xp": max(0, int(beast.get("xp") or 0)),
            "max_level": max(1, min(100, int(beast.get("max_level") or 100))),
            "lifetime_runtime_sec": max(0.0, float(beast.get("lifetime_runtime_sec") or 0.0)),
            "runtime_award_remainder_sec": max(0.0, float(beast.get("runtime_award_remainder_sec") or 0.0)),
            "seen_vendors": list(beast.get("seen_vendors") or []),
            "achievements": list(beast.get("achievements") or []),
            "last_achievement": last,
            "counters": dict(beast.get("counters") or {}),
        }

    def save_profile(self, beast_id: str, profile: dict[str, Any]) -> None:
        beast_id = str(beast_id)
        self.roster.get(beast_id)
        now = float(self.clock())
        counters = profile.get("counters") if isinstance(profile.get("counters"), dict) else {}
        vendors = list(dict.fromkeys(str(x) for x in (profile.get("seen_vendors") or []) if str(x).strip()))
        achievements = list(dict.fromkeys(str(x) for x in (profile.get("achievements") or []) if str(x).strip()))
        with self.conn:
            self.conn.execute(
                """UPDATE beast_progress SET xp=?,max_level=?,lifetime_runtime_sec=?,
                   runtime_award_remainder_sec=?,counters_json=?,seen_vendors_json=?,updated_at=?
                   WHERE beast_id=?""",
                (
                    max(0, int(profile.get("xp") or 0)),
                    max(1, min(100, int(profile.get("max_level") or 100))),
                    max(0.0, float(profile.get("lifetime_runtime_sec") or 0.0)),
                    max(0.0, float(profile.get("runtime_award_remainder_sec") or 0.0)),
                    json.dumps(counters, separators=(",", ":")),
                    json.dumps(vendors, separators=(",", ":")),
                    now,
                    beast_id,
                ),
            )
            self.conn.execute("UPDATE beasts SET updated_at=? WHERE id=?", (now, beast_id))
            existing = {
                r[0]
                for r in self.conn.execute(
                    "SELECT achievement_id FROM beast_achievements WHERE beast_id=?",
                    (beast_id,),
                ).fetchall()
            }
            for achievement_id in achievements:
                if achievement_id not in existing:
                    self.conn.execute(
                        """INSERT INTO beast_achievements(
                             beast_id,achievement_id,unlocked_at,context_json
                           ) VALUES(?,?,?,?)""",
                        (
                            beast_id,
                            achievement_id,
                            now,
                            json.dumps({"source": "progression_engine"}, separators=(",", ":")),
                        ),
                    )
            last = str(profile.get("last_achievement") or "").strip()
            if last:
                self._meta_set(f"progression.last_achievement.{beast_id}", last)

        if beast_id == "founder":
            self._write_founder_legacy_mirror(profile)

    def _write_founder_legacy_mirror(self, profile: dict[str, Any]) -> None:
        try:
            self.legacy_profile_path.parent.mkdir(parents=True, exist_ok=True)
            fd, tmp = tempfile.mkstemp(
                prefix=".profile.",
                suffix=".json",
                dir=str(self.legacy_profile_path.parent),
            )
            try:
                with os.fdopen(fd, "w") as f:
                    json.dump(profile, f, indent=2, sort_keys=True)
                    f.write("\n")
                os.replace(tmp, self.legacy_profile_path)
            finally:
                try:
                    if os.path.exists(tmp):
                        os.unlink(tmp)
                except Exception:
                    pass
        except Exception:
            # SQLite is authoritative after cutover; a failed legacy rollback mirror
            # must not interrupt live progression.
            pass

    def storage_label(self, beast_id: str) -> str:
        return f"sqlite:{self.store.path}#beast={str(beast_id)}"
