#!/usr/bin/env bash
set -euo pipefail
[[ ${EUID:-$(id -u)} -eq 0 ]] || { echo 'Run with sudo.'; exit 1; }
MINUTES=${1:-10}
[[ "$MINUTES" =~ ^[0-9]+$ ]] || { echo 'Usage: sudo claim_display_test.sh [rollback-minutes]'; exit 2; }
CFG=/etc/pwnagotchi/config.toml
STATE_DIR=/var/lib/beastagotchi/display-handoff
BACKUP=$STATE_DIR/config.toml.pre-beast
PY=/opt/beast-ui/bin/display_config.py
mkdir -p "$STATE_DIR" /run/beastagotchi
rm -f /run/beastagotchi/touch-gestures.jsonl

rollback_now() {
  echo 'Physical handoff failed; restoring Pwnagotchi display...'
  /opt/beast-ui/bin/release_display.sh || true
}
trap 'echo "ERROR during display handoff"; rollback_now' ERR

systemctl stop beast-ui.service 2>/dev/null || true
systemctl disable beast-ui.service 2>/dev/null || true
systemctl stop beast-display-rollback.timer 2>/dev/null || true
systemctl reset-failed beast-display-rollback.service 2>/dev/null || true
rm -f "$STATE_DIR/confirmed"

if [[ -f "$BACKUP" ]]; then
  echo "Existing ACTIVE display backup found at $BACKUP; refusing to overwrite it."
  echo 'If a previous test is active, run: sudo /opt/beast-ui/bin/release_display.sh'
  exit 3
fi

# Refuse to start a second display owner on top of Beast. These plugins may
# remain installed/disabled; they simply cannot render concurrently.
if /opt/beast-ui/bin/display_conflicts.py --config "$CFG" >/tmp/beast-display-conflicts.txt 2>&1; then
  :
else
  echo 'Known Pwnagotchi display-owner plugin is enabled:'
  cat /tmp/beast-display-conflicts.txt
  echo
  echo 'Disable the conflicting plugin before Beast claims the TFT.'
  echo 'Example: sudo pwnagotchi plugins disable theme_manager'
  exit 6
fi

"$PY" --config "$CFG" require-enabled >/dev/null || {
  echo 'Pwnagotchi ui.display.enabled is not true and no active Beast rollback backup exists.'
  echo 'Refusing to guess display ownership.'
  exit 3
}

"$PY" --config "$CFG" disable --backup "$BACKUP"
"$PY" --config "$CFG" require-disabled >/dev/null

systemctl restart pwnagotchi.service
for _ in $(seq 1 40); do
  systemctl is-active --quiet pwnagotchi.service && break
  sleep 0.5
done
systemctl is-active --quiet pwnagotchi.service || { echo 'Pwnagotchi failed to restart.'; exit 4; }

# Give the engine enough time to reload plugins/bridge before Beast takes the LCD.
sleep 5
systemctl start beast-core.service
systemctl start beast-studio.service
mkdir -p /run/beastagotchi
touch /run/beastagotchi/ui-test-mode
systemctl start beast-ui.service
sleep 3
systemctl is-active --quiet beast-ui.service || { journalctl -u beast-ui.service -n 80 --no-pager; exit 5; }

systemd-run --quiet --unit=beast-display-rollback --on-active="${MINUTES}m" /opt/beast-ui/bin/auto_rollback.sh
trap - ERR

echo
echo 'BEAST UI PHYSICAL TEST IS ACTIVE.'
echo "Automatic rollback to Pwnagotchi display is scheduled in ${MINUTES} minute(s)."
echo 'Test: arrows, repeated LEFT/RIGHT swipes from middle pages, vertical drawer swipe, and long-press.'
echo 'Touches/gestures are shown temporarily on-screen in PHYS TEST mode.'
echo
echo 'If it looks/works correctly:  sudo /opt/beast-ui/bin/confirm_display.sh'
echo 'If anything is wrong:         sudo /opt/beast-ui/bin/release_display.sh'
echo 'Status:                       sudo /opt/beast-ui/bin/display_status.sh'
