from __future__ import annotations

from types import SimpleNamespace

from beaststudio.runtime import RuntimeStudioState
from beastui import __version__ as UI_VERSION
from beastui.presentation_preferences import (
    PREFERENCE_SCHEMA_VERSION,
    PresentationPreferenceStore,
)
from beastui.runtime import RuntimeBeastUI


def _validated_draft(theme='classic'):
    return {
        'theme': theme,
        'face_profile': 'builtin',
        'animation_profile': 'none',
        'renderers': {'recon': 'radar'},
        'theme_options': {},
        'dashboard_widgets': [],
        'custom_boards': [],
        'context_decks': [],
        'active_context_deck': '',
        'palette_overrides': {},
        'correlation_keys': [],
    }


def test_runtime_ui_save_uses_canonical_store(tmp_path):
    path = tmp_path / 'preferences.json'
    ui = object.__new__(RuntimeBeastUI)
    ui._preference_store = PresentationPreferenceStore(path)
    ui._pref_sig = None
    ui.theme = SimpleNamespace(id='blackice')
    ui.face_profile_pref = 'builtin'
    ui.animation_profile_pref = 'none'
    ui.renderers = {'recon': 'radar'}
    ui.theme_options = {}
    ui.dashboard_widgets = []
    ui.custom_boards = []
    ui.context_decks = []
    ui.active_context_deck = ''
    ui.palette_overrides = {}
    ui.correlation_keys = []

    ui._save_prefs()

    assert ui._preference_store.read()['theme'] == 'blackice'
    assert ui._pref_sig == ui._preference_store.signature()
    assert (path.stat().st_mode & 0o777) == 0o600


def test_runtime_studio_apply_uses_same_store_and_creates_backup(tmp_path):
    path = tmp_path / 'preferences.json'
    store = PresentationPreferenceStore(path, clock=lambda: 1000.0)
    store.write(_validated_draft('classic'))

    st = object.__new__(RuntimeStudioState)
    st.prefs = path
    st.preference_store = store
    st.validate = lambda draft: _validated_draft(str(draft.get('theme') or 'classic'))

    row = st.apply({'theme': 'hunter'})

    assert row['ok'] is True
    assert row['changed'] is True
    assert store.read()['theme'] == 'hunter'
    assert len(list((path.parent / 'backups').glob('preferences-*.json'))) == 1


def test_runtime_studio_schema_separates_product_and_preference_versions(monkeypatch):
    st = object.__new__(RuntimeStudioState)
    monkeypatch.setattr(
        'beaststudio.server.StudioState.schema',
        lambda self: {'version': '0.18.0', 'themes': []},
    )

    row = RuntimeStudioState.schema(st)

    assert row['version'] == UI_VERSION
    assert row['product_version'] == UI_VERSION
    assert row['preference_schema_version'] == PREFERENCE_SCHEMA_VERSION
    assert row['version'] != '0.18.0'
