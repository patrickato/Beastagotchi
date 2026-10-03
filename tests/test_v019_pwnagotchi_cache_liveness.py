"""Collector-boundary live-truth for the handshake cache (PR #50 review).

captures.cache_present and captures.total must come from the same scan, and presence must mean a
*complete* scan: a cache dir that stats as present but fails to enumerate is an incomplete scan, not a
readable-empty cache, so it must not become a trustworthy zero baseline a later recovery reads as new
captures (ADR-0008).
"""
from __future__ import annotations

from beastcore.collectors.pwnagotchi import PwnagotchiCollector


class _UnreadableCache:
    def is_dir(self):
        return True

    def glob(self, _pattern):
        raise OSError("directory traversal failed")


class _DirStub:
    """Stands in for handshake_dir so `handshake_dir / 'cache'` yields a cache that stats present but
    cannot be enumerated."""
    def __truediv__(self, _other):
        return _UnreadableCache()


def test_incomplete_cache_scan_is_not_marked_present():
    c = PwnagotchiCollector()
    c.handshake_dir = _DirStub()
    ap, clients, hs, hidden, present = c._cache_summary(max_age=0.0)
    assert present is False          # glob() failed -> not a trustworthy readable cache
    assert hs == 0 and ap == 0
