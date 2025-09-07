# FACET Language

**FACET (Feature‑Aware Contracted Extension for Text)** is a human‑readable, machine‑deterministic markup language for **AI prompting, orchestration, and tooling**.

It merges the **clarity of plain text** with the **rigor of code** through:

- ✅ Explicit data types
- ✅ Strict indentation rules (2 spaces)
- ✅ First‑class **output contracts**
- ✅ Pure, deterministic **lenses (`|>`)**
- ✅ Lossless **canonical mapping to JSON**

Every `.facet` document has **one single valid JSON representation**, making FACET ideal for **reproducible AI pipelines** and **tooling ecosystems**.

## Quick Example

```facet
@system(role="Expert", version=1)
  style: "Friendly, concise"
  constraints:
    - "Use Markdown"
    - "English language"

@user
  request: """
  Explain recursion in Python
  and provide a short example.
  """ |> dedent |> trim |> limit(200)

@output(format="json")
  require: "Respond with JSON only."
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
  ``` |> json_parse
```

## Key Features

| Feature | FACET | YAML/JSON |
|---------|--------|-----------|
| **Determinism** | ✅ Single canonical JSON | ❌ Ambiguous scalars |
| **Contracts** | ✅ `@output` with JSON Schema | ❌ No validation |
| **Transforms** | ✅ Pure lenses (`|> trim`) | ❌ Manual processing |
| **Readability** | ✅ Human-first syntax | ❌ Verbose/machine-first |
| **Tooling** | ✅ Lint, format, validate | ❌ Limited |

## Why FACET?

FACET was born from the limitations of existing formats when working with AI systems:

- **YAML Ambiguities**: No more confusion between `yes`/`no` strings and booleans
- **JSON Verbosity**: Clean syntax without excessive braces and quotes
- **Prompt Engineering**: Structured way to organize AI instructions and constraints
- **Contract Enforcement**: Built-in output validation with JSON Schema
- **Team Collaboration**: Consistent, lintable, and versionable prompt definitions

## Getting Started

=== "Installation"

    ```bash
    pip install facet-lang
    ```

=== "Quick Test"

    ```bash
    # Create a simple FACET file
    cat > hello.facet << 'EOF'
    @system
      role: "Assistant"

    @user
      message: "Hello, world!"
    EOF

    # Convert to JSON
    facet to-json hello.facet
    ```

=== "Python API"

    ```python
    from facet import parser

    facet_text = """
    @user
      query: "Hello!"
    """

    json_output = parser.to_json(facet_text)
    print(json_output)
    ```

## Community

- 📖 **[Full Specification](./spec/full.md)** — Complete language reference
- 🛠️ **[Contributing Guide](../CONTRIBUTING.md)** — How to contribute
- 🐛 **[Issue Tracker](https://github.com/rokoss21/FACET/issues)** — Bug reports and feature requests
- 💬 **[Discussions](https://github.com/rokoss21/FACET/discussions)** — Community discussions

## License

FACET is open source software licensed under the **MIT License**.

---

**Ready to get started?** Check out our [Installation Guide](./getting-started/installation.md) or dive into the [Language Overview](./language/overview.md).
