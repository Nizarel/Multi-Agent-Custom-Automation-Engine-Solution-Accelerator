"""MCP configuration management with fastmcp integration."""

import os
from typing import Dict, Optional, Any

# Temporarily disable fastmcp due to import conflict with local mcp package
# try:
#     from fastmcp.utilities.mcp_config import MCPConfig as FastMCPConfig, RemoteMCPServer, StdioMCPServer
#     FASTMCP_AVAILABLE = True
# except ImportError:
FASTMCP_AVAILABLE = False
FastMCPConfig = None
RemoteMCPServer = None
StdioMCPServer = None


class MCPConfig:
    """Enhanced configuration for MCP services with fastmcp support."""
    
    def __init__(self):
        """Initialize MCP configuration from environment variables."""
        # Default MCP server URL - Your Azure SQL MCP Server
        self.default_server_url = os.getenv(
            "MCP_SERVER_URL", 
            "https://mcp-azsql-server.mangograss-c63d0418.eastus2.azurecontainerapps.io/mcp"
        )
        
        # Timeout settings
        self.timeout = int(os.getenv("MCP_TIMEOUT", "30"))
        self.retry_attempts = int(os.getenv("MCP_RETRY_ATTEMPTS", "3"))
        self.retry_delay = float(os.getenv("MCP_RETRY_DELAY", "1.0"))
        
        # Connection settings
        self.max_connections = int(os.getenv("MCP_MAX_CONNECTIONS", "10"))
        self.connection_pool_size = int(os.getenv("MCP_POOL_SIZE", "5"))
        
        # Authentication settings
        self.auth_token = os.getenv("MCP_AUTH_TOKEN")
        self.auth_type = os.getenv("MCP_AUTH_TYPE", "bearer")  # bearer, oauth, none
        
        # Transport configuration
        self.transport_type = os.getenv("MCP_TRANSPORT_TYPE", "sse")
        
        # Headers for HTTP requests
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "MACAE-MCP-Client/1.0"
        }
        
        if self.auth_token:
            self.headers["Authorization"] = f"Bearer {self.auth_token}"
    
    def get_server_url(self, server_name: str = "default") -> str:
        """Get server URL by name.
        
        Args:
            server_name: Name of the server (ignored, always returns default)
            
        Returns:
            Server URL
        """
        return self.default_server_url
from typing import Dict, Optional, Any

# Temporarily disable fastmcp due to import conflict with local mcp package
# try:
#     from fastmcp.utilities.mcp_config import MCPConfig as FastMCPConfig, RemoteMCPServer, StdioMCPServer
#     FASTMCP_AVAILABLE = True
# except ImportError:
#     FASTMCP_AVAILABLE = False
#     FastMCPConfig = None
#     RemoteMCPServer = None
#     StdioMCPServer = None

# Temporarily disable fastmcp integration
FASTMCP_AVAILABLE = False
FastMCPConfig = None
RemoteMCPServer = None
StdioMCPServer = None


class MCPConfig:
    """Enhanced configuration for MCP services with fastmcp support."""
    
    def __init__(self):
        """Initialize MCP configuration from environment variables."""
        # Default MCP server URL - Your Azure SQL MCP Server
        self.default_server_url = os.getenv(
            "MCP_SERVER_URL", 
            "https://mcp-azsql-server.mangograss-c63d0418.eastus2.azurecontainerapps.io/mcp"
        )
        
        # Timeout settings
        self.timeout = int(os.getenv("MCP_TIMEOUT", "30"))
        self.retry_attempts = int(os.getenv("MCP_RETRY_ATTEMPTS", "3"))
        self.retry_delay = float(os.getenv("MCP_RETRY_DELAY", "1.0"))
        
        # Connection settings
        self.max_connections = int(os.getenv("MCP_MAX_CONNECTIONS", "10"))
        self.connection_pool_size = int(os.getenv("MCP_POOL_SIZE", "5"))
        
        # Authentication settings
        self.auth_token = os.getenv("MCP_AUTH_TOKEN")
        self.auth_type = os.getenv("MCP_AUTH_TYPE", "bearer")  # bearer, oauth, none
        
        # Transport configuration
        self.transport_type = os.getenv("MCP_TRANSPORT_TYPE", "sse")
        
        # Headers for HTTP requests
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "MACAE-MCP-Client/1.0"
        }
        
        if self.auth_token:
            self.headers["Authorization"] = f"Bearer {self.auth_token}"
    
    def get_server_url(self, server_name: str = "default") -> str:
        """Get server URL by name.
        
        Args:
            server_name: Name of the server configuration
            
        Returns:
            Server URL
        """
        if server_name == "default":
            return self.default_server_url
        return self.servers.get(server_name, self.default_server_url)
    
    def get_auth_config(self) -> Optional[str]:
        """Get authentication configuration for fastmcp."""
        if self.auth_token:
            if self.auth_type == "oauth":
                return "oauth"
            else:
                return self.auth_token
        return None
    
    def to_fastmcp_config(self, server_name: str = "default") -> Optional[Any]:
        """Convert to fastmcp configuration format.
        
        Args:
            server_name: Name of the server to configure
            
        Returns:
            FastMCP configuration object or None if fastmcp not available
        """
        if not FASTMCP_AVAILABLE:
            return None
        
        server_url = self.get_server_url(server_name)
        auth_config = self.get_auth_config()
        
        # Create remote server configuration
        remote_server = RemoteMCPServer(
            url=server_url,
            headers=self.headers,
            auth=auth_config
        )
        
        # Create FastMCP configuration
        config_dict = {
            server_name: remote_server
        }
        
        return FastMCPConfig(mcpServers=config_dict)
    
    def get_connection_config(self) -> Dict[str, Any]:
        """Get connection configuration for enhanced client."""
        return {
            "timeout": self.timeout,
            "retry_attempts": self.retry_attempts,
            "retry_delay": self.retry_delay,
            "max_connections": self.max_connections,
            "pool_size": self.connection_pool_size,
            "headers": self.headers
        }
    
    def create_server_configs(self) -> Dict[str, 'MCPConfig']:
        """Create individual configs for each server."""
        configs = {}
        
        # Default server
        default_config = MCPConfig()
        configs["default"] = default_config
        
        # Individual server configs
        for server_name, server_url in self.servers.items():
            server_config = MCPConfig()
            server_config.default_server_url = server_url
            configs[server_name] = server_config
        
        return configs
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'MCPConfig':
        """Create configuration from dictionary.
        
        Args:
            config_dict: Configuration dictionary
            
        Returns:
            MCPConfig instance
        """
        config = cls()
        
        # Override with provided values
        if "server_url" in config_dict:
            config.default_server_url = config_dict["server_url"]
        
        if "timeout" in config_dict:
            config.timeout = config_dict["timeout"]
        
        if "servers" in config_dict:
            config.servers.update(config_dict["servers"])
        
        if "auth_token" in config_dict:
            config.auth_token = config_dict["auth_token"]
            config.headers["Authorization"] = f"Bearer {config.auth_token}"
        
        if "headers" in config_dict:
            config.headers.update(config_dict["headers"])
        
        return config
    
    def validate(self) -> bool:
        """Validate configuration.
        
        Returns:
            True if configuration is valid
        """
        try:
            # Check if URLs are valid
            from urllib.parse import urlparse
            
            # Validate default server URL
            result = urlparse(self.default_server_url)
            if not all([result.scheme, result.netloc]):
                return False
            
            # Validate server URLs
            for server_name, server_url in self.servers.items():
                result = urlparse(server_url)
                if not all([result.scheme, result.netloc]):
                    return False
            
            # Check timeout values
            if self.timeout <= 0:
                return False
            
            return True
            
        except Exception:
            return False
    
    def get_transport_type(self, server_url: str) -> str:
        """Determine the best transport type for the server URL.
        
        Args:
            server_url: The MCP server URL
            
        Returns:
            Transport type ('sse', 'http', or 'stdio')
        """
        # Your Azure SQL MCP server uses SSE (Server-Sent Events)
        if "mcp-azsql-server.mangograss-c63d0418.eastus2.azurecontainerapps.io" in server_url:
            return "sse"
        elif server_url.startswith(("http://", "https://")):
            return "http"
        else:
            return "stdio"
    
    def get_fastmcp_transport(self, server_name: str = "default"):
        """Get the appropriate fastmcp transport for the server.
        
        Args:
            server_name: Name of the server
            
        Returns:
            Transport instance or server URL string
        """
        server_url = self.get_server_url(server_name)
        transport_type = self.get_transport_type(server_url)
        
        if not FASTMCP_AVAILABLE:
            return server_url
        
        if transport_type == "sse":
            # Use SSE transport for your Azure SQL MCP server
            from fastmcp.client.transports import SSETransport
            return SSETransport(
                url=server_url,
                headers=self.headers,
                timeout=self.timeout
            )
        elif transport_type == "http":
            # Use HTTP transport for other servers
            from fastmcp.client.transports import StreamableHttpTransport
            return StreamableHttpTransport(
                url=server_url,
                headers=self.headers,
                timeout=self.timeout
            )
        else:
            # Return URL for stdio or other transports
            return server_url


# Global configuration instance
mcp_config = MCPConfig()
