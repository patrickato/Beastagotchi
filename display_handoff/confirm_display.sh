#!/usr/bin/env bash
set -euo pipefail
[[ ${EUID:-$(id -u)} -eq 0 ]] || { echo 'Run with sudo.'; exit 1; }
STATE_DIR=/var/lib/beastagotchi/display-handoff
/opt/beast-ui/bin/display_config.py --config /etc/pwnagotchi/config.toml require-disabled >/dev/null
systemctl is-active --quiet beast-ui.service || { echo 'beast-ui is not active; refusing to confirm.'; exit 2; }
systemctl stop beast-display-rollback.timer beast-display-rollback.service 2>/dev/null || true
systemctl reset-failed beast-display-rollback.service 2>/dev/null || true
rm -f /run/beastagotchi/ui-test-mode
mkdir -p "$STATE_DIR"; touch "$STATE_DIR/confirmed"
systemctl enable beast-ui.service beast-studio.service >/dev/null
systemctl start beast-studio.service
echo 'Beast display ownership CONFIRMED; beast-ui + Beast Studio enabled for boot.'
echo 'Rollback remains available at any time: sudo /opt/beast-ui/bin/release_display.sh'
