import inspect
import re
from pathlib import Path

from beastcore.core import BeastCore
from beastcore.rare import RareMomentEngine


ROOT = Path(__file__).resolve().parents[1]


def test_core_keeps_rare_moment_seed_next_to_its_database(tmp_path):
    core = BeastCore(db_path=str(tmp_path / "beast.db"), port=0)
    try:
        assert core.rare.root == tmp_path / "secrets"
        assert core.rare.secret_path.is_file()
    finally:
        core.store.close()


def test_production_rare_moment_seed_location_is_unchanged():
    # Moving the seed would regenerate it and change the device's rare schedule (ADR-0007).
    unit = (ROOT / "systemd" / "beast-core.service").read_text()
    db_path = re.search(r"--db (\S+)", unit).group(1)
    assert inspect.signature(BeastCore.__init__).parameters["db_path"].default == db_path
    default_root = inspect.signature(RareMomentEngine.__init__).parameters["root"].default
    assert Path(db_path).parent / "secrets" == Path(default_root)
