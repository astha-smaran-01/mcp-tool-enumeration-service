#!/bin/bash

# MCP Tool Enumeration Service Startup Script
# Author: Smaran Dhungana <smaran@astha.ai>
# Created: 2025-09-14
# Updated for uv package management

set -e

echo "🚀 Starting MCP Tool Enumeration Service..."

# Check if .env file exists, if not copy from example
if [ ! -f ".env" ]; then
    echo "📋 Creating .env from .env.example..."
    cp .env.example .env
    echo "⚠️  Please customize .env file for your environment"
fi

# Load environment variables
if [ -f ".env" ]; then
    echo "🔧 Loading environment variables..."
    export $(grep -v '^#' .env | xargs)
fi
# Set Python path to include the service directory
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Please install uv first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Install dependencies using uv
echo "📦 Installing dependencies with uv..."
uv sync

echo "🔧 Service Configuration:"
echo "  - Port: $PORT"
echo "  - Python Path: $PYTHONPATH"
echo "  - Working Directory: $(pwd)"

# Start the service using uv
echo "✅ Starting MCP Tool Enumeration Service on port $PORT..."
uv run uvicorn app.protocols.http.main:app --host 0.0.0.0 --port $PORT --reload