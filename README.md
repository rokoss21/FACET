<div align="center">

# 🔷 FACET — Feature‑Aware Contracted Extension for Text 🔶

**Human‑readable, deterministic markup for AI instructions.**  
Facets (`@name`) • Contracts (JSON Schema) • Lenses (`|>`) • Canonical JSON

[![spec](https://img.shields.io/badge/spec-v1.0%20(r1)-4c1)](./FACET-Language-Spec-v1.0-FULL-r1.md)
[![status](https://img.shields.io/badge/status-final-success)](./FACET-Language-Spec-v1.0-FULL-r1.md#editorial--normative-updates-in-r1)
[![mime](https://img.shields.io/badge/MIME-application%2Ffacet-blue)](#-media-type)
[![ext](https://img.shields.io/badge/ext-.facet-blueviolet)](#-file-extension)
[![author](https://img.shields.io/badge/author-Emil%20Rokossovskiy-0aa)](#-author)

</div>

---

## ✨ What is FACET?

**FACET** is a modern markup language tailored for **AI prompting**. It combines the clarity of plain text with **deterministic parsing** and **lossless canonical JSON**.  
Key innovations:
- **Facets** — top‑level blocks like `@system`, `@user`, `@output` (with attributes `@name(key=value)`).
- **Lenses (`|>`)** — inline **pure** transforms (`dedent`, `trim`, `limit(1024)`, `json_minify`) applied to values.
- **Contracts** — first‑class output specs (JSON Schema) inside `@output`.

> FACET evolves the earlier PRISM concept into a **production‑grade** language.

---

## 📚 Spec (v1.0 r1)

- **Full Specification (r1)** → [FACET-Language-Spec-v1.0-FULL-r1.md](./FACET-Language-Spec-v1.0-FULL-r1.md)  
- **Short Spec (r1)** → [FACET-SPEC-v1.0-r1.md](./FACET-SPEC-v1.0-r1.md)

Previous draft materials:
- **Full Draft (v1.0)** → [FACET-Language-Spec-v1.0-FULL.md](./FACET-Language-Spec-v1.0-FULL.md)  
- **Short Draft** → [FACET-SPEC-v1.0.md](./FACET-SPEC-v1.0.md)

Examples:
- [`examples/recursion.facet`](./examples/recursion.facet)  
- Canonical JSON → [`examples/recursion.json`](./examples/recursion.json)

---

## 🧩 Quick Look

```facet
@system(role="Expert")
  style: "Friendly, concise"
  constraints:
    - "Use Markdown"
    - "Russian language"

@user
  request: """
      Объясни рекурсию в Python
      и приведи короткий пример.
  """
    |> dedent |> trim |> limit(200)

@output(format="json")
  require: "Return JSON only."
  schema: ```json
    {{
      "type":"object",
      "required":["definition","code","explanation"],
      "properties":{{
        "definition":{{"type":"string"}},
        "code":{{"type":"string"}},
        "explanation":{{"type":"string"}}
      }}
    }}
  ```
```

**Canonical JSON (FACET → JSON)** preserves structure and applies lenses before serialization.

---

## 🧪 Why it’s different

- **Deterministic**: strict 2‑space indentation, no YAML ambiguities.  
- **Composable**: attributes on facets, reusable anchors/aliases.  
- **Contract‑driven**: schemas are first‑class citizens.  
- **Tool‑friendly**: clean grammar (ABNF), error taxonomy, security guidance.

---

## 🛠 Roadmap (tooling)

- `facet to-json file.facet > file.json`  
- `facet validate file.facet` (via `@output.schema`)  
- `facet fmt` / `facet lint`  
- SDKs: TypeScript • Python • Rust

> Community contributions welcome once the reference parser is published.

---

## 🔐 Security & Determinism

- Lenses are **pure**: no I/O, no randomness, no access to AST/global state.  
- Regex operations should be sandboxed to avoid ReDoS.  
- Imports/Macros are reserved; disabled by default.

---

## 🧾 Media Type & File Extension

- **Media Type**: `application/facet`  
- **File Extension**: `.facet`

---

## 👤 Author

**Emil Rokossovskiy** — [@rokoss21](https://github.com/rokoss21/)  
📧 ecsiar@gmail.com  
© 2025 Emil Rokossovskiy. All rights reserved.

---

## 📄 License

TBD. Until a license is published, all rights are reserved by the author.

---

## 🤝 Acknowledgements

FACET builds on prior work and ideas in prompt engineering and structured markup, evolving the PRISM concept into a **contract‑ and lens‑driven** language suitable for production ecosystems.

