import json
import subprocess
from pathlib import Path

from tools.v019_acceptance_report import summarize_session


ROOT = Path(__file__).resolve().parents[1]


def _read(rel: str) -> str:
    return (ROOT / rel).read_text()


def test_bounded_display_handoff_requires_telemetry_and_arms_independent_watchdog():
    claim = _read("display_handoff/claim_display_test.sh")
    watchdog = _read("display_handoff/display_watchdog.sh")
    release = _read("display_handoff/release_display.sh")
    confirm = _read("display_handoff/confirm_display.sh")

    assert 'RUNTIME=/run/beastagotchi/ui-runtime.json' in claim
    assert 'rm -f "$RUNTIME"' in claim
    assert "did not publish valid runtime telemetry" in claim
    assert "systemd-run --quiet --unit=beast-display-watchdog" in claim
    assert claim.index("did not publish valid runtime telemetry") < claim.index("--unit=beast-display-watchdog")
    assert claim.index("--unit=beast-display-watchdog") < claim.index("--unit=beast-display-rollback")

    assert "ui runtime heartbeat stale" in watchdog
    assert "ui runtime heartbeat missing" in watchdog
    assert "beast-ui inactive" in watchdog
    assert "final" not in watchdog.lower()  # watchdog evidence is immediate, not deferred to finish
    assert "BEAST_DISPLAY_WATCHDOG=1 /opt/beast-ui/bin/release_display.sh" in watchdog
    assert "beast-ui-journal.txt" in watchdog
    assert "beast-ui-show.txt" in watchdog
    assert "framebuffer.png" in watchdog

    assert release.index('systemctl stop "$WATCHDOG_UNIT"') < release.index("systemctl stop beast-ui.service")
    assert 'BEAST_DISPLAY_WATCHDOG:-0' in release
    assert 'systemctl stop "$WATCHDOG_UNIT"' in confirm


def test_all_display_handoff_scripts_pass_shell_syntax():
    scripts = sorted(str(p) for p in (ROOT / "display_handoff").glob("*.sh"))
    assert scripts
    subprocess.run(["bash", "-n", *scripts], check=True)


def test_acceptance_captures_failure_evidence_before_owner_decision():
    script = _read("tools/v019_physical_acceptance.sh")
    assert "capture_service_evidence" in script
    assert 'capture_service_evidence "$out" "after-sample"' in script
    before = script.index('capture_service_evidence "$out" "final-before-owner-decision"')
    decision = script.index('case "$mode" in')
    assert before < decision
    assert "runtime_path_exists" in script
    assert "ui_service_state" in script
    assert "ExecMainStatus" in script
    assert "NRestarts" in script


def test_acceptance_report_marks_core_only_samples_as_invalid_ui_telemetry(tmp_path):
    rows = [
        {
            "ts": 1,
            "state": {"system.temp.cpu_c": 68.0, "system.cpu.total": 45.0},
            "runtime": {},
            "runtime_error": "FileNotFoundError",
            "runtime_path_exists": False,
            "ui_service_state": "active",
        },
        {
            "ts": 2,
            "state": {"system.temp.cpu_c": 69.0, "system.cpu.total": 50.0},
            "runtime": {},
            "runtime_error": "FileNotFoundError",
            "runtime_path_exists": False,
            "ui_service_state": "active",
        },
    ]
    (tmp_path / "runtime-samples.jsonl").write_text("\n".join(json.dumps(x) for x in rows) + "\n")
    summary = summarize_session(tmp_path)
    assert summary["sample_count"] == 2
    assert summary["runtime_sample_count"] == 0
    assert summary["metrics"]["cpu_temp_c"]["avg"] == 68.5
    assert summary["metrics"]["avg_render_ms"]["samples"] == 0
    assert any("runtime telemetry was absent" in warning for warning in summary["warnings"])
