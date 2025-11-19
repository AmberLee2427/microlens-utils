"""Heliocentric/geocentric conversions derived from BAGLE."""
from __future__ import annotations

from typing import Literal

import numpy as np
from astropy.coordinates import Angle
from astropy import units as u

from .vectors import convert_piEvec_tE, convert_u0vec_t0

FrameName = Literal["helio", "geo"]
MuRelName = Literal["SL", "LS"]
CoordName = Literal["EN", "tb"]


def _check_convert_inputs(
    t0_in: float,
    u0_in: float,
    tE_in: float,
    piEE_in: float,
    piEN_in: float,
    *,
    in_frame: FrameName,
    coord_in: CoordName,
    coord_out: CoordName,
    murel_in: MuRelName,
    murel_out: MuRelName,
) -> None:
    if in_frame not in {"helio", "geo"}:
        raise ValueError('in_frame must be "helio" or "geo"')
    if coord_in not in {"EN", "tb"} or coord_out not in {"EN", "tb"}:
        raise ValueError('coord_in/coord_out must be "EN" or "tb"')
    if murel_in not in {"SL", "LS"} or murel_out not in {"SL", "LS"}:
        raise ValueError('murel_in/murel_out must be "SL" or "LS"')
    if any(np.isnan(value) for value in (t0_in, u0_in, tE_in, piEE_in, piEN_in)):
        raise ValueError("conversion inputs must be finite numbers")


def convert_helio_geo_phot(
    ra: str | float,
    dec: str | float,
    t0_in: float,
    u0_in: float,
    tE_in: float,
    piEE_in: float,
    piEN_in: float,
    t0par: float,
    *,
    in_frame: FrameName = "helio",
    murel_in: MuRelName = "SL",
    murel_out: MuRelName = "LS",
    coord_in: CoordName = "EN",
    coord_out: CoordName = "tb",
) -> tuple[float, float, float, float, float]:
    """
    Convert BAGLE photometric parameters between heliocentric and geocentric frames.

    Parameters
    ----------
    ra, dec : str or float
        Event coordinates. Strings are interpreted as sexagesimal hour/degrees.
    t0_in : float
        Heliocentric or geocentric epoch of closest approach (MJD TDB).
    u0_in : float
        Impact parameter in theta_E units with BAGLE sign convention.
    tE_in : float
        Einstein crossing time (days) in the input frame.
    piEE_in, piEN_in : float
        Parallax components following the source-minus-lens (SL) convention.
    t0par : float
        Reference epoch for the geocentric projection (MJD TDB).
    in_frame : {'helio', 'geo'}
        Indicates whether ``t0_in``/``piE_in`` are heliocentric or geocentric.
    murel_in, murel_out : {'SL', 'LS'}
        Relative motion conventions for input/output frames. SL is the BAGLE default.
    coord_in, coord_out : {'EN', 'tb'}
        Coordinate conventions (fixed East/North vs. tau/beta basis).

    Returns
    -------
    tuple
        ``(t0_out, u0_out, tE_out, piEE_out, piEN_out)`` in the opposite frame.
    """
    _check_convert_inputs(
        t0_in,
        u0_in,
        tE_in,
        piEE_in,
        piEN_in,
        in_frame=in_frame,
        coord_in=coord_in,
        coord_out=coord_out,
        murel_in=murel_in,
        murel_out=murel_out,
    )

    if isinstance(ra, str):
        ra = str(Angle(ra, unit=u.hourangle))

    if murel_in == "LS":
        piEE_in *= -1
        piEN_in *= -1

    piEE_out, piEN_out, tE_out = convert_piEvec_tE(
        ra,
        dec,
        t0par,
        piEE_in,
        piEN_in,
        tE_in,
        in_frame=in_frame,
    )
    piE = np.hypot(piEE_in, piEN_in)
    tauhatE_in = piEE_in / piE
    tauhatN_in = piEN_in / piE
    tauhatE_out = piEE_out / piE
    tauhatN_out = piEN_out / piE

    if coord_in == "EN":
        sign_term = np.sign(u0_in * piEN_in)
        if sign_term < 0:
            u0hatE_in = -tauhatN_in
            u0hatN_in = tauhatE_in
        elif sign_term > 0:
            u0hatE_in = tauhatN_in
            u0hatN_in = -tauhatE_in
        else:
            if np.sign(u0_in * piEE_in) > 0:
                u0hatE_in = -tauhatN_in
                u0hatN_in = tauhatE_in
            else:
                u0hatE_in = tauhatN_in
                u0hatN_in = -tauhatE_in
    else:  # coord_in == "tb"
        if np.sign(u0_in) > 0:
            u0hatE_in = tauhatN_in
            u0hatN_in = -tauhatE_in
        else:
            u0hatE_in = -tauhatN_in
            u0hatN_in = tauhatE_in

    t0_out, u0vec_out = convert_u0vec_t0(
        ra,
        dec,
        t0par,
        t0_in,
        u0_in,
        tE_in,
        tE_out,
        piE,
        tauhatE_in,
        tauhatN_in,
        u0hatE_in,
        u0hatN_in,
        tauhatE_out,
        tauhatN_out,
        in_frame=in_frame,
    )

    u0_out = float(np.hypot(u0vec_out[0], u0vec_out[1]))
    if u0vec_out[0] < 0:
        u0_out *= -1

    if coord_out == "tb":
        cross_sign = np.sign(tauhatE_out * u0vec_out[1] - tauhatN_out * u0vec_out[0])
        u0_out = float(np.hypot(u0vec_out[0], u0vec_out[1]))
        if cross_sign < 0:
            u0_out = -u0_out

    if murel_out == "LS":
        piEE_out *= -1
        piEN_out *= -1

    return t0_out, u0_out, tE_out, piEE_out, piEN_out
