# Source Code

This directory contains the main source code for FACET.

## Structure

```
src/
├── facet/                 # Main Python package
│   ├── __init__.py       # Package initialization
│   ├── parser.py         # Core FACET parser
│   ├── lenses.py         # Lens transformation functions
│   ├── cli.py            # Command-line interface
│   ├── errors.py         # Custom exception classes
│   ├── pyproject.toml    # Package configuration
│   └── README-DEV.md     # Developer documentation
└── README.md             # This file
```

## Installation

### Development Mode
```bash
# From project root
pip install -e .

# Or from src directory
cd src
pip install -e .
```

### Production Mode
```bash
pip install facet-lang
```

## Package Configuration

The `pyproject.toml` file contains:
- Package metadata (name, version, authors)
- Dependencies and optional dependencies
- Build system configuration
- Tool configurations (Black, isort, MyPy, pytest)
- Entry points for CLI

## Development

See `src/facet/README-DEV.md` for detailed development information.
