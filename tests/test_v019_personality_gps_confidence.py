"""Regression test for creature finding F2.

`PersonalityEngine` awarded a +10 confidence bonus when `gps.state == 'locked'`,
but the GPS collector only ever emits `fixed` / `connected_no_fix` / `unavailable`
(`beastcore/collectors/gps.py`). So the bonus was dead code and a real GPS fix
never lifted the Beast's confidence. The fix keys the bonus on `fixed`.
"""
from __future__ import annotations

from beastcore.personality import PersonalityEngine


class FakeState(dict):
    def get(self, key, default=None):
        return dict.get(self, key, default)


def _confidence(gps_state: str) -> int:
    base = {
        "health.core.state": "healthy",
        "governor.mode": "FULL",
        "system.temp.cpu_c": 50.0,
        "pwnagotchi.service.state": "active",
        "bettercap.state": "active",
        "progression.level": 10,
        "gps.state": gps_state,
    }
    engine = PersonalityEngine(FakeState(base), clock=lambda: 0.0)
    return engine.tick()["beast.confidence"]


def test_gps_fixed_grants_the_confidence_bonus():
    # A real fix is worth +10 over having the receiver but no fix.
    assert _confidence("fixed") == _confidence("connected_no_fix") + 10


def test_no_bonus_without_a_fix():
    assert _confidence("unavailable") == _confidence("connected_no_fix")


def test_emitted_fix_state_is_honoured_not_a_phantom_one():
    # The collector never emits 'locked'; a value it does emit must drive the bonus.
    assert _confidence("fixed") > _confidence("connected_no_fix")
