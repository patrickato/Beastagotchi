#!/usr/bin/env bash
set -euo pipefail
[[ ${EUID:-$(id -u)} -eq 0 ]] || { echo 'Run with sudo.'; exit 1; }
OUT=/tmp/beast-v051-validation
rm -rf "$OUT"
mkdir -p "$OUT"
chown pi:pi "$OUT"

systemctl start beast-core.service
sleep 3
curl -fsS http://127.0.0.1:8090/health > "$OUT/core-health.json"
curl -fsS 'http://127.0.0.1:8090/state?meta=0' > "$OUT/core-state.json"

sudo -u pi PYTHONPATH=/opt/beast-ui /opt/.pwn/bin/python3 -m beastui \
  --root /opt/beast-ui --output "$OUT/ui-classic.png" --theme classic --duration 1.5
sudo -u pi PYTHONPATH=/opt/beast-ui /opt/.pwn/bin/python3 -m beastui \
  --root /opt/beast-ui --output "$OUT/ui-blackice.png" --theme blackice --duration 1.5

PYTHONPATH=/opt/beast-ui:/opt/beast-core /opt/.pwn/bin/python3 -m pytest -q "$(cd "$(dirname "$0")" && pwd)/tests/test_touch_v051.py" > "$OUT/touch-tests.txt" || {
  cat "$OUT/touch-tests.txt"; exit 2;
}

journalctl -u beast-ui.service --no-pager -n 80 > "$OUT/ui-journal.txt" 2>/dev/null || true
journalctl -u beast-core.service --no-pager -n 80 > "$OUT/core-journal.txt" 2>/dev/null || true
cp -a /opt/beast-ui/config/touch.json "$OUT/touch.json" 2>/dev/null || true

tar -czf /home/pi/beast-core-validation-v051.tar.gz -C /tmp beast-v051-validation
chown pi:pi /home/pi/beast-core-validation-v051.tar.gz

echo 'Validation complete: /home/pi/beast-core-validation-v051.tar.gz'
echo 'Physical framebuffer was NOT touched by this validation.'
