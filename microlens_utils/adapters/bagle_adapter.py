"""Bagle adapter stub."""

from __future__ import annotations

from typing import Any, Mapping, Optional

from microlens_utils.adapters.base import BaseAdapter
from microlens_utils.models import BaseModel


class BagleAdapter(BaseAdapter):
    """Placeholder adapter that simply echoes the provided payload."""

    package_name = "bagle"
    supported_observers = ("earth", "roman_l2")
    supported_origins = ("lens1@t0", "barycenter")

    @classmethod
    def load(
        cls,
        params: Mapping[str, Any],
        observer: str,
        epochs: Optional[Any] = None,
    ) -> BaseModel:
        cls.ensure_observer(observer)
        return cls.build_model(params, observer=observer, epochs=epochs)

    @classmethod
    def dump(
        cls,
        model: BaseModel,
        observer: str,
        origin: Optional[str] = None,
    ) -> Mapping[str, Any]:
        cls.ensure_observer(observer)
        cls.ensure_origin(origin)
        payload = model.get_cached_package(cls.package_name)
        if payload is None:
            scalars = dict(model.scalars)
            payload = {
                "scalars": scalars,
                "meta": {
                    "observer": observer,
                    "origin": origin or model.meta.get("origin"),
                    "package": cls.package_name,
                },
            }
        return payload
