"""
STDIO Tool Discovery Strategy.

This module contains the strategy implementation for discovering tools from STDIO servers,
including enhanced support for uvx commands and MCP proxy servers.

Author: Smaran Dhungana <smaran@astha.ai>
Created: 2025-09-14
Last Updated: 2025-09-14
Version: 1.0
Status: Active
"""

import asyncio
import subprocess
import json
import os
import shutil
import logging
from datetime import datetime
from typing import List, Optional, Tuple

from domain.interfaces.tool_discovery_interfaces import IToolDiscoveryStrategy
from domain.dto.tool_enumeration_dtos import (
    ToolDiscoveryMethod,
    ServerTransportType,
    EnumeratedTool,
    ToolSchema,
    ToolParameter,
)
from domain.entities.mcp_config import McpServerConfig

logger = logging.getLogger(__name__)


class StdioToolDiscoveryStrategy(IToolDiscoveryStrategy):
    """Strategy for discovering tools from STDIO servers."""
    
    async def discover_tools(
        self,
        server_name: str,
        server_config: McpServerConfig,
        timeout_seconds: int = 30
    ) -> Tuple[List[EnumeratedTool], List[str], List[str]]:
        """Discover tools from STDIO server by actually running it."""
        tools = []
        errors = []
        warnings = []
        
        if not server_config.command:
            errors.append(f"No command provided for STDIO server: {server_name}")
            return tools, errors, warnings
        
        try:
            logger.info(f"Starting STDIO tool discovery for {server_name}")
            
            # Check if the command is available
            if not shutil.which(server_config.command):
                errors.append(f"Command '{server_config.command}' not found in PATH for server {server_name}")
                return tools, errors, warnings
            
            # Enhanced logging for npx/uvx commands
            if server_config.command in ["npx", "uvx", "uv"]:
                logger.info(f"{server_config.command} command detected for {server_name}, args: {server_config.args}")
                if not server_config.args:
                    errors.append(f"{server_config.command} requires package name as argument for server {server_name}")
                    return tools, errors, warnings
            
            # Prepare environment
            env = os.environ.copy()
            if server_config.env:
                env.update(server_config.env)
            
            # MCP protocol setup
            protocol_version = "2025-06-18"
            
            mcp_init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": protocol_version,
                    "capabilities": {
                        "tools": {},
                        "experimental": {}
                    },
                    "clientInfo": {
                        "name": "astha-tool-enumerator",
                        "version": "1.0.0"
                    }
                }
            }
            
            list_tools_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list"
            }
            
            # Run the STDIO server process
            cmd = [server_config.command] + server_config.args
            logger.info(f"Starting STDIO discovery for {server_name} with command: {' '.join(cmd)}")
            
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                text=True,
                bufsize=1
            )
            
            try:
                # For npx commands, increase timeout as package installation may take time
                if server_config.command == "npx":
                    process_timeout = min(timeout_seconds, 30)  # Allow more time for npx package installation
                    logger.info(f"Increased timeout to {process_timeout}s for npx command")
                else:
                    process_timeout = min(timeout_seconds, 10)
                
                # Give the process a moment to start up
                await asyncio.sleep(0.5)
                
                # Check if process is still running
                if process.poll() is not None:
                    errors.append(f"Process for {server_name} terminated early")
                    return tools, errors, warnings
                
                # Send initialization request
                init_msg = json.dumps(mcp_init_request) + "\n"
                try:
                    process.stdin.write(init_msg)
                    process.stdin.flush()
                except BrokenPipeError:
                    errors.append(f"Broken pipe when initializing {server_name}")
                    return tools, errors, warnings
                
                # Read initialization response
                try:
                    init_response = await asyncio.wait_for(
                        asyncio.to_thread(process.stdout.readline),
                        timeout=process_timeout
                    )
                    if init_response:
                        init_data = json.loads(init_response.strip())
                        if server_config.command in ["uvx", "uv"]:
                            logger.info(f"{server_config.command} server {server_name} init response: {init_data}")
                        else:
                            logger.debug(f"Init response from {server_name}: {init_data}")
                        
                        if "error" in init_data:
                            errors.append(f"Initialization failed for {server_name}: {init_data['error']}")
                            return tools, errors, warnings
                            
                except asyncio.TimeoutError:
                    errors.append(f"Initialization timeout for {server_name}")
                    return tools, errors, warnings
                
                # Send initialized notification
                initialized_notification = {
                    "jsonrpc": "2.0",
                    "method": "notifications/initialized"
                }
                init_notification_msg = json.dumps(initialized_notification) + "\n"
                process.stdin.write(init_notification_msg)
                process.stdin.flush()
                
                # Small delay for MCP protocol compliance
                if server_config.command in ["uvx", "uv"]:
                    await asyncio.sleep(1.0)
                
                # Send tools list request
                tools_msg = json.dumps(list_tools_request) + "\n"
                try:
                    process.stdin.write(tools_msg)
                    process.stdin.flush()
                except BrokenPipeError:
                    errors.append(f"Broken pipe when requesting tools from {server_name}")
                    return tools, errors, warnings
                
                # Read tools response
                try:
                    tools_response = await asyncio.wait_for(
                        asyncio.to_thread(process.stdout.readline),
                        timeout=process_timeout
                    )
                    if tools_response:
                        tools_data = json.loads(tools_response.strip())
                        if server_config.command in ["uvx", "uv"]:
                            logger.info(f"{server_config.command} server {server_name} tools response: {tools_data}")
                        else:
                            logger.debug(f"Tools response from {server_name}: {tools_data}")
                        
                        if "error" in tools_data:
                            error_info = tools_data["error"]
                            error_msg = f"MCP server error {error_info.get('code', 'unknown')}: {error_info.get('message', 'Unknown error')}"
                            if server_config.command in ["uvx", "uv"]:
                                logger.error(f"{server_config.command} server {server_name} returned error: {error_info}")
                            errors.append(error_msg)
                            return tools, errors, warnings
                    else:
                        logger.warning(f"Empty tools response from {server_name}")
                        
                except asyncio.TimeoutError:
                    errors.append(f"Tools list timeout for {server_name}")
                    return tools, errors, warnings
                
                # Parse tools from response
                if tools_response and isinstance(tools_data, dict):
                    tools_list = []
                    
                    if "result" in tools_data:
                        result = tools_data["result"]
                        if isinstance(result, dict) and "tools" in result:
                            tools_list = result["tools"]
                        elif isinstance(result, list):
                            tools_list = result
                    elif "tools" in tools_data:
                        tools_list = tools_data["tools"]
                    elif isinstance(tools_data.get("result"), list):
                        tools_list = tools_data["result"]
                    
                    if tools_list and isinstance(tools_list, list):
                        for tool_data in tools_list:
                            if isinstance(tool_data, dict):
                                tool = EnumeratedTool(
                                    name=tool_data.get("name", f"unknown_tool_{len(tools)}"),
                                    description=tool_data.get("description"),
                                    server_name=server_name,
                                    transport_type=self.get_transport_type(server_config),
                                    input_schema=self._convert_tool_schema(tool_data.get("inputSchema")),
                                    metadata={
                                        "command": server_config.command,
                                        "args": server_config.args,
                                        "env_vars": list(server_config.env.keys()) if server_config.env else [],
                                        "raw_tool_data": tool_data
                                    },
                                    discovery_method=ToolDiscoveryMethod.STDIO_INTROSPECTION,
                                    discovery_timestamp=datetime.utcnow().isoformat(),
                                )
                                tools.append(tool)
                        
                        logger.info(f"Discovered {len(tools)} tools from STDIO server {server_name}")
                    else:
                        if server_config.command in ["uvx", "uv"]:
                            logger.warning(f"{server_config.command} server {server_name}: No tools found in response structure. Full response: {tools_data}")
                        warnings.append(f"No tools found in response from {server_name}")
                else:
                    if server_config.command in ["uvx", "uv"]:
                        logger.warning(f"{server_config.command} server {server_name}: Invalid or empty response")
                    warnings.append(f"No valid tools response received from {server_name}")
                
            except subprocess.TimeoutExpired:
                errors.append(f"STDIO server {server_name} timed out after {timeout_seconds} seconds")
            except json.JSONDecodeError as e:
                errors.append(f"Invalid JSON response from {server_name}: {str(e)}")
            finally:
                try:
                    process.terminate()
                    process.wait(timeout=5)
                except:
                    process.kill()
            
            if not tools and not errors:
                warnings.append(f"STDIO server {server_name}: No tools discovered")
            
        except Exception as e:
            error_msg = f"STDIO discovery failed for {server_name}: {str(e)}"
            
            if server_config.command in ["npx", "uvx", "uv"]:
                if "No module named" in str(e):
                    error_msg += " (Python package may not be available for uvx)"
                elif "command not found" in str(e):
                    error_msg += " (mcp-proxy package may not be installed)"
                elif "Connection refused" in str(e):
                    error_msg += " (Target MCP server may be unreachable)"
                elif "timeout" in str(e).lower():
                    error_msg += " (npx/uvx execution or package installation timed out)"
                elif "Invalid argument" in str(e):
                    error_msg += " (Package may require specific arguments - check package documentation)"
                elif "npm WARN" in str(e):
                    error_msg += " (Package installation warnings - may still work)"
                    
                logger.error(f"{server_config.command} discovery error for {server_name}: {str(e)}")
            
            errors.append(error_msg)
        
        return tools, errors, warnings
    
    def get_transport_type(self, server_config: McpServerConfig) -> ServerTransportType:
        """Determine transport type for STDIO servers."""
        return ServerTransportType.STDIO
    
    def _convert_tool_schema(self, schema_data) -> Optional[ToolSchema]:
        """Convert MCP tool schema to v2 format."""
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