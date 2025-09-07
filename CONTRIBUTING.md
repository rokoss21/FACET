# 🤝 Contributing to FACET

Thank you for your interest in contributing to FACET! We welcome contributions from developers of all skill levels and backgrounds. This document provides guidelines and information to help you get started.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Running Tests](#running-tests)
- [Code Style](#code-style)
- [Submitting Changes](#submitting-changes)
- [Reporting Issues](#reporting-issues)
- [Documentation](#documentation)

## 🤝 Code of Conduct

This project follows a code of conduct to ensure a welcoming environment for all contributors. By participating, you agree to:

- Be respectful and inclusive
- Focus on constructive feedback
- Accept responsibility for mistakes
- Show empathy towards other contributors
- Help create a positive community

## 🚀 How to Contribute

### Types of Contributions

- **🐛 Bug Reports**: Report bugs and help us improve stability
- **✨ Feature Requests**: Suggest new features or improvements
- **📖 Documentation**: Improve documentation, add examples, or fix typos
- **🛠️ Code Contributions**: Submit pull requests with bug fixes or new features
- **🎯 Testing**: Add tests or improve test coverage
- **📣 Community**: Help answer questions and support other users

### Getting Started

1. **Fork** the repository on GitHub
2. **Clone** your fork locally
3. **Create** a new branch for your changes
4. **Make** your changes following our guidelines
5. **Test** your changes thoroughly
6. **Submit** a pull request

## 🛠️ Development Setup

### Prerequisites

- Python 3.9 or higher
- Git
- (Optional) Make for using development scripts

### Local Development Setup

```bash
# 1. Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/FACET.git
cd FACET

# 2. Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install in development mode
pip install -e .[dev,docs]

# 4. Verify installation
facet --help
```

### Development Tools Setup

```bash
# Install pre-commit hooks for code quality
pre-commit install

# Run pre-commit on all files
pre-commit run --all-files
```

## 🧪 Running Tests

### Run All Tests

```bash
# Run the full test suite
pytest

# Run with coverage report
pytest --cov=facet --cov-report=html

# Run specific test file
pytest tests/test_golden.py

# Run tests in verbose mode
pytest -v
```

### Test Categories

- **Unit Tests**: `pytest tests/ -k "unit"`
- **Integration Tests**: `pytest tests/ -k "integration"`
- **Golden Tests**: `pytest tests/test_golden.py`
- **Roundtrip Tests**: `pytest tests/test_roundtrip.py`

### Adding New Tests

1. Add test files to the `tests/` directory
2. Follow the naming convention: `test_*.py`
3. Use descriptive test function names
4. Include docstrings explaining what each test validates

## 💅 Code Style

### Python Code Style

We follow these style guidelines:

```python
# ✅ Good: Descriptive names, clear structure
def parse_facet_document(content: str) -> dict:
    """Parse FACET content into a dictionary structure."""
    # Implementation here
    pass

# ❌ Avoid: Abbreviations, unclear names
def pfd(c: str) -> dict:
    # What does this do?
    pass
```

### Key Guidelines

- **PEP 8**: Follow Python's official style guide
- **Type Hints**: Use type annotations for function parameters and return values
- **Docstrings**: Write clear, descriptive docstrings for all public functions
- **Descriptive Names**: Use meaningful variable and function names
- **Consistent Formatting**: Use consistent indentation and spacing

### Automated Code Quality

```bash
# Format code with Black
black src/facet/

# Sort imports with isort
isort src/facet/

# Lint with flake8
flake8 src/facet/

# Type check with mypy
mypy src/facet/
```

## 📝 Submitting Changes

### Pull Request Process

1. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/issue-number-description
   ```

2. **Make Your Changes**
   - Write clear, focused commits
   - Test your changes thoroughly
   - Update documentation if needed
   - Add tests for new functionality

3. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat: add new lens function

   - Add support for custom lens functions
   - Include validation for lens parameters
   - Add comprehensive test coverage

   Closes #123"
   ```

4. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then create a Pull Request on GitHub

### Commit Message Guidelines

We follow conventional commit format:

```
type(scope): description

[optional body]

[optional footer]
```

**Types:**
- `feat`: New features
- `fix`: Bug fixes
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test additions/changes
- `chore`: Maintenance tasks

**Examples:**
```
feat: add JSON Schema validation support
fix: resolve issue with multiline string parsing
docs: update installation instructions
test: add comprehensive test suite for lenses
```

### Pull Request Guidelines

- **Title**: Clear, descriptive title following commit conventions
- **Description**: Explain what changes were made and why
- **Testing**: Describe how the changes were tested
- **Screenshots**: Include screenshots for UI changes
- **Breaking Changes**: Clearly mark any breaking changes

## 🐛 Reporting Issues

### Bug Reports

When reporting bugs, please include:

1. **Clear Title**: Summarize the issue concisely
2. **Description**: Detailed description of the problem
3. **Steps to Reproduce**: Step-by-step instructions
4. **Expected Behavior**: What should happen
5. **Actual Behavior**: What actually happens
6. **Environment**: Python version, OS, FACET version
7. **Code Sample**: Minimal code to reproduce the issue

### Feature Requests

For feature requests, please include:

1. **Clear Title**: What feature you'd like to see
2. **Problem**: What problem would this solve?
3. **Solution**: Describe your proposed solution
4. **Alternatives**: Any alternative solutions considered
5. **Use Case**: How would you use this feature?

## 📚 Documentation

### Adding Examples

1. Add example files to the `examples/` directory
2. Follow the naming convention: `descriptive_name.facet`
3. Include comments explaining key concepts
4. Add corresponding JSON output files
5. Update `examples/README.md` with your example

### Improving Documentation

1. Check for typos and grammatical errors
2. Ensure code examples are accurate and runnable
3. Verify that links are working
4. Update screenshots and diagrams as needed
5. Improve clarity and readability

### Translation Contributions

We welcome translations of documentation:

1. Create a new directory under `docs/` (e.g., `docs/es/`)
2. Translate Markdown files maintaining structure
3. Update links to point to translated versions
4. Test that all links work correctly

## 🎯 Development Workflow

### Regular Development Cycle

1. **Plan**: Discuss features in GitHub Issues/Discussions
2. **Develop**: Create branch, implement changes, write tests
3. **Test**: Run full test suite, check code quality
4. **Review**: Submit PR, address feedback
5. **Merge**: Changes merged to main branch
6. **Release**: New version published to PyPI

### Release Process

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md` with release notes
3. Create git tag for the release
4. Publish to PyPI
5. Create GitHub Release with changelog

## 🙋 Questions?

If you have questions about contributing:

- **GitHub Discussions**: General questions and community support
- **GitHub Issues**: Bug reports and feature requests
- **Pull Request Comments**: Questions about specific changes

## 📄 License

By contributing to FACET, you agree that your contributions will be licensed under the same MIT License that covers the project.

Thank you for contributing to FACET! 🚀