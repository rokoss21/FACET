"""
MCP Message Formats and Types

Defines the message structures used in MCP protocol communication
between AI agents and the FACET MCP server.
"""

from typing import Any, Dict, Optional
from dataclasses import dataclass
from enum import Enum


class MessageType(Enum):
    """MCP message types"""
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    TOOLS_LIST = "tools_list"
    ERROR = "error"
    PING = "ping"
    PONG = "pong"


@dataclass
class MCPMessage:
    """
    Base MCP message structure

    All MCP communication happens through these messages.
    """
    type: str
    data: Dict[str, Any]
    id: Optional[str] = None
    timestamp: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary for JSON serialization"""
        result = {
            "type": self.type,
            "data": self.data
        }
        if self.id:
            result["id"] = self.id
        if self.timestamp:
            result["timestamp"] = self.timestamp
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MCPMessage':
        """Create message from dictionary"""
        return cls(
            type=data["type"],
            data=data["data"],
            id=data.get("id"),
            timestamp=data.get("timestamp")
        )


@dataclass
class ToolCall:
    """
    Tool call message from AI agent to MCP server

    Represents a request to execute a specific tool with parameters.
    """
    name: str
    parameters: Dict[str, Any]
    id: Optional[str] = None

    def to_message(self) -> MCPMessage:
        """Convert to MCP message"""
        return MCPMessage(
            type=MessageType.TOOL_CALL.value,
            data={
                "name": self.name,
                "parameters": self.parameters,
                "id": self.id
            },
            id=self.id
        )


@dataclass
class ToolResult:
    """
    Tool result message from MCP server to AI agent

    Contains the result of tool execution or error information.
    """
    tool_call_id: str
    result: Dict[str, Any]
    success: bool = True
    error: Optional[str] = None

    def to_message(self) -> MCPMessage:
        """Convert to MCP message"""
        data = {
            "tool_call_id": self.tool_call_id,
            "result": self.result,
            "success": self.success
        }
        if self.error:
            data["error"] = self.error

        return MCPMessage(
            type=MessageType.TOOL_RESULT.value,
            data=data,
            id=self.tool_call_id
        )


@dataclass
class ToolsList:
    """
    Tools list message from MCP server

    Provides AI agent with information about available tools.
    """
    tools: list

    def to_message(self) -> MCPMessage:
        """Convert to MCP message"""
        return MCPMessage(
            type=MessageType.TOOLS_LIST.value,
            data={"tools": self.tools}
        )


@dataclass
class MCPError:
    """
    Error message from MCP server

    Contains error information and potentially available alternatives.
    """
    error: str
    error_type: str = "general_error"
    available_tools: Optional[list] = None
    suggestions: Optional[list] = None

    def to_message(self) -> MCPMessage:
        """Convert to MCP message"""
        data = {
            "error": self.error,
            "error_type": self.error_type
        }
        if self.available_tools:
            data["available_tools"] = self.available_tools
        if self.suggestions:
            data["suggestions"] = self.suggestions

        return MCPMessage(
            type=MessageType.ERROR.value,
            data=data
        )


# Utility functions for creating common messages

def create_tool_call_message(
    tool_name: str,
    parameters: Dict[str, Any],
    call_id: Optional[str] = None
) -> MCPMessage:
    """Create a tool call message"""
    return ToolCall(
        name=tool_name,
        parameters=parameters,
        id=call_id
    ).to_message()


def create_tool_result_message(
    tool_call_id: str,
    result: Dict[str, Any],
    success: bool = True,
    error: Optional[str] = None
) -> MCPMessage:
    """Create a tool result message"""
    return ToolResult(
        tool_call_id=tool_call_id,
        result=result,
        success=success,
        error=error
    ).to_message()


def create_tools_list_message(tools: list) -> MCPMessage:
    """Create a tools list message"""
    return ToolsList(tools=tools).to_message()


def create_error_message(
    error: str,
    error_type: str = "general_error",
    available_tools: Optional[list] = None,
    suggestions: Optional[list] = None
) -> MCPMessage:
    """Create an error message"""
    return MCPError(
        error=error,
        error_type=error_type,
        available_tools=available_tools,
        suggestions=suggestions
    ).to_message()
