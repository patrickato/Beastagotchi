from pathlib import Path
import json

from beastui.theme import load_theme
from beastcore.collectors.pwnagotchi import PwnagotchiCollector


def test_matrix_motion_options_are_manifest_driven():
    root=Path(__file__).resolve().parents[1]
    t=load_theme(root/'beastui/themes/matrix.json')
    assert t.background=='matrix'
    assert t.background_options['column_spacing'] <= 12
    assert t.background_options['trail'] >= 7
    assert t.background_options['speed'] >= 70
    assert t.scanline_speed > 0


def test_plugin_inventory_exposes_repository_counts(tmp_path):
    cfg=tmp_path/'config.toml'
    cfg.write_text('''[main]\ncustom_plugin_repos=["https://example/a.zip","https://example/b.zip"]\n[main.plugins.alpha]\nenabled=true\n[main.plugins.beta]\nenabled=false\n''')
    c=PwnagotchiCollector(str(cfg))
    c.custom_plugin_dir=tmp_path/'plugins'; c.custom_plugin_dir.mkdir()
    c.conf_d=tmp_path/'conf.d'; c.conf_d.mkdir()
    c.handshake_dir=tmp_path/'hs'; c.handshake_dir.mkdir()
    c.session_dir=tmp_path/'sessions'; c.session_dir.mkdir()
    (c.custom_plugin_dir/'alpha.py').write_text('# alpha')
    out=c.collect()
    assert out['plugins.repo_count']==2
    assert len(out['plugins.repos'])==2
    assert out['plugins.configured_count']==2
    assert out['plugins.enabled_count']==1
    assert out['plugins.installed_custom_count']==1


def test_master_readme_and_path_helper_ship():
    root=Path(__file__).resolve().parents[1]
    assert (root/'docs/archive/drafts/BEASTAGOTCHI_MASTER_README_DRAFT.md').exists()
    assert (root/'tools/beast_paths.sh').exists()
