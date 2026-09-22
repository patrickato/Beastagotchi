import importlib.util
import time
from pathlib import Path

from beastcore.context import ContextEngine
from beastcore.semantic import SemanticEngine
from beastcore.state import StateRegistry


def _load_display_config():
    p=Path(__file__).resolve().parents[1]/"tools"/"display_config.py"
    spec=importlib.util.spec_from_file_location("display_config",p)
    m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


def test_display_config_edits_only_ui_display_enabled():
    m=_load_display_config()
    src='''[main]\nenabled = true\n\n[ui.display]\nenabled = true\nrotation = 180\ntype = "waveshare35lcd"\n\n[plugins.foo]\nenabled = true\n'''
    out=m.set_enabled_text(src,False)
    assert '[main]\nenabled = true' in out
    assert '[plugins.foo]\nenabled = true' in out
    assert '[ui.display]\nenabled = false' in out
    assert m.get_enabled(out) is False
    restored=m.set_enabled_text(out,True)
    assert m.get_enabled(restored) is True


def test_gps_semantic_debounce():
    s=StateRegistry(); eng=SemanticEngine(s)
    s.update_many('gps',{'gps.fix':False},priority=70)
    assert not eng.tick()
    assert s.get('gps.fix.debounced') is False

    s.update_many('gps',{'gps.fix':True,'gps.satellites_used':5},priority=70)
    assert not [e for e in eng.tick() if e[0].startswith('gps.')]
    eng._gps_candidate_since=time.monotonic()-4.0
    got=eng.tick()
    assert any(e[0]=='gps.lock_acquired' for e in got)
    assert s.get('gps.fix.debounced') is True

    s.update_many('gps',{'gps.fix':False},priority=70)
    assert not [e for e in eng.tick() if e[0]=='gps.lock_lost']
    eng._gps_candidate_since=time.monotonic()-6.0
    got=eng.tick()
    assert any(e[0]=='gps.lock_lost' for e in got)
    assert s.get('gps.fix.debounced') is False


def test_context_holds_mode_during_debounced_gps_grace():
    s=StateRegistry(); eng=ContextEngine(s); eng.current='wardrive'
    s.update_many('semantic',{'gps.fix.debounced':True},priority=85)
    s.update_many('gps',{'gps.fix':False,'gps.speed_mps':None},priority=70)
    out=eng.tick()
    assert out['context.mode.effective']=='wardrive'
    assert out['context.motion.raw']=='gps_grace'
    assert out['context.motion.confidence']=='medium'
