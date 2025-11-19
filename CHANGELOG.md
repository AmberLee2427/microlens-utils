
## [0.1.0] - 2025-11-19

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


## [0.0.0] - 2025-11-18

Add CI workflow, package stubs, and initial documentation structure

- Created a GitHub Actions CI workflow for testing and linting.
- Updated README.md to clarify transformation behavior and installation instructions.
- Enhanced TODO.md with version milestones and completed tasks.
- Introduced DESIGN.md to outline the architecture and goals of microlens-utils.
- Added Makefile for building documentation and cleaning build artifacts.
- Implemented Sphinx configuration in conf.py for documentation generation.
- Added guide.md for contributor instructions and usage examples.
- Created index.md for the main documentation entry point.
- Refactored __init__.py to expose public package exports.
- Developed Bagle, GULLS, MulensModel, and VBMicrolensing adapter stubs.
- Established a base adapter interface with error handling.
- Implemented frame configuration and canonical model structures.
- Created command-line interface for microlens-utils with JSON input/output.
- Enhanced converters to facilitate package-specific conversions.
- Added tests for frame rotation helpers to ensure correctness.
- Updated pyproject.toml to include optional dependencies and scripts.
- Fixed paths in bump_version.py for documentation updates.
