# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-09-07

### Added
- **Core FACET Parser**: Complete implementation of FACET v1.0 specification
- **CLI Tools**: `facet to-json`, `facet lint`, `facet validate`, `facet fmt`
- **Lens System**: Pure, deterministic transforms (`trim`, `dedent`, `squeeze_spaces`, etc.)
- **Facet Support**: `@system`, `@user`, `@output`, `@plan`, `@examples`, `@tools`, `@safety`, `@meta`
- **Extended Scalars**: Timestamps, durations, sizes, regex patterns
- **Anchors & Aliases**: Reusable value references with cycle detection
- **Comprehensive Examples**: Multiple `.facet` files demonstrating all features
- **Golden Tests**: Roundtrip validation ensuring deterministic JSON output
- **Production-Ready Packaging**: PEP 621 compliant `pyproject.toml`
- **CI/CD Pipeline**: GitHub Actions with multi-version Python testing
- **Documentation**: Complete specification, usage guide, and developer docs

### Features
- **Deterministic Parsing**: Single canonical JSON for every valid FACET document
- **Type Safety**: Strong typing with MyPy support
- **Error Handling**: Structured error codes (F001-F999) with location info
- **Security**: Resource limits, regex safety, no code execution
- **Extensibility**: Plugin architecture for custom lenses and facets

### Technical Details
- **Python 3.9+** support
- **Zero dependencies** for core functionality
- **UTF-8** encoding with BOM detection
- **2-space indentation** enforcement
- **LF normalization** for cross-platform compatibility

### Changed
- Initial release - no previous versions

### Fixed
- Initial release - no previous versions

---

## [Unreleased]

### Added
- Pre-commit hooks configuration
- MkDocs documentation site
- Performance benchmarks
- Integration with popular AI frameworks

### Planned
- TypeScript/JavaScript implementation
- LSP server for IDE integration
- VS Code extension
- Additional lens functions
- Plugin ecosystem

---

[1.0.0]: https://github.com/rokoss21/FACET/releases/tag/v1.0.0
