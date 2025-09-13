# FACET — Feature-Aware Contracted Extension for Text

**A deterministic markup language for the AI era.**

<div align="center">
  <img src="https://raw.githubusercontent.com/rokoss21/FACET/main/assets/logo.png" alt="FACET Logo" width="100%" height="auto" style="max-width: 600px;">
  <br>
  <h3>🚀 Feature-Aware Contracted Extension for Text</h3>
  <p><em>Human-readable, machine-deterministic instructions for AI systems.</em></p>
</div>

[![spec](https://img.shields.io/badge/spec-v1.1%20\(Draft%20r3\)-4c1)](https://github.com/rokoss21/FACET/blob/main/FACET-Language-Spec-v1.1-r3.md)
[![status](https://img.shields.io/badge/status-draft-yellow)](https://github.com/rokoss21/FACET/blob/main/FACET-Language-Spec-v1.1-r3.md)
[![mime](https://img.shields.io/badge/MIME-application%2Ffacet-blue)](#)
[![ext](https://img.shields.io/badge/ext-.facet-blueviolet)](#)
[![author](https://img.shields.io/badge/author-Emil%20Rokossovskiy-0aa)](https://github.com/rokoss21)

<!-- PyPI badges -->
[![PyPI version](https://img.shields.io/pypi/v/facet-lang.svg)](https://pypi.org/project/facet-lang/)
[![PyPI downloads](https://img.shields.io/pypi/dm/facet-lang.svg)](https://pypi.org/project/facet-lang/)
[![Python versions](https://img.shields.io/pypi/pyversions/facet-lang.svg)](https://pypi.org/project/facet-lang/)
[![License](https://img.shields.io/pypi/l/facet-lang.svg)](https://github.com/rokoss21/FACET/blob/main/LICENSE)

---

## ✨ What is FACET?

**FACET** is a markup language for authoring, managing, and executing instructions for AI systems. It merges the **clarity of plain text** with the **rigor of code** to build **reproducible** AI pipelines.

Every FACET document compiles to a **single canonical JSON** — no YAML-style ambiguity, no hidden magic. Version **v1.1** turns FACET into a **compile-time configuration language** with modularity, logic, static typing, and a pure transformation pipeline (*lenses*).

---

### ⚡ Your First Dynamic Prompt in 60 Seconds

Experience the power of conditional logic right from your terminal.

1.  Install FACET:
    ```bash
    pip install facet-lang
    ```

2.  Create a dynamic `.facet` file:
    ```bash
    cat > my_prompt.facet << EOF
    @vars
      # Try changing the default to "expert" and re-running!
      mode: "user"

    @system(if="mode == 'expert'")
      role: "You are a world-class computer science professor."

    @user
      request: "Explain recursion to me."
    EOF
    ```

3.  Canonize it in "user" mode:
    ```bash
    facet canon --var "mode=user" my_prompt.facet
    ```
    Notice the JSON output has no `@system` block.

4.  Now, canonize it in "expert" mode:
    ```bash
    facet canon --var "mode=expert" my_prompt.facet
    ```
    And now the `@system` block appears — you've just used compile-time logic.

## 🧠 How FACET Works

```
+------------------+     +------------------+     +-----------------+
|                  |     |                  |     |                 |
|   .facet file    | --> |   FACET Parser   | --> |  Canonical JSON |
|   (Source Text)  |     | (Lenses,         |     |     (Output)    |
|                  |     |  Contracts)      |     |                 |
+------------------+     +------------------+     +-----------------+
        |                        |                       |
        |-- Facets (@user)       |-- Data transforms     |-- Deterministic
        |-- Attributes (name="") |-- Schema validation   |-- Reproducible
        |-- Lenses (|> trim)     |-- Type checking       |-- Tool‑ready
        |-- Contracts (@output)  |-- Error handling      |-- Always valid
```

At authoring time you write readable `.facet` files. The reference parser expands imports, resolves variables, applies conditionals, validates types/contracts, and executes pure lens pipelines — producing a single canonical JSON that downstream tools can rely on.

## 🚀 The Innovation (Why Now, Why FACET)

Modern AI stacks drown in a mix of ad-hoc prompts, brittle scripts, and ambiguous configs. FACET replaces that with **contracts and determinism**.

* **Deterministic by design:** One source → one canonical JSON. No surprises.
* **Contract-first prompting:** Use `@output` to enforce **JSON Schema** on model responses. Prompts stop being strings and become **APIs with guarantees**.
* **Compile-time intelligence:** `@import`, `@vars`, `@var_types`, and `if="EXPR"` give вам модульность, параметризацию и статическую проверку ещё до запуска.
* **Pure transformation pipeline:** **Lenses (`|>`)** — встроенные детерминированные функции (в т.ч. `choose(seed)`/`shuffle(seed)`), без I/O и сайд-эффектов.
* **Security model:** Import allowlists, sandboxed lenses, отсутствие неявного доступа к окружению.

**FACET doesn’t just configure AI — it programs the instruction itself.**

---

## 🥊 FACET vs. Existing Options

| Capability / Tooling                       | YAML + JSON | Jsonnet/Cue | Templating (Jinja/Mustache) | **FACET** |
| :----------------------------------------- | :--------------: | :---------: | :-------------------------: | :-------: |
| Canonical, deterministic serialization     |        ⚠️ Depends |           ✅ |            ❌ (runtime text) |       **✅** |
| Contract-first (enforce model output)      |  🟡 External glue |          🟡 |                           ❌ | **✅ `@output`** |
| Compile-time imports & deterministic merge |        🟡 Plugins |          🟡 |                           ❌ | **✅ `@import`** |
| Static typing for variables                |   🟡 Schema hacks |           ✅ |                           ❌ | **✅ `@var_types`** |
| Conditional inclusion (no runtime eval)    |                🟡 |           ✅ |       ⚠️ Runtime templating | **✅ `if="EXPR"`** |
| Pure pipelines for text/JSON transforms    |                 ❌ |          🟡 |                           ❌ | ✅ `Lenses` |
| Deterministic randomness (seeded)          |                 ❌ |          🟡 |                           ❌ | **✅ `choose`/`shuffle`** |
| Sandbox for user plugins                   |  ⚠️ Tool-specific |          🟡 |                           ❌ | **✅ (spec §12)** |

> FACET combines the **readability of config** with the **guarantees of a DSL** that’s purpose-built for AI orchestration.

---

## 🧩 Core Concepts (v1.1)

* **Facets & Contracts:** Structured blocks (`@system`, `@user`, `@plan`, `@output`, …).
* **Modularity:** `@import` with deterministic `merge` / `replace`.
* **Variables:** `@vars` and string interpolation `{{path}}`; scalar substitution `$name`.
* **Static Typing:** `@var_types` enforces `type/enum/min/max/pattern` at compile time.
* **Conditionals:** `if="EXPR"` on any facet or list item (no runtime eval).
* **Lenses:** `value |> lensA |> lensB(...)` — pure, safe transformations (incl. deterministic `choose(seed)`/`shuffle(seed)`).
* **Security:** allowlisted imports, sandboxed lenses, no implicit env reads.

---

## 📖 Syntax in Action

```facet
# 1) Reuse prompt fragments and contracts
@import "common/prompts.facet"
@import(path="common/output_contracts.facet", strategy="merge")

# 2) Declare and type-check variables at compile-time
@vars
  username: "Alex"
  mode: "expert"
  seed: 42
  features: ["recursion", "tail-calls"]
  greetings: ["Hi", "Hello", "Hey"]

@var_types
  mode: { type: "string", enum: ["user", "expert"] }
  seed: { type: "int", min: 0 }

# 3) Conditional facets
@system(role="Deep Technical Expert", if="mode == 'expert'")
  constraints:
    - "Use precise terminology."

# 4) Interpolation + deterministic choice + formatting
@user
  request: """
    {{ greetings |> choose(seed=$seed) }}, {{username}}!
    Explain recursion with examples.
  """ |> dedent

# 5) Conditional list items
@plan
  steps:
    - "Introduction"
    - "Tail-call optimization" (if="'tail-calls' in features")

# 6) Contract-first output (enforced by host)
@output
  schema:
    type: "object"
    required: ["summary","examples"]
    properties:
      summary: { type: "string" }
      examples: { type: "array", items: { type: "string" } }
```

✅ Readable • ✅ Dynamic • ✅ Reproducible • ✅ Contract-enforced

---

## 🧭 Canonization Pipeline (Deterministic)

1. **Imports** → 2) **Variable resolution** → 3) **`@var_types` validation** →
2. **Conditional filtering** → 5) **Anchors/Aliases** → 6) **Lenses** →
3. **Canonical JSON construction** (stable key order)

> Compile-time facets (`@import`, `@vars`, `@var_types`) **do not appear** in the final JSON.

---

## 🧪 Canonical JSON (Illustrative)

```json
{
  "system": {
    "_attrs": { "role": "Deep Technical Expert" },
    "constraints": ["Use precise terminology."]
  },
  "user": {
    "request": "Hello, Alex!\nExplain recursion with examples."
  },
  "plan": {
    "steps": ["Introduction", "Tail-call optimization"]
  },
  "output": {
    "schema": {
      "type": "object",
      "required": ["summary","examples"],
      "properties": {
        "summary": { "type": "string" },
        "examples": { "type": "array", "items": { "type": "string" } }
      }
    }
  }
}
```

*(The exact content depends on chosen seed and inputs; structure and ordering are deterministic.)*

---

## 🧰 Installation

**Requirements:** Python ≥ 3.9

```bash
pip install facet-lang
```

**Python API**

```python
from facet_lang import canonize

doc = """@user
  request: "Hello"
"""
print(canonize(doc, resolve_mode="all"))
```

**CLI**

```bash
# Canonize a file
facet canon --resolve=all samples/complex.facet

# From stdin
cat samples/complex.facet | facet canon -
```

---

## 🧠 FACET System Prompt

`FACET_SYSTEM_PROMPT.md` helps LLMs produce valid `.facet` files by following syntax and canonization rules.
Use it as a system message in your agent/tooling to **generate FACET natively**.

---

## 🔐 Security Model (Essentials)

* **Imports:** allowlisted roots, no network URLs, no path escapes.
* **Variables:** no implicit env reads — host must pass them explicitly.
* **Conditionals:** dedicated parser (no `eval`).
* **Lenses:** sandboxed, timeouts, no I/O/time/random; deterministic `choose`/`shuffle` require explicit `seed`.

---

## 🧭 When to Use FACET (Real-World Wins)

* **Enterprise prompts with SLAs:** enforce output contracts → stable downstream pipelines.
* **Multi-env orchestration:** one source with `if="EXPR"`/`@vars` → dev/staging/prod without file sprawl.
* **Agent pipelines:** shared libraries via `@import`, deterministic transforms via lenses.
* **AB-tests & seeded variants:** reproducible `choose(seed)`/`shuffle(seed)` for prompt alternatives.

---

## ❓ FAQ (Objections You Might Have)

**“Why a dedicated language? Why not YAML + JSONSchema?”**
YAML remains ambiguous and typically requires external glue/scripts. FACET provides a **single deterministic pipeline** end‑to‑end: imports → typing → conditionals → lenses → canonical JSON.

**“Why not Cue/Jsonnet?”**
They are general‑purpose. FACET is purpose‑built for AI: `@output` contracts, built‑in lenses, explicit conditional semantics, bans on I/O/randomness, and determinism out of the box.

**“How do we keep it secure?”**
The spec includes sandboxing and restrictions (see §12). Lenses are pure (no I/O), imports are allowlisted, and variables are only provided explicitly by the host.

---

## 🗺️ Roadmap

### ✅ v1.1 — Foundation

* Finalize spec, strengthen reference parser, expand samples & docs.

### 🚀 Next — Tooling & Integrations

* **LSP** (VS Code/JetBrains/Zed/NeoVim): realtime diagnostics, autocomplete, hovers.
* **SDKs:** TypeScript / Rust (наряду с Python).
* **CI/CD:** ready-made GitHub Actions for canonization & schema checks.

### 🔮 Vision — Orchestration Stack

* **FACET MCP Server:** high-performance agent-first runtime.
* **Plugin Registry:** curated, sandboxed lens ecosystem.
* **Playground:** visual canonization & learning.

---

## 🤝 Contributing

* **Discussions:** ideas, proposals, showcases
* **Issues:** bugs & tasks
* **PRs:** features, fixes, docs

---

## 👤 Author

**Emil Rokossovskiy** — [@rokoss21](https://github.com/rokoss21)

---

## 📄 License

**MIT** — see [LICENSE](LICENSE)