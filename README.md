# FACET — Feature‑Aware Contracted Extension for Text
**A deterministic markup language for AI instructions**

[![PyPI version](https://img.shields.io/pypi/v/facet-lang.svg)](https://pypi.org/project/facet-lang/)
[![PyPI downloads](https://img.shields.io/pypi/dm/facet-lang.svg)](https://pypi.org/project/facet-lang/)
[![Python versions](https://img.shields.io/pypi/pyversions/facet-lang.svg)](https://pypi.org/project/facet-lang/)
[![License](https://img.shields.io/pypi/l/facet-lang.svg)](https://github.com/rokoss21/FACET/blob/main/LICENSE)

[![spec](https://img.shields.io/badge/spec-v1.0%20(r1)-4c1)](./specs/FACET-Language-Spec-v1.0-FULL-r1.md)
[![status](https://img.shields.io/badge/status-final-success)](./specs/FACET-Language-Spec-v1.0-FULL-r1.md#editorial--normative-updates-in-r1)
[![mime](https://img.shields.io/badge/MIME-application%2Ffacet-blue)](#-media-type)
[![ext](https://img.shields.io/badge/ext-.facet-blueviolet)](#-file-extension)
[![author](https://img.shields.io/badge/author-Emil%20Rokossovskiy-0aa)](#-author)

---

## ✨ What is FACET?

**FACET (Feature‑Aware Contracted Extension for Text)** is a human‑readable, machine‑deterministic markup language for **AI prompting, orchestration, and tooling**.

It merges the **clarity of plain text** with the **rigor of code**:

- Explicit data types
- Strict indentation rules (2 spaces)
- First‑class **output contracts**
- Pure, deterministic **lenses (`|>`)**
- Lossless **canonical mapping to JSON**

Every `.facet` document has **one single valid JSON representation**, making FACET ideal for **reproducible AI pipelines** and **tooling ecosystems**.

---

## 🚀 Why FACET?

FACET was born from the limitations of YAML, JSON, and ad‑hoc prompt formats used in AI projects:

| Problem in YAML/JSON | FACET’s Answer |
| --- | --- |
| Ambiguous scalars (`yes`, `on`, `null`) | Deterministic grammar (ABNF), no surprises |
| No inline transformations | Pure lenses (`|> trim |> dedent |> limit(200)`) |
| Comments missing or lossy | First‑class comments (`# …`) |
| No contracts/schemas inline | `@output` facet with JSON Schema validation |
| Poor readability for prompts | Multiline strings & fenced blocks |
| Inconsistent round‑trip | One canonical JSON, always lossless |

FACET is not "just another config format". It is a **prompt‑first contract language** — a bridge between humans and machines in AI systems.

---

## ⚖️ Comparison with Alternatives

FACET stands out from traditional data formats by addressing modern development challenges:

| Feature | YAML | JSON | TOML | **FACET** |
|---------|------|------|------|-----------|
| **Contracts & Schemas** | ❌ External validation | ❌ No built-in schemas | ❌ Limited validation | ✅ **JSON Schema integration** |
| **Data Transformations** | ❌ No built-in transforms | ❌ No transformations | ❌ No transformations | ✅ **Pure lenses** (`|> trim |> json_parse`) |
| **AI Prompt Engineering** | ❌ Not designed for AI | ❌ Verbose for prompts | ❌ Not suitable | ✅ **Structured prompts with contracts** |
| **API Contract Definition** | ❌ No contract support | ❌ No contract support | ❌ No contract support | ✅ **Complete API specifications** |
| **Configuration Management** | ⚠️ Basic templating | ❌ No templating | ⚠️ Basic templating | ✅ **Advanced templating** (`{{VAR_NAME}}`) |
| **Workflow Orchestration** | ❌ No workflow support | ❌ No workflow support | ❌ No workflow support | ✅ **Built-in workflow definitions** |
| **Multiline Strings** | ✅ Good support | ❌ Escaping required | ⚠️ Basic support | ✅ **Fenced blocks** (`````) |
| **Comments** | ✅ Full support | ❌ No comments | ✅ Full support | ✅ **Semantic comments** |
| **Deterministic Parsing** | ❌ Ambiguous scalars | ✅ Deterministic | ✅ Deterministic | ✅ **Always one canonical JSON** |
| **Tooling Ecosystem** | ✅ Mature tools | ✅ Universal support | ⚠️ Limited tools | 🚀 **Growing AI-first ecosystem** |

### 🎯 Why Choose FACET?

#### **For AI/ML Teams:**
- **Structured Prompts:** Guarantee consistent AI responses with `@output` contracts
- **Version Control:** Track prompt evolution with semantic versioning
- **Data Processing:** Built-in lenses for prompt preprocessing and cleanup

#### **For API Developers:**
- **Contract-First:** Define complete API specifications in one place
- **Automatic Validation:** Built-in request/response validation
- **Documentation Generation:** Generate docs from FACET specifications

#### **For DevOps Teams:**
- **Configuration as Code:** Structured, validated configurations
- **Secret Management:** Template variables for sensitive data
- **Environment Consistency:** Same config format across all environments

#### **For Data Engineers:**
- **ETL Orchestration:** Define complex data pipelines with dependencies
- **Quality Assurance:** Built-in data validation and monitoring
- **Error Handling:** Comprehensive error recovery and alerting

### 💡 Real-World Impact:

**Before FACET:**
```yaml
# YAML - ambiguous and limited
user:
  name: "John"
  age: 30  # Is this a number or string?
  description: |
    Multi-line text
    with formatting

# No built-in validation
# No transformations
# No contracts for AI responses
```

**With FACET:**
```facet
@user
  name: "John"
  age: 30
  description: """
    Multi-line text
    with formatting
    """
    |> dedent |> trim

@output
  schema: {
    "type": "object",
    "properties": {
      "name": {"type": "string"},
      "age": {"type": "number"},
      "description": {"type": "string"}
    }
  }
```

**Result:** Clear contracts, data transformations, guaranteed structure, AI-ready format.

---

## 🧩 Core Concepts

- **Facets** — top‑level blocks `@system`, `@user`, `@output`, etc. with optional attributes  
- **Attributes vs Inline Maps** — attributes configure the facet entity; inline maps represent data values  
- **Lenses (`|>`)** — pure transforms on values (`trim`, `dedent`, `squeeze_spaces`, `limit(1024)`, `json_minify`)  
- **Contracts** — enforceable schemas (`@output`) for deterministic model responses  
- **Anchors & Aliases** — reusable fragments, with cycle detection

---

## 📖 Syntax Snapshot

````facet
@system(role="Expert", version=1)
  style: "Friendly, concise"
  constraints:
    - "Use Markdown"
    - "English language"

@user
  request: """
      Explain recursion in Python
      with a short code example.
  """
    |> dedent |> trim |> limit(200)

@output(format="json")
  require: "Respond with JSON only."
  schema: ```json
    {
      "type": "object",
      "required": ["definition", "code", "explanation"],
      "properties": {
        "definition": {"type": "string"},
        "code": {"type": "string"},
        "explanation": {"type": "string"}
      }
    }
    ```
````

✅ Human‑readable • ✅ Tool‑friendly • ✅ Guaranteed canonical JSON

---

## 🔬 Philosophy & Ideology

1. **Determinism over ambiguity** — One canonical JSON, no hidden rules.  
2. **Purity over side‑effects** — Lenses are pure; no I/O, no randomness, no time.  
3. **Contracts over trust** — Output schemas are part of the language.  
4. **Toolability over hacks** — Designed for linting, formatting, validation, and IDEs.

> **FACET makes prompts as rigorous as APIs.**

---

## 🛠 Using the Parser

FACET ships with both a **CLI** and a **library API**.

### Install from PyPI (recommended)

```bash
# Install the latest stable version
pip install facet-lang

# Or install with optional dependencies
pip install facet-lang[dev,docs]  # For development
pip install facet-lang[all]       # For everything
```

### Install from source (development)

```bash
# Clone repository
git clone https://github.com/rokoss21/FACET.git
cd FACET

# (Optional) create virtual environment
python -m venv .venv && source .venv/bin/activate

# Install in editable mode for development
pip install -e .
```

### CLI Usage

After installation you'll have a `facet` command (or use `python -m facet.cli`).

**Available commands:**
- `facet to-json` — Convert FACET to canonical JSON
- `facet validate` — Validate against `@output.schema`
- `facet fmt` — Format FACET files
- `facet lint` — Check for errors with structured codes

```bash
# Convert FACET → canonical JSON
facet to-json examples/recursion.facet > examples/recursion.json

# Validate a document against its @output.schema
facet validate examples/recursion.facet

# Format with canonical indentation and newline policy
facet fmt path/to/file.facet

# Lint with structured error codes
facet lint path/to/file.facet
```

**Exit codes**
- `0` — success
- `1` — parse/validation error (see error code in message)
- `2` — internal error

### Library API (Python)

```python
from facet import parser

text = open("examples/recursion.facet", "r", encoding="utf-8").read()

# Parse to canonical JSON string (pretty-printed)
json_text = parser.to_json(text)

# Or build an AST / Python structure first and then dump if needed
ast = parser.parse_facet(text)         # returns a dict-like structure
# If you need a dict, ensure you serialize yourself:
import json
print(json.dumps(ast, ensure_ascii=False, indent=2))
```

> **Note:** `parser.to_json(text)` expects **source text**. If you already have an AST from `parse_facet`, dump it with `json.dumps`.

---

## 🎯 Use Cases

### 🤖 AI Prompt Engineering
```python
from facet import parser

# Parse structured prompt with contracts
prompt = parser.parse_facet("""
@system(role="Code Reviewer", version=1)
  style: "Thorough, constructive"
  constraints:
    - "Use markdown formatting"
    - "Focus on maintainability"

@user
  code: """
  def fibonacci(n):
      if n <= 1:
          return n
      return fibonacci(n-1) + fibonacci(n-2)
  """
    |> dedent |> trim

@output(format="json")
  schema: {"type": "object", "required": ["issues", "rating"]}
""")

# Use in your AI pipeline
ai_response = call_llm_with_structured_prompt(prompt)
```

### ⚙️ Configuration Management
```bash
# Validate configuration files
facet validate config.facet

# Convert to JSON for your app
facet to-json config.facet > config.json
```

### 🔧 API Contract Definition
```facet
@api(endpoint="/users", method="POST")
  description: "Create new user account"
  timeout: 30
  retries: 3

@input
  schema: {
    "type": "object",
    "required": ["email", "name"],
    "properties": {
      "email": {"type": "string", "format": "email"},
      "name": {"type": "string", "minLength": 2}
    }
  }

@output(status=201)
  schema: {
    "type": "object",
    "properties": {
      "id": {"type": "integer"},
      "created_at": {"type": "string", "format": "date-time"}
    }
  }
```

---

## 🧪 Examples

### 🚀 Quick Examples

#### **Basic Usage**
```bash
# Convert FACET to JSON
facet to-json examples/recursion.facet > output.json

# Validate FACET file
facet lint examples/recursion.facet

# Format FACET file
facet fmt examples/recursion.facet
```

### 📚 Comprehensive Examples

#### **🤖 AI Prompt Engineering**
**File:** [`examples/ai_prompt.facet`](./examples/ai_prompt.facet)
```facet
@system(role="Code Reviewer", version=1)
  style: "Thorough, constructive"
  constraints:
    - "Use markdown formatting"
    - "Focus on maintainability"

@user
  task: "Review this Python function"
  code: "def func(): pass" |> trim

@output(format="json")
  schema: {"type": "object", "required": ["issues", "rating"]}
```
**Use Case:** Structured AI prompts with guaranteed JSON responses

#### **🔧 API Contract Definition**
**File:** [`examples/api_contract.facet`](./examples/api_contract.facet)
```facet
@endpoint(path="/users", method="POST")
  description: "Create user account"
  authentication: "bearer_token"

  @request
    body: {
      "type": "object",
      "required": ["email", "name"],
      "properties": {
        "email": {"type": "string", "format": "email"}
      }
    }

  @response(status=201)
    body: {
      "type": "object",
      "properties": {
        "user_id": {"type": "string"}
      }
    }
```
**Use Case:** Complete API specifications with validation

#### **⚙️ Configuration Management**
**File:** [`examples/config_management.facet`](./examples/config_management.facet)
```facet
@database
  host: "prod-db.cluster.rds.amazonaws.com"
  credentials:
    username: "{{DB_USER}}"
    password: "{{DB_PASSWORD}}"
  ssl_mode: "require"

@cache
  type: "redis"
  url: "{{REDIS_URL}}"

@external_services
  payment_gateway:
    provider: "stripe"
    api_key: "{{STRIPE_SECRET_KEY}}"
```
**Use Case:** Production configuration with secret templating

#### **🔄 Workflow Orchestration**
**File:** [`examples/workflow_orchestration.facet`](./examples/workflow_orchestration.facet)
```facet
@workflow(name="DataPipeline", version="2.0")
  trigger: "scheduled"
  schedule: "0 */4 * * *"

@step(name="extract", order=1)
  type: "parallel"
  @source(type="postgresql", query="SELECT * FROM users")
  @source(type="rest", url="https://api.service.com/data")

@step(name="transform", order=2, depends_on="extract")
  @transform(type="lens", field="email", operations=["lower", "trim"])

@step(name="load", order=3, depends_on="transform")
  @destination(type="snowflake", table="analytics.users")
```
**Use Case:** ETL pipelines with dependencies and monitoring

#### **🧪 Data Validation & Testing**
**File:** [`examples/data_validation.facet`](./examples/data_validation.facet)
```facet
@test_suite(name="UserRegistration", version="1.1")

@test_case(name="valid_registration")
  @input
    user_data: {email: "user@example.com", password: "Secure123!"}
  @expected_output
    status: "success"
    user_id: "user_abc123"

@test_case(name="invalid_email")
  @input_matrix
    - email: ""
    - email: "invalid-email"
  @expected_output
    status: "error"
    error_code: "email_invalid"
```
**Use Case:** Comprehensive test suites with matrix testing

#### **📝 Basic Examples**
- [`examples/recursion.facet`](./examples/recursion.facet) — Simple function documentation
- [`examples/test_extended.facet`](./examples/test_extended.facet) — Extended scalars and anchors
- [`examples/simplified_complex_test.facet`](./examples/simplified_complex_test.facet) — Complex data structures
- [`tests/complete_test.facet`](./tests/complete_test.facet) — Full language features test

### 🎯 Example Categories

| Category | Complexity | Use Case | Files |
|----------|------------|----------|-------|
| **AI/ML** | Medium-High | Prompt engineering, contracts | `ai_prompt.facet` |
| **API Design** | High | Contract definition, validation | `api_contract.facet` |
| **DevOps** | Medium | Configuration management | `config_management.facet` |
| **Data Engineering** | High | ETL orchestration | `workflow_orchestration.facet` |
| **QA/Testing** | Very High | Validation suites | `data_validation.facet` |
| **Learning** | Low-Medium | Language basics | `recursion.facet`, `test_extended.facet` |

### 🔧 Working with Examples

#### **Convert Examples to JSON**
```bash
# Convert specific example
facet to-json examples/ai_prompt.facet > ai_prompt.json

# Convert all examples
for f in examples/*.facet; do
  facet to-json "$f" > "${f%.facet}.json"
done
```

#### **Validate Examples**
```bash
# Lint all examples
facet lint examples/*.facet

# Check for syntax errors
find examples -name "*.facet" -exec facet lint {} \;
```

#### **Integration Testing**
```python
from facet import parser

# Load and parse example
with open('examples/ai_prompt.facet', 'r') as f:
    content = f.read()

# Convert to JSON
json_output = parser.to_json(content)

# Use in your application
prompt_data = parser.parse_facet(content)
```

### 📖 More Examples

For additional examples and detailed documentation, see:
- **[`examples/README.md`](./examples/README.md)** — Complete examples guide
- **[`specs/FACET-Language-Spec-v1.0-FULL-r1.md`](./specs/FACET-Language-Spec-v1.0-FULL-r1.md)** — Full specification with examples
- **[GitHub Repository](https://github.com/rokoss21/FACET)** — Latest examples and community contributions

---

## 📦 Project Layout

- 📜 **Full Spec (r1)** — [`specs/FACET-Language-Spec-v1.0-FULL-r1.md`](./specs/FACET-Language-Spec-v1.0-FULL-r1.md)
- 📄 **Short Spec (r1)** — [`specs/FACET-SPEC-v1.0-r1.md`](./specs/FACET-SPEC-v1.0-r1.md)  
- 🧰 **Parser** — `src/facet/parser.py`, `src/facet/lenses.py`, `src/facet/errors.py`, `src/facet/cli.py`  
- 🧪 **Examples** — `examples/*.facet` (convert to JSON with `facet to-json`)

---

## 🧷 Lenses (built‑ins)

**Required**: `trim`, `dedent`, `squeeze_spaces`, `limit(N)`, `normalize_newlines`, `json_minify`, `strip_markdown`  
**Optional**: `lower`, `upper`, `title`, `replace(pattern,repl)`, `regex_replace(/pat/flags,repl)`

> Lens purity is **normative**: lenses operate only on their input value and **must not** access siblings, parents, global state, I/O, time, or randomness.

---

## 🧭 Canonicalization (FACET → JSON)

1. Normalize newlines to LF  
2. Tokenize; enforce 2‑space indentation; reject tabs  
3. Parse into AST (facets, statements, values)  
4. Resolve anchors/aliases; detect cycles → error  
5. Apply lens pipelines in source order  
6. Convert extended scalars/fences → strings  
7. Construct root JSON, insert facet attributes into `"_attrs"`  
8. Emit JSON with stable key ordering (UTF‑8)

---

## ❗ Errors & Diagnostics

Structured errors recommended (code, message, location):

- **F001** — Lexical error (invalid char/escape)  
- **F002** — Indentation error (tabs, wrong width)  
- **F003** — Unterminated fence/string  
- **F101** — Type error (invalid value)  
- **F102** — Lens type/unknown lens  
- **F201** — Anchor error (undefined alias, cycle)  
- **F301** — Attribute error (malformed attribute)  
- **F401** — Contract error (invalid JSON Schema)  
- **F999** — Internal error

---

## 🔐 Security

- **No hidden execution** — fences are inert text, not code  
- **No global state** — lenses cannot read filesystem/time/env  
- **Regex safety** — protect against ReDoS  
- **Resource limits** — cap size, depth, lens chain length, fence size

---

## 🗺️ Roadmap

- `facet to-json`, `facet validate`, `facet fmt`, `facet lint`
- Reference SDKs: **TypeScript**, **Python**, **Rust**
- LSP for **VS Code**, **Zed**, **Neovim**
- More lenses (e.g., `slugify`, `escape_json`, `hash(alg)`)

---

## 👤 Author

**Emil Rokossovskiy** — [@rokoss21](https://github.com/rokoss21)  
📧 ecsiar@gmail.com  
© 2025 Emil Rokossovskiy

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

The MIT License is a permissive open source license that allows:
- ✅ **Commercial use** - You can use the software for commercial purposes
- ✅ **Modification** - You can modify the software
- ✅ **Distribution** - You can distribute the software
- ✅ **Private use** - You can use the software privately
- ⚠️ **Liability** - No warranty or liability from the author
- ⚠️ **Trademark** - No trademark rights granted
