from pathlib import Path

from beastui.experience_live import ExperienceBeastUI


def test_runtime_directory_is_writable_by_beast_group_members():
    core = Path("systemd/beast-core.service").read_text()
    ui = Path("ui_systemd/beast-ui.service").read_text()
    studio = Path("ui_systemd/beast-studio.service").read_text()

    assert "RuntimeDirectory=beastagotchi" in core
    assert "RuntimeDirectoryMode=0775" in core
    assert "ExecStartPre=/usr/bin/chgrp beastagotchi /run/beastagotchi" in core
    assert "SupplementaryGroups=video input beastagotchi" in ui
    assert "SupplementaryGroups=beastagotchi" in studio


def test_studio_pythonpath_contains_installed_core():
    studio = Path("ui_systemd/beast-studio.service").read_text()
    assert "Environment=PYTHONPATH=/opt/beast-ui:/opt/beast-core:/opt/beast-python/site-packages" in studio


def test_experience_runtime_owns_idle_cadence():
    ui = ExperienceBeastUI.__new__(ExperienceBeastUI)
    assert ui._background_cadence({}) == 1.0
    assert ui._background_cadence({"pulse_level": "active"}) == 1.0
