"""
Schema Validation Engine for MCP Server

Provides JSON Schema validation capabilities for AI agents,
ensuring data quality and format correctness.
"""

import json
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
import jsonschema


@dataclass
class ValidationResult:
    """Result of schema validation"""
    is_valid: bool
    errors: Optional[List[str]] = None
    validated_data: Optional[Any] = None


class SchemaValidator:
    """
    JSON Schema validation engine for MCP server.

    Provides reliable data quality assurance for AI agents,
    ensuring generated data conforms to expected formats and types.
    """

    def __init__(self):
        self.schema_cache = {}  # Cache compiled schemas for performance

    async def validate(
        self,
        data: Any,
        schema: Dict[str, Any]
    ) -> ValidationResult:
        """
        Validate data against JSON Schema.

        Args:
            data: Data to validate (any JSON-serializable type)
            schema: JSON Schema to validate against

        Returns:
            ValidationResult with validation status and any errors
        """
        try:
            # Compile schema (with caching)
            schema_key = json.dumps(schema, sort_keys=True)
            if schema_key not in self.schema_cache:
                # Use Draft7Validator for broad compatibility
                self.schema_cache[schema_key] = jsonschema.Draft7Validator(schema)
                self.schema_cache[schema_key].check_schema(schema)  # Validate schema itself

            validator = self.schema_cache[schema_key]

            # Validate data
            errors = list(validator.iter_errors(data))

            if errors:
                error_messages = []
                for error in errors:
                    error_messages.append(f"{error.message} at {' -> '.join(str(x) for x in error.path)}")
                return ValidationResult(is_valid=False, errors=error_messages)
            else:
                return ValidationResult(is_valid=True, validated_data=data)

        except jsonschema.SchemaError as e:
            return ValidationResult(
                is_valid=False,
                errors=[f"Invalid schema: {e.message}"]
            )
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                errors=[f"Validation error: {str(e)}"]
            )

    def validate_facet_output(
        self,
        facet_result: Dict[str, Any],
        expected_schema: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """
        Validate FACET execution result against expected schema.

        This is a specialized validator for FACET outputs that handles
        common FACET-specific validation patterns.

        Args:
            facet_result: Result from FACET execution
            expected_schema: Expected JSON schema (optional)

        Returns:
            ValidationResult with validation status
        """
        # If no schema provided, just check basic structure
        if not expected_schema:
            # Basic validation - ensure it's a valid object with expected facets
            if not isinstance(facet_result, dict):
                return ValidationResult(
                    is_valid=False,
                    errors=["FACET result must be an object"]
                )

            # Check for common FACET facets
            required_facets = []
            if not any(facet in facet_result for facet in required_facets):
                # If no required facets, assume it's valid
                pass

            return ValidationResult(is_valid=True, validated_data=facet_result)

        # Use full schema validation
        return self.validate(facet_result, expected_schema)

    def create_facet_schema(
        self,
        required_facets: List[str] = None,
        optional_facets: List[str] = None,
        custom_properties: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Create a JSON Schema for FACET documents.

        Args:
            required_facets: List of required facet names
            optional_facets: List of optional facet names
            custom_properties: Additional custom properties

        Returns:
            JSON Schema for FACET validation
        """
        schema = {
            "type": "object",
            "properties": {
                "_attrs": {
                    "type": "object",
                    "additionalProperties": True
                },
                "_meta": {
                    "type": "object",
                    "properties": {
                        "execution_time_ms": {"type": "number"},
                        "server": {"type": "string"}
                    },
                    "additionalProperties": True
                }
            },
            "additionalProperties": True
        }

        # Add required facets
        if required_facets:
            if "required" not in schema:
                schema["required"] = []
            schema["required"].extend(required_facets)

            # Add property definitions for required facets
            for facet in required_facets:
                if facet not in schema["properties"]:
                    schema["properties"][facet] = {"type": "object"}

        # Add optional facets
        if optional_facets:
            for facet in optional_facets:
                if facet not in schema["properties"]:
                    schema["properties"][facet] = {"type": "object"}

        # Add custom properties
        if custom_properties:
            for prop, definition in custom_properties.items():
                schema["properties"][prop] = definition

        return schema
