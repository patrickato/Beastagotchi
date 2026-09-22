from beastui.input import classify_gesture


def test_tap_ignores_single_jitter_sample():
    pts=[(40,300),(41,299),(42,300),(125,245),(41,301),(40,300),(42,299),(41,300)]
    kind,p=classify_gesture(pts,0.22)
    assert kind=='tap'
    assert 38 <= p['x'] <= 44
    assert 296 <= p['y'] <= 303


def test_horizontal_swipe_uses_end_to_end_motion():
    pts=[(400,150),(382,151),(350,153),(310,154),(260,154),(210,153),(160,152),(110,150)]
    kind,p=classify_gesture(pts,0.48)
    assert kind=='swipe'
    assert p['axis']=='x'
    assert p['delta']==1


def test_vertical_swipe():
    pts=[(240,250),(240,225),(241,200),(240,165),(239,130),(240,95)]
    kind,p=classify_gesture(pts,0.42)
    assert kind=='swipe'
    assert p['axis']=='y'


def test_long_press_tolerates_resistive_wobble():
    pts=[(200,160),(204,157),(198,164),(206,161),(201,156),(203,163),(199,160),(202,159)]
    kind,p=classify_gesture(pts,0.91)
    assert kind=='long_press'


def test_footer_hitbox_is_finger_sized(tmp_path):
    import json
    from beastui.engine import BeastUI
    root=tmp_path/'root'; (root/'themes').mkdir(parents=True)
    src=__import__('pathlib').Path(__file__).resolve().parents[1]/'beastui'/'themes'/'classic.json'
    (root/'themes'/'classic.json').write_text(src.read_text())
    ui=BeastUI(str(root), output=str(tmp_path/'out.png'))
    ui.on_input('tap', {'x':100,'y':260})
    assert ui.page == len(ui.pages.IDS)-1
    ui.on_input('tap', {'x':365,'y':260})
    assert ui.page == 0
