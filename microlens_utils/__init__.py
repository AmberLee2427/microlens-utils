"""

```
microlens-utils/
├── microlens_utils/
│   ├── adapters/
│   │   ├── base.py         # input/output package interface
│   │   ├── gulls_adapter.py
│   │   ├── mm_adapter.py
│   │   ├── vbm_adapter.py
│   │   └── bagle_adapter.py
│   ├── frames/
│   │   ├── __init__.py
│   │   ├── projections.py  # coordinate projection utilities
│   │   └── rotations.py    # Roman/L2 rotation utilities (pure NumPy)
│   ├── converters.py       # orchestrates adapters + frames
│   ├── cli.py              # `microlens-utils` entry point
│   └── __init__.py
├── scripts/
│   └── bump_version.py
├── tests/
│   ├── test_rotations.py
│   ├── test_adapters.py
│   └── test_cli.py
├── README.md
├── pyproject.toml
└── CITATION.cff
```

"""
# version
__version__ = "0.0.0"