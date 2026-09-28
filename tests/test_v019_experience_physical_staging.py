import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text()


def test_physical_experience_staging_is_runtime_only_and_validated():
    claim = _read("display_handoff/claim_display_test.sh")
    service = _read("ui_systemd/beast-ui.service")
    installer = _read("install_ui.sh")

    assert "OVERRIDE_DIR=/run/systemd/system/beast-ui.service.d" in claim
    assert "90-beast-experience-test.conf" in claim
    assert "experience_renderer_summary" in claim
    assert "Unknown Experience" in claim
    assert "Unknown page" in claim
    assert 'EXPERIENCE="${EXPERIENCE,,}"' in claim
    assert 'EXPERIENCE_PAGE="${EXPERIENCE_PAGE,,}"' in claim
    assert "ExecStart=" in claim
    assert "--experience $EXPERIENCE --experience-page $EXPERIENCE_PAGE" in claim
    assert "systemctl daemon-reload" in claim

    # The normal boot service must remain Experience-neutral. Physical staging
    # is injected only through the runtime drop-in created by the claim script.
    assert "--experience" not in service
    assert "/run/systemd/system" not in service

    # install_ui ships every handoff script; no parallel display-owner path.
    assert '"$SRC"/display_handoff/*.sh' in installer


def test_release_always_clears_physical_experience_staging_override():
    release = _read("display_handoff/release_display.sh")

    assert "90-beast-experience-test.conf" in release
    assert 'rm -f "$EXPERIENCE_OVERRIDE"' in release
    assert "systemctl daemon-reload" in release

    # Cleanup is outside the BACKUP branch, so even an already-restored or
    # partially failed handoff cannot leave a staging selection behind.
    assert release.index('rm -f "$EXPERIENCE_OVERRIDE"') < release.index('if [[ -f "$BACKUP" ]]')


def test_confirm_clears_staging_before_disarming_rollback():
    confirm = _read("display_handoff/confirm_display.sh")

    assert "90-beast-experience-test.conf" in confirm
    assert 'rm -f "$EXPERIENCE_OVERRIDE"' in confirm
    assert "systemctl daemon-reload" in confirm
    assert "saved/default UI remains authoritative" in confirm

    # A failed daemon-reload must happen while automatic rollback is still
    # armed; only after staging cleanup succeeds may confirmation disarm it.
    assert confirm.index('rm -f "$EXPERIENCE_OVERRIDE"') < confirm.index(
        "systemctl stop beast-display-rollback.timer"
    )


def test_public_acceptance_entrypoint_forwards_experience_without_rewriting_backend():
    entry = _read("tools/v019_acceptance_entrypoint.sh")
    backend = _read("tools/v019_physical_acceptance.sh")
    installer = _read("install_ui.sh")

    assert "BACKEND=/opt/beast-ui/bin/v019_physical_acceptance.sh" in entry
    assert "start [rollback-minutes] [experience] [experience-page]" in entry
    assert 'BEAST_ACCEPT_EXPERIENCE="$experience"' in entry
    assert 'BEAST_ACCEPT_EXPERIENCE_PAGE="$page"' in entry
    assert '"$BACKEND" start "$minutes"' in entry

    # Legacy start remains available when no Experience is supplied.
    assert 'exec "$BACKEND" start "$minutes"' in entry
    assert '"$CLAIM" "$minutes"' in backend

    # Installer keeps the mature harness as a private backend and exposes the
    # small selector wrapper as the owner-facing command.
    assert '"$SRC/tools/v019_physical_acceptance.sh" /opt/beast-ui/bin/v019_physical_acceptance.sh' in installer
    assert '"$SRC/tools/v019_acceptance_entrypoint.sh" /usr/local/bin/beast-v019-accept' in installer
    assert '"$SRC/tools/v019_physical_acceptance.sh" /usr/local/bin/beast-v019-accept' not in installer


def test_experience_acceptance_session_records_exact_staged_target():
    entry = _read("tools/v019_acceptance_entrypoint.sh")

    assert 'experience-staging.json' in entry
    assert '"mode": "staging_only"' in entry
    assert '"experience": os.environ["EXPERIENCE"].strip().lower()' in entry
    assert '"page": os.environ["PAGE"].strip().lower()' in entry
    assert '"saved_ui_preferences_modified": False' in entry
    assert '"permanent_service_modified": False' in entry


def test_acceptance_report_surfaces_exact_staged_experience(tmp_path):
    from tools.v019_acceptance_report import summarize_session, write_text_report

    (tmp_path / "experience-staging.json").write_text(json.dumps({
        "schema": 1,
        "mode": "staging_only",
        "experience": "atlas",
        "page": "home",
        "saved_ui_preferences_modified": False,
        "permanent_service_modified": False,
    }))

    summary = summarize_session(tmp_path)
    staged = summary["experience"]
    assert staged["mode"] == "staging_only"
    assert staged["experience"] == "atlas"
    assert staged["page"] == "home"
    assert staged["saved_ui_preferences_modified"] is False
    assert staged["permanent_service_modified"] is False

    text = write_text_report(summary)
    assert "Experience staging" in text
    assert "target: atlas:home" in text
    assert "saved UI preferences modified: False" in text
    assert "permanent service modified: False" in text
