#!/usr/bin/env bash
set -euo pipefail
SRC="$(cd "$(dirname "$0")" && pwd)"
OUT=/tmp/beast-v011-validation
rm -rf "$OUT"; mkdir -p "$OUT"; chown pi:pi "$OUT"

echo '[1/11] core health/state/catalogs + expeditions'
curl -fsS http://127.0.0.1:8090/health > "$OUT/health.json"
curl -fsS 'http://127.0.0.1:8090/state?meta=0' > "$OUT/state.json"
curl -fsS 'http://127.0.0.1:8090/events?limit=120&transient=0' > "$OUT/events.json"
curl -fsS 'http://127.0.0.1:8090/achievements' > "$OUT/achievements.json"
curl -fsS 'http://127.0.0.1:8090/achievements?kind=awards' > "$OUT/awards.json"
curl -fsS 'http://127.0.0.1:8090/expeditions?limit=20' > "$OUT/expeditions.json"
curl -fsS 'http://127.0.0.1:8090/expedition?point_limit=500' > "$OUT/expedition-current.json" || true

echo '[2/11] exact Jayofelony native frame source'
beast-pwn-native > "$OUT/native-frame-status.json" || true
cp -a /var/tmp/pwnagotchi/pwnagotchi.png "$OUT/pwnagotchi-native-source.png" 2>/dev/null || true

echo '[3/11] production touch decision'
beast-touchcal status > "$OUT/touchcal-status.txt" 2>&1 || true
cp -a /opt/beast-ui/config/touch.json "$OUT/touch-active.json" 2>/dev/null || true
cp -a /opt/beast-ui/config/touch_experimental_rejected_v092.json "$OUT/touch-experimental-rejected-v092.json" 2>/dev/null || true

echo '[4/11] installed Python compile/import gate'
/opt/.pwn/bin/python3 -m compileall -q /opt/beast-ui/beastui /opt/beast-core/beastcore
PYTHONPATH=/opt/beast-core:/opt/beast-ui /opt/.pwn/bin/python3 - <<'PY' > "$OUT/import-gate.txt"
import beastcore,beastui
print('beastcore',beastcore.__version__)
print('beastui',beastui.__version__)
assert beastcore.__version__ == '0.11.0'
assert beastui.__version__ == '0.11.0'
PY

echo '[5/11] all theme smoke renders'
for T in pwn_native_raw pwn_native_dark pwn_native_light pwn_native_chroma pwn_dark pwn_light pwn_chroma classic matrix starcore blackice hunter minimal synthwave amber_tactical ghost_minimal; do
  sudo -u pi PYTHONPATH=/opt/beast-ui /opt/.pwn/bin/python3 -m beastui --root /opt/beast-ui --theme "$T" --output "$OUT/theme-$T.png" --duration 0.12 >/dev/null 2>&1
done

echo '[6/11] Governor + Expedition + new-theme validation gallery'
sudo -u pi PYTHONPATH=/opt/beast-ui /opt/.pwn/bin/python3 "$SRC/tools/render_v011_validation.py" --root /opt/beast-ui --state "$OUT/state.json" --out "$OUT/previews"

echo '[7/11] renderer registry'
PYTHONPATH=/opt/beast-ui /opt/.pwn/bin/python3 - <<'PY' > "$OUT/renderer-registry.json"
import json
from beastui.engine import BeastUI
print(json.dumps(BeastUI.RENDERER_CHOICES,indent=2))
assert len(BeastUI.RENDERER_CHOICES['spectrum']) >= 10
assert {'histogram','donut','waveform','waterfall','polar'} <= set(BeastUI.RENDERER_CHOICES['spectrum'])
PY

echo '[8/11] governor policy registry'
PYTHONPATH=/opt/beast-core /opt/.pwn/bin/python3 - <<'PY' > "$OUT/governor-policy.json"
import json
from beastcore.governor import ResourceGovernor
print(json.dumps(ResourceGovernor.POLICY,indent=2))
assert ResourceGovernor.POLICY['SURVIVAL']['fps_cap'] <= 3
assert ResourceGovernor._throttle_bits('0x50000') == (False, True)
assert ResourceGovernor._throttle_bits('0x1')[0] is True
PY

echo '[9/11] package unit regression'
if command -v pytest >/dev/null 2>&1; then
  (cd "$SRC" && PYTHONPATH=. pytest -q) > "$OUT/pytest.txt"
else
  echo 'pytest not installed on target; clean-package CI result is authoritative' > "$OUT/pytest.txt"
fi

echo '[10/11] services/runtime/journals'
{
  echo '== services =='; systemctl is-active pwnagotchi beast-core beast-ui gpsd 2>&1 || true
  echo '== versions =='; python3 - <<'PY'
import sys
sys.path.insert(0,'/opt/beast-core');sys.path.insert(0,'/opt/beast-ui')
import beastcore,beastui
print('beastcore',beastcore.__version__);print('beastui',beastui.__version__)
PY
} > "$OUT/runtime.txt"
sudo journalctl -u beast-core --no-pager -n 180 > "$OUT/beast-core-journal.txt" 2>&1 || true
sudo journalctl -u pwnagotchi --no-pager -n 120 > "$OUT/pwnagotchi-journal.txt" 2>&1 || true

echo '[11/11] package'
tar -czf /home/pi/beast-core-validation-v011.tar.gz -C /tmp beast-v011-validation
chown pi:pi /home/pi/beast-core-validation-v011.tar.gz
echo 'Validation complete: /home/pi/beast-core-validation-v011.tar.gz'
echo 'Physical framebuffer was NOT touched by this validation.'
