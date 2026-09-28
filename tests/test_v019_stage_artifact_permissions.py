from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_stage_from_artifact_does_not_require_executable_installer_bits():
    script = (ROOT / "tools" / "v019_stage_from_artifact.sh").read_text()

    assert '[[ -f "$SOURCE_ROOT/install.sh" && -f "$SOURCE_ROOT/install_ui.sh" ]]' in script
    assert '[[ -x "$SOURCE_ROOT/install.sh" && -x "$SOURCE_ROOT/install_ui.sh" ]]' not in script
    assert 'bash "$SOURCE_ROOT/install.sh"' in script
    assert 'bash "$SOURCE_ROOT/install_ui.sh"' in script
