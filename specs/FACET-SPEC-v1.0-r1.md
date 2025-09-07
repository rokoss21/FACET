# FACET Markup Language — Specification v1.0 (Short, r1)

**Status:** Final v1.0 (r1)  
**MIME:** application/facet • Ext: .facet

## What is FACET?
Human‑readable, deterministic markup for AI instructions with **Facets (@name)**, **Contracts**, and **Lenses (`|>`)**. Canonical **FACET → JSON** mapping is lossless.

## Key Concepts
- **Facets** — top‑level blocks `@system`, `@user`, `@output`, etc. + **attributes** `@output(format="json")`.  
- **Lenses** — inline, pure transforms: `dedent`, `trim`, `limit(1024)`, etc.  
- **Contracts** — JSON Schema + rules in `@output`.

## Syntax Snapshot
```facet
@system(role="Expert")
  style: "Friendly, concise"
  constraints:
    - "Use Markdown"

@user
  request: """
      Объясни рекурсию в Python
  """
    |> dedent |> trim

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

## JSON Mapping (Canonical)
- Each `@facet` becomes a JSON key.  
- Attributes serialize under `"_attrs"`.  
- Extended scalars and fences → strings.  
- Anchors resolved; lenses applied pre‑serialization.

## ABNF Fixes in r1
- `inline_map = "{" pair *( "," pair ) "}"` (single braces).  
- Lenses are **pure**; no AST/global access.  
- Attributes vs Inline Maps clarified; lenses cannot apply to attributes.
