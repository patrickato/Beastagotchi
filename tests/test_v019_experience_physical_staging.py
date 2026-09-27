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
    assert "ExecStart=" in claim
    assert "--experience $EXPERIENCE --experience-page $EXPERIENCE_PAGE" in claim
    assert "systemctl daemon-reload" in claim

    # The normal boot service must remain Experience-neutral. Physical staging
    # is injected only through the runtime drop-in created by the claim script.
    assert "--experience" not in service
    assert "/run/systemd/system" not in service

    # install_ui already ships every handoff script; no parallel install path.
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
