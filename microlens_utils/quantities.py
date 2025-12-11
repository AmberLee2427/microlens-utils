"""Custom quantity helpers for microlens-utils."""

from __future__ import annotations

from typing import Iterable, Optional

from astropy import units as u

thetaE_unit = u.def_unit("thetaE")


def _thetaE_equivalency(thetaE_mas: Optional[float]) -> Iterable[tuple[u.Unit, u.Unit, callable, callable]]:
    """Return the astropy equivalency mapping thetaE units to mas."""
    if thetaE_mas is None:
        return []
    thetaE_q = u.Quantity(thetaE_mas, u.mas)
    scale = thetaE_q.to_value(u.mas)
    return [
        (
            thetaE_unit,
            u.mas,
            lambda value: value * scale,
            lambda value: value / scale,
        )
    ]


class LensQuantity(u.Quantity):
    """Quantity subclass that knows how to convert in thetaE units."""

    _thetaE_mas: Optional[float] = None

    def __new__(cls, value, unit=None, thetaE_mas: Optional[float] = None, **kwargs):  # type: ignore[override]
        obj = super().__new__(cls, value, unit, **kwargs)
        obj._thetaE_mas = thetaE_mas
        return obj

    def _copy_with(self, quantity: u.Quantity) -> "LensQuantity":
        new = quantity.view(type(self))
        new._thetaE_mas = self._thetaE_mas
        return new

    def to(self, unit, equivalencies=None):  # type: ignore[override]
        eq = equivalencies or _thetaE_equivalency(self._thetaE_mas)
        result = super().to(unit, equivalencies=eq)
        if isinstance(result, LensQuantity):
            result._thetaE_mas = self._thetaE_mas
        return result

    def to_value(self, unit=None, equivalencies=None):  # type: ignore[override]
        eq = equivalencies or _thetaE_equivalency(self._thetaE_mas)
        return super().to_value(unit, equivalencies=eq)

    @property
    def mas(self) -> float:
        """Return the value expressed in milliarcseconds."""
        return float(self.to_value(u.mas))

    @property
    def deg(self) -> float:
        """Return the value expressed in degrees."""
        return float(self.to_value(u.deg))

    @property
    def rad(self) -> float:
        """Return the value expressed in radians."""
        return float(self.to_value(u.rad))

    @property
    def er(self) -> float:
        """Return the value expressed in thetaE units."""
        if self._thetaE_mas is None:
            raise ValueError("thetaE is not known; cannot convert to Einstein-radius units.")
        return float(self.to_value(thetaE_unit))

    def with_thetaE(self, thetaE_mas: Optional[float]) -> "LensQuantity":
        """Return a copy that carries a specific thetaE reference."""
        new = self.view(type(self))
        new._thetaE_mas = thetaE_mas
        return new
