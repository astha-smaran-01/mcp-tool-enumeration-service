"""
FastAPI application for MCP Tool Enumeration Service.

Author: Smaran Dhungana <smaran@astha.ai>
Created: 2025-09-14
Last Updated: 2025-09-14
Version: 1.0
Status: Active
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from adapters.inbound.http.tool_enumeration_controller import router as tool_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="MCP Tool Enumeration Service",
    description="Service for enumerating tools from MCP JSON configurations",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(tool_router)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "success": True,
        "message": "MCP Tool Enumeration Service",
        "data": {
            "__typename": "ServiceInfo",
            "service": "mcp-tool-enumeration-service",
            "version": "1.0.0",
            "status": "running"
        }
    }

# Health check
@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "success": True,
        "message": "Service is healthy",
        "data": {
            "__typename": "HealthCheck",
            "service": "mcp-tool-enumeration-service",
            "version": "1.0.0",
            "status": "healthy"
        }
    }

if __name__ == "__main__":
    import uvicorn
    import os
    
    port = int(os.getenv("PORT"))
    host = os.getenv("HOST")
    
    uvicorn.run(app, host=host, port=port)