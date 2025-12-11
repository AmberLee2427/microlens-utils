"""Tests for the Converter handle cache."""

from __future__ import annotations

from microlens_utils import converter


def _bagle_payload():
    return {
        "scalars": {
            "t0": 60000.0,
            "tE": 25.0,
            "u0_amp": 0.1,
            "u0_sign": 1,
        },
        "meta": {
            "origin": "lens1@t0",
        },
    }


def test_converter_attribute_handles():
    """Package handles should be addressable via attribute access."""
    conv = converter(source="bagle", params=_bagle_payload(), observer="earth")
    assert conv.bagle.params["scalars"]["t0"] == 60000.0

    gulls_handle = conv.to_package("gulls", observer="earth")
    assert conv.gulls is gulls_handle
    assert gulls_handle.params["scalars"]["t0"] == 60000.0

    second = conv.to_package("gulls", observer="earth")
    assert second is gulls_handle
