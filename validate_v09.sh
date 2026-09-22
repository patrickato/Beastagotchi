#!/usr/bin/env bash
set -euo pipefail
OUT=/tmp/beast-v09-validation
rm -rf "$OUT"; mkdir -p "$OUT"; chown pi:pi "$OUT"

echo '[1/6] core health/state/progression/ambient/rare'
curl -fsS http://127.0.0.1:8090/health > "$OUT/health.json"
curl -fsS 'http://127.0.0.1:8090/state?meta=0' > "$OUT/state.json"
curl -fsS 'http://127.0.0.1:8090/events?limit=100&transient=0' > "$OUT/events.json"
curl -fsS 'http://127.0.0.1:8090/encounters?limit=12' > "$OUT/encounters.json"
curl -fsS 'http://127.0.0.1:8090/achievements' > "$OUT/achievements.json"
cp -a /var/lib/beastagotchi/profile.json "$OUT/profile.json" 2>/dev/null || true
cp -a /var/lib/beastagotchi/secrets/rare_history.json "$OUT/rare-history.json" 2>/dev/null || true

echo '[2/6] off-screen render all six themes'
for T in classic matrix starcore blackice hunter minimal; do
  sudo -u pi PYTHONPATH=/opt/beast-ui /opt/.pwn/bin/python3 -m beastui --root /opt/beast-ui --theme "$T" --output "$OUT/theme-$T.png" --duration 0.35 >/dev/null 2>&1
  file "$OUT/theme-$T.png" >> "$OUT/render-files.txt"
done

echo '[3/6] Matrix customization + overlay render smoke'
sudo -u pi PYTHONPATH=/opt/beast-ui /opt/.pwn/bin/python3 - "$OUT" <<'PY'
import sys
from pathlib import Path
from beastui.engine import BeastUI
out=Path(sys.argv[1]);root='/opt/beast-ui'
state={'health.core.state':'healthy','radio.primary.channel':6,'wifi.ap_count':20,'system.cpu.total':20,'system.memory.used_pct':8,'system.temp.cpu_c':58,'context.mode.effective':'pwn','progression.level':12,'progression.max_level':100,'progression.stage':'Scout','progression.xp':900,'progression.xp_next_level':120,'progression.level_progress_pct':63,'progression.aura':'spark','progression.achievements.count':3,'progression.achievements.catalog_count':40,'progression.achievements.unlocked':[{'id':'first_signal','label':'First Signal','rarity':'common'}]}
for layer in ('background','mixed'):
  for palette in ('green','cyan','rainbow','holiday'):
    ui=BeastUI(root=root,output=str(out/f'matrix-{layer}-{palette}.png'),theme_id='matrix');ui.state=dict(state);ui.theme_options['matrix']={'layer_mode':layer,'density':'dense','speed_mode':'fast','palette_mode':palette};ui.render()
ui=BeastUI(root=root,output=str(out/'rare-moment.png'),theme_id='classic');ui.state=dict(state,**{'rare.moment.active':True,'rare.moment.id':'preview','rare.moment.rarity':'legendary','rare.moment.sigil':'eye'});ui.render()
ui=BeastUI(root=root,output=str(out/'achievements-overlay.png'),theme_id='classic');ui.state=state;ui.achievements_overlay=True;ui.render()
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
sudo journalctl -u beast-core --no-pager -n 180 > "$OUT/beast-core-journal.txt"

echo '[6/6] package'
tar -czf /home/pi/beast-core-validation-v09.tar.gz -C /tmp beast-v09-validation
chown pi:pi /home/pi/beast-core-validation-v09.tar.gz
echo 'Validation complete: /home/pi/beast-core-validation-v09.tar.gz'
echo 'Physical framebuffer was NOT touched by this validation.'
