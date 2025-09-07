"""
Integration Tests for FACET MCP Server

Tests the complete MCP server functionality including:
- WebSocket communication
- Tool execution end-to-end
- Error handling
- Concurrent operations
"""

import pytest
import asyncio
import json
import websockets
from unittest.mock import Mock, patch

# Add src to path for imports
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'server'))

from facet_mcp.server import FACETMCPServer
from facet_mcp.protocol.messages import MCPMessage


class TestMCPIntegration:
    """Integration tests for complete MCP server"""

    def setup_method(self):
        """Setup test fixtures"""
        self.server = FACETMCPServer()

    @pytest.mark.asyncio
    async def test_full_tool_execution_workflow(self):
        """Test complete tool execution workflow"""
        # Test data
        facet_code = '''
@system
  role: "Test Assistant"

@user
  query: "test query"

@output
  response: "test response"
'''

        # Mock the message handler
        received_messages = []

        async def mock_message_handler(message: MCPMessage) -> MCPMessage:
            received_messages.append(message)

            if message.type == "tool_call":
                tool_data = message.data
                if tool_data["name"] == "execute":
                    # Mock successful execution
                    return MCPMessage(
                        type="tool_result",
                        data={
                            "tool_call_id": tool_data.get("id"),
                            "result": {
                                "success": True,
                                "result": {"test": "executed"},
                                "execution_time_ms": 100
                            }
                        }
                    )
            return MCPMessage(
                type="error",
                data={"error": "Unknown tool"}
            )

        # Set up server with mock handler
        self.server.message_handler = mock_message_handler

        # Simulate tool call message
        tool_call_msg = MCPMessage(
            type="tool_call",
            data={
                "id": "test-123",
                "name": "execute",
                "parameters": {
                    "facet_source": facet_code
                }
            }
        )

        # Process message
        response = await self.server.handle_message(tool_call_msg)

        # Verify response
        assert response.type == "tool_result"
        assert response.data["tool_call_id"] == "test-123"
        assert response.data["result"]["success"] is True
        assert response.data["result"]["result"]["test"] == "executed"

    @pytest.mark.asyncio
    async def test_multiple_concurrent_tools(self):
        """Test handling multiple concurrent tool calls"""
        call_count = 0

        async def mock_message_handler(message: MCPMessage) -> MCPMessage:
            nonlocal call_count
            call_count += 1

            if message.type == "tool_call":
                tool_data = message.data
                if tool_data["name"] == "apply_lenses":
                    return MCPMessage(
                        type="tool_result",
                        data={
                            "tool_call_id": tool_data.get("id"),
                            "result": {
                                "success": True,
                                "result": f"processed_{call_count}",
                                "applied_lenses": tool_data["parameters"]["lenses"]
                            }
                        }
                    )
            return MCPMessage(type="error", data={"error": "Unknown tool"})

        self.server.message_handler = mock_message_handler

        # Create multiple tool calls
        messages = []
        for i in range(3):
            msg = MCPMessage(
                type="tool_call",
                data={
                    "id": f"call-{i}",
                    "name": "apply_lenses",
                    "parameters": {
                        "input_string": f"text_{i}",
                        "lenses": ["trim"]
                    }
                }
            )
            messages.append(msg)

        # Process all messages concurrently
        tasks = [self.server.handle_message(msg) for msg in messages]
        responses = await asyncio.gather(*tasks)

        # Verify all responses
        assert len(responses) == 3
        for i, response in enumerate(responses):
            assert response.type == "tool_result"
            assert response.data["tool_call_id"] == f"call-{i}"
            assert "processed" in response.data["result"]["result"]

    @pytest.mark.asyncio
    async def test_error_handling_workflow(self):
        """Test error handling throughout the workflow"""

        async def mock_message_handler(message: MCPMessage) -> MCPMessage:
            if message.type == "tool_call":
                tool_data = message.data
                if tool_data["name"] == "execute":
                    # Simulate execution error
                    return MCPMessage(
                        type="tool_result",
                        data={
                            "tool_call_id": tool_data.get("id"),
                            "result": {
                                "success": False,
                                "error": "FACET parsing failed",
                                "error_type": "FACETError"
                            }
                        }
                    )
            return MCPMessage(
                type="error",
                data={"error": "Unknown message type"}
            )

        self.server.message_handler = mock_message_handler

        # Send tool call that will fail
        error_message = MCPMessage(
            type="tool_call",
            data={
                "id": "error-test",
                "name": "execute",
                "parameters": {
                    "facet_source": "@invalid syntax here"
                }
            }
        )

        response = await self.server.handle_message(error_message)

        # Verify error response
        assert response.type == "tool_result"
        assert response.data["tool_call_id"] == "error-test"
        assert response.data["result"]["success"] is False
        assert "FACET parsing failed" in response.data["result"]["error"]
        assert response.data["result"]["error_type"] == "FACETError"

    @pytest.mark.asyncio
    async def test_list_tools_functionality(self):
        """Test list_tools message handling"""

        async def mock_message_handler(message: MCPMessage) -> MCPMessage:
            if message.type == "list_tools":
                # Return available tools
                tools_info = []
                for tool in self.server.tools.values():
                    tools_info.append({
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.parameters
                    })

                return MCPMessage(
                    type="tools_list",
                    data={"tools": tools_info}
                )
            return MCPMessage(type="error", data={"error": "Unknown message"})

        self.server.message_handler = mock_message_handler

        # Send list_tools message
        list_message = MCPMessage(type="list_tools", data={})

        response = await self.server.handle_message(list_message)

        # Verify response
        assert response.type == "tools_list"
        tools = response.data["tools"]
        assert len(tools) == 3

        # Check that all expected tools are present
        tool_names = [tool["name"] for tool in tools]
        assert "execute" in tool_names
        assert "apply_lenses" in tool_names
        assert "validate_schema" in tool_names

        # Verify tool structure
        for tool in tools:
            assert "name" in tool
            assert "description" in tool
            assert "parameters" in tool
            assert "type" in tool["parameters"]
            assert "properties" in tool["parameters"]

    @pytest.mark.asyncio
    async def test_unknown_message_type(self):
        """Test handling of unknown message types"""

        async def mock_message_handler(message: MCPMessage) -> MCPMessage:
            return MCPMessage(
                type="error",
                data={"error": f"Unknown message type: {message.type}"}
            )

        self.server.message_handler = mock_message_handler

        # Send unknown message type
        unknown_message = MCPMessage(
            type="unknown_type",
            data={"some": "data"}
        )

        response = await self.server.handle_message(unknown_message)

        # Verify error response
        assert response.type == "error"
        assert "Unknown message type" in response.data["error"]

    @pytest.mark.asyncio
    async def test_malformed_tool_call(self):
        """Test handling of malformed tool calls"""

        async def mock_message_handler(message: MCPMessage) -> MCPMessage:
            if message.type == "tool_call":
                tool_data = message.data
                if "name" not in tool_data:
                    return MCPMessage(
                        type="error",
                        data={"error": "Missing tool name"}
                    )
                if tool_data["name"] not in self.server.tools:
                    return MCPMessage(
                        type="error",
                        data={
                            "error": f"Unknown tool: {tool_data['name']}",
                            "available_tools": list(self.server.tools.keys())
                        }
                    )
            return MCPMessage(type="error", data={"error": "Invalid message"})

        self.server.message_handler = mock_message_handler

        # Test missing tool name
        malformed_message = MCPMessage(
            type="tool_call",
            data={
                "parameters": {"test": "data"}
                # Missing "name" field
            }
        )

        response = await self.server.handle_message(malformed_message)
        assert response.type == "error"
        assert "Missing tool name" in response.data["error"]

        # Test unknown tool name
        unknown_tool_message = MCPMessage(
            type="tool_call",
            data={
                "name": "unknown_tool_12345",
                "parameters": {}
            }
        )

        response = await self.server.handle_message(unknown_tool_message)
        assert response.type == "error"
        assert "Unknown tool" in response.data["error"]
        assert "available_tools" in response.data

    @pytest.mark.asyncio
    async def test_websocket_transport_integration(self):
        """Test WebSocket transport layer integration"""
        # This test would normally require starting actual WebSocket server
        # For unit testing, we'll mock the transport layer

        with patch('websockets.serve') as mock_serve:
            mock_server = Mock()
            mock_serve.return_value = mock_server
            mock_server.wait_closed = AsyncMock()

            # Mock the server startup
            transport = self.server.transport

            # This is a simplified test - in real integration testing,
            # we would start an actual server and connect with a real client
            assert transport is not None
            assert hasattr(transport, 'start_server')
            assert hasattr(transport, 'stop_server')

    @pytest.mark.asyncio
    async def test_server_lifecycle(self):
        """Test server start/stop lifecycle"""
        with patch('websockets.serve') as mock_serve, \
             patch('facet_mcp.config.settings.config') as mock_config:

            # Mock configuration
            mock_config.server.host = "localhost"
            mock_config.server.port = 3000

            mock_server = Mock()
            mock_serve.return_value = mock_server
            mock_server.wait_closed = AsyncMock()

            # Test server start (this would normally run indefinitely)
            # In test environment, we just verify the setup
            assert self.server is not None

            # Verify server has required components
            assert hasattr(self.server, 'tools')
            assert hasattr(self.server, 'handle_message')
            assert len(self.server.tools) == 3

    @pytest.mark.asyncio
    async def test_performance_monitoring(self):
        """Test performance monitoring in tool execution"""

        async def mock_message_handler(message: MCPMessage) -> MCPMessage:
            if message.type == "tool_call":
                tool_data = message.data
                if tool_data["name"] == "execute":
                    # Include performance metrics in response
                    import time
                    start_time = time.time()
                    # Simulate some processing time
                    await asyncio.sleep(0.01)
                    execution_time = (time.time() - start_time) * 1000

                    return MCPMessage(
                        type="tool_result",
                        data={
                            "tool_call_id": tool_data.get("id"),
                            "result": {
                                "success": True,
                                "result": {"processed": True},
                                "execution_time_ms": execution_time
                            }
                        }
                    )
            return MCPMessage(type="error", data={"error": "Unknown tool"})

        self.server.message_handler = mock_message_handler

        # Execute tool and verify performance metrics
        tool_message = MCPMessage(
            type="tool_call",
            data={
                "id": "perf-test",
                "name": "execute",
                "parameters": {
                    "facet_source": "@test\n  data: test"
                }
            }
        )

        response = await self.server.handle_message(tool_message)

        assert response.type == "tool_result"
        result = response.data["result"]
        assert result["success"] is True
        assert "execution_time_ms" in result
        assert isinstance(result["execution_time_ms"], (int, float))
        assert result["execution_time_ms"] >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
