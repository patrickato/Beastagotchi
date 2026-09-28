from beastui.experience_live import ExperienceBeastUI


def _idle_ui():
    ui = ExperienceBeastUI.__new__(ExperienceBeastUI)
    ui.transition = None
    ui.state = {}
    ui.monster_reveal_dismissed_id = None
    ui._monster_reveal_was_active = False
    ui.button_flash = None
    ui.button_flash_at = 0.0
    ui.notice = None
    ui.notice_started = 0.0
    ui.notice_duration = 2.4
    ui.last_render = 100.0
    ui._experience_ambient_at = 100.0
    return ui


def test_experience_idle_cadence_does_not_depend_on_legacy_background_cache():
    ui = _idle_ui()
    # Experience pages do not populate BeastUI's legacy _bg_cache. That must not
    # make every adaptive frame budget look like a requested ambient redraw.
    assert ui._dynamic_frame_due(100.20) is False
    assert ui._dynamic_frame_due(100.99) is False
    assert ui._dynamic_frame_due(101.01) is True


def test_experience_transient_animation_still_bypasses_idle_cadence():
    ui = _idle_ui()
    ui.state['rare.moment.active'] = True
    assert ui._dynamic_frame_due(100.05) is True
