"""
MCP Configuration domain entities.

Author: Smaran Dhungana <smaran@astha.ai>
Created: 2025-09-14
Last Updated: 2025-09-14
Version: 1.0
Status: Active
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class McpServerConfig(BaseModel):
    """MCP server configuration."""
    command: Optional[str] = Field(None, description="Command to run the server")
    args: Optional[List[str]] = Field(None, description="Command arguments")
    env: Optional[Dict[str, str]] = Field(None, description="Environment variables")
    url: Optional[str] = Field(None, description="Server URL for HTTP/SSE connections")
    headers: Optional[Dict[str, str]] = Field(None, description="HTTP headers")
    timeout: Optional[int] = Field(30, description="Connection timeout in seconds")


class McpJsonConfig(BaseModel):
    """MCP JSON configuration containing multiple servers."""
    mcpServers: Dict[str, McpServerConfig] = Field(
        ..., description="Dictionary of server name to server configuration"
    )


class McpTool(BaseModel):
    """MCP tool representation."""
    name: str = Field(..., description="Tool name")
    description: Optional[str] = Field(None, description="Tool description")
    input_schema: Optional[Dict[str, Any]] = Field(None, description="Tool input schema")
    
    class Config:
        extra = "allow"