"""Regression tests for the frame rotation helpers."""

from __future__ import annotations

import numpy as np
from microlens_utils.frames import (
    rotation_ne_to_xy,
    rotation_tu_to_xy,
    rotation_xy_to_ne,
    rotation_xy_to_tu,
)


def test_xy_to_tu_inverse():
    """The TU and XY transforms must be orthonormal pairs."""
    rotation = rotation_xy_to_tu(alpha_deg=35.0, sgn=1.0)
    inverse = rotation_tu_to_xy(alpha_deg=35.0, sgn=1.0)
    assert np.allclose(rotation @ inverse, np.eye(2))


def test_xy_to_ne_roundtrip():
    """Lens NE round-trips should preserve arbitrary vectors."""
    vec_xy = np.array([0.2, -1.4])
    rotation, diag = rotation_xy_to_ne(
        mu_rel_E=5.0,
        mu_rel_N=12.0,
        alpha_deg=20.0,
        sgn=1.0,
    )
    inverse, _ = rotation_ne_to_xy(
        mu_rel_E=5.0,
        mu_rel_N=12.0,
        alpha_deg=20.0,
        sgn=1.0,
    )
    ne = rotation @ vec_xy
    xy = inverse @ ne
    assert np.allclose(xy, vec_xy)
    assert diag["alpha_deg"] == 20.0
