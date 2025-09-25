"""
Tool Enumeration Service.

This module contains the main service class for enumerating and discovering tools
from MCP JSON configurations following SOLID principles and clean architecture.

Author: Smaran Dhungana <smaran@astha.ai>
Created: 2025-09-14
Last Updated: 2025-09-14
Version: 1.0
Status: Active
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

from src.domain.dto.tool_enumeration_dtos import (
    ToolDiscoveryMethod,
    ServerTransportType,
    EnumeratedTool,
    ServerEnumerationResult,
    ToolEnumerationResponse,
    ServerResult,
    SimplifiedTool
)
from src.domain.entities.mcp_config import McpJsonConfig, McpServerConfig
from src.domain.interfaces.tool_discovery_interfaces import IToolDiscoveryStrategy, IToolEnumerationService

from .strategies import (
    HttpToolDiscoveryStrategy,
    StdioToolDiscoveryStrategy,
    McpJsonParsingStrategy
)

logger = logging.getLogger(__name__)


class ToolEnumerationService(IToolEnumerationService):
    """
    Service for enumerating tools from MCP JSON configurations.
    
    Follows SOLID principles:
    - Single Responsibility: Only handles tool enumeration
    - Open/Closed: Extensible via strategy pattern
    - Liskov Substitution: Strategies are interchangeable
    - Interface Segregation: Small, focused interfaces
    - Dependency Inversion: Depends on abstractions
    """
    
    def __init__(self, strategies: Dict[ToolDiscoveryMethod, IToolDiscoveryStrategy]):
        """Initialize with strategy dictionary."""
        self._strategies = strategies
        logger.info("Tool Enumeration Service initialized with SOLID principles")
    
    async def enumerate_tools(
        self,
        request
    ) -> ToolEnumerationResponse:
        """
        Enumerate tools from tool enumeration request.
        
        Discovery method is automatically selected based on server type:
        - HTTP/SSE servers (with url) → HTTP discovery
        - STDIO servers (with command) → STDIO introspection  
        - Others → MCP JSON parsing fallback
        
        Args:
            request: Tool enumeration request containing MCP JSON config
            
        Returns:
            Tool enumeration response with all discovered tools
        """
        mcp_json = request.mcp_json
        timeout_seconds = request.timeout_seconds
        include_schemas = request.include_schemas
        parallel_discovery = request.parallel_discovery
        
        logger.info(
            "Starting smart tool enumeration: server_count=%d, parallel=%s",
            len(mcp_json.mcpServers),
            parallel_discovery
        )
        
        servers = []
        all_tools = []
        global_errors = []
        global_warnings = []
        
        try:
            if parallel_discovery:
                # Process servers in parallel
                tasks = [
                    self._enumerate_server_tools(
                        server_name, 
                        server_config, 
                        timeout_seconds,
                        include_schemas
                    )
                    for server_name, server_config in mcp_json.mcpServers.items()
                ]
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        server_name = list(mcp_json.mcpServers.keys())[i]
                        global_errors.append(f"Server {server_name} enumeration failed: {str(result)}")
                    else:
                        servers.append(result)
                        all_tools.extend(result.tools)
            else:
                # Process servers sequentially
                for server_name, server_config in mcp_json.mcpServers.items():
                    try:
                        result = await self._enumerate_server_tools(
                            server_name, 
                            server_config, 
                            timeout_seconds,
                            include_schemas
                        )
                        servers.append(result)
                        all_tools.extend(result.tools)
                    except Exception as e:
                        global_errors.append(f"Server {server_name} enumeration failed: {str(e)}")
            
            # Convert to simplified format matching reference API
            simplified_servers = []
            simplified_tools = []
            connected_count = 0
            
            for server in servers:
                # Create simplified server result
                server_status = "connected" if not server.errors else "error"
                if server_status == "connected":
                    connected_count += 1
                
                simplified_server = ServerResult(
                    name=server.server_name,
                    status=server_status,
                    tool_count=len(server.tools),
                    error=server.errors[0] if server.errors else None
                )
                simplified_servers.append(simplified_server)
                
                # Convert tools to simplified format
                for tool in server.tools:
                    simplified_tool = SimplifiedTool(
                        server=server.server_name,
                        name=tool.name,
                        description=tool.description,
                        inputSchema=tool.input_schema.dict() if tool.input_schema else None
                    )
                    simplified_tools.append(simplified_tool)
            
            # Determine overall status
            overall_status = "success" if connected_count > 0 else "error"
            message = f"Successfully connected to all {connected_count} servers" if connected_count == len(mcp_json.mcpServers) else f"Connected to {connected_count} of {len(mcp_json.mcpServers)} servers"
            
            response = ToolEnumerationResponse(
                status=overall_status,
                message=message,
                timestamp=datetime.utcnow().isoformat(),
                servers=simplified_servers,
                tools=simplified_tools,
                total_servers=len(mcp_json.mcpServers),
                connected_servers=connected_count
            )
            
            logger.info(
                f"Tool enumeration completed: total_servers={response.total_servers}, "
                f"connected_servers={response.connected_servers}, total_tools={len(response.tools)}"
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Tool enumeration failed: {str(e)}")
            raise
    
    async def _enumerate_server_tools(
        self,
        server_name: str,
        server_config: McpServerConfig,
        timeout_seconds: int,
        include_schemas: bool
    ) -> ServerEnumerationResult:
        """Enumerate tools from a single server."""
        start_time = datetime.utcnow()
        
        try:
            # Automatically select appropriate strategy based on server type
            strategy = self._auto_select_strategy(server_config)
            
            logger.info(f"Auto-selected {strategy.__class__.__name__} for {server_name}")
            
            # Discover tools using selected strategy
            tools, errors, warnings = await asyncio.wait_for(
                strategy.discover_tools(server_name, server_config, timeout_seconds),
                timeout=timeout_seconds
            )
            
            # Filter out schemas if not requested
            if not include_schemas:
                for tool in tools:
                    tool.input_schema = None
            
            # Calculate discovery duration
            end_time = datetime.utcnow()
            duration_ms = int((end_time - start_time).total_seconds() * 1000)
            
            # Extract server URL for result
            server_url = self._extract_server_url(server_config)
            
            return ServerEnumerationResult(
                server_name=server_name,
                transport_type=strategy.get_transport_type(server_config),
                server_url=server_url,
                command=server_config.command,
                tools=tools,
                errors=errors,
                warnings=warnings,
                discovery_duration_ms=duration_ms
            )
            
        except asyncio.TimeoutError:
            return ServerEnumerationResult(
                server_name=server_name,
                transport_type=ServerTransportType.UNKNOWN,
                server_url=self._extract_server_url(server_config),
                command=server_config.command,
                tools=[],
                errors=[f"Discovery timeout after {timeout_seconds} seconds"],
                warnings=[],
                discovery_duration_ms=timeout_seconds * 1000
            )
        except Exception as e:
            return ServerEnumerationResult(
                server_name=server_name,
                transport_type=ServerTransportType.UNKNOWN,
                server_url=self._extract_server_url(server_config),
                command=server_config.command,
                tools=[],
                errors=[f"Discovery failed: {str(e)}"],
                warnings=[],
                discovery_duration_ms=0
            )
    
    def _auto_select_strategy(self, server_config: McpServerConfig) -> IToolDiscoveryStrategy:
        """
        Automatically select the best discovery strategy based on server configuration.
        
        Selection logic:
        - If server has URL → HTTP discovery (can discover tools via API)
        - If server has command → STDIO introspection (can run and discover tools)
        - Otherwise → MCP JSON parsing (fallback for metadata-only)
        """
        if server_config.url:
            logger.debug("Selected HTTP discovery strategy (server has URL)")
            return self._strategies[ToolDiscoveryMethod.HTTP_DISCOVERY]
        elif server_config.command:
            logger.debug("Selected STDIO introspection strategy (server has command)")
            return self._strategies[ToolDiscoveryMethod.STDIO_INTROSPECTION]
        else:
            logger.debug("Selected MCP JSON parsing strategy (fallback)")
            return self._strategies[ToolDiscoveryMethod.MCP_JSON_PARSING]
    
    def _extract_server_url(self, server_config: McpServerConfig) -> Optional[str]:
        """Extract server URL using multiple methods."""
        # Method 1: Direct URL field
        if server_config.url:
            return server_config.url
        
        # Method 2: Parse from args
        if server_config.command and server_config.args:
            for arg in server_config.args:
                if isinstance(arg, str) and (arg.startswith('https://') or arg.startswith('http://')):
                    return arg
        
        return None
    
    def _generate_discovery_summary(
        self, 
        servers: List[ServerEnumerationResult], 
        all_tools: List[EnumeratedTool]
    ) -> Dict[str, Any]:
        """Generate discovery summary statistics."""
        transport_counts = {}
        method_counts = {}
        total_duration = 0
        
        for server in servers:
            # Count by transport type
            transport_type = server.transport_type.value
            transport_counts[transport_type] = transport_counts.get(transport_type, 0) + 1
            
            # Count by discovery method
            for tool in server.tools:
                method = tool.discovery_method.value
                method_counts[method] = method_counts.get(method, 0) + 1
            
            # Sum durations
            if server.discovery_duration_ms:
                total_duration += server.discovery_duration_ms
        
        return {
            "transport_types": transport_counts,
            "discovery_methods": method_counts,
            "total_discovery_duration_ms": total_duration,
            "average_duration_per_server_ms": total_duration // len(servers) if servers else 0,
            "servers_with_errors": len([s for s in servers if s.errors]),
            "servers_with_warnings": len([s for s in servers if s.warnings]),
            "tools_per_server": {s.server_name: len(s.tools) for s in servers}
        }