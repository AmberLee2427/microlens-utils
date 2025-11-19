# microlens-utils Design Notes

_Last updated: September 2024_

This document describes the canonical model, adapter contract, and API shape for `microlens-utils`. It captures the current design decisions so contributors have a shared reference when touching adapters or frame utilities.

## Goals

1. **Canonical parameterisation** – everything flows through a single `BaseModel` that mirrors BAGLE’s PSPL/PSBL schema (t0, u0_amp, tE, sep, q, α, πE, θE, μ components, distances, flux scales, astrometry/parallax flags). Model type (PSPL vs PSBL) is inferred deterministically from the supplied parameters.
2. **Adapter symmetry** – each supported package only needs to know how to map _to_ and _from_ the canonical model. No adapter depends on any other adapter.
3. **Strict frame control** – every quantity that depends on a frame/observer/origin must receive that context explicitly from the caller and validates it before returning anything.
4. **Python-first API** – the primary user interface is a Python object graph (`Converter → BaseModel → PackageAdapter`). A CLI can exist later, but it will be a thin wrapper around the Python API.

## BaseModel

The `BaseModel` dataclass represents the canonical “dad” model. Each instance contains:

| Field | Description |
| --- | --- |
| `meta` | Static info (event id, source/lens distances, θE, πE, observer metadata, epochs). |
| `scalars` | Scalar microlensing parameters (t0, u0, tE, α, β, μ components, πE components). |
| `series` | Dict of `TimeSeries` objects (e.g., source trajectory, blended centroid, magnification). The default series for each observable is accessible via convenience accessors. |
| `frames` | Known frame configs, e.g. `FrameConfig(observer="roman_l2", origin="lens1@t0", rest="lens")`. |

`BaseModel` validates all inputs on construction: missing scalars raise, series must have matching epochs, and frame configs must be mutually consistent.

### TimeSeries

`TimeSeries` encapsulates per-epoch data:

- `epochs`: numpy array of times (MJD TDB by default).
- `values`: numpy array (shape `(N,)` or `(N, 2)` depending on the observable).
- `coords`: string identifier (e.g., `"icrs"`, `"galactic"`, `"lens_xy"`).
- `projection`: string specifying the projection (`"heliocentric"`, `"geocentric"`, `None`).
- `rest`: which object or co-moving objects are at "rest" (`"source"`, `"lens"`, `"sky"`).
- `origin`: textual origin spec (`"lens1@t0"`, `"source_com"`, etc.).
- `observer`: which observer frame this series uses (`"earth"`, `"roman_l2"`, ...).

Accessors such as `model.astrometric_centroid(...)` accept overrides (`coords`, `projection`, `origin`, `rest`, `observer`). If the requested combination does not exist, the accessor raises and suggests which frames are available. Time-series data will live in `TimeSeries` instances, making it easy to query the same observable in multiple frames/observers.

## BaseAdapter

Adapters live in `microlens_utils.adapters`. Every adapter inherits from `BaseAdapter`, which enforces:

```python
class BaseAdapter(ABC):
    package_name: ClassVar[str]
    supported_observers: ClassVar[Sequence[str]]
    supported_origins: ClassVar[Sequence[str]]

    @classmethod
    @abstractmethod
    def load(cls, params: Mapping[str, Any], observer: str, epochs: np.ndarray | None) -> BaseModel:
        ...

    @classmethod
    @abstractmethod
    def dump(cls, model: BaseModel, observer: str, origin: str) -> Mapping[str, Any]:
        ...
```

- `load` takes a plain dictionary (the adapter is responsible for reading files if necessary) and returns a validated `BaseModel`. Adapters infer model type (PSPL/PSBL) from the provided keys and raise immediately if the inputs are inconsistent.
- `dump` takes a `BaseModel` plus frame info and emits a package-specific dictionary.
- Adapters may optionally implement helper methods (`load_series`, `load_meta`, …) but the contract above is the minimum.

Adapters should _never_ guess defaults: if the source package omitted a parameter that the canonical model requires, the adapter raises `AdapterError`.

## Converter API

The public entry point is `microlens_utils.converter`. It accepts:

```python
conv = converter(
    source="bagle",
    params=bagle_param_dict,
    observer="earth",
    epochs=epochs_mjd,  # optional
)
```

Internally, `converter`:

1. Resolves the adapter (`BagleAdapter`).
2. Calls `BagleAdapter.load(...)` to obtain a `BaseModel`.
3. Initializes `Converter.bagle` with the adapter’s native representation (cached for later).
4. Creates a typed package handle (`PackageHandle`) that is accessible as `Converter.<package>` so callers can reach package-specific attributes (`conv.gulls.rho`, `conv.bagle.params`, etc.) without digging through dicts.

`Converter` maintains a map of package handles. `to_package()` looks up the adapter, calls `adapter.dump(BaseModel, observer=...)`, and caches the resulting handle. Accessing `conv.bagle` (or any handle name) returns the cached `PackageHandle` if present.

## Frames module

`microlens_utils.frames` hosts:

- `rotations.py` – pure NumPy NE↔lens and TU↔XY rotation matrices (mirrors VBMicrolensing/GULLS conventions).
- `projections.py` – utilities for converting proper motions/parallaxes between heliocentric, geocentric, and spacecraft observers.
- `bagle.py` (planned) – refactored, numpydoc-documented versions of BAGLE’s `frame_convert.py` helpers. Rather than dragging in a 1k-line script, we will split their conversion math into composable functions (`convert_helio_geo_phot`, `convert_bagle_mulens_psbl_phot`, etc.) with clear signatures. Where BAGLE already exposes a suitable function we will wrap it directly; otherwise we will reimplement the math here (with attribution).

These helpers have no heavy dependencies beyond `astropy`, so they can be unit tested without touching BAGLE/VBM binaries.

## Implementation roadmap

The `TODO.md` file tracks milestone-level work. Short version:

1. **v0.0.x** – skeleton (stubs, rotation utility, basic pytest, docs scaffold).
2. **v0.1.x** – adopt BAGLE as canonical model; finish `BaseModel`/`BaseAdapter`, reorganise BAGLE conversion helpers into smaller modules with numpydoc docstrings, write TimeSeries scaffolding + rotation tests.
3. **v0.2.x** – thin BAGLE adapter (so that we can retain control over the base model should we choose to diverge from the pure BAGLE parameterization) + Converter handle cache (`conv.<package>` access) + BAGLE roundtrip tests.
4. **v0.3.x** – TimeSeries-backed accessors for astrometry/photometry; strict frame metadata on every series.
5. **v0.4.x** – GULLS photometry adapter + consistency tests against BAGLE/VBM.
6. **v0.5.x** – GULLS astrometry adapter once upstream astrometry is finalised.
7. **v0.6.x** – pyLIMA adapter using the shared BAGLE helpers; reproduce conversion notebook.
8. **v0.7.x** – MulensModel adapter; complete conversion unit tests across BAGLE/GULLS/pyLIMA/MM.
9. **v0.8.x** – CLI wrapper, release workflow, PyPI packaging.
10. **v0.9.x** – Adapter authoring guide & helper tooling.

Additional notes live in `docs/` as needed.
