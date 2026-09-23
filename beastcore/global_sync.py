from __future__ import annotations

import hashlib
import json
import time
import uuid
from copy import deepcopy
from typing import Any

from .roster import BeastRoster, SYNTHESIS_PARENT_MIN_LEVEL


DEFAULT_POLICY = {
    "enabled": False,
    "auto_sync": False,
    "roster_scope": "active",
    "selected_creature_ids": [],
    "publish_names": True,
    "publish_lineage": True,
    "publish_level_stage": True,
    "publish_synthesis_eligibility": True,
    "publish_achievements": "none",
    "selected_achievement_ids": [],
    "publish_monsters": True,
    "publish_ancestry": False,
    "publish_experience": False,
    "publish_roster_totals": True,
    "publish_global_unlocks": False,
    "selected_global_unlock_ids": [],
}


class GlobalPublishPolicyError(ValueError):
    pass


def clean_policy(obj: dict[str, Any] | None) -> dict[str, Any]:
    src = obj if isinstance(obj, dict) else {}
    out = deepcopy(DEFAULT_POLICY)
    for key in ("enabled","auto_sync","publish_names","publish_lineage","publish_level_stage",
                "publish_synthesis_eligibility","publish_monsters","publish_ancestry",
                "publish_experience","publish_roster_totals","publish_global_unlocks"):
        if key in src:
            out[key] = bool(src[key])
    scope = str(src.get("roster_scope") or out["roster_scope"]).lower()
    if scope not in {"active","all","selected"}:
        raise GlobalPublishPolicyError("roster_scope must be active, all, or selected")
    out["roster_scope"] = scope
    mode = str(src.get("publish_achievements") or out["publish_achievements"]).lower()
    if mode not in {"none","selected","all"}:
        raise GlobalPublishPolicyError("publish_achievements must be none, selected, or all")
    out["publish_achievements"] = mode
    for key in ("selected_creature_ids","selected_achievement_ids","selected_global_unlock_ids"):
        vals = src.get(key)
        out[key] = [str(x)[:160] for x in vals[:256] if str(x).strip()] if isinstance(vals,list) else []
    # Global is useless and misleading if automatic upload appears enabled while
    # publishing itself is disabled.
    if not out["enabled"]:
        out["auto_sync"] = False
    return out


class GlobalProfileSync:
    """Build and queue privacy-sanitized public Beast profile revisions.

    This engine never performs network I/O. A future connector drains the queue.
    Until then queued snapshots remain local. Local Beast data is authoritative.
    """

    POLICY_KEY = "global.publish_policy"
    PUBLIC_ID_KEY = "global.public_id"
    LAST_HASH_KEY = "global.last_public_hash"

    def __init__(self, state, store, roster: BeastRoster | None = None, *, clock=time.time) -> None:
        self.state = state
        self.store = store
        self.conn = store.conn
        self.roster = roster or BeastRoster(store)
        self.clock = clock

    def _meta_get(self, key: str, default: str = "") -> str:
        row = self.conn.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
        return str(row[0]) if row else default

    def _meta_set(self, key: str, value: str) -> None:
        with self.conn:
            self.conn.execute(
                "INSERT INTO meta(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (key, str(value)),
            )

    def policy(self) -> dict[str, Any]:
        raw = self._meta_get(self.POLICY_KEY)
        try: obj = json.loads(raw) if raw else {}
        except Exception: obj = {}
        return clean_policy(obj)

    def set_policy(self, policy: dict[str, Any]) -> dict[str, Any]:
        clean = clean_policy(policy)
        self._meta_set(self.POLICY_KEY, json.dumps(clean, separators=(",",":"), sort_keys=True))
        return clean

    def public_id(self, *, create: bool = False) -> str | None:
        value = self._meta_get(self.PUBLIC_ID_KEY).strip()
        if value:
            return value
        if not create:
            return None
        value = "beastpub-" + uuid.uuid4().hex
        self._meta_set(self.PUBLIC_ID_KEY, value)
        return value

    def rotate_public_id(self) -> str:
        value = "beastpub-" + uuid.uuid4().hex
        self._meta_set(self.PUBLIC_ID_KEY, value)
        self._meta_set(self.LAST_HASH_KEY, "")
        return value

    @staticmethod
    def _public_creature_id(public_id: str, creature_id: str) -> str:
        return "creature-" + hashlib.sha256(f"{public_id}|{creature_id}".encode()).hexdigest()[:20]

    def _select_roster(self, policy: dict[str, Any]) -> list[dict[str, Any]]:
        rows = self.roster.list()
        scope = policy["roster_scope"]
        if scope == "active":
            return [x for x in rows if x.get("active")]
        if scope == "selected":
            allow = set(policy["selected_creature_ids"])
            return [x for x in rows if x.get("id") in allow]
        return rows

    def _achievements(self, beast: dict[str, Any], policy: dict[str, Any]) -> list[str]:
        mode = policy["publish_achievements"]
        rows = [str(x) for x in beast.get("achievements") or []]
        if mode == "none":
            return []
        if mode == "selected":
            allowed = set(policy["selected_achievement_ids"])
            return [x for x in rows if x in allowed]
        return rows[:512]

    def build_snapshot(self, policy: dict[str, Any] | None = None) -> dict[str, Any]:
        policy = clean_policy(policy if policy is not None else self.policy())
        if not policy["enabled"]:
            return {"enabled": False, "schema": 1, "public_id": None, "creatures": []}
        public_id = self.public_id(create=True)
        assert public_id
        all_rows = self.roster.list()
        rows = self._select_roster(policy)
        creatures = []
        id_map = {b["id"]: self._public_creature_id(public_id,b["id"]) for b in all_rows}
        for b in rows:
            if b.get("kind") == "monster" and not policy["publish_monsters"]:
                continue
            row: dict[str, Any] = {
                "id": id_map[b["id"]],
                "kind": str(b.get("kind") or "beast"),
                "active": bool(b.get("active")),
                "generation": int(b.get("generation") or 0),
            }
            if policy["publish_names"]:
                row["name"] = str(b.get("name") or "")[:64]
            if policy["publish_lineage"]:
                row["lineage"] = str(b.get("lineage_id") or "")[:80]
            if policy["publish_level_stage"]:
                row["level"] = int(b.get("level") or 1)
                row["stage"] = str(b.get("stage") or "")[:48]
            if policy["publish_synthesis_eligibility"]:
                row["synthesis_eligible"] = bool(
                    b.get("kind") == "beast" and int(b.get("level") or 1) >= SYNTHESIS_PARENT_MIN_LEVEL
                )
            achievements = self._achievements(b, policy)
            if achievements:
                row["achievements"] = achievements
            if policy["publish_ancestry"] and b.get("parents"):
                row["parents"] = [id_map[x] for x in b.get("parents") if x in id_map]
            if policy["publish_experience"]:
                prefs = b.get("preferences") if isinstance(b.get("preferences"),dict) else {}
                # Only presentation identifiers; never arbitrary preference/config values.
                row["experience"] = {
                    k: str(prefs.get(k) or "")[:96]
                    for k in ("experience","theme","face_profile","animation_profile","board")
                    if prefs.get(k)
                }
            creatures.append(row)

        content: dict[str, Any] = {
            "schema": 1,
            "public_id": public_id,
            "creatures": creatures,
        }
        if policy["publish_roster_totals"]:
            content["roster"] = {
                "total": len(all_rows),
                "beasts": sum(1 for x in all_rows if x.get("kind") == "beast"),
                "monsters": sum(1 for x in all_rows if x.get("kind") == "monster"),
                "level_100": sum(1 for x in all_rows if int(x.get("level") or 1) >= 100),
            }
        if policy["publish_global_unlocks"]:
            allow = set(policy["selected_global_unlock_ids"])
            content["global_unlocks"] = [
                str(x.get("id"))
                for x in self.roster.global_unlocks()
                if not allow or str(x.get("id")) in allow
            ][:256]
        return content

    @staticmethod
    def content_hash(snapshot: dict[str, Any]) -> str:
        raw = json.dumps(snapshot, sort_keys=True, separators=(",",":"), ensure_ascii=True)
        return hashlib.sha256(raw.encode()).hexdigest()

    def _queue(self, snapshot: dict[str, Any], digest: str) -> bool:
        now = float(self.clock())
        try:
            with self.conn:
                self.conn.execute(
                    "INSERT INTO global_sync_queue(id,created_at,content_hash,status,payload_json) VALUES(?,?,?,?,?)",
                    ("gsync-" + uuid.uuid4().hex[:20], now, digest, "pending",
                     json.dumps(snapshot, separators=(",",":"), sort_keys=True)),
                )
            return True
        except Exception:
            # Unique hash means this exact revision is already queued/known.
            return False

    def tick(self) -> dict[str, Any]:
        policy = self.policy()
        pending = int(self.conn.execute("SELECT COUNT(*) FROM global_sync_queue WHERE status='pending'").fetchone()[0])
        base = {
            "global.enabled": bool(policy["enabled"]),
            "global.auto_sync": bool(policy["auto_sync"]),
            "global.connector.configured": False,
            "global.connector.state": "not_configured",
            "global.queue.pending": pending,
            "global.privacy.roster_scope": policy["roster_scope"],
            "global.privacy.publish_achievements": policy["publish_achievements"],
            "global.network_io_enabled": False,
        }
        if not policy["enabled"]:
            return dict(base, **{"global.sync.state":"disabled","global.public_id":None})
        snapshot = self.build_snapshot(policy)
        digest = self.content_hash(snapshot)
        last = self._meta_get(self.LAST_HASH_KEY)
        changed = digest != last
        queued = False
        if policy["auto_sync"] and changed:
            queued = self._queue(snapshot, digest)
            if queued or self.conn.execute("SELECT 1 FROM global_sync_queue WHERE content_hash=?", (digest,)).fetchone():
                self._meta_set(self.LAST_HASH_KEY, digest)
        pending = int(self.conn.execute("SELECT COUNT(*) FROM global_sync_queue WHERE status='pending'").fetchone()[0])
        state = "pending_connector" if pending else ("ready_manual" if changed else "up_to_date_local")
        return dict(base, **{
            "global.sync.state":state,
            "global.public_id":snapshot.get("public_id"),
            "global.public_snapshot_hash":digest,
            "global.public_snapshot_changed":changed,
            "global.last_revision_queued":queued,
            "global.queue.pending":pending,
        })

    def pending(self, limit: int = 20) -> list[dict[str, Any]]:
        rows=self.conn.execute(
            "SELECT id,created_at,content_hash,status,payload_json,attempts,last_attempt_at,last_error FROM global_sync_queue WHERE status='pending' ORDER BY created_at LIMIT ?",
            (max(1,min(int(limit),100)),),
        ).fetchall()
        out=[]
        for r in rows:
            out.append({"id":r[0],"created_at":r[1],"content_hash":r[2],"status":r[3],
                        "payload":json.loads(r[4]),"attempts":r[5],"last_attempt_at":r[6],"last_error":r[7]})
        return out
