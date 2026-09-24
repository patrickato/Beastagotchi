#!/usr/bin/env bash
set -euo pipefail
SRC="$(cd "$(dirname "$0")" && pwd)"
[[ ${EUID:-$(id -u)} -eq 0 ]] || { echo 'Run with sudo: sudo ./install_ui.sh'; exit 1; }
getent group beastagotchi >/dev/null 2>&1 || groupadd --system beastagotchi
[[ -x /opt/.pwn/bin/python3 ]] || { echo 'ERROR: /opt/.pwn/bin/python3 not found'; exit 1; }
/opt/.pwn/bin/python3 - <<'PY'
import PIL
print('Pillow OK', getattr(PIL,'__version__','?'))
PY
systemctl stop beast-ui.service beast-studio.service 2>/dev/null || true
install -d -m 0755 /opt/beast-ui /opt/beast-ui/themes /opt/beast-ui/config /opt/beast-ui/bin /var/lib/beastagotchi/display-handoff
install -d -o pi -g pi -m 0755 /var/lib/beastagotchi/ui
install -d -o pi -g beastagotchi -m 0750 /var/lib/beastagotchi/library /var/lib/beastagotchi/library/imports
rm -rf /opt/beast-ui/beastui /opt/beast-ui/beaststudio
cp -a "$SRC/beastui" /opt/beast-ui/
cp -a "$SRC/beaststudio" /opt/beast-ui/
cp -a "$SRC/beastui/themes/." /opt/beast-ui/themes/
for f in "$SRC"/tools/display_config.py "$SRC"/tools/display_conflicts.py "$SRC"/tools/capture_fb.py "$SRC"/display_handoff/*.sh; do
  install -m 0755 "$f" "/opt/beast-ui/bin/$(basename "$f")"
done
# Preserve an already-active Beast calibration across upgrades. Only import the
# legacy calibration the first time Beast UI is installed.
if [[ -f /opt/beast-ui/config/touch.json ]]; then
  echo 'Preserving existing Beast touch calibration.'
elif [[ -f /opt/beastagotchi-v1.2/config/touch.json ]]; then
  cp -a /opt/beastagotchi-v1.2/config/touch.json /opt/beast-ui/config/touch.json
elif [[ -f /opt/beastagotchi-v1/config/touch.json ]]; then
  cp -a /opt/beastagotchi-v1/config/touch.json /opt/beast-ui/config/touch.json
elif [[ -f /opt/beastagotchi/config/touch.json ]]; then
  cp -a /opt/beastagotchi/config/touch.json /opt/beast-ui/config/touch.json
else
  echo 'ERROR: no calibrated touch.json found'; exit 1
fi
install -m 0644 "$SRC/config/touch_experimental_rejected_v092.json" /opt/beast-ui/config/touch_experimental_rejected_v092.json
install -m 0755 "$SRC/tools/rare_preview.py" /usr/local/bin/beast-rare-preview
install -m 0755 "$SRC/tools/touch_lab.py" /opt/beast-ui/bin/touch_lab.py
install -m 0755 "$SRC/tools/beast_touchlab.sh" /usr/local/bin/beast-touchlab
install -m 0755 "$SRC/tools/touch_calibration.py" /usr/local/bin/beast-touchcal
install -m 0755 "$SRC/tools/pwn_native_status.py" /usr/local/bin/beast-pwn-native
install -m 0755 "$SRC/tools/beast_studio_token.py" /usr/local/bin/beast-studio-token
install -m 0755 "$SRC/tools/v019_acceptance_report.py" /opt/beast-ui/bin/v019_acceptance_report.py
install -m 0755 "$SRC/tools/v019_physical_acceptance.sh" /usr/local/bin/beast-v019-accept
install -m 0644 "$SRC/ui_systemd/beast-ui.service" /etc/systemd/system/beast-ui.service
install -m 0644 "$SRC/ui_systemd/beast-studio.service" /etc/systemd/system/beast-studio.service
systemctl daemon-reload
systemctl stop beast-ui.service 2>/dev/null || true
systemctl disable beast-ui.service 2>/dev/null || true
cat <<'EOF'
Beast UI v0.18.1 Platform / Compatibility milestone installed but NOT started.
Physical display ownership is protected: beast-ui refuses to start while Pwnagotchi ui.display.enabled=true.

Off-screen test:
  sudo -u pi PYTHONPATH=/opt/beast-ui /opt/.pwn/bin/python3 -m beastui --root /opt/beast-ui --output /tmp/beast-ui-v017.png --duration 2

Reversible physical handoff test:
  sudo /opt/beast-ui/bin/claim_display_test.sh 15
EOF
