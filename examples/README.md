# FACET Usage Examples

This directory contains comprehensive examples demonstrating real-world usage scenarios for FACET.

## 🎯 Example Categories

### 🤖 AI Prompt Engineering
**File:** `ai_prompt.facet`
```bash
# Convert to JSON for AI consumption
facet to-json examples/ai_prompt.facet

# Lint for syntax errors
facet lint examples/ai_prompt.facet
```

**Use Case:** Structured AI prompts with contracts and validation
- System instructions with constraints
- User prompts with data processing lenses
- Output schemas for deterministic responses
- Temperature and token limits

### 🔧 API Contract Definition
**File:** `api_contract.facet`

**Use Case:** API documentation and testing
- Endpoint specifications
- Request/response schemas
- Authentication requirements
- Error handling contracts

### ⚙️ Configuration Management
**File:** `config_management.facet`

**Use Case:** Production configuration with secrets
- Environment-specific settings
- External service credentials
- Monitoring and alerting rules
- Security policies

### 🔄 Workflow Orchestration
**File:** `workflow_orchestration.facet`

**Use Case:** ETL pipelines and data processing
- Step dependencies and parallel execution
- Error handling and retries
- Monitoring and notifications
- Data quality validation

### 🧪 Data Validation & Testing
**File:** `data_validation.facet`

**Use Case:** Comprehensive test suites
- Positive/negative test cases
- Performance testing
- Security validation
- Matrix testing with multiple inputs

### 📝 Documentation Generation
**File:** `recursion.facet` (from original)

**Use Case:** Technical documentation
- Code examples with explanations
- Multi-format output (JSON, text)
- Structured content with lenses

## 🚀 Quick Start Examples

### 1. Simple AI Prompt
```facet
@system(role="Assistant")
  style: "Helpful and concise"

@user
  question: "What is recursion?"
    |> trim

@output(format="json")
  schema: {"type": "object", "required": ["definition", "example"]}
```

### 2. API Endpoint Spec
```facet
@endpoint(path="/users", method="POST")
  description: "Create user"

  @request
    body:
      type: "object"
      required: ["email", "name"]

  @response(status=201)
    body:
      type: "object"
      properties:
        id: {type: "string"}
        created_at: {type: "string", format: "date-time"}
```

### 3. Configuration with Secrets
```facet
@database
  host: "prod-db.example.com"
  credentials:
    username: "{{DB_USER}}"
    password: "{{DB_PASSWORD}}"

@cache
  type: "redis"
  url: "{{REDIS_URL}}"
```

## 🔧 Working with Examples

### Convert to JSON
```bash
# Convert any .facet file to canonical JSON
facet to-json examples/ai_prompt.facet > output.json

# Pretty print with jq
facet to-json examples/ai_prompt.facet | jq .
```

### Lint and Validate
```bash
# Check syntax
facet lint examples/*.facet

# Format files
# (Note: format command would be implemented in CLI)
```

### Integration Examples

#### Python Integration
```python
import facet
from facet import parser

# Parse FACET file
with open('examples/ai_prompt.facet', 'r') as f:
    ast = parser.parse_facet(f.read())

# Convert to JSON
json_output = parser.to_json(f.read())

# Use in your application
ai_prompt = ast['system']
user_query = ast['user']
output_schema = ast['output']['schema']
```

#### JavaScript/TypeScript
```javascript
// Using facet-lang via REST API or library
const facet = require('facet-lang');

const prompt = facet.parseFile('examples/ai_prompt.facet');
const jsonPrompt = facet.toJSON(prompt);

// Send to AI service
const response = await aiService.generate({
  messages: [prompt.system, prompt.user],
  schema: prompt.output.schema
});
```

## 📊 Example Statistics

| Example | Lines | Complexity | Use Case |
|---------|-------|------------|----------|
| `ai_prompt.facet` | 57 | Medium | AI Integration |
| `api_contract.facet` | 57 | High | API Design |
| `config_management.facet` | 76 | Medium | DevOps |
| `workflow_orchestration.facet` | 144 | High | Data Engineering |
| `data_validation.facet` | 176 | Very High | QA/Testing |
| `recursion.facet` | 18 | Low | Learning |

## 🎨 FACET Best Practices

### For AI Prompts
1. Use `@output` contracts for structured responses
2. Apply lenses for data preprocessing
3. Include version numbers for prompt evolution
4. Use anchors for reusable prompt components

### For API Contracts
1. Define comprehensive request/response schemas
2. Include error response specifications
3. Use authentication requirements
4. Document rate limiting and timeouts

### For Configuration
1. Use environment variables for secrets
2. Structure by component (database, cache, etc.)
3. Include validation rules where possible
4. Version configurations for deployments

### For Workflows
1. Define clear step dependencies
2. Include error handling and retries
3. Add monitoring and alerting
4. Use timeouts for reliability

## 🔗 Related Resources

- **Specification:** [`../specs/FACET-Language-Spec-v1.0-FULL-r1.md`](../specs/FACET-Language-Spec-v1.0-FULL-r1.md)
- **CLI Documentation:** [`../README.md`](../README.md)
- **Python API:** [`../src/facet/`](../src/facet/)

## 🤝 Contributing Examples

To contribute new examples:

1. Add your `.facet` file to this directory
2. Update this README with description
3. Test with `facet lint` and `facet to-json`
4. Ensure example demonstrates real use case
5. Follow FACET formatting conventions

**Examples should be practical, well-documented, and demonstrate FACET's unique capabilities!** ✨
