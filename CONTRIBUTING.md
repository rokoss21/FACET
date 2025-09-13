# Contributing to FACET

Thank you for your interest in contributing! We welcome issues, feature proposals, documentation improvements, and pull requests.

## Getting Started

- Fork the repo and create a feature branch from `main`.
- Use Python 3.9+ and create a virtual environment.
- Install dev dependencies and run tests:
  ```bash
  cd facet-lang
  python3 -m venv .venv
  ./.venv/bin/pip install -e . pytest
  ./.venv/bin/pytest -q
  ```

## Style & Quality

- Python: keep types clear, avoid deep nesting, follow readability-first style.
- Tests: add/adjust tests for any behavior changes.
- Lint/format (if configured) should pass before submitting a PR.

## Commit Messages

- Use conventional style where possible, e.g. `feat:`, `fix:`, `docs:`, `refactor:`.
- Keep messages concise and meaningful.

## Pull Requests

- One logical change per PR.
- Include a brief description of the motivation and approach.
- Reference related issues if applicable.

## Reporting Issues

- Provide steps to reproduce and expected vs actual behavior.
- Include environment details (OS, Python version).

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
