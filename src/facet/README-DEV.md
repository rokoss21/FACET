# FACET Python Reference (minimal) — v1.0 r1
Date: 2025-09-07

This is a minimal reference parser **FACET → JSON** with CLI.

## Installation (editable)
```bash
cd facet
python -m pip install -e .
```

## CLI

```bash
# Convert to canonical JSON
facet to-json examples/recursion.facet

# Lint (indentation, basic checks)
facet lint examples/recursion.facet
```

Lenses (implemented): `trim`, `dedent`, `squeeze_spaces`, `limit`, `normalize_newlines`, `json_minify`, `strip_markdown`.
