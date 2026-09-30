from __future__ import annotations

from .engine import BeastUI
from .presentation_preferences import PresentationPreferenceStore


class RuntimeBeastUI(BeastUI):
    """Production BeastUI adapter using the canonical preference file contract.

    The large v0.19 renderer remains unchanged in this correctness tranche. The
    adapter is intentionally small and can disappear once preference ownership is
    injected directly into the future BeastUIShell/PresentationPreferenceStore
    client architecture.
    """

    def __init__(self, *args, **kwargs):
        output = kwargs.get('output')
        if output is None and len(args) >= 3:
            output = args[2]
        self._preference_store = PresentationPreferenceStore() if output is None else None
        super().__init__(*args, **kwargs)

    def _load_prefs(self):
        store = getattr(self, '_preference_store', None)
        if store is None:
            return {}
        return store.read()

    def _save_prefs(self):
        store = getattr(self, '_preference_store', None)
        if store is None:
            return
        payload = {
            'theme': self.theme.id,
            'face_profile': self.face_profile_pref,
            'animation_profile': self.animation_profile_pref,
            'renderers': self.renderers,
            'theme_options': self.theme_options,
            'dashboard_widgets': self.dashboard_widgets,
            'custom_boards': self.custom_boards,
            'context_decks': self.context_decks,
            'active_context_deck': self.active_context_deck,
            'palette_overrides': self.palette_overrides,
            'correlation_keys': self.correlation_keys,
        }
        try:
            result = store.write(payload, create_backup=False)
            self._pref_sig = result.get('signature') or store.signature()
        except Exception as exc:
            # Presentation persistence failure must not kill the physical UI.
            from .engine import log
            log.warning('could not persist UI prefs: %s', exc)
