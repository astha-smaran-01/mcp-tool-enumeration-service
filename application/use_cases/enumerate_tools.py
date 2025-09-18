"""
Enumerate Tools Use Case.

Author: Smaran Dhungana <smaran@astha.ai>
Created: 2025-09-14
Last Updated: 2025-09-14
Version: 1.0
Status: Active
"""

import logging
from domain.interfaces.tool_discovery_interfaces import IToolEnumerationService
from domain.dto.tool_enumeration_dtos import ToolEnumerationRequest, ToolEnumerationResponse

logger = logging.getLogger(__name__)


class EnumerateToolsUseCase:
    """Use case for enumerating tools from MCP JSON configuration."""
    
    def __init__(self, tool_enumeration_service: IToolEnumerationService):
        self.tool_enumeration_service = tool_enumeration_service
    
    async def execute(self, request: ToolEnumerationRequest) -> ToolEnumerationResponse:
        """Execute the tool enumeration use case."""
        logger.info("Executing enumerate tools use case")
        
        try:
            response = await self.tool_enumeration_service.enumerate_tools(request)
            logger.info("Tool enumeration use case completed successfully")
            return response
        except Exception as e:
            logger.error(f"Tool enumeration use case failed: {str(e)}")
            raise