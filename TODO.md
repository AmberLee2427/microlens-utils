Version 0.0.0

- [x] Stubs.
- [x] Rotation utility.
- [x] Basic pytest.
- [x] Version bumping automation.
- [x] CI.
- [x] Style checking.
- [x] Basic documentation (RtD, Sphinx build).

Version 0.1.0

- [x] Adopt BAGLE parameterisation for `BaseModel` (PSPL/PSBL inference, canonical fields).
- [x] Refactor BAGLE `frame_convert.py` into smaller modules with numpydoc docstrings.
- [x] Implement `TimeSeries` scaffolding (epochs + frame metadata).
- [x] Flesh out `BaseAdapter` contract + projection utilities + rotation/projection tests.

Version 0.1.1

- [x] Style checks with `Ruff`.

Version 0.2.0

- [ ] BAGLE adapter (load/dump canonical model) with round-trip tests. Should be fairly trivial with a BAGLE base model.
- [ ] Converter handle cache providing attribute-style access (`conv.bagle`, `conv.gulls`, …).
- [ ] Strict frame metadata validation on TimeSeries accessors.
- [ ] Usage example notebook (icorporated into docs build).

Version 0.3.0

- [ ] GULLS photometry adapter; ensure consistency with BAGLE/VBM.
- [ ] Reproduce the conversion notebook with BAGLE↔GULLS examples.

Version 0.4.0

- [ ] GULLS astrometry adapter (after upstream astrometry is finalised).
- [ ] TimeSeries-backed astrometric utilities (observer/origin aware).

Version 0.5.0

- [ ] pyLIMA adapter using shared BAGLE conversion helpers.
- [ ] Reproduce `docs/example_compare_packages.ipynb` with BAGLE/pyLIMA.

Version 0.6.0

- [ ] MulensModel adapter (if still needed once pyLIMA exists).
- [ ] Complete conversion unit tests across BAGLE/GULLS/pyLIMA/MulensModel/VBM.

Version 0.7.0

- [ ] CLI thin wrapper + CLI tests.
- [ ] Release workflow + PyPI publishing.
- [ ] Zenodo

Version 0.8.0

- [ ] Adapter authoring guide & helper tooling (templates, docs).
