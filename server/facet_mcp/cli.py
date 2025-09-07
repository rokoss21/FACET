"""
CLI Interface for FACET MCP Server

Provides command-line interface to start, stop, and manage
the FACET MCP Server with various configuration options.
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

from .server import FACETMCPServer
from .config.settings import config


def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, config.logging.level),
        format=config.logging.format
    )

    if config.logging.enable_file_logging:
        # Ensure log directory exists
        log_dir = Path(config.logging.log_file).parent
        log_dir.mkdir(parents=True, exist_ok=True)

        # Add file handler
        file_handler = logging.FileHandler(config.logging.log_file)
        file_handler.setFormatter(logging.Formatter(config.logging.format))
        logging.getLogger().addHandler(file_handler)


def cmd_start(args):
    """Start the MCP server"""
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("🚀 Starting FACET MCP Server...")
    logger.info(f"📍 Host: {config.server.host}")
    logger.info(f"🔌 Port: {config.server.port}")
    logger.info(f"⚡ SIMD Enabled: {config.performance.enable_simd}")
    logger.info(f"🛠️  Enabled Tools: {', '.join(config.tools.enabled_tools)}")

    server = FACETMCPServer()

    try:
        asyncio.run(server.start(
            host=config.server.host,
            port=config.server.port
        ))
    except KeyboardInterrupt:
        logger.info("⏹️  Received shutdown signal")
    except Exception as e:
        logger.error(f"❌ Server error: {e}")
        sys.exit(1)
    finally:
        asyncio.run(server.stop())


def cmd_config(args):
    """Show current configuration"""
    import json

    config_dict = config.to_dict()

    if args.json:
        print(json.dumps(config_dict, indent=2))
    else:
        print("🎛️  FACET MCP Server Configuration")
        print("=" * 50)

        print(f"📍 Server: {config.server.host}:{config.server.port}")
        print(f"🔗 Max Connections: {config.server.max_connections}")
        print(f"⚡ SIMD: {'Enabled' if config.performance.enable_simd else 'Disabled'}")
        print(f"🛠️  Tools: {', '.join(config.tools.enabled_tools)}")
        print(f"🔒 Security: {'Enabled' if config.security.enable_rate_limiting else 'Disabled'}")
        print(f"📊 Logging: {config.logging.level}")

        if args.verbose:
            print("\n📋 Detailed Configuration:")
            print(json.dumps(config_dict, indent=2))


def cmd_tools(args):
    """List available tools"""
    from .tools.facets import FACETTools

    tools = FACETTools()
    tool_descriptions = tools.get_tool_descriptions()

    print("🛠️  Available FACET MCP Tools")
    print("=" * 50)

    for tool_name, description in tool_descriptions.items():
        print(f"\n🔧 {tool_name}")
        print(f"   {description['description']}")
        print(f"   📝 Returns: {description['returns']}")

        if args.verbose:
            print("   📋 Parameters:"            for param_name, param_schema in description['parameters']['properties'].items():
                required = param_name in description['parameters'].get('required', [])
                required_mark = " (required)" if required else ""
                param_type = param_schema.get('type', 'any')
                param_desc = param_schema.get('description', 'No description')
                print(f"     • {param_name} ({param_type}){required_mark}: {param_desc}")


def cmd_lenses(args):
    """List available FACET lenses"""
    from .tools.facets import FACETTools

    tools = FACETTools()
    available_lenses = tools.get_available_lenses()

    print("🔍 Available FACET Lenses")
    print("=" * 30)

    lens_descriptions = {
        "trim": "Remove leading/trailing whitespace",
        "dedent": "Remove common leading whitespace from all lines",
        "squeeze_spaces": "Replace multiple consecutive spaces with single space",
        "normalize_newlines": "Normalize different newline characters to \\n",
        "json_minify": "Minify JSON by removing unnecessary whitespace",
        "json_parse": "Parse JSON string to object",
        "strip_markdown": "Remove markdown formatting",
        "limit": "Limit text to specified number of characters (requires parameter)"
    }

    for lens in available_lenses:
        description = lens_descriptions.get(lens, "No description available")
        print("2")


def cmd_examples(args):
    """Show usage examples"""
    from .examples.usage_examples import MCPUsageExamples

    examples = MCPUsageExamples()

    if args.category == "execute" or args.category == "all":
        print("📄 Execute Tool Examples")
        print("=" * 30)
        execute_examples = examples.get_execute_examples()
        for name, example in execute_examples.items():
            print(f"\n🔧 {name}")
            print(f"   {example['description']}")
            if args.verbose:
                print(f"   📝 Variables: {list(example.get('variables', {}).keys())}")

    if args.category == "lenses" or args.category == "all":
        print("\n🔍 Apply Lenses Tool Examples")
        print("=" * 35)
        lenses_examples = examples.get_lenses_examples()
        for name, example in lenses_examples.items():
            print(f"\n🔧 {name}")
            print(f"   {example['description']}")
            if args.verbose:
                print(f"   📝 Lenses: {example['lenses']}")

    if args.category == "validate" or args.category == "all":
        print("\n✅ Validate Schema Tool Examples")
        print("=" * 38)
        validation_examples = examples.get_validation_examples()
        for name, example in validation_examples.items():
            print(f"\n🔧 {name}")
            print(f"   {example['description']}")
            if args.verbose:
                print("   📝 Schema properties:"                print(f"     {list(example['json_schema'].get('properties', {}).keys())}")

    if args.category == "workflow" or args.category == "all":
        print("\n🔄 Complete Workflow Examples")
        print("=" * 32)
        workflow_examples = examples.get_workflow_examples()
        for name, example in workflow_examples.items():
            print(f"\n🔧 {name}")
            print(f"   {example['description']}")
            if args.verbose:
                print(f"   📝 Steps: {len(example['steps'])}")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="FACET MCP Server - Agent-First AI Tooling",
        prog="facet-mcp"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Start command
    start_parser = subparsers.add_parser("start", help="Start the MCP server")
    start_parser.set_defaults(func=cmd_start)

    # Config command
    config_parser = subparsers.add_parser("config", help="Show server configuration")
    config_parser.add_argument("--json", action="store_true", help="Output as JSON")
    config_parser.add_argument("-v", "--verbose", action="store_true", help="Show detailed configuration")
    config_parser.set_defaults(func=cmd_config)

    # Tools command
    tools_parser = subparsers.add_parser("tools", help="List available tools")
    tools_parser.add_argument("-v", "--verbose", action="store_true", help="Show detailed tool information")
    tools_parser.set_defaults(func=cmd_tools)

    # Lenses command
    lenses_parser = subparsers.add_parser("lenses", help="List available FACET lenses")
    lenses_parser.set_defaults(func=cmd_lenses)

    # Examples command
    examples_parser = subparsers.add_parser("examples", help="Show usage examples")
    examples_parser.add_argument(
        "category",
        choices=["execute", "lenses", "validate", "workflow", "all"],
        default="all",
        nargs="?",
        help="Example category to show"
    )
    examples_parser.add_argument("-v", "--verbose", action="store_true", help="Show detailed examples")
    examples_parser.set_defaults(func=cmd_examples)

    # Parse arguments
    args = parser.parse_args()

    if not hasattr(args, 'func'):
        parser.print_help()
        return

    # Execute command
    args.func(args)


if __name__ == "__main__":
    main()
