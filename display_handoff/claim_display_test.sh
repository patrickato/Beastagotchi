#!/usr/bin/env bash
set -euo pipefail
[[ ${EUID:-$(id -u)} -eq 0 ]] || { echo 'Run with sudo.'; exit 1; }
MINUTES=${1:-10}
EXPERIENCE=${2:-${BEAST_ACCEPT_EXPERIENCE:-}}
EXPERIENCE_PAGE=${3:-${BEAST_ACCEPT_EXPERIENCE_PAGE:-home}}
[[ "$MINUTES" =~ ^[0-9]+$ ]] || { echo 'Usage: sudo claim_display_test.sh [rollback-minutes] [experience] [experience-page]'; exit 2; }
CFG=/etc/pwnagotchi/config.toml
STATE_DIR=/var/lib/beastagotchi/display-handoff
BACKUP=$STATE_DIR/config.toml.pre-beast
PY=/opt/beast-ui/bin/display_config.py
UI_PY=/opt/.pwn/bin/python3
OVERRIDE_DIR=/run/systemd/system/beast-ui.service.d
EXPERIENCE_OVERRIDE=$OVERRIDE_DIR/90-beast-experience-test.conf
WATCHDOG_UNIT=beast-display-watchdog.service
RUNTIME=/run/beastagotchi/ui-runtime.json

if [[ -n "$EXPERIENCE" ]]; then
  [[ "$EXPERIENCE" =~ ^[A-Za-z0-9_-]+$ ]] || {
    echo 'Experience id may contain only letters, numbers, underscore, and dash.'
    exit 2
  }
  [[ "$EXPERIENCE_PAGE" =~ ^[A-Za-z0-9_-]+$ ]] || {
    echo 'Experience page may contain only letters, numbers, underscore, and dash.'
    exit 2
  }
  EXPERIENCE="${EXPERIENCE,,}"
  EXPERIENCE_PAGE="${EXPERIENCE_PAGE,,}"
  PYTHONPATH=/opt/beast-ui:/opt/beast-python/site-packages "$UI_PY" - "$EXPERIENCE" "$EXPERIENCE_PAGE" <<'PY'
import sys
from beastui.experience_registry import experience_renderer_summary

experience = sys.argv[1].strip().lower()
page = sys.argv[2].strip().lower()
catalog = experience_renderer_summary()
if experience not in catalog:
    available = ", ".join(sorted(catalog))
    raise SystemExit(f"Unknown Experience '{experience}'. Available: {available}")
if page not in catalog[experience]:
    available = ", ".join(catalog[experience])
    raise SystemExit(f"Unknown page '{page}' for Experience '{experience}'. Available: {available}")
PY
fi

mkdir -p "$STATE_DIR" /run/beastagotchi
rm -f /run/beastagotchi/touch-gestures.jsonl

clear_experience_override() {
  if [[ -f "$EXPERIENCE_OVERRIDE" ]]; then
    rm -f "$EXPERIENCE_OVERRIDE"
    rmdir "$OVERRIDE_DIR" 2>/dev/null || true
    systemctl daemon-reload
  fi
}

rollback_now() {
  echo 'Physical handoff failed; restoring Pwnagotchi display...'
  /opt/beast-ui/bin/release_display.sh || true
}
trap 'echo "ERROR during display handoff"; rollback_now' ERR

systemctl stop "$WATCHDOG_UNIT" 2>/dev/null || true
systemctl reset-failed "$WATCHDOG_UNIT" 2>/dev/null || true
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

# A stale runtime staging override must never leak into a new default session.
clear_experience_override

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
# Reassert the volatile telemetry contract before the unprivileged UI starts.
# A stale root-owned runtime file from an interrupted/manual test must not make
# telemetry silently disappear.
mkdir -p /run/beastagotchi
chgrp beastagotchi /run/beastagotchi
chmod 0775 /run/beastagotchi
rm -f "$RUNTIME" /run/beastagotchi/.ui-runtime.json.*.tmp
touch /run/beastagotchi/ui-test-mode

# Experience staging is a runtime-only systemd drop-in. The installed service,
# saved UI preferences, and normal boot path remain unchanged.
if [[ -n "$EXPERIENCE" ]]; then
  mkdir -p "$OVERRIDE_DIR"
  cat > "$EXPERIENCE_OVERRIDE" <<EOF
[Service]
ExecStart=
ExecStart=/opt/.pwn/bin/python3 -m beastui --root /opt/beast-ui --framebuffer /dev/fb1 --experience $EXPERIENCE --experience-page $EXPERIENCE_PAGE
EOF
  systemctl daemon-reload
fi

systemctl start beast-ui.service
sleep 3
systemctl is-active --quiet beast-ui.service || { journalctl -u beast-ui.service -n 80 --no-pager; exit 5; }

# The physical test is not considered armed until UI runtime telemetry exists
# and contains valid JSON. This turns telemetry loss into a start failure rather
# than a silent blind spot discovered after the test. Give a slower Pi up to
# ten additional seconds after the initial service settle time to publish it.
runtime_ok=0
for _ in $(seq 1 40); do
  if [[ -s "$RUNTIME" ]] && "$UI_PY" - "$RUNTIME" <<'PYJSON' >/dev/null 2>&1
import json, sys
with open(sys.argv[1]) as fh:
    obj=json.load(fh)
if not isinstance(obj,dict) or not obj.get("version"):
    raise SystemExit(1)
PYJSON
  then
    runtime_ok=1
    break
  fi
  sleep 0.25
done
if (( runtime_ok != 1 )); then
  echo 'Beast UI started but did not publish valid runtime telemetry.'
  systemctl status beast-ui.service --no-pager -l || true
  journalctl -u beast-ui.service -n 120 --no-pager || true
  exit 7
fi

# A bounded test gets a second, independent safety net in addition to the
# absolute rollback timer: sustained UI loss or a stale runtime heartbeat
# immediately records evidence and restores Pwnagotchi display ownership.
systemd-run --quiet --unit=beast-display-watchdog /opt/beast-ui/bin/display_watchdog.sh
systemd-run --quiet --unit=beast-display-rollback --on-active="${MINUTES}m" /opt/beast-ui/bin/auto_rollback.sh
trap - ERR

echo
echo 'BEAST UI PHYSICAL TEST IS ACTIVE.'
if [[ -n "$EXPERIENCE" ]]; then
  echo "Staging Experience: ${EXPERIENCE}:${EXPERIENCE_PAGE} (runtime-only; saved/default UI unchanged)."
fi
echo "Automatic rollback to Pwnagotchi display is scheduled in ${MINUTES} minute(s)."
echo 'Test: arrows, repeated LEFT/RIGHT swipes from middle pages, vertical drawer swipe, and long-press.'
echo 'Touches/gestures are shown temporarily on-screen in PHYS TEST mode.'
echo
echo 'If it looks/works correctly:  sudo /opt/beast-ui/bin/confirm_display.sh'
echo 'If anything is wrong:         sudo /opt/beast-ui/bin/release_display.sh'
echo 'Status:                       sudo /opt/beast-ui/bin/display_status.sh'
