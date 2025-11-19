# Contributor Guide

This project is intentionally lightweight at v0.0.0: it provides a canonical
`Converter` facade, placeholder adapters, and enough scaffolding (tests, docs,
linting) to scale into the physics-heavy releases that follow.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev,docs]
```

Install the optional `adapters` extra if you have access to the external
microlensing packages required for end-to-end conversions.

## Python API

```python
from microlens_utils import converter

conv = converter(
    source="bagle",
    params={"scalars": {"t0": 55775.0, "u0": 0.1}},
    observer="earth",
)

bagle_payload = conv.dump("bagle", observer="earth")
gulls_handle = conv.to_package("gulls", observer="roman_l2")
print("t0 =", gulls_handle.t0)
print("native payload =", gulls_handle.params)
```

## CLI

The `microlens-utils` executable expects JSON payloads:

```bash
microlens-utils \
  --source bagle \
  --target gulls \
  --observer earth \
  --input smoke_bagle.json \
  --output gulls.json
```

The CLI echoes the canonical model (`scalars` + `meta`) when no target package
is provided.

## Tests & style

- Run `pytest` to exercise the rotation helpers.
- Run `ruff check .` to lint and `ruff format .` to auto-format.

## Documentation

Build the Read the Docs-compatible HTML locally using:

```bash
make -C docs html
```
