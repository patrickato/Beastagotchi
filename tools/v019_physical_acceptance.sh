#!/usr/bin/env bash
set -euo pipefail

ROOT=/var/lib/beastagotchi/acceptance/v019
CURRENT="$ROOT/current"
PY=/opt/.pwn/bin/python3
UI_ROOT=/opt/beast-ui
CORE_ROOT=/opt/beast-core
BEAST_SITE=/opt/beast-python/site-packages
DEPS_DIR=/var/lib/beastagotchi/dependencies
QR_VERSION=8.2
BIN=/opt/beast-ui/bin
REPORT=/opt/beast-ui/bin/v019_acceptance_report.py
CAPTURE=/opt/beast-ui/bin/capture_fb.py
CLAIM=/opt/beast-ui/bin/claim_display_test.sh
CONFIRM=/opt/beast-ui/bin/confirm_display.sh
RELEASE=/opt/beast-ui/bin/release_display.sh
STATUS=/opt/beast-ui/bin/display_status.sh

require_root() {
  [[ ${EUID:-$(id -u)} -eq 0 ]] || { echo "Run with sudo."; exit 1; }
}

capture_state_subset() {
  local dest="$1"
  DEST="$dest" "$PY" - <<'PY'
import json, os, time, urllib.request
keep=(
    "health.core.state","health.core.ready","health.core.critical_count",
    "system.temp.cpu_c","system.cpu.total","system.memory.used_pct",
    "system.throttle.flags","system.clock.arm_mhz",
    "governor.mode","governor.reason","governor.budget_pct",
    "performance.beast.cpu_pct","performance.ui.avg_render_ms",
    "performance.fb.write_ratio_pct","performance.fb.changed_rows",
    "performance.fb.bytes_written","performance.fb.saved_bytes",
    "presentation.desired_owner","presentation.active_owner","presentation.status",
    "display.width","display.height","display.rotation",
    "progression.level","progression.stage","context.mode.effective",
    "power.battery.percent_estimate","power.power_w",
)
out={"captured_at":time.time(),"privacy":"curated_physical_acceptance"}
try:
    with urllib.request.urlopen("http://127.0.0.1:8090/state?meta=0",timeout=3) as r:
        state=json.load(r)
    if isinstance(state,dict):
        out["state"]={k:state.get(k) for k in keep if k in state}
except Exception as exc:
    out["error"]=type(exc).__name__
with open(os.environ["DEST"],"w") as fh:
    json.dump(out,fh,indent=2,sort_keys=True)
    fh.write("\n")
PY
}

session_dir() {
  [[ -L "$CURRENT" ]] || { echo "No current v0.19 acceptance session. Run: sudo beast-v019-accept start"; exit 2; }
  readlink -f "$CURRENT"
}

safe_label() {
  printf '%s' "${1:-capture}" | tr -cs 'A-Za-z0-9._-' '_' | cut -c1-48
}

write_preflight() {
  local out="$1"
  mkdir -p "$out"
  "$STATUS" > "$out/display-status-before.txt" 2>&1 || true
  systemctl status pwnagotchi.service bettercap.service beast-core.service beast-ui.service beast-studio.service --no-pager -l > "$out/services-before.txt" 2>&1 || true
  "$BIN/display_conflicts.py" > "$out/display-conflicts-before.txt" 2>&1 || true
  cp -a /opt/beast-ui/config/touch.json "$out/touch-active.json" 2>/dev/null || true
  sha256sum /etc/pwnagotchi/config.toml > "$out/pwnagotchi-config-before.sha256" 2>/dev/null || true
  capture_state_subset "$out/state-before.json"
  curl -fsS --max-time 4 'http://127.0.0.1:8090/health' > "$out/health-before.json" 2>/dev/null || true
  curl -fsS --max-time 5 'http://127.0.0.1:8090/capsule/types' > "$out/capsule-types.json" 2>/dev/null || true
  curl -fsS --max-time 5 'http://127.0.0.1:8090/capsule/export?type=lineage&name=0&achievements=0&appearance=0&qr_chars=220' > "$out/capsule-export.json" 2>/dev/null || true

  PYTHONPATH="$CORE_ROOT:$UI_ROOT:$BEAST_SITE" "$PY" - <<'PY' > "$out/preflight.json"
import hashlib, importlib.util, json, pathlib, time
result={"ts":time.time()}
try:
    import beastcore, beastui, beaststudio
    result["versions"]={
        "beastcore":getattr(beastcore,"__version__",None),
        "beastui":getattr(beastui,"__version__",None),
        "beaststudio":getattr(beaststudio,"__version__",None),
    }
except Exception as exc:
    result["versions_error"]=f"{type(exc).__name__}: {exc}"
try:
    import qrcode
    result["qr_renderer"]={
        "available":True,
        "backend":"python-qrcode",
        "version":getattr(qrcode,"__version__",None),
    }
except Exception as exc:
    result["qr_renderer"]={
        "available":False,
        "backend":None,
        "error":type(exc).__name__,
    }
fingerprints={}
for name in (
    "/opt/beast-ui/beastui/engine.py",
    "/opt/beast-ui/beastui/framebuffer.py",
    "/opt/beast-ui/beastui/qr_render.py",
    "/opt/beast-core/beastcore/capsules.py",
):
    p=pathlib.Path(name)
    if p.is_file():
        fingerprints[name]=hashlib.sha256(p.read_bytes()).hexdigest()
result["fingerprints"]=fingerprints
print(json.dumps(result,indent=2,sort_keys=True))
PY
}

capture_one() {
  local out label
  out="$(session_dir)"
  label="$(safe_label "${1:-capture}")"
  local stamp
  stamp="$(date +%Y%m%d_%H%M%S)"
  local prefix="$out/${stamp}-${label}"

  capture_state_subset "${prefix}-state.json"
  cp -a /run/beastagotchi/ui-runtime.json "${prefix}-ui-runtime.json" 2>/dev/null || true
  "$STATUS" > "${prefix}-display-status.txt" 2>&1 || true
  if [[ -c /dev/fb1 && -x "$CAPTURE" ]]; then
    "$PY" "$CAPTURE" /dev/fb1 "${prefix}-framebuffer.png" --width 480 --height 320 >/dev/null 2>&1 || true
  fi
  echo "Captured: $prefix-*"
}

sample_window() {
  local seconds="${1:-60}"
  [[ "$seconds" =~ ^[0-9]+$ ]] || { echo "sample seconds must be an integer"; exit 2; }
  (( seconds >= 5 && seconds <= 900 )) || { echo "sample seconds must be 5..900"; exit 2; }
  local out
  out="$(session_dir)"
  echo "Sampling objective UI/Core telemetry for ${seconds}s."
  echo "Use the TFT normally during this window: swipe pages, open Apps, open Capsules, cycle QR frames, open/close Control Center."
  SECONDS_TO_SAMPLE="$seconds" OUTFILE="$out/runtime-samples.jsonl" "$PY" - <<'PY'
import json, os, pathlib, time, urllib.request
seconds=int(os.environ["SECONDS_TO_SAMPLE"])
out=pathlib.Path(os.environ["OUTFILE"])
deadline=time.monotonic()+seconds
with out.open("a", buffering=1) as fh:
    while time.monotonic()<deadline:
        row={"ts":time.time(),"state":{},"runtime":{}}
        try:
            with urllib.request.urlopen("http://127.0.0.1:8090/state?meta=0",timeout=1.5) as r:
                obj=json.load(r)
            if isinstance(obj,dict):
                keep=(
                    "system.temp.cpu_c","system.cpu.total","system.memory.used_pct",
                    "system.throttle.flags","governor.mode","governor.reason",
                    "health.core.state","health.core.ready","presentation.active_owner",
                    "progression.beast.name","progression.level","progression.stage",
                )
                row["state"]={k:obj.get(k) for k in keep}
        except Exception as exc:
            row["state_error"]=type(exc).__name__
        try:
            obj=json.loads(pathlib.Path("/run/beastagotchi/ui-runtime.json").read_text())
            if isinstance(obj,dict): row["runtime"]=obj
        except Exception as exc:
            row["runtime_error"]=type(exc).__name__
        fh.write(json.dumps(row,separators=(",",":"))+"\n")
        time.sleep(1.0)
PY
  cp -a /run/beastagotchi/touch-gestures.jsonl "$out/touch-gestures.jsonl" 2>/dev/null || true
  capture_one "after-sample"
}

finalize_evidence() {
  local out mode stamp bundle
  out="$(session_dir)"
  mode="${1:-observe}"
  stamp="$(basename "$out")"

  capture_state_subset "$out/state-final.json"
  cp -a /run/beastagotchi/ui-runtime.json "$out/ui-runtime-final.json" 2>/dev/null || true
  cp -a /run/beastagotchi/touch-gestures.jsonl "$out/touch-gestures.jsonl" 2>/dev/null || true
  capture_one "final-before-owner-decision"

  cat > "$out/physical-observations.txt" <<'EOF'
BEASTAGOTCHI v0.19 PHYSICAL OBSERVATIONS
========================================
Fill this in only if useful, or simply tell ChatGPT the same observations.

READABILITY: unknown
TOUCH_ACCURACY: unknown
TOUCH_FEEL: unknown
NAVIGATION: unknown
QR_PHONE_SCAN: unknown
QR_MULTI_FRAME_USE: unknown
ANIMATION_SMOOTHNESS: unknown
BRIGHTNESS_GLARE: unknown
THERMAL_FEEL: unknown
OVERALL_POLISH: unknown
NOTES:
EOF

  if [[ -x "$REPORT" ]]; then
    "$PY" "$REPORT" "$out" --json "$out/acceptance-summary.json" --text "$out/acceptance-summary.txt" >/dev/null || true
  fi

  case "$mode" in
    pass|confirm)
      "$CONFIRM"
      echo "confirmed" > "$out/owner-decision.txt"
      ;;
    fail|rollback|release)
      "$RELEASE"
      echo "rolled_back" > "$out/owner-decision.txt"
      ;;
    observe|bundle)
      echo "no_owner_change" > "$out/owner-decision.txt"
      ;;
    *)
      echo "finish mode must be: observe | pass | rollback"
      exit 2
      ;;
  esac

  "$STATUS" > "$out/display-status-after.txt" 2>&1 || true
  systemctl status pwnagotchi.service bettercap.service beast-core.service beast-ui.service beast-studio.service --no-pager -l > "$out/services-after.txt" 2>&1 || true
  journalctl -u beast-ui.service --no-pager -n 260 > "$out/beast-ui-journal.txt" 2>&1 || true
  journalctl -u beast-core.service -p warning..alert --no-pager -n 160 > "$out/beast-core-warnings.txt" 2>&1 || true

  bundle="/home/pi/beast-v019-physical-acceptance-${stamp}.tar.gz"
  tar -czf "$bundle" -C "$ROOT" "$stamp"
  chown -R pi:pi "$out" 2>/dev/null || true
  chown pi:pi "$bundle" 2>/dev/null || true
  echo
  echo "Acceptance evidence bundle:"
  echo "  $bundle"
  echo
  if [[ -f "$out/acceptance-summary.txt" ]]; then
    cat "$out/acceptance-summary.txt"
  fi
}

cmd_start() {
  require_root
  local minutes="${1:-15}"
  [[ "$minutes" =~ ^[0-9]+$ ]] || { echo "rollback minutes must be an integer"; exit 2; }
  (( minutes >= 5 && minutes <= 120 )) || { echo "rollback minutes must be 5..120"; exit 2; }

  mkdir -p "$ROOT"
  if [[ -L "$CURRENT" ]]; then
    local old
    old="$(readlink -f "$CURRENT" 2>/dev/null || true)"
    if [[ -n "$old" && -f "$old/session-active" ]]; then
      echo "An acceptance session is already active: $old"
      echo "Finish it first: sudo beast-v019-accept finish observe"
      exit 3
    fi
  fi

  local stamp out
  stamp="$(date +%Y%m%d_%H%M%S)"
  out="$ROOT/$stamp"
  mkdir -p "$out"
  ln -sfn "$out" "$CURRENT"
  touch "$out/session-active"

  write_preflight "$out"

  "$PY" - "$out/preflight.json" <<'PY'
import json,sys
p=json.load(open(sys.argv[1]))
v=(p.get("versions") or {}).get("beastui")
qr=(p.get("qr_renderer") or {}).get("available")
print("Installed Beast UI:",v)
print("QR renderer available:",qr)
if not qr:
    print("NOTE: Capsule QR renderer is missing.")
    print("For the complete QR sub-gate, run before the session: sudo beast-v019-accept prepare-qr")
PY

  echo
  echo "Claiming TFT through the existing automatic-rollback handoff..."
  "$CLAIM" "$minutes"
  capture_one "initial-beast"

  cat > "$out/test-plan.txt" <<'EOF'
BEASTAGOTCHI v0.19 BOUNDED PHYSICAL ACCEPTANCE
==============================================
One substantial session; no piecemeal reinstall loop.

During the session:
1. Swipe through the main pages and use footer/page navigation.
2. Open Control Center; check target size/readability and close/open behavior.
3. Open Apps, move through categories/pages, then open CAPSULES.
4. On Capsule Share:
   - verify the QR is clean black/white with an intact quiet border;
   - scan the visible frame with a phone if the renderer is available;
   - use PREV/NEXT and horizontal swipe to change frames;
   - verify CLOSE is reliable.
5. Open at least one dense operational surface and one theme/visualizer surface.
6. Watch for clipped text, accidental taps, missed swipes, stutter or visual corruption.
7. From SSH while using the TFT, run:
      sudo beast-v019-accept sample 60
   This collects objective render/framebuffer/thermal evidence while you interact.

The rollback timer created by claim_display_test.sh remains authoritative.

PRIVACY:
- automated state/config evidence is curated and avoids raw config/full Core state;
- framebuffer PNGs preserve whatever is visibly on the TFT;
- keep this archive private unless screenshots have been reviewed/sanitized.

To end:
  sudo beast-v019-accept finish observe   # bundle only; leave current rollback timer/owner as-is
  sudo beast-v019-accept finish pass      # bundle + explicitly confirm Beast display ownership
  sudo beast-v019-accept finish rollback  # bundle + immediately restore Pwnagotchi display
EOF

  echo
  cat "$out/test-plan.txt"
  echo
  echo "Session: $out"
}

cmd_status() {
  require_root
  local out
  out="$(session_dir)"
  echo "Session: $out"
  "$STATUS" || true
  echo
  if [[ -f "$out/preflight.json" ]]; then cat "$out/preflight.json"; fi
}

cmd_capture() {
  require_root
  capture_one "${1:-manual}"
}

cmd_sample() {
  require_root
  sample_window "${1:-60}"
}

cmd_finish() {
  require_root
  local out
  out="$(session_dir)"
  finalize_evidence "${1:-observe}"
  rm -f "$out/session-active"
}

cmd_preflight() {
  require_root
  mkdir -p "$ROOT"
  local out="$ROOT/preflight-$(date +%Y%m%d_%H%M%S)"
  mkdir -p "$out"
  write_preflight "$out"
  cat "$out/preflight.json"
  echo "Preflight evidence: $out"
}

usage() {
  cat <<'EOF'
Usage:
  sudo beast-v019-accept preflight
  sudo beast-v019-accept start [rollback-minutes]
  sudo beast-v019-accept status
  sudo beast-v019-accept capture [label]
  sudo beast-v019-accept sample [seconds]
  sudo beast-v019-accept finish [observe|pass|rollback]
EOF
}

case "${1:-}" in
  preflight) shift; cmd_preflight "$@" ;;
  start) shift; cmd_start "$@" ;;
  status) shift; cmd_status "$@" ;;
  capture) shift; cmd_capture "$@" ;;
  sample) shift; cmd_sample "$@" ;;
  finish) shift; cmd_finish "$@" ;;
  *) usage; exit 2 ;;
esac
