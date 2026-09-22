#!/usr/bin/env bash
set -euo pipefail
[[ ${EUID:-$(id -u)} -eq 0 ]] || { echo 'Run with sudo.'; exit 1; }
OUT=/tmp/beast-v05-validation
rm -rf "$OUT"; mkdir -p "$OUT"; chown pi:pi "$OUT"

curl -s http://127.0.0.1:8090/health > "$OUT/health.json"
curl -s 'http://127.0.0.1:8090/state?meta=0' > "$OUT/state.json"
/opt/beast-ui/bin/display_config.py --config /etc/pwnagotchi/config.toml status > "$OUT/display-before.json"

sudo -u pi PYTHONPATH=/opt/beast-ui /opt/.pwn/bin/python3 -m beastui --root /opt/beast-ui --output "$OUT/ui-classic.png" --theme classic --duration 1
sudo -u pi PYTHONPATH=/opt/beast-ui /opt/.pwn/bin/python3 -m beastui --root /opt/beast-ui --output "$OUT/ui-blackice.png" --theme blackice --duration 1

/opt/.pwn/bin/python3 - <<PY > "$OUT/ui-image-check.txt"
from PIL import Image
for p in ["$OUT/ui-classic.png","$OUT/ui-blackice.png"]:
 im=Image.open(p); print(p, im.size, im.mode)
 assert im.size==(480,320)
PY

journalctl -u beast-core.service --no-pager -n 100 > "$OUT/beast-core-journal.txt" || true
TAR=/home/pi/beast-core-validation-v05-offscreen.tar.gz
tar -czf "$TAR" -C /tmp "$(basename "$OUT")"
chown pi:pi "$TAR"
echo "Off-screen validation complete: $TAR"
echo 'Physical framebuffer was NOT touched.'
