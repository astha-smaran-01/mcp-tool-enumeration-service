"""
Dependency Injection Container for MCP Tool Enumeration Service.

Author: Smaran Dhungana <smaran@astha.ai>
Created: 2025-09-14
Last Updated: 2025-09-14
Version: 1.0
Status: Active
"""

from functools import lru_cache
from typing import Dict

from domain.dto.tool_enumeration_dtos import ToolDiscoveryMethod
from domain.interfaces.tool_discovery_interfaces import IToolDiscoveryStrategy, IToolEnumerationService

# Application Services
from application.services.tool_enumeration_service import ToolEnumerationService
from application.services.tool_enumeration_service.strategies import (
    McpJsonParsingStrategy,
    HttpToolDiscoveryStrategy,
    StdioToolDiscoveryStrategy
)

# Use Cases
from application.use_cases.enumerate_tools import EnumerateToolsUseCase


class Container:
    """Dependency injection container."""
    
    def __init__(self):
        self._strategies = None
        self._tool_enumeration_service = None
        self._enumerate_tools_use_case = None
    
    def strategies(self) -> Dict[ToolDiscoveryMethod, IToolDiscoveryStrategy]:
        """Get tool discovery strategies."""
        if self._strategies is None:
            self._strategies = {
                ToolDiscoveryMethod.MCP_JSON_PARSING: McpJsonParsingStrategy(),
                ToolDiscoveryMethod.HTTP_DISCOVERY: HttpToolDiscoveryStrategy(),
                ToolDiscoveryMethod.STDIO_INTROSPECTION: StdioToolDiscoveryStrategy(),
            }
        return self._strategies
    
    def tool_enumeration_service(self) -> IToolEnumerationService:
        """Get tool enumeration service instance."""
        if self._tool_enumeration_service is None:
            strategies = self.strategies()
            self._tool_enumeration_service = ToolEnumerationService(strategies)
        return self._tool_enumeration_service
    
    def enumerate_tools_use_case(self) -> EnumerateToolsUseCase:
        """Get enumerate tools use case instance."""
        if self._enumerate_tools_use_case is None:
            service = self.tool_enumeration_service()
            self._enumerate_tools_use_case = EnumerateToolsUseCase(service)
        return self._enumerate_tools_use_case


# Global container instance
_container = None


@lru_cache()
def get_container() -> Container:
    """Get global container instance."""
    global _container
    if _container is None:
        _container = Container()
    return _container
