from __future__ import annotations

import json
import time
from typing import Any


GLOBAL_ACHIEVEMENTS = {
    # id: label, rarity, metric, target, description
    "world_first_signal": ("First Footprint","common","ap_unique",1,"The device cataloged its first unique access point."),
    "world_signals_100": ("Hundred Horizons","uncommon","ap_unique",100,"Catalog 100 unique access points across the device lifetime."),
    "world_signals_1000": ("Wide World","rare","ap_unique",1000,"Catalog 1,000 unique access points across the device lifetime."),
    "world_signals_10000": ("Signal Atlas","legendary","ap_unique",10000,"Catalog 10,000 unique access points across the device lifetime."),
    "roster_two": ("A Growing Den","common","roster_total",2,"Maintain at least two persistent creatures."),
    "first_monster": ("Something New","epic","monsters",1,"Create the first Monster lineage on this Beastagotchi."),
    "first_legend": ("Hall Opens","legendary","level_100",1,"Raise a creature to level 100."),
    "legends_five": ("Legendary Household","mythic","level_100",5,"Raise five distinct creatures to level 100."),
}


class GlobalAchievementEngine:
    """Device-wide accomplishments that never belong to one arbitrary active Beast."""

    def __init__(self,state,store,roster,*,clock=time.time) -> None:
        self.state=state;self.store=store;self.conn=store.conn;self.roster=roster;self.clock=clock
        self._publish()

    def metrics(self) -> dict[str,int]:
        roster=self.roster.list()
        return {
            "ap_unique":self.store.count_wifi_encounters(),
            "vendor_unique":int(self.store.encounter_summary(1).get("vendor_count") or 0),
            "roster_total":len(roster),
            "monsters":sum(1 for x in roster if x.get("kind")=="monster"),
            "level_100":sum(1 for x in roster if int(x.get("level") or 1)>=100),
        }

    def unlocked(self) -> list[dict[str,Any]]:
        rows=self.conn.execute(
            "SELECT achievement_id,unlocked_at,context_json FROM global_achievements ORDER BY unlocked_at,achievement_id"
        ).fetchall()
        out=[]
        for aid,ts,raw in rows:
            try:ctx=json.loads(raw or "{}")
            except Exception:ctx={}
            out.append({"id":aid,"unlocked_at":float(ts),"context":ctx})
        return out

    def _snapshot(self) -> dict[str,Any]:
        metrics=self.metrics();unlocked=self.unlocked();ids={x["id"] for x in unlocked}
        catalog=[]
        for aid,(label,rarity,metric,target,description) in GLOBAL_ACHIEVEMENTS.items():
            current=int(metrics.get(metric) or 0)
            catalog.append({
                "id":aid,"label":label,"rarity":rarity,"metric":metric,"current":current,
                "target":target,"progress_pct":round(max(0,min(100,current*100/max(1,target))),1),
                "unlocked":aid in ids,"description":description,
            })
        last=unlocked[-1] if unlocked else None
        return {
            "global.achievements.count":len(unlocked),
            "global.achievements.catalog_count":len(GLOBAL_ACHIEVEMENTS),
            "global.achievements.unlocked_ids":[x["id"] for x in unlocked],
            "global.achievements.catalog":catalog,
            "global.achievements.last":last,
            "global.collection.ap_unique":metrics["ap_unique"],
            "global.collection.vendor_unique":metrics["vendor_unique"],
            "global.collection.roster_total":metrics["roster_total"],
            "global.collection.monsters":metrics["monsters"],
            "global.collection.level_100":metrics["level_100"],
        }

    def _publish(self) -> None:
        self.state.update_many("global_achievements",self._snapshot(),priority=86)

    def tick(self) -> list[tuple[str,str,dict[str,Any],str]]:
        metrics=self.metrics()
        existing={x["id"] for x in self.unlocked()}
        now=float(self.clock());events=[]
        with self.conn:
            for aid,(label,rarity,metric,target,description) in GLOBAL_ACHIEVEMENTS.items():
                if aid in existing or int(metrics.get(metric) or 0)<target:continue
                context={"metric":metric,"value":int(metrics.get(metric) or 0),"target":target}
                self.conn.execute(
                    "INSERT OR IGNORE INTO global_achievements(achievement_id,unlocked_at,context_json) VALUES(?,?,?)",
                    (aid,now,json.dumps(context,separators=(",",":"))),
                )
                events.append(("global.achievement_unlocked","global_achievements",{
                    "id":aid,"label":label,"rarity":rarity,"description":description,**context
                },"info"))
        self._publish()
        return events
