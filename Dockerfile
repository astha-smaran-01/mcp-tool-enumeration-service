# Dockerfile for MCP Tool Enumeration Service
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies including Node.js for npx support
RUN apt-get update && apt-get install -y \
    curl \
    nodejs \
    npm \
    git \
    && rm -rf /var/lib/apt/lists/*

# Verify Node.js and npm versions
RUN node --version && npm --version

# Pre-install popular MCP packages for npx and uvx
COPY scripts/preinstall_mcp_packages.sh /tmp/preinstall_mcp_packages.sh
COPY popular_mcp_packages.json /tmp/popular_mcp_packages.json
RUN chmod +x /tmp/preinstall_mcp_packages.sh && \
    /tmp/preinstall_mcp_packages.sh

# Install uv
RUN pip install uv


# Copy dependency files and README (required for package build)
COPY pyproject.toml  README.md ./

# Install dependencies using uv
RUN uv lock
RUN uv sync --frozen --no-dev

# Copy application code
COPY . .

# Set Python path
ENV PYTHONPATH=/app

# Expose port (will be overridden by environment variable)
EXPOSE 8503

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8503}/health || exit 1

# Start the application
CMD ["uv", "run", "python", "-m", "src.app.protocols.http.main"]