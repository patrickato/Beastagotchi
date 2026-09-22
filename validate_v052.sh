#!/usr/bin/env bash
set -euo pipefail
[[ ${EUID:-$(id -u)} -eq 0 ]] || { echo 'Run with sudo.'; exit 1; }
OUT=/tmp/beast-v052-validation
rm -rf "$OUT"; mkdir -p "$OUT"; chown pi:pi "$OUT"
ROOT="$(cd "$(dirname "$0")" && pwd)"
PYTHONPATH=/opt/beast-ui:/opt/beast-core /opt/.pwn/bin/python3 -m pytest -q "$ROOT/tests" > "$OUT/tests.txt" || { cat "$OUT/tests.txt"; exit 2; }
sudo -u pi PYTHONPATH=/opt/beast-ui:/opt/beast-core /opt/.pwn/bin/python3 -m beastui --root /opt/beast-ui --output "$OUT/ui-classic.png" --duration 1.2
file "$OUT/ui-classic.png" > "$OUT/render.txt"
cp -a /opt/beast-ui/config/touch.json "$OUT/touch.json" 2>/dev/null || true
cat "$OUT/tests.txt"
cat "$OUT/render.txt"
echo 'Physical framebuffer was NOT touched.'
tar -czf /home/pi/beast-core-validation-v052.tar.gz -C /tmp beast-v052-validation
chown pi:pi /home/pi/beast-core-validation-v052.tar.gz
echo 'Validation complete: /home/pi/beast-core-validation-v052.tar.gz'
