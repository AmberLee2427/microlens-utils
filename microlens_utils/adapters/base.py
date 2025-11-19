"""Input/output package interface and base parameterization adapters."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, ClassVar, Dict, Mapping, MutableMapping, Optional, Type

from microlens_utils.models import BaseModel, FrameConfig


class AdapterError(RuntimeError):
    """Raised when an adapter cannot satisfy the requested conversion."""


class BaseAdapter(ABC):
    """Abstract contract all package adapters must implement."""

    package_name: ClassVar[str]
    supported_observers: ClassVar[tuple[str, ...]] = ()
    supported_origins: ClassVar[tuple[Optional[str], ...]] = ()
    registry: ClassVar[Dict[str, Type["BaseAdapter"]]] = {}

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        package = getattr(cls, "package_name", None)
        if package:
            BaseAdapter.registry[package] = cls

    @classmethod
    def ensure_observer(cls, observer: str) -> None:
        """Ensure the requested observer is supported."""
        if cls.supported_observers and observer not in cls.supported_observers:
            raise AdapterError(
                f"{cls.package_name} adapter does not support observer '{observer}'. "
                f"Supported observers: {cls.supported_observers}"
            )

    @classmethod
    def ensure_origin(cls, origin: Optional[str]) -> None:
        """Ensure the requested origin is supported."""
        if origin is None:
            return
        if cls.supported_origins and origin not in cls.supported_origins:
            raise AdapterError(
                f"{cls.package_name} adapter does not support origin '{origin}'. "
                f"Supported origins: {cls.supported_origins}"
            )

    @classmethod
    def _coerce_mapping(cls, payload: Mapping[str, Any]) -> MutableMapping[str, Any]:
        if not isinstance(payload, Mapping):
            raise AdapterError("Adapter payloads must be mapping-like objects.")
        return dict(payload)

    @classmethod
    def build_model(
        cls,
        params: Mapping[str, Any],
        observer: str,
        epochs: Optional[Any],
    ) -> BaseModel:
        """Normalize raw params into a BaseModel."""
        normalized = cls._coerce_mapping(params)
        meta = dict(normalized.get("meta", {}))
        meta.setdefault("package", cls.package_name)
        meta.setdefault("observer", observer)
        if epochs is not None:
            meta["epochs"] = epochs
        scalars = dict(normalized.get("scalars", {}))
        if not scalars and "t0" in normalized:
            scalars["t0"] = normalized["t0"]
        frames = {
            "native": FrameConfig(
                observer=observer,
                origin=meta.get("origin"),
                rest=meta.get("rest"),
                coords=meta.get("coords"),
                projection=meta.get("projection"),
            )
        }
        model = BaseModel(
            scalars=scalars,
            meta=meta,
            series=dict(normalized.get("series", {})),
            frames=frames,
        )
        return model

    @classmethod
    @abstractmethod
    def load(
        cls,
        params: Mapping[str, Any],
        observer: str,
        epochs: Optional[Any],
    ) -> BaseModel:
        """Convert native params into the canonical BaseModel."""

    @classmethod
    @abstractmethod
    def dump(
        cls,
        model: BaseModel,
        observer: str,
        origin: Optional[str],
    ) -> Mapping[str, Any]:
        """Emit package-native parameters from a BaseModel."""


def get_adapter(package: str) -> Type[BaseAdapter]:
    """Resolve the adapter class for a given package."""
    try:
        return BaseAdapter.registry[package]
    except KeyError as exc:
        raise AdapterError(f"No adapter registered for package '{package}'.") from exc
