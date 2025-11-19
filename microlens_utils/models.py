"""Canonical microlensing data structures used by microlens-utils."""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any, Mapping, MutableMapping, Optional

import numpy as np
from numpy.typing import ArrayLike

CANONICAL_SCALARS = ("t0", "tE", "u0_amp", "u0_sign")
BINARY_FIELDS = ("sep", "q")
PARALLAX_FIELDS = ("piEE", "piEN")
MU_FIELDS = ("mu_rel_e", "mu_rel_n")


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
