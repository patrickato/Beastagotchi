#!/usr/bin/env bash
set -euo pipefail
[[ ${EUID:-$(id -u)} -eq 0 ]] || { echo 'Run with sudo.'; exit 1; }
CFG=/etc/pwnagotchi/config.toml
STATE_DIR=/var/lib/beastagotchi/display-handoff
BACKUP=$STATE_DIR/config.toml.pre-beast
PY=/opt/beast-ui/bin/display_config.py

systemctl stop beast-ui.service 2>/dev/null || true
systemctl stop beast-studio.service 2>/dev/null || true
systemctl disable beast-ui.service 2>/dev/null || true
systemctl stop beast-display-rollback.timer 2>/dev/null || true
rm -f /run/beastagotchi/ui-test-mode

if [[ -f "$BACKUP" ]]; then
  "$PY" --config "$CFG" restore --backup "$BACKUP"
  systemctl restart pwnagotchi.service
  rm -f "$STATE_DIR/confirmed"
  TS=$(date +%Y%m%d_%H%M%S)
  mv "$BACKUP" "$STATE_DIR/config.toml.restored.$TS"
  echo "Pwnagotchi display ownership restored. Backup preserved as config.toml.restored.$TS"
else
  echo 'No Beast display backup exists; Beast UI stopped and no config was restored.'
fi
