"""Utilities to move between package-specific adapters via the canonical model."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Mapping, Optional, Tuple

from microlens_utils import adapters as _adapters  # noqa: F401  # ensure adapters register
from microlens_utils.adapters.base import get_adapter
from microlens_utils.models import BaseModel


@dataclass
class PackageHandle:
    """Lightweight wrapper around adapter output that proxies BaseModel attributes."""

    package: str
    params: Mapping[str, Any]
    model: BaseModel

    def __getattr__(self, name: str) -> Any:  # pragma: no cover - trivial proxy
        return getattr(self.model, name)


class Converter:
    """Coordinates adapters with the canonical BaseModel."""

    HandleKey = Tuple[str, Optional[str], Optional[str]]

    def __init__(
        self,
        model: BaseModel,
        source_package: str,
        source_params: Mapping[str, Any],
    ) -> None:
        self.model = model
        self.source_package = source_package
        self._handles: Dict[Converter.HandleKey, PackageHandle] = {}
        self._package_alias: Dict[str, PackageHandle] = {}
        self._cache_handle(
            source_package,
            source_params,
            observer=model.meta.get("observer"),
            origin=model.meta.get("origin"),
        )

    @staticmethod
    def _handle_key(
        package: str,
        observer: Optional[str],
        origin: Optional[str],
    ) -> "Converter.HandleKey":
        return (package, observer, origin)

    def _cache_handle(
        self,
        package: str,
        params: Mapping[str, Any],
        *,
        observer: Optional[str],
        origin: Optional[str],
    ) -> PackageHandle:
        handle = PackageHandle(package=package, params=dict(params), model=self.model)
        key = self._handle_key(package, observer, origin)
        self._handles[key] = handle
        self._package_alias[package] = handle
        return handle

    def get_handle(
        self,
        package: str,
        *,
        observer: Optional[str],
        origin: Optional[str],
    ) -> Optional[PackageHandle]:
        """Return the cached handle for a package if it exists."""
        return self._handles.get(self._handle_key(package, observer, origin))

    def to_package(
        self,
        package: str,
        *,
        observer: str,
        origin: Optional[str] = None,
    ) -> PackageHandle:
        """Dump the canonical model into the requested package format."""
        cached = self.get_handle(package, observer=observer, origin=origin)
        if cached is not None:
            return cached
        adapter_cls = get_adapter(package)
        params = adapter_cls.dump(self.model, observer=observer, origin=origin)
        return self._cache_handle(package, params, observer=observer, origin=origin)

    def dump(
        self,
        package: str,
        *,
        observer: str,
        origin: Optional[str] = None,
    ) -> Mapping[str, Any]:
        """Return just the package-native payload."""
        return self.to_package(package, observer=observer, origin=origin).params

    def __getattr__(self, name: str) -> Any:
        handle = self._package_alias.get(name)
        if handle is not None:
            return handle
        return getattr(self.model, name)


def converter(
    *,
    source: str,
    params: Mapping[str, Any],
    observer: str,
    epochs: Optional[Any] = None,
) -> Converter:
    """Factory function described in the README."""
    adapter_cls = get_adapter(source)
    model = adapter_cls.load(params=params, observer=observer, epochs=epochs)
    return Converter(model=model, source_package=source, source_params=params)
