"""
Tool enumeration DTOs for the MCP tool enumeration service.

Author: Smaran Dhungana <smaran@astha.ai>
Created: 2025-09-14
Last Updated: 2025-09-14
Version: 1.0
Status: Active
"""

from typing import Dict, List, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field
from pydantic._internal._model_construction import ModelMetaclass
from datetime import datetime

from domain.entities.mcp_config import McpJsonConfig


class TypeNameMeta(ModelMetaclass):
    """Metaclass to automatically inject __typename field into Pydantic models."""
    
    def __new__(cls, name, bases, namespace, **kwargs):
        # Add __typename field with class name as default
        if '__annotations__' not in namespace:
            namespace['__annotations__'] = {}
        namespace['__annotations__']['model_typename'] = str
        namespace['model_typename'] = Field(name, description="Type identifier", alias="__typename")
        
        return super().__new__(cls, name, bases, namespace, **kwargs)


class ToolDiscoveryMethod(str, Enum):
    """Tool discovery methods."""
    MCP_JSON_PARSING = "mcp_json_parsing"
    HTTP_DISCOVERY = "http_discovery"
    STDIO_INTROSPECTION = "stdio_introspection"
    COMBINED = "combined"


class ServerTransportType(str, Enum):
    """Server transport types."""
    STDIO = "stdio"
    HTTP = "http"
    SSE = "sse"
    WEBSOCKET = "websocket"
    UNKNOWN = "unknown"


class ToolParameter(BaseModel):
    """Tool parameter definition."""
    name: str = Field(..., description="Parameter name")
    type: str = Field(..., description="Parameter type")
    description: Optional[str] = Field(None, description="Parameter description")
    required: bool = Field(False, description="Whether parameter is required")
    default: Optional[Any] = Field(None, description="Default value")
    enum: Optional[List[Any]] = Field(None, description="Allowed values")


class ToolSchema(BaseModel):
    """Tool schema definition."""
    type: str = Field("object", description="Schema type")
    properties: Dict[str, ToolParameter] = Field(default_factory=dict, description="Tool parameters")
    required: List[str] = Field(default_factory=list, description="Required parameters")
    additionalProperties: bool = Field(False, description="Allow additional properties")


class EnumeratedTool(BaseModel, metaclass=TypeNameMeta):
    """Enumerated tool information."""
    name: str = Field(..., description="Tool name")
    description: Optional[str] = Field(None, description="Tool description")
    server_name: str = Field(..., description="Source server name")
    transport_type: ServerTransportType = Field(..., description="Server transport type")
    input_schema: Optional[ToolSchema] = Field(None, description="Tool input schema")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional tool metadata")
    discovery_method: ToolDiscoveryMethod = Field(..., description="How the tool was discovered")
    discovery_timestamp: str = Field(..., description="When the tool was discovered")


class ServerEnumerationResult(BaseModel):
    """Server enumeration result."""
    server_name: str = Field(..., description="Server name")
    transport_type: ServerTransportType = Field(..., description="Transport type")
    server_url: Optional[str] = Field(None, description="Extracted server URL")
    command: Optional[str] = Field(None, description="Command for STDIO servers")
    tools: List[EnumeratedTool] = Field(default_factory=list, description="Discovered tools")
    errors: List[str] = Field(default_factory=list, description="Discovery errors")
    warnings: List[str] = Field(default_factory=list, description="Discovery warnings")
    discovery_duration_ms: Optional[int] = Field(None, description="Discovery duration in milliseconds")


class ServerResult(BaseModel, metaclass=TypeNameMeta):
    """Server enumeration result (simplified format matching Astha AI standard)."""
    name: str = Field(..., description="Server name")
    status: str = Field(..., description="Connection status (connected/error)")
    tool_count: int = Field(..., description="Number of tools discovered")
    error: Optional[str] = Field(None, description="Error message if discovery failed")


class SimplifiedTool(BaseModel, metaclass=TypeNameMeta):
    """Simplified tool format matching Astha AI standard."""
    server: str = Field(..., description="Server name")
    name: str = Field(..., description="Tool name")
    description: Optional[str] = Field(None, description="Tool description")
    inputSchema: Optional[Dict[str, Any]] = Field(None, description="Tool input schema")


class ToolEnumerationRequest(BaseModel):
    """Tool enumeration request."""
    mcp_json: McpJsonConfig = Field(
        ..., 
        description="MCP JSON configuration to enumerate tools from",
        examples=[
            {
                "mcpServers": {
                    "aws-knowledge-mcp-server": {
                        "url": "https://knowledge-mcp.global.api.aws"
                    }
                }
            },
            {
                "mcpServers": {
                    "info-bib-2fa": {
                        "url": "https://mcp.infobip.com/2fa"
                    }
                }
            },
            {
                "mcpServers": {
                    "paypal": {
                        "command": "npx",
                        "args": ["-y", "@paypal/mcp", "--tools=all"],
                        "env": {
                            "PAYPAL_ACCESS_TOKEN": "YOUR_PAYPAL_ACCESS_TOKEN",
                            "PAYPAL_ENVIRONMENT": "SANDBOX"
                        }
                    }
                }
            },
            {
                "mcpServers": {
                    "paypal-mcp-server": {
                        "command": "npx",
                        "args": [
                            "mcp-remote",
                            "https://mcp.sandbox.paypal.com/sse",
                            "--header",
                            "Authorization: Bearer <auth_header>"
                        ]
                    }
                }
            }
        ]
    )
    timeout_seconds: int = Field(
        30, 
        description="Timeout for each server discovery", 
        ge=5, 
        le=300
    )
    include_schemas: bool = Field(
        True, 
        description="Whether to include tool input schemas"
    )
    parallel_discovery: bool = Field(
        True, 
        description="Whether to discover tools from multiple servers in parallel"
    )


class ToolEnumerationResponse(BaseModel, metaclass=TypeNameMeta):
    """Tool enumeration response following Astha AI standard format."""
    status: str = Field(..., description="Overall enumeration status")
    message: str = Field(..., description="Status message")
    timestamp: str = Field(..., description="Response timestamp")
    servers: List[ServerResult] = Field(default_factory=list, description="Server results")
    tools: List[SimplifiedTool] = Field(default_factory=list, description="All discovered tools")
    total_servers: int = Field(..., description="Total number of servers")
    connected_servers: int = Field(..., description="Number of successfully connected servers")