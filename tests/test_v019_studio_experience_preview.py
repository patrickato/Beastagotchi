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
