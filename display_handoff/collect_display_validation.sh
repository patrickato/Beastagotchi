#!/usr/bin/env bash
set -euo pipefail
[[ ${EUID:-$(id -u)} -eq 0 ]] || { echo 'Run with sudo.'; exit 1; }
OUT=/tmp/beast-display-validation-v013
rm -rf "$OUT"; mkdir -p "$OUT"

/opt/beast-ui/bin/display_status.sh > "$OUT/status.txt" 2>&1 || true
journalctl -u beast-ui.service --no-pager -n 350 > "$OUT/beast-ui-journal.txt" 2>&1 || true
journalctl -u beast-core.service --no-pager -n 220 > "$OUT/beast-core-journal.txt" 2>&1 || true
journalctl -u pwnagotchi.service --no-pager -n 120 > "$OUT/pwnagotchi-journal.txt" 2>&1 || true
curl -s http://127.0.0.1:8090/health > "$OUT/core-health.json" || true
curl -s 'http://127.0.0.1:8090/state?meta=0' > "$OUT/state.json" || true
curl -s 'http://127.0.0.1:8090/events?limit=120&transient=0' > "$OUT/events.json" || true
curl -s 'http://127.0.0.1:8090/encounters?limit=20' > "$OUT/encounters.json" || true
curl -s 'http://127.0.0.1:8090/beastdex?limit=30' > "$OUT/beastdex.json" || true
curl -s 'http://127.0.0.1:8090/capture-vault?limit=30' > "$OUT/capture-vault.json" || true
curl -s 'http://127.0.0.1:8090/telemetry' > "$OUT/telemetry.json" || true
curl -s 'http://127.0.0.1:8090/plugins' > "$OUT/plugins.json" || true
curl -s 'http://127.0.0.1:8090/actions?limit=40' > "$OUT/actions.json" || true
curl -s 'http://127.0.0.1:8090/expeditions?limit=20' > "$OUT/expeditions.json" || true
curl -s 'http://127.0.0.1:8090/expedition?point_limit=500' > "$OUT/expedition-current.json" || true
beast-pwn-native > "$OUT/native-frame-status.json" 2>&1 || true
cp -a /var/tmp/pwnagotchi/pwnagotchi.png "$OUT/pwnagotchi-native-source.png" 2>/dev/null || true
/opt/.pwn/bin/python3 /opt/beast-ui/bin/capture_fb.py /dev/fb1 "$OUT/framebuffer.png" || true
cp -a /opt/beast-ui/config/touch.json "$OUT/touch.json" 2>/dev/null || true
cp -a /opt/beast-ui/config/touch_experimental_rejected_v092.json "$OUT/touch-experimental-rejected-v092.json" 2>/dev/null || true
cp -a /var/lib/beastagotchi/touch-calibration/state.json "$OUT/touchcal-state.json" 2>/dev/null || true
cp -a /var/lib/beastagotchi/touch-calibration/pre-v092-touch.json "$OUT/touch-pre-v092-backup.json" 2>/dev/null || true
cp -a /run/beastagotchi/touch-gestures.jsonl "$OUT/touch-gestures.jsonl" 2>/dev/null || true
cp -a /var/lib/beastagotchi/display-handoff/confirmed "$OUT/confirmed" 2>/dev/null || true
cp -a /var/lib/beastagotchi/ui/preferences.json "$OUT/ui-preferences.json" 2>/dev/null || true
stat -c 'socket=%n mode=%a uid=%u gid=%g' /run/beastagotchi/action.sock > "$OUT/action-socket.txt" 2>&1 || true
if [[ -s /var/lib/beastagotchi/ui/studio.token ]]; then
  TOKEN="$(cat /var/lib/beastagotchi/ui/studio.token)"
  curl -s -H "X-Beast-Studio-Token: $TOKEN" http://127.0.0.1:8091/api/schema > "$OUT/studio-schema.json" || true
  curl -s -H "X-Beast-Studio-Token: $TOKEN" http://127.0.0.1:8091/api/preferences > "$OUT/studio-preferences.json" || true
fi
cp -a /run/beastagotchi/ui-runtime.json "$OUT/ui-runtime.json" 2>/dev/null || true
cp -a /var/lib/beastagotchi/profile.json "$OUT/profile.json" 2>/dev/null || true
cp -a /var/lib/beastagotchi/secrets/rare_history.json "$OUT/rare-history.json" 2>/dev/null || true
cp -a /etc/beastagotchi/home_dock.json "$OUT/home-dock-profile.json" 2>/dev/null || true

{
  echo '== i2c devices =='; ls -l /dev/i2c-* 2>&1 || true
  echo '== usb =='; lsusb 2>&1 || true
  echo '== ethernet =='; ip addr show eth0 2>&1 || true
  echo '== routes =='; ip route 2>&1 || true
  echo '== services =='; systemctl is-active beast-core beast-ui beast-studio pwnagotchi gpsd 2>&1 || true
} > "$OUT/hardware.txt"

if [[ -f "$OUT/touch-gestures.jsonl" ]]; then
  /opt/.pwn/bin/python3 - "$OUT/touch-gestures.jsonl" > "$OUT/touch-summary.txt" <<'PY'
import json,sys,collections
p=sys.argv[1]
rows=[]
for line in open(p,errors='replace'):
    try: rows.append(json.loads(line))
    except Exception: pass
print('gestures',len(rows))
c=collections.Counter(r.get('kind') for r in rows)
print('kinds',dict(c))
for i,r in enumerate(rows[-60:],1):
    q=r.get('payload') or {}
    print(f"{i:02d} {r.get('kind'):10} axis={q.get('axis','-')} dir={q.get('direction','-'):5} dx={q.get('dx','-')} dy={q.get('dy','-')} trend=({q.get('trend_dx','-')},{q.get('trend_dy','-')}) samples={q.get('samples','-')} duration={q.get('duration','-')}")
PY
fi

TAR=/home/pi/beast-display-validation-v013.tar.gz
tar -czf "$TAR" -C /tmp "$(basename "$OUT")"
chown pi:pi "$TAR"
echo "Validation complete: $TAR"
