#!/usr/bin/env bash
set -euo pipefail
OUT=/tmp/beast-v092-validation
rm -rf "$OUT"; mkdir -p "$OUT"; chown pi:pi "$OUT"

echo '[1/7] core health/state/progression'
curl -fsS http://127.0.0.1:8090/health > "$OUT/health.json"
curl -fsS 'http://127.0.0.1:8090/state?meta=0' > "$OUT/state.json"
curl -fsS 'http://127.0.0.1:8090/events?limit=100&transient=0' > "$OUT/events.json"
curl -fsS 'http://127.0.0.1:8090/achievements' > "$OUT/achievements.json" || true
cp -a /var/lib/beastagotchi/profile.json "$OUT/profile.json" 2>/dev/null || true

echo '[2/7] off-screen render all nine themes'
for T in pwn_dark pwn_light pwn_chroma classic matrix starcore blackice hunter minimal; do
  sudo -u pi PYTHONPATH=/opt/beast-ui /opt/.pwn/bin/python3 -m beastui --root /opt/beast-ui --theme "$T" --output "$OUT/theme-$T.png" --duration 0.35 >/dev/null 2>&1
  file "$OUT/theme-$T.png" >> "$OUT/render-files.txt"
done

echo '[3/7] touch calibration candidate/status'
beast-touchcal status > "$OUT/touchcal-status.txt" 2>&1 || true
cp -a /opt/beast-ui/config/touch.json "$OUT/touch-active.json" 2>/dev/null || true
cp -a /opt/beast-ui/config/touch_recommended_v092.json "$OUT/touch-recommended-v092.json" 2>/dev/null || true
cp -a /var/lib/beastagotchi/touch-calibration/state.json "$OUT/touchcal-state.json" 2>/dev/null || true

echo '[4/7] classic identity render smoke'
sudo -u pi PYTHONPATH=/opt/beast-ui /opt/.pwn/bin/python3 - "$OUT" <<'PY'
import sys
from pathlib import Path
from beastui.engine import BeastUI
out=Path(sys.argv[1]);root='/opt/beast-ui'
state={'pwnagotchi.mood':'cool','health.core.state':'healthy','radio.primary.channel':6,'wifi.ap_count':17,'wifi.client_count':4,'pwnagotchi.handshakes':3,'system.temp.cpu_c':61.4,'context.mode.effective':'pwn','gps.fix':True,'progression.level':12,'progression.stage':'Scout','wifi.encounters.lifetime_unique':827}
for tid in ('pwn_dark','pwn_light','pwn_chroma'):
    ui=BeastUI(root=root,output=str(out/f'classic-{tid}.png'),theme_id=tid);ui.state=dict(state);ui.render()
PY

echo '[5/7] target runtime/dependency snapshot'
{
  echo '== python =='; python3 -V 2>&1 || true
  echo '== pwn python =='; /opt/.pwn/bin/python3 -V 2>&1 || true
  echo '== pillow =='; /opt/.pwn/bin/python3 - <<'PY'
import PIL
print(getattr(PIL,'__version__','unknown'))
PY
  echo '== touch tools =='; command -v beast-touchcal; command -v beast-touchlab
  echo '== docs =='; ls -l /usr/local/share/beastagotchi 2>&1 || true
} > "$OUT/runtime.txt"

echo '[6/7] hardware/plugin/dock snapshot'
{
  echo '== i2c =='; ls -l /dev/i2c-* 2>&1 || true
  echo '== usb =='; lsusb 2>&1 || true
  echo '== ethernet =='; ip addr show eth0 2>&1 || true
  echo '== route =='; ip route 2>&1 || true
  echo '== home dock profile =='; cat /etc/beastagotchi/home_dock.json 2>&1 || true
} > "$OUT/platform.txt"
sudo journalctl -u beast-core --no-pager -n 180 > "$OUT/beast-core-journal.txt"

echo '[7/7] package'
tar -czf /home/pi/beast-core-validation-v092.tar.gz -C /tmp beast-v092-validation
chown pi:pi /home/pi/beast-core-validation-v092.tar.gz
echo 'Validation complete: /home/pi/beast-core-validation-v092.tar.gz'
echo 'Physical framebuffer was NOT touched by this validation.'
