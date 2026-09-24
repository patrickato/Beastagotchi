from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from .operator_policy import LEVELS

_LEVEL_ORDER=("observer","operator","maintainer","administrator")


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    level: str
    mutation: bool
    args: dict[str,str]

    def as_dict(self) -> dict[str,Any]:
        return {
            "name":self.name,
            "description":self.description,
            "required_level":self.level,
            "mutation":self.mutation,
            "args":dict(self.args),
        }


class OperatorToolRegistry:
    """Structured tools for a future local/remote Beast Operator.

    This is deliberately *not* a generic shell API.  Read tools query canonical
    Beast state/durable records; mutation tools delegate to ActionBroker so the
    exact same planning, audit, rollback and allow-list rules apply whether the
    caller is a human UI, automation, or an AI model.
    """

    SPECS=(
        ToolSpec("state.get","Read canonical Beast state keys.","observer",False,{"keys":"list[str]"}),
        ToolSpec("search.query","Search Beast records, telemetry and Field Library.","observer",False,{"query":"str","limit":"int"}),
        ToolSpec("library.search","Search offline Field Library documents.","observer",False,{"query":"str","limit":"int"}),
        ToolSpec("incidents.list","Read recent Black Box incidents.","observer",False,{"limit":"int","status":"str|null"}),
        ToolSpec("jobs.list","Read recent Beast jobs/tasks.","observer",False,{"limit":"int"}),
        ToolSpec("action.plan","Plan an allow-listed Beast mutation without executing it.","observer",False,{"action":"str","payload":"object"}),
        ToolSpec("operator.session","Read the current owner-authorized Operator privilege session.","observer",False,{}),
        ToolSpec("owner.mode","Read persistent Expert/Owner Override state.","observer",False,{}),
        ToolSpec("owner.expert_mode_set","Enable/disable persistent Expert Mode; requires an active administrator session.","administrator",True,{"enabled":"bool"}),
        ToolSpec("service.restart","Restart an allow-listed Beast/Pwnagotchi service through Action Broker.","operator",True,{"unit":"str"}),
        ToolSpec("backup.create","Create a verified Beast recovery backup.","operator",True,{}),
        ToolSpec("backup.stage","Stage a verified recovery backup without touching the live system.","maintainer",True,{"name":"str"}),
        ToolSpec("support.bundle","Create a sanitized troubleshooting support bundle.","operator",True,{}),
        ToolSpec("plugin.toggle","Enable/disable a Pwnagotchi plugin transactionally; Expert Mode may explicitly override policy blockers.","operator",True,{"name":"str","enabled":"bool","owner_override":"bool"}),
        ToolSpec("container.control","Start/stop/restart only a container explicitly enrolled as Beast-managed.","operator",True,{"target":"str","operation":"start|stop|restart"}),
    )

    def __init__(self,state,store,search_engine,action_broker) -> None:
        self.state=state;self.store=store;self.search_engine=search_engine;self.action_broker=action_broker
        self._specs={x.name:x for x in self.SPECS}
        self.sessions=getattr(action_broker,"operator_sessions",None)

    @staticmethod
    def _level_ok(active: str, required: str) -> bool:
        a=active if active in _LEVEL_ORDER else "observer"
        r=required if required in _LEVEL_ORDER else "administrator"
        return _LEVEL_ORDER.index(a)>=_LEVEL_ORDER.index(r)

    def catalog(self, active_level: str|None=None) -> dict[str,Any]:
        if active_level is None and self.sessions is not None:active_level=str(self.sessions.current().get("level") or "observer")
        level=active_level if active_level in LEVELS else "observer"
        items=[]
        for spec in self.SPECS:
            row=spec.as_dict();row["available_at_level"]=self._level_ok(level,spec.level);items.append(row)
        return {"active_level":level,"count":len(items),"items":items,"generic_shell":False,"mutations_via_action_broker":True}

    def invoke(self,name: str,args: dict[str,Any]|None=None,*,level: str|None=None,actor: str="operator") -> dict[str,Any]:
        spec=self._specs.get(str(name or ""))
        if spec is None:
            return {"ok":False,"error":"unknown tool"}
        effective=level
        if effective is None and self.sessions is not None:effective=str(self.sessions.current().get("level") or "observer")
        effective=effective if effective in _LEVEL_ORDER else "observer"
        if not self._level_ok(effective,spec.level):
            return {"ok":False,"error":f"tool requires {spec.level} level","tool":spec.name,"active_level":effective}
        a=dict(args or {})
        try:
            if spec.name=="state.get":
                keys=a.get("keys") or []
                if not isinstance(keys,list):keys=[]
                snap=self.state.snapshot(False)
                data={str(k):snap.get(str(k)) for k in keys[:128]} if keys else snap
                return {"ok":True,"tool":spec.name,"data":data}
            if spec.name=="search.query":
                return {"ok":True,"tool":spec.name,"data":self.search_engine.search(str(a.get('query') or ''),int(a.get('limit') or 12))}
            if spec.name=="library.search":
                rows=self.store.search_library(str(a.get('query') or ''),int(a.get('limit') or 20),0)
                return {"ok":True,"tool":spec.name,"data":{"count":len(rows),"items":rows}}
            if spec.name=="incidents.list":
                rows=self.store.recent_incidents(int(a.get('limit') or 20),a.get('status'))
                return {"ok":True,"tool":spec.name,"data":{"count":len(rows),"items":rows}}
            if spec.name=="jobs.list":
                rows=self.store.recent_jobs(int(a.get('limit') or 20))
                return {"ok":True,"tool":spec.name,"data":{"count":len(rows),"items":rows}}
            if spec.name=="operator.session":
                return {"ok":True,"tool":spec.name,"data":self.sessions.current() if self.sessions is not None else {"active":False,"level":"observer"}}
            if spec.name=="owner.mode":
                return {"ok":True,"tool":spec.name,"data":self.action_broker.owner_mode.snapshot()}
            if spec.name=="action.plan":
                plan=self.action_broker.plan(str(a.get('action') or ''),a.get('payload') if isinstance(a.get('payload'),dict) else {})
                return {"ok":True,"tool":spec.name,"data":plan}
            action={"service.restart":"service.restart","backup.create":"backup.create","backup.stage":"backup.stage","support.bundle":"support.bundle","plugin.toggle":"plugin.toggle","container.control":"container.control","owner.expert_mode_set":"owner.expert_mode_set"}[spec.name]
            payload={}
            if spec.name=="service.restart":payload={"unit":str(a.get('unit') or '')}
            elif spec.name=="plugin.toggle":payload={"name":str(a.get('name') or ''),"enabled":bool(a.get('enabled')),"owner_override":bool(a.get("owner_override",False))}
            elif spec.name=="backup.stage":payload={"name":str(a.get("name") or "")}
            elif spec.name=="container.control":payload={"target":str(a.get('target') or ''),"operation":str(a.get('operation') or '')}
            elif spec.name=="owner.expert_mode_set":payload={"enabled":bool(a.get("enabled",False))}
            row=self.action_broker.perform(action,payload,actor=str(actor))
            return {"ok":row.get('status')=='success',"tool":spec.name,"data":row}
        except Exception as exc:
            return {"ok":False,"tool":spec.name,"error":f"{type(exc).__name__}: {exc}"}
