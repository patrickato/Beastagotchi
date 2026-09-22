#!/usr/bin/env python3
from pathlib import Path
import socket
p=Path('/var/lib/beastagotchi/ui/studio.token')
if not p.exists():
    raise SystemExit('Beast Studio token not created yet. Start beast-studio first.')
t=p.read_text().strip();host=socket.gethostname() or 'beastagotchi'
print(f'Beast Studio: http://{host}.local:8091/?token={t}')
print(f'Token: {t}')
