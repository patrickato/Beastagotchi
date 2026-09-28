#!/usr/bin/env bash
set -euo pipefail

BACKEND=/opt/beast-ui/bin/v019_physical_acceptance.sh
ROOT=/var/lib/beastagotchi/acceptance/v019
CURRENT="$ROOT/current"
PY=/opt/.pwn/bin/python3

usage() {
  cat <<'EOF'
Usage:
  sudo beast-v019-accept prepare-qr
  sudo beast-v019-accept remove-qr
  sudo beast-v019-accept preflight
  sudo beast-v019-accept start [rollback-minutes] [experience] [experience-page]
  sudo beast-v019-accept status
  sudo beast-v019-accept capture [label]
  sudo beast-v019-accept sample [seconds]
  sudo beast-v019-accept finish [observe|pass|rollback]

Experience examples:
  sudo beast-v019-accept start 15 atlas home
  sudo beast-v019-accept start 15 forge system
  sudo beast-v019-accept start 15 observatory spectrum
  sudo beast-v019-accept start 15 habitat beast
  sudo beast-v019-accept start 15 monolith overview

Omit experience/page to run the normal legacy Beast UI acceptance path.
EOF
}

[[ -x "$BACKEND" ]] || {
  echo "Acceptance backend not installed: $BACKEND"
  exit 4
}

case "${1:-}" in
  start)
    shift
    minutes="${1:-15}"
    experience="${2:-}"
    page="${3:-home}"
    (( $# <= 3 )) || { usage; exit 2; }

    if [[ -z "$experience" ]]; then
      exec "$BACKEND" start "$minutes"
    fi

    # The claim helper performs authoritative Experience/page validation before
    # it changes display ownership. These environment values only select the
    # staging renderer for this bounded acceptance session.
    BEAST_ACCEPT_EXPERIENCE="$experience" \
    BEAST_ACCEPT_EXPERIENCE_PAGE="$page" \
      "$BACKEND" start "$minutes"

    session="$(readlink -f "$CURRENT" 2>/dev/null || true)"
    [[ -n "$session" && -d "$session" ]] || {
      echo 'Experience started but acceptance session directory could not be resolved.'
      exit 5
    }

    EXPERIENCE="$experience" PAGE="$page" DEST="$session/experience-staging.json" "$PY" - <<'PY'
import json, os, time
payload = {
    "schema": 1,
    "mode": "staging_only",
    "experience": os.environ["EXPERIENCE"].strip().lower(),
    "page": os.environ["PAGE"].strip().lower(),
    "saved_ui_preferences_modified": False,
    "permanent_service_modified": False,
    "recorded_at": time.time(),
}
with open(os.environ["DEST"], "w") as fh:
    json.dump(payload, fh, indent=2, sort_keys=True)
    fh.write("\n")
PY
    echo "Recorded staged Experience evidence: $session/experience-staging.json"
    ;;
  ""|-h|--help|help)
    usage
    ;;
  *)
    exec "$BACKEND" "$@"
    ;;
esac
