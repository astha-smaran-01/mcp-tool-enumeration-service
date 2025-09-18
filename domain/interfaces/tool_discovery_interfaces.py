"""
Tool discovery interfaces for the MCP tool enumeration service.

Author: Smaran Dhungana <smaran@astha.ai>
Created: 2025-09-14
Last Updated: 2025-09-14
Version: 1.0
Status: Active
"""

from abc import ABC, abstractmethod
from typing import List, Tuple

from domain.dto.tool_enumeration_dtos import (
    EnumeratedTool, 
    ServerTransportType,
    ToolEnumerationRequest,
    ToolEnumerationResponse
)
from domain.entities.mcp_config import McpServerConfig, McpJsonConfig


class IToolDiscoveryStrategy(ABC):
    """Interface for tool discovery strategies (Strategy Pattern)."""
    
    @abstractmethod
    async def discover_tools(
        self,
        server_name: str,
        server_config: McpServerConfig,
        timeout_seconds: int = 30
    ) -> Tuple[List[EnumeratedTool], List[str], List[str]]:
        """
        Discover tools from a server configuration.
        
        Returns:
            Tuple of (tools, errors, warnings)
        """
        pass
    
    @abstractmethod
    def get_transport_type(self, server_config: McpServerConfig) -> ServerTransportType:
        """Get the transport type for the server configuration."""
        pass


class IToolEnumerationService(ABC):
    """Interface for tool enumeration service."""
    
    @abstractmethod
    async def enumerate_tools(
        self,
        request: ToolEnumerationRequest
    ) -> ToolEnumerationResponse:
        """Enumerate tools from MCP JSON configuration."""
        pass