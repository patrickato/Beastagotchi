import json

import pytest

from beastcore.capsules import BeastCapsuleCodec, BeastCapsuleEngine, CapsuleError
from beastcore.db import Store
from beastcore.roster import BeastRoster
from beastcore.packs import clean_manifest, PackManifestError


def test_capsule_codec_roundtrip_and_qr_frames_are_order_independent():
    envelope = BeastCapsuleCodec.build(
        "lineage",
        {
            "format": "lineage_v1",
            "creature_id": "creature-abc123",
            "name": "Test Beast",
            "generation": 2,
        },
        created_at=123.0,
        capsule_id="capsule-test",
        producer={"name": "Beastagotchi", "version": "test"},
    )
    encoded = BeastCapsuleCodec.encode(envelope)
    decoded = BeastCapsuleCodec.decode(encoded)

    assert decoded == envelope
    assert decoded["integrity"]["authenticated"] is False
    assert decoded["integrity"]["algorithm"] == "sha256"

    frames = BeastCapsuleCodec.qr_frames(encoded, max_frame_chars=160)
    assert len(frames) > 1
    rebuilt = BeastCapsuleCodec.reassemble_qr_frames(list(reversed(frames)))
    assert rebuilt == encoded
    assert BeastCapsuleCodec.decode(rebuilt)["payload"]["name"] == "Test Beast"


def test_capsule_qr_frame_tampering_is_detected():
    envelope = BeastCapsuleCodec.build(
        "lineage",
        {"format": "lineage_v1", "creature_id": "creature-abc"},
        created_at=1.0,
    )
    encoded = BeastCapsuleCodec.encode(envelope)
    frames = BeastCapsuleCodec.qr_frames(encoded, max_frame_chars=150)
    bits = frames[0].split("|", 5)
    assert len(bits) == 6
    part = bits[5]
    replacement = ("A" if part[:1] != "A" else "B") + part[1:]
    frames[0] = "|".join(bits[:5] + [replacement])

    with pytest.raises(CapsuleError, match="checksum"):
        BeastCapsuleCodec.reassemble_qr_frames(frames)


def test_lineage_capsule_is_privacy_curated_and_preview_only(tmp_path):
    store = Store(str(tmp_path / "beast.db"))
    try:
        roster = BeastRoster(store, legacy_profile_path=tmp_path / "missing-profile.json", clock=lambda: 100.0)
        founder = roster.bootstrap_founder(name="Founder")
        child = roster.create_beast(
            "Child",
            lineage_id="test.lineage",
            identity={"secret_identity_note": "do-not-export"},
            appearance={"traits": {"eyes": "amber", "horns": 2}, "mutation": "spark", "private": "omit"},
            preferences={"secret_pref": "do-not-export"},
        )
        with store.conn:
            store.conn.execute(
                "INSERT INTO beast_ancestry(child_id,parent_id,parent_role) VALUES(?,?,?)",
                (child["id"], founder["id"], "parent_a"),
            )
            store.conn.execute(
                "INSERT INTO beast_achievements(beast_id,achievement_id,unlocked_at,context_json) VALUES(?,?,?,?)",
                (child["id"], "achievement.hidden-test", 100.0, "{}"),
            )

        engine = BeastCapsuleEngine(store, roster, beast_version="0.19-test", clock=lambda: 200.0)
        exported = engine.export_lineage(child["id"], qr_max_chars=180)
        payload = exported["envelope"]["payload"]
        raw = json.dumps(exported["envelope"], sort_keys=True)

        assert payload["format"] == "lineage_v1"
        assert payload["creature_id"].startswith("creature-")
        assert payload["parents"] and payload["parents"][0].startswith("creature-")
        assert payload["name"] == "Child"
        assert payload["appearance"] == {"traits": {"eyes": "amber", "horns": 2}, "mutation": "spark"}
        assert payload["achievement_count"] == 1
        assert "achievements" not in payload
        assert child["id"] not in raw
        assert founder["id"] not in raw
        assert "secret_identity_note" not in raw
        assert "secret_pref" not in raw
        assert "do-not-export" not in raw
        assert "counters" not in raw
        assert '"xp"' not in raw
        assert exported["envelope"]["privacy"]["credentials_included"] is False
        assert exported["envelope"]["privacy"]["captures_included"] is False
        assert exported["envelope"]["privacy"]["exact_location_included"] is False
        assert exported["import_performed"] is False
        assert exported["qr"]["frame_count"] >= 1
        assert exported["qr"]["renderer_bundled"] is False

        inspected = engine.inspect(exported["encoded"])
        assert inspected["ok"] is True
        assert inspected["import_supported"] is False
        assert inspected["import_performed"] is False
        assert inspected["payload"]["creature_id"] == payload["creature_id"]
    finally:
        store.close()


def test_lineage_capsule_public_identity_is_stable_but_local_only_namespace(tmp_path):
    store = Store(str(tmp_path / "beast.db"))
    try:
        roster = BeastRoster(store, legacy_profile_path=tmp_path / "missing-profile.json")
        beast = roster.bootstrap_founder(name="Founder")
        engine = BeastCapsuleEngine(store, roster)

        first = engine.lineage_payload(beast["id"])
        second = engine.lineage_payload(beast["id"])
        namespace = engine.namespace_id(create=False)

        assert namespace and namespace.startswith("capsulepub-")
        assert first["creature_id"] == second["creature_id"]
        assert first["creature_id"] != beast["id"]
    finally:
        store.close()


def test_lineage_capsule_can_include_achievement_ids_only_when_explicit(tmp_path):
    store = Store(str(tmp_path / "beast.db"))
    try:
        roster = BeastRoster(store, legacy_profile_path=tmp_path / "missing-profile.json")
        beast = roster.bootstrap_founder(name="Founder")
        with store.conn:
            store.conn.execute(
                "INSERT INTO beast_achievements(beast_id,achievement_id,unlocked_at,context_json) VALUES(?,?,?,?)",
                (beast["id"], "achievement.public-test", 1.0, '{"private_context":"not exported"}'),
            )
        engine = BeastCapsuleEngine(store, roster)

        hidden = engine.export_lineage(beast["id"], include_achievements=False)
        shown = engine.export_lineage(beast["id"], include_achievements=True)

        assert "achievements" not in hidden["envelope"]["payload"]
        assert shown["envelope"]["payload"]["achievements"] == ["achievement.public-test"]
        assert "private_context" not in json.dumps(shown["envelope"])
    finally:
        store.close()


def test_pack_manifest_supports_companion_expansion_metadata_without_new_pack_type():
    row = clean_manifest({
        "id": "expedition-companion",
        "label": "Expedition Companion",
        "version": "1",
        "pack_type": "integration",
        "extension_class": "companion",
        "content_roles": ["achievement_catalog", "widget_bundle", "capsule_schema"],
        "signals_provides": ["gps.fix.changed", "expedition.completed"],
        "signals_consumes": ["peer.detected"],
        "offline_transports": ["qr", "file", "nfc"],
        "capsule_types": ["lineage", "challenge"],
        "companion": {
            "pwnagotchi_plugins": ["beast_expedition_bridge"],
            "beast_apps": ["expedition-studio"],
            "beast_packs": ["expedition-achievements"],
        },
    })

    assert row["pack_type"] == "integration"
    assert row["extension_class"] == "companion"
    assert "achievement_catalog" in row["content_roles"]
    assert row["companion"]["pwnagotchi_plugins"] == ["beast_expedition_bridge"]
    assert row["capsule_types"] == ["lineage", "challenge"]


def test_pack_manifest_rejects_unknown_extension_class():
    with pytest.raises(PackManifestError, match="extension_class"):
        clean_manifest({
            "id": "bad-extension",
            "label": "Bad Extension",
            "pack_type": "integration",
            "extension_class": "mystery",
        })
