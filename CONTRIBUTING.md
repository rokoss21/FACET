# Contributing to FACET

First off, thank you for considering contributing to FACET 🚀

## How to Contribute

- **Report Bugs** — use GitHub Issues with the *Bug Report* template.
- **Suggest Features** — open a Feature Request issue.
- **Submit PRs** — fork, branch, commit, and open a Pull Request with clear description.

## Development Setup

```bash
git clone https://github.com/rokoss21/FACET.git
cd FACET
python -m venv .venv && source .venv/bin/activate
pip install -e .[dev]
```

## Code Style

- Python 3.11+
- [PEP8](https://peps.python.org/pep-0008/) formatting (use `black`).
- Type hints required.
- Commit messages: Conventional Commits (`feat:`, `fix:`, `docs:`, etc.).

## Testing

FACET uses **golden tests**: each `.facet` file has a canonical `.json` output.

```bash
make examples    # regenerate json from examples/
pytest tests/    # run test suite
```

## Pull Requests

1. Fork & branch from `main`.
2. Keep commits atomic and well-described.
3. Ensure `make lint validate` passes before PR.
4. Reference related issues.

---
By contributing, you agree to abide by the [Code of Conduct](CODE_OF_CONDUCT.md).
