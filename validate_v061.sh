#!/usr/bin/env bash
set -euo pipefail
OUT=/tmp/beast-v06-validation
rm -rf "$OUT"; mkdir -p "$OUT"; chown pi:pi "$OUT"
echo '[1/5] core health/state'
curl -fsS http://127.0.0.1:8090/health > "$OUT/health.json"
curl -fsS 'http://127.0.0.1:8090/state?meta=0' > "$OUT/state.json"
echo '[2/5] off-screen render all six structural themes'
for T in classic matrix starcore blackice hunter minimal; do
  sudo -u pi PYTHONPATH=/opt/beast-ui /opt/.pwn/bin/python3 -m beastui --root /opt/beast-ui --theme "$T" --output "$OUT/theme-$T.png" --duration 0.35 >/dev/null 2>&1
  file "$OUT/theme-$T.png" >> "$OUT/render-files.txt"
done
echo '[3/5] unit tests packaged build'
cd "$(dirname "$0")"
if python3 -c 'import pytest' >/dev/null 2>&1; then
  PYTHONPATH=. python3 -m pytest -q > "$OUT/pytest.txt"
else
  echo 'SKIPPED: pytest is a development dependency and is not installed on this target.' > "$OUT/pytest.txt"
fi
echo '[4/5] hardware/dock/power discovery snapshot'
{
  echo '== i2c =='; ls -l /dev/i2c-* 2>&1 || true
  echo '== usb =='; lsusb 2>&1 || true
  echo '== ethernet =='; ip addr show eth0 2>&1 || true
  echo '== route =='; ip route 2>&1 || true
  echo '== home dock profile =='; cat /etc/beastagotchi/home_dock.json 2>&1 || true
} > "$OUT/hardware.txt"
sudo journalctl -u beast-core --no-pager -n 120 > "$OUT/beast-core-journal.txt"
echo '[5/5] package'
tar -czf /home/pi/beast-core-validation-v06.tar.gz -C /tmp beast-v06-validation
chown pi:pi /home/pi/beast-core-validation-v06.tar.gz
echo 'Validation complete: /home/pi/beast-core-validation-v06.tar.gz'
echo 'Physical framebuffer was NOT touched by this validation.'
