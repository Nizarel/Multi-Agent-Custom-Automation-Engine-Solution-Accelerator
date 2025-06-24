"""Data analysis tools using MCP client with async/await best practices."""

import logging
import asyncio
from typing import Any, Dict, Optional, List

logger = logging.getLogger(__name__)


class DataAnalysisTools:
    """Data analysis and exploration tools for agents with async optimization."""
    
    def __init__(self, mcp_client):
        """Initialize data analysis tools.
        
        Args:
            mcp_client: MCP client instance with list_tables, describe_table, execute_query methods
        """
        self.mcp_client = mcp_client
    
    @classmethod
    async def create_with_client(cls, mcp_client):
        """Create DataAnalysisTools instance and ensure client is connected.
        
        Args:
            mcp_client: MCP client instance
            
        Returns:
            DataAnalysisTools instance
        """
        tools = cls(mcp_client)
        # Verify client is working
        try:
            await mcp_client.list_tables()
            logger.info("DataAnalysisTools initialized successfully")
        except Exception as e:
            logger.warning(f"DataAnalysisTools initialization warning: {e}")
        return tools
    
    async def get_available_tables(self) -> List[str]:
        """Get list of available tables for analysis.
        
        Returns:
            List of table names
        """
        try:
            result = await self.mcp_client.list_tables()
            if isinstance(result, dict):
                if "data" in result:
                    return result["data"]
                elif "tables" in result:
                    return result["tables"]
                elif "error" in result:
                    logger.error(f"Error listing tables: {result['error']}")
                    return []
            elif isinstance(result, list):
                return result
            return []
        except Exception as e:
            logger.error(f"Error getting available tables: {e}")
            return []
    
    async def explore_database_schema(self) -> Dict[str, Any]:
        """Explore the database schema and available tables concurrently.
        
        Returns:
            Database schema information
        """
        try:
            # Get list of tables
            tables_result = await self.mcp_client.list_tables()
            
            # Handle different result formats
            if isinstance(tables_result, dict):
                if "tables" in tables_result:
                    tables = tables_result["tables"]
                elif "error" in tables_result:
                    return {"error": f"Failed to list tables: {tables_result['error']}"}
                else:
                    tables = []
            elif isinstance(tables_result, list):
                tables = tables_result
            else:
                tables = []
            
            schema_info = {
                "total_tables": len(tables),
                "tables": []
            }
            
            # Get descriptions for all tables concurrently
            if tables:
                table_tasks = [
                    self._get_table_info(table) 
                    for table in tables
                ]
                table_results = await asyncio.gather(*table_tasks, return_exceptions=True)
                
                for table, result in zip(tables, table_results):
                    if isinstance(result, Exception):
                        logger.warning(f"Failed to describe table {table}: {result}")
                        schema_info["tables"].append({
                            "name": table,
                            "error": str(result)
                        })
                    elif result:
                        schema_info["tables"].append({
                            "name": table,
                            "description": result
                        })
            
            return schema_info
            
        except Exception as e:
            logger.error(f"Error exploring database schema: {e}")
            return {"error": str(e)}
    
    async def _get_table_info(self, table_name: str) -> Optional[Dict[str, Any]]:
        """Helper method to get table information asynchronously."""
        try:
            return await self.mcp_client.describe_table(table_name)
        except Exception as e:
            logger.warning(f"Failed to describe table {table_name}: {e}")
            return None
    
    async def execute_custom_query(self, sql: str) -> Dict[str, Any]:
        """Execute a custom SQL query with enhanced safety checks and result processing.
        
        Args:
            sql: SQL query to execute
            
        Returns:
            Query results with metadata
        """
        if not sql or not sql.strip():
            return {"error": "SQL query cannot be empty"}
            
        try:
            # Enhanced safety checks
            sql_lower = sql.lower().strip()
            
            # Block dangerous operations
            dangerous_keywords = [
                'drop', 'delete', 'truncate', 'alter table', 'create', 
                'insert', 'update', 'grant', 'revoke', 'exec'
            ]
            if any(keyword in sql_lower for keyword in dangerous_keywords):
                return {
                    "error": "Query contains potentially dangerous operations and was blocked",
                    "blocked_keywords": [kw for kw in dangerous_keywords if kw in sql_lower]
                }
            
            # Execute the query
            results = await self.mcp_client.execute_query(sql)
            
            # Enhanced result processing
            if isinstance(results, dict):
                if "error" in results:
                    return results
                elif "data" in results:
                    return {
                        "success": True,
                        "rows_returned": len(results["data"]) if isinstance(results["data"], list) else 1,
                        "data": results["data"],
                        "query": sql,
                        "columns": results.get("columns", [])
                    }
                else:
                    return {
                        "success": True,
                        "rows_returned": 1,
                        "data": results,
                        "query": sql
                    }
            elif isinstance(results, list):
                return {
                    "success": True,
                    "rows_returned": len(results),
                    "data": results,
                    "query": sql
                }
            else:
                return {"error": "Unexpected query result format"}
                
        except Exception as e:
            logger.error(f"Error executing custom query: {e}")
            return {"error": str(e), "query": sql}
    
    async def get_data_quality_report(self) -> Dict[str, Any]:
        """Generate a data quality report for key tables using concurrent queries.
        
        Returns:
            Data quality analysis
        """
        try:
            quality_report = {
                "segmentacion_table": {},
                "cliente_table": {},
                "producto_table": {},
                "overall_quality": "unknown"
            }
            
            # Define quality check queries for SQL Server
            queries = {
                "segmentacion": """
                    SELECT 
                        COUNT(*) as total_rows,
                        COUNT(DISTINCT customer_id) as unique_customers,
                        COUNT(DISTINCT material_id) as unique_products,
                        COUNT(DISTINCT calday) as unique_dates,
                        SUM(CASE WHEN net_revenue IS NULL THEN 1 ELSE 0 END) as null_revenue_count,
                        MIN(calday) as earliest_date,
                        MAX(calday) as latest_date
                    FROM (SELECT TOP 10000 * FROM dev.segmentacion) as sample
                """,
                "cliente": """
                    SELECT 
                        COUNT(*) as total_clients,
                        COUNT(DISTINCT Canal_Comercial) as unique_channels,
                        COUNT(DISTINCT Territorio_del_cliente) as unique_territories,
                        SUM(CASE WHEN Nombre_cliente IS NULL THEN 1 ELSE 0 END) as null_names_count
                    FROM (SELECT TOP 1000 * FROM dev.cliente) as sample
                """,
                "producto": """
                    SELECT 
                        COUNT(*) as total_products,
                        COUNT(DISTINCT Categoria) as unique_categories,
                        COUNT(DISTINCT AgrupadordeMarca) as unique_brands,
                        SUM(CASE WHEN Producto IS NULL THEN 1 ELSE 0 END) as null_product_names
                    FROM (SELECT TOP 1000 * FROM dev.producto) as sample
                """
            }
            
            # Execute all queries concurrently
            tasks = [
                self.mcp_client.execute_query(query)
                for query in queries.values()
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            table_names = list(queries.keys())
            successful_tables = 0
            
            for i, (table_name, result) in enumerate(zip(table_names, results)):
                if isinstance(result, Exception):
                    logger.error(f"Error querying {table_name}: {result}")
                    quality_report[f"{table_name}_table"] = {"error": str(result)}
                elif isinstance(result, dict):
                    if "error" in result:
                        logger.error(f"Query error for {table_name}: {result['error']}")
                        quality_report[f"{table_name}_table"] = result
                    elif "data" in result and result["data"]:
                        quality_report[f"{table_name}_table"] = result["data"][0]
                        successful_tables += 1
                    else:
                        quality_report[f"{table_name}_table"] = result
                        if result:  # Any non-empty result
                            successful_tables += 1
                elif isinstance(result, list) and result:
                    quality_report[f"{table_name}_table"] = result[0]
                    successful_tables += 1
            
            # Determine overall quality based on successful queries
            if successful_tables == len(table_names):
                quality_report["overall_quality"] = "good"
            elif successful_tables > 0:
                quality_report["overall_quality"] = "partial"
            else:
                quality_report["overall_quality"] = "poor"
            
            quality_report["successful_tables"] = successful_tables
            quality_report["total_tables_checked"] = len(table_names)
            
            return quality_report
            
        except Exception as e:
            logger.error(f"Error generating data quality report: {e}")
            return {"error": str(e)}
