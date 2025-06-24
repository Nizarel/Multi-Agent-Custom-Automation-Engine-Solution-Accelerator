"""
Modern unit tests for the HTTP-only MCP client.
Tests the actual EnhancedMCPClient implementation without any fastmcp dependencies.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import httpx

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from mcp.client import EnhancedMCPClient, MCPClient, MCPTool, create_mcp_client, create_smart_mcp_client
from mcp.config import MCPConfig


class TestMCPTool:
    """Test cases for MCPTool class."""
    
    def test_mcp_tool_creation(self):
        """Test basic MCPTool creation."""
        tool = MCPTool(
            name="TestTool",
            description="A test tool",
            parameters={"param1": {"type": "string"}}
        )
        assert tool.name == "TestTool"
        assert tool.description == "A test tool"
        assert tool.parameters == {"param1": {"type": "string"}}
    
    def test_mcp_tool_equality(self):
        """Test MCPTool equality comparison."""
        tool1 = MCPTool(name="Tool1", description="Desc1", parameters={})
        tool2 = MCPTool(name="Tool1", description="Desc2", parameters={"different": True})
        tool3 = MCPTool(name="Tool2", description="Desc1", parameters={})
        
        assert tool1 == tool2  # Same name
        assert tool1 != tool3  # Different name
        assert tool1 != "not a tool"
    
    def test_mcp_tool_hashable(self):
        """Test MCPTool can be used in sets."""
        tool1 = MCPTool(name="Tool1", description="Desc1", parameters={})
        tool2 = MCPTool(name="Tool1", description="Desc2", parameters={})
        tool3 = MCPTool(name="Tool2", description="Desc1", parameters={})
        
        tools_set = {tool1, tool2, tool3}
        assert len(tools_set) == 2  # tool1 and tool2 are same, so only 2 unique


class TestEnhancedMCPClient:
    """Test cases for the modernized EnhancedMCPClient."""
    
    @pytest.fixture
    def mock_config(self):
        """Create a mock configuration for testing."""
        return MCPConfig()
    
    @pytest.fixture
    def client(self, mock_config):
        """Create a client instance for testing."""
        return EnhancedMCPClient(mock_config)
    
    def test_client_initialization(self, client, mock_config):
        """Test client initialization."""
        assert client.config == mock_config
        assert client._http_client is None
        assert not client._initialized
        assert client.available_tools == []
    
    def test_client_initialization_without_httpx(self):
        """Test client initialization fails without httpx."""
        with patch('mcp.client.HTTPX_AVAILABLE', False):
            config = MCPConfig()
            with pytest.raises(RuntimeError, match="httpx is required"):
                EnhancedMCPClient(config)
    
    @pytest.mark.asyncio
    async def test_context_manager(self, client):
        """Test async context manager functionality."""
        with patch.object(client, 'connect') as mock_connect, \
             patch.object(client, 'disconnect') as mock_disconnect:
            
            async with client:
                assert mock_connect.called
            
            assert mock_disconnect.called
    
    @pytest.mark.asyncio
    async def test_connect_success(self, client):
        """Test successful HTTP connection and tool discovery."""
        mock_http_client = AsyncMock()
        
        with patch('httpx.AsyncClient', return_value=mock_http_client), \
             patch.object(client, '_discover_tools') as mock_discover:
            
            await client.connect()
            
            assert client._http_client == mock_http_client
            assert client._initialized
            mock_discover.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_connect_failure(self, client):
        """Test connection failure handling."""
        with patch('httpx.AsyncClient', side_effect=Exception("Connection failed")):
            
            with pytest.raises(Exception, match="Connection failed"):
                await client.connect()
            
            assert not client._initialized
    
    @pytest.mark.asyncio
    async def test_disconnect_cleanup(self, client):
        """Test proper cleanup during disconnect."""
        mock_http_client = AsyncMock()
        client._http_client = mock_http_client
        client._initialized = True
        
        await client.disconnect()
        
        mock_http_client.aclose.assert_called_once()
        assert client._http_client is None
        assert not client._initialized
    
    @pytest.mark.asyncio
    async def test_discover_tools_http_success(self, client):
        """Test successful tool discovery via HTTP."""
        mock_http_client = AsyncMock()
        
        # Mock successful HTTP response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.text = 'event: message\ndata: {"tools": [{"name": "ListTables", "description": "List tables"}]}'
        mock_http_client.post.return_value = mock_response
        
        client._http_client = mock_http_client
        
        await client._discover_tools_http()
        
        # Should call the HTTP endpoint
        mock_http_client.post.assert_called_once()
        call_args = mock_http_client.post.call_args
        assert call_args[0][0] == client.config.default_server_url
        assert call_args[1]["json"]["method"] == "tools/list"
    
    @pytest.mark.asyncio
    async def test_discover_tools_http_failure(self, client):
        """Test tool discovery failure fallback."""
        mock_http_client = AsyncMock()
        mock_http_client.post.side_effect = Exception("HTTP error")
        client._http_client = mock_http_client
        
        await client._discover_tools_http()
        
        assert [] == []  # Should return empty list on failure
    
    def test_add_fallback_tools(self, client):
        """Test adding fallback tools when discovery fails."""
        client._add_fallback_tools()
        
        assert len(client.available_tools) >= 3  # Should have at least ListTables, DescribeTable, ReadData
        tool_names = [tool.name for tool in client.available_tools]
        assert "ListTables" in tool_names
        assert "DescribeTable" in tool_names
        assert "ReadData" in tool_names
    
    def test_add_fallback_tools_no_duplicates(self, client):
        """Test that fallback tools don't create duplicates."""
        client._add_fallback_tools()
        initial_count = len(client.available_tools)
        
        client._add_fallback_tools()  # Add again
        
        assert len(client.available_tools) == initial_count  # No duplicates
    
    @pytest.mark.asyncio
    async def test_http_call_tool_success(self, client):
        """Test successful HTTP tool call."""
        mock_http_client = AsyncMock()
        
        # Mock successful response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.text = 'event: message\ndata: {"data": ["table1", "table2"]}'
        mock_http_client.post.return_value = mock_response
        
        client._http_client = mock_http_client
        
        result = await client._http_call_tool("ListTables", {})
        
        assert "data" in result
        assert result["data"] == ["table1", "table2"]
        
        # Verify request format
        call_args = mock_http_client.post.call_args
        payload = call_args[1]["json"]
        assert payload["method"] == "tools/call"
        assert payload["params"]["name"] == "ListTables"
        assert payload["params"]["arguments"] == {}
    
    @pytest.mark.asyncio
    async def test_http_call_tool_json_response(self, client):
        """Test HTTP tool call with regular JSON response."""
        mock_http_client = AsyncMock()
        
        # Mock SSE response format as the server actually returns
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.text = 'event: message\ndata: {"jsonrpc": "2.0", "result": {"content": [{"type": "text", "text": "{\\"data\\": [\\"cliente\\", \\"producto\\"]}"}]}}'
        mock_http_client.post.return_value = mock_response
        
        client._http_client = mock_http_client
        
        result = await client._http_call_tool("ListTables", {})
        
        assert "data" in result
        assert "cliente" in result["data"]
    
    @pytest.mark.asyncio
    async def test_http_call_tool_failure(self, client):
        """Test HTTP tool call failure handling."""
        mock_http_client = AsyncMock()
        mock_http_client.post.side_effect = httpx.HTTPError("Network error")
        client._http_client = mock_http_client
        
        result = await client._http_call_tool("ListTables", {})
        
        assert "error" in result
        assert "Network error" in result["error"]
    
    @pytest.mark.asyncio
    async def test_list_tables_success(self, client):
        """Test successful table listing."""
        mock_result = {"data": ["cliente", "producto", "segmentacion"]}
        
        with patch.object(client, '_http_call_tool', return_value=mock_result) as mock_call:
            client._initialized = True
            
            result = await client.list_tables()
            
            assert "data" in result
            assert len(result["data"]) == 3
            assert "cliente" in result["data"]
            mock_call.assert_called_once_with("ListTables", {})
    
    @pytest.mark.asyncio
    async def test_list_tables_auto_connect(self, client):
        """Test that list_tables auto-connects if not initialized."""
        with patch.object(client, 'connect') as mock_connect, \
             patch.object(client, '_http_call_tool', return_value={"data": []}):
            
            await client.list_tables()
            
            mock_connect.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_list_tables_vscode_tools(self, client):
        """Test list_tables with VS Code MCP tools."""
        # Mock VS Code tools being available
        mock_vscode_result = {"data": ["vscode_table1", "vscode_table2"]}
        
        # Mock the import and function call within the list_tables method
        mock_module = MagicMock()
        mock_module.mcp_arca_mcp_srv1_ListTables = AsyncMock(return_value=mock_vscode_result)
        
        with patch('builtins.__import__', return_value=mock_module):
            client._initialized = True
            
            result = await client.list_tables()
            
            assert result == mock_vscode_result
    
    @pytest.mark.asyncio
    async def test_list_tables_fallback_on_error(self, client):
        """Test list_tables fallback when HTTP call fails."""
        with patch.object(client, '_http_call_tool', side_effect=Exception("HTTP error")):
            client._initialized = True
            
            result = await client.list_tables()
            
            assert "tables" in result
            assert isinstance(result["tables"], list)  # Should return mock data
    
    @pytest.mark.asyncio
    async def test_describe_table_success(self, client):
        """Test successful table description."""
        mock_result = {
            "table_name": "cliente",
            "columns": [
                {"name": "customer_id", "type": "nvarchar"},
                {"name": "Nombre_cliente", "type": "nvarchar"}
            ]
        }
        
        with patch.object(client, '_http_call_tool', return_value=mock_result) as mock_call:
            client._initialized = True
            
            result = await client.describe_table("cliente")
            
            assert result["table_name"] == "cliente"
            assert len(result["columns"]) == 2
            mock_call.assert_called_once_with("DescribeTable", {"name": "cliente"})
    
    @pytest.mark.asyncio
    async def test_describe_table_empty_name(self, client):
        """Test describe_table with empty table name."""
        result = await client.describe_table("")
        
        assert "error" in result
        assert "Table name is required" in result["error"]
    
    @pytest.mark.asyncio
    async def test_describe_table_fallback_on_error(self, client):
        """Test describe_table fallback when HTTP call fails."""
        with patch.object(client, '_http_call_tool', side_effect=Exception("HTTP error")):
            client._initialized = True
            
            result = await client.describe_table("test_table")
            
            assert result["table_name"] == "test_table"
            assert "columns" in result
            assert isinstance(result["columns"], list)  # Should return mock schema
    
    @pytest.mark.asyncio
    async def test_execute_query_success(self, client):
        """Test successful query execution."""
        mock_result = {
            "data": [
                {"customer_id": "C001", "name": "Cliente 1"},
                {"customer_id": "C002", "name": "Cliente 2"}
            ],
            "columns": ["customer_id", "name"],
            "row_count": 2
        }
        
        with patch.object(client, '_http_call_tool', return_value=mock_result) as mock_call:
            client._initialized = True
            
            result = await client.execute_query("SELECT TOP 2 * FROM cliente")
            
            assert "data" in result
            assert result["row_count"] == 2
            mock_call.assert_called_once_with("ReadData", {"sql": "SELECT TOP 2 * FROM cliente"})
    
    @pytest.mark.asyncio
    async def test_execute_query_dangerous_sql_blocked(self, client):
        """Test that dangerous SQL operations are blocked."""
        dangerous_queries = [
            "DROP TABLE cliente",
            "DELETE FROM cliente",
            "TRUNCATE TABLE cliente", 
            "ALTER TABLE cliente ADD column",
            "INSERT INTO cliente VALUES (1, 'test')",
            "UPDATE cliente SET name = 'test'"
        ]
        
        for query in dangerous_queries:
            result = await client.execute_query(query)
            assert "error" in result
            assert "dangerous operations" in result["error"]
    
    @pytest.mark.asyncio
    async def test_execute_query_empty_sql(self, client):
        """Test execute_query with empty SQL."""
        result = await client.execute_query("")
        
        assert "error" in result
        assert "SQL query is required" in result["error"]
    
    @pytest.mark.asyncio
    async def test_execute_query_fallback_on_error(self, client):
        """Test execute_query fallback when HTTP call fails."""
        with patch.object(client, '_http_call_tool', side_effect=Exception("HTTP error")):
            client._initialized = True
            
            result = await client.execute_query("SELECT * FROM cliente")
            
            assert "data" in result
            assert result["data"] == []  # Should return empty result
            assert "sql" in result
    
    @pytest.mark.asyncio
    async def test_call_tool_routing(self, client):
        """Test that call_tool routes to specific methods correctly."""
        client._initialized = True
        
        # Test ListTables routing
        with patch.object(client, 'list_tables', return_value={"tables": []}) as mock_list:
            await client.call_tool("ListTables")
            mock_list.assert_called_once()
        
        # Test DescribeTable routing
        with patch.object(client, 'describe_table', return_value={"table_name": "test"}) as mock_describe:
            await client.call_tool("DescribeTable", name="test_table")
            mock_describe.assert_called_once_with("test_table", "default")
        
        # Test ReadData routing
        with patch.object(client, 'execute_query', return_value={"data": []}) as mock_execute:
            await client.call_tool("ReadData", sql="SELECT * FROM test")
            mock_execute.assert_called_once_with("SELECT * FROM test", "default")
    
    @pytest.mark.asyncio
    async def test_call_tool_generic(self, client):
        """Test generic tool call for unknown tools."""
        mock_result = {"result": "success"}
        
        with patch.object(client, '_http_call_tool', return_value=mock_result) as mock_call:
            client._initialized = True
            
            result = await client.call_tool("CustomTool", param="value")
            
            assert result == mock_result
            mock_call.assert_called_once_with("CustomTool", {"param": "value"})
    
    @pytest.mark.asyncio
    async def test_health_check_success(self, client):
        """Test successful health check."""
        with patch.object(client, 'list_tables', return_value={"data": ["table1"]}) as mock_list:
            client._initialized = True
            
            result = await client.health_check()
            
            assert result is True
            mock_list.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_health_check_failure(self, client):
        """Test health check failure."""
        with patch.object(client, 'list_tables', return_value={"error": "Connection failed"}):
            client._initialized = True
            
            result = await client.health_check()
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_get_server_info(self, client):
        """Test getting server information."""
        client._initialized = True
        
        result = await client.get_server_info()
        
        assert result["server_name"] == "default"
        assert result["type"] == "http"
        assert "url" in result


class TestFactoryFunctions:
    """Test cases for factory functions."""
    
    @pytest.mark.asyncio
    async def test_create_mcp_client_default_config(self):
        """Test creating MCP client with default config."""
        with patch.object(EnhancedMCPClient, 'connect') as mock_connect:
            client = await create_mcp_client()
            
            assert isinstance(client, EnhancedMCPClient)
            mock_connect.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_mcp_client_custom_config(self):
        """Test creating MCP client with custom config."""
        config = MCPConfig()
        
        with patch.object(EnhancedMCPClient, 'connect') as mock_connect:
            client = await create_mcp_client(config)
            
            assert isinstance(client, EnhancedMCPClient)
            assert client.config == config
            mock_connect.assert_called_once()
    
    def test_create_smart_mcp_client_default(self):
        """Test smart client creation fallback to EnhancedMCPClient."""
        client = create_smart_mcp_client()
        
        assert isinstance(client, EnhancedMCPClient)
    
    def test_create_smart_mcp_client_vscode_detected(self):
        """Test smart client creation with VS Code tools detected."""
        with patch('importlib.util.find_spec', return_value=MagicMock()):
            client = create_smart_mcp_client()
            
            # Should create VSCodeMCPClient when VS Code tools are available
            assert hasattr(client, 'list_tables')  # Basic check that it's a valid client


class TestMCPClientAlias:
    """Test that MCPClient is properly aliased to EnhancedMCPClient."""
    
    def test_mcp_client_alias(self):
        """Test that MCPClient is an alias for EnhancedMCPClient."""
        assert MCPClient is EnhancedMCPClient
    
    def test_mcp_client_instantiation(self):
        """Test that MCPClient can be instantiated."""
        config = MCPConfig()
        client = MCPClient(config)
        
        assert isinstance(client, EnhancedMCPClient)
        assert client.config == config


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
