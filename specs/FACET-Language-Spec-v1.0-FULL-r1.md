# FACET Language Specification v1.0 (Full Documentation, Revision 1)

**Status:** Final v1.0 (r1)  
**Author:** Emil Rokossovskiy <ecsiar@gmail.com> - [@rokoss21](https://github.com/rokoss21/)  
**Date:** 2025-09-07  
**MIME:** `application/facet`  
**File Extension:** `.facet`

---

## Editorial & Normative Updates in r1

- **ABNF fix (E‑001):** `inline_map` now uses **single** braces `{` `}`.  
- **Lens Purity (N‑002):** Lenses are **pure** functions: they operate **only on the value** they receive; they MUST NOT access sibling/parent nodes, global state, time, randomness, file system, or network.  
- **Attributes vs Inline Maps (N‑003):** Attributes configure the **facet itself** and appear in JSON under `"_attrs"`. Inline maps are **data values** in the facet body. Lenses **cannot** be applied to attributes; lenses apply only to values in the body.

---

## Abstract

**FACET (Feature‑Aware Contracted Extension for Text)** is a human‑readable, machine‑deterministic markup language for authoring, managing, and executing instructions for AI systems. FACET unifies the ergonomics of plain text with the rigor of code through strict indentation, explicit data types, **first‑class output contracts**, and **lenses** — pure, deterministic pipeline transforms applied inline via `|>`. Every FACET document maps to a **single canonical JSON representation**, enabling lossless roun...

This specification defines the syntax, data model, canonicalization rules, conformance requirements, and security considerations for **FACET v1.0**.

---

## 1. Conformance Keywords

The keywords **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**, **SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **MAY**, and **OPTIONAL** are to be interpreted as described in RFC 2119.

---

## 2. Design Goals

1. **Clarity & Readability** — Minimal syntactic noise; indentation as structure.  
2. **Unambiguous Parsing** — No YAML‑style ambiguities; fixed indentation (2 spaces).  
3. **Deterministic Serialization** — One canonical JSON; lossless round‑trip.  
4. **Prompt‑First Primitives** — Multiline strings, code fences, contracts, examples.  
5. **Extensibility** — Block‑based facets `@name` + attributes; lenses; reserved vocabulary that does not prevent domain‑specific ones.  
6. **Toolability** — Easy to lint, format, validate; predictable error classes and codes.

---

## 3. Document Model

A FACET document is a UTF‑8 text file consisting of **facets** (blocks), key‑value pairs, lists, inline maps, fenced code blocks, anchors/aliases, **lenses**, and comments.

### 3.1 Encoding
Documents **MUST** be UTF‑8 encoded. A BOM, if present, **MUST** be ignored.

### 3.2 Whitespace & Newlines
- Line endings **MAY** be `LF` or `CRLF`. Canonicalization **MUST** normalize to `LF`.  
- Trailing spaces **SHOULD** be ignored by parsers and removed by formatters.

### 3.3 Indentation
- Inside facet bodies, indentation is **exactly two spaces** per level. Tabs are invalid and **MUST** cause a parse error.  
- Dedentation closes the current nested block.

### 3.4 Comments
- A `#` begins a comment and continues to end of line. Comments are ignored by canonical JSON mapping.  
- Inline comments after values are permitted: `key: "value" # note`.

### 3.5 Facets
A **facet** starts with `@` + identifier (ASCII letters, digits, underscore; not starting with a digit), optionally followed by **attributes** in parentheses, then a newline and an indented body.

```
@system(role="Expert", version=1)
  style: "Friendly, concise"
  constraints:
    - "Use Markdown"
```

**Attributes** are parsed as an inline map of `key=value` pairs. Values in attributes MAY be unquoted identifiers, numbers, booleans, or quoted strings. Attributes are included in the facet's JSON object under the `"_attrs"` key (implementations MAY desugar them to regular fields, but preserving `"_attrs"` is RECOMMENDED to prevent collisions).

### 3.6 Keys & Values
Key‑value pairs use `key: value`. Keys follow the identifier rule. Values follow the data types in §4. Any value (scalar, list, map, fence) **MAY** be followed by a **lens pipeline** (§6).

### 3.7 Anchors & Aliases
- `&name` defines an anchor for the value on the same line.  
- `*name` references the anchored value.  
- Aliases **MUST** refer to a previously defined anchor; cycles **MUST** be rejected.

Example:
```
style &friendly: "Polite, helpful"
apply_style: *friendly
```

### 3.8 Fenced Code Blocks
Triple backticks introduce a **fenced block** with an optional language identifier. The entire fence body is preserved verbatim.

````
schema: ```json
{ "type":"object","properties":{"ok":{"type":"boolean"}} }
```
````

---

## 4. Data Types

### 4.1 Scalars
- **String**: `"..."` with escapes (`\n`, `\t`, `\"`, `\\`), or `"""..."""` for multiline (preserve newlines verbatim).  
- **Number**: integers, floats, scientific notation. `NaN`, `Infinity`, `-Infinity` are **invalid**.  
- **Boolean**: `true`, `false`.  
- **Null**: `null`.

### 4.2 Extended Scalars (serialize as JSON strings)
- **Timestamp**: `@YYYY-MM-DDThh:mm:ss[.fff][Z|±hh:mm]` (ISO‑8601).  
- **Duration**: `\d+(ms|s|m|h|d)`.  
- **Size**: `\d+(B|KB|MB|GB)`.  
- **Regex**: `/pattern/flags` (UTF‑8; `/` must be escaped inside pattern as `\/`).

### 4.3 Structures
- **List**:
  ```
  steps:
    - "One"
    - "Two"
  ```
- **Map**:
  ```
  user:
    name: "Alex"
    active: true
  ```
- **Inline Map**: `{a: 1, b: 2}` (no trailing comma).

### 4.4 Nesting
A value may open a nested block when followed by a newline and further indented content (e.g., nested maps).

---

## 5. Standard Facets (Reserved Names)

The following facet names are **reserved** for interoperability. Tools **SHOULD** recognize them semantically:

- `@meta` — metadata (`id`, `version`, `author`, `tags`).  
- `@system` — role, style, global constraints.  
- `@user` — user request or input data.  
- `@assistant` — assistant directives or final prompt template.  
- `@plan` — ordered list of steps for the assistant.  
- `@examples` — few‑shot examples.  
- `@tools` — tool/function declarations.  
- `@output` — output contract (format, schema, requirements).  
- `@safety` — safety & policy guidance.

Other facet names MAY be used. Name collisions with the reserved set SHOULD be avoided in shared libraries.

---

## 6. Lenses (Pipeline Operators)

A **lens** is a pure, deterministic transform applied to a value via `|>`. Multiple lenses are applied left‑to‑right:

```
prompt: """
    Hello,   world!
"""
  |> dedent
  |> squeeze_spaces
  |> trim
  |> limit(1024)
```

### 6.1 Syntax
```
value |> lensName(arg1, arg2) |> lensTwo
```
Arguments MAY be numbers, booleans, identifiers, or quoted strings.

### 6.2 Semantics (Purity & Determinism)
- Lenses operate on the **parsed value** passed to them and **MUST NOT** access sibling/parent nodes or global document state.  
- Lenses **MUST NOT** perform I/O, depend on time or randomness, or mutate any external state.  
- If a lens cannot operate on the value type, it **MUST** raise a lens‑type error.  
- Lenses are **pure** and **order‑sensitive**.  
- Lens application is part of canonicalization; the resulting value is serialized.

### 6.3 Required Lenses (MUST implement)
- `trim()` — remove leading and trailing whitespace from strings.  
- `dedent()` — remove common leading indentation from multiline strings.  
- `squeeze_spaces()` — collapse consecutive spaces/TABs to single spaces (preserve newlines).  
- `limit(N)` — truncate string to `N` bytes (UTF‑8 safe).  
- `normalize_newlines()` — CRLF→LF.  
- `json_minify()` — if value is a JSON text, minify; on parse failure, no‑op.  
- `strip_markdown()` — remove Markdown formatting (best‑effort, no guarantees).

### 6.4 Optional Lenses (MAY implement)
- `lower()`, `upper()`, `title()` — case transforms.  
- `replace(pattern, repl)` — literal replacement.  
- `regex_replace(/pat/flags, repl)` — regex replacement (guard against ReDoS).

---

## 7. Contracts (Output Specification)

FACET integrates **contracts** within `@output` facets to define output format and validation requirements.

```
@output(format="json")
  require: "Respond with JSON only."
  schema: ```json
    { "type":"object","required":["summary"],
      "properties":{ "summary":{ "type":"string" } } }
  ```
```

- `format` MAY be `json`, `markdown`, or `text`.  
- `schema` SHOULD be JSON Schema 2020‑12; tools MAY accept earlier drafts.  
- Tools **SHOULD** validate model outputs against `schema` when present.  
- `require` is a natural‑language constraint surfaced to the model.

---

## 8. Canonical JSON Mapping

Every FACET document serializes to a **single JSON object**:

1. **Root** → JSON object.  
2. **Facet** `@name` → JSON key `"name": { ... }`.  
3. **Attributes** → under key `"_attrs"` (object) within the facet, unless desugared.  
4. **Scalars** → JSON scalars; extended scalars → JSON strings.  
5. **Lists/Maps** → JSON arrays/objects.  
6. **Fenced blocks** → JSON strings (verbatim, without the backticks).  
7. **Anchors/Aliases** → aliases resolved; anchors not emitted.  
8. **Lenses** → applied during parsing; serialized post‑transform.  
9. **Key order** within objects SHOULD be preserved.

### 8.1 Canonicalization Algorithm (Normative)
Given a FACET document `D`:
1. Normalize newlines to `LF`.  
2. Tokenize; enforce indentation = 2 spaces; reject tabs.  
3. Parse into an AST of facets, statements, and values.  
4. Resolve anchors and aliases; detect cycles → error.  
5. Apply lens pipelines to each value in source order.  
6. Convert extended scalars and fences to strings.  
7. Construct the root JSON object; insert facet attributes into `"_attrs"`.  
8. Emit canonical JSON with stable key ordering and UTF‑8 encoding.

### 8.2 Number Semantics
- Integers and decimals map to JSON numbers.  
- Leading zeros are allowed only for zero itself (`0`).  
- `NaN`, `Infinity`, `-Infinity` are invalid → parse error.  

---

## 9. Grammar (ABNF)

**Note:** Indentation (`IND`) is normative: exactly `2*SP`. Dedentation (`DED`) is implementation‑defined based on indentation stack.

```
document        = *(WS / comment / facet)
facet           = "@" ident [attrs] NL IND block
attrs           = "(" attr *( "," SP? attr ) ")"
attr            = ident "=" attrval
attrval         = number / boolean / quoted / ident

block           = 1*(kv / list / fenced / comment)
kv              = key ":" SP? value lens* NL
list            = "-" SP value lens* NL

value           = scalar / inline_map / nested_block
nested_block    = NL IND block DED

scalar          = quoted / triple / number / boolean / null / ext_scalar
quoted          = DQUOTE *( ESC / CHAR ) DQUOTE
triple          = 3DQUOTE *( CHAR / NL ) 3DQUOTE

inline_map      = "{" SP? pair *( "," SP? pair ) SP? "}"
pair            = key ":" SP? value

ext_scalar      = timestamp / duration / size / regex
timestamp       = "@" ISO8601
duration        = 1*DIGIT ( "ms" / "s" / "m" / "h" / "d" )
size            = 1*DIGIT ( "B" / "KB" / "MB" / "GB" )
regex           = "/" *( ESC / RCHAR ) "/" *ALPHA

lens            = SP "|>" SP lens_name [ "(" [ lens_args ] ")" ]
lens_name       = ident
lens_args       = [ arg *( "," SP? arg ) ]
arg             = number / boolean / quoted / ident

key             = ident
ident           = ALPHA *( ALPHA / DIGIT / "_" )
boolean         = "true" / "false"
null            = "null"

comment         = "#" *CHAR NL

WS              = *( SP / HTAB )
NL              = %x0A / %x0D.0A
IND             = 2*SP
DED             = ; dedent when indentation decreases
```

---

## 10. Errors and Diagnostics

Implementations **SHOULD** report structured errors with code, message, and location (line, column). Suggested classes:

- **F001** — Lexical error (invalid character, bad escape).  
- **F002** — Indentation error (tabs, wrong indent width).  
- **F003** — Unterminated fence or string.  
- **F101** — Type error (invalid value for context).  
- **F102** — Lens type error (lens cannot apply to this value).  
- **F201** — Anchor error (undefined alias, cycle detected).  
- **F301** — Attribute error (malformed attribute value).  
- **F401** — Contract error (invalid JSON Schema).  
- **F999** — Unknown internal error.

Errors **SHOULD** include a caret snippet for quick diagnosis.

---

## 11. Security Considerations

- **Resource Limits:** Parsers SHOULD cap document size, depth, lens chain length, and fence size.  
- **Regex Safety:** Engines MUST mitigate ReDoS; consider timeouts.  
- **Code Fences:** Execution is out of scope; tools that execute MUST sandbox.  
- **Imports/Macros:** Reserved; MUST be disabled by default; when enabled, restrict to allowed roots.  
- **Anchors:** Reject cycles; avoid unbounded alias expansion.

---

## 12. IANA Considerations

- Proposed Media Type: `application/facet`  
- File Extension: `.facet`

---

## 13. Interoperability & Migration

### 13.1 From JSON
- Move objects into facets (`@system`, `@user`, etc.).  
- Replace large strings with `"""..."""` or fences.  
- Add contracts under `@output`.

### 13.2 From YAML
- Replace ambiguous scalars with explicit strings (`"on"`, `"yes"`).  
- Fix indentation to 2 spaces.  
- Replace anchors with `&name`/`*name` where used; avoid YAML tag semantics.

### 13.3 From PRISM/Custom DSL
- Rename sections to facets; map directives to attributes.  
- Replace preprocessors with lenses.

---

## 14. Style Guide (Non‑Normative)

**Attributes vs Inline Maps**  
- Use **attributes** `@facet(key=value)` to configure the facet entity itself; attributes are serialized into `"_attrs"`.  
- Use **inline maps** `{...}` for **data values** inside the facet body.  
- **Do not** apply lenses to attributes; lenses apply to values in the body.

**General**  
- Max line length: 100 characters.  
- Quote any string with spaces or punctuation.  
- Prefer fences for code or JSON Schema.  
- Keep facet names lowercase.

---

## 15. Reference: Standard Facet Keys (Informative)

- `@meta`: `id`, `version`, `author`, `tags`  
- `@system`: `role`, `style`, `constraints`  
- `@user`: `request`, `data`  
- `@assistant`: `prompt`, `style`, `format`  
- `@plan`: steps (list of strings)  
- `@examples`: arbitrary map/list  
- `@tools`: each tool has `name`, `call`, `policy`  
- `@output`: `format`, `require`, `schema`  
- `@safety`: `policies`, `blocked`, `notes`

---

## 16. Worked Examples

### 16.1 Basic Prompt with Contract
```facet
@meta
  id: "recursion-basic"
  version: 1.0

@system
  role: "Expert programmer"
  constraints:
    - "Use Markdown"
    - "English language"

@user
  request: "Explain recursion in Python"

@plan
  - "Definition"
  - "Code example"
  - "Explanation"

@output(format="json")
  require: "Return JSON only."
  schema: ```json
    {
      "type":"object",
      "required":["definition","code","explanation"],
      "properties":{
        "definition":{"type":"string"},
        "code":{"type":"string"},
        "explanation":{"type":"string"}
      }
    }
  ```
```

### 16.2 Using Lenses
```facet
@user
  request: """
      Explain recursion in Python
      and provide a short example.
  """
    |> dedent |> trim |> limit(200)
```

### 16.3 Anchors & Aliases
```facet
@system
  style &teachy: "Educational, friendly"
  constraints:
    - "Short examples"

@assistant
  style: *teachy
  prompt: "Follow the plan and return JSON according to the schema."
```
