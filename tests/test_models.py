"""Unit tests for the canonical BaseModel and TimeSeries classes."""

from __future__ import annotations

import numpy as np
import pytest
from microlens_utils.frames import geocentric_to_heliocentric_piE
from microlens_utils.models import BaseModel, TimeSeries
from microlens_utils.quantities import LensQuantity, thetaE_unit


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


def test_get_series_requires_explicit_frame():
    """Requesting a series without specifying the frame should raise."""
    model = BaseModel(
        scalars=_scalars(),
        series={
            "centroid": TimeSeries(
                epochs=[0.0, 1.0],
                values=[[0.0, 0.0], [0.1, -0.1]],
                observer="earth",
                origin="lens1@t0",
                coords="lens_xy",
            )
        },
    )
    with pytest.raises(ValueError, match="requires explicit frame metadata"):
        model.get_series("centroid")


def test_get_series_reports_mismatched_frame():
    """Mismatched frames should produce a helpful error."""
    model = BaseModel(
        scalars=_scalars(),
        series={
            "centroid": TimeSeries(
                epochs=[0.0],
                values=[[0.0, 0.0]],
                observer="earth",
                origin="lens1@t0",
                coords="lens_xy",
            )
        },
    )
    with pytest.raises(ValueError, match="observer='roman_l2'"):
        model.get_series("centroid", observer="roman_l2")


def test_scalar_quantity_exposes_units():
    model = BaseModel(scalars=_scalars(thetaE=0.2, piEE=0.1))
    quantity = model.scalar_quantity("piEE")
    assert isinstance(quantity, LensQuantity)
    assert pytest.approx(quantity.er, rel=1e-9) == 0.1
    assert pytest.approx(quantity.mas, rel=1e-9) == 0.02
    assert pytest.approx(quantity.to_value(thetaE_unit), rel=1e-9) == 0.1


def test_piE_projection_conversion():
    scalars = _scalars(thetaE=0.2, piEE=0.1, piEN=0.05, tE=28.0)
    meta = {"raL": "17:45:40", "decL": -29.0, "t0_par": 60000.0}
    model = BaseModel(scalars=scalars, meta=meta)
    geo_e, geo_n = model.piE()
    helio_e, helio_n = model.piE(projection="heliocentric")
    assert isinstance(geo_e, LensQuantity)
    assert isinstance(helio_e, LensQuantity)
    assert pytest.approx(geo_e.er, rel=1e-9) == 0.1
    assert pytest.approx(geo_e.mas, rel=1e-9) == 0.02
    expected = geocentric_to_heliocentric_piE(
        meta["raL"], meta["decL"], meta["t0_par"], 0.1, 0.05, scalars["tE"]
    )
    assert pytest.approx(helio_e.er, rel=1e-9) == expected[0]
    assert pytest.approx(helio_n.er, rel=1e-9) == expected[1]
