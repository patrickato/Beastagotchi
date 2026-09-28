#!/usr/bin/env bash
set -euo pipefail
[[ ${EUID:-$(id -u)} -eq 0 ]] || { echo 'Run with sudo.'; exit 1; }
STATE_DIR=/var/lib/beastagotchi/display-handoff
OVERRIDE_DIR=/run/systemd/system/beast-ui.service.d
EXPERIENCE_OVERRIDE=$OVERRIDE_DIR/90-beast-experience-test.conf
WATCHDOG_UNIT=beast-display-watchdog.service
/opt/beast-ui/bin/display_config.py --config /etc/pwnagotchi/config.toml require-disabled >/dev/null
systemctl is-active --quiet beast-ui.service || { echo 'beast-ui is not active; refusing to confirm.'; exit 2; }

# Confirmation approves Beast display ownership, not a staging Experience as a
# persistent boot preference. Remove the runtime override first. The currently
# running staging renderer may remain visible until Beast UI next restarts.
if [[ -f "$EXPERIENCE_OVERRIDE" ]]; then
  rm -f "$EXPERIENCE_OVERRIDE"
  rmdir "$OVERRIDE_DIR" 2>/dev/null || true
  systemctl daemon-reload
fi

systemctl stop "$WATCHDOG_UNIT" 2>/dev/null || true
systemctl reset-failed "$WATCHDOG_UNIT" 2>/dev/null || true
systemctl stop beast-display-rollback.timer beast-display-rollback.service 2>/dev/null || true
systemctl reset-failed beast-display-rollback.service 2>/dev/null || true
rm -f /run/beastagotchi/ui-test-mode
mkdir -p "$STATE_DIR"; touch "$STATE_DIR/confirmed"
systemctl enable beast-ui.service beast-studio.service >/dev/null
systemctl start beast-studio.service
echo 'Beast display ownership CONFIRMED; beast-ui + Beast Studio enabled for boot.'
echo 'Any staging Experience selection was cleared; saved/default UI remains authoritative on the next Beast UI start.'
echo 'Rollback remains available at any time: sudo /opt/beast-ui/bin/release_display.sh'
