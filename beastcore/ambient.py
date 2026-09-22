from __future__ import annotations

import math
import time
from datetime import datetime


def _moon_phase_name(ts: float) -> tuple[str, float]:
    # Simple, dependency-free synodic approximation. Good enough for ambient UI
    # context; not intended for navigation/astronomy measurements.
    synodic = 29.53058867
    known_new_moon = 947182440.0  # 2000-01-06T18:14Z
    age = ((ts - known_new_moon) / 86400.0) % synodic
    frac = age / synodic
    names = [
        (0.03,'new'),(0.22,'waxing_crescent'),(0.28,'first_quarter'),
        (0.47,'waxing_gibbous'),(0.53,'full'),(0.72,'waning_gibbous'),
        (0.78,'last_quarter'),(0.97,'waning_crescent'),(1.01,'new')
    ]
    name='new'
    for limit,label in names:
        if frac <= limit:
            name=label; break
    illumination = 0.5 * (1 - math.cos(2 * math.pi * frac))
    return name, illumination * 100.0


def _season(month: int, latitude: float | None) -> str:
    north = latitude is None or latitude >= 0
    if month in (12,1,2): s='winter'
    elif month in (3,4,5): s='spring'
    elif month in (6,7,8): s='summer'
    else: s='autumn'
    if north:return s
    return {'winter':'summer','spring':'autumn','summer':'winter','autumn':'spring'}[s]


class AmbientContextEngine:
    """Low-cost calendar/celestial context used by visual themes.

    Weather is intentionally not guessed. Online weather or sensor-backed weather
    can plug into the same namespace later.
    """
    def __init__(self, state):
        self.state=state

    def tick(self, now: float | None = None) -> dict:
        now=float(now if now is not None else time.time())
        dt=datetime.fromtimestamp(now)
        lat=self.state.get('gps.latitude')
        try:lat=float(lat) if lat is not None else None
        except Exception:lat=None
        moon,illum=_moon_phase_name(now)
        hour=dt.hour + dt.minute/60.0
        if 5 <= hour < 7: day='dawn'
        elif 7 <= hour < 18: day='day'
        elif 18 <= hour < 20: day='dusk'
        else: day='night'
        return {
            'ambient.season': _season(dt.month,lat),
            'ambient.day_phase': day,
            'ambient.month': dt.month,
            'ambient.day': dt.day,
            'ambient.weekday': dt.strftime('%A').lower(),
            'celestial.moon.phase': moon,
            'celestial.moon.illumination_pct': round(illum,1),
            'ambient.weather.source': 'unavailable',
        }
