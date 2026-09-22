#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os, shutil, subprocess, sys, time
from pathlib import Path

ACTIVE=Path('/opt/beast-ui/config/touch.json')
EXPERIMENTAL=Path('/opt/beast-ui/config/touch_experimental_rejected_v092.json')
STATE=Path('/var/lib/beastagotchi/touch-calibration')
BACKUP=STATE/'pre-v092-touch.json'
META=STATE/'state.json'
ROLLBACK_UNIT='beast-touchcal-rollback'

def read_json(path):
    return json.loads(path.read_text())

def write_json(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+'.tmp')
    tmp.write_text(json.dumps(obj,indent=2)+'\n')
    os.replace(tmp,path)

def restart_ui():
    subprocess.run(['systemctl','try-restart','beast-ui.service'],check=False)

def cancel_timer():
    subprocess.run(['systemctl','stop',ROLLBACK_UNIT+'.timer'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=False)
    subprocess.run(['systemctl','stop',ROLLBACK_UNIT+'.service'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=False)

def status():
    print('Active:',ACTIVE)
    if ACTIVE.exists(): print(json.dumps(read_json(ACTIVE).get('transform'),indent=2))
    else: print('MISSING')
    print('\nExperimental Touch-Lab candidate (physically A/B tested and REJECTED):',EXPERIMENTAL)
    if EXPERIMENTAL.exists():
        r=read_json(EXPERIMENTAL); print(json.dumps(r.get('transform'),indent=2)); print('Lab validation:',json.dumps(r.get('validation'),indent=2))
        print('Production decision: preserve the restored/original calibration; candidate is reference-only.')
    else: print('MISSING')
    print('\nBackup:',BACKUP,'exists='+str(BACKUP.exists()))
    if META.exists(): print('State:',META.read_text().strip())

def apply_test(minutes:int,experimental:bool=False):
    if os.geteuid()!=0: raise SystemExit('Run with sudo.')
    if not experimental: raise SystemExit('The Touch-Lab candidate was rejected in physical A/B testing. Re-run with --experimental only for deliberate diagnostics.')
    if not ACTIVE.exists() or not EXPERIMENTAL.exists(): raise SystemExit('Required calibration file missing.')
    STATE.mkdir(parents=True,exist_ok=True)
    if not BACKUP.exists(): shutil.copy2(ACTIVE,BACKUP)
    active=read_json(ACTIVE); rec=read_json(EXPERIMENTAL)
    active['transform']=rec['transform']
    active['calibration_profile']='touchlab-pooled-v092'
    active['calibration_source']=rec.get('source')
    write_json(ACTIVE,active)
    write_json(META,{'mode':'test','applied_at':time.time(),'rollback_minutes':minutes,'backup':str(BACKUP)})
    cancel_timer()
    subprocess.run(['systemd-run','--unit',ROLLBACK_UNIT,'--on-active',f'{minutes}m','/usr/local/bin/beast-touchcal','restore'],check=True)
    restart_ui()
    print(f'EXPERIMENTAL rejected calibration applied for a {minutes}-minute reversible diagnostic test.')
    print('Confirm: sudo beast-touchcal confirm')
    print('Restore now: sudo beast-touchcal restore')

def confirm():
    if os.geteuid()!=0: raise SystemExit('Run with sudo.')
    cancel_timer()
    write_json(META,{'mode':'confirmed','confirmed_at':time.time(),'backup':str(BACKUP)})
    print('Touch calibration confirmed. Backup retained:',BACKUP)

def restore():
    if os.geteuid()!=0: raise SystemExit('Run with sudo.')
    cancel_timer()
    if not BACKUP.exists(): raise SystemExit('No pre-v0.9.2 calibration backup exists.')
    shutil.copy2(BACKUP,ACTIVE)
    write_json(META,{'mode':'restored','restored_at':time.time(),'backup':str(BACKUP)})
    restart_ui()
    print('Previous calibration restored.')

def main():
    p=argparse.ArgumentParser(description='Beastagotchi reversible touch calibration manager')
    sub=p.add_subparsers(dest='cmd',required=True)
    sub.add_parser('status')
    t=sub.add_parser('apply-test');t.add_argument('minutes',nargs='?',type=int,default=10);t.add_argument('--experimental',action='store_true',help='required: candidate was rejected in physical A/B testing')
    sub.add_parser('confirm');sub.add_parser('restore')
    a=p.parse_args()
    if a.cmd=='status':status()
    elif a.cmd=='apply-test':apply_test(max(1,min(a.minutes,120)),a.experimental)
    elif a.cmd=='confirm':confirm()
    elif a.cmd=='restore':restore()
if __name__=='__main__':main()
