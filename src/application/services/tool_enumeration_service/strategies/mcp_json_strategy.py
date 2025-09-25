"""
MCP JSON Parsing Strategy.

This module contains the strategy implementation for parsing tools directly from 
MCP JSON configuration metadata when direct discovery is not possible.

Author: Smaran Dhungana <smaran@astha.ai>
Created: 2025-09-14
Last Updated: 2025-09-14
Version: 1.0
Status: Active
"""

import logging
from datetime import datetime
from typing import List, Optional, Tuple

from src.domain.interfaces.tool_discovery_interfaces import IToolDiscoveryStrategy
from src.domain.dto.tool_enumeration_dtos import (
    ToolDiscoveryMethod,
    ServerTransportType,
    EnumeratedTool,
)
from src.domain.entities.mcp_config import McpServerConfig

logger = logging.getLogger(__name__)


class McpJsonParsingStrategy(IToolDiscoveryStrategy):
    """Strategy for parsing tools from MCP JSON configuration as fallback."""
    
    async def discover_tools(
        self,
        server_name: str,
        server_config: McpServerConfig,
        timeout_seconds: int = 30
    ) -> Tuple[List[EnumeratedTool], List[str], List[str]]:
        """Parse tools from MCP JSON metadata if available."""
        tools = []
        errors = []
        warnings = []
        
        try:
            server_url = self._extract_server_url(server_config)
            
            # Create a basic tool entry based on server configuration
            basic_tool = EnumeratedTool(
                name=f"{server_name}_config",
                description=f"Configuration-based tool for {server_name}",
                server_name=server_name,
                transport_type=self.get_transport_type(server_config),
                input_schema=None,
                metadata={
                    "source": "mcp_json_config",
                    "command": server_config.command,
                    "url": server_url,
                    "args": server_config.args,
                    "env": server_config.env,
                    "note": "Fallback tool created from MCP JSON configuration"
                },
                discovery_method=ToolDiscoveryMethod.MCP_JSON_PARSING,
                discovery_timestamp=datetime.utcnow().isoformat(),
            )
            tools.append(basic_tool)
            
            warnings.append(f"Created fallback tool from MCP JSON config for {server_name}")
            logger.info(f"Created fallback tool from MCP JSON config for {server_name}")
            
        except Exception as e:
            errors.append(f"MCP JSON parsing failed for {server_name}: {str(e)}")
            logger.error(f"MCP JSON parsing failed for {server_name}: {str(e)}")
        
        return tools, errors, warnings
    
    def get_transport_type(self, server_config: McpServerConfig) -> ServerTransportType:
        """Determine transport type based on server configuration."""
        if server_config.url:
            return ServerTransportType.HTTP
        elif server_config.command:
            return ServerTransportType.STDIO
        return ServerTransportType.UNKNOWN
    
    def _extract_server_url(self, server_config: McpServerConfig) -> Optional[str]:
        """Extract server URL using multiple methods."""
        if server_config.url:
            return server_config.url
        
        if server_config.command and server_config.args:
            for arg in server_config.args:
                if isinstance(arg, str) and (arg.startswith('https://') or arg.startswith('http://')):
                    return arg
        
        return None