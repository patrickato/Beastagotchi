#!/usr/bin/env bash
set -euo pipefail
OUT=/tmp/beast-v082-validation
rm -rf "$OUT"; mkdir -p "$OUT"; chown pi:pi "$OUT"

echo '[1/6] core health/state/progression'
curl -fsS http://127.0.0.1:8090/health > "$OUT/health.json"
curl -fsS 'http://127.0.0.1:8090/state?meta=0' > "$OUT/state.json"
curl -fsS 'http://127.0.0.1:8090/events?limit=80&transient=0' > "$OUT/events.json"
curl -fsS 'http://127.0.0.1:8090/encounters?limit=12' > "$OUT/encounters.json"
cp -a /var/lib/beastagotchi/profile.json "$OUT/profile.json" 2>/dev/null || true

echo '[2/6] off-screen render all six themes'
for T in classic matrix starcore blackice hunter minimal; do
  rm -f /tmp/beast-ui-test-prefs.json
  sudo -u pi PYTHONPATH=/opt/beast-ui /opt/.pwn/bin/python3 -m beastui --root /opt/beast-ui --theme "$T" --output "$OUT/theme-$T.png" --duration 0.35 >/dev/null 2>&1
  file "$OUT/theme-$T.png" >> "$OUT/render-files.txt"
done

echo '[3/6] renderer smoke test'
sudo -u pi PYTHONPATH=/opt/beast-ui /opt/.pwn/bin/python3 - "$OUT" <<'PY'
import sys
from pathlib import Path
from beastui.engine import BeastUI
out=Path(sys.argv[1])
root='/opt/beast-ui'
state={
 'health.core.state':'healthy','radio.primary.channel':6,'radio.primary.band':'2.4GHz',
 'wifi.ap_count':8,'wifi.client_count':2,
 'wifi.aps':[{'hostname':'A','channel':1,'rssi':-45,'encryption':'WPA2'},
             {'hostname':'B','channel':6,'rssi':-55,'encryption':'WPA2'},
             {'hostname':'C','channel':11,'rssi':-65,'encryption':'WPA2'},
             {'hostname':'D','channel':36,'rssi':-60,'encryption':'WPA2'}],
 'system.temp.cpu_c':60.0,'system.cpu.total':20.0,'system.memory.used_pct':7.0,
 'context.mode.effective':'pwn','pwnagotchi.mood':'awake','pwnagotchi.handshakes':1,
 'progression.level':7,'progression.max_level':100,'progression.stage':'Cub','progression.xp':420,
 'progression.xp_next_level':80,'progression.level_progress_pct':62.5,'progression.aura':'spark',
 'progression.vendors.count':5,'progression.achievements.count':2,
 'wifi.encounters.lifetime_unique':37,'wifi.encounters.lifetime_vendors':5,
}
for mode in BeastUI.SPECTRUM_RENDERERS:
    ui=BeastUI(root=root,output=str(out/f'spectrum-{mode}.png'),theme_id='classic')
    ui.state=state; ui.page=3; ui.renderers['spectrum']=mode; ui.render()
PY

echo '[4/6] runtime/dependency snapshot'
{
  echo '== python =='; python3 -V 2>&1 || true
  echo '== pwn python =='; /opt/.pwn/bin/python3 -V 2>&1 || true
  echo '== pillow =='; /opt/.pwn/bin/python3 - <<'PY'
import PIL
print(getattr(PIL,'__version__','unknown'))
PY
  echo '== docs =='; ls -l /usr/local/share/beastagotchi 2>&1 || true
  echo '== beast-paths =='; command -v beast-paths 2>&1 || true
} > "$OUT/runtime.txt"

echo '[5/6] hardware/plugin/dock snapshot'
{
  echo '== i2c =='; ls -l /dev/i2c-* 2>&1 || true
  echo '== usb =='; lsusb 2>&1 || true
  echo '== ethernet =='; ip addr show eth0 2>&1 || true
  echo '== route =='; ip route 2>&1 || true
  echo '== home dock profile =='; cat /etc/beastagotchi/home_dock.json 2>&1 || true
} > "$OUT/platform.txt"
sudo journalctl -u beast-core --no-pager -n 160 > "$OUT/beast-core-journal.txt"

echo '[6/6] package'
tar -czf /home/pi/beast-core-validation-v082.tar.gz -C /tmp beast-v082-validation
chown pi:pi /home/pi/beast-core-validation-v082.tar.gz
echo 'Validation complete: /home/pi/beast-core-validation-v082.tar.gz'
echo 'Physical framebuffer was NOT touched by this validation.'
