"""
HTTP Tool Discovery Strategy.

This module contains the strategy implementation for discovering tools from HTTP/SSE servers
using multiple HTTP discovery methods.

Author: Smaran Dhungana <smaran@astha.ai>
Created: 2025-09-14
Last Updated: 2025-09-14
Version: 1.0
Status: Active
"""

import logging
import httpx
from datetime import datetime
from typing import List, Optional, Tuple

from src.domain.interfaces.tool_discovery_interfaces import IToolDiscoveryStrategy
from src.domain.dto.tool_enumeration_dtos import (
    ToolDiscoveryMethod,
    ServerTransportType,
    EnumeratedTool,
    ToolSchema,
    ToolParameter,
)
from src.domain.entities.mcp_config import McpServerConfig

logger = logging.getLogger(__name__)


class HttpToolDiscoveryStrategy(IToolDiscoveryStrategy):
    """Strategy for discovering tools from HTTP/SSE servers using multiple HTTP methods."""
    
    def __init__(self):
        # HTTP discovery methods in order of preference
        self.discovery_methods = [
            self._discover_public_info,
            self._discover_mcp_jsonrpc,
            self._discover_rest_api,
        ]
    
    async def discover_tools(
        self,
        server_name: str,
        server_config: McpServerConfig,
        timeout_seconds: int = 30
    ) -> Tuple[List[EnumeratedTool], List[str], List[str]]:
        """Discover tools from HTTP/SSE server using multiple methods."""
        tools = []
        errors = []
        warnings = []
        
        if not server_config.url:
            errors.append(f"No URL provided for HTTP server: {server_name}")
            return tools, errors, warnings
        
        try:
            headers = {"Content-Type": "application/json"}
            if server_config.headers:
                headers.update(server_config.headers)
            
            async with httpx.AsyncClient(
                timeout=timeout_seconds, 
                follow_redirects=True
            ) as client:
                
                for method in self.discovery_methods:
                    try:
                        method_tools = await method(client, server_config.url, headers, server_name)
                        if method_tools:
                            tools.extend(method_tools)
                            logger.info(f"Discovered {len(method_tools)} tools from HTTP server {server_name} using {method.__name__}")
                            break
                    except Exception as e:
                        errors.append(f"{method.__name__}: {str(e)}")
                        continue
                
                if not tools and not errors:
                    warnings.append(f"No tools discovered from HTTP server {server_name} using any method")
            
            logger.info(f"HTTP discovery completed for {server_name}, found {len(tools)} tools")
            
        except Exception as e:
            errors.append(f"HTTP discovery failed for {server_name}: {str(e)}")
            logger.error(f"HTTP discovery failed for {server_name}: {str(e)}")
        
        return tools, errors, warnings
    
    def get_transport_type(self, server_config: McpServerConfig) -> ServerTransportType:
        """Determine transport type for HTTP servers."""
        return ServerTransportType.HTTP
    
    async def _discover_public_info(self, client, server_url: str, headers: dict, server_name: str) -> List[EnumeratedTool]:
        """Discover tools from public information endpoints."""
        tools = []
        endpoints = ["/info", "/.well-known/mcp", "/api/info", "/"][::-1]
        
        for endpoint in endpoints:
            try:
                url = f"{server_url.rstrip('/')}{endpoint}"
                response = await client.get(url, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    logger.debug(f"Public info response from {server_name} at {endpoint}: {data}")
                    
                    tools_data = data
                    if isinstance(data, dict):
                        tools_data = data.get("tools", data.get("data", []))
                    
                    for i, tool_data in enumerate(tools_data):
                        if isinstance(tool_data, dict):
                            # Handle nested tool structure: {tool_name: {name: ..., description: ...}}
                            if len(tool_data) == 1 and not any(key in tool_data for key in ["name", "description", "inSchema", "inputSchema"]):
                                # This is a nested structure - extract the tool details
                                tool_name = list(tool_data.keys())[0]
                                tool_details = tool_data[tool_name]
                                if isinstance(tool_details, dict):
                                    actual_name = tool_details.get("name", tool_name)
                                    description = tool_details.get("description")
                                    schema_data = tool_details.get("inSchema", tool_details.get("inputSchema", tool_details.get("schema")))
                                else:
                                    actual_name = tool_name
                                    description = None
                                    schema_data = None
                            else:
                                # This is a flat structure
                                tool_name = tool_data.get("name")
                                if not tool_name:
                                    tool_name = tool_data.get("id", tool_data.get("tool_name", f"tool_{i}"))
                                actual_name = tool_name
                                description = tool_data.get("description", tool_data.get("summary"))
                                schema_data = tool_data.get("inputSchema", tool_data.get("inSchema", tool_data.get("schema")))
                            
                            tool = EnumeratedTool(
                                name=actual_name,
                                description=description,
                                server_name=server_name,
                                transport_type=ServerTransportType.HTTP,
                                input_schema=self._convert_tool_schema(schema_data),
                                metadata={
                                    "source_url": server_url,
                                    "endpoint": endpoint,
                                    "protocol": "public-info",
                                    "raw_tool_data": tool_data
                                },
                                discovery_method=ToolDiscoveryMethod.HTTP_DISCOVERY,
                                discovery_timestamp=datetime.utcnow().isoformat(),
                            )
                            tools.append(tool)
                    
                    if tools:
                        logger.info(f"Found {len(tools)} tools from public info endpoint {endpoint}")
                        return tools
            except Exception as e:
                logger.debug(f"Public info discovery failed at {endpoint}: {e}")
                continue
        
        if not tools:
            raise Exception("No valid public info endpoints found")
        return tools
    
    async def _discover_mcp_jsonrpc(self, client, server_url: str, headers: dict, server_name: str) -> List[EnumeratedTool]:
        """Discover tools using MCP JSON-RPC protocol over HTTP."""
        tools = []
        
        # Initialize MCP session
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "astha-tool-enumerator",
                    "version": "1.0.0",
                },
            },
        }
        
        response = await client.post(server_url, json=init_request, headers=headers)
        response.raise_for_status()
        
        init_result = response.json()
        logger.debug(f"MCP init response from {server_name}: {init_result}")
        
        if "error" in init_result:
            raise Exception(f"MCP initialization failed: {init_result['error']}")
        
        # List tools
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
        }
        
        response = await client.post(server_url, json=tools_request, headers=headers)
        response.raise_for_status()
        
        tools_result = response.json()
        logger.debug(f"MCP tools response from {server_name}: {tools_result}")
        
        if "error" in tools_result:
            raise Exception(f"Tools list failed: {tools_result['error']}")
        
        # Parse tools from result
        tools_data = tools_result.get("result", {}).get("tools", [])
        for i, tool_data in enumerate(tools_data):
            if isinstance(tool_data, dict):
                # Handle nested tool structure: {tool_name: {name: ..., description: ...}}
                if len(tool_data) == 1 and not any(key in tool_data for key in ["name", "description", "inSchema", "inputSchema"]):
                    # This is a nested structure - extract the tool details
                    tool_name = list(tool_data.keys())[0]
                    tool_details = tool_data[tool_name]
                    if isinstance(tool_details, dict):
                        actual_name = tool_details.get("name", tool_name)
                        description = tool_details.get("description")
                        schema_data = tool_details.get("inSchema", tool_details.get("inputSchema", tool_details.get("schema")))
                    else:
                        actual_name = tool_name
                        description = None
                        schema_data = None
                else:
                    # This is a flat structure
                    tool_name = tool_data.get("name")
                    if not tool_name:
                        tool_name = tool_data.get("id", tool_data.get("tool_name", f"tool_{i}"))
                    actual_name = tool_name
                    description = tool_data.get("description", tool_data.get("summary"))
                    schema_data = tool_data.get("inputSchema", tool_data.get("inSchema", tool_data.get("schema")))
                
                tool = EnumeratedTool(
                    name=actual_name,
                    description=description,
                    server_name=server_name,
                    transport_type=ServerTransportType.HTTP,
                    input_schema=self._convert_tool_schema(schema_data),
                    metadata={
                        "source_url": server_url,
                        "protocol": "mcp-jsonrpc",
                        "raw_tool_data": tool_data
                    },
                    discovery_method=ToolDiscoveryMethod.HTTP_DISCOVERY,
                    discovery_timestamp=datetime.utcnow().isoformat(),
                )
                tools.append(tool)
        
        logger.info(f"Found {len(tools)} tools from MCP JSON-RPC")
        return tools
    
    async def _discover_rest_api(self, client, server_url: str, headers: dict, server_name: str) -> List[EnumeratedTool]:
        """Discover tools using REST API endpoints."""
        tools = []
        endpoints = ["/tools", "/api/tools", "/v1/tools", "/mcp/tools"]
        
        for endpoint in endpoints:
            try:
                url = f"{server_url.rstrip('/')}{endpoint}"
                response = await client.get(url, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    logger.debug(f"REST API response from {server_name} at {endpoint}: {data}")
                    
                    tools_data = data
                    if isinstance(data, dict):
                        tools_data = data.get("tools", data.get("data", []))
                    
                    for i, tool_data in enumerate(tools_data):
                        if isinstance(tool_data, dict):
                            # Handle nested tool structure: {tool_name: {name: ..., description: ...}}
                            if len(tool_data) == 1 and not any(key in tool_data for key in ["name", "description", "inSchema", "inputSchema"]):
                                # This is a nested structure - extract the tool details
                                tool_name = list(tool_data.keys())[0]
                                tool_details = tool_data[tool_name]
                                if isinstance(tool_details, dict):
                                    actual_name = tool_details.get("name", tool_name)
                                    description = tool_details.get("description")
                                    schema_data = tool_details.get("inSchema", tool_details.get("inputSchema", tool_details.get("schema")))
                                else:
                                    actual_name = tool_name
                                    description = None
                                    schema_data = None
                            else:
                                # This is a flat structure
                                tool_name = tool_data.get("name")
                                if not tool_name:
                                    tool_name = tool_data.get("id", tool_data.get("tool_name", f"tool_{i}"))
                                actual_name = tool_name
                                description = tool_data.get("description", tool_data.get("summary"))
                                schema_data = tool_data.get("inputSchema", tool_data.get("inSchema", tool_data.get("schema")))
                            
                            tool = EnumeratedTool(
                                name=actual_name,
                                description=description,
                                server_name=server_name,
                                transport_type=ServerTransportType.HTTP,
                                input_schema=self._convert_tool_schema(schema_data),
                                metadata={
                                    "source_url": server_url,
                                    "endpoint": endpoint,
                                    "protocol": "rest-api",
                                    "raw_tool_data": tool_data
                                },
                                discovery_method=ToolDiscoveryMethod.HTTP_DISCOVERY,
                                discovery_timestamp=datetime.utcnow().isoformat(),
                            )
                            tools.append(tool)
                    
                    if tools:
                        logger.info(f"Found {len(tools)} tools from REST API endpoint {endpoint}")
                        return tools
            except Exception as e:
                logger.debug(f"REST API discovery failed at {endpoint}: {e}")
                continue
        
        if not tools:
            raise Exception("No valid REST API endpoints found")
        return tools
    
    def _convert_tool_schema(self, schema_data) -> Optional[ToolSchema]:
        """Convert MCP tool schema to our format."""
        if not schema_data:
            return None
        
        try:
            if isinstance(schema_data, dict):
                properties = {}
                for prop_name, prop_data in schema_data.get('properties', {}).items():
                    properties[prop_name] = ToolParameter(
                        name=prop_name,
                        type=prop_data.get('type', 'string'),
                        description=prop_data.get('description'),
                        required=prop_name in schema_data.get('required', []),
                        default=prop_data.get('default'),
                        enum=prop_data.get('enum')
                    )
                
                return ToolSchema(
                    type=schema_data.get('type', 'object'),
                    properties=properties,
                    required=schema_data.get('required', []),
                    additionalProperties=schema_data.get('additionalProperties', False)
                )
        except Exception as e:
            logger.warning(f"Failed to convert tool schema: {e}")
        
        return None