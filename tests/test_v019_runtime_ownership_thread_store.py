from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from beastcore.core import BeastCore
from beastcore.roster import BeastRoster
from beastcore.thread_store import ThreadBoundStore


def test_thread_bound_store_uses_distinct_same_thread_connections(tmp_path):
    store = ThreadBoundStore(str(tmp_path / "threaded.db"))
    roster = BeastRoster(store, legacy_profile_path=tmp_path / "missing.json", clock=lambda: 1000.0)
    founder = roster.bootstrap_founder(name="Hex")
    main_connection = store.current_connection_identity()

    def worker():
        worker_connection = store.current_connection_identity()
        created = roster.create_beast("Orbit", lineage_id="starcore")
        # The roster cached store.conn on the main thread. This call proves that
        # cached object is a thread-bound proxy rather than the main connection.
        snapshot = roster.get(created["id"])
        store.release_thread_connection()
        return worker_connection, snapshot

    with ThreadPoolExecutor(max_workers=1) as pool:
        worker_connection, orbit = pool.submit(worker).result(timeout=10)

    assert worker_connection != main_connection
    assert orbit["name"] == "Orbit"
    assert roster.get(founder["id"])["name"] == "Hex"
    assert roster.get(orbit["id"])["lineage_id"] == "starcore"
    store.close()


def test_core_action_broker_uses_core_owned_stateful_managers(tmp_path):
    core = BeastCore(str(tmp_path / "beast.db"))
    try:
        assert core.actions.roster is core.roster
        assert core.actions.global_sync is core.global_sync
        assert core.actions.memories is core.memories
        assert core.global_sync.roster is core.roster
        assert core.memories.roster is core.roster
    finally:
        core.store.close()


def test_worker_roster_action_updates_the_same_core_roster(tmp_path):
    core = BeastCore(str(tmp_path / "beast.db"))
    try:
        founder = core.roster.bootstrap_founder(name="Hex")
        orbit = core.roster.create_beast("Orbit", lineage_id="starcore")

        with ThreadPoolExecutor(max_workers=1) as pool:
            row = pool.submit(
                core.action_server._run_broker_call,
                core.actions.perform,
                "roster.switch",
                {"id": orbit["id"]},
                actor="test-worker",
            ).result(timeout=10)

        assert row["status"] == "success"
        assert row["result"]["active"]["id"] == orbit["id"]
        assert core.roster.active()["id"] == orbit["id"]
        assert core.roster.get(founder["id"])["active"] is False
    finally:
        core.store.close()
