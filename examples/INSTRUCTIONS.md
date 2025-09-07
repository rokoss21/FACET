# FACET Examples - Detailed Instructions

## 🤖 AI Prompt Engineering Examples

### ai_prompt.facet - Code Review Agent
```bash
# Convert to JSON for AI consumption
facet to-json ai_prompt.facet > ai_prompt.json

# View the structured output
cat ai_prompt.json | jq .
```

**Features Demonstrated:**
- @meta facet with metadata
- @system facet with role and constraints
- Extended scalars (timestamps, durations, sizes)
- @user facet with data processing lenses
- @output facet with JSON Schema validation

### code_refactoring_assistant.facet - Refactoring Agent
```bash
# Generate refactoring prompt
facet to-json code_refactoring_assistant.facet
```

**Features Demonstrated:**
- Multi-line string processing
- @examples facet with before/after code
- @output facet with structured response format

### frontend_developer.facet - Frontend Development Agent
```bash
# Generate frontend development specifications
facet to-json frontend_developer.facet
```

**Features Demonstrated:**
- Complex nested structures
- Extended scalars for build configuration
- Performance metrics and accessibility standards

## 🔧 API Contract Examples

### api_contract.facet - REST API Specification
```bash
# Generate OpenAPI-compatible specification
facet to-json api_contract.facet > api_spec.json

# Validate the contract
facet validate api_contract.facet
```

**Features Demonstrated:**
- @endpoint facet for API definition
- Request/response schemas
- Authentication specifications
- Error handling contracts

## ⚙️ Configuration Management Examples

### config_management.facet - Production Configuration
```bash
# Generate configuration for different environments
facet to-json config_management.facet > prod_config.json

# Validate configuration structure
facet lint config_management.facet
```

**Features Demonstrated:**
- Environment-specific configurations
- Secret templating with {{VARIABLES}}
- Multi-region deployment settings
- Monitoring and alerting configurations

## 🔄 Workflow Orchestration Examples

### workflow_orchestration.facet - ETL Pipeline
```bash
# Generate workflow specification
facet to-json workflow_orchestration.facet > pipeline_spec.json

# Validate workflow structure
facet validate workflow_orchestration.facet
```

**Features Demonstrated:**
- @workflow facet with scheduling
- @step facets with dependencies
- Parallel execution patterns
- Error handling and retry logic

## 🧪 Testing Examples

### data_validation.facet - Test Suite
```bash
# Generate test specifications
facet to-json data_validation.facet > test_suite.json

# Run validation
facet validate data_validation.facet
```

**Features Demonstrated:**
- @test_suite and @test_case facets
- Matrix testing with multiple inputs
- Validation rules and assertions
- Performance testing specifications

## 🔒 Security Examples

### security_specialist.facet - Security Architecture
```bash
# Generate security requirements
facet to-json security_specialist.facet > security_spec.json
```

**Features Demonstrated:**
- Security assessment configurations
- Compliance framework specifications
- Threat modeling structures
- Access control policies

## ⚡ Performance Examples

### performance_engineer.facet - Performance Optimization
```bash
# Generate performance specifications
facet to-json performance_engineer.facet > perf_spec.json
```

**Features Demonstrated:**
- Performance SLA definitions
- Monitoring and alerting thresholds
- Scalability requirements
- Benchmark specifications

## 📝 Documentation Examples

### technical_writer.facet - Documentation Generation
```bash
# Generate documentation specifications
facet to-json technical_writer.facet > docs_spec.json
```

**Features Demonstrated:**
- Documentation structure definitions
- Content management policies
- Review and approval workflows
- Accessibility requirements

## 🔧 Code Quality Examples

### test_automation_engineer.facet - Test Automation
```bash
# Generate test automation specifications
facet to-json test_automation_engineer.facet > automation_spec.json
```

**Features Demonstrated:**
- Test automation frameworks
- CI/CD integration specifications
- Quality gate definitions
- Reporting and analytics

## 🗄️ Database Examples

### database_architecture_specialist.facet - Database Design
```bash
# Generate database specifications
facet to-json database_architecture_specialist.facet > db_spec.json
```

**Features Demonstrated:**
- Database schema definitions
- Performance optimization rules
- Security and compliance requirements
- Migration strategies

## ☁️ Infrastructure Examples

### devops_infrastructure_engineer.facet - Cloud Infrastructure
```bash
# Generate infrastructure specifications
facet to-json devops_infrastructure_engineer.facet > infra_spec.json
```

**Features Demonstrated:**
- Infrastructure as Code specifications
- Cloud provider configurations
- Deployment strategies
- Monitoring and logging setups

## 📚 Learning Examples

### recursion.facet - Basic Concepts
```bash
# Simple function documentation
facet to-json recursion.facet > recursion.json
```

**Features Demonstrated:**
- Basic FACET structure
- Simple data transformation
- JSON output generation

### test_extended.facet - Advanced Features
```bash
# Extended scalars and anchors
facet to-json test_extended.facet > extended.json
```

**Features Demonstrated:**
- Extended scalar types
- Anchor and alias usage
- Complex data structures

### simple_demo.facet - Minimal Example
```bash
# Minimal FACET demonstration
facet to-json simple_demo.facet > demo.json
```

**Features Demonstrated:**
- Minimal viable FACET document
- Core syntax elements
- Basic JSON conversion

## 🚀 Advanced Usage Patterns

### Converting Multiple Files
```bash
# Batch convert all examples
for file in *.facet; do
  facet to-json "$file" > "${file%.facet}.json"
  echo "Converted $file -> ${file%.facet}.json"
done
```

### Validating All Examples
```bash
# Lint all FACET files
find . -name "*.facet" -exec facet lint {} \;

# Validate schemas
find . -name "*.facet" -exec facet validate {} \;
```

### Using in Python Applications
```python
import json
from facet import parser

def process_facet_file(filepath):
    """Process a FACET file and return structured data."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Parse to Python dict
    data = parser.parse_facet(content)

    # Convert to JSON string
    json_str = parser.to_json(content)

    # Parse JSON for validation
    json_data = json.loads(json_str)

    return {
        'original': content,
        'parsed': data,
        'json': json_data
    }
```

### Integration with AI Systems
```python
from facet import parser
import openai

def generate_ai_response(facet_file, user_input):
    """Use FACET file to generate structured AI responses."""

    # Load FACET specification
    with open(facet_file, 'r') as f:
        spec = f.read()

    # Parse specification
    prompt_spec = parser.parse_facet(spec)

    # Build prompt from specification
    system_prompt = build_system_prompt(prompt_spec)
    user_prompt = f"{user_input}\n\nContext: {prompt_spec.get('context', '')}"

    # Generate response
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=prompt_spec.get('temperature', 0.7),
        max_tokens=prompt_spec.get('max_tokens', 1000)
    )

    return response.choices[0].message.content
```

## 🛠️ Development Workflow

### Creating New Examples
1. **Define the use case** - What problem does this example solve?
2. **Choose FACET features** - Which facets and lenses to demonstrate?
3. **Structure the content** - Use appropriate indentation and organization
4. **Add metadata** - Include @meta facet with tags and descriptions
5. **Test the example** - Validate with `facet lint` and `facet validate`
6. **Document usage** - Add instructions to this file

### Best Practices
- Use consistent naming conventions
- Include comprehensive comments
- Demonstrate error handling patterns
- Show real-world usage scenarios
- Keep examples focused and concise
- Use extended scalars where appropriate
- Include JSON Schema validation
- Test with multiple input scenarios

## 📊 Example Statistics

| Category | Files | Primary Features |
|----------|-------|------------------|
| AI Prompts | 10 | @meta, @system, @user, @output, lenses |
| API Contracts | 1 | @endpoint, schemas, validation |
| Configuration | 1 | Environment variables, secrets |
| Workflows | 1 | @workflow, @step, dependencies |
| Testing | 1 | @test_suite, @test_case, matrices |
| Security | 1 | Compliance, threat modeling |
| Performance | 1 | SLAs, monitoring, scaling |
| Documentation | 1 | Content management, workflows |
| Database | 1 | Schema design, optimization |
| Infrastructure | 1 | IaC, deployment, monitoring |
| Learning | 4 | Basic syntax, advanced features |

## 🤝 Contributing Examples

We welcome contributions of new examples! Please:
1. Follow the established patterns
2. Include comprehensive documentation
3. Test with the FACET parser
4. Add appropriate metadata
5. Update this instruction file
