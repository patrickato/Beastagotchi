#!/usr/bin/env bash
set -euo pipefail
OUT=/tmp/beast-v093-validation
rm -rf "$OUT"; mkdir -p "$OUT"; chown pi:pi "$OUT"

echo '[1/8] core health/state'
curl -fsS http://127.0.0.1:8090/health > "$OUT/health.json"
curl -fsS 'http://127.0.0.1:8090/state?meta=0' > "$OUT/state.json"
curl -fsS 'http://127.0.0.1:8090/events?limit=100&transient=0' > "$OUT/events.json"

echo '[2/8] exact Jayofelony native frame source'
beast-pwn-native > "$OUT/native-frame-status.json" || true
cp -a /var/tmp/pwnagotchi/pwnagotchi.png "$OUT/pwnagotchi-native-source.png" 2>/dev/null || true

echo '[3/8] native profile renders'
for T in pwn_native_raw pwn_native_dark pwn_native_light pwn_native_chroma; do
  sudo -u pi PYTHONPATH=/opt/beast-ui /opt/.pwn/bin/python3 -m beastui --root /opt/beast-ui --theme "$T" --output "$OUT/theme-$T.png" --duration 0.20 >/dev/null 2>&1
  file "$OUT/theme-$T.png" >> "$OUT/native-render-files.txt"
done

echo '[4/8] all theme smoke renders'
for T in pwn_dark pwn_light pwn_chroma classic matrix starcore blackice hunter minimal; do
  sudo -u pi PYTHONPATH=/opt/beast-ui /opt/.pwn/bin/python3 -m beastui --root /opt/beast-ui --theme "$T" --output "$OUT/theme-$T.png" --duration 0.15 >/dev/null 2>&1
done

echo '[5/8] touch decision/status'
beast-touchcal status > "$OUT/touchcal-status.txt" 2>&1 || true
cp -a /opt/beast-ui/config/touch.json "$OUT/touch-active.json" 2>/dev/null || true

echo '[6/8] services/runtime'
{
  echo '== services =='; systemctl is-active pwnagotchi beast-core beast-ui gpsd 2>&1 || true
  echo '== pwnagotchi frame =='; stat /var/tmp/pwnagotchi/pwnagotchi.png 2>&1 || true
  echo '== pwn native tool =='; command -v beast-pwn-native || true
} > "$OUT/runtime.txt"

echo '[7/8] journals'
sudo journalctl -u beast-core --no-pager -n 160 > "$OUT/beast-core-journal.txt" 2>&1 || true
sudo journalctl -u pwnagotchi --no-pager -n 160 > "$OUT/pwnagotchi-journal.txt" 2>&1 || true

echo '[8/8] package'
tar -czf /home/pi/beast-core-validation-v093.tar.gz -C /tmp beast-v093-validation
chown pi:pi /home/pi/beast-core-validation-v093.tar.gz
echo 'Validation complete: /home/pi/beast-core-validation-v093.tar.gz'
echo 'Physical framebuffer was NOT touched by this validation.'
