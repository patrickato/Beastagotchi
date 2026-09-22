#!/usr/bin/env bash
set -euo pipefail
if [[ ${EUID:-$(id -u)} -ne 0 ]]; then echo "Run with sudo: sudo ./remove_bridge.sh"; exit 1; fi
rm -f /etc/pwnagotchi/custom-plugins/beast_bridge.py /run/beastagotchi/pwnagotchi_bridge.json
cat <<'EOF'
Bridge plugin file removed. The [main.plugins.beast_bridge] TOML section was intentionally left in place rather than editing user configuration automatically. Set enabled=false or restore the backup created by install_bridge.sh before restarting Pwnagotchi.
EOF
