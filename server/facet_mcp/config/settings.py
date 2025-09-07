"""
MCP Server Configuration Settings

Centralized configuration management for FACET MCP Server.
Includes server settings, performance tuning, and tool configurations.
"""

import os
from typing import Dict, Any, List
from dataclasses import dataclass, field


@dataclass
class ServerConfig:
    """Server configuration settings"""
    host: str = "localhost"
    port: int = 3000
    max_connections: int = 100
    connection_timeout: int = 30
    ping_interval: int = 30
    ping_timeout: int = 10
    close_timeout: int = 5

    # Performance settings
    max_concurrent_requests: int = 50
    request_timeout: int = 60
    worker_threads: int = 4


@dataclass
class PerformanceConfig:
    """Performance optimization settings"""
    enable_simd: bool = True
    max_text_size_kb: int = 1024  # 1MB limit for SIMD optimization
    cache_schema_validators: bool = True
    cache_template_engines: bool = True

    # Memory management
    max_memory_mb: int = 512
    garbage_collection_threshold: int = 100


@dataclass
class ToolConfig:
    """Tool-specific configurations"""
    enabled_tools: List[str] = field(default_factory=lambda: [
        "execute", "apply_lenses", "validate_schema"
    ])

    # Tool-specific limits
    max_facet_size_kb: int = 512
    max_lens_chain_length: int = 10
    max_template_variables: int = 50

    # Security settings
    allowed_lenses: List[str] = field(default_factory=lambda: [
        "trim", "dedent", "squeeze_spaces", "normalize_newlines",
        "json_minify", "json_parse", "strip_markdown", "limit"
    ])


@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    enable_file_logging: bool = False
    log_file: str = "logs/facet_mcp.log"
    max_log_size_mb: int = 10
    backup_count: int = 5


@dataclass
class SecurityConfig:
    """Security settings"""
    enable_rate_limiting: bool = True
    max_requests_per_minute: int = 60
    enable_request_validation: bool = True
    allowed_origins: List[str] = field(default_factory=lambda: ["*"])

    # Resource limits
    max_request_size_kb: int = 1024
    max_response_size_kb: int = 2048


class MCPConfig:
    """
    Main configuration class for FACET MCP Server.

    Loads configuration from environment variables and provides
    default values for all settings.
    """

    def __init__(self):
        self.server = self._load_server_config()
        self.performance = self._load_performance_config()
        self.tools = self._load_tool_config()
        self.logging = self._load_logging_config()
        self.security = self._load_security_config()

    def _load_server_config(self) -> ServerConfig:
        """Load server configuration from environment"""
        return ServerConfig(
            host=os.getenv("MCP_HOST", "localhost"),
            port=int(os.getenv("MCP_PORT", "3000")),
            max_connections=int(os.getenv("MCP_MAX_CONNECTIONS", "100")),
            connection_timeout=int(os.getenv("MCP_CONNECTION_TIMEOUT", "30")),
            ping_interval=int(os.getenv("MCP_PING_INTERVAL", "30")),
            ping_timeout=int(os.getenv("MCP_PING_TIMEOUT", "10")),
            close_timeout=int(os.getenv("MCP_CLOSE_TIMEOUT", "5")),
            max_concurrent_requests=int(os.getenv("MCP_MAX_CONCURRENT_REQUESTS", "50")),
            request_timeout=int(os.getenv("MCP_REQUEST_TIMEOUT", "60")),
            worker_threads=int(os.getenv("MCP_WORKER_THREADS", "4"))
        )

    def _load_performance_config(self) -> PerformanceConfig:
        """Load performance configuration from environment"""
        return PerformanceConfig(
            enable_simd=os.getenv("MCP_ENABLE_SIMD", "true").lower() == "true",
            max_text_size_kb=int(os.getenv("MCP_MAX_TEXT_SIZE_KB", "1024")),
            cache_schema_validators=os.getenv("MCP_CACHE_SCHEMA_VALIDATORS", "true").lower() == "true",
            cache_template_engines=os.getenv("MCP_CACHE_TEMPLATE_ENGINES", "true").lower() == "true",
            max_memory_mb=int(os.getenv("MCP_MAX_MEMORY_MB", "512")),
            garbage_collection_threshold=int(os.getenv("MCP_GC_THRESHOLD", "100"))
        )

    def _load_tool_config(self) -> ToolConfig:
        """Load tool configuration from environment"""
        enabled_tools = os.getenv("MCP_ENABLED_TOOLS", "execute,apply_lenses,validate_schema")
        enabled_tools_list = [tool.strip() for tool in enabled_tools.split(",")]

        return ToolConfig(
            enabled_tools=enabled_tools_list,
            max_facet_size_kb=int(os.getenv("MCP_MAX_FACET_SIZE_KB", "512")),
            max_lens_chain_length=int(os.getenv("MCP_MAX_LENS_CHAIN_LENGTH", "10")),
            max_template_variables=int(os.getenv("MCP_MAX_TEMPLATE_VARIABLES", "50")),
            allowed_lenses=os.getenv("MCP_ALLOWED_LENSES", "trim,dedent,squeeze_spaces,normalize_newlines,json_minify,json_parse,strip_markdown,limit").split(",")
        )

    def _load_logging_config(self) -> LoggingConfig:
        """Load logging configuration from environment"""
        return LoggingConfig(
            level=os.getenv("MCP_LOG_LEVEL", "INFO"),
            format=os.getenv("MCP_LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
            enable_file_logging=os.getenv("MCP_ENABLE_FILE_LOGGING", "false").lower() == "true",
            log_file=os.getenv("MCP_LOG_FILE", "logs/facet_mcp.log"),
            max_log_size_mb=int(os.getenv("MCP_MAX_LOG_SIZE_MB", "10")),
            backup_count=int(os.getenv("MCP_LOG_BACKUP_COUNT", "5"))
        )

    def _load_security_config(self) -> SecurityConfig:
        """Load security configuration from environment"""
        allowed_origins = os.getenv("MCP_ALLOWED_ORIGINS", "*")
        if allowed_origins == "*":
            allowed_origins_list = ["*"]
        else:
            allowed_origins_list = [origin.strip() for origin in allowed_origins.split(",")]

        return SecurityConfig(
            enable_rate_limiting=os.getenv("MCP_ENABLE_RATE_LIMITING", "true").lower() == "true",
            max_requests_per_minute=int(os.getenv("MCP_MAX_REQUESTS_PER_MINUTE", "60")),
            enable_request_validation=os.getenv("MCP_ENABLE_REQUEST_VALIDATION", "true").lower() == "true",
            allowed_origins=allowed_origins_list,
            max_request_size_kb=int(os.getenv("MCP_MAX_REQUEST_SIZE_KB", "1024")),
            max_response_size_kb=int(os.getenv("MCP_MAX_RESPONSE_SIZE_KB", "2048"))
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "server": {
                "host": self.server.host,
                "port": self.server.port,
                "max_connections": self.server.max_connections,
                "connection_timeout": self.server.connection_timeout,
                "max_concurrent_requests": self.server.max_concurrent_requests,
                "request_timeout": self.server.request_timeout,
                "worker_threads": self.server.worker_threads
            },
            "performance": {
                "enable_simd": self.performance.enable_simd,
                "max_text_size_kb": self.performance.max_text_size_kb,
                "cache_schema_validators": self.performance.cache_schema_validators,
                "cache_template_engines": self.performance.cache_template_engines,
                "max_memory_mb": self.performance.max_memory_mb,
                "garbage_collection_threshold": self.performance.garbage_collection_threshold
            },
            "tools": {
                "enabled_tools": self.tools.enabled_tools,
                "max_facet_size_kb": self.tools.max_facet_size_kb,
                "max_lens_chain_length": self.tools.max_lens_chain_length,
                "max_template_variables": self.tools.max_template_variables,
                "allowed_lenses": self.tools.allowed_lenses
            },
            "logging": {
                "level": self.logging.level,
                "format": self.logging.format,
                "enable_file_logging": self.logging.enable_file_logging,
                "log_file": self.logging.log_file,
                "max_log_size_mb": self.logging.max_log_size_mb,
                "backup_count": self.logging.backup_count
            },
            "security": {
                "enable_rate_limiting": self.security.enable_rate_limiting,
                "max_requests_per_minute": self.security.max_requests_per_minute,
                "enable_request_validation": self.security.enable_request_validation,
                "allowed_origins": self.security.allowed_origins,
                "max_request_size_kb": self.security.max_request_size_kb,
                "max_response_size_kb": self.security.max_response_size_kb
            }
        }


# Global configuration instance
config = MCPConfig()
