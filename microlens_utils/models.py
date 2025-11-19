"""Canonical microlensing data structures used by microlens-utils."""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any, Mapping, MutableMapping, Optional


@dataclass
class FrameConfig:
    """Explicit description of a frame/origin/rest definition for observables."""

    observer: str
    origin: Optional[str] = None
    rest: Optional[str] = None
    coords: Optional[str] = None
    projection: Optional[str] = None


@dataclass
class BaseModel:
    """Minimal canonical model that adapters can emit/consume."""

    scalars: MutableMapping[str, Any] = field(default_factory=dict)
    meta: MutableMapping[str, Any] = field(default_factory=dict)
    series: MutableMapping[str, Any] = field(default_factory=dict)
    frames: MutableMapping[str, FrameConfig] = field(default_factory=dict)
    package_cache: MutableMapping[str, Mapping[str, Any]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.meta = dict(self.meta)
        self.scalars = dict(self.scalars)
        self.series = dict(self.series)
        self.frames = dict(self.frames)
        self.package_cache = dict(self.package_cache)

    @property
    def t0(self) -> Any:
        """Convenience accessor for t0 if the adapter provided it."""
        return self.scalars.get("t0")

    @property
    def epochs(self) -> Any:
        """Return epochs metadata if provided."""
        return self.meta.get("epochs")

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
            series=dict(self.series),
            frames=dict(self.frames),
            package_cache=dict(self.package_cache),
        )
