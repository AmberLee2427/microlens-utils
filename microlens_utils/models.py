"""Canonical microlensing data structures used by microlens-utils."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any, Mapping, MutableMapping, Optional

import numpy as np
from astropy import units as u
from numpy.typing import ArrayLike

from microlens_utils.frames import geocentric_to_heliocentric_piE
from microlens_utils.quantities import LensQuantity, thetaE_unit

CANONICAL_SCALARS = ("t0", "tE", "u0_amp", "u0_sign")
BINARY_FIELDS = ("sep", "q")
PARALLAX_FIELDS = ("piEE", "piEN")
MU_FIELDS = ("mu_rel_e", "mu_rel_n")

SCALAR_UNITS = {
    "t0": u.day,
    "tE": u.day,
    "thetaE": u.mas,
    "piEE": thetaE_unit,
    "piEN": thetaE_unit,
    "u0_amp": thetaE_unit,
    "mu_rel_e": u.mas / u.yr,
    "mu_rel_n": u.mas / u.yr,
}


@dataclass
class FrameConfig:
    """Explicit description of an observable's reference frame."""

    observer: str
    origin: Optional[str] = None
    rest: Optional[str] = None
    coords: Optional[str] = None
    projection: Optional[str] = None

    def key(self) -> tuple[str, Optional[str], Optional[str], Optional[str], Optional[str]]:
        """Return a tuple identifier for hashing comparisons."""
        return (self.observer, self.origin, self.rest, self.coords, self.projection)


@dataclass
class TimeSeries:
    """Per-epoch values annotated with frame metadata."""

    epochs: ArrayLike
    values: ArrayLike
    coords: Optional[str] = None
    observer: Optional[str] = None
    origin: Optional[str] = None
    rest: Optional[str] = None
    projection: Optional[str] = None
    meta: MutableMapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.epochs = np.atleast_1d(np.array(self.epochs, dtype=float))
        self.values = np.atleast_1d(np.array(self.values, dtype=float))
        if self.epochs.ndim != 1:
            raise ValueError("epochs must be a 1-D array of MJD samples")
        if self.values.shape[0] != self.epochs.shape[0]:
            raise ValueError("values must have the same leading dimension as epochs")
        self.meta = dict(self.meta)

    def copy(self) -> "TimeSeries":
        """Return a detached copy of the time series."""
        return replace(
            self,
            epochs=self.epochs.copy(),
            values=self.values.copy(),
            meta=dict(self.meta),
        )

    def frame_key(
        self,
        *,
        observer: Optional[str] = None,
        origin: Optional[str] = None,
        rest: Optional[str] = None,
        coords: Optional[str] = None,
        projection: Optional[str] = None,
    ) -> tuple[Optional[str], Optional[str], Optional[str], Optional[str], Optional[str]]:
        """Return a tuple representing the requested frame selection."""
        return (observer, origin, rest, coords, projection)

    def matches(
        self,
        *,
        observer: Optional[str] = None,
        origin: Optional[str] = None,
        rest: Optional[str] = None,
        coords: Optional[str] = None,
        projection: Optional[str] = None,
    ) -> bool:
        """Return True if the stored metadata matches the requested frame arguments."""

        def _eq(current: Optional[str], expected: Optional[str]) -> bool:
            if expected is None:
                return True
            return current == expected

        return all(
            _eq(current, expected)
            for current, expected in (
                (self.observer, observer),
                (self.origin, origin),
                (self.rest, rest),
                (self.coords, coords),
                (self.projection, projection),
            )
        )

    def frame_summary(self) -> str:
        """Return a human-readable description of the stored frame metadata."""
        return (
            f"observer={self.observer}, origin={self.origin}, rest={self.rest}, "
            f"coords={self.coords}, projection={self.projection}"
        )


@dataclass
class BaseModel:
    """Canonical BAGLE-like microlensing model."""

    scalars: MutableMapping[str, Any] = field(default_factory=dict)
    meta: MutableMapping[str, Any] = field(default_factory=dict)
    series: MutableMapping[str, TimeSeries] = field(default_factory=dict)
    frames: MutableMapping[str, FrameConfig] = field(default_factory=dict)
    package_cache: MutableMapping[str, Mapping[str, Any]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.scalars = dict(self.scalars)
        self.meta = dict(self.meta)
        self.series = {name: self._coerce_series(series) for name, series in self.series.items()}
        self.frames = {name: self._coerce_frame(frame) for name, frame in self.frames.items()}
        self.package_cache = dict(self.package_cache)
        self._validate_scalars()
        self._piE_cache: dict[str, tuple[float, float, float]] = {}

    @staticmethod
    def _coerce_series(series: Any) -> TimeSeries:
        if isinstance(series, TimeSeries):
            return series
        if isinstance(series, Mapping):
            return TimeSeries(**series)
        raise TypeError("Series entries must be TimeSeries instances or mapping-like definitions.")

    @staticmethod
    def _coerce_frame(frame: FrameConfig | Mapping[str, Any]) -> FrameConfig:
        if isinstance(frame, FrameConfig):
            return frame
        if isinstance(frame, Mapping):
            return FrameConfig(**frame)
        raise TypeError("Frame entries must be FrameConfig instances or mapping-like definitions.")

    def _thetaE_mas(self) -> Optional[float]:
        value = self.scalars.get("thetaE")
        if value is None:
            return None
        return float(value)

    def _make_quantity(self, name: str) -> LensQuantity:
        if name not in self.scalars:
            raise KeyError(f"Scalar '{name}' not present on the model.")
        unit = SCALAR_UNITS.get(name, u.dimensionless_unscaled)
        return LensQuantity(self.scalars[name], unit=unit, thetaE_mas=self._thetaE_mas())

    def _validate_scalars(self) -> None:
        missing = [field for field in CANONICAL_SCALARS if field not in self.scalars]
        if missing:
            raise ValueError(f"Missing canonical BAGLE fields: {', '.join(missing)}")
        if self.scalars["u0_sign"] not in (-1, 1):
            raise ValueError("u0_sign must be either +1 or -1 following BAGLE conventions.")

    @property
    def t0(self) -> Any:
        """Reference time of closest approach."""
        return self.scalars["t0"]

    @property
    def tE(self) -> Any:
        """Einstein crossing time."""
        return self.scalars["tE"]

    @property
    def model_family(self) -> str:
        """Return `PSBL` when binary parameters are provided, otherwise `PSPL`."""
        if all(self.scalars.get(field) is not None for field in BINARY_FIELDS):
            return "PSBL"
        return "PSPL"

    @property
    def has_parallax(self) -> bool:
        """Return True if parallax vector components are available."""
        return any(self.scalars.get(field) is not None for field in PARALLAX_FIELDS)

    @property
    def has_astrometry(self) -> bool:
        """Return True when a proper motion vector is provided."""
        return all(self.scalars.get(field) is not None for field in MU_FIELDS)

    @property
    def epochs(self) -> Optional[Any]:
        """Return canonical epochs array if provided."""
        if "epochs" in self.meta:
            return self.meta["epochs"]
        if self.series:
            return next(iter(self.series.values())).epochs
        return None

    def piE_vector(self) -> Optional[np.ndarray]:
        """Return the microlensing parallax vector as (E, N)."""
        if not self.has_parallax:
            return None
        return np.array(
            [self.scalars.get("piEE", 0.0), self.scalars.get("piEN", 0.0)],
            dtype=float,
        )

    def _piE_components(self, projection: str = "geocentric") -> tuple[float, float, float]:
        projection = projection.lower()
        if projection in self._piE_cache:
            return self._piE_cache[projection]
        if projection not in {"geocentric", "heliocentric"}:
            raise ValueError("projection must be 'geocentric' or 'heliocentric'")
        if projection == "geocentric":
            values = (
                float(self.scalars.get("piEE", 0.0)),
                float(self.scalars.get("piEN", 0.0)),
                float(self.scalars.get("tE", 0.0)),
            )
        else:
            required = ("raL", "decL", "t0_par")
            missing = [key for key in required if key not in self.meta]
            if missing:
                raise ValueError(
                    "Cannot convert piE without metadata keys: " + ", ".join(missing)
                )
            piEE_geo = float(self.scalars.get("piEE", 0.0))
            piEN_geo = float(self.scalars.get("piEN", 0.0))
            tE_geo = float(self.scalars.get("tE", 0.0))
            ra = self.meta["raL"]
            dec = self.meta["decL"]
            t0par = float(self.meta["t0_par"])
            piEE_helio, piEN_helio, tE_helio = geocentric_to_heliocentric_piE(
                ra,
                dec,
                t0par,
                piEE_geo,
                piEN_geo,
                tE_geo,
            )
            values = (float(piEE_helio), float(piEN_helio), float(tE_helio))
        self._piE_cache[projection] = values
        return values

    def piE(self, projection: str = "geocentric") -> tuple[LensQuantity, LensQuantity]:
        """Return piE components as quantities in the requested projection."""
        piEE, piEN, _ = self._piE_components(projection)
        thetaE = self._thetaE_mas()
        return (
            LensQuantity(piEE, unit=thetaE_unit, thetaE_mas=thetaE),
            LensQuantity(piEN, unit=thetaE_unit, thetaE_mas=thetaE),
        )

    def piEE(self, projection: str = "geocentric") -> LensQuantity:
        """Return a single piE component."""
        return self.piE(projection=projection)[0]

    def piEN(self, projection: str = "geocentric") -> LensQuantity:
        """Return the North piE component."""
        return self.piE(projection=projection)[1]

    def mu_rel_vector(self) -> Optional[np.ndarray]:
        """Return the relative proper motion vector as (E, N)."""
        if not self.has_astrometry:
            return None
        return np.array(
            [self.scalars["mu_rel_e"], self.scalars["mu_rel_n"]],
            dtype=float,
        )

    def cache_package(self, package: str, payload: Mapping[str, Any]) -> None:
        """Persist a package's dumped representation for reuse."""
        self.package_cache[package] = dict(payload)

    def get_cached_package(self, package: str) -> Optional[Mapping[str, Any]]:
        """Fetch cached adapter output if it exists."""
        return self.package_cache.get(package)

    def copy(self) -> "BaseModel":
        """Return a shallow copy of the canonical model."""
        return replace(
            self,
            scalars=dict(self.scalars),
            meta=dict(self.meta),
            series={name: ts.copy() for name, ts in self.series.items()},
            frames={name: replace(cfg) for name, cfg in self.frames.items()},
            package_cache=dict(self.package_cache),
        )

    def require_fields(self, *fields: str) -> None:
        """Ensure that the requested canonical fields are populated."""
        missing = [field for field in fields if self.scalars.get(field) is None]
        if missing:
            raise ValueError(f"Missing required fields for this operation: {', '.join(missing)}")

    def add_series(self, name: str, series: TimeSeries | Mapping[str, Any]) -> None:
        """Attach a time series to the model."""
        self.series[name] = self._coerce_series(series)

    def add_frames(self, frames: Mapping[str, FrameConfig | Mapping[str, Any]]) -> None:
        """Attach one or more frame configs."""
        for key, cfg in frames.items():
            self.frames[key] = self._coerce_frame(cfg)

    def scalar_quantity(self, name: str, unit: Optional[u.Unit] = None) -> LensQuantity:
        """Return a scalar wrapped as a LensQuantity, with optional unit conversion."""
        quantity = self._make_quantity(name)
        if unit is not None:
            quantity = quantity.to(unit)
        return quantity

    def u0(self) -> LensQuantity:
        """Return the signed impact parameter as a quantity."""
        u0_amp = self.scalars["u0_amp"]
        u0_sign = self.scalars.get("u0_sign", 1)
        value = float(u0_amp) * float(u0_sign)
        return LensQuantity(value, unit=thetaE_unit, thetaE_mas=self._thetaE_mas())

    def get_series(
        self,
        name: str,
        *,
        observer: Optional[str] = None,
        origin: Optional[str] = None,
        rest: Optional[str] = None,
        coords: Optional[str] = None,
        projection: Optional[str] = None,
    ) -> TimeSeries:
        """Return a time series that matches the requested frame metadata."""
        try:
            series = self.series[name]
        except KeyError as exc:  # pragma: no cover - simple passthrough
            raise KeyError(f"Series '{name}' not present on the model.") from exc

        if all(value is None for value in (observer, origin, rest, coords, projection)):
            raise ValueError(
                f"Series '{name}' requires explicit frame metadata. "
                f"Available frame: {series.frame_summary()}"
            )

        if series.matches(
            observer=observer,
            origin=origin,
            rest=rest,
            coords=coords,
            projection=projection,
        ):
            return series

        mismatches = []
        for attr_name, current, expected in (
            ("observer", series.observer, observer),
            ("origin", series.origin, origin),
            ("rest", series.rest, rest),
            ("coords", series.coords, coords),
            ("projection", series.projection, projection),
        ):
            if expected is None:
                continue
            if current != expected:
                mismatches.append((attr_name, expected, current))

        mismatch_summary = ", ".join(
            f"{attr}={expected!r} (stored {current!r})"
            for attr, expected, current in mismatches
        )
        raise ValueError(
            f"Series '{name}' does not match the requested frame "
            f"({mismatch_summary}). Available frame: {series.frame_summary()}"
        )
