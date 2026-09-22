#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,time
from pathlib import Path

p=argparse.ArgumentParser(prog='beast-rare-preview',description='Preview Beastagotchi rare visuals without changing the real rare schedule or achievements.')
p.add_argument('mode',choices=['omen','moment','clear'])
p.add_argument('seconds',type=int,nargs='?',default=15)
p.add_argument('--sigil',choices=['veil','eye','spiral','gate','constellation','cipher'],default='eye')
p.add_argument('--rarity',choices=['rare','epic','legendary','mythic'],default='legendary')
p.add_argument('--presentation',choices=['fade','drift','cross','orbit','ghost','storm','apparition','cinematic'],default='drift')
a=p.parse_args()
path=Path('/var/lib/beastagotchi/ui/rare_preview.json');path.parent.mkdir(parents=True,exist_ok=True)
if a.mode=='clear':
    try:path.unlink()
    except FileNotFoundError:pass
    print('Rare visual preview cleared.')
else:
    seconds=max(3,min(120,int(a.seconds)))
    obj={'mode':a.mode,'sigil':a.sigil,'rarity':a.rarity,'presentation':a.presentation,'expires':time.time()+seconds}
    path.write_text(json.dumps(obj,separators=(',',':'))+'\n')
    print(f'Rare {a.mode} preview active for {seconds}s. This does NOT affect the real annual schedule or achievements.')
