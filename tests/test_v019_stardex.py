"""Creature idea 11 increment 2: the StarDex -- a persistent, live-honest collection of satellite PRNs.

Each real PRN gpsd reports in a SKY skyview (surfaced as gps.satellites[] by #59) is a lifetime collectible.
A discovery is a PRN never caught before. These tests lock in the persistence, the lifetime-first signal
(for discovery XP, increment 3), the best-SNR high-water mark, and the live-honest handling of an absent
skyview / missing fields (ADR-0008).
"""
from __future__ import annotations

from beastcore.db import Store
from beastcore.stardex import StarDex


def sat(prn, snr=None, gnssid=None, el=None, az=None, used=False):
    # One gps.satellites[] entry in the shape GPSCollector._satellites emits.
    return {"prn": prn, "elevation_deg": el, "azimuth_deg": az,
            "snr_dbhz": snr, "used": used, "gnssid": gnssid}


def test_first_catch_is_new_repeat_is_not(tmp_path):
    dex = StarDex(Store(str(tmp_path / "beast.db")), clock=lambda: 100.0)
    a = dex.observe([sat(5), sat(12)], ts=100.0)
    assert a["accepted"] is True
    assert sorted(a["new_prns"]) == [5, 12] and a["new_count"] == 2
    b = dex.observe([sat(5), sat(12)], ts=200.0)
    assert b["new_prns"] == [] and b["new_count"] == 0       # already in the collection
    assert b["catch_count"] == 2
    assert dex.summary()["stardex.total_prns"] == 2


def test_discovery_only_the_genuinely_new_prn(tmp_path):
    dex = StarDex(Store(str(tmp_path / "beast.db")), clock=lambda: 0.0)
    dex.observe([sat(5), sat(12)], ts=100.0)
    out = dex.observe([sat(5), sat(30)], ts=200.0)              # 30 is new, 5 is not
    assert out["new_prns"] == [30]
    assert dex.summary()["stardex.total_prns"] == 3


def test_first_seen_preserved_last_seen_and_events_advance(tmp_path):
    dex = StarDex(Store(str(tmp_path / "beast.db")))
    dex.observe([sat(7)], ts=100.0)
    dex.observe([sat(7)], ts=250.0)
    row = dex.recent(1)[0]
    assert row["prn"] == 7
    assert row["first_seen"] == 100.0          # preserved from the first catch
    assert row["last_seen"] == 250.0           # advances
    assert row["seen_events"] == 2


def test_best_snr_is_a_high_water_mark(tmp_path):
    dex = StarDex(Store(str(tmp_path / "beast.db")))
    dex.observe([sat(5, snr=22.0)], ts=100.0)
    dex.observe([sat(5, snr=41.0)], ts=200.0)   # stronger -> raises the record
    dex.observe([sat(5, snr=30.0)], ts=300.0)   # weaker -> record stays
    assert dex.recent(1)[0]["best_snr_dbhz"] == 41.0
    assert dex.summary()["stardex.best_snr_dbhz"] == 41.0


def test_missing_snr_leaves_best_none(tmp_path):
    dex = StarDex(Store(str(tmp_path / "beast.db")))
    dex.observe([sat(5)], ts=100.0)                      # gpsd sent no ss -> snr None
    assert dex.recent(1)[0]["best_snr_dbhz"] is None
    assert dex.summary()["stardex.best_snr_dbhz"] is None


def test_gnssid_stored_and_kept_when_later_omitted(tmp_path):
    dex = StarDex(Store(str(tmp_path / "beast.db")))
    dex.observe([sat(5, gnssid=0)], ts=100.0)
    assert dex.recent(1)[0]["gnssid"] == 0
    dex.observe([sat(5, gnssid=None)], ts=200.0)         # a later skyview omits gnssid
    assert dex.recent(1)[0]["gnssid"] == 0               # keep the known value, don't wipe it


def test_absent_skyview_records_nothing(tmp_path):
    dex = StarDex(Store(str(tmp_path / "beast.db")))
    out = dex.observe(None)                              # gps.satellites unavailable/unknown
    assert out["accepted"] is False and out["new_prns"] == []
    assert dex.summary()["stardex.total_prns"] == 0


def test_empty_sky_is_accepted_but_catalogs_nothing(tmp_path):
    dex = StarDex(Store(str(tmp_path / "beast.db")))
    out = dex.observe([])                                # a genuinely empty sky (distinct from None)
    assert out["accepted"] is True and out["catch_count"] == 0
    assert dex.summary()["stardex.total_prns"] == 0


def test_malformed_entries_are_skipped(tmp_path):
    dex = StarDex(Store(str(tmp_path / "beast.db")))
    out = dex.observe([sat(5), {"no": "prn"}, "notadict", sat(None), sat(0), sat(True)], ts=100.0)
    assert out["new_prns"] == [5]                        # only the real positive-int PRN is cataloged
    assert dex.summary()["stardex.total_prns"] == 1


def test_fractional_prn_is_rejected_not_truncated(tmp_path):
    # A malformed fractional PRN (e.g. 5.9) must not be truncated to 5 -- that would catalog a wrong
    # satellite and pre-empt the real PRN 5's later discovery. An integral float (12.0) is still a valid PRN.
    dex = StarDex(Store(str(tmp_path / "beast.db")))
    assert dex.observe([sat(5.9)], ts=100.0)["new_prns"] == []      # fractional -> not cataloged
    assert dex.summary()["stardex.total_prns"] == 0
    assert dex.observe([sat(5)], ts=200.0)["new_prns"] == [5]       # the genuine PRN 5 is still a discovery
    assert dex.observe([sat(12.0)], ts=300.0)["new_prns"] == [12]   # integral float accepted as PRN 12


def test_empty_collection_reports_unavailable_not_zero(tmp_path):
    # A new StarDex has caught nothing: last_caught_at / best_snr must be unavailable (None), never a
    # fabricated 0 a consumer could not tell from a real timestamp / signal (ADR-0008). total is a real 0.
    s = StarDex(Store(str(tmp_path / "beast.db"))).summary()
    assert s["stardex.total_prns"] == 0
    assert s["stardex.last_caught_at"] is None
    assert s["stardex.best_snr_dbhz"] is None
    assert s["stardex.recent"] == []


def test_duplicate_prn_in_one_skyview_counts_once_keeps_max_snr(tmp_path):
    # A multiband receiver may report one satellite several times in a SKY (different sigid). Count the catch
    # once, but keep the STRONGEST SNR across those records -- discarding the later ones would understate it.
    dex = StarDex(Store(str(tmp_path / "beast.db")))
    out = dex.observe([sat(5, snr=20.0), sat(5, snr=44.0)], ts=100.0)
    assert out["new_prns"] == [5] and out["catch_count"] == 1
    row = dex.recent(1)[0]
    assert row["seen_events"] == 1                       # one observation of PRN 5, not two
    assert row["best_snr_dbhz"] == 44.0                  # max across the duplicate records, not the first


def test_recent_orders_by_last_seen(tmp_path):
    dex = StarDex(Store(str(tmp_path / "beast.db")))
    dex.observe([sat(5)], ts=100.0)
    dex.observe([sat(12)], ts=300.0)
    dex.observe([sat(9)], ts=200.0)
    assert [r["prn"] for r in dex.recent(3)] == [12, 9, 5]


def test_summary_reports_lifetime_totals(tmp_path):
    dex = StarDex(Store(str(tmp_path / "beast.db")), clock=lambda: 0.0)
    dex.observe([sat(5, snr=33.0), sat(12, snr=40.0)], ts=150.0)
    s = dex.summary()
    assert s["stardex.total_prns"] == 2
    assert s["stardex.last_caught_at"] == 150.0
    assert s["stardex.best_snr_dbhz"] == 40.0
    assert len(s["stardex.recent"]) == 2


def test_persists_across_reopen(tmp_path):
    path = str(tmp_path / "beast.db")
    StarDex(Store(path)).observe([sat(5), sat(12)], ts=100.0)
    # a fresh Store/StarDex over the same DB file sees the lifetime collection
    reopened = StarDex(Store(path))
    assert reopened.summary()["stardex.total_prns"] == 2
    assert reopened.observe([sat(5)], ts=200.0)["new_prns"] == []   # 5 already cataloged before reopen
