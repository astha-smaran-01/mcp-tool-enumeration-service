# MCP Tool Enumeration Service - Docker Compose Management

.PHONY: help build up down logs shell test clean dev prod monitoring

# Default target
help: ## Show this help message
	@echo "MCP Tool Enumeration Service - Docker Compose Commands"
	@echo "======================================================"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Development commands
dev: ## Start development environment
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build

dev-detached: ## Start development environment in background
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build -d

# Production commands
prod: ## Start production environment
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d

prod-with-monitoring: ## Start production environment with monitoring
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml --profile monitoring up --build -d

# Basic commands
build: ## Build the Docker image
	docker-compose build

up: ## Start the service
	docker-compose up -d

down: ## Stop and remove containers
	docker-compose down

logs: ## Show logs
	docker-compose logs -f

logs-service: ## Show service logs only
	docker-compose logs -f mcp-tool-enumeration-service

# Development utilities
shell: ## Open shell in running container
	docker-compose exec mcp-tool-enumeration-service /bin/bash

shell-dev: ## Open shell in development container
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml exec mcp-tool-enumeration-service /bin/bash

# Testing
test: ## Run tests in container
	docker-compose exec mcp-tool-enumeration-service uv run pytest

test-coverage: ## Run tests with coverage
	docker-compose exec mcp-tool-enumeration-service uv run pytest --cov=app --cov=domain --cov=adapters --cov=application

# Monitoring
monitoring: ## Start monitoring stack (Prometheus + Grafana)
	docker-compose --profile monitoring up -d

monitoring-logs: ## Show monitoring logs
	docker-compose logs -f prometheus grafana

# Health checks
health: ## Check service health
	curl -f http://localhost:8503/health || echo "Service is not healthy"

status: ## Show container status
	docker-compose ps

# Cleanup
clean: ## Remove containers, networks, and volumes
	docker-compose down -v --remove-orphans
	docker system prune -f

clean-all: ## Remove everything including images
	docker-compose down -v --remove-orphans --rmi all
	docker system prune -af

# API Testing
test-api: ## Test the API endpoints
	@echo "Testing API endpoints..."
	@echo "1. Health check:"
	curl -s http://localhost:8503/health | jq .
	@echo "\n2. Examples endpoint:"
	curl -s http://localhost:8503/api/v1/tools/examples | jq .
	@echo "\n3. AWS test endpoint:"
	curl -s -X POST http://localhost:8503/api/v1/tools/test/aws | jq .

# Documentation
docs: ## Open API documentation
	@echo "Opening API documentation at http://localhost:8503/docs"
	@command -v xdg-open >/dev/null 2>&1 && xdg-open http://localhost:8503/docs || echo "Please open http://localhost:8503/docs in your browser"

# Quick start
quick-start: build up ## Quick start - build and run
	@echo "Service is starting up..."
	@sleep 5
	@make health
	@echo "Service is ready! API docs available at http://localhost:8503/docs"