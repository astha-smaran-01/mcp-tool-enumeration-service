# Docker Compose Setup for MCP Tool Enumeration Service

This document provides instructions for running the MCP Tool Enumeration Service using Docker Compose.

## Quick Start

### Development Environment
```bash
# Start development environment with hot reload
make dev

# Or manually:
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

### Production Environment
```bash
# Start production environment
make prod

# Or manually:
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d
```

## Available Commands

### Using Makefile (Recommended)
```bash
make help              # Show all available commands
make dev               # Start development environment
make prod              # Start production environment
make logs              # Show logs
make shell             # Open shell in container
make test              # Run tests
make health            # Check service health
make test-api          # Test API endpoints
make clean             # Clean up containers and volumes
```

### Using Docker Compose Directly

#### Development
```bash
# Start with hot reload
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build

# Start in background
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build -d

# View logs
docker-compose -f docker-compose.yml -f docker-compose.dev.yml logs -f

# Stop
docker-compose -f docker-compose.yml -f docker-compose.dev.yml down
```

#### Production
```bash
# Start production environment
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d

# Start with monitoring
docker-compose -f docker-compose.yml -f docker-compose.prod.yml --profile monitoring up --build -d

# View logs
docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs -f

# Stop
docker-compose -f docker-compose.yml -f docker-compose.prod.yml down
```

## Environment Configuration

### Environment Variables
The service uses the following environment variables:

- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8503)
- `ENVIRONMENT`: Environment type (development/production)
- `LOG_LEVEL`: Logging level (DEBUG/INFO/WARNING/ERROR)
- `PYTHONPATH`: Python path (default: /app)
- `PYTHONUNBUFFERED`: Python output buffering (default: 1)

### Custom Environment File
Create a `.env` file in the project root to override default values:

```bash
# .env
HOST=0.0.0.0
PORT=8503
ENVIRONMENT=development
LOG_LEVEL=DEBUG
```

## Service Endpoints

Once running, the service will be available at:

- **API Documentation**: http://localhost:8503/docs
- **Health Check**: http://localhost:8503/health
- **Examples Endpoint**: http://localhost:8503/api/v1/tools/examples
- **Enumerate Tools**: http://localhost:8503/api/v1/tools/enumerate

## Monitoring (Optional)

### Start Monitoring Stack
```bash
# Start with monitoring
make prod-with-monitoring

# Or manually:
docker-compose --profile monitoring up -d
```

### Access Monitoring Services
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)

## File Structure

```
mcp-tool-enumeration-service/
├── docker-compose.yml              # Main compose file
├── docker-compose.dev.yml          # Development overrides
├── docker-compose.prod.yml         # Production overrides
├── Dockerfile                      # Container definition
├── Makefile                        # Convenience commands
├── monitoring/                     # Monitoring configuration
│   ├── prometheus.yml             # Prometheus config
│   └── grafana/                   # Grafana configuration
│       ├── dashboards/
│       └── datasources/
└── logs/                          # Log directory (created automatically)
```

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Check what's using the port
   lsof -i :8503
   
   # Stop conflicting services or change port in docker-compose.yml
   ```

2. **Permission Issues**
   ```bash
   # Fix log directory permissions
   sudo chown -R $USER:$USER logs/
   ```

3. **Container Won't Start**
   ```bash
   # Check logs
   docker-compose logs mcp-tool-enumeration-service
   
   # Rebuild without cache
   docker-compose build --no-cache
   ```

4. **Health Check Failing**
   ```bash
   # Check if service is responding
   curl http://localhost:8503/health
   
   # Check container logs
   docker-compose logs mcp-tool-enumeration-service
   ```

### Debugging

1. **Access Container Shell**
   ```bash
   make shell
   # or
   docker-compose exec mcp-tool-enumeration-service /bin/bash
   ```

2. **View Real-time Logs**
   ```bash
   make logs
   # or
   docker-compose logs -f mcp-tool-enumeration-service
   ```

3. **Check Container Status**
   ```bash
   make status
   # or
   docker-compose ps
   ```

## Production Deployment

### Security Considerations

1. **Environment Variables**: Use secure environment variable management
2. **Secrets**: Store sensitive data in Docker secrets or external secret management
3. **Network**: Use proper network isolation
4. **Volumes**: Avoid mounting source code in production
5. **Resources**: Set appropriate resource limits

### Scaling

```bash
# Scale the service
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up --scale mcp-tool-enumeration-service=3 -d
```

### Health Monitoring

The service includes health checks that can be used with orchestration platforms:

```bash
# Check health
curl -f http://localhost:8503/health
```

## Cleanup

```bash
# Remove containers and volumes
make clean

# Remove everything including images
make clean-all
```