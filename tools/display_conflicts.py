#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import tomllib
from pathlib import Path

DISPLAY_OWNERS={
    'theme_manager':'Korrie71 Theme Manager',
    'fancygotchi':'Fancygotchi',
}


def main() -> int:
    ap=argparse.ArgumentParser(description='Detect enabled Pwnagotchi plugins that compete for display ownership.')
    ap.add_argument('--config',default='/etc/pwnagotchi/config.toml')
    ap.add_argument('--json',action='store_true')
    args=ap.parse_args()
    try:cfg=tomllib.loads(Path(args.config).read_text(errors='replace'))
    except Exception as exc:
        print(f'cannot parse {args.config}: {exc}',file=sys.stderr);return 2
    plugins=((cfg.get('main') or {}).get('plugins') or {}) if isinstance(cfg,dict) else {}
    conflicts=[]
    for key,label in DISPLAY_OWNERS.items():
        row=plugins.get(key) if isinstance(plugins,dict) else None
        if isinstance(row,dict) and bool(row.get('enabled')):
            conflicts.append({'name':key,'label':label,'reason':'legacy plugin owns/hooks Pwnagotchi display rendering'})
    if args.json:print(json.dumps({'count':len(conflicts),'items':conflicts},indent=2))
    elif conflicts:
        for row in conflicts:print(f"{row['name']}: ENABLED ({row['label']})")
    else:print('No enabled known display-owner plugins detected.')
    return 1 if conflicts else 0

if __name__=='__main__':raise SystemExit(main())
