#!/usr/bin/env bash
set -euo pipefail
SRC="$(cd "$(dirname "$0")" && pwd)"
OUT=/tmp/beast-v095-validation
rm -rf "$OUT"; mkdir -p "$OUT"; chown pi:pi "$OUT"

echo '[1/9] core health/state/catalogs'
curl -fsS http://127.0.0.1:8090/health > "$OUT/health.json"
curl -fsS 'http://127.0.0.1:8090/state?meta=0' > "$OUT/state.json"
curl -fsS 'http://127.0.0.1:8090/events?limit=120&transient=0' > "$OUT/events.json"
curl -fsS 'http://127.0.0.1:8090/achievements' > "$OUT/achievements.json"
curl -fsS 'http://127.0.0.1:8090/achievements?kind=awards' > "$OUT/awards.json"

echo '[2/9] exact Jayofelony native frame source'
beast-pwn-native > "$OUT/native-frame-status.json" || true
cp -a /var/tmp/pwnagotchi/pwnagotchi.png "$OUT/pwnagotchi-native-source.png" 2>/dev/null || true

echo '[3/9] production touch decision'
beast-touchcal status > "$OUT/touchcal-status.txt" 2>&1 || true
cp -a /opt/beast-ui/config/touch.json "$OUT/touch-active.json" 2>/dev/null || true
cp -a /opt/beast-ui/config/touch_experimental_rejected_v092.json "$OUT/touch-experimental-rejected-v092.json" 2>/dev/null || true

echo '[4/9] installed Python compile/import gate'
/opt/.pwn/bin/python3 -m compileall -q /opt/beast-ui/beastui /opt/beast-core/beastcore
PYTHONPATH=/opt/beast-core:/opt/beast-ui /opt/.pwn/bin/python3 - <<'PY' > "$OUT/import-gate.txt"
import beastcore,beastui
print('beastcore',beastcore.__version__)
print('beastui',beastui.__version__)
assert beastcore.__version__ == '0.9.5'
assert beastui.__version__ == '0.9.5'
PY

echo '[5/9] all theme smoke renders'
for T in pwn_native_raw pwn_native_dark pwn_native_light pwn_native_chroma pwn_dark pwn_light pwn_chroma classic matrix starcore blackice hunter minimal; do
  sudo -u pi PYTHONPATH=/opt/beast-ui /opt/.pwn/bin/python3 -m beastui --root /opt/beast-ui --theme "$T" --output "$OUT/theme-$T.png" --duration 0.12 >/dev/null 2>&1
done

echo '[6/9] interaction/theme/progression preview renders'
sudo -u pi PYTHONPATH=/opt/beast-ui /opt/.pwn/bin/python3 "$SRC/tools/render_v095_validation.py" --root /opt/beast-ui --state "$OUT/state.json" --out "$OUT/previews"

echo '[7/9] rare presentation preview metadata'
for P in fade drift cross orbit ghost storm apparition cinematic; do
  echo "$P" >> "$OUT/rare-presentations.txt"
done

echo '[8/9] services/runtime/journals'
{
  echo '== services =='; systemctl is-active pwnagotchi beast-core beast-ui gpsd 2>&1 || true
  echo '== native frame =='; stat /var/tmp/pwnagotchi/pwnagotchi.png 2>&1 || true
  echo '== versions =='; python3 - <<'PY'
import sys
sys.path.insert(0,'/opt/beast-core');sys.path.insert(0,'/opt/beast-ui')
import beastcore,beastui
print('beastcore',beastcore.__version__);print('beastui',beastui.__version__)
PY
} > "$OUT/runtime.txt"
sudo journalctl -u beast-core --no-pager -n 180 > "$OUT/beast-core-journal.txt" 2>&1 || true
sudo journalctl -u pwnagotchi --no-pager -n 120 > "$OUT/pwnagotchi-journal.txt" 2>&1 || true

echo '[9/9] package'
tar -czf /home/pi/beast-core-validation-v095.tar.gz -C /tmp beast-v095-validation
chown pi:pi /home/pi/beast-core-validation-v095.tar.gz
echo 'Validation complete: /home/pi/beast-core-validation-v095.tar.gz'
echo 'Physical framebuffer was NOT touched by this validation.'
