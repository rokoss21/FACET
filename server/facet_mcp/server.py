"""
FACET MCP Server Implementation

Main server class that implements the MCP protocol and provides tools for AI agents.
Handles FACET document execution, text processing, and schema validation.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from .core.facets import FACETEngine
from .core.validator import SchemaValidator
from .protocol.messages import MCPMessage, ToolCall, ToolResult
from .protocol.transport import MCPTransport

logger = logging.getLogger(__name__)


@dataclass
class MCPTool:
    """Represents an MCP tool that can be called by AI agents"""
    name: str
    description: str
    parameters: Dict[str, Any]
    handler: callable


class FACETMCPServer:
    """
    Main MCP Server for FACET - Agent-First AI Tooling

    Provides three core tools:
    1. execute - Full FACET document execution
    2. apply_lenses - Atomic text transformations
    3. validate_schema - Data quality assurance
    """

    def __init__(self):
        self.transport = MCPTransport()
        self.facets_engine = FACETEngine()
        self.schema_validator = SchemaValidator()
        self.tools = self._initialize_tools()

    def _initialize_tools(self) -> Dict[str, MCPTool]:
        """Initialize all available MCP tools"""
        return {
            "execute": MCPTool(
                name="execute",
                description="Executes a complete FACET document with SIMD optimizations. Use for complex multi-step pipelines with input processing, transformations, and output contracts.",
                parameters={
                    "type": "object",
                    "properties": {
                        "facet_source": {
                            "type": "string",
                            "description": "Complete FACET document text to execute"
                        },
                        "variables": {
                            "type": "object",
                            "description": "Optional variables for template substitution",
                            "additionalProperties": True
                        }
                    },
                    "required": ["facet_source"]
                },
                handler=self._handle_execute
            ),

            "apply_lenses": MCPTool(
                name="apply_lenses",
                description="Applies one or more FACET lenses to input text. Use for atomic, reliable text transformations like trimming, dedenting, or squeezing spaces.",
                parameters={
                    "type": "object",
                    "properties": {
                        "input_string": {
                            "type": "string",
                            "description": "Text to process with lenses"
                        },
                        "lenses": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of lenses to apply (e.g., ['dedent', 'trim', 'limit(100)'])"
                        }
                    },
                    "required": ["input_string", "lenses"]
                },
                handler=self._handle_apply_lenses
            ),

            "validate_schema": MCPTool(
                name="validate_schema",
                description="Validates JSON data against a JSON Schema. Use to ensure data quality and format correctness before returning results to users.",
                parameters={
                    "type": "object",
                    "properties": {
                        "json_object": {
                            "type": "object",
                            "description": "JSON object to validate"
                        },
                        "json_schema": {
                            "type": "object",
                            "description": "JSON Schema to validate against"
                        }
                    },
                    "required": ["json_object", "json_schema"]
                },
                handler=self._handle_validate_schema
            )
        }

    async def _handle_execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle execute tool calls"""
        try:
            facet_source = params["facet_source"]
            variables = params.get("variables", {})

            # Execute FACET document with SIMD optimizations
            result = await self.facets_engine.execute_facet(
                facet_source=facet_source,
                variables=variables
            )

            return {
                "success": True,
                "result": result,
                "execution_time_ms": result.get("_meta", {}).get("execution_time_ms", 0)
            }

        except Exception as e:
            logger.error(f"Execute tool error: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }

    async def _handle_apply_lenses(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle apply_lenses tool calls"""
        try:
            input_string = params["input_string"]
            lenses = params["lenses"]

            # Apply lenses with SIMD optimizations where beneficial
            result = await self.facets_engine.apply_lenses_to_text(
                text=input_string,
                lenses=lenses
            )

            return {
                "success": True,
                "result": result,
                "applied_lenses": lenses
            }

        except Exception as e:
            logger.error(f"Apply lenses tool error: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }

    async def _handle_validate_schema(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle validate_schema tool calls"""
        try:
            json_object = params["json_object"]
            json_schema = params["json_schema"]

            # Validate against schema
            validation_result = await self.schema_validator.validate(
                data=json_object,
                schema=json_schema
            )

            return {
                "success": True,
                "valid": validation_result.is_valid,
                "errors": validation_result.errors if not validation_result.is_valid else None
            }

        except Exception as e:
            logger.error(f"Validate schema tool error: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }

    async def handle_message(self, message: MCPMessage) -> MCPMessage:
        """Main message handler for MCP protocol"""
        if message.type == "tool_call":
            tool_call = message.data
            tool_name = tool_call.get("name")

            if tool_name in self.tools:
                tool = self.tools[tool_name]
                result = await tool.handler(tool_call.get("parameters", {}))

                return MCPMessage(
                    type="tool_result",
                    data={
                        "tool_call_id": tool_call.get("id"),
                        "result": result
                    }
                )
            else:
                return MCPMessage(
                    type="error",
                    data={
                        "error": f"Unknown tool: {tool_name}",
                        "available_tools": list(self.tools.keys())
                    }
                )

        elif message.type == "list_tools":
            # Return available tools
            tools_info = []
            for tool in self.tools.values():
                tools_info.append({
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters
                })

            return MCPMessage(
                type="tools_list",
                data={"tools": tools_info}
            )

        else:
            return MCPMessage(
                type="error",
                data={"error": f"Unknown message type: {message.type}"}
            )

    async def start(self, host: str = "localhost", port: int = 3000):
        """Start the MCP server"""
        logger.info(f"Starting FACET MCP Server on {host}:{port}")

        await self.transport.start_server(
            host=host,
            port=port,
            message_handler=self.handle_message
        )

    async def stop(self):
        """Stop the MCP server"""
        logger.info("Stopping FACET MCP Server")
        await self.transport.stop_server()


async def main():
    """Main entry point for running the MCP server"""
    import argparse

    parser = argparse.ArgumentParser(description="FACET MCP Server")
    parser.add_argument("--host", default="localhost", help="Server host")
    parser.add_argument("--port", type=int, default=3000, help="Server port")
    parser.add_argument("--log-level", default="INFO", help="Logging level")

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(level=getattr(logging, args.log_level.upper()))

    # Create and start server
    server = FACETMCPServer()

    try:
        await server.start(args.host, args.port)
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    finally:
        await server.stop()


if __name__ == "__main__":
    asyncio.run(main())
