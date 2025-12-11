# microlens-utils v0.2.0 Release Notes

**Release Date:** 2025-11-20

## Highlights

- BAGLE is now the first fully implemented adapter: `load()`/`dump()` convert real BAGLE payloads into the canonical `BaseModel`, cache the result, and serialize back out for downstream tools.
- `Converter` caches adapter payloads per `(package, observer, origin)` and exposes them via attribute access (`conv.bagle`, `conv.gulls`, …), so you always know which dictionary produced a conversion.
- `TimeSeries.get_series()` enforces explicit frame metadata (observer/origin/rest/coords/projection) and emits detailed errors whenever the request does not match the stored series.
- The documentation build now renders the BAGLE comparison notebook through `myst-nb`, giving readers a full worked example without running the code.

## Getting Started

1. `pip install -e .[dev,docs]` (or add `adapters` if you have the external packages available).
2. Use `microlens_utils.converter(...)` with `source="bagle"` to ingest BAGLE payloads – the new adapter is the canonical model, so conversions require no hacks.
3. Access cached payloads through attribute handles (`conv.bagle.params`, `conv.gulls.params`) to keep track of how each package was produced.
4. Visit the updated docs (`docs/examples.md`) for the rendered notebook walkthrough.

## Changelog

See [CHANGELOG.md](CHANGELOG.md#020---2025-11-20) for the complete list of commits in this release.

---

**Previous Release:** v0.1.1
