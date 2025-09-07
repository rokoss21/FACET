"""
Unit Tests for Schema Validator

Tests the JSON Schema validation functionality used by MCP server.
"""

import pytest
import json
from unittest.mock import Mock, patch

# Add src to path for imports
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'server'))

from facet_mcp.core.validator import SchemaValidator, ValidationResult


class TestSchemaValidator:
    """Test cases for schema validation"""

    def setup_method(self):
        """Setup test fixtures"""
        self.validator = SchemaValidator()

    @pytest.mark.asyncio
    async def test_validate_valid_data(self):
        """Test validation of valid data against schema"""
        data = {
            "name": "John Doe",
            "age": 30,
            "email": "john@example.com"
        }

        schema = {
            "type": "object",
            "required": ["name", "age"],
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "number", "minimum": 0},
                "email": {"type": "string", "format": "email"}
            }
        }

        result = await self.validator.validate(data, schema)

        assert result.is_valid is True
        assert result.validated_data == data
        assert result.errors is None

    @pytest.mark.asyncio
    async def test_validate_invalid_data(self):
        """Test validation of invalid data against schema"""
        data = {
            "name": "John",
            "age": "thirty"  # Should be number
        }

        schema = {
            "type": "object",
            "required": ["name", "age"],
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "number", "minimum": 0}
            }
        }

        result = await self.validator.validate(data, schema)

        assert result.is_valid is False
        assert result.validated_data is None
        assert len(result.errors) > 0
        assert "age" in str(result.errors[0]).lower()

    @pytest.mark.asyncio
    async def test_validate_missing_required_field(self):
        """Test validation with missing required field"""
        data = {
            "name": "John"
            # Missing required "age" field
        }

        schema = {
            "type": "object",
            "required": ["name", "age"],
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "number"}
            }
        }

        result = await self.validator.validate(data, schema)

        assert result.is_valid is False
        assert result.validated_data is None
        assert len(result.errors) > 0

    @pytest.mark.asyncio
    async def test_validate_invalid_schema(self):
        """Test validation with invalid schema"""
        data = {"name": "John"}
        invalid_schema = {
            "type": "invalid_type",  # Invalid JSON Schema
            "properties": {
                "name": {"type": "string"}
            }
        }

        result = await self.validator.validate(data, invalid_schema)

        assert result.is_valid is False
        assert result.validated_data is None
        assert len(result.errors) > 0
        assert "Invalid schema" in str(result.errors[0])

    @pytest.mark.asyncio
    async def test_validate_complex_schema(self):
        """Test validation with complex schema including arrays and nested objects"""
        data = {
            "user": {
                "name": "Alice",
                "age": 28,
                "preferences": ["dark_mode", "notifications"]
            },
            "posts": [
                {"title": "First Post", "published": True},
                {"title": "Second Post", "published": False}
            ]
        }

        schema = {
            "type": "object",
            "required": ["user", "posts"],
            "properties": {
                "user": {
                    "type": "object",
                    "required": ["name", "age"],
                    "properties": {
                        "name": {"type": "string"},
                        "age": {"type": "number", "minimum": 13},
                        "preferences": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    }
                },
                "posts": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["title"],
                        "properties": {
                            "title": {"type": "string"},
                            "published": {"type": "boolean"}
                        }
                    }
                }
            }
        }

        result = await self.validator.validate(data, schema)

        assert result.is_valid is True
        assert result.validated_data == data

    def test_create_facet_schema_basic(self):
        """Test creating basic FACET schema"""
        schema = self.validator.create_facet_schema(
            required_facets=["system", "user"],
            optional_facets=["output"]
        )

        assert schema["type"] == "object"
        assert "system" in schema["required"]
        assert "user" in schema["required"]
        assert "output" not in schema["required"]
        assert "properties" in schema

    def test_create_facet_schema_with_custom_properties(self):
        """Test creating FACET schema with custom properties"""
        custom_props = {
            "custom_field": {"type": "string", "maxLength": 100}
        }

        schema = self.validator.create_facet_schema(
            required_facets=["system"],
            custom_properties=custom_props
        )

        assert "custom_field" in schema["properties"]
        assert schema["properties"]["custom_field"]["type"] == "string"
        assert schema["properties"]["custom_field"]["maxLength"] == 100

    def test_validate_facet_output_success(self):
        """Test FACET output validation"""
        facet_result = {
            "system": {"role": "Assistant"},
            "user": {"query": "Hello"},
            "output": {"response": "Hi there!"}
        }

        result = self.validator.validate_facet_output(facet_result)

        assert result.is_valid is True
        assert result.validated_data == facet_result

    def test_validate_facet_output_invalid(self):
        """Test FACET output validation with invalid data"""
        invalid_result = "not an object"

        result = self.validator.validate_facet_output(invalid_result)

        assert result.is_valid is False
        assert result.errors is not None
        assert len(result.errors) > 0

    def test_schema_caching(self):
        """Test that schemas are cached for performance"""
        data = {"name": "Test"}
        schema = {
            "type": "object",
            "properties": {"name": {"type": "string"}}
        }

        # First validation should cache the schema
        result1 = self.validator.validate(data, schema)
        assert result1.is_valid is True

        # Second validation should use cached schema
        result2 = self.validator.validate(data, schema)
        assert result2.is_valid is True

        # Verify caching by checking internal cache
        schema_key = json.dumps(schema, sort_keys=True)
        assert schema_key in self.validator.schema_cache

    @pytest.mark.asyncio
    async def test_concurrent_validations(self):
        """Test concurrent schema validations"""
        import asyncio

        data = {"name": "Test", "value": 42}
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "value": {"type": "number"}
            }
        }

        # Run multiple validations concurrently
        tasks = [
            self.validator.validate(data, schema)
            for _ in range(5)
        ]

        results = await asyncio.gather(*tasks)

        # All should be valid
        for result in results:
            assert result.is_valid is True
            assert result.validated_data == data


class TestValidationResult:
    """Test cases for ValidationResult dataclass"""

    def test_valid_result(self):
        """Test valid validation result"""
        result = ValidationResult(is_valid=True, validated_data={"test": "data"})

        assert result.is_valid is True
        assert result.validated_data == {"test": "data"}
        assert result.errors is None

    def test_invalid_result(self):
        """Test invalid validation result"""
        errors = ["Missing required field", "Invalid type"]
        result = ValidationResult(is_valid=False, errors=errors)

        assert result.is_valid is False
        assert result.errors == errors
        assert result.validated_data is None

    def test_empty_result(self):
        """Test empty validation result"""
        result = ValidationResult()

        assert result.is_valid is False
        assert result.errors is None
        assert result.validated_data is None


if __name__ == "__main__":
    pytest.main([__file__])
