"""Sphinx configuration for microlens-utils."""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def _get_version() -> str:
    try:
        from microlens_utils import __version__
    except Exception:  # pragma: no cover - docs build-time fallback
        return "0.0.0"
    return __version__


project = "microlens-utils"
author = "Amber Malpas"
copyright = f"{datetime.now():%Y}, {author}"  # noqa: A003 - sphinx expects the name "copyright"
version = release = _get_version()

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.autosectionlabel",
]

templates_path = ["_templates"]
exclude_patterns: list[str] = ["_build"]
myst_enable_extensions = ["colon_fence", "deflist"]

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
