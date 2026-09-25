import io

from PIL import Image
import pytest

from beaststudio.server import StudioState
from beaststudio.experiences import ExperienceDraftError


class _API:
    def __init__(self, state):
        self._state=state
    def live(self, limit=24):
        return {"state":self._state,"events":[]}
    def experiences(self):
        return {
            "schema":1,
            "mode":"read_only",
            "count":1,
            "items":[{"experience_id":"atlas","ready_for_preview":True}],
            "tft_activation_enabled":False,
        }


def _studio(state):
    st=object.__new__(StudioState)
    st.api=_API(state)
    return st


def test_studio_experience_preview_returns_actual_renderer_png():
    st=_studio({
        "wifi.ap_count":3,
        "wifi.aps":[{"channel":6,"rssi":-55,"handshake":False}],
        "radio.primary.channel":6,
        "radio.primary.band":"2.4GHz",
        "progression.stage":"Cub",
        "progression.level":7,
        "health.core.state":"healthy",
    })
    payload=st.experience_preview({"id":"atlas","page":"recon"})
    im=Image.open(io.BytesIO(payload))
    assert im.size==(480,320)


def test_studio_experience_preview_rejects_unimplemented_page():
    st=_studio({})
    with pytest.raises(ExperienceDraftError):
        st.experience_preview({"id":"forge","page":"spectrum"})


def test_studio_reads_core_compiled_experience_plan_without_local_recompile():
    st=_studio({})
    row=st.experiences()
    assert row["mode"]=="read_only"
    assert row["items"][0]["experience_id"]=="atlas"
    assert row["tft_activation_enabled"] is False


def test_studio_html_exposes_core_backed_compiled_experience_browser():
    from beaststudio.server import HTML
    assert 'id="builtinExperienceList"' in HTML
    assert "jfetch('/api/experiences')" in HTML
    assert "COMPILED EXPERIENCE DNA" in HTML
    assert "previewCompiledExperience" in HTML
    assert "renderer_experience_id" in HTML
    assert "TRY ON TFT PLAN" in HTML
    assert "planTryOnTft" in HTML
    assert "/api/experience-try-plan" in HTML
