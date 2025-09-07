# Development Tools

This directory contains configuration files and scripts for development, testing, and building.

## Contents

```
tools/
├── Makefile              # Build and development tasks
├── tox.ini              # Multi-environment testing configuration
├── .pre-commit-config.yaml  # Moved to root for easier access
└── README.md            # This file
```

## Makefile

Common targets:
```bash
make install     # Install package in development mode
make lint        # Lint all FACET files
make validate    # Validate FACET files against schemas
make json        # Generate JSON from FACET examples
make clean       # Clean generated files
```

## tox.ini

Multi-environment testing configuration:
```bash
tox -e py39,py310,py311,py312  # Test on multiple Python versions
tox -e lint                   # Run linting tools
tox -e type                   # Run type checking
tox -e docs                   # Build documentation
```

## Pre-commit Hooks

Located in root directory for easier access. Install with:
```bash
pre-commit install
```

## Usage

Most tools are designed to be run from the project root:

```bash
# Run from project root
make lint
tox -e py311

# Or specify paths explicitly
python3 -m pytest tests/
python3 -m black src/facet/
```

## Adding New Tools

When adding new development tools:
1. Add configuration to appropriate file in `tools/`
2. Update this README
3. Consider adding to CI/CD pipeline if applicable
