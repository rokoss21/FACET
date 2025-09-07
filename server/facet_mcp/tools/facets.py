"""
FACET Tools for MCP Server

Implements the three core tools that AI agents can use through MCP:
1. execute - Full FACET document execution with SIMD optimizations
2. apply_lenses - Atomic text transformations
3. validate_schema - Data quality assurance
"""

from typing import Any, Dict, List
from ..core.facets import FACETEngine
from ..core.validator import SchemaValidator


class FACETTools:
    """
    Collection of FACET tools for MCP server.

    Provides AI agents with reliable, deterministic tools for:
    - Complex data processing pipelines
    - Text transformations
    - Data validation
    """

    def __init__(self):
        self.facets_engine = FACETEngine()
        self.schema_validator = SchemaValidator()

    async def execute(
        self,
        facet_source: str,
        variables: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Execute complete FACET document.

        This is the primary tool for complex, multi-step data processing.
        Use when you need to define input processing, transformations,
        and output contracts in a single, declarative specification.

        Args:
            facet_source: Complete FACET document as string
            variables: Optional template variables

        Returns:
            Execution result with canonical JSON output
        """
        return await self.facets_engine.execute_facet(
            facet_source=facet_source,
            variables=variables or {}
        )

    async def apply_lenses(
        self,
        input_string: str,
        lenses: List[str]
    ) -> Dict[str, Any]:
        """
        Apply FACET lenses to text.

        Use for quick, atomic text transformations when full FACET
        document execution is not needed. Perfect for cleaning up
        user input or normalizing text data.

        Args:
            input_string: Text to process
            lenses: List of lens names (e.g., ['dedent', 'trim', 'squeeze_spaces'])

        Returns:
            Processing result with transformed text
        """
        try:
            result = await self.facets_engine.apply_lenses_to_text(
                text=input_string,
                lenses=lenses
            )

            return {
                "success": True,
                "result": result,
                "applied_lenses": lenses,
                "input_length": len(input_string),
                "output_length": len(result)
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }

    async def validate_schema(
        self,
        json_object: Any,
        json_schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate JSON data against schema.

        Ensures data quality and format correctness. Use before
        returning results to users or sending data to other systems.
        Prevents common AI agent mistakes with data formats.

        Args:
            json_object: Data to validate
            json_schema: JSON Schema to validate against

        Returns:
            Validation result with success status and any errors
        """
        result = await self.schema_validator.validate(
            data=json_object,
            schema=json_schema
        )

        return {
            "success": True,
            "valid": result.is_valid,
            "errors": result.errors,
            "validated_data": result.validated_data if result.is_valid else None
        }

    def get_available_lenses(self) -> List[str]:
        """
        Get list of available FACET lenses.

        Returns:
            List of lens names that can be used with apply_lenses
        """
        return [
            "trim",
            "dedent",
            "squeeze_spaces",
            "normalize_newlines",
            "json_minify",
            "json_parse",
            "strip_markdown",
            "limit"  # Requires parameter, e.g., "limit(1000)"
        ]

    def get_tool_descriptions(self) -> Dict[str, Dict[str, Any]]:
        """
        Get detailed descriptions of all available tools.

        Returns:
            Dictionary mapping tool names to their descriptions and schemas
        """
        return {
            "execute": {
                "description": "Execute complete FACET documents with SIMD optimizations. Use for complex multi-step pipelines with input processing, transformations, and output contracts.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "facet_source": {
                            "type": "string",
                            "description": "Complete FACET document text"
                        },
                        "variables": {
                            "type": "object",
                            "description": "Optional template variables",
                            "additionalProperties": True
                        }
                    },
                    "required": ["facet_source"]
                },
                "returns": "Canonical JSON result from FACET execution"
            },

            "apply_lenses": {
                "description": "Apply FACET lenses for atomic text transformations. Perfect for cleaning and normalizing text data.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "input_string": {
                            "type": "string",
                            "description": "Text to process"
                        },
                        "lenses": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of lenses to apply (e.g., ['dedent', 'trim'])"
                        }
                    },
                    "required": ["input_string", "lenses"]
                },
                "returns": "Transformed text after applying lenses"
            },

            "validate_schema": {
                "description": "Validate JSON data against JSON Schema. Ensures data quality and prevents format errors.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "json_object": {
                            "type": "object",
                            "description": "JSON data to validate"
                        },
                        "json_schema": {
                            "type": "object",
                            "description": "JSON Schema for validation"
                        }
                    },
                    "required": ["json_object", "json_schema"]
                },
                "returns": "Validation result with success status and any errors"
            }
        }
