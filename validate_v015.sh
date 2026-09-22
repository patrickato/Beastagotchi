#!/usr/bin/env bash
set -euo pipefail
SRC="$(cd "$(dirname "$0")" && pwd)"
OUT=/tmp/beast-v015-validation
rm -rf "$OUT"; mkdir -p "$OUT"; chown pi:pi "$OUT"

STUDIO_WAS_ACTIVE=0
systemctl is-active --quiet beast-studio.service && STUDIO_WAS_ACTIVE=1 || true
cleanup(){
  if [[ "$STUDIO_WAS_ACTIVE" -eq 0 ]]; then systemctl stop beast-studio.service 2>/dev/null || true; fi
}
trap cleanup EXIT

echo '[1/13] live Core catalogs / records / provenance'
curl -fsS http://127.0.0.1:8090/health > "$OUT/health.json"
curl -fsS 'http://127.0.0.1:8090/state?meta=0' > "$OUT/state.json"
curl -fsS 'http://127.0.0.1:8090/events?limit=160&transient=0' > "$OUT/events.json"
curl -fsS 'http://127.0.0.1:8090/telemetry' > "$OUT/telemetry.json"
curl -fsS 'http://127.0.0.1:8090/plugins' > "$OUT/plugins.json"
curl -fsS 'http://127.0.0.1:8090/actions?limit=30' > "$OUT/actions.json"
curl -fsS 'http://127.0.0.1:8090/beastdex?limit=30' > "$OUT/beastdex.json"
curl -fsS 'http://127.0.0.1:8090/capture-vault?limit=30' > "$OUT/capture-vault.json"
curl -fsS 'http://127.0.0.1:8090/expeditions?limit=20' > "$OUT/expeditions.json"
curl -fsS 'http://127.0.0.1:8090/expedition?point_limit=500' > "$OUT/expedition-current.json" || true

echo '[2/13] bridge/native/touch invariants'
beast-pwn-native > "$OUT/native-frame-status.json" || true
cp -a /var/tmp/pwnagotchi/pwnagotchi.png "$OUT/pwnagotchi-native-source.png" 2>/dev/null || true
beast-touchcal status > "$OUT/touchcal-status.txt" 2>&1 || true
cp -a /opt/beast-ui/config/touch.json "$OUT/touch-active.json" 2>/dev/null || true
ls -lah /run/beastagotchi/pwnagotchi_bridge.json > "$OUT/bridge-file.txt" 2>&1 || true

echo '[3/13] installed compile/import/version gate'
/opt/.pwn/bin/python3 -m compileall -q /opt/beast-ui/beastui /opt/beast-ui/beaststudio /opt/beast-core/beastcore
PYTHONPATH=/opt/beast-core:/opt/beast-ui /opt/.pwn/bin/python3 - <<'PY' > "$OUT/import-gate.txt"
import beastcore,beastui,beaststudio
print('beastcore',beastcore.__version__)
print('beastui',beastui.__version__)
print('beaststudio',beaststudio.__version__)
assert beastcore.__version__ == '0.15.1'
assert beastui.__version__ == '0.15.1'
assert beaststudio.__version__ == '0.15.1'
PY

echo '[4/13] privileged action channel is local-only'
{
  stat -c 'socket=%n mode=%a uid=%u gid=%g' /run/beastagotchi/action.sock
  id pi
  grep -n '^SupplementaryGroups=' /etc/systemd/system/beast-studio.service /etc/systemd/system/beast-ui.service || true
} > "$OUT/action-channel.txt"
test -S /run/beastagotchi/action.sock

echo '[5/13] Beast Studio paired live schema'
systemctl reset-failed beast-studio.service 2>/dev/null || true
systemctl start beast-studio.service
STUDIO_READY=0
for _ in $(seq 1 60); do
  if systemctl is-active --quiet beast-studio.service && [[ -s /var/lib/beastagotchi/ui/studio.token ]]; then
    TOKEN="$(cat /var/lib/beastagotchi/ui/studio.token)"
    if curl -fsS --max-time 2 -H "X-Beast-Studio-Token: $TOKEN" http://127.0.0.1:8091/api/schema > "$OUT/studio-schema.json" 2>/dev/null; then
      STUDIO_READY=1
      break
    fi
  fi
  sleep .5
done
if [[ "$STUDIO_READY" -ne 1 ]]; then
  systemctl status beast-studio.service --no-pager -l > "$OUT/beast-studio-status.txt" 2>&1 || true
  journalctl -u beast-studio.service --no-pager -n 120 > "$OUT/beast-studio-startup-journal.txt" 2>&1 || true
  tar -czf /home/pi/beast-core-validation-v015-failed.tar.gz -C /tmp beast-v015-validation
  chown pi:pi /home/pi/beast-core-validation-v015-failed.tar.gz
  echo 'ERROR: Beast Studio did not become ready within 30 seconds.'
  echo 'Failure bundle: /home/pi/beast-core-validation-v015-failed.tar.gz'
  exit 1
fi
curl -fsS --max-time 5 -H "X-Beast-Studio-Token: $TOKEN" http://127.0.0.1:8091/api/preferences > "$OUT/studio-preferences.json"
curl -fsS --max-time 5 -H "X-Beast-Studio-Token: $TOKEN" http://127.0.0.1:8091/api/plugins > "$OUT/studio-plugins.json"
# Never archive the pairing token itself.

echo '[6/13] read-only plugin action planning through local socket'
sudo -u pi -g beastagotchi PYTHONPATH=/opt/beast-ui /opt/.pwn/bin/python3 - <<'PY' > "$OUT/action-plan.txt"
from beaststudio.action_client import BeastActionClient
c=BeastActionClient()
# Protected bridge disable is a safe no-mutation plan and must be blocked.
r=c.plan('plugin.toggle',{'name':'beast_bridge','enabled':False})
print(r)
assert r.get('ok') is True
assert (r.get('plan') or {}).get('allowed') is False
PY

echo '[7/13] all-theme off-screen smoke renders'
for T in pwn_native_raw pwn_native_dark pwn_native_light pwn_native_chroma pwn_dark pwn_light pwn_chroma classic matrix starcore blackice hunter minimal synthwave amber_tactical ghost_minimal cyberpunk wopr_norad lcars retro_crt; do
  sudo -u pi PYTHONPATH=/opt/beast-ui /opt/.pwn/bin/python3 -m beastui --root /opt/beast-ui --theme "$T" --output "$OUT/theme-$T.png" --duration 0.08 >/dev/null 2>&1
done

echo '[8/13] platform / Studio / Dashboard validation gallery'
sudo -u pi PYTHONPATH=/opt/beast-ui /opt/.pwn/bin/python3 "$SRC/tools/render_v015_validation.py" --root /opt/beast-ui --state "$OUT/state.json" --events "$OUT/events.json" --out "$OUT/previews"

echo '[9/13] app/board/dashboard/runtime registry'
PYTHONPATH=/opt/beast-ui /opt/.pwn/bin/python3 - <<'PY' > "$OUT/ui-registry.json"
import json
from beastui.apps import AppRegistry
from beastui.pages import Pages
from beastui.customization import DEFAULT_DASHBOARD_WIDGETS,WIDGET_STYLES,MAX_DASHBOARD_WIDGETS
print(json.dumps({'main_pages':Pages.IDS,'app_count':len(AppRegistry().all()),'categories':AppRegistry().categories(),'widget_styles':WIDGET_STYLES,'dashboard_defaults':DEFAULT_DASHBOARD_WIDGETS,'max_dashboard_widgets':MAX_DASHBOARD_WIDGETS},indent=2))
assert 'dashboard' in Pages.IDS
assert len(AppRegistry().all()) > len(Pages.IDS)
PY

echo '[10/13] package unit regression'
if command -v pytest >/dev/null 2>&1; then
  (cd "$SRC" && PYTHONPATH=. pytest -q) > "$OUT/pytest.txt"
else
  echo 'pytest not installed on target; clean-package CI result is authoritative' > "$OUT/pytest.txt"
fi

echo '[11/13] service/runtime/performance evidence'
{
  echo '== services =='; systemctl is-active pwnagotchi beast-core beast-ui beast-studio gpsd 2>&1 || true
  echo '== governor =='; python3 - <<'PY'
import json
s=json.load(open('/tmp/beast-v015-validation/state.json'))
for k in ('system.temp.cpu_c','system.cpu.total','governor.mode','governor.reason','performance.beast.cpu_pct','performance.ui.avg_render_ms','performance.fb.write_ratio_pct'):
 print(k,'=',s.get(k))
PY
} > "$OUT/runtime.txt"
cp -a /run/beastagotchi/ui-runtime.json "$OUT/ui-runtime.json" 2>/dev/null || true
cp -a /var/lib/beastagotchi/ui/preferences.json "$OUT/ui-preferences.json" 2>/dev/null || true

echo '[12/13] journals'
sudo journalctl -u beast-core --no-pager -n 220 > "$OUT/beast-core-journal.txt" 2>&1 || true
sudo journalctl -u beast-ui --no-pager -n 180 > "$OUT/beast-ui-journal.txt" 2>&1 || true
sudo journalctl -u beast-studio --no-pager -n 160 > "$OUT/beast-studio-journal.txt" 2>&1 || true
sudo journalctl -u pwnagotchi --no-pager -n 120 > "$OUT/pwnagotchi-journal.txt" 2>&1 || true

echo '[13/13] package'
tar -czf /home/pi/beast-core-validation-v015.tar.gz -C /tmp beast-v015-validation
chown pi:pi /home/pi/beast-core-validation-v015.tar.gz
echo 'Validation complete: /home/pi/beast-core-validation-v015.tar.gz'
echo 'Physical framebuffer was NOT touched by this validation.'
