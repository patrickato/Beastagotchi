from beastui.experience_registry import render_experience_page as registry_render
from tools import render_v019_atlas_home as atlas_home_tool
from tools import render_v019_experience_homes as homes_tool
from tools import render_v019_experience_page_translations as pages_tool


def test_experience_proof_generators_use_active_registry_renderer():
    assert atlas_home_tool.render_experience_page is registry_render
    assert homes_tool.render_experience_page is registry_render
    assert pages_tool.render_experience_page is registry_render


def test_cross_page_proof_declares_experience_and_page_ids_not_renderer_functions():
    source = pages_tool.Path(pages_tool.__file__).read_text()
    assert "from beastui.experience_atlas import render_atlas" not in source
    assert '("atlas","home")' in source
    assert '("atlas","recon")' in source
