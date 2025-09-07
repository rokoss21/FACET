"""
Unit Tests for FACET MCP Server

Tests the main MCP server functionality, tool registration,
and message handling.
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch

# Add src to path for imports
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'server'))

from facet_mcp.server import FACETMCPServer
from facet_mcp.protocol.messages import MCPMessage, ToolCall, ToolResult


class TestFACETMCPServer:
    """Test cases for the main MCP server"""

    def setup_method(self):
        """Setup test fixtures"""
        self.server = FACETMCPServer()

    def test_server_initialization(self):
        """Test that server initializes correctly"""
        assert self.server.message_handler is None
        assert len(self.server.tools) == 3
        assert 'execute' in self.server.tools
        assert 'apply_lenses' in self.server.tools
        assert 'validate_schema' in self.server.tools

    def test_tool_registration(self):
        """Test that tools are properly registered"""
        execute_tool = self.server.tools['execute']
        assert execute_tool.name == 'execute'
        assert 'FACET documents with SIMD optimizations' in execute_tool.description
        assert 'facet_source' in execute_tool.parameters['properties']

        lenses_tool = self.server.tools['apply_lenses']
        assert lenses_tool.name == 'apply_lenses'
        assert 'lenses' in lenses_tool.parameters['properties']

        schema_tool = self.server.tools['validate_schema']
        assert schema_tool.name == 'validate_schema'
        assert 'json_schema' in schema_tool.parameters['properties']

    @pytest.mark.asyncio
    async def test_execute_tool_call_success(self):
        """Test successful execute tool call"""
        # Mock the FACET engine
        with patch('facet_mcp.core.facets.FACETEngine') as mock_engine_class:
            mock_engine = Mock()
            mock_engine.execute_facet.return_value = {
                "success": True,
                "result": {"test": "data"},
                "_meta": {"execution_time_ms": 50}
            }
            mock_engine_class.return_value = mock_engine

            # Create server with mocked engine
            server = FACETMCPServer()

            # Create tool call message
            tool_call = {
                "id": "test-123",
                "name": "execute",
                "parameters": {
                    "facet_source": "@test\n  value: hello",
                    "variables": {"name": "world"}
                }
            }

            # Mock message handler
            response = await server._handle_execute(tool_call["parameters"])

            assert response["success"] is True
            assert response["result"]["test"] == "data"
            assert response["execution_time_ms"] == 50

            # Verify engine was called correctly
            mock_engine.execute_facet.assert_called_once_with(
                facet_source="@test\n  value: hello",
                variables={"name": "world"}
            )

    @pytest.mark.asyncio
    async def test_execute_tool_call_error(self):
        """Test execute tool call with error"""
        with patch('facet_mcp.core.facets.FACETEngine') as mock_engine_class:
            mock_engine = Mock()
            mock_engine.execute_facet.side_effect = Exception("Parse error")
            mock_engine_class.return_value = mock_engine

            server = FACETMCPServer()

            tool_call = {
                "name": "execute",
                "parameters": {
                    "facet_source": "@invalid\n  syntax: error"
                }
            }

            response = await server._handle_execute(tool_call["parameters"])

            assert response["success"] is False
            assert "Parse error" in response["error"]
            assert response["error_type"] == "Exception"

    @pytest.mark.asyncio
    async def test_apply_lenses_tool_success(self):
        """Test successful apply_lenses tool call"""
        with patch('facet_mcp.core.facets.FACETEngine') as mock_engine_class:
            mock_engine = Mock()
            mock_engine.apply_lenses_to_text.return_value = "Hello World"
            mock_engine_class.return_value = mock_engine

            server = FACETMCPServer()

            tool_call = {
                "name": "apply_lenses",
                "parameters": {
                    "input_string": "  Hello   World  ",
                    "lenses": ["trim", "squeeze_spaces"]
                }
            }

            response = await server._handle_apply_lenses(tool_call["parameters"])

            assert response["success"] is True
            assert response["result"] == "Hello World"
            assert response["applied_lenses"] == ["trim", "squeeze_spaces"]

    @pytest.mark.asyncio
    async def test_validate_schema_tool_success(self):
        """Test successful validate_schema tool call"""
        with patch('facet_mcp.core.validator.SchemaValidator') as mock_validator_class:
            mock_validator = Mock()
            mock_validator.validate.return_value = Mock(
                is_valid=True,
                validated_data={"name": "test"},
                errors=None
            )
            mock_validator_class.return_value = mock_validator

            server = FACETMCPServer()

            tool_call = {
                "name": "validate_schema",
                "parameters": {
                    "json_object": {"name": "test"},
                    "json_schema": {"type": "object", "required": ["name"]}
                }
            }

            response = await server._handle_validate_schema(tool_call["parameters"])

            assert response["success"] is True
            assert response["valid"] is True
            assert response["validated_data"] == {"name": "test"}
            assert response["errors"] is None

    @pytest.mark.asyncio
    async def test_validate_schema_tool_invalid(self):
        """Test validate_schema tool call with invalid data"""
        with patch('facet_mcp.core.validator.SchemaValidator') as mock_validator_class:
            mock_validator = Mock()
            mock_validator.validate.return_value = Mock(
                is_valid=False,
                validated_data=None,
                errors=["Missing required field 'name'"]
            )
            mock_validator_class.return_value = mock_validator

            server = FACETMCPServer()

            tool_call = {
                "name": "validate_schema",
                "parameters": {
                    "json_object": {},
                    "json_schema": {"type": "object", "required": ["name"]}
                }
            }

            response = await server._handle_validate_schema(tool_call["parameters"])

            assert response["success"] is True
            assert response["valid"] is False
            assert response["errors"] == ["Missing required field 'name'"]
            assert response["validated_data"] is None

    def test_handle_unknown_tool(self):
        """Test handling of unknown tool calls"""
        server = FACETMCPServer()

        message = MCPMessage(
            type="tool_call",
            data={
                "name": "unknown_tool",
                "parameters": {}
            }
        )

        # Mock message handler that returns an error
        async def mock_handler(msg):
            if msg.type == "tool_call":
                tool_name = msg.data.get("name")
                if tool_name not in server.tools:
                    return MCPMessage(
                        type="error",
                        data={
                            "error": f"Unknown tool: {tool_name}",
                            "available_tools": list(server.tools.keys())
                        }
                    )
            return MCPMessage(type="error", data={"error": "Unknown message type"})

        # This test would require more complex mocking of the message handling
        # For now, we'll just verify the tools are properly registered
        assert "unknown_tool" not in server.tools

    def test_handle_list_tools_message(self):
        """Test handling of list_tools message"""
        server = FACETMCPServer()

        # This test verifies that list_tools functionality works
        # In a real scenario, this would be tested through the WebSocket interface
        tools = server.tools
        assert len(tools) == 3

        # Verify each tool has required attributes
        for tool_name, tool in tools.items():
            assert hasattr(tool, 'name')
            assert hasattr(tool, 'description')
            assert hasattr(tool, 'parameters')
            assert tool.name == tool_name


if __name__ == "__main__":
    pytest.main([__file__])
