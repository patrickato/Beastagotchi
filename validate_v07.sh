#!/usr/bin/env bash
set -euo pipefail
OUT=/tmp/beast-v07-validation
rm -rf "$OUT"; mkdir -p "$OUT"; chown pi:pi "$OUT"
echo '[1/5] core health/state'
curl -fsS http://127.0.0.1:8090/health > "$OUT/health.json"
curl -fsS 'http://127.0.0.1:8090/state?meta=0' > "$OUT/state.json"
echo '[2/5] off-screen render all six structural themes'
for T in classic matrix starcore blackice hunter minimal; do
  sudo -u pi PYTHONPATH=/opt/beast-ui /opt/.pwn/bin/python3 -m beastui --root /opt/beast-ui --theme "$T" --output "$OUT/theme-$T.png" --duration 0.35 >/dev/null 2>&1
  file "$OUT/theme-$T.png" >> "$OUT/render-files.txt"
done
echo '[3/5] target runtime/dependency snapshot'
{
  echo '== pwn python =='; /opt/.pwn/bin/python3 -V 2>&1 || true
  echo '== pillow =='; /opt/.pwn/bin/python3 - <<'PY'
try:
 import PIL; print(getattr(PIL,'__version__','unknown'))
except Exception as e: print('ERROR',e)
try:
 import numpy; print('numpy',numpy.__version__)
except Exception as e: print('numpy not present:',e)
PY
  echo '== docs =='; ls -l /usr/local/share/beastagotchi 2>&1 || true
  echo '== beast-paths =='; command -v beast-paths 2>&1 || true
} > "$OUT/runtime.txt"
echo '[4/5] plugin/hardware/dock snapshot'
{
  echo '== plugin config =='
  python3 - <<'PY'
import json
try:
 s=json.load(open('/tmp/beast-v07-validation/state.json'))
 for k in ('plugins.repo_count','plugins.repos','plugins.custom_dir','plugins.conf_d','plugins.configured_count','plugins.enabled_count','plugins.installed_custom_count'):
  print(k,':',s.get(k))
except Exception as e: print('ERROR',e)
PY
  echo '== i2c =='; ls -l /dev/i2c-* 2>&1 || true
  echo '== usb =='; lsusb 2>&1 || true
  echo '== ethernet =='; ip addr show eth0 2>&1 || true
  echo '== route =='; ip route 2>&1 || true
  echo '== home dock profile =='; cat /etc/beastagotchi/home_dock.json 2>&1 || true
} > "$OUT/platform.txt"
sudo journalctl -u beast-core --no-pager -n 120 > "$OUT/beast-core-journal.txt"
echo '[5/5] package'
tar -czf /home/pi/beast-core-validation-v07.tar.gz -C /tmp beast-v07-validation
chown pi:pi /home/pi/beast-core-validation-v07.tar.gz
echo 'Validation complete: /home/pi/beast-core-validation-v07.tar.gz'
echo 'Physical framebuffer was NOT touched by this validation.'
