#!/usr/bin/env bash
set -euo pipefail
SRC="$(cd "$(dirname "$0")" && pwd)"
OUT=/tmp/beast-v018-validation
rm -rf "$OUT"; mkdir -p "$OUT"; chown pi:pi "$OUT"
STUDIO_WAS_ACTIVE=0
systemctl is-active --quiet beast-studio.service && STUDIO_WAS_ACTIVE=1 || true
cleanup(){ if [[ "$STUDIO_WAS_ACTIVE" -eq 0 ]]; then systemctl stop beast-studio.service 2>/dev/null || true; fi; }
fail_bundle(){
  systemctl status beast-core.service beast-studio.service pwnagotchi.service --no-pager -l > "$OUT/failure-services.txt" 2>&1 || true
  journalctl -u beast-core.service -u beast-studio.service -u pwnagotchi.service --no-pager -n 220 > "$OUT/failure-journal.txt" 2>&1 || true
  tar -czf /home/pi/beast-core-validation-v018-failed.tar.gz -C /tmp beast-v018-validation
  chown pi:pi /home/pi/beast-core-validation-v018-failed.tar.gz
  echo 'Failure bundle: /home/pi/beast-core-validation-v018-failed.tar.gz'
}
trap 'rc=$?; if [[ $rc -ne 0 ]]; then fail_bundle; fi; cleanup; exit $rc' EXIT

echo '[1/20] semantic Core readiness / protected engine'
for _ in $(seq 1 90); do
  [[ "$(systemctl is-active pwnagotchi 2>/dev/null || true)" == active ]] || { sleep 1; continue; }
  [[ "$(systemctl is-active bettercap 2>/dev/null || true)" == active ]] || { sleep 1; continue; }
  if curl -fsS --max-time 2 'http://127.0.0.1:8090/state?meta=0' > "$OUT/state-ready.json" 2>/dev/null; then
    if python3 - <<'PY'
import json
s=json.load(open('/tmp/beast-v018-validation/state-ready.json'))
ready=bool(s.get('health.core.ready'))
starting=s.get('health.core.starting_collectors') or []
plugins=s.get('plugins.catalog_count')
raise SystemExit(0 if ready and not starting and plugins is not None else 1)
PY
    then break; fi
  fi
  sleep 1
done
python3 - <<'PY'
import json
s=json.load(open('/tmp/beast-v018-validation/state-ready.json'))
assert s.get('health.core.ready') is True,s.get('health.core.state')
assert not (s.get('health.core.starting_collectors') or []),s.get('health.core.starting_collectors')
assert s.get('plugins.catalog_count') is not None
PY
curl -fsS http://127.0.0.1:8090/health > "$OUT/health.json"
python3 - <<'PY'
import json
h=json.load(open('/tmp/beast-v018-validation/health.json'))
assert h.get('state') in {'healthy','degraded'},h
PY

echo '[2/20] live platform / knowledge / Operator catalogs'
curl -fsS 'http://127.0.0.1:8090/state?meta=0' > "$OUT/state.json"
curl -fsS 'http://127.0.0.1:8090/events?limit=200&transient=0' > "$OUT/events.json"
curl -fsS 'http://127.0.0.1:8090/telemetry' > "$OUT/telemetry.json"
curl -fsS 'http://127.0.0.1:8090/platform-bundle' > "$OUT/platform-bundle.json"
curl -fsS 'http://127.0.0.1:8090/library?limit=50' > "$OUT/library.json"
curl -fsS 'http://127.0.0.1:8090/incidents?limit=40' > "$OUT/incidents.json"
curl -fsS 'http://127.0.0.1:8090/jobs?limit=40' > "$OUT/jobs.json"
curl -fsS 'http://127.0.0.1:8090/operator-policy' > "$OUT/operator-policy.json"
curl -fsS 'http://127.0.0.1:8090/operator-tools' > "$OUT/operator-tools.json"
curl -fsS 'http://127.0.0.1:8090/search?q=system' > "$OUT/search-system.json"
curl -fsS 'http://127.0.0.1:8090/plugins' > "$OUT/plugins.json"
curl -fsS 'http://127.0.0.1:8090/actions?limit=50' > "$OUT/actions.json"
curl -fsS 'http://127.0.0.1:8090/beastdex?limit=30' > "$OUT/beastdex.json"
curl -fsS 'http://127.0.0.1:8090/capture-vault?limit=30' > "$OUT/capture-vault.json"
curl -fsS 'http://127.0.0.1:8090/expeditions?limit=20' > "$OUT/expeditions.json"
curl -fsS 'http://127.0.0.1:8090/expedition?point_limit=500' > "$OUT/expedition-current.json" || true

echo '[3/20] bridge/native/touch/display-conflict invariants'
beast-pwn-native > "$OUT/native-frame-status.json" || true
cp -a /var/tmp/pwnagotchi/pwnagotchi.png "$OUT/pwnagotchi-native-source.png" 2>/dev/null || true
beast-touchcal status > "$OUT/touchcal-status.txt" 2>&1 || true
cp -a /opt/beast-ui/config/touch.json "$OUT/touch-active.json" 2>/dev/null || true
ls -lah /run/beastagotchi/pwnagotchi_bridge.json > "$OUT/bridge-file.txt" 2>&1 || true
/opt/beast-ui/bin/display_conflicts.py > "$OUT/display-conflicts.txt" 2>&1 || true

echo '[4/20] installed compile/import/version gate'
/opt/.pwn/bin/python3 -m compileall -q /opt/beast-ui/beastui /opt/beast-ui/beaststudio /opt/beast-core/beastcore
PYTHONPATH=/opt/beast-core:/opt/beast-ui /opt/.pwn/bin/python3 - <<'PY' > "$OUT/import-gate.txt"
import beastcore,beastui,beaststudio
print('beastcore',beastcore.__version__);print('beastui',beastui.__version__);print('beaststudio',beaststudio.__version__)
assert beastcore.__version__=='0.18.1';assert beastui.__version__=='0.18.1';assert beaststudio.__version__=='0.18.1'
PY

echo '[5/20] local privileged channel invariants'
{ stat -c 'socket=%n mode=%a uid=%u gid=%g' /run/beastagotchi/action.sock; id pi; grep -n '^SupplementaryGroups=' /etc/systemd/system/beast-studio.service /etc/systemd/system/beast-ui.service || true; } > "$OUT/action-channel.txt"
test -S /run/beastagotchi/action.sock

echo '[6/20] safe action plans / Operator boundary (no mutation)'
sudo -u pi -g beastagotchi PYTHONPATH=/opt/beast-ui /opt/.pwn/bin/python3 - <<'PY' > "$OUT/action-plans.txt"
from beaststudio.action_client import BeastActionClient
c=BeastActionClient()
for action,payload in [('plugin.toggle',{'name':'beast_bridge','enabled':False}),('service.restart',{'unit':'pwnagotchi.service'}),('backup.create',{}),('support.bundle',{})]:
 r=c.plan(action,payload);print(action,r);assert r.get('ok') is True
assert c.plan('plugin.toggle',{'name':'beast_bridge','enabled':False})['plan']['allowed'] is False
assert c.plan('service.restart',{'unit':'pwnagotchi.service'})['plan']['allowed'] is True
assert c.plan('backup.create',{})['plan']['allowed'] is True
assert c.plan('support.bundle',{})['plan']['allowed'] is True
PY
python3 - <<'PY' > "$OUT/operator-boundary.txt"
import json
x=json.load(open('/tmp/beast-v018-validation/operator-tools.json'))
assert x.get('generic_shell') is False
names={r.get('name') for r in x.get('items',[])}
assert {'state.get','search.query','library.search','action.plan','service.restart','backup.create','support.bundle','plugin.toggle','container.control'} <= names
print(json.dumps(x,indent=2))
PY

echo '[7/20] Beast Studio paired API readiness'
systemctl reset-failed beast-studio.service 2>/dev/null || true
systemctl start beast-studio.service
STUDIO_READY=0
for _ in $(seq 1 80); do
  if systemctl is-active --quiet beast-studio.service && [[ -s /var/lib/beastagotchi/ui/studio.token ]]; then
    TOKEN="$(cat /var/lib/beastagotchi/ui/studio.token)"
    if curl -fsS --max-time 2 -H "X-Beast-Studio-Token: $TOKEN" http://127.0.0.1:8091/api/schema > "$OUT/studio-schema.json" 2>/dev/null; then STUDIO_READY=1; break; fi
  fi
  sleep .5
done
[[ "$STUDIO_READY" -eq 1 ]]
curl -fsS --max-time 5 -H "X-Beast-Studio-Token: $TOKEN" http://127.0.0.1:8091/api/preferences > "$OUT/studio-preferences.json"
curl -fsS --max-time 5 -H "X-Beast-Studio-Token: $TOKEN" http://127.0.0.1:8091/api/platform > "$OUT/studio-platform.json"
curl -fsS --max-time 5 -H "X-Beast-Studio-Token: $TOKEN" 'http://127.0.0.1:8091/api/search?q=system' > "$OUT/studio-search.json"

echo '[8/20] Field Library extractor/search capability'
python3 - <<'PY' > "$OUT/field-library-capability.txt"
import json
s=json.load(open('/tmp/beast-v018-validation/state.json'))
for k in ('library.state','library.document_count','library.text_indexed_count','library.search_engine','library.extractors','library.extract_failures'):
 print(k,'=',s.get(k))
PY

echo '[9/20] recovery backup inspection (read-only if backup exists)'
python3 - <<'PY' > "$OUT/backup-inspection.txt"
import json,urllib.parse,urllib.request
s=json.load(open('/tmp/beast-v018-validation/state.json'));items=s.get('backups.items') or []
if not items:
 print('no Beast recovery backup exists; inspection skipped without creating one')
else:
 name=str(items[0].get('name') or '')
 with urllib.request.urlopen('http://127.0.0.1:8090/backup-inspect?'+urllib.parse.urlencode({'name':name}),timeout=5) as r:x=json.load(r)
 print(json.dumps(x,indent=2));assert x.get('ok') is True;assert x.get('restore_applied') is False
PY

echo '[10/20] all-theme 480x320 off-screen smoke renders'
for T in pwn_native_raw pwn_native_dark pwn_native_light pwn_native_chroma pwn_dark pwn_light pwn_chroma classic matrix starcore blackice hunter minimal synthwave amber_tactical ghost_minimal cyberpunk wopr_norad lcars retro_crt; do
  sudo -u pi PYTHONPATH=/opt/beast-ui /opt/.pwn/bin/python3 -m beastui --root /opt/beast-ui --theme "$T" --output "$OUT/theme-$T.png" --duration 0.08 >/dev/null 2>&1
done

echo '[11/20] v0.18 validation gallery + compatibility proofs'
sudo -u pi PYTHONPATH=/opt/beast-ui /opt/.pwn/bin/python3 "$SRC/tools/render_v018_validation.py" --root /opt/beast-ui --state "$OUT/state.json" --events "$OUT/events.json" --out "$OUT/previews"

echo '[12/20] gallery dimensions / nonblank / compatibility gate'
/opt/.pwn/bin/python3 - <<'PY' > "$OUT/gallery-gate.txt"
from pathlib import Path
from PIL import Image,ImageStat
root=Path('/tmp/beast-v018-validation/previews');rows=[]
for p in sorted(root.glob('*.png')):
 im=Image.open(p).convert('RGB');ext=ImageStat.Stat(im).extrema
 expected=(640,480) if p.name=='compat-640x480.png' else (800,480) if p.name=='compat-800x480.png' else (480,320)
 assert im.size==expected,(p,im.size,expected);assert any(lo!=hi for lo,hi in ext),f'blank {p}';rows.append((p.name,im.size))
print('valid',len(rows));print('\n'.join(f'{n} {s}' for n,s in rows));assert len(rows)>=32
PY

echo '[13/20] app/capability registry'
PYTHONPATH=/opt/beast-ui /opt/.pwn/bin/python3 - <<'PY' > "$OUT/ui-registry.json"
import json
from beastui.apps import AppRegistry,OPTIONAL_APPS
from beastui.pages import Pages
from beastui.customization import DEFAULT_CONTEXT_DECKS,WIDGET_STYLES,MAX_DASHBOARD_WIDGETS
x={'main_pages':Pages.IDS,'apps':[a.id for a in AppRegistry().all()],'optional_apps':list(OPTIONAL_APPS),'decks':DEFAULT_CONTEXT_DECKS,'widget_styles':WIDGET_STYLES,'max_dashboard_widgets':MAX_DASHBOARD_WIDGETS};print(json.dumps(x,indent=2))
assert {'operations','topology','tasks','field_library','incidents','backups'} <= set(x['apps']);assert {'containers','ai_operator','command_center'} <= set(OPTIONAL_APPS)
PY

echo '[14/20] optional capability snapshot'
python3 - <<'PY' > "$OUT/capability-status.txt"
import json
s=json.load(open('/tmp/beast-v018-validation/state.json'))
for k in ('bluetooth.available','bluetooth.adapter.present','containers.runtime.available','ai.local.available','desktop.runtime.available','desktop.browser.available','display.connected_outputs','display.external_connected','system.arm_clock_mhz','system.gpu_mem_mb','network.route.available','network.internet.state'):
 print(k,'=',s.get(k))
PY

echo '[15/20] v0.18 personality / mission / Operator-session state'
python3 - <<'PY2' > "$OUT/v018-state.txt"
import json
s=json.load(open('/tmp/beast-v018-validation/state.json'))
for k in ('beast.mood','beast.expression','beast.energy','beast.curiosity','beast.focus','beast.personality.source','missions.count','missions.available_count','operator.policy.level','operator.session'):
 print(k,'=',s.get(k))
assert s.get('beast.personality.source')=='derived_live'
assert int(s.get('missions.count') or 0)>=4
assert str(s.get('operator.policy.level') or 'observer')=='observer'
PY2

echo '[16/20] v0.18 native-responsive Board proof'
sudo -u pi PYTHONPATH=/opt/beast-ui /opt/.pwn/bin/python3 - <<'PY2' > "$OUT/responsive-board.txt"
from pathlib import Path
from PIL import Image
from beastui.theme import load_theme
from beastui.responsive import render_responsive_board
th=load_theme(Path('/opt/beast-ui/themes/classic.json'))
widgets=[{'id':'cpu','key':'system.cpu.total','label':'CPU','x':0,'y':0,'w':6,'h':4,'z':0,'visible':True}]
im=render_responsive_board((800,480),th,{'system.cpu.total':42.0},widgets,'FIELD OPS')
im.save('/tmp/beast-v018-validation/responsive-board-800x480.png')
assert im.size==(800,480)
print('native responsive board',im.size)
PY2

echo '[17/20] package unit regression'
if command -v pytest >/dev/null 2>&1; then (cd "$SRC" && PYTHONPATH=. pytest -q) > "$OUT/pytest.txt"; else echo 'pytest not installed on target; clean-package source gate is authoritative' > "$OUT/pytest.txt"; fi

echo '[18/20] service/runtime/performance evidence'
{ echo '== services =='; systemctl is-active pwnagotchi bettercap beast-core beast-ui beast-studio gpsd 2>&1 || true; echo '== core health =='; cat "$OUT/health.json"; echo '== selected =='; python3 - <<'PY'
import json
s=json.load(open('/tmp/beast-v018-validation/state.json'))
for k in ('system.temp.cpu_c','system.cpu.total','governor.mode','governor.reason','health.core.state','health.core.ready','health.core.critical_failures','performance.beast.cpu_pct','performance.ui.avg_render_ms','performance.fb.write_ratio_pct'):
 print(k,'=',s.get(k))
PY
} > "$OUT/runtime.txt"
cp -a /run/beastagotchi/ui-runtime.json "$OUT/ui-runtime.json" 2>/dev/null || true
cp -a /var/lib/beastagotchi/ui/preferences.json "$OUT/ui-preferences.json" 2>/dev/null || true

echo '[19/20] journals / support evidence'
sudo journalctl -u beast-core --no-pager -n 240 > "$OUT/beast-core-journal.txt" 2>&1 || true
sudo journalctl -u beast-ui --no-pager -n 180 > "$OUT/beast-ui-journal.txt" 2>&1 || true
sudo journalctl -u beast-studio --no-pager -n 180 > "$OUT/beast-studio-journal.txt" 2>&1 || true
sudo journalctl -u pwnagotchi --no-pager -n 160 > "$OUT/pwnagotchi-journal.txt" 2>&1 || true

echo '[20/20] package validation archive'
tar -czf /home/pi/beast-core-validation-v018.tar.gz -C /tmp beast-v018-validation
chown pi:pi /home/pi/beast-core-validation-v018.tar.gz
echo 'Validation complete: /home/pi/beast-core-validation-v018.tar.gz'
echo 'Physical framebuffer was NOT touched by this validation.'
