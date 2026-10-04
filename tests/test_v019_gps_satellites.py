"""Creature idea 11, increment 1: the GPS collector surfaces gpsd's per-satellite SKY detail (F4).

`GPSCollector._satellites` normalizes the raw gpsd SKY `satellites` list into the canonical skyplot
(`gps.satellites`) instead of discarding it. Faithful + live-honest (ADR-0008): only entries with a
real PRN are kept, only the fields gpsd actually sent are carried (a missing one stays None, never
fabricated), and `used` is coerced to a real bool.
"""
from __future__ import annotations

from beastcore.collectors.gps import GPSCollector


def test_satellites_normalizes_gpsd_records():
    raw = [
        {"PRN": 5, "el": 42, "az": 310, "ss": 38, "used": True, "gnssid": 0},
        {"PRN": 29, "el": 7, "az": 150, "ss": 21, "used": False},
    ]
    assert GPSCollector._satellites(raw) == [
        {"prn": 5, "elevation_deg": 42, "azimuth_deg": 310, "snr_dbhz": 38, "used": True, "gnssid": 0},
        {"prn": 29, "elevation_deg": 7, "azimuth_deg": 150, "snr_dbhz": 21, "used": False, "gnssid": None},
    ]


def test_missing_fields_stay_none_not_fabricated():
    # A satellite gpsd reports with only a PRN keeps el/az/ss as None, never guessed.
    assert GPSCollector._satellites([{"PRN": 12}]) == [
        {"prn": 12, "elevation_deg": None, "azimuth_deg": None, "snr_dbhz": None, "used": False, "gnssid": None},
    ]


def test_entries_without_a_prn_or_malformed_are_dropped():
    raw = [{"el": 40, "az": 90}, "nonsense", None, {"PRN": 7, "el": 10}]
    assert [s["prn"] for s in GPSCollector._satellites(raw)] == [7]


def test_non_list_input_is_empty():
    assert GPSCollector._satellites(None) == []
    assert GPSCollector._satellites({}) == []


def test_used_is_coerced_to_a_real_bool():
    out = GPSCollector._satellites([{"PRN": 3, "used": 1}, {"PRN": 4, "used": 0}])
    assert out[0]["used"] is True
    assert out[1]["used"] is False
