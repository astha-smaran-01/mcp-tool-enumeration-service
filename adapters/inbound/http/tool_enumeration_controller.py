"""
Tool Enumeration HTTP Controller.

Author: Smaran Dhungana <smaran@astha.ai>
Created: 2025-09-14
Last Updated: 2025-09-14
Version: 1.0
Status: Active
"""

import logging
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any

from application.use_cases.enumerate_tools import EnumerateToolsUseCase
from domain.dto.tool_enumeration_dtos import ToolEnumerationRequest, ToolEnumerationResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/tools", tags=["Tool Enumeration"])


def get_enumerate_tools_use_case() -> EnumerateToolsUseCase:
    """Dependency injection for enumerate tools use case."""
    # This will be properly injected via container
    from app.container import get_container
    container = get_container()
    return container.enumerate_tools_use_case()


@router.post("/enumerate", response_model=Dict[str, Any])
async def enumerate_tools(
    request: ToolEnumerationRequest,
    use_case: EnumerateToolsUseCase = Depends(get_enumerate_tools_use_case)
) -> Dict[str, Any]:
    """
    Enumerate tools from MCP JSON configuration.
    
    This endpoint accepts MCP JSON configuration and returns all discovered tools
    from the configured servers using appropriate discovery strategies.
    
    ## Example Configurations:
    
    ### AWS Knowledge MCP Server (HTTP):
    ```json
    {
        "mcp_json": {
            "mcpServers": {
                "aws-knowledge-mcp-server": {
                    "url": "https://knowledge-mcp.global.api.aws"
                }
            }
        }
    }
    ```
    
    ### Infobip 2FA (HTTP):
    ```json
    {
        "mcp_json": {
            "mcpServers": {
                "info-bib-2fa": {
                    "url": "https://mcp.infobip.com/2fa"
                }
            }
        }
    }
    ```
    
    ### PayPal NPX (STDIO with Environment):
    ```json
    {
        "mcp_json": {
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
        }
    }
    ```
    
    ### PayPal Remote (STDIO with Remote Connection):
    ```json
    {
        "mcp_json": {
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
    }
    ```
    """
    try:
        logger.info(f"Received tool enumeration request: {request.model_dump_json()}")
        
        response = await use_case.execute(request)
        
        # Return in Astha AI standard format
        return {
            "success": True if response.status == "success" else False,
            "message": response.message,
            "data": {
                "__typename": response.model_typename,
                "status": response.status,
                "timestamp": response.timestamp,
                "servers": [server.model_dump() for server in response.servers],
                "tools": [tool.model_dump() for tool in response.tools],
                "total_servers": response.total_servers,
                "connected_servers": response.connected_servers
            }
        }
        
    except Exception as e:
        logger.error(f"Tool enumeration failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "status": 500,
                "success": False,
                "message": "Tool enumeration failed",
                "data": {
                    "message": "Tool enumeration failed",
                    "error": str(e),
                    "error_code": "TOOL_ENUMERATION_ERROR"
                }
            }
        )



@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint."""
    return {
        "success": True,
        "message": "MCP Tool Enumeration Service is healthy",
        "data": {
            "__typename": "HealthCheck",
            "service": "mcp-tool-enumeration-service",
            "version": "1.0.0",
            "status": "healthy"
        }
    }