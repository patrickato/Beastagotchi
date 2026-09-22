#!/usr/bin/env bash
set -euo pipefail
logger -t beast-display 'Automatic display rollback timer fired.'
exec /opt/beast-ui/bin/release_display.sh
