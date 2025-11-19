# microlens-utils Design Notes

_Last updated: September 2024_

This document describes the canonical model, adapter contract, and API shape for `microlens-utils`. It captures the current design decisions so contributors have a shared reference when touching adapters or frame utilities.

## Goals

1. **Canonical parameterisation** – everything flows through a single `BaseModel` that looks as close to the MulensModel schema as practical (t0, u0, tE, θE, πE, μ, distances, epochs, magnification, centroid tracks, etc.).
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
| `package_cache` | Optional cache where adapters can stash their native parameter dictionaries after conversion. This lets downstream code fetch e.g. `converter.bagle.params` without rerunning the adapter. |

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

Accessors such as `model.astrometric_centroid(...)` accept overrides (`coords`, `projection`, `origin`, `rest`, `observer`). If the requested combination does not exist, the accessor raises and suggests which frames are available.

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

- `load` takes a plain dictionary (the adapter is responsible for reading files if necessary) and returns a validated `BaseModel`.
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
4. Leaves the canonical `BaseModel` accessible via `Converter.model`.

To populate another package’s cache:

```python
gulls_model = conv.to_package("gulls", observer="roman_l2")
t0_gulls = gulls_model.t0
```

`to_package()` looks up the adapter, calls `adapter.dump(BaseModel, observer=...)`, and stores the result under `Converter.gulls`. Adapters are only run when requested.

## Frames module

`microlens_utils.frames` hosts:

- `rotations.py` – pure NumPy NE↔lens and TU↔XY rotation matrices (mirrors VBMicrolensing and GULLS conventions).
- `projections.py` – utilities for converting proper motions/parallaxes between heliocentric, geocentric, and spacecraft observers.

These helpers have no heavy dependencies beyond `astropy` and `astroquery` so they can be unit tested without touching BAGLE/VBM.

## Implementation roadmap

The `TODO.md` file tracks milestone-level work. Short version:

1. **v0.0.x** – skeleton (stubs, rotations, basic pytest, docs).
2. **v0.1.x** – canonical BaseModel + BaseAdapter + projection utilities + rotation tests.
3. **v0.2.x** – BAGLE adapter + end-to-end tests.
4. **v0.4.x** – GULLS photometry adapter + consistency tests.
5. **v0.5.x** – GULLS astrometry utilities.
6. **v0.7.x** – MulensModel adapter (if needed).
7. **v0.8.x** – pyLIMA adapter.
8. **v0.9.x** – Adapter authoring guide & tooling.

Additional notes live in `docs/` as needed.

