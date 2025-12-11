"""Ensure built-in adapters register themselves."""

from __future__ import annotations

# Import adapter modules for their side effects (registry registration).
from . import bagle_adapter as _bagle_adapter  # noqa: F401
from . import gulls_adapter as _gulls_adapter  # noqa: F401
from . import mm_adapter as _mm_adapter  # noqa: F401
from . import vbm_adapter as _vbm_adapter  # noqa: F401

__all__ = ["_bagle_adapter", "_gulls_adapter", "_mm_adapter", "_vbm_adapter"]
