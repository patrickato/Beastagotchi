#!/usr/bin/env bash
set -euo pipefail
OUT=/tmp/beast-v04-validation
rm -rf "$OUT"
mkdir -p "$OUT"

curl -fsS http://127.0.0.1:8090/health > "$OUT/health.json"
curl -fsS 'http://127.0.0.1:8090/state?meta=0' > "$OUT/state.json"
curl -fsS 'http://127.0.0.1:8090/state?meta=1' > "$OUT/state_meta.json"
curl -fsS 'http://127.0.0.1:8090/events?limit=80&transient=0' > "$OUT/events_semantic.json"
curl -fsS 'http://127.0.0.1:8090/history?key=system.temp.cpu_c&limit=12' > "$OUT/history_temp.json" || true

systemctl status beast-core pwnagotchi bettercap gpsd --no-pager > "$OUT/services.txt" 2>&1 || true
journalctl -u beast-core --no-pager -n 120 > "$OUT/beast-core-journal.txt" 2>&1 || true
journalctl -u pwnagotchi --no-pager -n 80 > "$OUT/pwnagotchi-journal.txt" 2>&1 || true

{
  echo "python=$(/opt/.pwn/bin/python3 --version 2>&1)"
  /opt/.pwn/bin/python3 - <<'PY'
import PIL
print('pillow='+str(getattr(PIL,'__version__','unknown')))
try:
 import numpy
 print('numpy='+str(numpy.__version__))
except Exception as e:
 print('numpy=unavailable:'+type(e).__name__)
PY
} > "$OUT/ui-runtime.txt"

# Safe off-screen render: this does NOT write to /dev/fb1.
sudo -u pi env PYTHONPATH=/opt/beast-ui /opt/.pwn/bin/python3 -m beastui \
  --root /opt/beast-ui --theme classic --output "$OUT/ui-classic.png" --duration 1.2
sudo -u pi env PYTHONPATH=/opt/beast-ui /opt/.pwn/bin/python3 -m beastui \
  --root /opt/beast-ui --theme blackice --output "$OUT/ui-blackice.png" --duration 0.5

/opt/.pwn/bin/python3 - <<PY > "$OUT/ui-image-check.txt"
from PIL import Image
from pathlib import Path
for p in sorted(Path('$OUT').glob('ui-*.png')):
    im=Image.open(p)
    print(p.name, im.size, im.mode, p.stat().st_size)
    if im.size != (480,320):
        raise SystemExit('bad size: '+p.name)
PY

if [[ -f /run/beastagotchi/pwnagotchi_bridge.json ]]; then
  cp /run/beastagotchi/pwnagotchi_bridge.json "$OUT/pwnagotchi_bridge.json"
fi

ARCHIVE=/home/pi/beast-core-validation-v04.tar.gz
tar -czf "$ARCHIVE" -C /tmp beast-v04-validation
chown pi:pi "$ARCHIVE" || true

echo
printf 'Validation complete: %s\n' "$ARCHIVE"
printf 'Physical framebuffer was NOT touched by this validation.\n'
