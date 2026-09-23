from __future__ import annotations

import hashlib
import json
import time
import uuid
from pathlib import Path
from typing import Any

from .progression import level_for_xp, stage_for_level
from .heritage import generate_heritage


SYNTHESIS_UNLOCK_LEVEL = 70
SYNTHESIS_PARENT_MIN_LEVEL = 70
MONSTER_GLOBAL_UNLOCK = "monstergotchi.core"


class BeastRosterError(RuntimeError):
    pass


def _loads(value: Any, default):
    try:
        obj = json.loads(value) if isinstance(value, str) else value
        return obj if isinstance(obj, type(default)) else default
    except Exception:
        return default


class BeastRoster:
    """Persistent multi-Beast roster and Monster ancestry foundation.

    This layer intentionally does not yet replace ProgressionEngine's legacy
    profile writer. v0.19 first proves lossless storage/migration/switching and
    ancestry semantics, then the live progression engine can be cut over to the
    active Beast in a separate migration gate.
    """

    def __init__(self, store, *, legacy_profile_path: str | Path = "/var/lib/beastagotchi/profile.json", clock=time.time):
        self.store = store
        self.conn = store.conn
        self.legacy_profile_path = Path(legacy_profile_path)
        self.clock = clock

    def _legacy_profile(self) -> dict[str, Any] | None:
        try:
            obj = json.loads(self.legacy_profile_path.read_text())
            return obj if isinstance(obj, dict) else None
        except Exception:
            return None

    def bootstrap_founder(self, *, name: str = "Founder") -> dict[str, Any]:
        row = self.conn.execute("SELECT id FROM beasts ORDER BY created_at LIMIT 1").fetchone()
        if row:
            return self.get(str(row[0]))

        now = float(self.clock())
        legacy = self._legacy_profile() or {}
        founder_id = "founder"
        identity = {
            "founder": True,
            "legacy_profile_migrated": bool(legacy),
            "legacy_created_at": legacy.get("created_at"),
        }
        appearance = {}
        preferences = {}
        counters = legacy.get("counters") if isinstance(legacy.get("counters"), dict) else {}
        vendors = [str(x) for x in (legacy.get("seen_vendors") or []) if str(x).strip()]
        achievements = [str(x) for x in (legacy.get("achievements") or []) if str(x).strip()]
        xp = max(0, int(legacy.get("xp") or 0))
        max_level = max(1, min(100, int(legacy.get("max_level") or 100)))
        runtime = max(0.0, float(legacy.get("lifetime_runtime_sec") or 0.0))
        remainder = max(0.0, float(legacy.get("runtime_award_remainder_sec") or 0.0))

        with self.conn:
            self.conn.execute("UPDATE beasts SET active=0,status=CASE WHEN status='active' THEN 'resting' ELSE status END")
            self.conn.execute(
                """INSERT INTO beasts(id,name,kind,lineage_id,status,active,generation,created_at,updated_at,trait_seed,identity_json,appearance_json,preferences_json)
                   VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (founder_id, str(name)[:64] or "Founder", "beast", "founder", "active", 1, 0,
                 float(legacy.get("created_at") or now), now, "founder",
                 json.dumps(identity, separators=(",", ":")),
                 json.dumps(appearance), json.dumps(preferences)),
            )
            self.conn.execute(
                """INSERT INTO beast_progress(beast_id,xp,max_level,lifetime_runtime_sec,runtime_award_remainder_sec,counters_json,seen_vendors_json,updated_at)
                   VALUES(?,?,?,?,?,?,?,?)""",
                (founder_id, xp, max_level, runtime, remainder,
                 json.dumps(counters, separators=(",", ":")),
                 json.dumps(vendors, separators=(",", ":")), now),
            )
            for aid in achievements:
                self.conn.execute(
                    "INSERT OR IGNORE INTO beast_achievements(beast_id,achievement_id,unlocked_at,context_json) VALUES(?,?,?,?)",
                    (founder_id, aid, now, json.dumps({"source": "legacy_profile_migration"})),
                )
        return self.get(founder_id)

    def create_beast(
        self,
        name: str,
        *,
        lineage_id: str = "standard",
        identity: dict[str, Any] | None = None,
        appearance: dict[str, Any] | None = None,
        preferences: dict[str, Any] | None = None,
        activate: bool = False,
    ) -> dict[str, Any]:
        now = float(self.clock())
        beast_id = "beast-" + uuid.uuid4().hex[:16]
        seed = hashlib.sha256(beast_id.encode()).hexdigest()[:24]
        with self.conn:
            if activate:
                self.conn.execute("UPDATE beasts SET active=0,status=CASE WHEN status='active' THEN 'resting' ELSE status END")
            self.conn.execute(
                """INSERT INTO beasts(id,name,kind,lineage_id,status,active,generation,created_at,updated_at,trait_seed,identity_json,appearance_json,preferences_json)
                   VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (beast_id, str(name or "Beast")[:64], "beast", str(lineage_id or "standard")[:80],
                 "active" if activate else "resting", 1 if activate else 0, 0, now, now, seed,
                 json.dumps(identity or {}, separators=(",", ":")),
                 json.dumps(appearance or {}, separators=(",", ":")),
                 json.dumps(preferences or {}, separators=(",", ":"))),
            )
            self.conn.execute(
                "INSERT INTO beast_progress(beast_id,xp,max_level,lifetime_runtime_sec,runtime_award_remainder_sec,counters_json,seen_vendors_json,updated_at) VALUES(?,?,?,?,?,?,?,?)",
                (beast_id, 0, 100, 0.0, 0.0, "{}", "[]", now),
            )
        return self.get(beast_id)

    def get(self, beast_id: str) -> dict[str, Any]:
        row = self.conn.execute(
            """SELECT b.id,b.name,b.kind,b.lineage_id,b.status,b.active,b.generation,b.created_at,b.updated_at,b.trait_seed,
                      b.identity_json,b.appearance_json,b.preferences_json,
                      p.xp,p.max_level,p.lifetime_runtime_sec,p.runtime_award_remainder_sec,p.counters_json,p.seen_vendors_json
               FROM beasts b JOIN beast_progress p ON p.beast_id=b.id WHERE b.id=?""",
            (str(beast_id),),
        ).fetchone()
        if not row:
            raise BeastRosterError("Beast not found")
        keys = [
            "id","name","kind","lineage_id","status","active","generation","created_at","updated_at","trait_seed",
            "identity_json","appearance_json","preferences_json","xp","max_level","lifetime_runtime_sec",
            "runtime_award_remainder_sec","counters_json","seen_vendors_json",
        ]
        out = dict(zip(keys, row))
        out["active"] = bool(out["active"])
        out["identity"] = _loads(out.pop("identity_json"), {})
        out["appearance"] = _loads(out.pop("appearance_json"), {})
        out["preferences"] = _loads(out.pop("preferences_json"), {})
        out["counters"] = _loads(out.pop("counters_json"), {})
        out["seen_vendors"] = _loads(out.pop("seen_vendors_json"), [])
        out["achievements"] = [
            r[0] for r in self.conn.execute(
                "SELECT achievement_id FROM beast_achievements WHERE beast_id=? ORDER BY unlocked_at,achievement_id",
                (out["id"],),
            ).fetchall()
        ]
        out["unlocks"] = [
            r[0] for r in self.conn.execute(
                "SELECT unlock_id FROM beast_unlocks WHERE beast_id=? ORDER BY unlocked_at,unlock_id",
                (out["id"],),
            ).fetchall()
        ]
        out["parents"] = [
            r[0] for r in self.conn.execute(
                "SELECT parent_id FROM beast_ancestry WHERE child_id=? ORDER BY parent_id",
                (out["id"],),
            ).fetchall()
        ]
        out["level"] = level_for_xp(int(out["xp"] or 0))
        out["stage"] = stage_for_level(out["level"], out["kind"])
        return out

    def list(self) -> list[dict[str, Any]]:
        ids = [r[0] for r in self.conn.execute("SELECT id FROM beasts ORDER BY active DESC,created_at,id").fetchall()]
        return [self.get(str(x)) for x in ids]

    def active(self) -> dict[str, Any]:
        row = self.conn.execute("SELECT id FROM beasts WHERE active=1 LIMIT 1").fetchone()
        if not row:
            return self.bootstrap_founder()
        return self.get(str(row[0]))

    def set_active(self, beast_id: str) -> dict[str, Any]:
        self.get(beast_id)
        now = float(self.clock())
        with self.conn:
            self.conn.execute("UPDATE beasts SET active=0,status=CASE WHEN status='active' THEN 'resting' ELSE status END,updated_at=?", (now,))
            self.conn.execute("UPDATE beasts SET active=1,status='active',updated_at=? WHERE id=?", (now, str(beast_id)))
        return self.get(beast_id)

    def update_progress(self, beast_id: str, *, xp: int | None = None, counters: dict[str, Any] | None = None) -> dict[str, Any]:
        current = self.get(beast_id)
        now = float(self.clock())
        new_xp = max(0, int(current["xp"] if xp is None else xp))
        new_counters = dict(current.get("counters") or {})
        if isinstance(counters, dict):
            new_counters.update(counters)
        with self.conn:
            self.conn.execute(
                "UPDATE beast_progress SET xp=?,counters_json=?,updated_at=? WHERE beast_id=?",
                (new_xp, json.dumps(new_counters, separators=(",", ":")), now, str(beast_id)),
            )
            self.conn.execute("UPDATE beasts SET updated_at=? WHERE id=?", (now, str(beast_id)))
        return self.get(beast_id)

    PRESENTATION_KEYS = (
        "experience_id","theme","face_profile","animation_profile","renderers","theme_options",
        "dashboard_widgets","custom_boards","context_decks","active_context_deck",
        "palette_overrides","correlation_keys",
    )

    def set_presentation_preferences(self, beast_id: str, presentation: dict[str, Any] | None) -> dict[str, Any]:
        beast=self.get(str(beast_id))
        incoming=presentation if isinstance(presentation,dict) else {}
        clean={k:incoming[k] for k in self.PRESENTATION_KEYS if k in incoming}
        raw=json.dumps(clean,separators=(",",":"),sort_keys=True)
        if len(raw.encode("utf-8"))>262144:
            raise BeastRosterError("preferred presentation is too large")
        prefs=dict(beast.get("preferences") or {})
        prefs["presentation"]=clean
        prefs["presentation_updated_at"]=float(self.clock())
        now=float(self.clock())
        with self.conn:
            self.conn.execute(
                "UPDATE beasts SET preferences_json=?,updated_at=? WHERE id=?",
                (json.dumps(prefs,separators=(",",":")),now,str(beast_id)),
            )
        return self.get(str(beast_id))

    def clear_presentation_preferences(self, beast_id: str) -> dict[str, Any]:
        beast=self.get(str(beast_id));prefs=dict(beast.get("preferences") or {})
        prefs.pop("presentation",None);prefs.pop("presentation_updated_at",None)
        now=float(self.clock())
        with self.conn:
            self.conn.execute(
                "UPDATE beasts SET preferences_json=?,updated_at=? WHERE id=?",
                (json.dumps(prefs,separators=(",",":")),now,str(beast_id)),
            )
        return self.get(str(beast_id))

    def presentation_preferences(self, beast_id: str) -> dict[str, Any]:
        beast=self.get(str(beast_id));prefs=beast.get("preferences") if isinstance(beast.get("preferences"),dict) else {}
        row=prefs.get("presentation")
        return dict(row) if isinstance(row,dict) else {}

    def synthesis_plan(self, parent_a: str, parent_b: str) -> dict[str, Any]:
        if str(parent_a) == str(parent_b):
            return {"allowed": False, "blockers": ["Lineage Synthesis requires two distinct Beasts"]}
        a = self.get(parent_a)
        b = self.get(parent_b)
        blockers = []
        if a["kind"] != "beast" or b["kind"] != "beast":
            blockers.append("v1 Lineage Synthesis requires two Beast-class parents")
        if a["level"] < SYNTHESIS_PARENT_MIN_LEVEL:
            blockers.append(f"{a['name']} must reach level {SYNTHESIS_PARENT_MIN_LEVEL}")
        if b["level"] < SYNTHESIS_PARENT_MIN_LEVEL:
            blockers.append(f"{b['name']} must reach level {SYNTHESIS_PARENT_MIN_LEVEL}")
        prior = self.conn.execute(
            """SELECT child_id FROM monster_syntheses
               WHERE (parent_a=? AND parent_b=?) OR (parent_a=? AND parent_b=?) LIMIT 1""",
            (a["id"], b["id"], b["id"], a["id"]),
        ).fetchone()
        if prior:
            blockers.append("this Beast pair has already produced its v1 Monster")
        return {
            "allowed": not blockers,
            "operation": "roster.synthesize",
            "parent_a": a,
            "parent_b": b,
            "minimum_level": SYNTHESIS_PARENT_MIN_LEVEL,
            "global_unlock": MONSTER_GLOBAL_UNLOCK,
            "parents_consumed": False,
            "parents_reset": False,
            "offspring_kind": "monster",
            "offspring_start_level": 1,
            "blockers": blockers,
        }

    def synthesize(self, parent_a: str, parent_b: str, *, name: str = "Monster") -> dict[str, Any]:
        plan = self.synthesis_plan(parent_a, parent_b)
        if not plan["allowed"]:
            raise BeastRosterError("; ".join(plan["blockers"]))
        a, b = plan["parent_a"], plan["parent_b"]
        now = float(self.clock())
        child_id = "monster-" + uuid.uuid4().hex[:16]
        synthesis_id = "synth-" + uuid.uuid4().hex[:16]
        seed_material = "|".join(sorted([a["id"], b["id"]]) + [child_id, "lineage_synthesis_v1"])
        seed = hashlib.sha256(seed_material.encode()).hexdigest()
        generated = generate_heritage(a,b,seed)
        heritage = {
            "schema": 2,
            "parent_ids": [a["id"], b["id"]],
            "parent_lineages": [a["lineage_id"], b["lineage_id"]],
            "parent_levels_at_synthesis": [a["level"], b["level"]],
            "parent_preferences": [a.get("preferences") or {}, b.get("preferences") or {}],
            "inheritance_seed": seed,
            "generated_identity_pending": False,
            "generated": generated,
        }
        lineage = "monster.hybrid"
        with self.conn:
            self.conn.execute(
                """INSERT INTO beasts(id,name,kind,lineage_id,status,active,generation,created_at,updated_at,trait_seed,identity_json,appearance_json,preferences_json)
                   VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (child_id, str(name or "Monster")[:64], "monster", lineage, "resting", 0,
                 max(int(a["generation"]), int(b["generation"])) + 1, now, now, seed[:24],
                 json.dumps({"monster": True, "heritage": heritage, "traits": generated.get("traits") or {}}, separators=(",", ":")),
                 json.dumps({"traits": generated.get("traits") or {}, "mutation": generated.get("mutation")}, separators=(",", ":")),
                 json.dumps({}, separators=(",", ":"))),
            )
            self.conn.execute(
                "INSERT INTO beast_progress(beast_id,xp,max_level,lifetime_runtime_sec,runtime_award_remainder_sec,counters_json,seen_vendors_json,updated_at) VALUES(?,?,?,?,?,?,?,?)",
                (child_id, 0, 100, 0.0, 0.0, "{}", "[]", now),
            )
            self.conn.executemany(
                "INSERT INTO beast_ancestry(child_id,parent_id,parent_role) VALUES(?,?,?)",
                [(child_id, a["id"], "parent_a"), (child_id, b["id"], "parent_b")],
            )
            self.conn.execute(
                "INSERT INTO monster_syntheses(id,created_at,parent_a,parent_b,child_id,seed,recipe_id,data_json) VALUES(?,?,?,?,?,?,?,?)",
                (synthesis_id, now, a["id"], b["id"], child_id, seed, "lineage_synthesis_v1",
                 json.dumps(heritage, separators=(",", ":"))),
            )
            self.conn.execute(
                "INSERT OR IGNORE INTO global_unlocks(unlock_id,unlocked_at,source,data_json) VALUES(?,?,?,?)",
                (MONSTER_GLOBAL_UNLOCK, now, "monster_synthesis",
                 json.dumps({"synthesis_id": synthesis_id, "child_id": child_id}, separators=(",", ":"))),
            )
        return {
            "ok": True,
            "synthesis_id": synthesis_id,
            "monster": self.get(child_id),
            "global_unlock": MONSTER_GLOBAL_UNLOCK,
            "parents": [self.get(a["id"]), self.get(b["id"])],
            "parents_consumed": False,
            "parents_reset": False,
        }

    def global_unlocks(self) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            "SELECT unlock_id,unlocked_at,source,data_json FROM global_unlocks ORDER BY unlocked_at,unlock_id"
        ).fetchall()
        return [
            {"id": r[0], "unlocked_at": r[1], "source": r[2], "data": _loads(r[3], {})}
            for r in rows
        ]
