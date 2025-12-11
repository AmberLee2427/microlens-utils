"""Tests for the BAGLE adapter."""

from __future__ import annotations

import numpy as np
import pytest
from microlens_utils.adapters.bagle_adapter import BagleAdapter
from microlens_utils.adapters.base import AdapterError


def _payload():
    return {
        "scalars": {
            "t0": 60000.0,
            "tE": 25.0,
            "u0_amp": 0.1,
            "u0_sign": 1,
            "piEE": 0.12,
            "piEN": -0.04,
        },
        "meta": {
            "origin": "lens1@t0",
            "event": "demo",
        },
        "series": {
            "source_track": {
                "epochs": np.array([59990.0, 60010.0]),
                "values": np.array([[0.0, 0.0], [0.1, -0.05]]),
                "coords": "lens_xy",
                "observer": "earth",
                "origin": "lens1@t0",
                "rest": "source",
            }
        },
    }


def test_load_requires_scalars():
    """Missing scalar payloads should raise."""
    with pytest.raises(AdapterError, match="missing required scalars"):
        BagleAdapter.load({}, observer="earth")


def test_round_trip_dump_updates_scalars():
    """Modified canonical values should propagate back to BAGLE payloads."""
    payload = _payload()
    model = BagleAdapter.load(payload, observer="earth")
    assert model.scalars["t0"] == 60000.0

    model.scalars["t0"] = 60001.0
    dumped = BagleAdapter.dump(model, observer="earth", origin="lens1@t0")
    assert dumped["scalars"]["t0"] == 60001.0
    assert dumped["meta"]["observer"] == "earth"
    assert dumped["meta"]["origin"] == "lens1@t0"

    # Ensure the time series survived and was serialized cleanly.
    assert "series" in dumped
    series_payload = dumped["series"]["source_track"]
    assert series_payload["coords"] == "lens_xy"
