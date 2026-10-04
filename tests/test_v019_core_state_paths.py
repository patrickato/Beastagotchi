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


def test_stardex_step_catalogs_only_a_live_skyview(tmp_path):
    # The StarDex loop records the currently-visible satellites, but only while gps.satellites is LIVE:
    # a stalled GPS collector's retained list must not keep re-logging catches off stale data (ADR-0008).
    core = BeastCore(db_path=str(tmp_path / "beast.db"), port=0)
    try:
        sats = [{"prn": 5, "snr_dbhz": 30.0, "gnssid": 0, "elevation_deg": 40,
                 "azimuth_deg": 120, "used": True}]
        # A live skyview is cataloged and the summary is published.
        core.state.update_many("gps", {"gps.satellites": sats}, priority=70)
        core._stardex_step()
        assert core.state.get("stardex.total_prns") == 1
        assert core.stardex.summary()["stardex.total_prns"] == 1

        # The same list gone stale is a no-op -- no new catch, no re-log.
        core.state.update_many("gps", {"gps.satellites": [{"prn": 9}]}, priority=70)
        core.state.mark_source_stale("gps", 0.0)
        core._stardex_step()
        assert core.stardex.summary()["stardex.total_prns"] == 1   # PRN 9 not cataloged (stale skyview)
    finally:
        core.store.close()


def test_stardex_step_is_shed_under_survival_governor(tmp_path):
    # Optional cataloging the thermal governor can shed (AGENTS.md): under SURVIVAL the step does no SQLite
    # work at all, even with a live skyview.
    core = BeastCore(db_path=str(tmp_path / "beast.db"), port=0)
    try:
        core.state.update_many("gps", {"gps.satellites": [{"prn": 5}]}, priority=70)
        core.state.update_many("governor", {"governor.mode": "SURVIVAL"}, priority=96)
        core._stardex_step()
        assert core.stardex.summary()["stardex.total_prns"] == 0   # shed: nothing cataloged
        # back to FULL -> cataloging resumes
        core.state.update_many("governor", {"governor.mode": "FULL"}, priority=96)
        core._stardex_step()
        assert core.stardex.summary()["stardex.total_prns"] == 1
    finally:
        core.store.close()


def test_stardex_step_marks_namespace_stale_on_persistence_failure(tmp_path):
    # If a runtime SQLite op fails, stardex.* must not keep looking live/current: the step marks the
    # namespace stale so consumers see it stopped updating (ADR-0008), rather than only logging.
    core = BeastCore(db_path=str(tmp_path / "beast.db"), port=0)
    try:
        core.state.update_many("gps", {"gps.satellites": [{"prn": 5}]}, priority=70)
        core._stardex_step()
        assert core.state.meta("stardex.total_prns")["quality"] == "live"
        def boom(*a, **k):
            raise RuntimeError("database is locked")
        core.stardex.observe = boom                      # simulate a persistence failure
        core._stardex_step()
        assert core.state.meta("stardex.total_prns")["quality"] == "stale"
    finally:
        core.store.close()
