from __future__ import annotations

import argparse
import time
from pathlib import Path

from beastui import __version__ as UI_VERSION
from beastui.apps import AppRegistry
from beastui.customization import (
    validate_context_decks,
    validate_correlation_keys,
    validate_custom_boards,
    validate_dashboard_widgets,
    validate_palette_overrides,
)
from beastui.engine import BeastUI
from beastui.face import FaceEngine
from beastui.pack_content import discover_enabled_pack_boards
from beastui.presentation_preferences import (
    PREFERENCE_SCHEMA_VERSION,
    PresentationPreferenceStore,
)
from beastui.theme import discover_enabled_pack_themes

from . import server


class RuntimeStudioState(server.StudioState):
    """Production Studio adapter for the shared presentation preference store.

    The current StudioState remains usable by existing tests/tools while the
    production entrypoint converges on one persistence contract. This adapter is
    intentionally temporary; the future Studio domain split should inject the
    store directly instead of subclassing the v0.19 composition root.
    """

    def __init__(self, root: str, prefs: str, token_file: str) -> None:
        super().__init__(root, prefs, token_file)
        self.preference_store = PresentationPreferenceStore(self.prefs)

    def preferences(self) -> dict:
        obj = self.preference_store.read()
        renderers = dict(obj.get('renderers') or {})
        for pid, vals in BeastUI.RENDERER_CHOICES.items():
            renderers.setdefault(pid, vals[0])
        pack_boards = discover_enabled_pack_boards()
        app_ids = [a.id for a in AppRegistry().all()] + [f"board:{b['id']}" for b in pack_boards]
        decks = validate_context_decks(obj.get('context_decks'), app_ids=app_ids)
        active = str(obj.get('active_context_deck') or '')
        if active not in {d['id'] for d in decks}:
            active = ''
        theme_ids = list(BeastUI.THEMES) + [
            x for x in discover_enabled_pack_themes() if x not in BeastUI.THEMES
        ]
        face_ids = {'builtin', *server.discover_enabled_face_profiles().keys()}
        face_profile = str(obj.get('face_profile') or 'builtin')
        face_profile = face_profile if face_profile in face_ids else 'builtin'
        anim_ids = {'none', *FaceEngine().animation_profiles.keys()}
        animation_profile = str(obj.get('animation_profile') or 'none')
        animation_profile = animation_profile if animation_profile in anim_ids else 'none'
        return {
            'theme': str(obj.get('theme') or 'classic'),
            'face_profile': face_profile,
            'animation_profile': animation_profile,
            'page': 'home',
            'preview_output': '480x320',
            'renderers': renderers,
            'theme_options': dict(obj.get('theme_options') or {}),
            'dashboard_widgets': validate_dashboard_widgets(obj.get('dashboard_widgets')),
            'custom_boards': validate_custom_boards(obj.get('custom_boards')),
            'preview_board_id': '',
            'context_decks': decks,
            'active_context_deck': active,
            'palette_overrides': validate_palette_overrides(obj.get('palette_overrides'), theme_ids=theme_ids),
            'correlation_keys': validate_correlation_keys(obj.get('correlation_keys')),
        }

    def schema(self) -> dict:
        row = super().schema()
        # `version` is retained for the existing browser contract, but it now
        # means the actual UI product version rather than a stale hand-written
        # schema label. Preference schema identity is a separate field.
        row['version'] = UI_VERSION
        row['product_version'] = UI_VERSION
        row['preference_schema_version'] = PREFERENCE_SCHEMA_VERSION
        return row

    def apply(self, draft: dict) -> dict:
        cfg = self.validate(draft)
        payload = {
            'theme': cfg['theme'],
            'face_profile': cfg['face_profile'],
            'animation_profile': cfg['animation_profile'],
            'renderers': cfg['renderers'],
            'theme_options': cfg['theme_options'],
            'dashboard_widgets': cfg['dashboard_widgets'],
            'custom_boards': cfg['custom_boards'],
            'context_decks': cfg['context_decks'],
            'active_context_deck': cfg['active_context_deck'],
            'palette_overrides': cfg['palette_overrides'],
            'correlation_keys': cfg['correlation_keys'],
        }
        result = self.preference_store.write(payload, create_backup=True)
        return {
            'ok': True,
            'theme': cfg['theme'],
            'applied_at': time.time(),
            'changed': bool(result.get('changed')),
            'preference_generation': result.get('generation'),
            'preference_fingerprint': result.get('fingerprint'),
        }


def serve(
    host: str = '0.0.0.0',
    port: int = 8091,
    root: str = '/opt/beast-ui',
    prefs: str = '/var/lib/beastagotchi/ui/preferences.json',
    token_file: str = '/var/lib/beastagotchi/ui/studio.token',
) -> None:
    state = RuntimeStudioState(root, prefs, token_file)
    srv = server.ReusableThreadingHTTPServer((host, int(port)), server.Handler)
    srv.studio = state
    srv.serve_forever()


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument('--host', default='0.0.0.0')
    p.add_argument('--port', type=int, default=8091)
    p.add_argument('--root', default='/opt/beast-ui')
    p.add_argument('--prefs', default='/var/lib/beastagotchi/ui/preferences.json')
    p.add_argument('--token-file', default='/var/lib/beastagotchi/ui/studio.token')
    a = p.parse_args()
    serve(a.host, a.port, a.root, a.prefs, a.token_file)
