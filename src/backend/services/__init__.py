"""Services package for the Multi-Agent Custom Automation Engine Solution Accelerator.

This package contains service layer components that manage external integrations,
business logic, and cross-cutting concerns.
"""

from .mcp_integration_service import (
    MCPIntegrationService,
    get_mcp_service,
    initialize_mcp_service,
    shutdown_mcp_service,
    execute_query,
    list_tables,
    describe_table,
    health_check,
    get_connection_info
)

__all__ = [
    "MCPIntegrationService",
    "get_mcp_service", 
    "initialize_mcp_service",
    "shutdown_mcp_service",
    "execute_query",
    "list_tables",
    "describe_table",
    "health_check",
    "get_connection_info"
]
