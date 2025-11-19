"""Regression tests for projection utilities."""
from __future__ import annotations

import numpy as np

from microlens_utils.frames import (
    convert_helio_geo_phot,
    geocentric_to_heliocentric_piE,
    heliocentric_to_geocentric_piE,
)


def test_piE_roundtrip_between_frames():
    """Heliocentric↔geocentric conversions should be mutual inverses."""
    ra = "17:45:40"
    dec = -29.0
    t0par = 60000.0
    piEE = 0.12
    piEN = -0.08
    tE = 28.0

    to_geo = heliocentric_to_geocentric_piE(ra, dec, t0par, piEE, piEN, tE)
    back_to_helio = geocentric_to_heliocentric_piE(ra, dec, t0par, *to_geo)
    np.testing.assert_allclose(back_to_helio[0], piEE, atol=1e-8)
    np.testing.assert_allclose(back_to_helio[1], piEN, atol=1e-8)
    np.testing.assert_allclose(back_to_helio[2], tE, rtol=1e-9)


def test_convert_helio_geo_phot_roundtrip():
    """Converting PSPL parameters helio→geo→helio should preserve inputs."""
    ra = "17:45:40"
    dec = -29.0
    params = dict(
        t0_in=60005.5,
        u0_in=0.1,
        tE_in=32.0,
        piEE_in=0.1,
        piEN_in=-0.05,
    )
    t0par = 60000.0

    geo = convert_helio_geo_phot(
        ra,
        dec,
        t0par=t0par,
        in_frame="helio",
        murel_out="SL",
        coord_in="EN",
        coord_out="EN",
        **params,
    )
    back = convert_helio_geo_phot(
        ra,
        dec,
        t0_in=geo[0],
        u0_in=geo[1],
        tE_in=geo[2],
        piEE_in=geo[3],
        piEN_in=geo[4],
        t0par=t0par,
        in_frame="geo",
        murel_out="SL",
        coord_in="EN",
        coord_out="EN",
    )

    np.testing.assert_allclose(back[0], params["t0_in"], atol=1e-6)
    np.testing.assert_allclose(back[1], params["u0_in"], atol=1e-6)
    np.testing.assert_allclose(back[2], params["tE_in"], atol=1e-6)
    np.testing.assert_allclose(back[3], params["piEE_in"], atol=1e-8)
    np.testing.assert_allclose(back[4], params["piEN_in"], atol=1e-8)
