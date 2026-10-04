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


def test_in_memory_core_keeps_its_rare_moment_seed_out_of_the_working_directory(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    core = BeastCore(db_path=":memory:", port=0)
    try:
        assert core.rare.secret_path.is_file()
        assert not (tmp_path / "secrets").exists()
        assert not core.rare.root.is_relative_to(Path("/var/lib/beastagotchi"))
    finally:
        core.store.close()


def test_production_rare_moment_seed_location_is_unchanged():
    # Moving the seed would regenerate it and change the device's rare schedule (ADR-0007).
    unit = (ROOT / "systemd" / "beast-core.service").read_text()
    db_path = re.search(r"--db (\S+)", unit).group(1)
    assert inspect.signature(BeastCore.__init__).parameters["db_path"].default == db_path
    default_root = inspect.signature(RareMomentEngine.__init__).parameters["root"].default
    assert Path(db_path).parent / "secrets" == Path(default_root)


def test_health_watchdog_ages_engine_loop_sources(tmp_path):
    # Engine loops (context, governor) publish their keys directly, not through a registered collector, so
    # only the health watchdog can age them. Prove the watchdog marks those sources stale once they stop
    # refreshing -- this is what makes PersonalityEngine/NeedsEngine's `_live` reads honest in production
    # (ADR-0008), rather than relying on synthetic test metadata. `health` is deliberately NOT aged: it is
    # produced by the watchdog loop itself and cannot observe its own staleness.
    core = BeastCore(db_path=str(tmp_path / "beast.db"), port=0)
    try:
        core.state.update_many("context", {"context.motion.state": "walking"}, priority=90)
        core.state.update_many("governor", {"governor.mode": "SURVIVAL"}, priority=96)
        core.state.update_many("health", {"health.core.state": "critical"}, priority=100)

        core._age_engine_sources()                       # fresh values -> left live
        assert core.state.meta("context.motion.state")["quality"] == "live"
        assert core.state.meta("governor.mode")["quality"] == "live"

        for key in ("context.motion.state", "governor.mode", "health.core.state"):
            core.state._values[key].updated_at -= 3600.0  # simulate every loop stalling long ago
        core._age_engine_sources()
        assert core.state.meta("context.motion.state")["quality"] == "stale"   # aged
        assert core.state.meta("governor.mode")["quality"] == "stale"          # aged
        assert core.state.meta("health.core.state")["quality"] == "live"       # watchdog never ages itself
    finally:
        core.store.close()
