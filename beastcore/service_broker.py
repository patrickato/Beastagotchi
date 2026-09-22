from __future__ import annotations

import subprocess
from typing import Any, Callable


ALLOWED_RESTARTS={
    'pwnagotchi.service','bettercap.service','gpsd.service','beast-ui.service',
}


class ServiceBrokerError(RuntimeError):pass


class ServiceBroker:
    """Allow-listed service operations for Beast/AI operator workflows."""
    def __init__(self,runner: Callable[[list[str]], subprocess.CompletedProcess] | None=None) -> None:
        self.runner=runner or self._run

    @staticmethod
    def _run(cmd: list[str]):
        return subprocess.run(cmd,text=True,capture_output=True,timeout=60,check=False)

    def plan_restart(self,unit: str)->dict[str,Any]:
        unit=str(unit or '').strip()
        blockers=[]
        if unit not in ALLOWED_RESTARTS:blockers.append('service is not in Beast restart allow-list')
        return {'unit':unit,'operation':'restart','allowed':not blockers,'blockers':blockers,'warnings':[]}

    def restart(self,unit: str)->dict[str,Any]:
        plan=self.plan_restart(unit)
        if not plan['allowed']:raise ServiceBrokerError('; '.join(plan['blockers']))
        p=self.runner(['systemctl','restart',unit])
        return {'ok':int(p.returncode)==0,'plan':plan,'returncode':int(p.returncode),'stdout':(p.stdout or '')[-2000:],'stderr':(p.stderr or '')[-2000:]}
