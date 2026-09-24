import json
from pathlib import Path

from tools.v019_acceptance_report import summarize_session, write_text_report


def test_v019_acceptance_report_summarizes_runtime_and_preserves_physical_boundary(tmp_path):
    session = tmp_path / "session"
    session.mkdir()
    (session / "preflight.json").write_text(json.dumps({
        "qr_renderer": {"available": True, "backend": "python-qrcode"},
        "versions": {"beastui": "0.19.0"},
        "deployment": {
            "source_commit": "a" * 40,
            "ci_tested_commit": "b" * 40,
            "archive_sha256": "c" * 64,
            "staged_at_utc": "2026-09-24T12:00:00Z",
        },
    }))
    (session / "capsule-export.json").write_text(json.dumps({
        "ok": True,
        "qr": {"frame_count": 3},
    }))
    rows = [
        {
            "ts": 1,
            "state": {"system.temp.cpu_c": 51.0, "system.cpu.total": 12.0},
            "runtime": {
                "avg_render_ms": 10.0,
                "avg_compose_ms": 7.0,
                "avg_fb_write_ms": 2.0,
                "target_fps": 12.0,
                "lifetime_fps": 9.0,
                "framebuffer": {
                    "changed_rows": 40,
                    "bytes_written": 40000,
                    "frame_bytes": 307200,
                    "full_write": False,
                    "totals": {"frames": 100, "bytes_written": 1000000, "full_writes": 5, "saved_bytes": 10000000},
                },
            },
        },
        {
            "ts": 2,
            "state": {"system.temp.cpu_c": 55.0, "system.cpu.total": 22.0},
            "runtime": {
                "avg_render_ms": 14.0,
                "avg_compose_ms": 9.0,
                "avg_fb_write_ms": 3.0,
                "target_fps": 12.0,
                "lifetime_fps": 10.0,
                "framebuffer": {
                    "changed_rows": 80,
                    "bytes_written": 80000,
                    "frame_bytes": 307200,
                    "full_write": False,
                    "totals": {"frames": 112, "bytes_written": 1500000, "full_writes": 5, "saved_bytes": 12500000},
                },
            },
        },
    ]
    (session / "runtime-samples.jsonl").write_text("\n".join(json.dumps(x) for x in rows) + "\n")
    (session / "touch-gestures.jsonl").write_text(
        json.dumps({"kind": "tap"}) + "\n" +
        json.dumps({"kind": "swipe"}) + "\n" +
        json.dumps({"kind": "swipe"}) + "\n"
    )
    (session / "state-final.json").write_text(json.dumps({
        "privacy": "curated_physical_acceptance",
        "state": {
            "health.core.state": "healthy",
            "governor.mode": "FULL",
        },
    }))
    (session / "ui-runtime-final.json").write_text(json.dumps({
        "version": "0.19.0",
        "theme": "classic",
        "page": "home",
    }))

    summary = summarize_session(session)
    assert summary["evidence_class"] == "target_physical_session"
    assert summary["physical_user_judgment"] == "required"
    assert summary["sample_count"] == 2
    assert summary["deployment"]["source_commit"] == "a" * 40
    assert summary["deployment"]["ci_tested_commit"] == "b" * 40
    assert summary["deployment"]["archive_sha256"] == "c" * 64
    assert summary["metrics"]["cpu_temp_c"]["avg"] == 53.0
    assert summary["metrics"]["avg_render_ms"]["avg"] == 12.0
    assert summary["metrics"]["framebuffer_totals_delta"]["frames"] == 12
    assert summary["metrics"]["framebuffer_totals_delta"]["saved_bytes"] == 2500000
    assert summary["touch"]["kinds"] == {"swipe": 2, "tap": 1}
    assert summary["capsule"]["export_ok"] is True
    assert summary["capsule"]["frame_count"] == 3
    assert summary["capsule"]["renderer_available"] is True
    assert summary["warnings"] == []

    text = write_text_report(summary)
    assert "does not decide physical acceptance" in text
    assert "Source commit: " + ("a" * 40) in text
    assert "CI-tested commit: " + ("b" * 40) in text
    assert "QR_PHONE_SCAN" not in text


def test_v019_acceptance_report_warns_without_faking_missing_evidence(tmp_path):
    session = tmp_path / "session"
    session.mkdir()
    (session / "preflight.json").write_text(json.dumps({
        "qr_renderer": {"available": False, "backend": None},
    }))
    (session / "capsule-export.json").write_text(json.dumps({"ok": False}))
    (session / "ui-runtime-final.json").write_text(json.dumps({
        "version": "0.18.0",
        "theme": "classic",
        "page": "system",
    }))

    summary = summarize_session(session)
    assert summary["sample_count"] == 0
    assert summary["metrics"]["cpu_temp_c"]["avg"] is None
    assert summary["capsule"]["renderer_available"] is False
    assert any("No runtime sample" in x for x in summary["warnings"])
    assert any("QR renderer" in x for x in summary["warnings"])
    assert any("Lineage Capsule" in x for x in summary["warnings"])
    assert any("older v0.18" in x for x in summary["warnings"])


def test_v019_acceptance_harness_curates_sensitive_evidence():
    script = (Path(__file__).resolve().parents[1] / "tools" / "v019_physical_acceptance.sh").read_text()
    assert "curated_physical_acceptance" in script
    assert "pwnagotchi-config-before.sha256" in script
    assert "pwnagotchi-config-before.toml" not in script
    assert "platform-bundle" not in script
    assert "pwnagotchi-journal.txt" not in script
    assert "name=0&achievements=0&appearance=0" in script
    assert "deployment-provenance.json" in script
    assert "/var/lib/beastagotchi/deployments/v019/current-staged" in script


def test_v019_qr_optional_dependency_is_beast_owned_and_provenanced():
    root = Path(__file__).resolve().parents[1]
    script = (root / "tools" / "v019_physical_acceptance.sh").read_text()
    ui_service = (root / "ui_systemd" / "beast-ui.service").read_text()
    studio_service = (root / "ui_systemd" / "beast-studio.service").read_text()
    installer = (root / "install_ui.sh").read_text()

    assert "QR_VERSION=8.2" in script
    assert '--target "$BEAST_SITE"' in script
    assert '"qrcode==$QR_VERSION"' in script
    assert '"wheel_sha256"' in script
    assert '"dependency_scope":"beast_owned_optional"' in script
    assert '"pwnagotchi_site_packages_modified":False' in script
    assert "prepare-qr" in script and "remove-qr" in script
    assert '"$BEAST_SITE/bin/qr"' in script
    assert "/opt/beast-python/site-packages" in ui_service
    assert "/opt/beast-python/site-packages" in studio_service
    assert "/opt/beast-python/site-packages" in installer
    assert "/opt/.pwn/lib/" not in script


def test_v019_pi_source_artifact_pins_real_pr_head_and_portable_checksum():
    workflow = (Path(__file__).resolve().parents[1] / ".github" / "workflows" / "tests.yml").read_text()
    assert "github.event.pull_request.head.sha || github.sha" in workflow
    assert 'git archive --format=tar.gz' in workflow
    assert '"$SOURCE_SHA"' in workflow
    assert "SOURCE_COMMIT_SHA.txt" in workflow
    assert "CI_TESTED_SHA.txt" in workflow
    assert '(cd "$OUTDIR" && sha256sum "$NAME"' in workflow
    assert '> "$OUTDIR/COMMIT_SHA.txt"' not in workflow


def test_v019_acceptance_harness_keeps_owner_decision_explicit():
    script = (Path(__file__).resolve().parents[1] / "tools" / "v019_physical_acceptance.sh").read_text()
    assert "finish [observe|pass|rollback]" in script
    assert 'finalize_evidence "${1:-observe}"' in script
    assert '"$CONFIRM"' in script
    assert '"$RELEASE"' in script
    # Starting a session uses the already-proven auto-rollback handoff rather
    # than re-implementing config ownership mutations in a second script.
    assert '"$CLAIM" "$minutes"' in script
