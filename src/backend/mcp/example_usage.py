"""
Example usage of the enhanced MCP client with fastmcp integration.

This example demonstrates the key features and improvements of the new MCP client.
"""

import asyncio
import logging
from typing import Dict, Any

from .client import (
    EnhancedMCPClient, 
    VSCodeMCPClient, 
    MCPConnectionPool,
    create_smart_mcp_client, 
    create_mcp_client
)
from .config import MCPConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def basic_usage_example():
    """Basic usage example with the enhanced client."""
    print("\n=== Basic Usage Example ===")
    
    # Create configuration
    config = MCPConfig()
    
    # Create client using smart factory
    client = create_smart_mcp_client(config)
    
    async with client:
        # Check server health
        healthy = await client.health_check()
        print(f"Server healthy: {healthy}")
        
        # Get server information
        server_info = await client.get_server_info()
        print(f"Server info: {server_info}")
        
        # List available tools
        tools = client.get_available_tools()
        print(f"Available tools: {[tool.name for tool in tools]}")
        
        # List tables
        tables_result = await client.list_tables()
        print(f"Tables: {tables_result}")
        
        # Describe a table
        if "tables" in tables_result and tables_result["tables"]:
            table_name = tables_result["tables"][0]
            schema = await client.describe_table(table_name)
            print(f"Schema for {table_name}: {schema}")
        
        # Execute a simple query
        query_result = await client.execute_query("SELECT 1 as test")
        print(f"Query result: {query_result}")


async def multi_server_example():
    """Example using multiple MCP servers."""
    print("\n=== Multi-Server Example ===")
    
    # Create configurations for multiple servers
    configs = {
        "sales": MCPConfig.from_dict({
            "server_url": "https://mcp-sales-server.example.com/mcp",
            "auth_token": "sales_token_123"
        }),
        "analytics": MCPConfig.from_dict({
            "server_url": "https://mcp-analytics-server.example.com/mcp", 
            "auth_token": "analytics_token_456"
        })
    }
    
    # Create connection pool
    pool = MCPConnectionPool(configs)
    
    async with pool:
        # Check health of all servers
        health_status = await pool.health_check_all()
        print(f"Health status: {health_status}")
        
        # Call tool on specific server
        try:
            sales_tables = await pool.call_tool_on_server("sales", "ListTables")
            print(f"Sales tables: {sales_tables}")
        except Exception as e:
            print(f"Sales server not available: {e}")
        
        # Broadcast tool call to all servers
        all_tables = await pool.broadcast_tool_call("ListTables")
        print(f"All server tables: {all_tables}")


async def error_handling_example():
    """Example demonstrating error handling."""
    print("\n=== Error Handling Example ===")
    
    # Configure with invalid server for testing
    config = MCPConfig.from_dict({
        "server_url": "https://invalid-server.example.com/mcp",
        "timeout": 5
    })
    
    client = EnhancedMCPClient(config)
    
    try:
        async with client:
            # This will likely fail, but client handles it gracefully
            result = await client.list_tables()
            print(f"Unexpected success: {result}")
    except Exception as e:
        print(f"Expected error handled: {e}")
    
    # Test health check
    healthy = await client.health_check()
    print(f"Health check after error: {healthy}")


async def vscode_integration_example():
    """Example of VS Code integration."""
    print("\n=== VS Code Integration Example ===")
    
    config = MCPConfig()
    
    # Create VS Code optimized client
    vscode_client = VSCodeMCPClient(config)
    
    async with vscode_client:
        # This will use VS Code MCP tools if available, fallback to fastmcp
        tables = await vscode_client.list_tables()
        print(f"Tables via VS Code client: {tables}")
        
        # Check which implementation is being used
        tools = vscode_client.get_available_tools()
        print(f"Available tools: {len(tools)} tools discovered")


async def advanced_features_example():
    """Example of advanced features."""
    print("\n=== Advanced Features Example ===")
    
    config = MCPConfig()
    client = EnhancedMCPClient(config)
    
    async with client:
        # Call tool with timeout
        try:
            result = await client.call_tool(
                "ListTables", 
                timeout=10.0
            )
            print(f"Tool call with timeout: {result}")
        except Exception as e:
            print(f"Tool call timed out: {e}")
        
        # Generic tool calling
        try:
            result = await client.call_tool(
                "ReadData",
                sql="SELECT COUNT(*) FROM information_schema.tables"
            )
            print(f"Generic tool call result: {result}")
        except Exception as e:
            print(f"Generic tool call error: {e}")


async def configuration_example():
    """Example of advanced configuration."""
    print("\n=== Configuration Example ===")
    
    # Create configuration from environment variables
    env_config = MCPConfig()
    print(f"Default server: {env_config.default_server_url}")
    print(f"Timeout: {env_config.timeout}")
    print(f"Auth type: {env_config.auth_type}")
    
    # Create configuration from dictionary
    custom_config = MCPConfig.from_dict({
        "server_url": "https://custom-server.example.com/mcp",
        "timeout": 60,
        "auth_token": "custom_token",
        "headers": {
            "X-Custom-Header": "CustomValue"
        }
    })
    
    print(f"Custom server: {custom_config.default_server_url}")
    print(f"Custom headers: {custom_config.headers}")
    
    # Validate configuration
    is_valid = custom_config.validate()
    print(f"Configuration valid: {is_valid}")
    
    # Get fastmcp configuration (if available)
    fastmcp_config = custom_config.to_fastmcp_config()
    if fastmcp_config:
        print("FastMCP configuration created successfully")
    else:
        print("FastMCP not available")


async def main():
    """Run all examples."""
    print("Enhanced MCP Client Examples")
    print("=" * 50)
    
    # Run examples
    await basic_usage_example()
    await multi_server_example()
    await error_handling_example()
    await vscode_integration_example()
    await advanced_features_example()
    await configuration_example()
    
    print("\n" + "=" * 50)
    print("Examples completed!")


if __name__ == "__main__":
    asyncio.run(main())
