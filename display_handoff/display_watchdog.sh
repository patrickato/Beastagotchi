#!/usr/bin/env bash
set -euo pipefail

STATE_DIR=/var/lib/beastagotchi/display-handoff
BACKUP=$STATE_DIR/config.toml.pre-beast
ACCEPT_ROOT=/var/lib/beastagotchi/acceptance/v019
CURRENT=$ACCEPT_ROOT/current
RUNTIME=/run/beastagotchi/ui-runtime.json
TEST_MODE=/run/beastagotchi/ui-test-mode
STATUS=/opt/beast-ui/bin/display_status.sh
CAPTURE=/opt/beast-ui/bin/capture_fb.py
PY=/opt/.pwn/bin/python3
INTERVAL=${BEAST_WATCHDOG_INTERVAL:-2}
STALE_SECONDS=${BEAST_WATCHDOG_STALE_SECONDS:-20}
START_GRACE=${BEAST_WATCHDOG_START_GRACE:-8}

snapshot_failure() {
  local reason="$1" stamp dest session
  stamp="$(date +%Y%m%d_%H%M%S)"
  session="$(readlink -f "$CURRENT" 2>/dev/null || true)"
  if [[ -n "$session" && -d "$session" ]]; then
    dest="$session/watchdog-$stamp"
  else
    dest="$STATE_DIR/failures/$stamp"
  fi
  mkdir -p "$dest"
  printf '%s\n' "$reason" > "$dest/reason.txt"
  date -Ins > "$dest/captured-at.txt" 2>/dev/null || date > "$dest/captured-at.txt"
  "$STATUS" > "$dest/display-status.txt" 2>&1 || true
  systemctl show beast-ui.service \
    -p ActiveState -p SubState -p Result -p ExecMainCode -p ExecMainStatus \
    -p NRestarts -p ActiveEnterTimestamp -p InactiveEnterTimestamp \
    > "$dest/beast-ui-show.txt" 2>&1 || true
  systemctl status pwnagotchi.service beast-core.service beast-ui.service beast-studio.service \
    --no-pager -l > "$dest/services.txt" 2>&1 || true
  journalctl -u beast-ui.service -b --no-pager -n 400 > "$dest/beast-ui-journal.txt" 2>&1 || true
  journalctl -u beast-core.service -b -p warning..alert --no-pager -n 200 > "$dest/beast-core-warnings.txt" 2>&1 || true
  cp -a "$RUNTIME" "$dest/ui-runtime.json" 2>/dev/null || true
  cp -a /run/beastagotchi/touch-gestures.jsonl "$dest/touch-gestures.jsonl" 2>/dev/null || true
  if [[ -c /dev/fb1 && -x "$CAPTURE" ]]; then
    "$PY" "$CAPTURE" /dev/fb1 "$dest/framebuffer.png" --width 480 --height 320 >/dev/null 2>&1 || true
  fi
  logger -t beast-display "Watchdog restoring Pwnagotchi display: $reason; evidence=$dest"
}

# The watchdog exists only for a bounded, reversible physical handoff.
[[ -f "$TEST_MODE" && -f "$BACKUP" ]] || exit 0
sleep "$START_GRACE"

inactive_checks=0
while [[ -f "$TEST_MODE" && -f "$BACKUP" ]]; do
  if systemctl is-active --quiet beast-ui.service; then
    inactive_checks=0
  else
    inactive_checks=$((inactive_checks+1))
    # Restart=on-failure gets a chance to recover. Sustained loss of the display
    # owner is not acceptable during a protected test.
    if (( inactive_checks >= 3 )); then
      snapshot_failure "beast-ui inactive for at least $((inactive_checks*INTERVAL)) seconds"
      BEAST_DISPLAY_WATCHDOG=1 /opt/beast-ui/bin/release_display.sh || true
      exit 20
    fi
  fi

  if [[ -f "$RUNTIME" ]]; then
    now=$(date +%s)
    mtime=$(stat -c %Y "$RUNTIME" 2>/dev/null || echo 0)
    age=$((now-mtime))
    if (( mtime > 0 && age > STALE_SECONDS )); then
      snapshot_failure "ui runtime heartbeat stale for ${age} seconds"
      BEAST_DISPLAY_WATCHDOG=1 /opt/beast-ui/bin/release_display.sh || true
      exit 21
    fi
  else
    # After startup grace the runtime contract requires a first-frame file.
    snapshot_failure "ui runtime heartbeat missing after startup grace"
    BEAST_DISPLAY_WATCHDOG=1 /opt/beast-ui/bin/release_display.sh || true
    exit 22
  fi
  sleep "$INTERVAL"
done
