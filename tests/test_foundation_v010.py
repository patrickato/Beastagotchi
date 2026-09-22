from pathlib import Path
from PIL import Image

from beastui.engine import BeastUI
from beastui.widgets import histogram, waveform, waterfall, donut, polar, signal_meter, timeline

ROOT=Path(__file__).resolve().parents[1]/'beastui'


def _state():
    return {
        'health.core.state':'healthy','radio.primary.channel':6,'radio.primary.band':'2.4GHz',
        'wifi.ap_count':6,'wifi.client_count':2,'wifi.handshake_ap_count':3,
        'wifi.aps':[{'hostname':f'AP{i}','channel':ch,'rssi':-35-i*5,'encryption':'WPA2'} for i,ch in enumerate([1,1,6,6,11,44])],
        'system.temp.cpu_c':65.0,'system.cpu.total':22.0,'system.memory.used_pct':11.0,
        'context.mode.effective':'pwn','pwnagotchi.mood':'awake','pwnagotchi.handshakes':2,
        'progression.level':8,'progression.max_level':100,'progression.stage':'Cub','progression.xp':500,
        'progression.xp_next_level':900,'progression.level_progress_pct':55.0,'progression.aura':'spark',
        'progression.vendors.count':3,'progression.achievements.count':2,'wifi.encounters.lifetime_unique':22,
        'captures.total':4,'capabilities.count':6,'network.ethernet.carrier':True,
    }


def test_visualizer_catalog_is_broad():
    assert len(BeastUI.RENDERER_CHOICES['spectrum']) >= 10
    assert set(['histogram','donut','waveform','waterfall','polar']).issubset(BeastUI.RENDERER_CHOICES['spectrum'])
    assert len(BeastUI.RENDERER_CHOICES['system']) >= 5
    assert set(BeastUI.RENDERER_CHOICES)=={'recon','spectrum','captures','system'}


def test_all_registered_renderers_render_offscreen(tmp_path):
    ui=BeastUI(root=ROOT,output=str(tmp_path/'x.png'),theme_id='classic');ui.state=_state()
    ui.histories={'wifi.ap_count':[1,2,4,3,5,6],'system.cpu.total':[10,20,15,30,22], 'system.temp.cpu_c':[55,58,60,62,65]}
    ui.events=[{'type':'system.thermal_band','severity':'warning'}]
    for pid,choices in ui.RENDERER_CHOICES.items():
        ui.page=ui.pages.IDS.index(pid)
        for mode in choices:
            ui.renderers[pid]=mode
            im=ui.render()
            assert im.size==(480,320)


def test_visualizer_overlay_cycles_selected_renderer(tmp_path):
    ui=BeastUI(root=ROOT,output=str(tmp_path/'x.png'),theme_id='classic');ui.state=_state();ui.visualizer_overlay=True
    before=ui.renderer_for('recon')
    ui.on_input('tap',{'x':400,'y':90})
    assert ui.renderer_for('recon') != before


def test_non_matrix_themes_have_runtime_options(tmp_path):
    ui=BeastUI(root=ROOT,output=str(tmp_path/'x.png'),theme_id='classic')
    assert ui._theme_option_rows('classic')
    assert ui._theme_option_rows('starcore')
    assert ui._theme_option_rows('blackice')
    assert ui._theme_option_rows('hunter')
    assert ui._theme_option_rows('minimal')


def test_classic_grid_density_changes_frame(tmp_path):
    ui=BeastUI(root=ROOT,output=str(tmp_path/'x.png'),theme_id='classic');ui.state=_state();ui.phase=1.0
    ui.theme_options['classic']={'grid_density':'off','scanline':'off','pulse_level':'off'};a=ui._compose(0)
    ui.theme_options['classic']={'grid_density':'dense','scanline':'off','pulse_level':'active'};b=ui._compose(0)
    assert a.tobytes()!=b.tobytes()


def test_starcore_and_hunter_options_change_frame(tmp_path):
    for tid,aopt,bopt in [
        ('starcore',{'star_density':'sparse','twinkle':'off','orbit':'off'},{'star_density':'nebula','twinkle':'high','orbit':'on'}),
        ('hunter',{'grid_density':'off','reticle':'off','embers':'off'},{'grid_density':'dense','reticle':'on','embers':'heavy'}),
    ]:
        ui=BeastUI(root=ROOT,output=str(tmp_path/f'{tid}.png'),theme_id=tid);ui.state=_state();ui.phase=1.3
        ui.theme_options[tid]=aopt;a=ui._compose(0)
        ui.theme_options[tid]=bopt;b=ui._compose(0)
        assert a.tobytes()!=b.tobytes()


def test_renderer_primitives_do_not_raise():
    from beastui.theme import load_theme
    from PIL import ImageDraw, ImageFont
    t=load_theme(ROOT/'themes'/'classic.json');im=Image.new('RGB',(480,320),t.c('bg'));d=ImageDraw.Draw(im)
    vals=[1,4,2,8,5,9,3,6]
    histogram(d,(0,0,100,80),vals,t);waveform(d,(100,0,200,80),vals,t);waterfall(d,(200,0,300,80),vals,t)
    donut(d,(300,0,400,80),vals,t);polar(d,(0,80,120,200),vals,t);signal_meter(d,(120,80,260,160),70,t)
    timeline(d,(260,80,479,160),[{'severity':'info'},{'severity':'warning'},{'severity':'critical'}],t)
    assert im.getbbox() is not None


def test_footer_still_wins_over_graph_touch(tmp_path):
    ui=BeastUI(root=ROOT,output=str(tmp_path/'x.png'),theme_id='classic');ui.page=ui.pages.IDS.index('system')
    ui.on_input('tap',{'x':365,'y':260})
    assert ui.page==0
