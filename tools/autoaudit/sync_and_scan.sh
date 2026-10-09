#!/usr/bin/env bash
# Read-only sync from Pwnagotchi to a separate GPU host.
set -euo pipefail
: "$PI_CAPTURE_SOURCE"
: "$AUTOAUDIT_CONFIG"
: "$AUTOAUDIT_INBOX"
umask 077
mkdir -p -- "$AUTOAUDIT_INBOX"
rsync -rtz --delay-updates --prune-empty-dirs \
  --include='*/' --include='*.pcapng' --include='*.pcap' --include='*.cap' \
  --exclude='*' -e 'ssh -o BatchMode=yes' \
  "$PI_CAPTURE_SOURCE" "$AUTOAUDIT_INBOX/"
python3 -m tools.autoaudit.runner --config "$AUTOAUDIT_CONFIG"
