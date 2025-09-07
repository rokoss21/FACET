# FACET — Usage Guide

This guide shows how to **install**, **use the CLI**, **embed the parser as a library**, validate against **contracts**, work with **lenses**, and integrate FACET into **CI**.

> FACET turns human‑readable AI instructions into **canonical JSON** with deterministic semantics.

---

## 1) Installation

```bash
# Clone and enter the repo
git clone https://github.com/rokoss21/FACET.git
cd FACET

# (Optional) virtualenv
python -m venv .venv && source .venv/bin/activate

# Install in editable mode
pip install -e .
```

After installation you can use the **CLI** via `facet` (or run `python -m facet.cli`).

---

## 2) CLI Overview

```bash
facet to-json <file.facet>        # FACET → canonical JSON
facet validate <file.facet>       # Validate against @output.schema if present
facet fmt <file.facet>            # Auto-format: indentation, newlines
facet lint <file.facet>           # Lint: structured diagnostics (Fxxx codes)
```

**Exit codes**
- `0` — success
- `1` — parse/validation error (see diagnostic code)
- `2` — internal error

### 2.1 Convert to JSON

```bash
facet to-json examples/recursion.facet > examples/recursion.json
```

### 2.2 Validate Against Contracts

Validation uses the `@output` facet’s `schema` (JSON Schema 2020‑12 preferred).

```facet
@output(format="json")
  require: "JSON only"
  schema: ```json
    {
      "type": "object",
      "required": ["summary"],
      "properties": {
        "summary": { "type": "string" }
      }
    }
  ```
```

```bash
facet validate path/to/doc.facet
```

If the document lacks `@output.schema`, `validate` will succeed with a note (no schema present).

### 2.3 Lint & Format

```bash
facet lint path/to/doc.facet     # Strict checks: indentation, tabs, anchors, lenses, etc.
facet fmt  path/to/doc.facet     # Rewrites to canonical whitespace/newlines
```

---

## 3) Library API (Python)

```python
from facet import parser

# Read FACET text
text = open("examples/recursion.facet", "r", encoding="utf-8").read()

# Option A: get pretty JSON string directly
json_text = parser.to_json(text)

# Option B: get the parsed structure (dict-like) then dump yourself
ast = parser.parse_facet(text)
import json
print(json.dumps(ast, ensure_ascii=False, indent=2))
```

> **Important:** `parser.to_json(text)` expects **source text**. If you already called `parse_facet`, serialize with `json.dumps` yourself.

---

## 4) Lenses: Before → After

Input:

```facet
@user
  request: """
      Hello,   world!
      This line is indented.
  """
    |> dedent |> squeeze_spaces |> trim |> limit(32)
```

Resulting value after lenses (conceptual):

```text
Hello, world!
This line is indented.
```

> Lenses are **pure** and **deterministic**. They operate **only** on the value they receive: **no** I/O, time, randomness, or access to siblings/parents/AST.

Built‑ins (common): `trim`, `dedent`, `squeeze_spaces`, `limit(N)`, `normalize_newlines`, `json_minify`, `strip_markdown`

---

## 5) Anchors & Aliases

```facet
@system
  style &teachy: "Friendly, didactic"
  constraints:
    - "Short examples"

@assistant
  style: *teachy
  prompt: "Follow the plan and return JSON."
```

Rules:
- `&name` defines an anchor for the **value** on the same line.
- `*name` references a previously defined anchor.
- Undefined alias → **F201** (Anchor error).
- Cycles are rejected.

---

## 6) Errors & Diagnostics (F‑codes)

The CLI returns clear messages with codes and (where possible) caret snippets.

Common classes:
- **F001** — Lexical error (invalid char/escape)
- **F002** — Indentation error (tabs, wrong width)
- **F003** — Unterminated fence/string
- **F101** — Type error (value invalid for context)
- **F102** — Lens error (unknown lens or type mismatch)
- **F201** — Anchor error (undefined alias, cycle)
- **F301** — Attribute error (malformed attribute)
- **F401** — Contract error (invalid JSON Schema)
- **F999** — Internal error

Example output:

```
F002 Indentation error at line 14, col 1
  expected indent = 2 spaces, found tab
  12:   constraints:
  13: 	- "Use Markdown"
        ^
```

---

## 7) Round‑trip & Canonicalization Guarantees

- **Single canonical JSON** for every valid FACET document.
- Newlines normalized to **LF**.
- Indentation **exactly 2 spaces** inside facet bodies.
- Extended scalars (`@timestamp`, durations, sizes, regex) → serialized as strings.
- Fenced blocks → verbatim strings (the fence markers are not included).
- Attributes appear under `"_attrs"` (implementations may desugar, but collision‑safe storage is recommended).

---

## 8) CI Integration (GitHub Actions)

```yaml
name: FACET CI

on:
  push:
    paths: ["**.facet"]
  pull_request:
    paths: ["**.facet"]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install FACET
        run: |
          python -m pip install --upgrade pip
          pip install -e .
      - name: Lint & Validate
        run: |
          facet lint $(git ls-files '*.facet')
          facet validate $(git ls-files '*.facet')
```

---

## 9) Troubleshooting

- **`ImportError: attempted relative import with no known parent package`**  
  Install the package (`pip install -e .`) or import via the package name (e.g., `from facet import parser`).

- **`F102: lens 'X' expects string`**  
  The lens is applied to a non‑string value. Ensure the target value is a string or remove the lens.

- **`F002: tabs detected`**  
  Replace tabs with **two spaces** per indent level.

---

## 10) Best Practices

- Keep facet names lowercase (`@system`, `@user`, …).
- Prefer triple‑quoted strings and fenced blocks for prompts and schemas.
- Apply lenses **sparingly** and **left‑to‑right** (order matters).
- Co‑locate contracts in `@output` for immediate validation.
- Treat FACET like **API definitions**: version your documents, lint in CI, and keep tests/golden files.
