"""Creature finding F5: heritage temperament now biases personality behaviour.

Temperament axes are derived in `heritage.py` but, before this change, were read by
nothing at runtime, so every Beast produced identical personality output. Core now
publishes `beast.temperament.<axis>` for the active Beast; `PersonalityEngine`
applies modest biases to the expressed numbers (mood selection is unchanged).
"""
from __future__ import annotations

from beastcore.personality import PersonalityEngine


class FakeState(dict):
    def get(self, key, default=None):
        return dict.get(self, key, default)


BASE = {
    "health.core.state": "healthy",
    "governor.mode": "FULL",
    "system.temp.cpu_c": 50.0,
    "pwnagotchi.service.state": "active",
    "bettercap.state": "active",
    "progression.level": 10,
    "gps.state": "fixed",
    "ambient.day_phase": "day",
    "system.cpu.total": 0.0,
}


def _out(base=None, **temperament):
    state = dict(base or BASE)
    state.update({"beast.temperament." + k: v for k, v in temperament.items()})
    return PersonalityEngine(FakeState(state), clock=lambda: 0.0).tick()


def test_curiosity_axis_shifts_expressed_curiosity():
    assert _out(curiosity=95)["beast.curiosity"] > _out(curiosity=5)["beast.curiosity"]


def test_focus_axis_shifts_expressed_focus():
    assert _out(focus=95)["beast.focus"] > _out(focus=5)["beast.focus"]


def test_bolder_beast_has_more_energy_and_less_stress():
    bold = _out(boldness=95)
    timid = _out(boldness=5)
    assert bold["beast.energy"] > timid["beast.energy"]
    assert bold["beast.stress"] < timid["beast.stress"]


def test_absent_temperament_is_neutral():
    # No temperament keys must behave exactly like an explicit all-50 (neutral) Beast,
    # so Beasts without heritage data keep today's behaviour.
    none = PersonalityEngine(FakeState(dict(BASE)), clock=lambda: 0.0).tick()
    neutral = _out(curiosity=50, focus=50, boldness=50, nocturnal=50, social=50)
    for key in ("beast.curiosity", "beast.focus", "beast.energy", "beast.stress"):
        assert none[key] == neutral[key]


def test_nocturnal_axis_depends_on_day_phase():
    night = dict(BASE, **{"ambient.day_phase": "night"})
    assert _out(night, nocturnal=95)["beast.energy"] > _out(night, nocturnal=5)["beast.energy"]


def test_mood_selection_is_unchanged_by_temperament():
    # Temperament biases the numbers, not which mood is chosen.
    assert _out(curiosity=95, boldness=95)["beast.mood"] == _out(curiosity=5, boldness=5)["beast.mood"]
