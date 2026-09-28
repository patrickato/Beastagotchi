from PIL import ImageChops

from beastui.experience_atlas_fieldscene_v30 import render_atlas_home, render_atlas_recon
from beastui.scene_runtime import SceneRuntime


def _state(*, live=True):
    state={
        'health.core.state':'healthy','governor.mode':'FULL','system.temp.cpu_c':58.0,
        'progression.beast.name':'Hex','progression.beast.kind':'beast','progression.beast.lineage':'field.standard',
        'progression.beast.generation':0,'progression.stage':'Stalker','progression.level':27,
        'progression.aura':'spark','beast.expression':'curious','pwnagotchi.mood':'awake',
        'wifi.ap_count':0,'wifi.aps':[],'radio.primary.channel':1,'radio.primary.band':'2.4GHz',
        'gps.fix':False,'gps.satellites_used':0,'expedition.active':False,'expedition.route_points':0,
        'expedition.ap_unique':0,'expedition.captures_delta':0,'expedition.xp_delta':0,
        'wifi.handshake_ap_count':0,'wifi.hidden_count':0,
    }
    if live:
        state.update({
            'wifi.ap_count':3,'wifi.aps':[
                {'channel':1,'rssi':-42},{'channel':6,'rssi':-58},
                {'channel':149,'rssi':-67,'handshake':True}],
            'radio.primary.channel':6,'gps.fix':True,'gps.satellites_used':7,
            'expedition.active':True,'expedition.route_points':4,'expedition.ap_unique':17,
            'expedition.distance_m':1420.0,'expedition.duration_sec':754,
            'expedition.captures_delta':2,'expedition.xp_delta':14,
            'wifi.handshake_ap_count':3,'wifi.hidden_count':1,
        })
    return state


def test_atlas_v30_renders_truth_states_with_stable_scene_ids_and_creature_layer():
    for page,renderer in [('home',render_atlas_home),('recon',render_atlas_recon)]:
        runtime=SceneRuntime()
        image=renderer(_state(live=True),phase=.7,scene_runtime=runtime)
        assert image.size==(480,320)
        snap=runtime.snapshot()
        assert snap['page']==page
        assert snap['scene']==f'experience:atlas:{page}'
        assert any(row['kind']=='creature' for row in snap['layers'])


def test_atlas_v30_live_state_and_recon_motion_are_visually_real():
    empty=render_atlas_home(_state(live=False),phase=.5)
    live=render_atlas_home(_state(live=True),phase=.5)
    assert ImageChops.difference(empty,live).getbbox() is not None
    a=render_atlas_recon(_state(live=True),phase=0.0)
    b=render_atlas_recon(_state(live=True),phase=2.0)
    assert ImageChops.difference(a,b).getbbox() is not None


def test_atlas_v30_semantic_palette_roles_are_overrideable():
    base=render_atlas_home(_state(live=True),phase=.5)
    custom=render_atlas_home(_state(live=True),phase=.5,palette_overrides={
        'primary':'#FF55AA','text':'#FFFFFF','dim':'#AAAAAA','secondary':'#44CCFF',
    })
    assert ImageChops.difference(base,custom).getbbox() is not None
