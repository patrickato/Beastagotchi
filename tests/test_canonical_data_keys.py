"""Drift guard for the consolidated canonical data-key spec (v7).

v1-v6 fragmented the canonical state keys across six files (three full snapshots, then three
delta files) that nothing in code loaded, so the spec silently drifted from the machine. v7 is
the single consolidated spec; these tests keep it well-formed and -- crucially -- tie its
`beast.*` namespace to the keys Beast Core's `PersonalityEngine` actually emits, so the spec can
no longer claim a Beast state the code does not produce (ADR-0008 live-truth; ADR-0009 the
temperament contract).
"""
from __future__ import annotations

import json
from pathlib import Path

from beastcore.personality import PersonalityEngine

ROOT = Path(__file__).resolve().parents[1]
SPEC = json.loads((ROOT / "docs" / "Beastagotchi_Canonical_Data_Keys_v7.json").read_text())
NAMESPACES = SPEC["namespaces"]


class FakeState(dict):
    def get(self, key, default=None):
        return dict.get(self, key, default)


def test_spec_is_v7_and_wellformed():
    assert SPEC["schema_version"] == 7
    assert isinstance(NAMESPACES, dict) and NAMESPACES
    # Every key lives under its namespace (namespace == first dotted segment).
    for ns, keys in NAMESPACES.items():
        assert isinstance(keys, list) and keys, ns
        for k in keys:
            assert k.split(".", 1)[0] == ns, f"{k} is not under namespace {ns}"


def test_prior_namespaces_are_covered():
    # v3's full-snapshot namespaces plus the v4/v5/v6 additions must all survive consolidation.
    expected = {
        "system", "storage", "radio", "wifi", "captures", "gps", "pwnagotchi", "bettercap",
        "beast", "platform", "context", "health", "history", "session",   # v1-v3
        "power", "dock", "network", "capabilities", "plugins",            # v4
        "progression",                                                    # v5
        "rare", "ambient", "celestial",                                   # v6
    }
    assert expected <= set(NAMESPACES)


def test_beast_namespace_matches_personality_engine_output():
    # The north-star guard: every beast.* key the engine actually emits must be documented in v7,
    # so the canonical spec can never again describe a Beast the code does not produce.
    base = {
        "health.core.state": "healthy", "governor.mode": "FULL", "system.temp.cpu_c": 50.0,
        "pwnagotchi.service.state": "active", "bettercap.state": "active",
        "progression.level": 10, "gps.state": "fixed", "ambient.day_phase": "day",
    }
    emitted = PersonalityEngine(FakeState(base), clock=lambda: 0.0).tick()
    beast_keys = {k for k in emitted if k.startswith("beast.")}
    assert beast_keys, "engine emitted no beast.* keys?"
    missing = beast_keys - set(NAMESPACES.get("beast", []))
    assert not missing, f"emitted beast.* keys missing from v7 spec: {sorted(missing)}"


def test_temperament_contract_is_documented():
    # ADR-0009: the beast.temperament.* contract (five axes) is part of the canonical spec.
    beast = set(NAMESPACES.get("beast", []))
    for axis in ("curiosity", "social", "focus", "boldness", "nocturnal"):
        assert f"beast.temperament.{axis}" in beast


def test_retired_keys_are_documented_not_silently_dropped():
    # Keys the code stopped emitting are recorded with a reason (ADR-0007), not deleted without a
    # trace, and must not reappear among the live namespaces.
    retired = SPEC.get("retired_keys", {})
    assert {"beast.boredom", "beast.current_expression", "beast.current_animation"} <= set(retired)
    all_keys = {k for keys in NAMESPACES.values() for k in keys}
    assert not (set(retired) & all_keys), "a retired key is still listed as live"
