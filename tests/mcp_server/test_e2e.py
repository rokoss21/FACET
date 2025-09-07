"""
End-to-End Tests for FACET MCP Server

Tests the complete MCP server with real WebSocket connections,
simulating actual AI agent interactions.
"""

import pytest
import asyncio
import json
import websockets
from contextlib import asynccontextmanager

# Add src to path for imports
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'server'))

from facet_mcp.server import FACETMCPServer


@asynccontextmanager
async def mcp_server_lifecycle(host="localhost", port=3001):
    """Context manager for MCP server lifecycle"""
    server = FACETMCPServer()

    # Start server
    server_task = asyncio.create_task(server.start(host, port))

    # Give server time to start
    await asyncio.sleep(0.1)

    try:
        yield server, f"ws://{host}:{port}"
    finally:
        # Stop server
        await server.stop()
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass


class TestMCPE2E:
    """End-to-end tests with real WebSocket connections"""

    @pytest.mark.asyncio
    async def test_websocket_connection(self):
        """Test basic WebSocket connection to MCP server"""
        async with mcp_server_lifecycle() as (server, ws_url):
            try:
                async with websockets.connect(ws_url) as websocket:
                    # Test connection
                    assert websocket.open
                    print("✅ WebSocket connection established")
            except Exception as e:
                pytest.fail(f"WebSocket connection failed: {e}")

    @pytest.mark.asyncio
    async def test_list_tools_e2e(self):
        """Test list_tools through WebSocket"""
        async with mcp_server_lifecycle() as (server, ws_url):
            async with websockets.connect(ws_url) as websocket:
                # Send list_tools message
                list_message = {
                    "type": "list_tools",
                    "data": {}
                }

                await websocket.send(json.dumps(list_message))

                # Receive response
                response_raw = await websocket.recv()
                response = json.loads(response_raw)

                # Verify response
                assert response["type"] == "tools_list"
                assert "tools" in response["data"]
                assert len(response["data"]["tools"]) == 3

                # Check tool names
                tool_names = [tool["name"] for tool in response["data"]["tools"]]
                assert "execute" in tool_names
                assert "apply_lenses" in tool_names
                assert "validate_schema" in tool_names

                print("✅ List tools E2E test passed")

    @pytest.mark.asyncio
    async def test_execute_tool_e2e(self):
        """Test execute tool through WebSocket"""
        facet_code = '''
@system
  role: "Test Assistant"

@user
  query: "test query"

@output
  response: "test response"
'''

        async with mcp_server_lifecycle() as (server, ws_url):
            async with websockets.connect(ws_url) as websocket:
                # Send execute tool call
                execute_message = {
                    "type": "tool_call",
                    "data": {
                        "id": "e2e-test-123",
                        "name": "execute",
                        "parameters": {
                            "facet_source": facet_code
                        }
                    }
                }

                await websocket.send(json.dumps(execute_message))

                # Receive response
                response_raw = await websocket.recv()
                response = json.loads(response_raw)

                # Verify response structure
                assert response["type"] == "tool_result"
                assert response["data"]["tool_call_id"] == "e2e-test-123"

                result = response["data"]["result"]
                assert "success" in result
                assert "execution_time_ms" in result["_meta"]

                print("✅ Execute tool E2E test passed")

    @pytest.mark.asyncio
    async def test_apply_lenses_e2e(self):
        """Test apply_lenses tool through WebSocket"""
        async with mcp_server_lifecycle() as (server, ws_url):
            async with websockets.connect(ws_url) as websocket:
                # Send apply_lenses tool call
                lenses_message = {
                    "type": "tool_call",
                    "data": {
                        "id": "lenses-test-456",
                        "name": "apply_lenses",
                        "parameters": {
                            "input_string": "  Hello   World  ",
                            "lenses": ["trim", "squeeze_spaces"]
                        }
                    }
                }

                await websocket.send(json.dumps(lenses_message))

                # Receive response
                response_raw = await websocket.recv()
                response = json.loads(response_raw)

                # Verify response
                assert response["type"] == "tool_result"
                assert response["data"]["tool_call_id"] == "lenses-test-456"

                result = response["data"]["result"]
                assert result["success"] is True
                assert "result" in result
                assert isinstance(result["result"], str)
                assert "applied_lenses" in result

                print("✅ Apply lenses E2E test passed")

    @pytest.mark.asyncio
    async def test_validate_schema_e2e(self):
        """Test validate_schema tool through WebSocket"""
        async with mcp_server_lifecycle() as (server, ws_url):
            async with websockets.connect(ws_url) as websocket:
                # Send validate_schema tool call
                schema_message = {
                    "type": "tool_call",
                    "data": {
                        "id": "schema-test-789",
                        "name": "validate_schema",
                        "parameters": {
                            "json_object": {
                                "name": "John",
                                "age": 30
                            },
                            "json_schema": {
                                "type": "object",
                                "required": ["name"],
                                "properties": {
                                    "name": {"type": "string"},
                                    "age": {"type": "number"}
                                }
                            }
                        }
                    }
                }

                await websocket.send(json.dumps(schema_message))

                # Receive response
                response_raw = await websocket.recv()
                response = json.loads(response_raw)

                # Verify response
                assert response["type"] == "tool_result"
                assert response["data"]["tool_call_id"] == "schema-test-789"

                result = response["data"]["result"]
                assert result["success"] is True
                assert result["valid"] is True
                assert result["validated_data"]["name"] == "John"

                print("✅ Validate schema E2E test passed")

    @pytest.mark.asyncio
    async def test_error_handling_e2e(self):
        """Test error handling through WebSocket"""
        async with mcp_server_lifecycle() as (server, ws_url):
            async with websockets.connect(ws_url) as websocket:
                # Send tool call with invalid syntax
                error_message = {
                    "type": "tool_call",
                    "data": {
                        "id": "error-test",
                        "name": "execute",
                        "parameters": {
                            "facet_source": "@invalid syntax here"
                        }
                    }
                }

                await websocket.send(json.dumps(error_message))

                # Receive response
                response_raw = await websocket.recv()
                response = json.loads(response_raw)

                # Verify error response
                assert response["type"] == "tool_result"
                assert response["data"]["tool_call_id"] == "error-test"

                result = response["data"]["result"]
                assert result["success"] is False
                assert "error" in result

                print("✅ Error handling E2E test passed")

    @pytest.mark.asyncio
    async def test_unknown_tool_e2e(self):
        """Test unknown tool handling through WebSocket"""
        async with mcp_server_lifecycle() as (server, ws_url):
            async with websockets.connect(ws_url) as websocket:
                # Send unknown tool call
                unknown_message = {
                    "type": "tool_call",
                    "data": {
                        "id": "unknown-test",
                        "name": "unknown_tool_12345",
                        "parameters": {}
                    }
                }

                await websocket.send(json.dumps(unknown_message))

                # Receive response
                response_raw = await websocket.recv()
                response = json.loads(response_raw)

                # Verify error response
                assert response["type"] == "error"
                assert "Unknown tool" in response["data"]["error"]
                assert "available_tools" in response["data"]

                print("✅ Unknown tool E2E test passed")

    @pytest.mark.asyncio
    async def test_concurrent_connections(self):
        """Test multiple concurrent WebSocket connections"""
        async with mcp_server_lifecycle() as (server, ws_url):
            async def client_worker(client_id):
                """Worker function for each client"""
                try:
                    async with websockets.connect(ws_url) as websocket:
                        # Send a simple tool call
                        message = {
                            "type": "tool_call",
                            "data": {
                                "id": f"concurrent-{client_id}",
                                "name": "apply_lenses",
                                "parameters": {
                                    "input_string": f"test from client {client_id}",
                                    "lenses": ["trim"]
                                }
                            }
                        }

                        await websocket.send(json.dumps(message))

                        # Receive response
                        response_raw = await websocket.recv()
                        response = json.loads(response_raw)

                        return response["type"] == "tool_result"
                except Exception as e:
                    print(f"Client {client_id} error: {e}")
                    return False

            # Create multiple concurrent clients
            num_clients = 5
            tasks = [client_worker(i) for i in range(num_clients)]
            results = await asyncio.gather(*tasks)

            # Verify all clients succeeded
            successful_clients = sum(results)
            assert successful_clients == num_clients, f"Only {successful_clients}/{num_clients} clients succeeded"

            print(f"✅ Concurrent connections test passed ({num_clients} clients)")

    @pytest.mark.asyncio
    async def test_message_format_validation(self):
        """Test validation of message formats"""
        async with mcp_server_lifecycle() as (server, ws_url):
            async with websockets.connect(ws_url) as websocket:
                # Test invalid JSON
                await websocket.send("invalid json")

                # Should receive error response
                response_raw = await websocket.recv()
                response = json.loads(response_raw)

                assert response["type"] == "error"
                assert "Invalid JSON" in response["data"]["error"]

                print("✅ Message format validation test passed")

    @pytest.mark.asyncio
    async def test_server_reconnection(self):
        """Test server reconnection handling"""
        server, ws_url = None, None

        # Start server manually for more control
        server = FACETMCPServer()
        server_task = asyncio.create_task(server.start("localhost", 3002))

        await asyncio.sleep(0.1)  # Let server start
        ws_url = "ws://localhost:3002"

        try:
            # First connection
            async with websockets.connect(ws_url) as ws1:
                # Send a message
                message = {
                    "type": "list_tools",
                    "data": {}
                }
                await ws1.send(json.dumps(message))

                response_raw = await ws1.recv()
                response = json.loads(response_raw)
                assert response["type"] == "tools_list"

            # Second connection (reconnection test)
            async with websockets.connect(ws_url) as ws2:
                # Send another message
                await ws2.send(json.dumps(message))

                response_raw = await ws2.recv()
                response = json.loads(response_raw)
                assert response["type"] == "tools_list"

            print("✅ Server reconnection test passed")

        finally:
            # Cleanup
            await server.stop()
            server_task.cancel()
            try:
                await server_task
            except asyncio.CancelledError:
                pass

    @pytest.mark.asyncio
    async def test_large_payload_handling(self):
        """Test handling of large payloads"""
        async with mcp_server_lifecycle() as (server, ws_url):
            async with websockets.connect(ws_url) as websocket:
                # Create a large FACET document
                large_facet = "@system\n  role: \"Test\"\n\n@user\n  request: \""
                large_facet += "x" * 10000  # 10KB of content
                large_facet += "\"\n\n@output\n  response: \"large response\""

                # Send large payload
                message = {
                    "type": "tool_call",
                    "data": {
                        "id": "large-payload-test",
                        "name": "execute",
                        "parameters": {
                            "facet_source": large_facet
                        }
                    }
                }

                await websocket.send(json.dumps(message))

                # Receive response
                response_raw = await websocket.recv()
                response = json.loads(response_raw)

                # Verify response (should handle large payload)
                assert response["type"] == "tool_result"
                assert response["data"]["tool_call_id"] == "large-payload-test"

                print("✅ Large payload handling test passed")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
