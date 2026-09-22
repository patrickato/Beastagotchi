#!/usr/bin/env bash
set -u
CFG=/etc/pwnagotchi/config.toml
PY=/opt/beast-ui/bin/display_config.py
"$PY" --config "$CFG" status
printf '\nbeast-ui: '; systemctl is-active beast-ui.service 2>/dev/null || true
printf 'beast-ui enabled: '; systemctl is-enabled beast-ui.service 2>/dev/null || true
printf 'pwnagotchi: '; systemctl is-active pwnagotchi.service 2>/dev/null || true
printf 'beast-core: '; systemctl is-active beast-core.service 2>/dev/null || true
printf 'rollback timer: '; systemctl is-active beast-display-rollback.timer 2>/dev/null || true
