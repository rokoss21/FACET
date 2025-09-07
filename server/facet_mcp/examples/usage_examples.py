"""
Usage Examples for FACET MCP Server

Demonstrates how AI agents can leverage FACET MCP tools
for common data processing and validation tasks.
"""

# Example 1: Complex Data Processing Pipeline
EXECUTE_EXAMPLE = """
@workflow(name="UserDataProcessing", version="1.0")
  description: "Process and validate user registration data"

@input
  user_data: {
    "email": "john.doe@example.com",
    "name": "John Doe",
    "age": 25,
    "preferences": ["newsletters", "updates"]
  }

@processing
  steps: [
    "validate_email_format",
    "normalize_name",
    "check_age_restrictions",
    "sanitize_preferences"
  ]

@output(format="json")
  require: "Valid processed user data"
  schema: {
    "type": "object",
    "required": ["user_id", "email", "name", "processed_at"],
    "properties": {
      "user_id": {"type": "string"},
      "email": {"type": "string", "format": "email"},
      "name": {"type": "string"},
      "processed_at": {"type": "string", "format": "date-time"}
    }
  }
"""

# Example 2: Text Cleaning and Normalization
LENSES_EXAMPLE = """
Input text: "   Hello   World   \n\n  This is a test   \n\n  With extra spaces   "

Apply lenses: ["squeeze_spaces", "trim", "dedent"]

Expected output: "Hello World\nThis is a test\nWith extra spaces"
"""

# Example 3: API Response Validation
VALIDATION_EXAMPLE = {
    "json_object": {
        "user_id": "12345",
        "email": "user@example.com",
        "created_at": "2024-01-15T10:30:00Z",
        "preferences": {
            "theme": "dark",
            "language": "en"
        }
    },
    "json_schema": {
        "type": "object",
        "required": ["user_id", "email", "created_at"],
        "properties": {
            "user_id": {"type": "string"},
            "email": {"type": "string", "format": "email"},
            "created_at": {"type": "string", "format": "date-time"},
            "preferences": {
                "type": "object",
                "properties": {
                    "theme": {"type": "string", "enum": ["light", "dark"]},
                    "language": {"type": "string"}
                }
            }
        }
    }
}

# Example 4: Template Processing with Variables
TEMPLATE_EXAMPLE = """
@system(role="Assistant")
  name: "{{assistant_name}}"
  version: "{{version}}"
  style: "{{communication_style}}"

@user
  request: "{{user_request}}"
    |> dedent |> trim

@output(format="json")
  schema: {
    "type": "object",
    "properties": {
      "response": {"type": "string"},
      "confidence": {"type": "number", "minimum": 0, "maximum": 1}
    }
  }
"""

# Example 5: Multi-step Content Processing
CONTENT_PROCESSING_EXAMPLE = """
@content_processor(version="1.0")
  description: "Process and clean user-generated content"

@input
  raw_content: "{{raw_content}}"
  content_type: "{{content_type}}"

@processing
  steps: [
    {"lens": "strip_markdown", "condition": "content_type == 'markdown'"},
    {"lens": "normalize_newlines"},
    {"lens": "squeeze_spaces"},
    {"lens": "dedent"},
    {"lens": "limit", "params": [5000]}
  ]

@output
  cleaned_content: processed_content
  word_count: "len(cleaned_content.split())"
  processing_time: execution_time
"""

# Example 6: Configuration Management
CONFIG_EXAMPLE = """
@config(name="AppSettings", version="1.0")
  environment: "{{environment}}"

@database
  host: "{{db_host}}"
  port: {{db_port}}
  name: "{{db_name}}_{{environment}}"
  credentials:
    username: "{{db_user}}"
    password: "{{db_password}}"

@cache
  type: "redis"
  host: "{{cache_host}}"
  port: {{cache_port}}
  ttl: {{cache_ttl}}

@features
  enable_debug: {{enable_debug}}
  enable_metrics: {{enable_metrics}}
  max_concurrent_users: {{max_users}}
"""


class MCPUsageExamples:
    """
    Collection of usage examples for FACET MCP Server.

    Shows AI agents how to effectively use each tool for
    different types of data processing tasks.
    """

    @staticmethod
    def get_execute_examples():
        """Examples for the execute tool"""
        return {
            "data_processing_pipeline": {
                "description": "Complete data processing workflow",
                "facet_code": EXECUTE_EXAMPLE,
                "variables": {
                    "environment": "production",
                    "db_host": "prod-db.example.com"
                }
            },
            "template_processing": {
                "description": "Process templates with variables",
                "facet_code": TEMPLATE_EXAMPLE,
                "variables": {
                    "assistant_name": "CodeAssistant",
                    "version": "2.0",
                    "communication_style": "helpful",
                    "user_request": "Help me debug this Python code"
                }
            },
            "config_management": {
                "description": "Generate configuration files",
                "facet_code": CONFIG_EXAMPLE,
                "variables": {
                    "environment": "staging",
                    "db_host": "staging-db.example.com",
                    "db_port": 5432,
                    "db_name": "myapp",
                    "db_user": "app_user",
                    "db_password": "secret123",
                    "cache_host": "cache.example.com",
                    "cache_port": 6379,
                    "cache_ttl": 3600,
                    "enable_debug": False,
                    "enable_metrics": True,
                    "max_users": 1000
                }
            }
        }

    @staticmethod
    def get_lenses_examples():
        """Examples for the apply_lenses tool"""
        return {
            "text_cleanup": {
                "description": "Clean up messy user input",
                "input_text": "   Hello   World   \n\n  This is a   test   \n\n  With extra   spaces   ",
                "lenses": ["squeeze_spaces", "trim", "dedent"]
            },
            "code_formatting": {
                "description": "Format code snippets",
                "input_text": """
                    def hello_world():
                        print("Hello, World!")
                        return True
                """,
                "lenses": ["dedent", "trim"]
            },
            "markdown_cleanup": {
                "description": "Clean markdown content",
                "input_text": "# **Hello** *World*   \n\nThis is   a test.\n\n\nMore content.",
                "lenses": ["strip_markdown", "squeeze_spaces", "normalize_newlines"]
            },
            "json_minification": {
                "description": "Minify JSON for transmission",
                "input_text": '''{
                    "name": "John",
                    "age": 30,
                    "city": "New York"
                }''',
                "lenses": ["json_minify"]
            }
        }

    @staticmethod
    def get_validation_examples():
        """Examples for the validate_schema tool"""
        return {
            "user_profile": {
                "description": "Validate user profile data",
                "json_object": {
                    "user_id": "12345",
                    "email": "user@example.com",
                    "name": "John Doe",
                    "age": 25
                },
                "json_schema": {
                    "type": "object",
                    "required": ["user_id", "email", "name"],
                    "properties": {
                        "user_id": {"type": "string"},
                        "email": {"type": "string", "format": "email"},
                        "name": {"type": "string", "minLength": 2},
                        "age": {"type": "number", "minimum": 13, "maximum": 120}
                    }
                }
            },
            "api_response": {
                "description": "Validate API response format",
                "json_object": {
                    "status": "success",
                    "data": {
                        "items": [
                            {"id": 1, "name": "Item 1"},
                            {"id": 2, "name": "Item 2"}
                        ]
                    },
                    "timestamp": "2024-01-15T10:30:00Z"
                },
                "json_schema": {
                    "type": "object",
                    "required": ["status", "data"],
                    "properties": {
                        "status": {"type": "string", "enum": ["success", "error"]},
                        "data": {
                            "type": "object",
                            "properties": {
                                "items": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "required": ["id", "name"],
                                        "properties": {
                                            "id": {"type": "number"},
                                            "name": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        },
                        "timestamp": {"type": "string", "format": "date-time"}
                    }
                }
            }
        }

    @staticmethod
    def get_workflow_examples():
        """Complete workflow examples combining multiple tools"""
        return {
            "content_processing_workflow": {
                "description": "Complete content processing workflow",
                "steps": [
                    {
                        "tool": "apply_lenses",
                        "description": "Clean and normalize raw content",
                        "parameters": {
                            "input_string": "{{raw_content}}",
                            "lenses": ["strip_markdown", "normalize_newlines", "squeeze_spaces"]
                        }
                    },
                    {
                        "tool": "execute",
                        "description": "Process content with FACET pipeline",
                        "parameters": {
                            "facet_source": CONTENT_PROCESSING_EXAMPLE,
                            "variables": {
                                "raw_content": "{{processed_content}}",
                                "content_type": "{{content_type}}"
                            }
                        }
                    },
                    {
                        "tool": "validate_schema",
                        "description": "Validate final output",
                        "parameters": {
                            "json_object": "{{facet_result}}",
                            "json_schema": {
                                "type": "object",
                                "required": ["cleaned_content", "word_count", "processing_time"]
                            }
                        }
                    }
                ]
            }
        }
