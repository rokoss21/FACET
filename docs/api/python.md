# Python API Reference

This page documents the Python API for FACET.

## Core Functions

### `facet.parser.to_json(text: str) -> str`

Converts a FACET document to its canonical JSON representation.

**Parameters:**
- `text` (str): The FACET document as a string

**Returns:**
- `str`: Canonical JSON string

**Raises:**
- `FACETError`: If the document is invalid

**Example:**
```python
from facet import parser

facet_doc = """
@system
  role: "Assistant"

@user
  message: "Hello!"
"""

json_str = parser.to_json(facet_doc)
print(json_str)
# {"system":{"role":"Assistant"},"user":{"message":"Hello!"}}
```

### `facet.parser.parse_facet(text: str) -> dict`

Parses a FACET document into a Python dictionary (AST representation).

**Parameters:**
- `text` (str): The FACET document as a string

**Returns:**
- `dict`: Parsed AST as a dictionary

**Raises:**
- `FACETError`: If the document is invalid

**Example:**
```python
from facet import parser
import json

facet_doc = "@user\n  query: 'Hello!'"
ast = parser.parse_facet(facet_doc)

# AST structure
print(ast)
# {'user': {'query': 'Hello!'}}
```

## Error Handling

### `facet.errors.FACETError`

Base exception class for all FACET parsing errors.

**Attributes:**
- `code` (str): Error code (e.g., "F001", "F002")
- `message` (str): Human-readable error message
- `line` (int): Line number where error occurred
- `column` (int): Column number where error occurred

**Example:**
```python
from facet import parser
from facet.errors import FACETError

try:
    result = parser.to_json("invalid facet content")
except FACETError as e:
    print(f"Error {e.code} at line {e.line}: {e.message}")
```

## Lens System

### Built-in Lenses

FACET provides several built-in lens functions that can be applied to values:

- **`trim`** — Remove leading and trailing whitespace
- **`dedent`** — Remove common leading indentation from multiline strings
- **`squeeze_spaces`** — Collapse consecutive spaces to single spaces
- **`limit(n)`** — Truncate string to n bytes (UTF-8 safe)
- **`normalize_newlines`** — Convert CRLF to LF
- **`json_minify`** — Minify JSON text (no-op if invalid)
- **`strip_markdown`** — Remove Markdown formatting (best-effort)

### Using Lenses Programmatically

```python
from facet.lenses import apply_lenses

# Apply lenses to a value
original = "  Hello,   world!  \n  Second line  "
result = apply_lenses(original, ["trim", "squeeze_spaces"])
print(repr(result))  # "Hello, world!\nSecond line"
```

## Advanced Usage

### Custom Lens Implementation

```python
from facet.lenses import LensRegistry

def custom_upper(value):
    """Custom lens that converts strings to uppercase."""
    if not isinstance(value, str):
        raise ValueError("upper lens requires string input")
    return value.upper()

# Register custom lens
registry = LensRegistry()
registry.register("upper", custom_upper)

# Use in parsing
# Note: This would require extending the parser
```

### Working with Extended Scalars

```python
from facet import parser
import json

facet_doc = """
@meta
  timestamp: @2024-01-01T12:00:00Z
  duration: 30s
  size: 1MB
  pattern: /test/i
"""

result = parser.to_json(facet_doc)
parsed = json.loads(result)

print(parsed["meta"]["timestamp"])  # "2024-01-01T12:00:00Z"
print(parsed["meta"]["duration"])   # "30s"
print(parsed["meta"]["size"])       # "1MB"
print(parsed["meta"]["pattern"])    # "/test/i"
```

## CLI Integration

The Python API can be easily integrated with the CLI:

```python
#!/usr/bin/env python3
"""Custom FACET processor using the Python API."""

import sys
from facet import parser
from facet.errors import FACETError

def process_facet_file(filepath):
    """Process a .facet file and return JSON."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        json_output = parser.to_json(content)
        return json_output

    except FACETError as e:
        print(f"Error in {filepath}: {e.message}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python process_facet.py <file.facet>", file=sys.stderr)
        sys.exit(1)

    result = process_facet_file(sys.argv[1])
    print(result)
```
