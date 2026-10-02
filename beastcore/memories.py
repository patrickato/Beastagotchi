from __future__ import annotations

import json
import time
import uuid
from typing import Any


class BeastMemoryEngine:
    """Low-volume per-creature history for meaningful milestones.

    Raw AP/client/GPS telemetry is intentionally not copied here. Dedicated
    BeastDex/Expedition/PeerDex stores remain authoritative for detailed data.
    """

    MEMORY_EVENTS = {
        "progression.level_up": "level",
        "progression.stage_changed": "evolution",
        "progression.achievement_unlocked": "achievement",
        "rare.moment.acknowledged": "rare",
        "expedition.started": "expedition",
        "expedition.recovered": "expedition",
        "expedition.checkpointed": "expedition",
    }

    def __init__(self,state,store,roster,*,clock=time.time,mono=time.monotonic) -> None:
        self.state=state;self.store=store;self.conn=store.conn;self.roster=roster
        self.clock=clock;self.mono=mono
        self._personality_last: dict[str,str] = {}
        self._personality_candidate: dict[str,tuple[str,float,dict[str,Any]]] = {}
        self._exp_touch: dict[tuple[str,str],float] = {}

    def _active_id(self) -> str:
        try:return str(self.roster.active()["id"])
        except Exception:return ""

    @staticmethod
    def _safe_data(event_type: str, data: dict[str,Any]) -> dict[str,Any]:
        d=data if isinstance(data,dict) else {}
        allowed={
            "progression.level_up":("from","to","stage","xp"),
            "progression.stage_changed":("from","to","level"),
            "progression.achievement_unlocked":("id","label","rarity","bonus_xp","count"),
            "rare.moment.acknowledged":("id","rarity","sigil","presentation"),
            "expedition.started":("id",),
            "expedition.recovered":("id",),
            "expedition.checkpointed":("id","distance_m","ap_unique","captures_delta","xp_delta","reason"),
        }.get(event_type,())
        return {k:d.get(k) for k in allowed if k in d}

    @staticmethod
    def _summary(event_type: str, data: dict[str,Any]) -> str:
        if event_type=="progression.level_up":
            return f"Reached level {int(data.get('to') or 1)} · {data.get('stage') or 'evolved'}"
        if event_type=="progression.stage_changed":
            return f"Evolved from {data.get('from') or '?'} to {data.get('to') or '?'}"
        if event_type=="progression.achievement_unlocked":
            return f"Achievement unlocked · {data.get('label') or data.get('id') or 'Unknown'}"
        if event_type=="rare.moment.acknowledged":
            return f"Witnessed {str(data.get('rarity') or 'rare').title()} moment · {data.get('sigil') or data.get('id') or 'unknown'}"
        if event_type=="expedition.started":
            return f"Joined Expedition {data.get('id') or ''}".strip()
        if event_type=="expedition.recovered":
            return f"Rejoined Expedition {data.get('id') or ''}".strip()
        if event_type=="expedition.checkpointed":
            return f"Expedition checkpoint · {round(float(data.get('distance_m') or 0),1)} m · {int(data.get('ap_unique') or 0)} APs"
        return event_type

    def record_event(self, ev, *, beast_id: str | None = None) -> bool:
        et=str(getattr(ev,"type","") or "")
        kind=self.MEMORY_EVENTS.get(et)
        if not kind:return False
        bid=str(beast_id or (getattr(ev,"data",{}) or {}).get("beast_id") or self._active_id()).strip()
        if not bid:return False
        try:self.roster.get(bid)
        except Exception:return False
        data=self._safe_data(et,getattr(ev,"data",{}) or {})
        ts=float(getattr(ev,"ts",self.clock()) or self.clock())
        rarity=str(data.get("rarity") or "") or None
        expedition_id=str(data.get("id") or "") if kind=="expedition" else None
        mid=f"event:{getattr(ev,'id',uuid.uuid4().hex)}:{bid}"
        try:
            with self.conn:
                self.conn.execute(
                    """INSERT OR IGNORE INTO beast_memories(
                       id,beast_id,ts,kind,source_event_type,rarity,expedition_id,summary,data_json
                       ) VALUES(?,?,?,?,?,?,?,?,?)""",
                    (mid,bid,ts,kind,et,rarity,expedition_id,self._summary(et,data),
                     json.dumps(data,separators=(",",":"))),
                )
            return True
        except Exception:
            return False

    def record_custom(self, beast_id: str, kind: str, summary: str, data: dict[str,Any] | None = None,
                      *, rarity: str | None = None, expedition_id: str | None = None, memory_id: str | None = None) -> bool:
        bid=str(beast_id);self.roster.get(bid);now=float(self.clock())
        mid=memory_id or f"memory:{uuid.uuid4().hex}"
        payload=data if isinstance(data,dict) else {}
        with self.conn:
            self.conn.execute(
                """INSERT OR IGNORE INTO beast_memories(
                   id,beast_id,ts,kind,source_event_type,rarity,expedition_id,summary,data_json
                   ) VALUES(?,?,?,?,?,?,?,?,?)""",
                (mid,bid,now,str(kind)[:48],"custom",rarity,expedition_id,str(summary)[:240],
                 json.dumps(payload,separators=(",",":"))),
            )
        return True

    def observe_expedition(self, patch: dict[str,Any]) -> None:
        if not isinstance(patch,dict) or not patch.get("expedition.active"):return
        eid=str(patch.get("expedition.id") or "").strip();bid=self._active_id()
        if not eid or not bid:return
        now=float(self.clock());key=(bid,eid)
        last=self._exp_touch.get(key,0.0)
        if last and now-last<30.0:return
        self._exp_touch[key]=now
        with self.conn:
            self.conn.execute(
                """INSERT INTO beast_expeditions(beast_id,expedition_id,first_active_at,last_active_at)
                   VALUES(?,?,?,?)
                   ON CONFLICT(beast_id,expedition_id) DO UPDATE SET last_active_at=excluded.last_active_at""",
                (bid,eid,now,now),
            )

    def observe_personality(self, patch: dict[str,Any]) -> None:
        if not isinstance(patch,dict):return
        mood=str(patch.get("beast.mood") or "").strip()
        bid=self._active_id()
        if not bid or not mood:return
        last=self._personality_last.get(bid)
        if last==mood:
            self._personality_candidate.pop(bid,None);return
        now=self.mono();cand=self._personality_candidate.get(bid)
        if not cand or cand[0]!=mood:
            self._personality_candidate[bid]=(mood,now,dict(patch));return
        if now-cand[1]<10.0:return
        data={
            "mood":mood,
            "energy":int(patch.get("beast.energy") or 0),
            "curiosity":int(patch.get("beast.curiosity") or 0),
            "focus":int(patch.get("beast.focus") or 0),
            "confidence":int(patch.get("beast.confidence") or 0),
            "stress":int(patch.get("beast.stress") or 0),
        }
        self.record_custom(
            bid,"personality",f"Mood shifted to {mood}",data,
            memory_id=f"personality:{bid}:{int(self.clock())}:{mood}",
        )
        self._personality_last[bid]=mood
        self._personality_candidate.pop(bid,None)

    def recent(self, beast_id: str, limit: int = 20) -> list[dict[str,Any]]:
        rows=self.conn.execute(
            """SELECT id,ts,kind,source_event_type,rarity,expedition_id,summary,data_json
               FROM beast_memories WHERE beast_id=? ORDER BY ts DESC LIMIT ?""",
            (str(beast_id),max(1,min(int(limit),200))),
        ).fetchall()
        out=[]
        for r in rows:
            try:data=json.loads(r[7] or "{}")
            except Exception:data={}
            out.append({"id":r[0],"ts":r[1],"kind":r[2],"source_event_type":r[3],
                        "rarity":r[4],"expedition_id":r[5],"summary":r[6],"data":data})
        return out

    def summary(self, beast_id: str) -> dict[str,Any]:
        bid=str(beast_id)
        row=self.conn.execute(
            """SELECT COUNT(*),
                      SUM(CASE WHEN kind='rare' THEN 1 ELSE 0 END),
                      SUM(CASE WHEN kind='achievement' THEN 1 ELSE 0 END),
                      SUM(CASE WHEN kind='personality' THEN 1 ELSE 0 END)
               FROM beast_memories WHERE beast_id=?""",(bid,)
        ).fetchone()
        ex=int(self.conn.execute("SELECT COUNT(*) FROM beast_expeditions WHERE beast_id=?",(bid,)).fetchone()[0] or 0)
        last=self.recent(bid,1)
        return {
            "memory_count":int((row or [0])[0] or 0),
            "rare_witness_count":int((row or [0,0])[1] or 0),
            "achievement_memory_count":int((row or [0,0,0])[2] or 0),
            "personality_transition_count":int((row or [0,0,0,0])[3] or 0),
            "expedition_count":ex,
            "last_memory":last[0] if last else None,
        }
