from beastcore.db import Store


def test_meta_json_round_trip_and_change_gate(tmp_path):
    store = Store(str(tmp_path / "beast.db"))
    try:
        assert store.get_meta_json("doctor.patient", {"empty": True}) == {"empty": True}
        assert store.set_meta_json("doctor.patient", {"schema": 1, "value": 7}) is True
        assert store.get_meta_json("doctor.patient") == {"schema": 1, "value": 7}
        # Identical content should not cause another durable write.
        assert store.set_meta_json("doctor.patient", {"value": 7, "schema": 1}) is False
        assert store.set_meta_json("doctor.patient", {"schema": 1, "value": 8}) is True
        assert store.get_meta_json("doctor.patient")["value"] == 8
    finally:
        store.close()


def test_meta_json_malformed_value_falls_back_safely(tmp_path):
    store = Store(str(tmp_path / "beast.db"))
    try:
        with store.conn:
            store.conn.execute(
                "INSERT OR REPLACE INTO meta(key,value) VALUES(?,?)",
                ("doctor.patient", "{not-json"),
            )
        assert store.get_meta_json("doctor.patient", {"safe": True}) == {"safe": True}
    finally:
        store.close()
