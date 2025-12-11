"""BAGLE adapter."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, Mapping, Optional

from microlens_utils.adapters.base import AdapterError, BaseAdapter
from microlens_utils.models import BaseModel, FrameConfig, TimeSeries


class BagleAdapter(BaseAdapter):
    """Adapter that treats BAGLE payloads as the canonical representation."""

    package_name = "bagle"
    supported_observers = ("earth", "roman_l2")
    supported_origins = ("lens1@t0", "barycenter")
    required_scalars = ("t0", "tE", "u0_amp", "u0_sign")

    @classmethod
    def load(
        cls,
        params: Mapping[str, Any],
        observer: str,
        epochs: Optional[Any] = None,
    ) -> BaseModel:
        cls.ensure_observer(observer)
        normalized = cls._coerce_mapping(params)
        scalars = cls._extract_scalars(normalized)
        meta = dict(normalized.get("meta", {}))
        meta.setdefault("observer", observer)
        meta.setdefault("package", cls.package_name)
        if epochs is not None:
            meta.setdefault("epochs", epochs)
        frames = dict(normalized.get("frames", {}))
        series = dict(normalized.get("series", {}))

        model = BaseModel(
            scalars=scalars,
            meta=meta,
            series=series,
            frames=frames,
        )
        model.cache_package(
            cls.package_name,
            cls._serialize_payload(model, observer, meta.get("origin")),
        )
        return model

    @classmethod
    def dump(
        cls,
        model: BaseModel,
        observer: str,
        origin: Optional[str] = None,
    ) -> Mapping[str, Any]:
        cls.ensure_observer(observer)
        resolved_origin = origin or model.meta.get("origin")
        cls.ensure_origin(resolved_origin)
        payload = cls._serialize_payload(model, observer, resolved_origin)
        model.cache_package(cls.package_name, payload)
        return payload

    @classmethod
    def _extract_scalars(cls, normalized: Mapping[str, Any]) -> Dict[str, Any]:
        scalars = dict(normalized.get("scalars", {}))
        if not scalars:
            scalars = {
                key: normalized[key]
                for key in cls.required_scalars
                if key in normalized
            }
        missing = [field for field in cls.required_scalars if field not in scalars]
        if missing:
            raise AdapterError(
                f"BAGLE payload missing required scalars: {', '.join(missing)}"
            )
        return scalars

    @staticmethod
    def _serialize_series(series: TimeSeries) -> Dict[str, Any]:
        return {
            "epochs": series.epochs.tolist(),
            "values": series.values.tolist(),
            "coords": series.coords,
            "observer": series.observer,
            "origin": series.origin,
            "rest": series.rest,
            "projection": series.projection,
            "meta": dict(series.meta),
        }

    @classmethod
    def _serialize_frames(cls, model: BaseModel) -> Dict[str, Dict[str, Any]]:
        serialized: Dict[str, Dict[str, Any]] = {}
        for name, frame in model.frames.items():
            if isinstance(frame, FrameConfig):
                serialized[name] = asdict(frame)
            else:  # pragma: no cover - BaseModel already coerces to FrameConfig
                serialized[name] = dict(frame)
        return serialized

    @classmethod
    def _serialize_payload(
        cls,
        model: BaseModel,
        observer: str,
        origin: Optional[str],
    ) -> Dict[str, Any]:
        payload = {
            "scalars": dict(model.scalars),
            "meta": {
                **model.meta,
                "observer": observer,
                "origin": origin,
                "package": cls.package_name,
            },
        }
        if model.series:
            payload["series"] = {
                name: cls._serialize_series(series)
                for name, series in model.series.items()
            }
        if model.frames:
            payload["frames"] = cls._serialize_frames(model)
        return payload
