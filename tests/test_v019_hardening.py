"""Regression tests for the v0.19 hardening pass.

Covers, one test per fix:
  1. Beast Studio binds to loopback by default (not 0.0.0.0 / all interfaces).
  2. The Studio token is stripped from the URL after it is read.
  3. The Beast UI render loop survives a per-frame exception instead of blanking.
  4. Operational retention prunes churny log tables but never durable records.
  5. The semantic seen-BSSID cache is memory-bounded.
"""
import inspect
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


# 1. Studio bind address ------------------------------------------------------
def test_studio_serve_defaults_to_loopback():
    from beaststudio import server
    assert inspect.signature(server.serve).parameters["host"].default == "127.0.0.1"
    main_src = inspect.getsource(server.main)
    assert "default='127.0.0.1'" in main_src
    assert "default='0.0.0.0'" not in main_src


# 2. Studio token not left in the URL ----------------------------------------
def test_studio_strips_token_from_url():
    from beaststudio import server
    src = inspect.getsource(server)
    # Token is read from the query string once, then removed from history so it
    # cannot leak via browser history / Referer / access logs.
    assert "history.replaceState" in src


# 3. Render loop exception guard ---------------------------------------------
def test_safe_render_survives_render_exception():
    from beastui.engine import BeastUI
    ui = BeastUI.__new__(BeastUI)  # bypass the heavy __init__; exercise the guard only
    calls = {"n": 0}

    def boom():
        calls["n"] += 1
        raise ValueError("malformed live state value")

    ui.render = boom
    ui.last_render = 0.0
    # Must not propagate; returns None and keeps the loop alive.
    assert ui._safe_render() is None
    assert calls["n"] == 1


# 4. Operational retention ----------------------------------------------------
def test_prune_operational_bounds_logs_but_keeps_records(tmp_path):
    from beastcore.db import Store
    st = Store(str(tmp_path / "beast.db"))
    c = st.conn
    now = 2_000_000_000.0
    old = now - 400 * 86400  # 400 days ago — beyond every default window
    with c:
        c.execute("INSERT INTO events(id,ts,type,source,severity,data_json) VALUES('e_old',?,'t','s','info','{}')", (old,))
        c.execute("INSERT INTO events(id,ts,type,source,severity,data_json) VALUES('e_new',?,'t','s','info','{}')", (now,))
        c.execute("INSERT INTO jobs(id,kind,label,status,created_at,finished_at,result_json) VALUES('j_old','k','l','done',?,?,'{}')", (old, old))
        c.execute("INSERT INTO incidents(id,kind,severity,status,opened_at,last_seen,resolved_at,summary,snapshot_json) VALUES(?,?,?,?,?,?,?,?,?)",
                  ("i_res", "k", "info", "resolved", old, old, old, "s", "{}"))
        c.execute("INSERT INTO incidents(id,kind,severity,status,opened_at,last_seen,summary,snapshot_json) VALUES('i_open','k','info','open',?,?,'s','{}')", (old, old))
        c.execute("INSERT INTO actions(id,ts,actor,action,status,request_json,plan_json,result_json) VALUES('a_old',?,'local','x','ok','{}','{}','{}')", (old,))
        # A durable field record that must NEVER be pruned by retention:
        c.execute("INSERT INTO expedition_points(expedition_id,ts,latitude,longitude) VALUES('exp1',?,1.0,2.0)", (old,))

    st.prune_operational(now)

    assert c.execute("SELECT COUNT(*) FROM events").fetchone()[0] == 1            # old gone, recent kept
    assert c.execute("SELECT COUNT(*) FROM jobs").fetchone()[0] == 0             # finished+old gone
    assert c.execute("SELECT COUNT(*) FROM incidents WHERE status='open'").fetchone()[0] == 1   # open never pruned
    assert c.execute("SELECT COUNT(*) FROM incidents WHERE status='resolved'").fetchone()[0] == 0
    assert c.execute("SELECT COUNT(*) FROM actions").fetchone()[0] == 0
    # The durable record is untouched — "no silent scope loss".
    assert c.execute("SELECT COUNT(*) FROM expedition_points").fetchone()[0] == 1


def test_prune_operational_keeps_recent_and_open(tmp_path):
    from beastcore.db import Store
    st = Store(str(tmp_path / "beast.db"))
    c = st.conn
    now = 2_000_000_000.0
    recent = now - 3600  # an hour ago — inside every window
    with c:
        c.execute("INSERT INTO events(id,ts,type,source,severity,data_json) VALUES('e',?,'t','s','info','{}')", (recent,))
        c.execute("INSERT INTO actions(id,ts,actor,action,status,request_json,plan_json,result_json) VALUES('a',?,'local','x','ok','{}','{}','{}')", (recent,))
    st.prune_operational(now)
    assert c.execute("SELECT COUNT(*) FROM events").fetchone()[0] == 1
    assert c.execute("SELECT COUNT(*) FROM actions").fetchone()[0] == 1


# 5. Bounded semantic seen-BSSID cache ---------------------------------------
class _FakeState:
    def __init__(self, snap):
        self._snap = snap

    def snapshot(self, include_meta=False):
        return dict(self._snap)

    def meta(self, key):
        return {}

    def get(self, key, default=None):
        return self._snap.get(key, default)

    def update_many(self, *args, **kwargs):
        return None


def test_seen_bssids_is_memory_bounded():
    from beastcore.semantic import SemanticEngine
    aps = [{"mac": f"00:11:22:33:{i // 256:02x}:{i % 256:02x}"} for i in range(500)]
    eng = SemanticEngine(_FakeState({"wifi.aps": aps}), store=None)
    eng._seen_bssids_cap = 20
    eng.tick()
    assert len(eng.seen_bssids) <= 20
