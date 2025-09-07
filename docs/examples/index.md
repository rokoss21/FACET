# Examples

This section contains practical examples of using FACET for various AI prompting scenarios.

## Basic Examples

### Simple Q&A

```facet
@system
  role: "Helpful Assistant"
  style: "Clear and concise"

@user
  question: "What is recursion in programming?"
```

**Output:**
```json
{
  "system": {
    "role": "Helpful Assistant",
    "style": "Clear and concise"
  },
  "user": {
    "question": "What is recursion in programming?"
  }
}
```

### With Lenses

```facet
@user
  request: """
    Explain recursion with a Python example.
    Please be thorough but not verbose.
  """
    |> dedent |> trim |> limit(300)
```

### Complex Prompt with Contract

```facet
@meta
  id: "recursion-explanation"
  version: 1.0
  author: "FACET Example"

@system(role="Programming Expert")
  style: "Educational, patient"
  constraints:
    - "Use simple language"
    - "Include working code"
    - "Explain step by step"

@user
  topic: "recursion"
  language: "Python"
  level: "beginner"

@plan
  - "Define recursion"
  - "Show base case and recursive case"
  - "Provide code example"
  - "Explain execution flow"
  - "Mention common pitfalls"

@output(format="json")
  require: "Return structured JSON with explanation and code"
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
  ``` |> json_parse
```

## Advanced Patterns

### Anchors and Aliases

```facet
@system
  style &teaching: "Educational, encouraging"
  personality: *teaching
  constraints:
    - "Use analogies"
    - "Build understanding progressively"

@user
  learning_style: *teaching
  request: "Explain quantum computing"
```

### Extended Scalars

```facet
@meta
  created: @2024-01-15T10:30:00Z
  timeout: 120s
  max_tokens: 4096
  model_size: 7B

@system
  model: "llama-2-7b-chat"
  temperature: 0.7
  max_new_tokens: 512

@user
  query: "Explain machine learning"
  context_window: 4096
```

### Multi-turn Conversation

```facet
@system
  role: "AI Tutor"
  memory: "Maintain context across turns"

@conversation
  - user: "What is a neural network?"
    assistant: "A neural network is..."
  - user: "How does backpropagation work?"
    assistant: "Backpropagation is..."
  - user: "Can you show a simple example?"

@user
  message: "Can you show a simple example?"
  history: *conversation
```

## Domain-Specific Examples

### Code Review

```facet
@system
  role: "Senior Code Reviewer"
  focus: "Security, performance, maintainability"

@code
  language: "python"
  content: """
  def authenticate_user(username, password):
      return username == "admin" and password == "12345"
  """

@user
  task: "Review this authentication function"
  code: *code
  criteria:
    - "Security vulnerabilities"
    - "Code quality"
    - "Best practices"

@output(format="json")
  schema: ```json
  {
    "type": "object",
    "properties": {
      "issues": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "severity": {"enum": ["critical", "high", "medium", "low"]},
            "category": {"type": "string"},
            "description": {"type": "string"},
            "line": {"type": "integer"},
            "suggestion": {"type": "string"}
          }
        }
      },
      "score": {"type": "integer", "minimum": 0, "maximum": 100}
    }
  }
  ``` |> json_parse
```

### Data Analysis

```facet
@system
  role: "Data Scientist"
  tools: ["pandas", "matplotlib", "scikit-learn"]

@dataset
  format: "csv"
  columns: ["feature1", "feature2", "target"]
  size: 1000
  description: "Customer churn prediction dataset"

@user
  task: "Analyze this dataset for churn prediction"
  dataset: *dataset
  requirements:
    - "Exploratory data analysis"
    - "Feature engineering suggestions"
    - "Model recommendations"

@output(format="json")
  schema: ```json
  {
    "type": "object",
    "properties": {
      "eda": {
        "type": "object",
        "properties": {
          "summary_stats": {"type": "object"},
          "correlations": {"type": "object"},
          "distributions": {"type": "object"}
        }
      },
      "recommendations": {
        "type": "array",
        "items": {"type": "string"}
      }
    }
  }
  ``` |> json_parse
```

## Testing and Validation

### Unit Test Case

```facet
@meta
  type: "unit_test"
  function: "fibonacci"

@system
  role: "Test Case Generator"
  style: "Comprehensive, edge-case focused"

@test_case
  input: 5
  expected_output: 8
  description: "Fibonacci of 5 should be 8"

@user
  task: "Generate comprehensive test cases"
  function: "fibonacci"
  test_case: *test_case

@output(format="json")
  schema: ```json
  {
    "type": "array",
    "items": {
      "type": "object",
      "properties": {
        "input": {"type": "integer"},
        "expected": {"type": "integer"},
        "description": {"type": "string"}
      }
    }
  }
  ``` |> json_parse
```

## Real-World Templates

### API Documentation

```facet
@system
  role: "Technical Writer"
  expertise: "API documentation"

@endpoint
  method: "POST"
  path: "/api/v1/users"
  description: "Create a new user"

@user
  task: "Generate comprehensive API documentation"
  endpoint: *endpoint
  requirements:
    - "Request/response examples"
    - "Error codes"
    - "Authentication details"

@output(format="markdown")
```

### Content Generation

```facet
@system
  role: "Content Creator"
  style: "Engaging, informative"
  audience: "developers"

@topic
  title: "Introduction to Microservices"
  level: "intermediate"
  format: "blog_post"

@user
  task: "Write a blog post"
  topic: *topic
  word_count: 1500
  include_code: true

@output(format="markdown")
  require: "Well-structured blog post with code examples"
```

These examples demonstrate the versatility of FACET for various AI prompting scenarios, from simple Q&A to complex multi-step workflows with validation contracts.
