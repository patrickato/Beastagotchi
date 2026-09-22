from pathlib import Path

from beastui.input import classify_gesture


def test_left_swipe_survives_liftoff_snap():
    pts=[(410,150),(390,151),(360,150),(320,151),(275,150),(230,150),(185,151),(145,150),(110,151),(108,150),(150,151)]
    kind,p=classify_gesture(pts,0.60)
    assert kind=='swipe'
    assert p['axis']=='x'
    assert p['direction']=='left'
    assert p['delta']==1


def test_right_swipe_survives_liftoff_snap():
    pts=[(90,150),(110,150),(145,151),(190,151),(240,151),(290,150),(340,151),(390,150),(410,150),(405,151),(360,150)]
    kind,p=classify_gesture(pts,0.60)
    assert kind=='swipe'
    assert p['axis']=='x'
    assert p['direction']=='right'
    assert p['delta']==-1


def test_diagonal_human_swipe_is_still_horizontal():
    pts=[(400,210),(370,205),(330,195),(290,185),(250,175),(210,166),(165,155),(120,145)]
    kind,p=classify_gesture(pts,0.68)
    assert kind=='swipe'
    assert p['axis']=='x'
    assert p['direction']=='left'


def _ui(tmp_path):
    from beastui.engine import BeastUI
    root=tmp_path/'root'; (root/'themes').mkdir(parents=True)
    src=Path(__file__).resolve().parents[1]/'beastui'/'themes'/'classic.json'
    (root/'themes'/'classic.json').write_text(src.read_text())
    return BeastUI(str(root),output=str(tmp_path/'out.png'))


def test_swipes_do_not_wrap_home_to_system(tmp_path):
    ui=_ui(tmp_path)
    assert ui.page==0
    ui.on_input('swipe',{'axis':'x','delta':-1,'direction':'right','dx':120,'dy':2})
    assert ui.page==0
    ui.on_input('swipe',{'axis':'x','delta':1,'direction':'left','dx':-120,'dy':2})
    assert ui.page==1


def test_footer_arrows_remain_circular(tmp_path):
    ui=_ui(tmp_path)
    ui.on_input('tap',{'x':40,'y':295})
    assert ui.page==len(ui.pages.IDS)-1
