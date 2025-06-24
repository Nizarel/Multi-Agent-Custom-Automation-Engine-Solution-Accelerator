"""MCP (Model Context Protocol) integration package."""

from .client import (
    EnhancedMCPClient, 
    VSCodeMCPClient, 
    MCPConnectionPool,
    MCPTool,
    SalesDataAnalyzer,
    create_mcp_client, 
    create_smart_mcp_client,
    create_vscode_mcp_client
)
from .config import MCPConfig, mcp_config

# Legacy aliases for backward compatibility
MCPClient = EnhancedMCPClient
MCPClientConfig = MCPConfig

__all__ = [
    "EnhancedMCPClient",
    "VSCodeMCPClient", 
    "MCPConnectionPool",
    "MCPTool",
    "SalesDataAnalyzer",
    "MCPClient",  # Legacy alias
    "MCPClientConfig",  # Legacy alias
    "create_mcp_client",
    "create_smart_mcp_client", 
    "create_vscode_mcp_client",
    "MCPConfig",
    "mcp_config"
]
