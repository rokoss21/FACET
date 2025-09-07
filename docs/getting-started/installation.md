# Installation

This guide will help you install FACET and get it running on your system.

## Requirements

- **Python**: 3.9 or higher
- **Operating System**: Linux, macOS, or Windows

## Quick Install

=== "pip (Recommended)"

    ```bash
    # Install from PyPI (when available)
    pip install facet-lang
    ```

=== "Development Install"

    ```bash
    # Clone the repository
    git clone https://github.com/rokoss21/FACET.git
    cd FACET

    # Install in development mode
    pip install -e facet[dev]
    ```

=== "Docker"

    ```bash
    # Pull and run the FACET container
    docker run -it --rm ghcr.io/rokoss21/facet:latest
    ```

## Verify Installation

After installation, verify that FACET is working correctly:

```bash
# Check version
facet --version

# Test basic functionality
echo '@user\n  message: "Hello!"' | facet to-json
```

You should see:

```json
{
  "user": {
    "message": "Hello!"
  }
}
```

## Development Setup

For contributors and developers:

```bash
# Clone repository
git clone https://github.com/rokoss21/FACET.git
cd FACET

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install with all development dependencies
pip install -e facet[all]

# Install pre-commit hooks
pre-commit install

# Run tests
pytest tests/
```

## Troubleshooting

### Import Error

If you get an import error, try reinstalling:

```bash
pip uninstall facet-lang
pip install -e facet
```

### Command Not Found

If `facet` command is not found:

```bash
# Add to PATH
export PATH="$HOME/.local/bin:$PATH"

# Or use Python module directly
python -m facet.cli --help
```

### Permission Issues

If you get permission errors during installation:

```bash
# Install with user flag
pip install --user -e facet

# Or use sudo (not recommended)
sudo pip install -e facet
```

## Next Steps

Once installed, you can:

- [Follow the Quick Start guide](./quick-start.md)
- [Learn about CLI usage](./cli.md)
- [Explore the Python API](../api/python.md)
