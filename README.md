# microlens-utils

Microlensing toolchains all describe the same physics, but each one uses its own file formats, reference frames, and reparameterization hacks. `microlens-utils` is the glue layer that lets you move an event description from one package to another (GULLS → BAGLE → VBMicrolensing → …) without hand-editing headers or quietly changing frames. You declare the input package + frame, the output package + frame, and the utility does the bookkeeping.

```
from microlens_utils import converter

bagle_model = converter(
    source="bagle",
    params=bagle_dict,
    observer="earth",
)
gulls_model = bagle_model.to_package("gulls", observer="roman_l2")
t0_gulls = gulls_model.t0
mu_rel_icrs = gulls_model.mu_rel(coords="icrs", projection="heliocentric")
```

Every transformation is deterministic, frame-aware, and fail-fast—if a parameter can’t be mapped, the converter ALWAYS raises instead of guessing.

## Features

- **Adapters with a common contract** – each supported package subclasses `BaseAdapter` and knows how to `load()` its native files into a `BaseModel` and `dump()` back out.
- **Frame-aware accessors** – model properties (e.g., `mu_rel`, `source_traj`, `centroid`) require explicit `coords`, `projection`, `rest`, and `origin` arguments whenever the frame matters. No implicit defaults.
- **Rotation + projection utilities** – reusable NE↔lens and sky↔observer transforms that match the VBMicrolensing/GULLS/BAGLE conventions.
- **Python-first API** – provide parameter dictionaries directly to `converter(...)`; adapters and frame transforms run strictly in Python (no mandatory file IO or CLI usage).
- **Strict validation** – adapters enforce unit, frame, and metadata checks; missing values or inconsistent reference frames raise immediately.

## Quickstart

### Install

```bash
git clone https://github.com/<org>/microlens-utils.git
cd microlens-utils
pip install --editable .
```

Python 3.10+ is required. Install with `pip install -e .[dev,docs]` if you plan to run
tests, style checks, or build the documentation locally.

### Python example

```python
from microlens_utils import converter

conv = converter(
    source="gulls",
    params=gulls_dict,
    observer="roman_l2",
    epochs=epochs_mjd,
)

bagle_model = conv.to_package("bagle", observer="earth")
sky_track = bagle_model.source_traj(
    coords="icrs",
    projection="geocentric",
    rest="source",
    origin="lens1@t0",
)
```

See `docs/DESIGN.md` for deeper detail on the types below.

## Concepts

- **BaseModel** – canonical dataclass holding physics (t0, u0, θE, μ, parallax, frames, epochs). All adapters produce/consume this form.
- **BaseAdapter** – abstract class adapters inherit; guarantees consistent `load()`/`dump()`/`supports()` APIs.
- **FrameConfig** – explicit observer/origin/rest-frame definition (e.g., `observer="roman_l2"`, `origin="lens1@t0"`, `rest="source"`). Every accessor that depends on frames requires a config.
- **Adapters** – located under `microlens_utils.adapters`. Current stubs: `gulls`, `bagle`, `vbm`, `mm`. Each validates its inputs before emitting a `BaseModel`.
- **Frames** – numeric transforms live in `microlens_utils.frames` (`rotations.py`, `projections.py`). They are pure NumPy functions so they can be tested without heavy deps.

## Adding a new adapter

1. Subclass `BaseAdapter` in `microlens_utils/adapters/<package>_adapter.py`.
2. Implement `load(raw_params, observer, epochs)` to return a `BaseModel`.
3. Implement `dump(model, frame_config)` to emit the package’s native dict/rows.
4. Declare supported frames/observers (e.g., `{"observer": ["earth", "roman_l2"], "origin": ["lens1@t0"]}`).
5. Add tests under `tests/test_<package>_adapter.py`.

## Testing

```bash
python -m pytest
```

If you only need to exercise the frame math:

```bash
python -m pytest tests/test_rotations.py -k rotations
```

Note: some adapters depend on external binaries (VBMicrolensing, BAGLE). Those tests are marked and skipped unless the corresponding environment variables are set.

Run `ruff check .` for style/linting.

## Documentation

The docs directory contains a Read the Docs compatible Sphinx project. Build it locally with:

```bash
make -C docs html
```

## Contributing

See `CONTRIBUTING.md`. The TL;DR: strict linting, fail-fast, no hidden defaults. Adapters must never fabricate physics values if the source is missing.

## Citation

See `CITATION.cff`.

## Acknowledgements

NASA • RGES_PIT • The Ohio State University
