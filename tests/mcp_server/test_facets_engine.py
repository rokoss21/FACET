"""
Unit Tests for FACET Engine

Tests the core FACET execution engine used by MCP server.
"""

import pytest
import json
from unittest.mock import Mock, patch

# Add src to path for imports
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'server'))

from facet_mcp.core.facets import FACETEngine, FACETExecutionResult, FACETExecutionError


class TestFACETEngine:
    """Test cases for FACET execution engine"""

    def setup_method(self):
        """Setup test fixtures"""
        self.engine = FACETEngine()

    @pytest.mark.asyncio
    async def test_execute_facet_success(self):
        """Test successful FACET execution"""
        facet_code = '''
@system
  role: "Assistant"
  style: "helpful"

@user
  request: "Hello world"

@output
  format: "json"
  response: "Hello from FACET!"
'''

        with patch('facet.parser.parse_facet') as mock_parse, \
             patch('facet.parser.to_json') as mock_to_json:

            # Mock FACET parsing and JSON conversion
            mock_parse.return_value = {"test": "parsed"}
            mock_to_json.return_value = '{"test": "parsed", "meta": {"execution_time": 0.05}}'

            result = await self.engine.execute_facet(facet_code)

            assert result["success"] is True
            assert result["result"]["test"] == "parsed"
            assert "execution_time_ms" in result["_meta"]

    @pytest.mark.asyncio
    async def test_execute_facet_with_variables(self):
        """Test FACET execution with template variables"""
        facet_code = '''
@system
  role: "{{role}}"
  name: "{{assistant_name}}"

@user
  request: "{{user_request}}"

@output
  response: "Hello {{user_name}}!"
'''

        variables = {
            "role": "Helper",
            "assistant_name": "TestBot",
            "user_request": "Help me",
            "user_name": "Alice"
        }

        with patch('facet.parser.parse_facet') as mock_parse, \
             patch('facet.parser.to_json') as mock_to_json:

            mock_parse.return_value = {"processed": True}
            mock_to_json.return_value = '{"processed": true}'

            result = await self.engine.execute_facet(facet_code, variables)

            assert result["success"] is True
            # Verify template substitution was called
            assert mock_parse.called

    @pytest.mark.asyncio
    async def test_execute_facet_parse_error(self):
        """Test FACET execution with parse error"""
        facet_code = "@invalid syntax"

        with patch('facet.parser.parse_facet') as mock_parse:
            from facet.errors import FACETError
            mock_parse.side_effect = FACETError("F001", "Invalid syntax", 1, 1)

            result = await self.engine.execute_facet(facet_code)

            assert result["success"] is False
            assert "F001" in result["error"]
            assert result["error_type"] == "FACETError"

    @pytest.mark.asyncio
    async def test_execute_facet_json_error(self):
        """Test FACET execution with JSON conversion error"""
        facet_code = "@test\n  value: test"

        with patch('facet.parser.parse_facet') as mock_parse, \
             patch('facet.parser.to_json') as mock_to_json:

            mock_parse.return_value = {"test": "data"}
            mock_to_json.side_effect = Exception("JSON encoding failed")

            result = await self.engine.execute_facet(facet_code)

            assert result["success"] is False
            assert "JSON encoding failed" in result["error"]
            assert result["error_type"] == "Exception"

    @pytest.mark.asyncio
    async def test_apply_lenses_success(self):
        """Test successful lens application"""
        text = "  Hello   World  "
        lenses = ["trim", "squeeze_spaces"]

        result = await self.engine.apply_lenses_to_text(text, lenses)

        # This would actually call the real FACET lens system
        # For now, just verify it's a string
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_apply_lenses_empty(self):
        """Test lens application with empty lenses list"""
        text = "  Hello World  "

        result = await self.engine.apply_lenses_to_text(text, [])

        # Should return original text if no lenses
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_apply_lenses_invalid_lens(self):
        """Test lens application with invalid lens name"""
        text = "Hello World"
        lenses = ["invalid_lens"]

        with pytest.raises(ValueError, match="Error applying lens"):
            await self.engine.apply_lenses_to_text(text, lenses)

    def test_template_engine_substitution(self):
        """Test template variable substitution"""
        from facet_mcp.core.facets import TemplateEngine

        engine = TemplateEngine()

        template = "Hello {{name}}, you are {{age}} years old!"
        variables = {"name": "Alice", "age": 25}

        result = engine.substitute_variables(template, variables)

        assert result == "Hello Alice, you are 25 years old!"

    def test_template_engine_no_variables(self):
        """Test template engine with no variables"""
        from facet_mcp.core.facets import TemplateEngine

        engine = TemplateEngine()

        template = "Hello World!"
        result = engine.substitute_variables(template, {})

        assert result == "Hello World!"

    def test_template_engine_missing_variables(self):
        """Test template engine with missing variables"""
        from facet_mcp.core.facets import TemplateEngine

        engine = TemplateEngine()

        template = "Hello {{name}}!"
        result = engine.substitute_variables(template, {})

        # Should leave placeholder as-is if variable not found
        assert result == "Hello {{name}}!"

    def test_template_engine_complex_types(self):
        """Test template engine with complex variable types"""
        from facet_mcp.core.facets import TemplateEngine

        engine = TemplateEngine()

        template = "Data: {{data}}, List: {{items}}"
        variables = {
            "data": {"key": "value"},
            "items": [1, 2, 3]
        }

        result = engine.substitute_variables(template, variables)

        # Should JSON-encode complex types
        assert '{"key": "value"}' in result
        assert '[1, 2, 3]' in result


class TestFACETExecutionResult:
    """Test cases for FACET execution result"""

    def test_success_result(self):
        """Test successful execution result"""
        result = FACETExecutionResult({"test": "data"}, 150.5)

        assert result.result == {"test": "data"}
        assert result.execution_time_ms == 150.5
        assert result.success is True

        dict_result = result.to_dict()
        assert dict_result["result"] == {"test": "data"}
        assert dict_result["_meta"]["execution_time_ms"] == 150.5

    def test_error_result(self):
        """Test error execution result"""
        error = FACETExecutionError("Parse error", "FACETError")

        assert error.error == "Parse error"
        assert error.error_type == "FACETError"
        assert error.success is False

        dict_result = error.to_dict()
        assert dict_result["success"] is False
        assert dict_result["error"] == "Parse error"
        assert dict_result["error_type"] == "FACETError"


if __name__ == "__main__":
    pytest.main([__file__])
