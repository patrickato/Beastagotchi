#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path

def run(*args):
    return subprocess.check_output(args,text=True,stderr=subprocess.DEVNULL).strip()

def main():
    try:
        routes=json.loads(run('ip','-j','route','show','default'))
    except Exception as e:
        print('ERROR: could not read default route:',e,file=sys.stderr); return 2
    r=next((x for x in routes if x.get('dev')=='eth0'),None)
    if not r:
        print('ERROR: eth0 is not the active default route. Connect Ethernet to your home network first.',file=sys.stderr); return 2
    gw=str(r.get('gateway') or '')
    mac=''
    if gw:
        try:
            n=run('ip','neigh','show',gw,'dev','eth0').split()
            if 'lladdr' in n: mac=n[n.index('lladdr')+1].lower()
        except Exception: pass
    obj={'gateway':gw,'gateway_mac':mac,'interface':'eth0'}
    p=Path('/etc/beastagotchi/home_dock.json'); p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,indent=2)+'\n')
    p.chmod(0o644)
    print('Enrolled Beast home dock fingerprint:')
    print(json.dumps(obj,indent=2))
    return 0
if __name__=='__main__': raise SystemExit(main())
