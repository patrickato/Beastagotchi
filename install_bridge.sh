#!/usr/bin/env bash
set -euo pipefail
SRC="$(cd "$(dirname "$0")" && pwd)"
CFG=/etc/pwnagotchi/config.toml
PLUGDIR=/etc/pwnagotchi/custom-plugins
STAMP="$(date +%Y%m%d_%H%M%S)"
if [[ ${EUID:-$(id -u)} -ne 0 ]]; then echo "Run with sudo: sudo ./install_bridge.sh"; exit 1; fi
install -d -m 0755 "$PLUGDIR"
install -m 0644 "$SRC/pwnagotchi_plugin/beast_bridge.py" "$PLUGDIR/beast_bridge.py"
if grep -q '^\[main\.plugins\.beast_bridge\]' "$CFG"; then
  echo "beast_bridge config section already exists; plugin file refreshed only."
else
  cp -a "$CFG" "${CFG}.before-beast-bridge-${STAMP}"
  cat >> "$CFG" <<'EOF'

# Beastagotchi read-only telemetry bridge
[main.plugins.beast_bridge]
enabled = true
state_file = "/run/beastagotchi/pwnagotchi_bridge.json"
EOF
  echo "Added [main.plugins.beast_bridge] and saved backup: ${CFG}.before-beast-bridge-${STAMP}"
fi
cat <<'EOF'
Bridge installed/enabled in configuration but Pwnagotchi was NOT restarted.
To activate when ready:
  sudo systemctl restart pwnagotchi
Then verify:
  sleep 10
  cat /run/beastagotchi/pwnagotchi_bridge.json | python3 -m json.tool | head -n 100
EOF
