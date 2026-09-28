#!/usr/bin/env bash
set -euo pipefail
[[ ${EUID:-$(id -u)} -eq 0 ]] || { echo 'Run with sudo.'; exit 1; }
CFG=/etc/pwnagotchi/config.toml
STATE_DIR=/var/lib/beastagotchi/display-handoff
BACKUP=$STATE_DIR/config.toml.pre-beast
PY=/opt/beast-ui/bin/display_config.py
OVERRIDE_DIR=/run/systemd/system/beast-ui.service.d
EXPERIENCE_OVERRIDE=$OVERRIDE_DIR/90-beast-experience-test.conf
WATCHDOG_UNIT=beast-display-watchdog.service

# Stop the independent acceptance watchdog before intentionally stopping the UI.
# When the watchdog itself invokes rollback, it must not stop/wait on itself.
if [[ ${BEAST_DISPLAY_WATCHDOG:-0} != 1 ]]; then
  systemctl stop "$WATCHDOG_UNIT" 2>/dev/null || true
  systemctl reset-failed "$WATCHDOG_UNIT" 2>/dev/null || true
fi

systemctl stop beast-ui.service 2>/dev/null || true
systemctl stop beast-studio.service 2>/dev/null || true
systemctl disable beast-ui.service 2>/dev/null || true
systemctl stop beast-display-rollback.timer 2>/dev/null || true
rm -f /run/beastagotchi/ui-test-mode

# Staging selection is always temporary. Clear it before any future Beast start,
# even when there is no display-config backup left to restore.
if [[ -f "$EXPERIENCE_OVERRIDE" ]]; then
  rm -f "$EXPERIENCE_OVERRIDE"
  rmdir "$OVERRIDE_DIR" 2>/dev/null || true
  systemctl daemon-reload 2>/dev/null || true
fi

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
