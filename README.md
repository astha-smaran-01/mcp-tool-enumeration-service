# MCP Tool Enumeration Service

## Metadata
- **Author**: Smaran Dhungana <smaran@astha.ai>
- **Created**: 2025-09-14
- **Last Updated**: 2025-09-14
- **Version**: 1.0
- **Status**: Active
- **Category**: Service-Specific

## Overview

The MCP Tool Enumeration Service is a focused microservice that extracts and enumerates tools from MCP JSON configurations. This service was extracted from the agent-onboarding service to provide a clean, dedicated tool enumeration capability for the Astha Compliance Engine.

## Architecture

This service follows Clean Architecture principles with clear separation of concerns:

```
├── domain/                    # Domain layer (interfaces, entities, DTOs)
│   ├── dto/                  # Data Transfer Objects
│   ├── entities/             # Domain entities
│   ├── interfaces/           # Domain interfaces
│   └── services/             # Domain service interfaces only
├── application/              # Application layer (business logic)
│   ├── services/            # Application services and strategies
│   └── use_cases/           # Use case implementations
├── adapters/                 # Infrastructure layer
│   ├── inbound/http/        # HTTP controllers
│   └── outbound/            # External service adapters
└── app/                     # Application entry point
    ├── container.py         # Dependency injection
    └── protocols/http/      # HTTP protocol implementation
```

## Features

### Tool Discovery Strategies

The service uses the Strategy Pattern to support multiple tool discovery methods:

1. **HTTP Discovery Strategy**: Discovers tools from HTTP/SSE servers via API calls
2. **STDIO Introspection Strategy**: Discovers tools by running STDIO commands and using JSON-RPC
3. **MCP JSON Parsing Strategy**: Fallback strategy that parses metadata from MCP JSON configuration

### Automatic Strategy Selection

The service automatically selects the appropriate strategy based on server configuration:
- Servers with `url` → HTTP Discovery
- Servers with `command` → STDIO Introspection
- Others → MCP JSON Parsing (fallback)

## API Endpoints

### POST `/api/v1/tools/enumerate`

Enumerate tools from MCP JSON configuration.

**Request Body:**
```json
{
  "mcp_json": {
    "mcpServers": {
      "server1": {
        "command": "npx",
        "args": ["mcp-remote", "https://example.com"],
        "env": {"API_KEY": "value"}
      },
      "server2": {
        "url": "https://api.example.com",
        "headers": {"Authorization": "Bearer token"}
      }
    }
  },
  "timeout_seconds": 30,
  "include_schemas": true,
  "parallel_discovery": true
}
```

**Response (Astha AI Standard Format):**
```json
{
  "success": true,
  "message": "Connected to 2 of 2 servers",
  "data": {
    "__typename": "ToolEnumerationResponse",
    "status": "success",
    "timestamp": "2025-09-14T10:30:00Z",
    "servers": [
      {
        "name": "server1",
        "status": "connected",
        "tool_count": 3,
        "error": null
      }
    ],
    "tools": [
      {
        "server": "server1",
        "name": "example_tool",
        "description": "Example tool description",
        "inputSchema": {...}
      }
    ],
    "total_servers": 2,
    "connected_servers": 2
  }
}
```

### GET `/health`

Health check endpoint.

## Configuration

The service can be configured via environment variables. See `.env.example` for all available options.

### Key Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8503` | Service port |
| `HOST` | `0.0.0.0` | Service host |
| `LOG_LEVEL` | `INFO` | Logging level |
| `DEFAULT_TIMEOUT_SECONDS` | `30` | Default timeout for tool discovery |
| `MAX_SERVERS_PER_REQUEST` | `10` | Maximum servers per enumeration request |
| `ENABLE_PARALLEL_DISCOVERY` | `true` | Enable parallel tool discovery |
| `HTTP_TIMEOUT` | `30` | HTTP client timeout |
| `HTTP_MAX_RETRIES` | `3` | HTTP client max retries |

### Configuration Files

- `.env.example`: Example environment configuration
- Copy to `.env` for local development

## Running the Service

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### Installation

#### Using uv (Recommended)

1. Install uv if not already installed:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Install dependencies:
```bash
cd backend/mcp-tool-enumeration-service
uv sync
```

#### Using pip (Alternative)
```bash
cd backend/mcp-tool-enumeration-service
pip install -e .
```

### Development

#### Using uv (Recommended)
```bash
uv run uvicorn app.protocols.http.main:app --host 0.0.0.0 --port 8503 --reload
```

#### Using startup script
```bash
chmod +x start.sh
./start.sh
```

#### Using pip
```bash
python -m app.protocols.http.main
```

### Production
```bash
uv run uvicorn app.protocols.http.main:app --host 0.0.0.0 --port 8503
```

## Integration with Compliance Engine

This service replaces the complex MCP JSON scanning logic in the compliance-scanning-service. The compliance service now calls this dedicated enumeration service to get tool data, then applies compliance analysis directly to the enumerated tools.

## SOLID Principles

The service strictly follows SOLID principles:

- **Single Responsibility**: Each class has one reason to change
- **Open/Closed**: Extensible via strategy pattern without modification
- **Liskov Substitution**: Strategies are fully interchangeable
- **Interface Segregation**: Small, focused interfaces
- **Dependency Inversion**: Depends on abstractions, not concretions

## Clean Architecture

- **Domain Layer**: Contains only interfaces, entities, and DTOs - no business logic
- **Application Layer**: Contains all business logic, use cases, and service implementations
- **Infrastructure Layer**: Contains adapters for external systems (HTTP, databases, etc.)
- **Dependency Direction**: All dependencies point inward toward the domain

## Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app --cov=domain --cov=application --cov=adapters

# Type checking
mypy .

# Code formatting
black .
isort .
```

## Related Services

- **compliance-scanning-service**: Uses this service to get tool enumeration data
- **api-gateway**: Routes requests to this service
- **agent-onboarding**: Original source of the tool enumeration logic

## Port Mapping

| Service | Port | Purpose |
|---------|------|---------|
| mcp-tool-enumeration-service | 8503 | Tool enumeration from MCP JSON |