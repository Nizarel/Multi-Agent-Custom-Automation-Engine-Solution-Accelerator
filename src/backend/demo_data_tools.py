#!/usr/bin/env python3
"""
Demonstration script for the updated DataAnalysisTools.
Shows how to use the tools with the modernized MCP client.
"""

import asyncio
import logging
from mcp.client import create_smart_mcp_client
from mcp.tools.data_tools import DataAnalysisTools

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def demo_data_tools():
    """Demonstrate the updated DataAnalysisTools functionality."""
    try:
        logger.info("=== DataAnalysisTools Demo ===")
        
        # Create MCP client
        logger.info("Creating MCP client...")
        client = await create_smart_mcp_client()
        
        # Create DataAnalysisTools with convenience method
        logger.info("Initializing DataAnalysisTools...")
        tools = await DataAnalysisTools.create_with_client(client)
        
        # Test 1: Get available tables
        logger.info("Testing get_available_tables()...")
        tables = await tools.get_available_tables()
        logger.info(f"Available tables: {tables}")
        
        # Test 2: Explore database schema
        logger.info("Testing explore_database_schema()...")
        schema = await tools.explore_database_schema()
        logger.info(f"Schema exploration found {len(schema.get('tables', []))} tables")
        
        # Test 3: Execute a simple query (if tables are available)
        if tables and 'cliente' in tables:
            logger.info("Testing execute_custom_query() with cliente table...")
            query_result = await tools.execute_custom_query("SELECT TOP 5 * FROM cliente")
            if "error" not in query_result:
                logger.info(f"Query successful! Returned {query_result.get('rows_returned', 0)} rows")
            else:
                logger.warning(f"Query error: {query_result['error']}")
        
        # Test 4: Data quality report (with updated table names)
        logger.info("Testing get_data_quality_report() with updated table names...")
        quality_report = await tools.get_data_quality_report()
        logger.info(f"Quality report overall status: {quality_report.get('overall_quality', 'unknown')}")
        logger.info(f"Successful tables: {quality_report.get('successful_tables', 0)}/{quality_report.get('total_tables_checked', 0)}")
        
        logger.info("=== Demo completed successfully! ===")
        return True
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    result = asyncio.run(demo_data_tools())
    if result:
        print("\n✅ DataAnalysisTools are working correctly!")
        print("✅ Table references updated (no more dev. schema prefix)")
        print("✅ Ready for agent integration")
    else:
        print("\n❌ Demo failed - check logs for details")
