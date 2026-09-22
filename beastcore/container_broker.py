from __future__ import annotations

import json
import shutil
import subprocess
from typing import Any, Callable


MANAGED_LABELS={"io.beastagotchi.managed":"true","beastagotchi.managed":"true"}


class ContainerBrokerError(RuntimeError):
    pass


class ContainerBroker:
    """Control only containers explicitly enrolled for Beast management.

    Beast never assumes ownership of arbitrary Docker/Podman workloads. A
    container must carry a Beast managed label before start/stop/restart is
    offered to UI, automation, or AI Operator.
    """

    def __init__(self, runner: Callable[..., Any] | None=None, which: Callable[[str],str|None] | None=None) -> None:
        self.runner=runner or subprocess.run
        self.which=which or shutil.which

    def _runtime(self) -> tuple[str,str] | None:
        for name in ("podman","docker"):
            p=self.which(name)
            if p:return name,p
        return None

    @staticmethod
    def _labels(obj: Any) -> dict[str,str]:
        if isinstance(obj,dict):
            labels=obj.get("Config",{}).get("Labels") or obj.get("Labels") or {}
            if isinstance(labels,dict):return {str(k):str(v) for k,v in labels.items()}
        return {}

    @staticmethod
    def _managed(labels: dict[str,str]) -> bool:
        low={str(k).lower():str(v).lower() for k,v in labels.items()}
        return any(low.get(k)==v for k,v in MANAGED_LABELS.items())

    def _inspect(self,path: str,target: str) -> dict[str,Any]:
        r=self.runner([path,"inspect",target],capture_output=True,text=True,timeout=5)
        if int(getattr(r,"returncode",1))!=0:
            raise ContainerBrokerError((getattr(r,"stderr","") or "inspect failed")[-400:])
        try:
            obj=json.loads(getattr(r,"stdout","") or "[]")
            if isinstance(obj,list) and obj:return obj[0] if isinstance(obj[0],dict) else {}
            return obj if isinstance(obj,dict) else {}
        except Exception as exc:
            raise ContainerBrokerError(f"invalid inspect output: {exc}") from exc

    def plan(self,target: str,operation: str) -> dict[str,Any]:
        op=str(operation or "").lower();target=str(target or "").strip();rt=self._runtime()
        blockers=[];runtime=None;managed=False;labels={}
        if op not in {"start","stop","restart"}:blockers.append("unsupported container operation")
        if not target:blockers.append("container target required")
        if not rt:blockers.append("no Docker/Podman runtime installed")
        if rt and target:
            runtime,path=rt
            try:
                obj=self._inspect(path,target);labels=self._labels(obj);managed=self._managed(labels)
                if not managed:blockers.append("container is not enrolled as Beast-managed")
            except ContainerBrokerError as exc:blockers.append(str(exc))
        return {"target":target,"operation":op,"runtime":runtime,"managed":managed,"labels":labels,"allowed":not blockers,"blockers":blockers,"warnings":[]}

    def perform(self,target: str,operation: str) -> dict[str,Any]:
        plan=self.plan(target,operation)
        if not plan["allowed"]:raise ContainerBrokerError("; ".join(plan["blockers"]))
        rt=self._runtime();assert rt is not None
        name,path=rt
        r=self.runner([path,str(operation),str(target)],capture_output=True,text=True,timeout=30)
        if int(getattr(r,"returncode",1))!=0:
            raise ContainerBrokerError((getattr(r,"stderr","") or f"{operation} failed")[-500:])
        return {"ok":True,"runtime":name,"target":str(target),"operation":str(operation),"output":(getattr(r,"stdout","") or "")[-500:]}
