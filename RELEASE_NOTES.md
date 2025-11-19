# Gulls v0.1.0 Release Notes

**Release Date:** 2025-11-19

## Minor Release


### Added
- Adopted BAGLE-style canonical scalars in `BaseModel` with PSPL/PSBL inference helpers.
- Introduced the `TimeSeries` container and validation plus new projection utilities/tests.
- Ported BAGLE `frame_convert.py` math into `microlens_utils.frames.bagle` with numpydoc docs.

### Changed  
- Strengthened the base adapter contract to normalize metadata/frames consistently.

### Fixed
- N/A

### Security
- N/A
## What's New

This release includes the following changes:

## What's Included

- **Source code**: Complete Gulls source with CMake build system
- **Binaries**: Linux executables (GSL fallbacks - testing only)
- **Documentation**: Built HTML documentation
- **Smoke test plots**: Visual proof that the release works

## Getting Started

1. **Install Gulls** - See the [Installation Guide](https://gulls.readthedocs.io/en/latest/install_gulls.html)
2. **Validate your inputs** - Use `python scripts/validate_inputs.py your_file.prm`
3. **Run simulations** - See the [Running Guide](https://gulls.readthedocs.io/en/latest/run_simulations.html)

## Full Changelog

See [CHANGELOG.md](CHANGELOG.md) for the complete list of changes.

---

**Previous Release:** v0.1.0