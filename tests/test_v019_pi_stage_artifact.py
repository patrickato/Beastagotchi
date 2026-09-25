from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(rel: str) -> str:
    return (ROOT / rel).read_text()


def test_core_installer_preserves_existing_beast_config_on_upgrade():
    text = _read("install.sh")
    assert "if [[ -f /etc/beastagotchi/core.toml ]]" in text
    assert "Preserving existing Beast Core configuration" in text
    assert 'install -m 0644 "$SRC/config/core.toml" /etc/beastagotchi/core.toml' in text


def test_pi_stage_wrapper_verifies_provenance_before_install():
    text = _read("tools/v019_stage_from_artifact.sh")
    verify = text.index('sha256sum -c')
    source = text.index('SOURCE_SHA=')
    extract = text.index('tar -xzf')
    install_core = text.index('"$SOURCE_ROOT/install.sh"')
    install_ui = text.index('"$SOURCE_ROOT/install_ui.sh"')
    assert verify < extract < install_core < install_ui
    assert source < extract
    assert 'SOURCE_COMMIT_SHA.txt' in text
    assert 'CI_TESTED_SHA.txt' in text
    assert 'Beastagotchi-v019-$SHORT' in text


def test_pi_stage_wrapper_never_claims_or_confirms_display():
    text = _read("tools/v019_stage_from_artifact.sh")
    assert "claim_display_test.sh" not in text
    assert "confirm_display.sh" not in text
    assert "beast-v019-accept start 15" in text
    assert "Display claimed: NO" in text
    assert "Physical display ownership remains with Pwnagotchi" in text


def test_pi_stage_wrapper_keeps_optional_qr_out_of_pwnagotchi_environment():
    text = _read("tools/v019_stage_from_artifact.sh")
    assert "--prepare-qr" in text
    assert "beast-v019-accept prepare-qr" in text
    assert "/opt/.pwn site-packages" in text
    assert "does not modify Pwnagotchi" in text or "Pwnagotchi's /opt/.pwn" in text


def test_pi_stage_wrapper_starts_core_but_not_ui():
    text = _read("tools/v019_stage_from_artifact.sh")
    assert "systemctl start beast-core.service" in text
    assert "systemctl start beast-ui.service" not in text
    assert "systemctl enable beast-ui.service" not in text


def test_ci_artifact_contains_staging_wrapper_quickstart_and_source_metadata():
    text = _read(".github/workflows/tests.yml")
    assert "v019-pi-acceptance-source" in text
    assert 'SOURCE_COMMIT_SHA.txt' in text
    assert 'CI_TESTED_SHA.txt' in text
    assert 'STAGE_ON_PI.sh' in text
    assert 'PHYSICAL_TEST_QUICKSTART.txt' in text
    assert 'tools/v019_stage_from_artifact.sh' in text
    assert 'Beastagotchi_v019_Physical_Acceptance_Quickstart.txt' in text


def test_quickstart_keeps_staging_and_display_claim_as_separate_decisions():
    text = _read("docs/Beastagotchi_v019_Physical_Acceptance_Quickstart.txt")
    assert "sudo ./STAGE_ON_PI.sh --prepare-qr" in text
    assert "Staging does NOT claim the TFT" in text
    assert "sudo beast-v019-accept start 15" in text
    assert "sudo beast-v019-accept sample 60" in text
    assert "sudo beast-v019-accept finish observe" in text
    assert "sudo beast-v019-accept finish rollback" in text

def test_pi_stage_wrapper_preserves_local_beast_database_before_starting_new_core():
    text = _read("tools/v019_stage_from_artifact.sh")
    backup = text.index('src=sqlite3.connect("/var/lib/beastagotchi/beast.db"')
    install_core = text.index('"$SOURCE_ROOT/install.sh"')
    start_core = text.index("systemctl start beast-core.service")
    assert backup < install_core < start_core
    assert 'BACKUP_DB="$SESSION/beast.db.before"' in text
    assert 'chmod 0600 "$SESSION/beast.db.before"' in text


def test_pi_stage_archive_root_probe_avoids_head_pipefail_trap():
    text = _read("tools/v019_stage_from_artifact.sh")
    assert "tar -tzf" in text
    assert "| head -n1" not in text
    assert "awk -F/ 'NR==1{first=$1} END{print first}'" in text

