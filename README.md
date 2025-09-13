# FACET — Feature‑Aware Contracted Extension for Text
**A deterministic markup language for the AI era.**

<div align="center">
  <img src="https://raw.githubusercontent.com/rokoss21/FACET/main/assets/logo.png" alt="FACET Logo" width="100%" height="auto" style="max-width: 600px;">
  <br>
  <h3>🚀 Feature-Aware Contracted Extension for Text</h3>
  <p><em>Human-readable, machine-deterministic instructions for AI systems.</em></p>
</div>

[![spec](https://img.shields.io/badge/spec-v1.1%20(Draft%20r3)-4c1)](https://github.com/rokoss21/FACET/blob/main/FACET-Language-Spec-v1.1-r3.md)
[![status](https://img.shields.io/badge/status-draft-yellow)](https://github.com/rokoss21/FACET/blob/main/FACET-Language-Spec-v1.1-r3.md)
[![mime](https://img.shields.io/badge/MIME-application%2Ffacet-blue)](#)
[![ext](https://img.shields.io/badge/ext-.facet-blueviolet)](#)
[![author](https://img.shields.io/badge/author-Emil%20Rokossovskiy-0aa)](https://github.com/rokoss21)

---

## ✨ What is FACET?

**FACET** is a markup language designed from the ground up for authoring, managing, and executing instructions for AI systems. It merges the **clarity of plain text** with the **rigor of code**, enabling developers to build complex, reliable, and reproducible AI pipelines.

At its core, every FACET document deterministically compiles to a **single, canonical JSON representation**. This eliminates the ambiguity and unpredictability of formats like YAML, making FACET the ideal foundation for a robust AI tooling ecosystem.

With version 1.1, FACET evolves from a data format into a complete **compile-time configuration language**, introducing modularity, logic, and static typing to the world of AI prompting and orchestration.

## 🚀 The Innovation: Why FACET?

Modern AI development is plagued by a chaotic mix of ad-hoc prompt files, brittle scripts, and ambiguous configuration. FACET was created to replace this chaos with structure, safety, and scale.

### From Ambiguous Data to Deterministic Contracts
YAML's infamous parsing quirks (`yes`/`no`/`on`/`off`) are unacceptable in production AI systems.
> **FACET's Answer:** A strict, context-free grammar with no ambiguity. What you see is what you get. The `@output` facet allows you to enforce a JSON Schema contract on AI responses, turning unpredictable generation into reliable, structured data.

### From Static Files to Dynamic Blueprints
A prompt isn't just a static string; it's a template, a blueprint for interaction. Managing variations for different environments or user levels often leads to a spaghetti of duplicated files.
> **FACET's Answer:** A powerful, compile-time logic system.
> - **`@import`:** Build reusable libraries of prompts, configurations, and contracts.
> - **`@vars` & `{{...}}`:** Parameterize your documents with local variables and string interpolation.
> - **`if="EXPR"`:** Dynamically include or exclude entire sections of a document based on variables, creating adaptable and intelligent blueprints from a single source file.
> - **`@var_types`:** Add a layer of static analysis to validate your variables against types and constraints *before* execution.

### From Ad-Hoc Scripts to a Pure Transformation Pipeline
Text preprocessing—trimming, dedenting, cleaning—is a universal need, yet it's often handled by fragile, external scripts.
> **FACET's Answer:** **Lenses (`|>`)**, a built-in, purely functional transformation pipeline. Chain together safe, deterministic operations right inside your document. Version 1.1 introduces **deterministic choice lenses** like `choose(seed)` and `shuffle(seed)`, solving the problem of reproducible "randomness" without side effects.

**FACET doesn't just configure AI. It programs the instruction itself.**

---

## 🧩 Core Concepts of v1.1

- **Facets & Contracts:** Top-level blocks (`@system`, `@user`, `@output`) that structure instructions and define enforceable output schemas.
- **Modularity & Imports:** The `@import` directive allows you to include other `.facet` files with deterministic merge strategies (`merge`, `replace`).
- **Variables & Templating:** The `@vars` facet declares compile-time local variables, usable via `$var` substitution or `{{var.path}}` string interpolation.
- **Conditional Logic:** The `if="EXPR"` attribute can be attached to any facet or list item to dynamically include or exclude it from the final document.
- **Deterministic Lenses (`|>`):** A pipeline of pure functions for value transformation, including deterministic choice and user-defined plugins running in a secure sandbox.
- **Static Typing:** The `@var_types` facet provides compile-time validation for variables, ensuring type correctness and adherence to constraints (`enum`, `min`, `max`, `pattern`).

---

## 📖 Syntax in Action (v1.1)

This example showcases the power of FACET v1.1's features working in concert to create a dynamic, modular, and reliable AI instruction.

```facet
# 1. Import common configurations and prompt fragments
@import "common/prompts.facet"

# 2. Declare variables and their types for compile-time validation
@vars
  username: "Alex"
  mode: "expert"
  features: ["recursion", "tail-calls"]
  seed: 42
  greetings: ["Hi", "Hello", "Hey"]

@var_types
  mode: { type: "string", enum: ["user", "expert"] }
  seed: { type: "int" }

# 3. Conditionally activate a facet based on a variable
@system(role="Deep Technical Expert", if="mode == 'expert'")
  constraints:
    - "Use precise terminology."

@user
  # 4. Use variable interpolation and deterministic lenses
  request: """
    {{ greetings |> choose(seed=$seed) }}, {{username}}!
    Explain recursion.
  """ |> dedent

@plan
  steps:
    - "Introduction to recursion"
    # 5. Conditionally include a list item
    - "Explanation of tail-call optimization" (if="'tail-calls' in features")
```

✅ **Readable** &nbsp; ✅ **Dynamic** &nbsp; ✅ **Guaranteed Reproducible**

---

## 🧭 The Canonization Pipeline

The process of converting a FACET document into its canonical JSON is a strict, deterministic algorithm that ensures predictability:

1.  **Imports:** All `@import` directives are recursively expanded.
2.  **Variable Resolution:** `@vars` and host-provided variables are resolved and substituted.
3.  **Variable Type Validation:** Values in `@vars` are validated against schemas in `@var_types`.
4.  **Conditional Filtering:** All `if` attributes are evaluated, and nodes with false conditions are pruned.
5.  **Anchor & Alias Resolution:** `&anchor` and `*alias` references are resolved.
6.  **Lens Application:** Transformation pipelines (`|>`) are executed from left to right.
7.  **JSON Construction:** The final, clean Abstract Syntax Tree is mapped to JSON.

The compile-time directives (`@import`, `@vars`, `@var_types`) **do not appear** in the final JSON output.

---

## 📚 Full Language Specification

For the complete FACET v1.1 (Draft r3) language specification, see `FACET_LANGUAGE_SPEC.md`.

---

## 📦 Installation

- Requirements: Python >= 3.9
- Install from PyPI:
```bash
pip install facet-lang==0.0.1
```

Notes:
- Distribution name: `facet-lang`
- Import name: `facet_lang`
- CLI command: `facet`

## ⚡ Quickstart

Python API:
```python
from facet_lang import canonize

doc = """@user
  request: "Hello"
"""

out = canonize(doc, resolve_mode="all")
print(out)
```

CLI:
```bash
# Canonize a file
facet canon --resolve=all samples/complex.facet

# Or from stdin
cat samples/complex.facet | facet canon -
```

---

## 🧠 FACET System Prompt

`FACET_SYSTEM_PROMPT.md` is a system instruction for AI that helps compose correct and valid FACET documents.

- **Purpose**: guide LLMs to follow FACET syntax, canonization rules, and specification constraints when generating instructions.
- **How to use**: include the file’s content as a system prompt in your agent/IDE, or integrate it into your generation workflow to produce valid `.facet` files from the start.
- **Location**: see `FACET_SYSTEM_PROMPT.md` at the repository root.

## 🗺️ Roadmap: From Specification to Ecosystem

FACET is more than a language; it's the blueprint for a new generation of AI development tools.

### ✅ v1.1 — The Foundation
- **🎯 Current Focus:** Finalize the v1.1 language specification, enhance the reference parser, and expand documentation with real-world examples.

### 🚀 Next Steps — Tooling & Integration
- **💻 Language Server Protocol (LSP):** Our highest priority is building a full LSP for first-class IDE support. Expect:
  - Real-time error diagnostics and linting.
  - Autocompletion for facets, variables, and lenses.
  - Hover-info for documentation and type definitions.
  - Seamless integration with **VS Code, Zed, Neovim, and the JetBrains suite.**
- **🌐 Multi-Language SDKs:** Develop official, high-performance SDKs for **TypeScript/JavaScript** and **Rust** to broaden adoption.

### 🔮 Future Vision — The AI Orchestration Stack
- **🤖 FACET MCP (Master Control Program) Server:** A high-performance, agent-first runtime designed to execute FACET documents at scale. It will serve as a reference implementation for a new class of AI tools that are fast, reliable, and built on deterministic principles.
- **🧩 Plugin Ecosystem:** A centralized registry for discovering and sharing custom, sandboxed lens plugins.
- **🎓 Interactive Learning Platform:** A web-based playground for learning FACET and visually exploring the canonization pipeline.

---

## 🤝 Contributing

FACET is an open-source project, and we welcome community contributions. Your ideas, bug reports, and code are essential to its growth.

- **💬 [GitHub Discussions](https://github.com/rokoss21/FACET/discussions):** The best place for questions, feature proposals, and sharing your projects.
- **🐛 [GitHub Issues](https://github.com/rokoss21/FACET/issues):** For reporting bugs and tracking development tasks.
- **🛠️ Pull Requests:** We welcome PRs for bug fixes, new features, and documentation improvements.

---

## 👤 Author

**Emil Rokossovskiy** — [@rokoss21](https://github.com/rokoss21)

---

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.