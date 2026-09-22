import tempfile
from pathlib import Path

from beastcore.collectors.services import ServicesCollector
from beastcore.collectors.bettercap import BettercapCollector


def test_service_parser_shape(monkeypatch):
    import beastcore.collectors.services as mod
    def fake_run(cmd, timeout=2):
        return 0, "LoadState=loaded\nActiveState=active\nSubState=running\nMainPID=123\nExecMainStartTimestamp=Sun 2026-09-20 00:08:35 BST\n", ""
    monkeypatch.setattr(mod, "run", fake_run)
    out = ServicesCollector(["bettercap.service"]).collect()
    item = out["platform.services"][0]
    assert item["load"] == "loaded"
    assert item["active"] == "active"
    assert item["sub"] == "running"
    assert item["pid"] == 123
    assert out["bettercap.state"] == "active"


def test_caplet_parse():
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "x.cap"
        p.write_text('set api.rest.address 0.0.0.0\nset api.rest.port 8081\nset api.rest.username "u"\nset api.rest.password "p"\n')
        cfg = BettercapCollector._parse_caplet(p)
        assert cfg["address"] == "127.0.0.1"
        assert cfg["port"] == "8081"
        assert cfg["username"] == "u"
        assert cfg["password"] == "p"
