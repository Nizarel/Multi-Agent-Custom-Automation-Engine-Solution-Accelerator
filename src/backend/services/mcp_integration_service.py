"""MCP Integration Service for Revenue Performance Tools.

This service manages MCP client connections and provides a unified interface
for the Revenue Performance Tools to interact with the database through MCP.
"""

import logging
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

from mcp.client import EnhancedMCPClient, create_smart_mcp_client
from mcp.config import MCPConfig

logger = logging.getLogger(__name__)


class MCPIntegrationService:
    """Singleton service for managing MCP client connections."""
    
    _instance = None
    _client: Optional[EnhancedMCPClient] = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MCPIntegrationService, cls).__new__(cls)
        return cls._instance
    
    async def initialize(self, config: Optional[MCPConfig] = None):
        """Initialize the MCP client connection."""
        if self._initialized:
            return
        
        try:
            logger.info("Initializing MCP Integration Service...")
            
            # Create MCP client with smart detection
            if config is None:
                config = MCPConfig()
            
            self._client = create_smart_mcp_client(config)
            await self._client.connect()
            
            # Verify connection with a health check
            health_check = await self._client.health_check()
            if health_check:
                logger.info("✅ MCP client connected and healthy")
            else:
                logger.warning("⚠️ MCP client connected but health check failed")
            
            self._initialized = True
            logger.info("🚀 MCP Integration Service initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize MCP Integration Service: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from MCP client."""
        if self._client:
            try:
                await self._client.disconnect()
                logger.info("MCP client disconnected successfully")
            except Exception as e:
                logger.error(f"Error disconnecting MCP client: {e}")
            finally:
                self._client = None
                self._initialized = False
    
    def get_client(self) -> Optional[EnhancedMCPClient]:
        """Get the MCP client instance."""
        return self._client
    
    def is_initialized(self) -> bool:
        """Check if the service is initialized."""
        return self._initialized
    
    async def ensure_connected(self):
        """Ensure the MCP client is connected."""
        if not self._initialized:
            await self.initialize()
        
        if self._client and not self._client._initialized:
            await self._client.connect()
    
    async def execute_query(self, sql: str) -> Dict[str, Any]:
        """Execute a SQL query through the MCP client.
        
        Args:
            sql: SQL query to execute
            
        Returns:
            Query result from MCP client
        """
        await self.ensure_connected()
        
        if not self._client:
            raise RuntimeError("MCP client not available")
        
        try:
            result = await self._client.execute_query(sql)
            logger.debug(f"Query executed successfully: {sql[:100]}...")
            return result
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
    
    async def list_tables(self) -> Dict[str, Any]:
        """List all available tables."""
        await self.ensure_connected()
        
        if not self._client:
            raise RuntimeError("MCP client not available")
        
        try:
            result = await self._client.list_tables()
            logger.debug("Tables listed successfully")
            return result
        except Exception as e:
            logger.error(f"Failed to list tables: {e}")
            raise
    
    async def describe_table(self, table_name: str) -> Dict[str, Any]:
        """Describe a table schema.
        
        Args:
            table_name: Name of the table to describe
            
        Returns:
            Table schema information
        """
        await self.ensure_connected()
        
        if not self._client:
            raise RuntimeError("MCP client not available")
        
        try:
            result = await self._client.describe_table(table_name)
            logger.debug(f"Table '{table_name}' described successfully")
            return result
        except Exception as e:
            logger.error(f"Failed to describe table '{table_name}': {e}")
            raise
    
    async def health_check(self) -> bool:
        """Perform a health check on the MCP connection."""
        try:
            await self.ensure_connected()
            
            if not self._client:
                return False
            
            return await self._client.health_check()
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    async def get_connection_info(self) -> Dict[str, Any]:
        """Get information about the current MCP connection."""
        if not self._client:
            return {"status": "disconnected"}
        
        try:
            info = await self._client.get_server_info()
            info["status"] = "connected" if self._initialized else "disconnected"
            info["health"] = await self.health_check()
            return info
        except Exception as e:
            logger.error(f"Failed to get connection info: {e}")
            return {"status": "error", "error": str(e)}
    
    @asynccontextmanager
    async def get_connection(self):
        """Context manager for getting a connection."""
        await self.ensure_connected()
        try:
            yield self._client
        finally:
            # Keep connection alive for reuse
            pass


# Global instance
_mcp_service = MCPIntegrationService()


async def get_mcp_service() -> MCPIntegrationService:
    """Get the global MCP integration service instance."""
    if not _mcp_service.is_initialized():
        await _mcp_service.initialize()
    return _mcp_service


async def initialize_mcp_service(config: Optional[MCPConfig] = None):
    """Initialize the global MCP service."""
    await _mcp_service.initialize(config)


async def shutdown_mcp_service():
    """Shutdown the global MCP service."""
    await _mcp_service.disconnect()


# Convenience functions for direct access
async def execute_query(sql: str) -> Dict[str, Any]:
    """Execute a SQL query through the global MCP service."""
    service = await get_mcp_service()
    return await service.execute_query(sql)


async def list_tables() -> Dict[str, Any]:
    """List all tables through the global MCP service."""
    service = await get_mcp_service()
    return await service.list_tables()


async def describe_table(table_name: str) -> Dict[str, Any]:
    """Describe a table through the global MCP service."""
    service = await get_mcp_service()
    return await service.describe_table(table_name)


async def health_check() -> bool:
    """Perform a health check through the global MCP service."""
    try:
        service = await get_mcp_service()
        return await service.health_check()
    except Exception:
        return False


async def get_connection_info() -> Dict[str, Any]:
    """Get connection info through the global MCP service."""
    try:
        service = await get_mcp_service()
        return await service.get_connection_info()
    except Exception as e:
        return {"status": "error", "error": str(e)}
