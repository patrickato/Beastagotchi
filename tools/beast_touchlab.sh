#!/usr/bin/env bash
set -euo pipefail
exec /opt/.pwn/bin/python3 /opt/beast-ui/bin/touch_lab.py "$@"
