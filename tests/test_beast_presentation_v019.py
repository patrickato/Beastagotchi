from PIL import Image

from beastui.beast_presentation import (
    BeastPalette,
    _prepared_concept,
    draw_beast_presence,
    presentation_snapshot,
    resolve_beast_identity,
)


def _state():
    return {
        'progression.beast.name':'Hex','progression.beast.kind':'beast',
        'progression.beast.lineage':'field.standard','progression.beast.generation':2,
        'progression.stage':'Stalker','progression.level':27,'progression.aura':'spark',
        'beast.expression':'curious','pwnagotchi.mood':'awake',
    }


def test_beast_presentation_resolves_identity_independently_of_experience():
    ident=resolve_beast_identity(_state())
    assert presentation_snapshot(ident)=={
        'name':'Hex','kind':'beast','lineage':'field.standard','generation':2,
        'stage':'Stalker','level':27,'expression':'curious','mood':'awake','aura':'spark',
    }


def test_beast_scene_asset_preparation_is_cached_across_frames():
    _prepared_concept.cache_clear()
    state=_state()
    for phase in (.1,1.1):
        im=Image.new('RGB',(480,320),(0,0,0))
        draw_beast_presence(im,(20,40,250,240),state,phase,palette=BeastPalette.atlas_default())
    info=_prepared_concept.cache_info()
    assert info.misses==1
    assert info.hits>=1
