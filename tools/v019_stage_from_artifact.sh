#!/usr/bin/env bash
set -euo pipefail

# Stage the exact commit-pinned v0.19 acceptance artifact on the reference Pi.
# This wrapper verifies provenance, extracts the tested source, reuses the normal
# Core/UI installers, starts Core only, and leaves physical display ownership
# untouched until the user explicitly runs beast-v019-accept start.

require_root() {
  [[ ${EUID:-$(id -u)} -eq 0 ]] || { echo "Run with sudo."; exit 1; }
}

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PREPARE_QR=0
KEEP_SOURCE=1

usage() {
  cat <<'EOF'
Usage:
  sudo ./STAGE_ON_PI.sh [--prepare-qr] [--no-keep-source]

What it does:
  - verifies the Pi acceptance source archive SHA-256
  - verifies SOURCE_COMMIT_SHA.txt matches the archive name/root
  - extracts the exact commit-pinned source
  - preserves an existing Beast Core config
  - installs Beast Core + Beast UI/Studio using the project installers
  - starts Beast Core only
  - optionally prepares qrcode==8.2 in /opt/beast-python/site-packages
  - runs beast-v019-accept preflight

What it does NOT do:
  - does not enable or start Beast UI
  - does not claim the TFT
  - does not modify Pwnagotchi's /opt/.pwn site-packages
  - does not confirm permanent Beast display ownership
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --prepare-qr) PREPARE_QR=1 ;;
    --no-keep-source) KEEP_SOURCE=0 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1"; usage; exit 2 ;;
  esac
  shift
done

require_root

mapfile -t ARCHIVES < <(find "$SCRIPT_DIR" -maxdepth 1 -type f -name 'beastagotchi-v019-pi-acceptance-*.tar.gz' -printf '%f\n' | sort)
[[ ${#ARCHIVES[@]} -eq 1 ]] || {
  echo "Expected exactly one beastagotchi-v019-pi-acceptance-*.tar.gz beside this script."
  printf 'Found: %s\n' "${ARCHIVES[*]:-(none)}"
  exit 3
}
ARCHIVE_NAME="${ARCHIVES[0]}"
ARCHIVE="$SCRIPT_DIR/$ARCHIVE_NAME"
CHECKSUM="$SCRIPT_DIR/$ARCHIVE_NAME.sha256"
SOURCE_SHA_FILE="$SCRIPT_DIR/SOURCE_COMMIT_SHA.txt"
CI_SHA_FILE="$SCRIPT_DIR/CI_TESTED_SHA.txt"

[[ -f "$CHECKSUM" ]] || { echo "Missing checksum: $CHECKSUM"; exit 4; }
[[ -f "$SOURCE_SHA_FILE" ]] || { echo "Missing SOURCE_COMMIT_SHA.txt"; exit 4; }
[[ -f "$CI_SHA_FILE" ]] || { echo "Missing CI_TESTED_SHA.txt"; exit 4; }

echo "Verifying acceptance source archive..."
(
  cd "$SCRIPT_DIR"
  sha256sum -c "$(basename "$CHECKSUM")"
)

SOURCE_SHA="$(tr -d '[:space:]' < "$SOURCE_SHA_FILE")"
CI_SHA="$(tr -d '[:space:]' < "$CI_SHA_FILE")"
[[ "$SOURCE_SHA" =~ ^[0-9a-f]{40}$ ]] || { echo "Invalid source SHA."; exit 5; }
[[ "$CI_SHA" =~ ^[0-9a-f]{40}$ ]] || { echo "Invalid CI-tested SHA."; exit 5; }

SHORT="${SOURCE_SHA:0:12}"
case "$ARCHIVE_NAME" in
  *"$SHORT"*) ;;
  *) echo "Archive filename does not contain source SHA prefix $SHORT"; exit 6 ;;
esac

ROOT_NAME="$(tar -tzf "$ARCHIVE" | awk -F/ 'NR==1{first=$1} END{print first}')"
[[ "$ROOT_NAME" == "Beastagotchi-v019-$SHORT" ]] || {
  echo "Archive root mismatch: expected Beastagotchi-v019-$SHORT, got $ROOT_NAME"
  exit 6
}

DEPLOY_ROOT="/var/lib/beastagotchi/deployments/v019"
STAMP="$(date +%Y%m%d_%H%M%S)"
SESSION="$DEPLOY_ROOT/$STAMP-$SHORT"
SOURCE_ROOT="$SESSION/source"
mkdir -p "$SOURCE_ROOT"

cat > "$SESSION/provenance.json" <<EOF
{
  "schema": 1,
  "source_commit": "$SOURCE_SHA",
  "ci_tested_commit": "$CI_SHA",
  "archive": "$ARCHIVE_NAME",
  "archive_sha256": "$(sha256sum "$ARCHIVE" | awk '{print $1}')",
  "staged_at_utc": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "display_claimed": false
}
EOF

# Record only non-secret deployment state. Do not copy raw Pwnagotchi config.
systemctl is-active pwnagotchi.service > "$SESSION/pwnagotchi-service-before.txt" 2>&1 || true
systemctl is-active beast-core.service > "$SESSION/beast-core-service-before.txt" 2>&1 || true
systemctl is-active beast-ui.service > "$SESSION/beast-ui-service-before.txt" 2>&1 || true
sha256sum /etc/pwnagotchi/config.toml > "$SESSION/pwnagotchi-config-before.sha256" 2>/dev/null || true
if [[ -f /etc/beastagotchi/core.toml ]]; then
  cp -a /etc/beastagotchi/core.toml "$SESSION/core.toml.before"
fi
if [[ -f /var/lib/beastagotchi/beast.db && -x /opt/.pwn/bin/python3 ]]; then
  echo "Creating local pre-stage Beast SQLite backup..."
  BACKUP_DB="$SESSION/beast.db.before" /opt/.pwn/bin/python3 - <<'PY'
import os, sqlite3
src=sqlite3.connect("/var/lib/beastagotchi/beast.db", timeout=10)
dst=sqlite3.connect(os.environ["BACKUP_DB"])
try:
    src.backup(dst)
finally:
    dst.close()
    src.close()
PY
  chmod 0600 "$SESSION/beast.db.before"
fi

echo "Extracting exact source commit $SOURCE_SHA ..."
tar -xzf "$ARCHIVE" -C "$SOURCE_ROOT" --strip-components=1

[[ -x "$SOURCE_ROOT/install.sh" && -x "$SOURCE_ROOT/install_ui.sh" ]] || {
  echo "Extracted source is missing expected installers."
  exit 7
}

echo
echo "Installing Beast Core from $SHORT ..."
"$SOURCE_ROOT/install.sh"

echo
echo "Installing Beast UI/Studio from $SHORT ..."
"$SOURCE_ROOT/install_ui.sh"

echo
echo "Starting Beast Core only. Physical display ownership remains with Pwnagotchi."
systemctl start beast-core.service
sleep 3

if [[ $PREPARE_QR -eq 1 ]]; then
  echo
  echo "Preparing optional Beast-owned QR renderer..."
  /usr/local/bin/beast-v019-accept prepare-qr
fi

echo
echo "Running target preflight..."
/usr/local/bin/beast-v019-accept preflight

ln -sfn "$SESSION" "$DEPLOY_ROOT/current-staged"
if [[ $KEEP_SOURCE -eq 0 ]]; then
  rm -rf "$SOURCE_ROOT"
fi

echo
echo "============================================================"
echo "Beastagotchi v0.19 staged successfully."
echo "Source commit: $SOURCE_SHA"
echo "CI-tested SHA: $CI_SHA"
echo "Display claimed: NO"
echo "Pwnagotchi display ownership remains untouched."
echo
echo "NEXT:"
if [[ $PREPARE_QR -eq 0 ]]; then
  echo "  Optional QR gate: sudo beast-v019-accept prepare-qr"
fi
echo "  Start bounded TFT session: sudo beast-v019-accept start 15"
echo "  During use:                sudo beast-v019-accept sample 60"
echo "  Finish without deciding:   sudo beast-v019-accept finish observe"
echo "  Or rollback immediately:   sudo beast-v019-accept finish rollback"
echo
echo "Deployment provenance: $SESSION/provenance.json"
echo "============================================================"
