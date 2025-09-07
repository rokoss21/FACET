#!/usr/bin/env python3
"""
FACET MCP Client Example

Demonstrates how AI agents can connect to and use the FACET MCP Server.
This example shows basic usage of all three MCP tools.
"""

import asyncio
import json
import sys
import os

# Add server to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'server'))

from facet_mcp.protocol.transport import MCPClient


async def main():
    """Main example demonstrating MCP client usage"""

    # Initialize MCP client
    client = MCPClient()

    try:
        # Connect to MCP server
        print("🔌 Connecting to FACET MCP Server...")
        await client.connect("ws://localhost:3000")
        print("✅ Connected successfully!")

        # Get available tools
        print("\n🛠️  Available Tools:")
        tools = await client.list_tools()
        for tool in tools:
            print(f"  • {tool['name']}: {tool['description']}")

        # Example 1: Apply lenses for text cleaning
        print("\n🔧 Example 1: Text Cleaning with apply_lenses")
        dirty_text = "   Hello   World   \n\n  This is a   test   \n\n  With extra   spaces   "
        print(f"Input: {repr(dirty_text)}")

        result = await client.call_tool("apply_lenses", {
            "input_string": dirty_text,
            "lenses": ["squeeze_spaces", "trim", "dedent"]
        })

        if result["success"]:
            print(f"Output: {repr(result['result'])}")
            print("✅ Lenses applied successfully!")

        # Example 2: Execute FACET document
        print("\n📄 Example 2: FACET Document Execution")

        facet_doc = '''
@system(role="Assistant")
  name: "CodeHelper"
  style: "Helpful, concise"

@user
  request: "Help me debug this Python code"
    |> dedent |> trim

@output(format="json")
  require: "Response must be valid JSON"
  schema: {
    "type": "object",
    "required": ["advice", "confidence"],
    "properties": {
      "advice": {"type": "string"},
      "confidence": {"type": "number", "minimum": 0, "maximum": 1}
    }
  }
'''

        result = await client.call_tool("execute", {
            "facet_source": facet_doc,
            "variables": {
                "user_code": "print('Hello World')",
                "language": "python"
            }
        })

        if result["success"]:
            print("✅ FACET document executed successfully!")
            print(f"Execution time: {result.get('_meta', {}).get('execution_time_ms', 'N/A')}ms")
            # Print result (would contain the processed FACET output)
            print("Result structure:", json.dumps(result, indent=2)[:500] + "...")

        # Example 3: Schema validation
        print("\n✅ Example 3: Schema Validation")

        test_data = {
            "user_id": "12345",
            "email": "user@example.com",
            "name": "John Doe",
            "age": 25
        }

        schema = {
            "type": "object",
            "required": ["user_id", "email", "name"],
            "properties": {
                "user_id": {"type": "string"},
                "email": {"type": "string", "format": "email"},
                "name": {"type": "string", "minLength": 2},
                "age": {"type": "number", "minimum": 13, "maximum": 120}
            }
        }

        result = await client.call_tool("validate_schema", {
            "json_object": test_data,
            "json_schema": schema
        })

        if result["success"]:
            print(f"✅ Validation result: {'Valid' if result['valid'] else 'Invalid'}")
            if not result["valid"]:
                print("Errors:", result["errors"])

        # Example 4: Error handling
        print("\n🚨 Example 4: Error Handling")

        try:
            # Try to apply non-existent lens
            result = await client.call_tool("apply_lenses", {
                "input_string": "test",
                "lenses": ["non_existent_lens"]
            })
            print("Result:", result)
        except Exception as e:
            print(f"Expected error: {e}")

        print("\n🎉 All examples completed!")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await client.disconnect()


async def advanced_example():
    """Advanced example showing workflow orchestration"""
    client = MCPClient()

    try:
        await client.connect("ws://localhost:3000")

        print("🔄 Advanced Example: Complete AI Agent Workflow")

        # Step 1: Clean user input
        raw_input = "   User said:   'please help me format this JSON'   \n\n  {name: 'John'}   "
        print(f"Step 1 - Raw input: {repr(raw_input)}")

        cleaned = await client.call_tool("apply_lenses", {
            "input_string": raw_input,
            "lenses": ["trim", "squeeze_spaces", "normalize_newlines"]
        })

        print(f"Step 1 - Cleaned: {repr(cleaned['result'])}")

        # Step 2: Execute FACET document to process the data
        facet_workflow = '''
@workflow(name="JSONProcessing")
  description: "Process and validate JSON data"

@input
  user_request: "{{user_request}}"
  raw_data: "{{raw_data}}"

@processing
  steps: [
    "extract_json_from_text",
    "validate_json_structure",
    "format_json_output"
  ]

@output(format="json")
  require: "Valid JSON response"
  schema: {
    "type": "object",
    "required": ["processed_data", "status"],
    "properties": {
      "processed_data": {"type": "object"},
      "status": {"type": "string", "enum": ["success", "error"]}
    }
  }
'''

        result = await client.call_tool("execute", {
            "facet_source": facet_workflow,
            "variables": {
                "user_request": cleaned["result"],
                "raw_data": "{name: 'John'}"
            }
        })

        print("Step 2 - FACET execution completed")
        print(f"Status: {result.get('status', 'unknown')}")

        # Step 3: Validate the final result
        final_result = result.get("result", {})
        validation = await client.call_tool("validate_schema", {
            "json_object": final_result,
            "json_schema": {
                "type": "object",
                "required": ["processed_data", "status"],
                "properties": {
                    "processed_data": {"type": "object"},
                    "status": {"type": "string"}
                }
            }
        })

        print("Step 3 - Final validation completed")
        print(f"Valid: {validation['valid']}")

        print("\n🎉 Advanced workflow completed successfully!")

    except Exception as e:
        print(f"❌ Advanced example error: {e}")
    finally:
        await client.disconnect()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="FACET MCP Client Example")
    parser.add_argument("--advanced", action="store_true", help="Run advanced example")
    parser.add_argument("--host", default="localhost", help="MCP server host")
    parser.add_argument("--port", type=int, default=3000, help="MCP server port")

    args = parser.parse_args()

    if args.advanced:
        asyncio.run(advanced_example())
    else:
        asyncio.run(main())
