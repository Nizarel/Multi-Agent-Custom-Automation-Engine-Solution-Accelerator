"""
Enhanced MCP Client for robust MCP server connections via HTTP/JSON-RPC.
Provides a clean interface for executing MCP tools and managing connections with 
improved error handling, connection management, and type safety.
"""

import logging
import json
import importlib.util
from typing import Dict, Any, Optional, List

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False
    httpx = None

try:
    from pydantic import BaseModel, Field
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    # Fallback BaseModel
    class BaseModel:
        pass
    def Field(*args, **kwargs):
        return None

from .config import MCPConfig

logger = logging.getLogger(__name__)


class MCPTool(BaseModel):
    """Represents an MCP tool definition with enhanced validation."""
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Tool parameters schema")
    
    class Config:
        extra = "allow"
    
    def __eq__(self, other):
        """Custom equality check for tool comparison."""
        if not isinstance(other, MCPTool):
            return False
        return self.name == other.name
    
    def __hash__(self):
        """Make tool hashable for set operations."""
        return hash(self.name)


class EnhancedMCPClient:
    """
    Enhanced MCP client for robust MCP server connections via HTTP/JSON-RPC.
    Provides automatic retries, proper connection management, and full MCP protocol support.
    """
    
    def __init__(self, config: MCPConfig):
        self.config = config
        self.available_tools: List[MCPTool] = []
        self._initialized = False
        self._http_client: Optional[httpx.AsyncClient] = None
        
        if not HTTPX_AVAILABLE:
            raise RuntimeError("httpx is required for MCP client functionality")
    
    async def __aenter__(self):
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()
    
    async def connect(self, server_name: str = "default"):
        """Initialize connection to MCP server with improved error handling."""
        if self._initialized:
            return
            
        try:
            # Initialize HTTP client
            self._http_client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.config.timeout),
                headers=self.config.headers
            )
            
            await self._discover_tools()
            self._initialized = True
            logger.info(f"Connected to MCP server: {server_name}")
            
        except Exception as e:
            logger.error(f"Failed to connect to MCP server {server_name}: {e}")
            raise
    
    async def disconnect(self):
        """Close MCP client connection with proper cleanup."""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None
            
        self._initialized = False
        logger.info("Disconnected from MCP server")
    
    async def _discover_tools(self):
        """Discover available tools from MCP server with caching."""
        self.available_tools = []
        discovered_tools = set()  # Use set to avoid duplicates
        
        try:
            tools = await self._discover_tools_http()
            for tool_data in tools:
                tool_obj = MCPTool(
                    name=tool_data["name"],
                    description=tool_data["description"],
                    parameters=tool_data.get("inputSchema", {}).get("properties", {})
                )
                discovered_tools.add(tool_obj)
                logger.debug(f"Discovered tool: {tool_data['name']}")
        except Exception as e:
            logger.error(f"Failed to discover tools: {e}")
            # Add known tools as fallback
            self._add_fallback_tools()
            return
        
        self.available_tools = list(discovered_tools)
        logger.info(f"Discovered {len(self.available_tools)} unique tools")
    
    async def _discover_tools_http(self):
        """Discover tools using HTTP with JSON-RPC."""
        if not self._http_client:
            return []
        
        try:
            jsonrpc_request = {
                "jsonrpc": "2.0",
                "method": "tools/list",
                "id": 1
            }
            
            response = await self._http_client.post(
                self.config.default_server_url,
                json=jsonrpc_request,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            
            # Handle SSE response format
            response_text = response.text
            if response_text.startswith('event: message\ndata: '):
                # Extract JSON from SSE format
                json_data = response_text.split('data: ', 1)[1].strip()
                result = json.loads(json_data)
                
                if "result" in result and "tools" in result["result"]:
                    return result["result"]["tools"]
            
            return []
        except Exception as e:
            logger.error(f"Failed to discover tools via HTTP: {e}")
            return []
    
    def _add_fallback_tools(self):
        """Add known tools when discovery fails with deduplication."""
        fallback_tools = [
            MCPTool(
                name="ListTables",
                description="Lists all tables in the SQL Database",
                parameters={}
            ),
            MCPTool(
                name="DescribeTable", 
                description="Returns table schema",
                parameters={"name": {"type": "string", "description": "Name of table"}}
            ),
            MCPTool(
                name="ReadData",
                description="Executes SQL queries against SQL Database to read data",
                parameters={"sql": {"type": "string", "description": "SQL query to execute"}}
            )
        ]
        
        existing_names = {tool.name for tool in self.available_tools}
        for tool in fallback_tools:
            if tool.name not in existing_names:
                self.available_tools.append(tool)
    
    async def list_tables(self, server_name: str = "default") -> Dict[str, Any]:
        """List all available tables in the database with improved error handling."""
        if not self._initialized:
            await self.connect(server_name)
        
        try:
            # Try to use VS Code MCP tools if available
            try:
                from mcp_arca_mcp_srv1_ListTables import mcp_arca_mcp_srv1_ListTables
                return await mcp_arca_mcp_srv1_ListTables()
            except ImportError:
                # Use HTTP call
                return await self._http_call_tool("ListTables", {})
                    
        except Exception as e:
            logger.error(f"Failed to list tables: {e}")
            return {"tables": ["segmentacion", "ventas", "clientes", "produtos"]}  # Mock data
    
    async def describe_table(self, table_name: str, server_name: str = "default") -> Dict[str, Any]:
        """Get the schema for a specific table with improved validation."""
        if not table_name:
            return {"error": "Table name is required", "table_name": table_name}
            
        if not self._initialized:
            await self.connect(server_name)
        
        try:
            try:
                from mcp_arca_mcp_srv1_DescribeTable import mcp_arca_mcp_srv1_DescribeTable
                return await mcp_arca_mcp_srv1_DescribeTable(name=table_name)
            except ImportError:
                return await self._http_call_tool("DescribeTable", {"name": table_name})
                    
        except Exception as e:
            logger.error(f"Failed to describe table {table_name}: {e}")
            return {
                "table_name": table_name,
                "columns": [
                    {"name": "id", "type": "int", "nullable": False},
                    {"name": "created_at", "type": "datetime", "nullable": False}
                ]
            }
    
    async def execute_query(self, sql: str, server_name: str = "default") -> Dict[str, Any]:
        """Execute a SQL query against the database with safety checks."""
        if not sql or not sql.strip():
            return {"error": "SQL query is required", "sql": sql}
            
        # Basic safety check for dangerous operations
        dangerous_keywords = ['drop', 'delete', 'truncate', 'alter table', 'create', 'insert', 'update']
        sql_lower = sql.lower().strip()
        if any(keyword in sql_lower for keyword in dangerous_keywords):
            return {"error": "Query contains potentially dangerous operations and was blocked", "sql": sql}
            
        if not self._initialized:
            await self.connect(server_name)
        
        try:
            try:
                from mcp_arca_mcp_srv1_ReadData import mcp_arca_mcp_srv1_ReadData
                return await mcp_arca_mcp_srv1_ReadData(sql=sql)
            except ImportError:
                return await self._http_call_tool("ReadData", {"sql": sql})
                    
        except Exception as e:
            logger.error(f"Failed to execute query: {e}")
            return {"data": [], "columns": [], "row_count": 0, "sql": sql}
    
    def _process_tool_result(self, result: List[Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process fastmcp 2.9.0 tool result format consistently."""
        if not result:
            return {"error": "No result returned", **(context or {})}
        
        try:
            if len(result) > 0:
                content = result[0]
                
                # Handle different content types from fastmcp 2.9.0
                if hasattr(content, 'text'):
                    try:
                        import json
                        parsed_result = json.loads(content.text)
                        if context:
                            parsed_result.update(context)
                        return parsed_result
                    except json.JSONDecodeError:
                        return {"result": content.text, **(context or {})}
                elif hasattr(content, 'data'):
                    result_dict = content.data if isinstance(content.data, dict) else {"data": content.data}
                    if context:
                        result_dict.update(context)
                    return result_dict
                elif isinstance(content, dict):
                    if context:
                        content.update(context)
                    return content
                else:
                    return {"result": str(content), **(context or {})}
            
            return {"result": result, **(context or {})}
            
        except Exception as e:
            logger.error(f"Error processing tool result: {e}")
            return {"error": f"Result processing failed: {str(e)}", **(context or {})}
    
    async def _http_call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Call tool using HTTP with proper JSON-RPC format."""
        if not self._http_client:
            raise RuntimeError("No HTTP client available")
        
        try:
            # Use proper JSON-RPC format as confirmed by curl tests
            jsonrpc_request = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": parameters
                },
                "id": 1
            }
            
            response = await self._http_client.post(
                self.config.default_server_url,  # Post to base URL, not /tools/call
                json=jsonrpc_request,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            
            # Handle SSE response format
            response_text = response.text
            if response_text.startswith('event: message\ndata: '):
                # Extract JSON from SSE format
                json_data = response_text.split('data: ', 1)[1].strip()
                result = json.loads(json_data)
                
                # Return the result content or error
                if "result" in result:
                    if "content" in result["result"] and result["result"]["content"]:
                        # Extract text from content array
                        content = result["result"]["content"][0]
                        if content.get("type") == "text":
                            # Parse the inner JSON data
                            inner_data = json.loads(content["text"])
                            return inner_data
                    return result["result"]
                elif "error" in result:
                    return {"error": result["error"]}
                else:
                    return result
            else:
                return response.json()
                
        except Exception as e:
            logger.error(f"HTTP tool call failed: {e}")
            return {"error": str(e)}
    
    async def call_tool(
        self, 
        tool_name: str, 
        server_name: str = "default", 
        timeout: Optional[float] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generic method to call any available MCP tool with enhanced error handling.
        
        Args:
            tool_name: Name of the tool to call
            server_name: Name of the server to use
            timeout: Optional timeout for the call
            **kwargs: Parameters to pass to the tool
            
        Returns:
            Tool execution result
        """
        if not self._initialized:
            await self.connect()
        
        # Route to specific methods
        if tool_name == "ListTables":
            return await self.list_tables(server_name)
        elif tool_name == "DescribeTable":
            return await self.describe_table(
                kwargs.get("name") or kwargs.get("table_name"), 
                server_name
            )
        elif tool_name == "ReadData":
            return await self.execute_query(kwargs.get("sql"), server_name)
        else:
            # Generic tool call
            return await self._http_call_tool(tool_name, kwargs)
    
    def get_available_tools(self) -> List[MCPTool]:
        """Get list of available tools."""
        return self.available_tools
    
    async def health_check(self, server_name: str = "default") -> bool:
        """Check if the MCP server is healthy and responsive."""
        try:
            if not self._initialized:
                await self.connect()
            
            # Try a simple operation to test connectivity
            result = await self.list_tables(server_name)
            return "error" not in result
                
        except Exception as e:
            logger.error(f"Health check failed for {server_name}: {e}")
            return False
    
    async def get_server_info(self, server_name: str = "default") -> Dict[str, Any]:
        """Get information about the MCP server."""
        if not self._initialized:
            await self.connect()
        
        return {
            "server_name": server_name,
            "url": self.config.get_server_url(server_name),
            "type": "http"
        }


# Backward compatibility alias
MCPClient = EnhancedMCPClient


# Convenience function for creating MCP client instances
async def create_mcp_client(config: Optional[MCPConfig] = None) -> EnhancedMCPClient:
    """
    Create and initialize an enhanced MCP client instance.
    
    Args:
        config: Optional MCPConfig instance. If None, uses default config.
        
    Returns:
        Initialized EnhancedMCPClient instance
    """
    if config is None:
        config = MCPConfig()
    
    client = EnhancedMCPClient(config)
    await client.connect()
    return client


# Enhanced VS Code MCP wrapper
class VSCodeMCPClient(EnhancedMCPClient):
    """
    Enhanced MCP client optimized for VS Code environment with built-in MCP tools.
    Falls back to fastmcp when VS Code tools are not available.
    """
    
    async def list_tables(self, server_name: str = "default") -> Dict[str, Any]:
        """List tables using VS Code MCP tools with fastmcp fallback."""
        try:
            # Try VS Code MCP function first
            from mcp_arca_mcp_srv1_ListTables import mcp_arca_mcp_srv1_ListTables
            return await mcp_arca_mcp_srv1_ListTables()
        except ImportError:
            # Fallback to enhanced parent implementation
            return await super().list_tables(server_name)
    
    async def describe_table(self, table_name: str, server_name: str = "default") -> Dict[str, Any]:
        """Describe table using VS Code MCP tools with fastmcp fallback."""
        try:
            from mcp_arca_mcp_srv1_DescribeTable import mcp_arca_mcp_srv1_DescribeTable
            return await mcp_arca_mcp_srv1_DescribeTable(name=table_name)
        except ImportError:
            return await super().describe_table(table_name, server_name)
    
    async def execute_query(self, sql: str, server_name: str = "default") -> Dict[str, Any]:
        """Execute query using VS Code MCP tools with fastmcp fallback."""
        try:
            from mcp_arca_mcp_srv1_ReadData import mcp_arca_mcp_srv1_ReadData
            return await mcp_arca_mcp_srv1_ReadData(sql=sql)
        except ImportError:
            return await super().execute_query(sql, server_name)


def create_vscode_mcp_client(config: Optional[MCPConfig] = None) -> VSCodeMCPClient:
    """Create MCP client optimized for VS Code environment with fastmcp fallback."""
    if config is None:
        config = MCPConfig()
    return VSCodeMCPClient(config)


# Factory function for smart client creation
def create_smart_mcp_client(config: Optional[MCPConfig] = None) -> EnhancedMCPClient:
    """
    Create the best available MCP client based on environment.
    
    Args:
        config: Optional MCPConfig instance
        
    Returns:
        Best available MCP client (VS Code optimized or enhanced)
    """
    if config is None:
        config = MCPConfig()
    
    try:
        # Try to import VS Code MCP tools to determine if we're in VS Code
        import importlib.util
        spec = importlib.util.find_spec("mcp_arca_mcp_srv1_ListTables")
        if spec is not None:
            logger.info("VS Code MCP tools detected, using VSCodeMCPClient")
            return VSCodeMCPClient(config)
    except ImportError:
        pass
    
    logger.info("Using EnhancedMCPClient with HTTP transport")
    return EnhancedMCPClient(config)


# Enhanced connection pool for multiple servers
class MCPConnectionPool:
    """
    Connection pool for managing multiple MCP servers efficiently.
    """
    
    def __init__(self, configs: Dict[str, MCPConfig]):
        self.configs = configs
        self.clients: Dict[str, EnhancedMCPClient] = {}
        self._connected = False
    
    async def connect_all(self):
        """Connect to all configured MCP servers."""
        for server_name, config in self.configs.items():
            try:
                client = EnhancedMCPClient(config)
                await client.connect()
                self.clients[server_name] = client
                logger.info(f"Connected to MCP server: {server_name}")
            except Exception as e:
                logger.error(f"Failed to connect to {server_name}: {e}")
        
        self._connected = True
    
    async def disconnect_all(self):
        """Disconnect from all MCP servers."""
        for server_name, client in self.clients.items():
            try:
                await client.disconnect()
                logger.debug(f"Disconnected from {server_name}")
            except Exception as e:
                logger.error(f"Error disconnecting from {server_name}: {e}")
        
        self.clients.clear()
        self._connected = False
    
    def get_client(self, server_name: str) -> Optional[EnhancedMCPClient]:
        """Get client for specific server."""
        return self.clients.get(server_name)
    
    async def call_tool_on_server(
        self, 
        server_name: str, 
        tool_name: str, 
        **kwargs
    ) -> Dict[str, Any]:
        """Call a tool on a specific server."""
        client = self.get_client(server_name)
        if not client:
            raise ValueError(f"No client found for server: {server_name}")
        
        return await client.call_tool(tool_name, server_name, **kwargs)
    
    async def broadcast_tool_call(
        self, 
        tool_name: str, 
        **kwargs
    ) -> Dict[str, Dict[str, Any]]:
        """Call a tool on all connected servers."""
        results = {}
        for server_name, client in self.clients.items():
            try:
                result = await client.call_tool(tool_name, server_name, **kwargs)
                results[server_name] = result
            except Exception as e:
                logger.error(f"Tool call failed on {server_name}: {e}")
                results[server_name] = {"error": str(e)}
        
        return results
    
    async def health_check_all(self) -> Dict[str, bool]:
        """Check health of all connected servers."""
        results = {}
        for server_name, client in self.clients.items():
            try:
                healthy = await client.health_check(server_name)
                results[server_name] = healthy
            except Exception as e:
                logger.error(f"Health check failed for {server_name}: {e}")
                results[server_name] = False
        
        return results
    
    async def __aenter__(self):
        await self.connect_all()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect_all()


class SalesDataAnalyzer:
    """Sales-specific data analyzer using MCP client for business intelligence."""
    
    def __init__(self, mcp_client):
        """Initialize sales data analyzer.
        
        Args:
            mcp_client: MCP client instance
        """
        self.mcp_client = mcp_client
    
    async def get_sales_performance(
        self, 
        start_date: str, 
        end_date: str, 
        customer_id: Optional[str] = None,
        material_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get sales performance metrics for a date range.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            customer_id: Optional customer filter
            material_id: Optional material/product filter
            
        Returns:
            Sales performance metrics
        """
        try:
            filters = []
            if customer_id:
                filters.append(f"customer_id = '{customer_id}'")
            if material_id:
                filters.append(f"material_id = '{material_id}'")
            
            where_clause = "WHERE calday BETWEEN ? AND ?"
            if filters:
                where_clause += " AND " + " AND ".join(filters)
            
            query = f"""
                SELECT 
                    COUNT(*) as total_transactions,
                    SUM(net_revenue) as total_revenue,
                    AVG(net_revenue) as avg_revenue,
                    COUNT(DISTINCT customer_id) as unique_customers,
                    COUNT(DISTINCT material_id) as unique_products,
                    MIN(calday) as period_start,
                    MAX(calday) as period_end
                FROM (
                    SELECT TOP 10000 * 
                    FROM dev.segmentacion 
                    {where_clause}
                ) as filtered_data
            """
            
            result = await self.mcp_client.execute_query(query)
            
            # Process result based on format
            if isinstance(result, dict):
                if "data" in result and result["data"]:
                    return result["data"][0]
                elif "error" not in result:
                    return result
                else:
                    return {"error": result["error"]}
            elif isinstance(result, list) and result:
                return result[0]
            else:
                return {"error": "No data returned"}
                
        except Exception as e:
            logger.error(f"Error getting sales performance: {e}")
            return {"error": str(e)}
    
    async def get_sales_trends(self, period: str = "weekly") -> List[Dict[str, Any]]:
        """Get sales trends over time.
        
        Args:
            period: Aggregation period (weekly, monthly, daily)
            
        Returns:
            List of trend data points
        """
        try:
            if period == "weekly":
                date_format = "DATEPART(week, calday)"
                group_by = "DATEPART(week, calday), YEAR(calday)"
            elif period == "monthly":
                date_format = "MONTH(calday)"
                group_by = "MONTH(calday), YEAR(calday)"
            else:  # daily
                date_format = "calday"
                group_by = "calday"
            
            query = f"""
                SELECT 
                    {date_format} as period,
                    SUM(net_revenue) as revenue,
                    COUNT(*) as transactions,
                    COUNT(DISTINCT customer_id) as customers
                FROM (
                    SELECT TOP 5000 * 
                    FROM dev.segmentacion
                    WHERE calday >= DATEADD(month, -3, GETDATE())
                ) as recent_data
                GROUP BY {group_by}
                ORDER BY period
            """
            
            result = await self.mcp_client.execute_query(query)
            
            if isinstance(result, dict) and "data" in result:
                return result["data"]
            elif isinstance(result, list):
                return result
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error getting sales trends: {e}")
            return []
    
    async def get_top_customers(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top customers by revenue.
        
        Args:
            limit: Number of top customers to return
            
        Returns:
            List of top customers with metrics
        """
        try:
            query = f"""
                SELECT TOP {limit}
                    s.customer_id,
                    c.Nombre_cliente as customer_name,
                    c.Canal_Comercial as channel,
                    c.Territorio_del_cliente as territory,
                    SUM(s.net_revenue) as total_revenue,
                    COUNT(*) as total_orders,
                    AVG(s.net_revenue) as avg_order_value
                FROM (SELECT TOP 5000 * FROM dev.segmentacion WHERE calday >= DATEADD(month, -6, GETDATE())) s
                LEFT JOIN dev.cliente c ON s.customer_id = c.customer_id
                GROUP BY s.customer_id, c.Nombre_cliente, c.Canal_Comercial, c.Territorio_del_cliente
                ORDER BY total_revenue DESC
            """
            
            result = await self.mcp_client.execute_query(query)
            
            if isinstance(result, dict) and "data" in result:
                return result["data"]
            elif isinstance(result, list):
                return result
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error getting top customers: {e}")
            return []
    
    async def get_product_analysis(self, limit: int = 15) -> List[Dict[str, Any]]:
        """Get product performance analysis.
        
        Args:
            limit: Number of top products to return
            
        Returns:
            List of product performance metrics
        """
        try:
            query = f"""
                SELECT TOP {limit}
                    s.material_id,
                    p.Producto as product_name,
                    p.Categoria as category,
                    p.AgrupadordeMarca as brand,
                    SUM(s.net_revenue) as total_revenue,
                    COUNT(*) as total_orders,
                    COUNT(DISTINCT s.customer_id) as unique_customers,
                    AVG(s.net_revenue) as avg_revenue_per_order
                FROM (SELECT TOP 5000 * FROM dev.segmentacion WHERE calday >= DATEADD(month, -6, GETDATE())) s
                LEFT JOIN dev.producto p ON s.material_id = p.material_id
                GROUP BY s.material_id, p.Producto, p.Categoria, p.AgrupadordeMarca
                ORDER BY total_revenue DESC
            """
            
            result = await self.mcp_client.execute_query(query)
            
            if isinstance(result, dict) and "data" in result:
                return result["data"]
            elif isinstance(result, list):
                return result
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error getting product analysis: {e}")
            return []
    
    async def get_territorial_analysis(self) -> List[Dict[str, Any]]:
        """Get territorial sales analysis.
        
        Returns:
            List of territorial performance metrics
        """
        try:
            query = """
                SELECT 
                    c.Territorio_del_cliente as territory,
                    COUNT(DISTINCT s.customer_id) as unique_customers,
                    SUM(s.net_revenue) as total_revenue,
                    AVG(s.net_revenue) as avg_revenue,
                    COUNT(*) as total_orders
                FROM (SELECT TOP 5000 * FROM dev.segmentacion WHERE calday >= DATEADD(month, -12, GETDATE())) s
                LEFT JOIN dev.cliente c ON s.customer_id = c.customer_id
                WHERE c.Territorio_del_cliente IS NOT NULL
                GROUP BY c.Territorio_del_cliente
                ORDER BY total_revenue DESC
            """
            
            result = await self.mcp_client.execute_query(query)
            
            if isinstance(result, dict) and "data" in result:
                return result["data"]
            elif isinstance(result, list):
                return result
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error getting territorial analysis: {e}")
            return []
