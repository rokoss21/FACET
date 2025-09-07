# FACET — Feature‑Aware Contracted Extension for Text
**A deterministic markup language for AI instructions**

```
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║                ███████╗ █████╗  ██████╗███████╗████████╗               ║
║                ██╔════╝██╔══██╗██╔════╝██╔════╝╚══██╔══╝               ║
║                █████╗  ███████║██║     █████╗     ██║                  ║
║                ██╔══╝  ██╔══██║██║     ██╔══╝     ██║                  ║
║                ██║     ██║  ██║╚██████╗███████╗   ██║                  ║
║                ╚═╝     ╚═╝  ╚═╝ ╚═════╝╚══════╝   ╚═╝                  ║
║                                                                      ║
║           Feature-Aware Contracted Extension for Text                ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
```

[![PyPI version](https://img.shields.io/pypi/v/facet-lang.svg)](https://pypi.org/project/facet-lang/)
[![PyPI downloads](https://img.shields.io/pypi/dm/facet-lang.svg)](https://pypi.org/project/facet-lang/)
[![Python versions](https://img.shields.io/pypi/pyversions/facet-lang.svg)](https://pypi.org/project/facet-lang/)
[![License](https://img.shields.io/pypi/l/facet-lang.svg)](https://github.com/rokoss21/FACET/blob/main/LICENSE)
[![CI](https://github.com/rokoss21/FACET/actions/workflows/ci.yml/badge.svg)](https://github.com/rokoss21/FACET/actions/workflows/ci.yml)

[![spec](https://img.shields.io/badge/spec-v1.0%20(r1)-4c1)](https://github.com/rokoss21/FACET/blob/main/specs/FACET-Language-Spec-v1.0-FULL-r1.md)
[![status](https://img.shields.io/badge/status-final-success)](https://github.com/rokoss21/FACET/blob/main/specs/FACET-Language-Spec-v1.0-FULL-r1.md#editorial--normative-updates-in-r1)
[![mime](https://img.shields.io/badge/MIME-application%2Ffacet-blue)](#-media-type)
[![ext](https://img.shields.io/badge/ext-.facet-blueviolet)](#-file-extension)
[![author](https://img.shields.io/badge/author-Emil%20Rokossovskiy-0aa)](#-author)

---

## 📋 Table of Contents

- [✨ What is FACET?](#-what-is-facet)
- [⚡ Quickstart: Your First FACET in 60 Seconds](#-quickstart-your-first-facet-in-60-seconds)
- [🚀 Why FACET?](#-why-facet)
- [⚖️ Comparison with Alternatives](#️-comparison-with-alternatives)
- [🧩 Core Concepts](#-core-concepts)
- [🛠 CLI Usage](#-cli-usage)
- [🎯 Use Cases](#-use-cases)
- [🧪 Examples](#-examples)
- [📦 Project Layout](#-project-layout)
- [🧷 Lenses (built‑ins)](#-lenses-built‑ins)
- [🧭 Canonicalization (FACET → JSON)](#-canonicalization-facet--json)
- [❗ Errors & Diagnostics](#-errors--diagnostics)
- [🔐 Security](#-security)
- [🗺️ Roadmap](#️-roadmap)
- [🤝 Contributing](#-contributing)
- [💬 Community & Support](#-community--support)
- [👤 Author](#-author)
- [📄 License](#-license)

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

### How FACET Works

```
+------------------+     +------------------+     +-----------------+
|                  |     |                  |     |                 |
|   .facet file    | --> |   FACET Parser   | --> | Canonical JSON  |
|  (Source Text)   |     | (Lenses,         |     |   (Output)      |
|                  |     |  Contracts)      |     |                 |
+------------------+     +------------------+     +-----------------+
        |                        |                       |
        |-- Facets (@user)       |-- Data Transforms     |-- Deterministic
        |-- Attributes (name="") |-- Schema Validation   |-- Reproducible
        |-- Lenses (|> trim)     |-- Type Checking       |-- Tool-Ready
        |-- Contracts (@output)  |-- Error Handling      |-- Always Valid
```

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

---

## ⚡ Quickstart: Your First FACET in 60 Seconds

### 1. Install FACET
```bash
pip install facet-lang
```

### 2. Create your first FACET file (`greeting.facet`)
```facet
@user(name="Alex")
  message: "Hello, world!"

@output
  schema: {"type": "object", "required": ["greeting"]}
```

### 3. Convert to JSON
```bash
facet to-json greeting.facet
```

### 4. See the result! ✨
```json
{
  "user": {
    "_attrs": {
      "name": "Alex"
    },
    "message": "Hello, world!"
  },
  "output": {
    "_attrs": {},
    "schema": {
      "type": "object",
      "required": [
        "greeting"
      ]
    }
  }
}
```

**Congratulations!** 🎉 You've just created your first FACET document and converted it to canonical JSON. This demonstrates the core FACET features: **facets**, **attributes**, and **guaranteed canonical JSON output**.

### 📺 See FACET in Action

Here's what the CLI workflow looks like:

```bash
# Create a simple FACET file
echo '@user(name="Alice")
  greeting: "Hello from FACET!"
  active: true

@output
  schema: {"type": "object", "required": ["greeting"]}' > demo.facet

# Convert to JSON
facet to-json demo.facet

# Output:
# {
#   "user": {
#     "_attrs": {"name": "Alice"},
#     "greeting": "Hello from FACET!",
#     "active": true
#   },
#   "output": {
#     "_attrs": {},
#     "schema": {"type": "object", "required": ["greeting"]}
#   }
# }

# Validate the file
facet lint demo.facet  # OK: demo.facet
```

**Try it yourself!** Copy the FACET code above and run it locally.

---

## 🛠 CLI Usage

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
@meta
  id: "ai-code-reviewer"
  version: 1.0
  author: "AI Prompt Engineer"
  tags: ["code-review", "python", "best-practices", "production-ready"]

@system(role="Senior Code Reviewer", expertise="python_development")
  style: "Thorough, constructive, professional, educational"
  principles:
    - "Clean Code by Robert Martin"
    - "Python PEP 8 compliance"
    - "Security-first approach"
    - "Performance considerations"
  constraints:
    - "Use markdown formatting for readability"
    - "Focus on maintainability and scalability"
    - "Provide specific examples for improvements"
    - "Consider edge cases and error handling"
    - "Include security vulnerability assessment"

  # Extended scalars demonstration
  review_deadline: @2025-12-31T17:00:00Z  # Timestamp for review completion
  max_review_time: 30m                    # Duration limit for review
  code_size_limit: 100KB                  # Size limit for code under review
  security_pattern: /^[a-zA-Z_][a-zA-Z0-9_]*$/  # Valid Python identifier pattern

@user
  task: "Review this Python function for production readiness and security"
    |> trim

  code: """
def process_user_data(user_id, data):
    if user_id is None:
        return {"error": "Invalid user ID"}

    # Process data
    result = {"user_id": user_id, "processed": True}
    return result
  """
    |> dedent |> trim |> limit(2000)

  # Additional context with nested structures
  context:
    framework: "Flask/FastAPI"
    database: "PostgreSQL"
    deployment: "Docker + Kubernetes"
    team_size: 5
    timeline: "2 weeks to production"

@output(format="json")
  schema: ```json
    {
      "$schema": "https://json-schema.org/draft/2020-12/schema",
      "type": "object",
      "required": ["overall_assessment", "security_review", "code_quality", "performance_analysis", "production_readiness", "recommendations"],
      "properties": {
        "overall_assessment": {
          "type": "object",
          "properties": {
            "rating": {"type": "string", "enum": ["excellent", "good", "needs_work", "critical_issues"]},
            "score": {"type": "number", "minimum": 0, "maximum": 100},
            "confidence": {"type": "number", "minimum": 0, "maximum": 1}
          }
        }
      }
    }
  ```
```
**Use Case:** Complete AI agent prompt for code review with extended scalars, anchors, and comprehensive JSON Schema

#### **🔧 API Contract Definition**
**File:** [`examples/api_contract.facet`](./examples/api_contract.facet)
```facet
@meta
  id: "api-contract-designer"
  version: 1.0
  author: "API Architecture Specialist"
  tags: ["api", "rest", "design", "contracts", "documentation"]

@system(role="Senior API Architect", expertise="rest_api_design")
  style: "RESTful, pragmatic, standards-compliant, comprehensive"
  principles:
    - "REST architectural constraints"
    - "API First Development"
    - "HATEOAS principles"
    - "Resource modeling"
    - "Versioning strategies"
  constraints:
    - "Follow OpenAPI 3.0 specification"
    - "Implement proper HTTP status codes"
    - "Ensure backward compatibility"
    - "Include comprehensive error handling"
    - "Design for scalability and maintainability"

  # Extended scalars for API specification
  api_launch_date: @2025-06-01T00:00:00Z     # API launch timestamp
  response_timeout: 30s                       # API response timeout
  rate_limit_window: 1h                       # Rate limiting window
  max_request_size: 10MB                      # Maximum request payload
  api_version_pattern: /^v\d+\.\d+$/         # API versioning regex

@user
  task: "Design a comprehensive REST API for user management system"
    |> trim

  requirements:
    authentication: "JWT Bearer tokens with refresh"
    authorization: "Role-based access control (RBAC)"
    database: "PostgreSQL with connection pooling"
    caching: "Redis for session and data caching"
    monitoring: "Prometheus metrics and structured logging"

  # Complex nested business rules
  business_rules: {
    user_lifecycle: {
      registration: "Email verification required",
      activation: "Admin approval for enterprise users",
      deactivation: "Soft delete with data retention",
      deletion: "GDPR-compliant permanent deletion"
    },
    data_privacy: {
      pii_fields: ["email", "phone", "address"],
      retention_period: "7 years for financial data",
      consent_management: "Granular user preferences"
    }
  }

@endpoint(path="/users", method="POST")
  description: "Create new user account"
  authentication: "bearer_token"
  rate_limit: "100/hour"

  request:
    headers:
      content_type: "application/json"
      Authorization: "Bearer {{token}}"
    body:
      type: "object"
      required: ["email", "name"]
      properties:
        email: {type: "string", format: "email"}
        name: {type: "string", minLength: 2, maxLength: 100}
        preferences: {type: "object", additionalProperties: true}

  response:(status=201)
    description: "User created successfully"
    headers:
      content_type: "application/json"
      Location: "/users/{{user_id}}"
    body:
      type: "object"
      properties:
        user_id: {type: "string", pattern: "^user_[a-zA-Z0-9]{24}$"}
        email: {type: "string", format: "email"}
        name: {type: "string"}
        created_at: {type: "string", format: "date-time"}
        status: {type: "string", enum: ["active", "pending_verification"]}
```
**Use Case:** Complete API design system with anchors, extended scalars, and comprehensive contract definition

#### **⚙️ Configuration Management**
**File:** [`examples/config_management.facet`](./examples/config_management.facet)
```facet
@meta
  id: "config-management-system"
  version: 1.0
  author: "DevOps Configuration Specialist"
  tags: ["config", "devops", "infrastructure", "security", "monitoring"]

@system(role="Senior DevOps Engineer", expertise="infrastructure_configuration")
  style: "Infrastructure-as-Code, secure, scalable, maintainable"
  principles:
    - "Configuration as Code"
    - "Secrets Management"
    - "Environment Parity"
    - "Immutable Infrastructure"
    - "Zero Trust Security"
  constraints:
    - "Never store secrets in configuration files"
    - "Use environment-specific configurations"
    - "Implement proper validation and error handling"
    - "Ensure configuration is version controlled"
    - "Follow security best practices"

  # Extended scalars for configuration management
  config_update_frequency: 24h      # Configuration update interval
  secret_rotation_period: 90d       # Secret rotation timeframe
  backup_retention_period: 30d      # Backup retention time
  monitoring_interval: 60s          # Monitoring check interval
  log_retention_pattern: /^\d+[dh]$/ # Log retention regex pattern

@user
  task: "Design comprehensive configuration management system"
    |> trim

  requirements:
    environments: ["development", "staging", "production"]
    security_level: "enterprise"
    scalability: "auto-scaling enabled"
    compliance: ["SOC2", "GDPR", "HIPAA"]
    monitoring: "24/7 observability"

  # Complex nested configuration structure
  architecture_requirements: {
    multi_region: {
      enabled: true,
      regions: ["us-east-1", "eu-west-1", "ap-southeast-1"],
      failover_strategy: "active-passive",
      data_replication: "synchronous"
    },
    high_availability: {
      load_balancer: "application-load-balancer",
      auto_scaling: {
        min_instances: 3,
        max_instances: 50,
        target_cpu_utilization: 70
      },
      health_checks: {
        interval: 30,
        timeout: 5,
        healthy_threshold: 2,
        unhealthy_threshold: 2
      }
    },
    disaster_recovery: {
      backup_frequency: "daily",
      recovery_time_objective: "4h",
      recovery_point_objective: "1h",
      cross_region_replication: true
    }
  }

@database
  host: "prod-db-cluster.us-east-1.rds.amazonaws.com"
  port: 5432
  name: "myapp_production"
  ssl_mode: "require"
  connection_pool:
    min_connections: 10
    max_connections: 100
    connection_timeout: 30
    idle_timeout: 300
  credentials:
    username: "{{DB_USER}}"
    password: "{{DB_PASSWORD}}"
  schema: "public"
```
**Use Case:** Enterprise configuration management with anchors, extended scalars, and security policies

#### **🔄 Workflow Orchestration**
**File:** [`examples/workflow_orchestration.facet`](./examples/workflow_orchestration.facet)
```facet
@meta
  id: "workflow-orchestration-system"
  version: 1.0
  author: "Data Engineering Specialist"
  tags: ["workflow", "orchestration", "etl", "data-pipeline", "monitoring"]

@system(role="Senior Data Engineer", expertise="workflow_orchestration")
  style: "Reliable, scalable, observable, fault-tolerant"
  principles:
    - "Event-Driven Architecture"
    - "Idempotent Operations"
    - "Circuit Breaker Pattern"
    - "Graceful Degradation"
    - "Infrastructure as Code"
  constraints:
    - "Ensure exactly-once processing semantics"
    - "Implement comprehensive error handling"
    - "Maintain data quality and integrity"
    - "Optimize for cost and performance"
    - "Enable real-time monitoring and alerting"

  # Extended scalars for workflow orchestration
  pipeline_timeout: 3600s              # Maximum pipeline execution time
  retry_backoff_base: 60s             # Base delay for retry attempts
  monitoring_interval: 30s            # Health check frequency
  data_retention_period: 90d          # How long to keep processed data
  sla_response_time: 4h               # Service level agreement target
  validation_pattern: /^[a-zA-Z0-9_-]+$/ # Valid workflow name pattern

@user
  task: "Design comprehensive workflow orchestration system"
    |> trim

  requirements:
    scalability: "Handle millions of events per day"
    reliability: "99.9% uptime with automatic recovery"
    observability: "Full tracing, metrics, and logging"
    data_quality: "Schema validation and integrity checks"
    security: "End-to-end encryption and access controls"

  # Complex nested workflow architecture
  architecture_requirements: {
    event_processing: {
      throughput: "1000 events/second"
      latency: "< 100ms"
      ordering: "guaranteed within partitions"
      exactly_once: true
    },
    state_management: {
      persistence: "durable with replication"
      consistency: "strong consistency for critical data"
      backup: "automated with point-in-time recovery"
      scaling: "horizontal scaling with sharding"
    },
    error_handling: {
      retry_logic: "exponential backoff with jitter"
      dead_letter_queues: "separate queues for unprocessable messages"
      alerting: "immediate notification for critical failures"
      recovery: "automated recovery procedures"
    }
  }

@workflow(name="DataProcessingPipeline", version="2.0")
  description: "ETL pipeline for customer analytics"
  trigger: "scheduled"
  schedule: "0 */4 * * *"  # Every 4 hours
  timeout: 3600  # 1 hour max execution
  retry_policy:
    max_attempts: 3
    backoff: "exponential"
    base_delay: 60

@step(name="extract", order=1)
  description: "Extract customer data from multiple sources"
  type: "parallel"
  timeout: 900

  source:
    type: "postgresql"
    query: """
    SELECT
      customer_id,
      email,
      signup_date,
      last_login,
      total_orders,
      lifetime_value
    FROM customers
    WHERE updated_at >= '{{last_run_time}}'
    """
      |> dedent |> trim |> normalize_newlines
    connection: "{{DB_CONNECTION_STRING}}"

  source:
    type: "rest"
    url: "https://api.customer-service.com/customers"
    method: "GET"
    headers:
      Authorization: "Bearer {{API_TOKEN}}"
      Content-Type: "application/json"
    params:
      since: "{{last_run_time}}"
      limit: 1000
```
**Use Case:** Complete workflow orchestration with anchors, extended scalars, and complex data processing

#### **🧪 Data Validation & Testing**
**File:** [`examples/data_validation.facet`](./examples/data_validation.facet)
```facet
@meta
  id: "data-validation-testing-framework"
  version: 1.0
  author: "QA Automation Specialist"
  tags: ["testing", "validation", "qa", "data-quality", "test-automation"]

@system(role="Senior QA Engineer", expertise="test_automation")
  style: "Thorough, systematic, comprehensive, data-driven"
  principles:
    - "Test Pyramid Strategy (Unit > Integration > E2E)"
    - "Behavior-Driven Development (BDD)"
    - "Test Data Management"
    - "Continuous Testing"
    - "Quality Gates and Standards"
  constraints:
    - "Ensure 100% test reliability and determinism"
    - "Cover all edge cases and boundary conditions"
    - "Implement proper test isolation and cleanup"
    - "Use realistic test data and scenarios"
    - "Maintain test execution performance"

  # Extended scalars for testing framework
  test_execution_timeout: 300s           # Maximum test suite runtime
  test_data_retention: 30d               # How long to keep test results
  test_coverage_target: 85               # Minimum code coverage percentage
  test_parallelization: 4                # Number of parallel test workers
  test_retry_attempts: 2                 # Retry failed tests

@user
  task: "Design comprehensive data validation and testing framework"
    |> trim

  requirements:
    test_types: ["unit", "integration", "system", "performance"]
    coverage: "Complete edge case and boundary testing"
    automation: "CI/CD integration with automated reporting"
    data_quality: "Schema validation, constraint checking, integrity"
    performance: "Fast test execution with parallelization"

  # Complex testing framework architecture
  testing_architecture: {
    test_organization: {
      pyramid_structure: {
        unit_tests: "80% of test suite"
        integration_tests: "15% of test suite"
        e2e_tests: "5% of test suite"
      },
      test_categories: ["positive", "negative", "edge_case", "boundary", "security"]
    },
    data_management: {
      test_data_generation: "Synthetic data with realistic patterns"
      test_data_isolation: "Separate databases/schemas per test"
      test_data_cleanup: "Automatic cleanup after test completion"
      sensitive_data_masking: "PII protection in test environments"
    },
    quality_gates: {
      code_coverage: "Minimum 85% branch coverage"
      performance_regression: "No more than 5% degradation"
      security_scan: "Zero critical vulnerabilities"
      documentation: "All public APIs documented"
    }
  }

@test_suite(name="UserRegistrationValidation", version="1.1")
  description: "Comprehensive validation tests for user registration"
  environment: "testing"
  timeout: 300

@test_case(name="valid_user_registration")
  description: "Test successful user registration with valid data"
  category: "positive"

  input:
    user_data:
      email: "john.doe@example.com"
      password: "SecurePass123!"
      first_name: "John"
      last_name: "Doe"
      date_of_birth: "1990-05-15"
      phone: "+1-555-0123"
      preferences:
        newsletter: true
        notifications: "email"
        language: "en"

  expected_output:
    status: "success"
    user_id: "user_abc123def456"
    verification_token: "verify_xyz789"
    email_sent: true

  validations:
  - field: "user_id"
    rule: "pattern"
    pattern: "^user_[a-zA-Z0-9]{24}$"
  - field: "verification_token"
    rule: "length"
    min: 32
    max: 32
  - field: "email_sent"
      rule: "equals"
      value: true
```
**Use Case:** Complete testing framework with anchors, extended scalars, and comprehensive validation

#### **📝 Basic Examples**
- [`examples/recursion.facet`](./examples/recursion.facet) — Simple function documentation
- [`examples/test_extended.facet`](./examples/test_extended.facet) — Extended scalars and anchors
- [`examples/simplified_complex_test.facet`](./examples/simplified_complex_test.facet) — Complex data structures
- [`examples/simple_demo.facet`](./examples/simple_demo.facet) — Minimal FACET example

### 🎯 AI Agent Prompts (Advanced Examples)

#### **💻 Frontend Development Agent**
**File:** [`examples/frontend_developer.facet`](./examples/frontend_developer.facet)
```facet
@meta
  id: "frontend-developer"
  version: 1.0
  author: "Frontend Architecture Specialist"
  tags: ["frontend", "react", "typescript", "ui-ux", "performance"]

@system(role="Senior Frontend Engineer", expertise="modern_frontend")
  style: "Component-driven, accessible, performant, maintainable"
  principles:
    - "Component Composition over Inheritance"
    - "Progressive Enhancement"
    - "Mobile-First Responsive Design"
    - "Accessibility First (WCAG 2.1 AA)"
    - "Performance as Feature"

  build_time_target: 30s
  bundle_size_limit: 500KB
  lighthouse_target: 90
  accessibility_standard: "WCAG2.1AA"
  browser_support_pattern: /^(Chrome|Firefox|Safari|Edge)\s\d+/

@user
  task: "Build a modern, accessible, and performant React application"
    |> trim

  requirements:
    framework: "React 18 with TypeScript"
    styling: "TailwindCSS with custom design system"
    state_management: "Zustand for client state, React Query for server state"
    routing: "React Router v6 with code splitting"
    testing: "Jest + React Testing Library + Playwright"
    deployment: "Vercel with CDN and edge functions"
    monitoring: "Sentry for error tracking, Vercel Analytics for metrics"
```
**Use Case:** Complete frontend development workflow with React, TypeScript, performance optimization, and accessibility

#### **🔒 Security Specialist Agent**
**File:** [`examples/security_specialist.facet`](./examples/security_specialist.facet)
```facet
@meta
  id: "security-specialist"
  version: 1.0
  author: "Security Architecture Expert"
  tags: ["security", "owasp", "threat-modeling", "compliance", "risk-assessment"]

@system(role="Chief Information Security Officer", expertise="enterprise_security")
  style: "Defense-in-depth, risk-based, compliance-driven, proactive"
  principles:
    - "Zero Trust Architecture"
    - "Defense in Depth"
    - "Least Privilege Access"
    - "Security by Design"
    - "Continuous Security Monitoring"

  security_assessment_frequency: 90d
  vulnerability_response_time: 24h
  encryption_key_rotation: 365d
  access_review_frequency: 180d
  security_incident_pattern: /^INC-\d{4}-\d{2}-\d{2}-\d{3}$/

@user
  task: "Design and implement comprehensive security architecture"
    |> trim

  requirements:
    authentication: "Multi-factor authentication with biometrics"
    authorization: "Role-based access control with fine-grained permissions"
    data_protection: "End-to-end encryption with perfect forward secrecy"
    network_security: "Zero trust network with micro-segmentation"
    monitoring: "Real-time threat detection and automated response"
    compliance: "GDPR, HIPAA, SOC2, PCI-DSS compliance frameworks"
```
**Use Case:** Complete security architecture with threat modeling, compliance, and enterprise security controls

#### **⚡ Performance Engineer Agent**
**File:** [`examples/performance_engineer.facet`](./examples/performance_engineer.facet)
```facet
@meta
  id: "performance-engineer"
  version: 1.0
  author: "Performance Engineering Specialist"
  tags: ["performance", "optimization", "scalability", "monitoring", "benchmarking"]

@system(role="Senior Performance Engineer", expertise="system_performance")
  style: "Data-driven, systematic, scalable, measurable"
  principles:
    - "Performance as Architecture"
    - "Measure Everything"
    - "Bottleneck-Driven Optimization"
    - "Scalability Patterns"
    - "Continuous Performance Monitoring"

  response_time_sla: 100ms
  throughput_target: 1000rps
  error_budget: 0.001
  ttfb_target: 500ms
  lighthouse_score_target: 90
  performance_budget_pattern: /^\d+(ms|rps|KB|MB)$/

@user
  task: "Design and optimize high-performance system architecture"
    |> trim

  requirements:
    scalability: "Auto-scaling from 10 to 10,000 concurrent users"
    performance: "Sub-100ms response times at scale"
    reliability: "99.99% uptime with graceful degradation"
    monitoring: "Real-time performance metrics and alerting"
    optimization: "Continuous performance improvement"
```
**Use Case:** Complete performance engineering with monitoring, optimization, and scalability planning

#### **📝 Technical Writer Agent**
**File:** [`examples/technical_writer.facet`](./examples/technical_writer.facet)
```facet
@meta
  id: "technical-writer"
  version: 1.0
  author: "Technical Documentation Specialist"
  tags: ["documentation", "api-docs", "user-guides", "technical-writing", "diagrams"]

@system(role="Senior Technical Writer", expertise="technical_documentation")
  style: "Clear, concise, comprehensive, user-focused"
  principles:
    - "Write for the Reader, Not the Writer"
    - "Progressive Disclosure of Information"
    - "Active Voice and Clear Language"
    - "Consistency in Terminology and Style"
    - "Comprehensive yet Concise"

  documentation_update_frequency: 7d
  readability_score_target: 60
  content_coverage_target: 95
  review_cycle_duration: 14d
  documentation_age_limit: 365d
  version_pattern: /^v\d+\.\d+\.\d+$/

@user
  task: "Create comprehensive technical documentation for software system"
    |> trim

  requirements:
    audience: "Developers, system administrators, product managers"
    deliverables: "API docs, user guides, architecture docs, deployment guides"
    format: "Markdown with diagrams, interactive examples"
    maintenance: "Automated documentation updates with CI/CD"
    accessibility: "WCAG 2.1 AA compliant documentation"
```
**Use Case:** Complete technical writing workflow with documentation architecture, content strategy, and maintenance

#### **🔧 Code Refactoring Agent**
**File:** [`examples/code_refactoring_assistant.facet`](./examples/code_refactoring_assistant.facet)
```facet
@meta
  id: "code-refactoring-assistant"
  version: 1.0
  author: "Expert Prompt Engineer"
  tags: ["refactoring", "clean-code", "SOLID", "code-improvement"]

@system(role="Senior Software Architect", expertise="code_refactoring")
  style: "Professional, methodical, educational"
  principles:
    - "Clean Code by Robert Martin"
    - "SOLID principles"
    - "DRY (Don't Repeat Yourself)"
    - "KISS (Keep It Simple, Stupid)"

  constraints:
    - "Preserve original functionality"
    - "Maintain backward compatibility"
    - "Improve without breaking changes"
    - "Document all modifications"

@user
  task: """
    Improve code architecture and readability without changing behavior.
    Apply clean code principles and SOLID design patterns.
    Eliminate duplication, redundancy, and excessive nesting.
    Ensure consistent style and clear naming conventions.
    Always document changes made in comments.
  """
    |> dedent |> trim
```
**Use Case:** Code refactoring and quality improvement with SOLID principles and clean code practices
- [`tests/complete_test.facet`](./tests/complete_test.facet) — Full language features test

### 🎯 Example Categories

| Category | Complexity | Use Case | Files |
|----------|------------|----------|-------|
| **🤖 AI/ML** | Medium-High | Prompt engineering, contracts | `ai_prompt.facet`, `facet_complete_demo.facet` |
| **🔧 API Design** | High | Contract definition, validation | `api_contract.facet` |
| **⚙️ DevOps** | Medium | Configuration management | `config_management.facet` |
| **🔄 Data Engineering** | High | ETL orchestration | `workflow_orchestration.facet` |
| **🧪 QA/Testing** | Very High | Validation suites | `data_validation.facet` |
| **💻 Frontend Development** | High | React/TypeScript, performance | `frontend_developer.facet` |
| **🔒 Security** | Very High | Threat modeling, compliance | `security_specialist.facet` |
| **⚡ Performance** | High | Optimization, scalability | `performance_engineer.facet` |
| **📝 Technical Writing** | Medium | Documentation, guides | `technical_writer.facet` |
| **🔧 Code Quality** | Medium | Refactoring, best practices | `code_refactoring_assistant.facet` |
| **🗄️ Database Design** | High | Schema design, optimization | `database_architecture_specialist.facet` |
| **🔄 CI/CD Automation** | Medium | Testing automation | `test_automation_engineer.facet` |
| **☁️ Cloud Infrastructure** | High | IaC, deployment | `devops_infrastructure_engineer.facet` |
| **📚 Learning** | Low-Medium | Language basics | `recursion.facet`, `test_extended.facet`, `simple_demo.facet`, `simplified_complex_test.facet` |

### 📊 FACET Examples Statistics

| Metric | Value |
|--------|-------|
| **Total Examples** | 20 .facet files |
| **AI Agent Prompts** | 10 specialized roles |
| **Use Cases Covered** | 14 different domains |
| **Language Features** | All 9 facets + extended scalars + anchors + lenses |
| **Code Examples** | TypeScript, Python, Go, YAML, SQL |
| **Complexity Levels** | Low to Very High |
| **Documentation Quality** | Production-ready examples |

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

For additional examples and documentation, see:
- **[`examples/README.md`](https://github.com/rokoss21/FACET/blob/main/examples/README.md)** — Complete examples guide with 20 comprehensive use cases
- **[`specs/FACET-Language-Spec-v1.0-FULL-r1.md`](https://github.com/rokoss21/FACET/blob/main/specs/FACET-Language-Spec-v1.0-FULL-r1.md)** — Language specification and grammar
- **[`specs/FACET-SPEC-v1.0-r1.md`](https://github.com/rokoss21/FACET/blob/main/specs/FACET-SPEC-v1.0-r1.md)** — Quick reference specification
- **[GitHub Repository](https://github.com/rokoss21/FACET)** — Latest examples and community contributions

### 🚀 Future Documentation
- 📚 **MkDocs Site** - Professional documentation site (planned)
- 📖 **API Reference** - Detailed Python SDK documentation (planned)
- 🎓 **Tutorials** - Step-by-step learning guides (planned)
- 🍳 **Cookbook** - Real-world patterns and recipes (planned)

---

## 📦 Project Layout

- 📜 **Full Spec (r1)** — [`specs/FACET-Language-Spec-v1.0-FULL-r1.md`](https://github.com/rokoss21/FACET/blob/main/specs/FACET-Language-Spec-v1.0-FULL-r1.md)
- 📄 **Short Spec (r1)** — [`specs/FACET-SPEC-v1.0-r1.md`](https://github.com/rokoss21/FACET/blob/main/specs/FACET-SPEC-v1.0-r1.md)  
- 🧰 **Parser** — `src/facet/parser.py`, `src/facet/lenses.py`, `src/facet/errors.py`, `src/facet/cli.py`  
- 🧪 **Examples** — `examples/*.facet` (20 comprehensive use cases: AI agents, API design, DevOps, security, performance, documentation)

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

### ✅ Completed (v1.0+)

#### 🛠️ Core CLI Tools
- ✅ **`facet to-json`** - Convert FACET to canonical JSON
- ✅ **`facet lint`** - Syntax validation and error checking
- ✅ **`facet fmt`** - Code formatting (auto-fix whitespace/indentation)
- ✅ **`facet validate`** - Schema validation against `@output` contracts

#### 📚 Python SDK
- ✅ **Python API** - `facet` package with parser and CLI functionality
- ✅ **PyPI Distribution** - `pip install facet-lang` available
- ✅ **Type Hints** - Type annotations for better IDE support
- ✅ **Error Handling** - Structured error codes and messages

#### 🎨 Built-in Lenses
- ✅ **`trim`** - Remove leading/trailing whitespace
- ✅ **`dedent`** - Remove common leading whitespace
- ✅ **`normalize_newlines`** - Standardize line endings
- ✅ **`limit(N)`** - Truncate text to N characters
- ✅ **`json_minify`** - Compact JSON output
- ✅ **`strip_markdown`** - Remove markdown formatting
- ✅ **`squeeze_spaces`** - Collapse multiple spaces
- ✅ **`json_parse`** - Parse JSON strings to objects

#### 📖 Documentation & Examples
- ✅ **Language Specification** - FACET v1.0 formal grammar and rules
- ✅ **Interactive Examples** - 20 comprehensive use cases with working code
- ✅ **MkDocs Setup** - Documentation infrastructure prepared (rokoss21.github.io/FACET)
- ✅ **CONTRIBUTING.md** - Complete developer onboarding guide
- 🚀 **Extended Documentation** - Planned comprehensive guides and tutorials

### 🔄 In Progress

#### 🧪 Quality Assurance
- 🔄 **Golden Tests** - Output validation against expected results
- 🔄 **Performance Benchmarks** - CLI speed and memory usage tests
- 🔄 **Cross-platform Testing** - Windows, macOS, Linux validation

### 🚀 Planned (Future Releases)

#### 🔧 Additional CLI Tools
- 🚀 **`facet diff`** - Compare FACET files and show differences
- 🚀 **`facet merge`** - Merge multiple FACET documents
- 🚀 **`facet template`** - Template processing with variables
- 🚀 **`facet watch`** - File watching and auto-processing

#### 🌐 Reference SDKs
- 🚀 **TypeScript SDK** - NPM package with full type safety
- 🚀 **Rust SDK** - High-performance parsing library
- 🚀 **Go SDK** - Cloud-native implementation
- 🚀 **Java SDK** - Enterprise integration support

#### 💻 Language Server Protocol (LSP)
- 🚀 **VS Code Extension** - Full IDE support with syntax highlighting
- 🚀 **Zed Extension** - Native LSP integration
- 🚀 **Neovim Plugin** - Lua-based LSP client
- 🚀 **IntelliJ Plugin** - Java-based LSP implementation

#### 🔍 Advanced Lenses
- 🚀 **`slugify`** - Convert text to URL-safe slugs
- 🚀 **`escape_json`** - JSON string escaping
- 🚀 **`hash(alg)`** - Cryptographic hashing (SHA256, MD5, etc.)
- 🚀 **`base64_encode/decode`** - Base64 transformations
- 🚀 **`url_encode/decode`** - URL encoding operations
- 🚀 **`regex_replace`** - Advanced pattern replacement
- 🚀 **`date_format`** - Date/time formatting
- 🚀 **`number_format`** - Numeric formatting and rounding

#### ☁️ Cloud & Platform Integration
- 🚀 **GitHub Actions** - CI/CD integration
- 🚀 **Docker Images** - Containerized CLI tools
- 🚀 **AWS Lambda Layer** - Serverless processing
- 🚀 **Kubernetes Operator** - Declarative FACET processing

#### 📊 Advanced Features
- 🚀 **Streaming Parser** - Large file processing
- 🚀 **Parallel Processing** - Multi-core utilization
- 🚀 **Plugin System** - Custom lenses and extensions
- 🚀 **Schema Evolution** - Version-aware validation
- 🚀 **Import System** - Modular FACET composition

### 🎯 Community & Ecosystem

#### 🤝 Community Tools
- 🚀 **FACET Language Server** - Universal LSP implementation
- 🚀 **Editor Plugins** - Support for all major editors
- 🚀 **CI/CD Templates** - GitHub Actions, GitLab CI, Jenkins
- 🚀 **Pre-commit Hooks** - Automated quality checks

#### 📚 Learning & Education
- 🚀 **Interactive Tutorial** - Web-based FACET playground (planned)
- 🚀 **Video Course** - Comprehensive learning materials (planned)
- 🚀 **Cookbook** - Real-world patterns and recipes (planned)
- 🚀 **Migration Guides** - Converting from YAML/JSON/TOML (planned)
- 🚀 **API Reference** - Complete Python SDK documentation (planned)

### 📅 Release Timeline

#### **v1.1** (Q4 2025) - Enhancement Release
- 🔍 **Advanced Lenses** - slugify, hash, base64, regex_replace functions
- ⚡ **Performance Improvements** - Optimized parsing, memory usage, streaming support
- 🧪 **Golden Tests** - Complete output validation suite
- 📊 **Metrics & Monitoring** - Built-in performance tracking and analytics

#### **v1.2** (Q2 2026) - Ecosystem Expansion
- 🌐 **TypeScript SDK** - NPM package with full type safety
- 💻 **VS Code Extension** - Full IDE support with LSP integration
- 🔧 **Advanced CLI Tools** - `facet diff`, `facet merge`, `facet watch`, `facet template`
- 📚 **MkDocs Documentation** - Live documentation site with API reference

#### **v2.0** (Q1 2027) - Enterprise Platform
- 🔌 **Plugin System** - Extensible architecture for custom lenses and parsers
- 🦀 **Rust SDK** - High-performance parsing library with streaming support
- ☁️ **Cloud Integrations** - AWS Lambda, Docker, Kubernetes operators
- 🎯 **LSP Server** - Universal Language Server Protocol implementation
- 📈 **Enterprise Monitoring** - Advanced analytics and performance insights

#### **v2.1** (Q3 2027) - Global Ecosystem
- 🌍 **Multi-Language SDKs** - Go, Java implementations
- 🤖 **AI Integration Framework** - Native AI workflow support and optimization
- 🔄 **Auto-optimization** - Self-tuning performance and memory management
- 📖 **Interactive Learning Platform** - Web-based tutorials and playground
- 🎓 **Comprehensive Education** - Video courses, cookbook, migration guides

**Help shape FACET's future!** Share your ideas in [GitHub Discussions](https://github.com/rokoss21/FACET/discussions) or contribute via [pull requests](https://github.com/rokoss21/FACET/blob/main/CONTRIBUTING.md).

---

## 🤝 Contributing

FACET is an open-source project and we welcome contributions from the community! Whether it's reporting a bug, proposing a new feature, or submitting a pull request, your help is valued.

Please read our **[Contributing Guidelines](https://github.com/rokoss21/FACET/blob/main/CONTRIBUTING.md)** to get started.

### Ways to Contribute
- **🐛 Report a Bug:** Open an issue with a clear description and steps to reproduce
- **✨ Suggest a Feature:** Start a discussion on the GitHub Discussions tab
- **📖 Improve Documentation:** Help make docs clearer and add examples
- **🛠️ Submit a Pull Request:** We welcome PRs for bug fixes, new lenses, or improvements
- **🎯 Add Tests:** Improve test coverage and add edge case testing

---

## 💬 Community & Support

Have a question or want to share an idea?

- **💬 [GitHub Discussions](https://github.com/rokoss21/FACET/discussions):** Best place for questions, feature proposals, and sharing what you've built with FACET
- **🐛 [GitHub Issues](https://github.com/rokoss21/FACET/issues):** For reporting bugs and tracking development tasks
- **📖 [Documentation](https://github.com/rokoss21/FACET/tree/main/docs):** Current guides and examples
- **📚 [Future Documentation](https://rokoss21.github.io/FACET/):** Planned MkDocs site (coming soon)

### Stay Connected
- **⭐ Star** this repository to show your support
- **👁️ Watch** for updates and new releases
- **🔄 Fork** to contribute your own improvements
- **📣 Share** FACET with your network

---

## 👤 Author

**Emil Rokossovskiy** — [@rokoss21](https://github.com/rokoss21)
📧 ecsiar@gmail.com
© 2025 Emil Rokossovskiy

---

## 🌟 Support FACET

If you find FACET useful, please consider:

- **⭐ Star** this repository to show your support
- **🔄 Fork** to contribute your own improvements
- **📣 Share** FACET with your network
- **🤝 Contribute** via pull requests or issues
- **💬 Discuss** ideas in GitHub Discussions

**Your support helps FACET grow and become the standard for AI-first configuration!** 🚀

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

