# ScrapeMaster Intelligence - Development Makefile
# Usage: make <target>

.PHONY: help install install-dev clean test test-cov lint format type-check security-check docs build run run-dev docker-build docker-run docker-stop deploy-railway deploy-heroku

# Default target
help: ## Show this help message
	@echo "ScrapeMaster Intelligence - Development Commands"
	@echo "================================================"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Installation
install: ## Install production dependencies
	pip install -r requirements.txt

install-dev: ## Install development dependencies
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pre-commit install

clean: ## Clean up generated files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type d -name "dist" -exec rm -rf {} +
	find . -type d -name "build" -exec rm -rf {} +

# Testing
test: ## Run tests
	python -m pytest tests/ -v

test-cov: ## Run tests with coverage
	python -m pytest tests/ --cov=src --cov-report=html --cov-report=term-missing

test-fast: ## Run tests without coverage (faster)
	python -m pytest tests/ -v --no-cov

test-unit: ## Run unit tests only
	python -m pytest tests/ -v -m "unit"

test-integration: ## Run integration tests only
	python -m pytest tests/ -v -m "integration"

test-e2e: ## Run end-to-end tests only
	python -m pytest tests/ -v -m "e2e"

# Code Quality
lint: ## Run linting checks
	flake8 src/ tests/
	black --check src/ tests/
	isort --check-only src/ tests/

format: ## Format code
	black src/ tests/
	isort src/ tests/

type-check: ## Run type checking
	mypy src/

security-check: ## Run security checks
	bandit -r src/
	safety check

quality: format lint type-check security-check ## Run all quality checks

# Documentation
docs: ## Build documentation
	cd docs && make html

docs-serve: ## Serve documentation locally
	cd docs/_build/html && python -m http.server 8000

# Building
build: ## Build the package
	python setup.py sdist bdist_wheel

build-docker: ## Build Docker image
	docker build -t scrapemaster-intelligence .

# Running
run: ## Run the application in production mode
	streamlit run src/app.py --server.port 8501 --server.address 0.0.0.0

run-dev: ## Run the application in development mode
	streamlit run src/app.py --server.port 8501 --server.address 0.0.0.0 --server.runOnSave true

run-debug: ## Run with debug logging
	LOG_LEVEL=DEBUG streamlit run src/app.py --server.port 8501 --server.address 0.0.0.0

# Docker
docker-build: ## Build Docker image
	docker build -t scrapemaster-intelligence .

docker-run: ## Run Docker container
	docker run -p 8501:8501 --name scrapemaster scrapemaster-intelligence

docker-stop: ## Stop Docker container
	docker stop scrapemaster || true
	docker rm scrapemaster || true

docker-compose-up: ## Start services with Docker Compose
	docker-compose up -d

docker-compose-down: ## Stop services with Docker Compose
	docker-compose down

docker-compose-logs: ## View Docker Compose logs
	docker-compose logs -f

# Database
db-init: ## Initialize database
	python -c "from src.core.database import DatabaseManager; DatabaseManager().initialize_database()"

db-reset: ## Reset database (WARNING: This will delete all data)
	rm -f scrapemaster.db scrapemaster.db-shm scrapemaster.db-wal
	python -c "from src.core.database import DatabaseManager; DatabaseManager().initialize_database()"

# Deployment
deploy-railway: ## Deploy to Railway
	railway up

deploy-heroku: ## Deploy to Heroku
	git push heroku main

# Monitoring
monitor: ## Start monitoring dashboard
	python src/core/monitoring.py

health-check: ## Run health check
	python health_check.py

# Development Tools
pre-commit-run: ## Run pre-commit hooks on all files
	pre-commit run --all-files

pre-commit-update: ## Update pre-commit hooks
	pre-commit autoupdate

# Performance
benchmark: ## Run performance benchmarks
	python -m pytest tests/ --benchmark-only

profile: ## Profile the application
	python -m cProfile -o profile.stats src/app.py

# Git
git-setup: ## Setup Git hooks and configuration
	pre-commit install
	git config core.autocrlf input
	git config core.eol lf

git-clean: ## Clean Git repository
	git clean -fd
	git reset --hard HEAD

# Environment
env-setup: ## Setup environment variables
	cp config/env.example .env
	@echo "Please edit .env file with your configuration"

env-check: ## Check environment configuration
	python -c "from src.core.config import get_config; print('Configuration loaded successfully')"

# Backup and Restore
backup: ## Create backup of database and data
	mkdir -p backups
	cp scrapemaster.db backups/scrapemaster_$(shell date +%Y%m%d_%H%M%S).db
	cp -r data backups/data_$(shell date +%Y%m%d_%H%M%S)

restore: ## Restore from backup (specify BACKUP_DATE=YYYYMMDD_HHMMSS)
	@if [ -z "$(BACKUP_DATE)" ]; then echo "Please specify BACKUP_DATE=YYYYMMDD_HHMMSS"; exit 1; fi
	cp backups/scrapemaster_$(BACKUP_DATE).db scrapemaster.db
	cp -r backups/data_$(BACKUP_DATE) data

# All-in-one commands
setup: env-setup install-dev db-init git-setup ## Complete development setup

dev: run-dev ## Start development server

prod: run ## Start production server

test-all: test-cov lint type-check security-check ## Run all tests and checks

deploy: test-all build ## Prepare for deployment

# Windows-specific commands (for PowerShell)
windows-setup: ## Setup for Windows
	powershell -ExecutionPolicy Bypass -File start_scrapemaster.ps1

windows-run: ## Run on Windows
	start_scrapemaster.bat

# Quick commands
q: run-dev ## Quick start development server
qc: clean ## Quick clean
qt: test-fast ## Quick test
qf: format ## Quick format
ql: lint ## Quick lint 