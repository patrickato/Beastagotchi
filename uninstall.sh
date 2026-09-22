#!/usr/bin/env bash
set -euo pipefail
if [[ ${EUID:-$(id -u)} -ne 0 ]]; then echo "Run with sudo"; exit 1; fi

# Never remove Beast UI while it owns the LCD; restore the exact prior Pwnagotchi
# configuration first when a rollback backup is active.
if [[ -x /opt/beast-ui/bin/release_display.sh ]]; then
  /opt/beast-ui/bin/release_display.sh || true
else
  systemctl disable --now beast-ui.service 2>/dev/null || true
fi
systemctl disable --now beast-core.service 2>/dev/null || true
rm -f /etc/systemd/system/beast-ui.service /etc/systemd/system/beast-core.service
rm -rf /opt/beast-ui /opt/beast-core
systemctl daemon-reload
printf 'Beast Core/UI code and services removed. Preserved /etc/beastagotchi and /var/lib/beastagotchi history/database.\n'
