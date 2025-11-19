"""Unit tests for the canonical BaseModel and TimeSeries classes."""

from __future__ import annotations

import numpy as np
import pytest
from microlens_utils.models import BaseModel, TimeSeries


def _scalars(**kwargs):
    scalars = {"t0": 60000.0, "tE": 20.0, "u0_amp": 0.1, "u0_sign": 1}
    scalars.update(kwargs)
    return scalars


def test_base_model_requires_canonical_fields():
    """Missing BAGLE scalars should trigger a validation error."""
    scalars = {"t0": 60000.0, "tE": 20.0}
    with pytest.raises(ValueError, match="Missing canonical BAGLE fields"):
        BaseModel(scalars=scalars)


def test_base_model_infers_psbl_family():
    """Presence of sep+q promotes the model to PSBL."""
    model = BaseModel(scalars=_scalars(sep=1.2, q=0.3))
    assert model.model_family == "PSBL"
    model = BaseModel(scalars=_scalars())
    assert model.model_family == "PSPL"


def test_time_series_validation_shapes():
    """Epoch/value length mismatches must raise."""
    with pytest.raises(ValueError, match="same leading dimension"):
        TimeSeries(epochs=[1.0, 2.0], values=[1.0])


def test_base_model_coerces_series_dicts():
    """Series payloads provided as dicts should be converted to TimeSeries."""
    model = BaseModel(
        scalars=_scalars(),
        series={
            "phot": {
                "epochs": np.arange(3, dtype=float),
                "values": np.ones(3),
                "coords": "icrs",
                "observer": "earth",
            }
        },
    )
    assert isinstance(model.series["phot"], TimeSeries)
    np.testing.assert_allclose(model.series["phot"].epochs, np.arange(3, dtype=float))
