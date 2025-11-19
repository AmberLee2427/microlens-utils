"""Convenience wrappers around microlensing projection utilities."""
from __future__ import annotations

from typing import Tuple

from .bagle import convert_piEvec_tE


def heliocentric_to_geocentric_piE(
    ra: str | float,
    dec: str | float,
    t0par: float,
    piEE: float,
    piEN: float,
    tE: float,
) -> Tuple[float, float, float]:
    """
    Convert a heliocentric parallax vector into the geocentric-projected frame.

    Parameters
    ----------
    ra, dec : str or float
        Sky coordinates of the microlensing event.
    t0par : float
        Epoch defining the geocentric projection (MJD TDB).
    piEE, piEN : float
        Heliocentric parallax vector components (source minus lens).
    tE : float
        Einstein timescale in the heliocentric frame (days).

    Returns
    -------
    tuple
        ``(piEE_geo, piEN_geo, tE_geo)`` converted to the geocentric-projected frame.
    """
    return convert_piEvec_tE(ra, dec, t0par, piEE, piEN, tE, in_frame="helio")


def geocentric_to_heliocentric_piE(
    ra: str | float,
    dec: str | float,
    t0par: float,
    piEE: float,
    piEN: float,
    tE: float,
) -> Tuple[float, float, float]:
    """
    Convert a geocentric parallax vector into the heliocentric frame.

    Parameters
    ----------
    ra, dec : str or float
        Sky coordinates of the microlensing event.
    t0par : float
        Epoch defining the geocentric projection (MJD TDB).
    piEE, piEN : float
        Geocentric-projected parallax components (source minus lens).
    tE : float
        Einstein timescale measured in the geocentric frame (days).

    Returns
    -------
    tuple
        ``(piEE_helio, piEN_helio, tE_helio)`` converted to the heliocentric frame.
    """
    return convert_piEvec_tE(ra, dec, t0par, piEE, piEN, tE, in_frame="geo")
