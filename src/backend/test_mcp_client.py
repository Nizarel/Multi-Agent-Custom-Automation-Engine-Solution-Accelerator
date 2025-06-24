#!/usr/bin/env python3
"""
Test script for MCP client functionality.
This will verify that the MCP client can connect to your server and execute basic operations.
"""

import asyncio
import logging
import sys
import traceback
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_vscode_mcp_functions():
    """Test VS Code MCP functions directly."""
    print("\n" + "="*60)
    print("🧪 Testing VS Code MCP Functions")
    print("="*60)
    
    try:
        # Test ListTables function
        print("\n📋 Testing ListTables...")
        from mcp_arca_mcp_srv1_ListTables import mcp_arca_mcp_srv1_ListTables
        tables_result = mcp_arca_mcp_srv1_ListTables()
        print(f"✅ ListTables result: {tables_result}")
        
        # Test DescribeTable function
        print("\n🔍 Testing DescribeTable...")
        from mcp_arca_mcp_srv1_DescribeTable import mcp_arca_mcp_srv1_DescribeTable
        describe_result = mcp_arca_mcp_srv1_DescribeTable(name="segmentacion")
        print(f"✅ DescribeTable result: {describe_result}")
        
        # Test ReadData function
        print("\n📊 Testing ReadData...")
        from mcp_arca_mcp_srv1_ReadData import mcp_arca_mcp_srv1_ReadData
        query_result = mcp_arca_mcp_srv1_ReadData(sql="SELECT TOP 3 * FROM dev.segmentacion ORDER BY calday DESC")
        print(f"✅ ReadData result: {query_result}")
        
        return True
        
    except ImportError as e:
        print(f"❌ VS Code MCP functions not available: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing VS Code MCP functions: {e}")
        traceback.print_exc()
        return False

async def test_mcp_client():
    """Test the MCP client implementation."""
    print("\n" + "="*60)
    print("🔧 Testing MCP Client Implementation")
    print("="*60)
    
    try:
        # Import MCP client components
        from mcp.config import MCPConfig
        from mcp.client import create_vscode_mcp_client
        
        print("\n⚙️ Creating MCP configuration...")
        config = MCPConfig()
        print(f"✅ Config created with server URL: {config.server_url}")
        
        print("\n🔌 Creating VS Code MCP client...")
        client = create_vscode_mcp_client(config)
        print(f"✅ Client created: {type(client).__name__}")
        
        print("\n🔗 Testing client connection...")
        await client.connect()
        print("✅ Client connected successfully")
        
        print("\n📋 Testing list_tables...")
        tables = await client.list_tables()
        print(f"✅ Tables retrieved: {tables}")
        
        print("\n🔍 Testing describe_table...")
        table_desc = await client.describe_table("segmentacion")
        print(f"✅ Table description: {table_desc}")
        
        print("\n📊 Testing execute_query...")
        query_result = await client.execute_query("SELECT TOP 2 * FROM dev.segmentacion ORDER BY calday DESC")
        print(f"✅ Query result: {query_result}")
        
        print("\n🏥 Testing health check...")
        health = await client.health_check()
        print(f"✅ Health check: {'PASSED' if health else 'FAILED'}")
        
        print("\n🔌 Disconnecting client...")
        await client.disconnect()
        print("✅ Client disconnected")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing MCP client: {e}")
        traceback.print_exc()
        return False

async def test_mcp_with_context_manager():
    """Test MCP client using async context manager."""
    print("\n" + "="*60)
    print("🔄 Testing MCP Client with Context Manager")
    print("="*60)
    
    try:
        from mcp.config import MCPConfig
        from mcp.client import create_vscode_mcp_client
        
        config = MCPConfig()
        client = create_vscode_mcp_client(config)
        
        print("\n🔄 Using async context manager...")
        async with client:
            print("✅ Context manager entered")
            
            # Test operations within context
            tools = client.get_available_tools()
            print(f"✅ Available tools: {[tool.name for tool in tools]}")
            
            tables = await client.list_tables()
            print(f"✅ Tables: {tables}")
            
        print("✅ Context manager exited")
        return True
        
    except Exception as e:
        print(f"❌ Error testing context manager: {e}")
        traceback.print_exc()
        return False

async def test_sales_data_operations():
    """Test sales-specific data operations."""
    print("\n" + "="*60)
    print("📈 Testing Sales Data Operations")
    print("="*60)
    
    try:
        from mcp.config import MCPConfig
        from mcp.client import create_vscode_mcp_client
        
        config = MCPConfig()
        
        async with create_vscode_mcp_client(config) as client:
            print("\n📊 Testing sales performance query...")
            sales_query = """
            SELECT 
                COUNT(DISTINCT customer_id) as unique_customers,
                SUM(net_revenue) as total_revenue,
                AVG(net_revenue) as avg_revenue,
                MAX(calday) as latest_date
            FROM dev.segmentacion 
            WHERE calday >= '2025-06-01'
            """
            
            result = await client.execute_query(sales_query)
            print(f"✅ Sales performance: {result}")
            
            print("\n👥 Testing customer data query...")
            customer_query = """
            SELECT TOP 5 
                customer_id, 
                Nombre_cliente, 
                Canal_Comercial 
            FROM dev.cliente 
            WHERE Nombre_cliente IS NOT NULL
            """
            
            customers = await client.execute_query(customer_query)
            print(f"✅ Customer data: {customers}")
            
            print("\n🛍️ Testing product data query...")
            product_query = """
            SELECT TOP 5 
                Material, 
                Producto, 
                Categoria 
            FROM dev.producto 
            WHERE Producto IS NOT NULL
            """
            
            products = await client.execute_query(product_query)
            print(f"✅ Product data: {products}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error testing sales data operations: {e}")
        traceback.print_exc()
        return False

async def main():
    """Main test function."""
    print("🚀 Starting MCP Client Tests")
    print(f"⏰ Test started at: {datetime.now()}")
    
    test_results = []
    
    # Test 1: VS Code MCP functions
    vscode_result = await test_vscode_mcp_functions()
    test_results.append(("VS Code MCP Functions", vscode_result))
    
    # Test 2: MCP Client implementation
    client_result = await test_mcp_client()
    test_results.append(("MCP Client Implementation", client_result))
    
    # Test 3: Context manager
    context_result = await test_mcp_with_context_manager()
    test_results.append(("Context Manager", context_result))
    
    # Test 4: Sales data operations
    sales_result = await test_sales_data_operations()
    test_results.append(("Sales Data Operations", sales_result))
    
    # Summary
    print("\n" + "="*60)
    print("📋 TEST SUMMARY")
    print("="*60)
    
    passed = 0
    failed = 0
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\n📊 Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! MCP client is working correctly.")
        return 0
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        traceback.print_exc()
        sys.exit(1)
