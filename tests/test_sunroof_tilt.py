"""Sunroof tilt / vent position, exposed as the tilt half of the sunroof cover.

The car accepts `skylightControl` with `controlType` "2" for the tilt position (the
official app's `controlTiltUp`). It is wired to `open_cover_tilt` on the existing sunroof
cover rather than to a new button, so the entity count does not move.

These tests check the wiring only. Whether the car actually tilts is a hardware question
that no test here can answer.
"""
from __future__ import annotations

import pytest
from homeassistant.components.cover import CoverEntityFeature

from custom_components.omoda9 import coordinator as coord_mod
from custom_components.omoda9.const import COMMANDS_AS_RICH_ENTITY

SUNROOF = "cover.chery_connect_sunroof"
TRUNK = "cover.chery_connect_trunk"
WINDOWS = "cover.chery_connect_windows"


@pytest.fixture
def sent(monkeypatch):
    keys: list[str] = []

    async def _fake(self, key, params=None):
        keys.append(key)
        return "sent (test)"

    monkeypatch.setattr(coord_mod.Omoda9Coordinator, "async_send_command", _fake)
    return keys


def test_tilt_command_body(core):
    """Same endpoint as open/close, only `controlType` differs."""
    catalogue = dict(core["commands"].COMMANDS)
    assert catalogue["tetto_ventila"]["endpoint"] == "skylightControl"
    assert catalogue["tetto_ventila"]["body"] == {"controlType": "2", "skylightType": "1"}
    # open and close are untouched
    assert catalogue["tetto_apri"]["body"] == {"controlType": "1", "skylightType": "1"}
    assert catalogue["tetto_chiudi"]["body"] == {"controlType": "0", "skylightType": "1"}


def test_tilt_command_does_not_become_a_button():
    assert "tetto_ventila" in COMMANDS_AS_RICH_ENTITY


async def test_only_the_sunroof_supports_tilt(hass, integrazione_avviata):
    tilt = CoverEntityFeature.OPEN_TILT | CoverEntityFeature.CLOSE_TILT
    sunroof = hass.states.get(SUNROOF).attributes["supported_features"]
    assert sunroof & tilt == tilt
    for other in (TRUNK, WINDOWS):
        assert hass.states.get(other).attributes["supported_features"] & tilt == 0, other


async def test_open_tilt_sends_tilt_and_close_tilt_sends_close(hass, integrazione_avviata,
                                                                sent):
    await hass.services.async_call("cover", "open_cover_tilt",
                                   {"entity_id": SUNROOF}, blocking=True)
    assert sent == ["tetto_ventila"]
    assert hass.states.get(SUNROOF).state == "open", "tilted is shown as not closed"

    await hass.services.async_call("cover", "close_cover_tilt",
                                   {"entity_id": SUNROOF}, blocking=True)
    assert sent == ["tetto_ventila", "tetto_chiudi"]
    assert hass.states.get(SUNROOF).state == "closed"


async def test_full_open_is_unchanged(hass, integrazione_avviata, sent):
    await hass.services.async_call("cover", "open_cover",
                                   {"entity_id": SUNROOF}, blocking=True)
    assert sent == ["tetto_apri"]
