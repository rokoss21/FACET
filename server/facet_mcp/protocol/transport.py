"""
MCP Transport Layer

Provides transport mechanisms for MCP communication:
- JSON-RPC over WebSockets
- HTTP/JSON endpoints
- gRPC support (future)

Handles connection management, message serialization, and error handling.
"""

import asyncio
import json
import logging
from typing import Callable, Optional
import websockets
from websockets.exceptions import ConnectionClosedError

from .messages import MCPMessage

logger = logging.getLogger(__name__)


class MCPTransport:
    """
    MCP Transport Layer

    Handles the low-level communication details for MCP protocol.
    Supports WebSocket connections for real-time communication.
    """

    def __init__(self):
        self.server: Optional[asyncio.AbstractServer] = None
        self.message_handler: Optional[Callable[[MCPMessage], MCPMessage]] = None
        self.connections = set()

    async def start_server(
        self,
        host: str = "localhost",
        port: int = 3000,
        message_handler: Optional[Callable[[MCPMessage], MCPMessage]] = None
    ):
        """
        Start MCP server on specified host and port.

        Args:
            host: Server host address
            port: Server port
            message_handler: Function to handle incoming MCP messages
        """
        self.message_handler = message_handler

        # Start WebSocket server
        self.server = await websockets.serve(
            self._handle_connection,
            host,
            port,
            ping_interval=30,  # Keep connections alive
            ping_timeout=10,
            close_timeout=5
        )

        logger.info(f"MCP server started on {host}:{port}")
        logger.info("Available endpoints:")
        logger.info(f"  WebSocket: ws://{host}:{port}")
        logger.info(f"  HTTP: http://{host}:{port}/health")

        # Keep server running
        await self.server.wait_closed()

    async def stop_server(self):
        """Stop the MCP server gracefully"""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            logger.info("MCP server stopped")

    async def _handle_connection(self, websocket):
        """
        Handle individual WebSocket connection.

        Manages the lifecycle of a single client connection,
        including message handling and connection cleanup.
        """
        connection_id = id(websocket)
        self.connections.add(websocket)

        try:
            logger.info(f"New MCP connection established: {connection_id}")

            async for message_raw in websocket:
                try:
                    # Parse incoming message
                    message_data = json.loads(message_raw)
                    message = MCPMessage.from_dict(message_data)

                    logger.debug(f"Received message: {message.type}")

                    # Handle message
                    if self.message_handler:
                        response = await self.message_handler(message)

                        # Send response
                        response_data = response.to_dict()
                        await websocket.send(json.dumps(response_data))
                        logger.debug(f"Sent response: {response.type}")
                    else:
                        # No handler - send error
                        error_response = MCPMessage(
                            type="error",
                            data={"error": "No message handler configured"}
                        )
                        await websocket.send(json.dumps(error_response.to_dict()))

                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON received: {e}")
                    error_response = MCPMessage(
                        type="error",
                        data={"error": "Invalid JSON format"}
                    )
                    await websocket.send(json.dumps(error_response.to_dict()))

                except Exception as e:
                    logger.error(f"Error handling message: {e}")
                    error_response = MCPMessage(
                        type="error",
                        data={"error": f"Internal server error: {str(e)}"}
                    )
                    await websocket.send(json.dumps(error_response.to_dict()))

        except ConnectionClosedError:
            logger.info(f"MCP connection closed: {connection_id}")
        except Exception as e:
            logger.error(f"Connection error: {e}")
        finally:
            # Cleanup connection
            self.connections.discard(websocket)
            logger.info(f"Connection cleanup completed: {connection_id}")


class MCPClient:
    """
    MCP Client for connecting to MCP servers.

    Allows AI agents and other tools to connect to and use MCP servers.
    """

    def __init__(self):
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None

    async def connect(self, uri: str):
        """
        Connect to MCP server.

        Args:
            uri: WebSocket URI (e.g., "ws://localhost:3000")
        """
        try:
            self.websocket = await websockets.connect(uri)
            logger.info(f"Connected to MCP server: {uri}")
        except Exception as e:
            logger.error(f"Failed to connect to MCP server: {e}")
            raise

    async def disconnect(self):
        """Disconnect from MCP server"""
        if self.websocket:
            await self.websocket.close()
            logger.info("Disconnected from MCP server")

    async def send_message(self, message: MCPMessage) -> MCPMessage:
        """
        Send message to MCP server and wait for response.

        Args:
            message: MCP message to send

        Returns:
            Response message from server
        """
        if not self.websocket:
            raise ConnectionError("Not connected to MCP server")

        try:
            # Send message
            message_data = message.to_dict()
            await self.websocket.send(json.dumps(message_data))

            # Wait for response
            response_raw = await self.websocket.recv()
            response_data = json.loads(response_raw)
            response = MCPMessage.from_dict(response_data)

            return response

        except Exception as e:
            logger.error(f"Error sending message: {e}")
            raise

    async def call_tool(
        self,
        tool_name: str,
        parameters: dict,
        timeout: float = 30.0
    ) -> dict:
        """
        Call a tool on the MCP server.

        Args:
            tool_name: Name of the tool to call
            parameters: Tool parameters
            timeout: Timeout in seconds

        Returns:
            Tool execution result
        """
        from .messages import create_tool_call_message

        message = create_tool_call_message(tool_name, parameters)
        response = await asyncio.wait_for(
            self.send_message(message),
            timeout=timeout
        )

        if response.type == "tool_result":
            result_data = response.data
            if result_data.get("success", False):
                return result_data["result"]
            else:
                raise Exception(f"Tool execution failed: {result_data.get('error', 'Unknown error')}")
        else:
            raise Exception(f"Unexpected response type: {response.type}")

    async def list_tools(self) -> list:
        """
        Get list of available tools from MCP server.

        Returns:
            List of available tools
        """
        message = MCPMessage(type="list_tools", data={})
        response = await self.send_message(message)

        if response.type == "tools_list":
            return response.data.get("tools", [])
        else:
            raise Exception(f"Unexpected response type: {response.type}")


# Health check endpoint for HTTP requests
async def health_check(request):
    """Simple health check endpoint"""
    return {
        "status": "healthy",
        "service": "FACET MCP Server",
        "version": "0.1.0"
    }
