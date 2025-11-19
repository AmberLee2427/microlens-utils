"""VBMicrolensing adapter stub."""

from __future__ import annotations

from typing import Any, Mapping, Optional

from microlens_utils.adapters.base import BaseAdapter
from microlens_utils.models import BaseModel


class VBMicrolensingAdapter(BaseAdapter):
    """Minimal adapter that simply echoes canonical scalars."""

    package_name = "vbm"
    supported_observers = ("earth", "roman_l2")
    supported_origins = ("lens1@t0",)

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
        scalars = dict(model.scalars)
        scalars.setdefault("origin", origin or model.meta.get("origin"))
        return scalars
