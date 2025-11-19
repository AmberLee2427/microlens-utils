"""Vector utilities adapted from BAGLE's `frame_convert.py`."""

from __future__ import annotations

from typing import Tuple

import numpy as np
from astropy import units as u
from astropy.coordinates import SkyCoord, get_body_barycentric_posvel
from astropy.time import Time

AU_PER_DAY_TO_KM_S = 1731.45683


def _basis_vectors(ra: str | float, dec: str | float) -> Tuple[np.ndarray, np.ndarray]:
    if isinstance(ra, str):
        coord = SkyCoord(ra, dec, unit=(u.hourangle, u.deg))
    else:
        coord = SkyCoord(ra, dec, unit=(u.deg, u.deg))
    direction = coord.cartesian.xyz.value
    north = np.array([0.0, 0.0, 1.0])
    east = np.cross(north, direction)
    east /= np.linalg.norm(east)
    north_proj = np.cross(direction, east)
    north_proj /= np.linalg.norm(north_proj)
    return east, north_proj


def _time_array(mjd: float | np.ndarray) -> Time:
    return Time(np.atleast_1d(mjd) + 2400000.5, format="jd", scale="tdb")


def parallax_vector(ra: str | float, dec: str | float, mjd: float | np.ndarray) -> np.ndarray:
    """
    Compute the Sun-observer projected separation vector at the supplied epochs.

    Parameters
    ----------
    ra, dec : str or float
        Target coordinates (ICRS). Strings may be passed in ``HH:MM:SS`` form.
    mjd : float or array-like
        Epoch(s) in MJD TDB.

    Returns
    -------
    numpy.ndarray
        Array of shape ``(N, 2)`` containing the projected (East, North) offsets in AU.
    """
    east, north = _basis_vectors(ra, dec)
    times = _time_array(mjd)
    pos, _ = get_body_barycentric_posvel("earth", times)
    pos_arr = pos.xyz.T.to(u.au).value
    if pos_arr.ndim == 1:
        pos_arr = pos_arr[np.newaxis, :]
    east_comp = pos_arr @ east
    north_comp = pos_arr @ north
    return np.column_stack((east_comp, north_comp))


def earth_projected_velocity(
    ra: str | float,
    dec: str | float,
    mjd: float,
) -> Tuple[float, float]:
    """
    Project Earth's barycentric velocity into East/North components.

    Parameters
    ----------
    ra, dec : str or float
        Target coordinates.
    mjd : float
        Epoch in MJD TDB.

    Returns
    -------
    tuple of float
        Velocity components ``(v_E, v_N)`` in km/s.
    """
    east, north = _basis_vectors(ra, dec)
    _, vel = get_body_barycentric_posvel("earth", _time_array(mjd))
    vel_arr = vel.xyz.T.to(u.km / u.s).value
    if vel_arr.ndim == 1:
        vel_arr = vel_arr[np.newaxis, :]
    dot_east = np.atleast_1d(vel_arr @ east)
    dot_north = np.atleast_1d(vel_arr @ north)
    v_east = float(dot_east[0])
    v_north = float(dot_north[0])
    return v_east, v_north


def convert_piEvec_tE(
    ra: str | float,
    dec: str | float,
    t0par: float,
    piEE_in: float,
    piEN_in: float,
    tE_in: float,
    *,
    in_frame: str = "helio",
) -> Tuple[float, float, float]:
    """
    Convert parallax vector components between heliocentric and geocentric frames.

    Parameters
    ----------
    ra, dec : str or float
        Event coordinates.
    t0par : float
        Reference epoch for the geocentric frame (MJD TDB).
    piEE_in, piEN_in : float
        East and North components (source - lens convention) in the ``in_frame`` frame.
    tE_in : float
        Einstein crossing time corresponding to the ``in_frame`` frame.
    in_frame : {'helio', 'geo'}
        Indicates whether the inputs are heliocentric or geocentric.

    Returns
    -------
    tuple
        ``(piEE_out, piEN_out, tE_out)`` converted to the opposite frame.
    """
    if in_frame not in {"helio", "geo"}:
        raise ValueError("in_frame must be 'helio' or 'geo'")
    piE = np.hypot(piEE_in, piEN_in)
    if piE == 0:
        raise ValueError("piE vector cannot be zero-length.")
    piE2 = piE**2
    vtildeN_in = piEN_in / (tE_in * piE2)
    vtildeE_in = piEE_in / (tE_in * piE2)
    vtildeN_in *= AU_PER_DAY_TO_KM_S
    vtildeE_in *= AU_PER_DAY_TO_KM_S

    v_Earth_E, v_Earth_N = earth_projected_velocity(ra, dec, t0par)
    if in_frame == "helio":
        vtildeN_out = -vtildeN_in - v_Earth_N
        vtildeE_out = -vtildeE_in - v_Earth_E
    else:
        vtildeN_out = -vtildeN_in + v_Earth_N
        vtildeE_out = -vtildeE_in + v_Earth_E

    vtilde_in = np.hypot(vtildeE_in, vtildeN_in)
    vtilde_out = np.hypot(vtildeE_out, vtildeN_out)
    e_out = -vtildeE_out / vtilde_out
    n_out = -vtildeN_out / vtilde_out
    piEE_out = piE * e_out
    piEN_out = piE * n_out
    tE_out = (vtilde_in / vtilde_out) * tE_in
    return piEE_out, piEN_out, tE_out


def convert_u0vec_t0(
    ra: str | float,
    dec: str | float,
    t0par: float,
    t0_in: float,
    u0_in: float,
    tE_in: float,
    tE_out: float,
    piE: float,
    tauhatE_in: float,
    tauhatN_in: float,
    u0hatE_in: float,
    u0hatN_in: float,
    tauhatE_out: float,
    tauhatN_out: float,
    *,
    in_frame: str = "helio",
) -> Tuple[float, np.ndarray]:
    """
    Convert the u0 vector and peak time between heliocentric and geocentric frames.

    Parameters
    ----------
    ra, dec : str or float
        Event coordinates.
    t0par : float
        Reference epoch of the geocentric frame (MJD).
    t0_in, u0_in, tE_in : float
        Canonical parameters in the input frame.
    tE_out : float
        Einstein crossing time in the output frame.
    piE : float
        Magnitude of the microlensing parallax vector.
    tauhat*, u0hat* : float
        Components of the tau (motion) and u (impact parameter) unit vectors
        in the input/output frames.
    in_frame : {'helio', 'geo'}
        Direction of conversion.

    Returns
    -------
    tuple
        ``(t0_out, u0_vector_out)`` where the vector is ``[E, N]`` in theta_E units.
    """
    par_vec = parallax_vector(ra, dec, np.array([t0par])).reshape(
        2,
    )
    u0vec_in = np.abs(u0_in) * np.array([u0hatE_in, u0hatN_in])
    tauhat_out = np.array([tauhatE_out, tauhatN_out])
    tauhat_in_vec = np.array([tauhatE_in, tauhatN_in])

    if in_frame == "helio":
        dp_dt = ((tauhat_in_vec / tE_in) - (tauhat_out / tE_out)) / piE
        vec = u0vec_in - piE * par_vec - (t0_in - t0par) * piE * dp_dt
        t0_out = t0_in - tE_out * np.dot(tauhat_out, vec)
        u0vec_out = (
            u0vec_in
            + tauhat_in_vec * (t0par - t0_in) / tE_in
            - tauhat_out * (t0par - t0_out) / tE_out
            - piE * par_vec
        )
    elif in_frame == "geo":
        dp_dt = -((tauhat_in_vec / tE_in) - (tauhat_out / tE_out)) / piE
        vec = u0vec_in + piE * par_vec + (t0_in - t0par) * piE * dp_dt
        t0_out = t0_in - tE_out * np.dot(tauhat_out, vec)
        u0vec_out = (
            u0vec_in
            + tauhat_in_vec * (t0par - t0_in) / tE_in
            - tauhat_out * (t0par - t0_out) / tE_out
            + piE * par_vec
        )
    else:
        raise ValueError('in_frame must be "helio" or "geo"')

    return t0_out, u0vec_out
