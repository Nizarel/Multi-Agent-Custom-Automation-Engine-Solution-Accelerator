"""MCP Client for Sales Analysis Agent integration."""

import asyncio
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

import httpx
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class MCPClientConfig(BaseModel):
    """Configuration for MCP client."""
    
    server_url: str
    timeout: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0


class MCPClient:
    """Client for communicating with MCP servers."""
    
    def __init__(self, config: MCPClientConfig):
        """Initialize MCP client.
        
        Args:
            config: Configuration for the MCP client
        """
        self.config = config
        self.client = httpx.AsyncClient(timeout=config.timeout)
        
    async def __aenter__(self):
        """Async context manager entry."""
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.client.aclose()
    
    async def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on the MCP server.
        
        Args:
            tool_name: Name of the tool to call
            parameters: Parameters to pass to the tool
            
        Returns:
            Tool execution result
        """
        for attempt in range(self.config.retry_attempts):
            try:
                logger.info(f"Calling MCP tool: {tool_name} (attempt {attempt + 1})")
                
                # Format the request according to MCP protocol
                request_data = {
                    "method": "tools/call",
                    "params": {
                        "name": tool_name,
                        "arguments": parameters
                    }
                }
                
                response = await self.client.post(
                    f"{self.config.server_url}/call",
                    json=request_data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"MCP tool {tool_name} executed successfully")
                    return result
                else:
                    logger.warning(f"MCP tool call failed with status {response.status_code}: {response.text}")
                    
            except Exception as e:
                logger.error(f"Error calling MCP tool {tool_name} (attempt {attempt + 1}): {e}")
                
                if attempt < self.config.retry_attempts - 1:
                    await asyncio.sleep(self.config.retry_delay * (attempt + 1))
                else:
                    raise
        
        raise Exception(f"Failed to call MCP tool {tool_name} after {self.config.retry_attempts} attempts")
    
    async def list_tables(self) -> List[str]:
        """List available tables in the database.
        
        Returns:
            List of table names
        """
        try:
            result = await self.call_tool("ListTables", {})
            if result.get("success"):
                return result.get("data", [])
            else:
                logger.error(f"Failed to list tables: {result.get('error', 'Unknown error')}")
                return []
        except Exception as e:
            logger.error(f"Error listing tables: {e}")
            return []
    
    async def describe_table(self, table_name: str) -> Optional[Dict[str, Any]]:
        """Describe a table structure.
        
        Args:
            table_name: Name of the table to describe
            
        Returns:
            Table description or None if error
        """
        try:
            result = await self.call_tool("DescribeTable", {"name": table_name})
            if result.get("success"):
                return result.get("data")
            else:
                logger.error(f"Failed to describe table {table_name}: {result.get('error', 'Unknown error')}")
                return None
        except Exception as e:
            logger.error(f"Error describing table {table_name}: {e}")
            return None
    
    async def execute_query(self, sql: str) -> Optional[List[Dict[str, Any]]]:
        """Execute a SQL query.
        
        Args:
            sql: SQL query to execute
            
        Returns:
            Query results or None if error
        """
        try:
            logger.info(f"Executing SQL query: {sql}")
            result = await self.call_tool("ReadData", {"sql": sql})
            
            if result.get("success"):
                data = result.get("data", [])
                logger.info(f"Query executed successfully, returned {len(data)} rows")
                return data
            else:
                logger.error(f"Query failed: {result.get('error', 'Unknown error')}")
                return None
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            return None


class SalesDataAnalyzer:
    """Sales data analyzer using MCP client."""
    
    def __init__(self, mcp_client: MCPClient):
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
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            customer_id: Optional customer filter
            material_id: Optional product filter
            
        Returns:
            Sales performance analysis
        """
        try:
            # Build the SQL query
            where_conditions = [f"calday BETWEEN '{start_date}' AND '{end_date}'"]
            
            if customer_id:
                where_conditions.append(f"customer_id = '{customer_id}'")
            if material_id:
                where_conditions.append(f"material_id = '{material_id}'")
            
            where_clause = " AND ".join(where_conditions)
            
            sql = f"""
            SELECT 
                COUNT(DISTINCT customer_id) as unique_customers,
                COUNT(DISTINCT material_id) as unique_products,
                SUM(VentasCajasUnidad) as total_unit_sales,
                SUM(IngresoNetoSImpuestos) as total_net_revenue,
                SUM(net_revenue) as total_revenue,
                SUM(bottles_sold_m) as total_bottles_sold,
                AVG(VentasCajasUnidad) as avg_unit_sales,
                AVG(IngresoNetoSImpuestos) as avg_net_revenue,
                MIN(calday) as first_sale_date,
                MAX(calday) as last_sale_date
            FROM dev.segmentacion
            WHERE {where_clause}
            """
            
            results = await self.mcp_client.execute_query(sql)
            
            if results and len(results) > 0:
                data = results[0]
                
                # Calculate additional metrics
                days_in_period = (datetime.strptime(end_date, "%Y-%m-%d") - 
                                datetime.strptime(start_date, "%Y-%m-%d")).days + 1
                
                analysis = {
                    "period": f"{start_date} to {end_date}",
                    "days_analyzed": days_in_period,
                    "metrics": {
                        "unique_customers": int(data.get("unique_customers", 0)),
                        "unique_products": int(data.get("unique_products", 0)),
                        "total_unit_sales": float(data.get("total_unit_sales", 0)),
                        "total_net_revenue": float(data.get("total_net_revenue", 0)),
                        "total_revenue": float(data.get("total_revenue", 0)),
                        "total_bottles_sold": float(data.get("total_bottles_sold", 0)),
                        "avg_unit_sales_per_transaction": float(data.get("avg_unit_sales", 0)),
                        "avg_revenue_per_transaction": float(data.get("avg_net_revenue", 0)),
                        "daily_avg_revenue": float(data.get("total_revenue", 0)) / days_in_period if days_in_period > 0 else 0
                    },
                    "date_range": {
                        "first_sale": data.get("first_sale_date"),
                        "last_sale": data.get("last_sale_date")
                    }
                }
                
                return analysis
            else:
                return {"error": "No data found for the specified period"}
                
        except Exception as e:
            logger.error(f"Error analyzing sales performance: {e}")
            return {"error": str(e)}
    
    async def get_top_customers(self, limit: int = 10, period_months: int = 3) -> List[Dict[str, Any]]:
        """Get top customers by revenue.
        
        Args:
            limit: Number of top customers to return
            period_months: Number of months to analyze
            
        Returns:
            List of top customers with metrics
        """
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period_months * 30)
            
            sql = f"""
            SELECT TOP {limit}
                s.customer_id,
                c.Nombre_cliente,
                c.Canal_Comercial,
                c.Territorio_del_cliente,
                SUM(s.net_revenue) as total_revenue,
                SUM(s.VentasCajasUnidad) as total_unit_sales,
                SUM(s.bottles_sold_m) as total_bottles_sold,
                COUNT(DISTINCT s.calday) as active_days,
                COUNT(DISTINCT s.material_id) as unique_products_purchased
            FROM dev.segmentacion s
            LEFT JOIN dev.cliente c ON s.customer_id = c.customer_id
            WHERE s.calday >= '{start_date.strftime("%Y-%m-%d")}'
            GROUP BY s.customer_id, c.Nombre_cliente, c.Canal_Comercial, c.Territorio_del_cliente
            ORDER BY total_revenue DESC
            """
            
            results = await self.mcp_client.execute_query(sql)
            
            if results:
                return [
                    {
                        "customer_id": row["customer_id"],
                        "customer_name": row.get("Nombre_cliente", "Unknown"),
                        "commercial_channel": row.get("Canal_Comercial", "Unknown"),
                        "territory": row.get("Territorio_del_cliente", "Unknown"),
                        "total_revenue": float(row.get("total_revenue", 0)),
                        "total_unit_sales": float(row.get("total_unit_sales", 0)),
                        "total_bottles_sold": float(row.get("total_bottles_sold", 0)),
                        "active_days": int(row.get("active_days", 0)),
                        "unique_products_purchased": int(row.get("unique_products_purchased", 0)),
                        "avg_daily_revenue": float(row.get("total_revenue", 0)) / max(int(row.get("active_days", 1)), 1)
                    }
                    for row in results
                ]
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error getting top customers: {e}")
            return []
    
    async def get_product_analysis(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get product performance analysis.
        
        Args:
            limit: Number of top products to return
            
        Returns:
            List of products with performance metrics
        """
        try:
            sql = f"""
            SELECT TOP {limit}
                s.material_id,
                p.Producto,
                p.Categoria,
                p.Subcategoria,
                p.AgrupadordeMarca,
                SUM(s.net_revenue) as total_revenue,
                SUM(s.VentasCajasUnidad) as total_unit_sales,
                SUM(s.bottles_sold_m) as total_bottles_sold,
                COUNT(DISTINCT s.customer_id) as unique_customers,
                COUNT(DISTINCT s.calday) as active_days,
                AVG(s.net_revenue) as avg_revenue_per_transaction
            FROM dev.segmentacion s
            LEFT JOIN dev.producto p ON s.material_id = p.Material
            WHERE s.calday >= DATEADD(month, -3, GETDATE())
            GROUP BY s.material_id, p.Producto, p.Categoria, p.Subcategoria, p.AgrupadordeMarca
            ORDER BY total_revenue DESC
            """
            
            results = await self.mcp_client.execute_query(sql)
            
            if results:
                return [
                    {
                        "material_id": row["material_id"],
                        "product_name": row.get("Producto", "Unknown Product"),
                        "category": row.get("Categoria", "Unknown"),
                        "subcategory": row.get("Subcategoria", "Unknown"),
                        "brand_group": row.get("AgrupadordeMarca", "Unknown"),
                        "total_revenue": float(row.get("total_revenue", 0)),
                        "total_unit_sales": float(row.get("total_unit_sales", 0)),
                        "total_bottles_sold": float(row.get("total_bottles_sold", 0)),
                        "unique_customers": int(row.get("unique_customers", 0)),
                        "active_days": int(row.get("active_days", 0)),
                        "avg_revenue_per_transaction": float(row.get("avg_revenue_per_transaction", 0))
                    }
                    for row in results
                ]
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error getting product analysis: {e}")
            return []
    
    async def get_sales_trends(self, period: str = "monthly") -> List[Dict[str, Any]]:
        """Get sales trends over time.
        
        Args:
            period: Period for trend analysis (daily, weekly, monthly)
            
        Returns:
            List of trend data points
        """
        try:
            if period == "monthly":
                sql = """
                SELECT 
                    CALMONTH,
                    YEAR(MIN(calday)) as year,
                    MONTH(MIN(calday)) as month,
                    SUM(net_revenue) as total_revenue,
                    SUM(VentasCajasUnidad) as total_unit_sales,
                    SUM(bottles_sold_m) as total_bottles_sold,
                    COUNT(DISTINCT customer_id) as active_customers,
                    COUNT(DISTINCT material_id) as products_sold
                FROM dev.segmentacion
                WHERE calday >= DATEADD(month, -12, GETDATE())
                GROUP BY CALMONTH
                ORDER BY CALMONTH
                """
            elif period == "weekly":
                sql = """
                SELECT 
                    DATEPART(year, calday) as year,
                    DATEPART(week, calday) as week,
                    MIN(calday) as week_start,
                    MAX(calday) as week_end,
                    SUM(net_revenue) as total_revenue,
                    SUM(VentasCajasUnidad) as total_unit_sales,
                    COUNT(DISTINCT customer_id) as active_customers
                FROM dev.segmentacion
                WHERE calday >= DATEADD(week, -12, GETDATE())
                GROUP BY DATEPART(year, calday), DATEPART(week, calday)
                ORDER BY year, week
                """
            else:  # daily
                sql = """
                SELECT 
                    calday,
                    SUM(net_revenue) as total_revenue,
                    SUM(VentasCajasUnidad) as total_unit_sales,
                    COUNT(DISTINCT customer_id) as active_customers
                FROM dev.segmentacion
                WHERE calday >= DATEADD(day, -30, GETDATE())
                GROUP BY calday
                ORDER BY calday
                """
            
            results = await self.mcp_client.execute_query(sql)
            
            if results:
                return results
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error getting sales trends: {e}")
            return []
    
    async def get_territorial_analysis(self) -> List[Dict[str, Any]]:
        """Get sales analysis by territory.
        
        Returns:
            List of territories with performance metrics
        """
        try:
            sql = """
            SELECT 
                m.Zona,
                m.Territorio,
                m.LocalForaneo,
                COUNT(DISTINCT s.customer_id) as unique_customers,
                SUM(s.net_revenue) as total_revenue,
                SUM(s.VentasCajasUnidad) as total_unit_sales,
                AVG(s.net_revenue) as avg_revenue_per_transaction,
                COUNT(DISTINCT s.material_id) as unique_products_sold
            FROM dev.segmentacion s
            LEFT JOIN dev.cliente c ON s.customer_id = c.customer_id
            LEFT JOIN dev.mercado m ON c.ID_Territorio_del_cliente = m.CEDIid
            WHERE s.calday >= DATEADD(month, -3, GETDATE())
            GROUP BY m.Zona, m.Territorio, m.LocalForaneo
            ORDER BY total_revenue DESC
            """
            
            results = await self.mcp_client.execute_query(sql)
            
            if results:
                return [
                    {
                        "zone": row.get("Zona", "Unknown"),
                        "territory": row.get("Territorio", "Unknown"),
                        "local_foreign": row.get("LocalForaneo", "Unknown"),
                        "unique_customers": int(row.get("unique_customers", 0)),
                        "total_revenue": float(row.get("total_revenue", 0)),
                        "total_unit_sales": float(row.get("total_unit_sales", 0)),
                        "avg_revenue_per_transaction": float(row.get("avg_revenue_per_transaction", 0)),
                        "unique_products_sold": int(row.get("unique_products_sold", 0))
                    }
                    for row in results
                ]
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error getting territorial analysis: {e}")
            return []


# Factory function to create MCP client
def create_mcp_client(server_url: str) -> MCPClient:
    """Create MCP client instance.
    
    Args:
        server_url: URL of the MCP server
        
    Returns:
        Configured MCP client
    """
    config = MCPClientConfig(server_url=server_url)
    return MCPClient(config)
