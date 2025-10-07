# Makefile for GitHub to App Converter
# Provides convenient shortcuts for common tasks

.PHONY: help install install-dev test test-unit test-integration test-smoke test-fast test-all coverage lint format clean setup

# Default target
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "GitHub to App Converter - Make Commands"
	@echo "========================================"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Installation targets
install: ## Install production dependencies
	pip install -r requirements.txt

install-dev: ## Install development dependencies
	pip install -r requirements-dev.txt

setup: ## Initial project setup
	mkdir -p generated_apps temp_repos static templates
	pip install -r requirements.txt
	@echo "✅ Project setup complete!"

# Testing targets
test: ## Run all tests
	pytest -v

test-unit: ## Run unit tests only
	pytest -m unit -v

test-integration: ## Run integration tests only
	pytest -m integration -v

test-smoke: ## Run smoke tests (quick validation)
	pytest -m smoke -v

test-fast: ## Run fast tests (exclude slow tests)
	pytest -m "not slow" -v

test-all: ## Run all tests including slow ones
	pytest -v --tb=short

test-watch: ## Run tests in watch mode (requires pytest-watch)
	pip install pytest-watch
	ptw -- -v

test-failed: ## Re-run only failed tests
	pytest --lf -v

test-parallel: ## Run tests in parallel (requires pytest-xdist)
	pip install pytest-xdist
	pytest -n auto -v

# Coverage targets
coverage: ## Run tests with coverage report
	pytest --cov=src --cov-report=term-missing

coverage-html: ## Generate HTML coverage report
	pytest --cov=src --cov-report=html
	@echo "📊 Coverage report: htmlcov/index.html"

coverage-xml: ## Generate XML coverage report (for CI)
	pytest --cov=src --cov-report=xml

coverage-report: ## Generate and open HTML coverage report
	pytest --cov=src --cov-report=html
	@python -m webbrowser htmlcov/index.html || echo "Open htmlcov/index.html in your browser"

# Code quality targets
lint: ## Run linters (flake8)
	flake8 src tests

lint-all: ## Run all linters (flake8, pylint, mypy)
	flake8 src tests
	pylint src tests || true
	mypy src || true

format: ## Format code with black and isort
	black src tests
	isort src tests

format-check: ## Check code formatting without making changes
	black --check src tests
	isort --check-only src tests

security: ## Run security checks
	bandit -r src
	safety check

# Cleaning targets
clean: ## Clean up generated files
	rm -rf __pycache__ .pytest_cache .coverage htmlcov
	rm -rf build dist *.egg-info
	rm -rf .mypy_cache .tox
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

clean-all: clean ## Clean everything including generated apps
	rm -rf generated_apps/* temp_repos/*
	@echo "⚠️  Cleaned all generated content"

clean-test: ## Clean test artifacts
	rm -rf .pytest_cache htmlcov .coverage coverage.xml
	rm -rf .tox .mypy_cache

# Development targets
run: ## Run the application
	python3 run.py

run-dev: ## Run application in development mode
	uvicorn main:app --reload --host 0.0.0.0 --port 8000

dev: install-dev ## Setup development environment
	pre-commit install || echo "pre-commit not available"
	@echo "✅ Development environment ready!"

# Documentation targets
docs: ## Generate documentation (requires sphinx)
	pip install sphinx sphinx-rtd-theme
	sphinx-build -b html docs docs/_build

docs-serve: docs ## Build and serve documentation
	cd docs/_build && python3 -m http.server 8080

# Validation targets
validate: format-check lint test-unit ## Run all validation checks
	@echo "✅ All validation checks passed!"

ci: ## Run CI checks locally
	pytest -m "not requires_api and not requires_network" --cov=src --cov-report=xml
	flake8 src tests
	black --check src tests
	@echo "✅ CI checks complete!"

# Release targets
pre-commit: format lint test-fast ## Run pre-commit checks
	@echo "✅ Pre-commit checks passed!"

pre-push: format lint test coverage ## Run pre-push checks
	@echo "✅ Pre-push checks passed!"

# Information targets
info: ## Show project information
	@echo "Project: GitHub to App Converter"
	@echo "Python version: $$(python3 --version)"
	@echo "Pytest version: $$(python3 -m pytest --version 2>/dev/null || echo 'Not installed')"
	@echo ""
	@echo "Test files: $$(find tests -name 'test_*.py' | wc -l)"
	@echo "Source files: $$(find src -name '*.py' | wc -l)"
	@echo ""
	@pytest --co -q 2>/dev/null | tail -1 || echo "Run 'make install' first"

list-tests: ## List all available tests
	pytest --co -q

# Docker targets (if needed)
docker-build: ## Build Docker image
	docker build -t github-to-app-converter .

docker-run: ## Run in Docker container
	docker run -p 8000:8000 github-to-app-converter

docker-test: ## Run tests in Docker
	docker run github-to-app-converter pytest

# Quick shortcuts
t: test ## Shortcut for 'test'
tu: test-unit ## Shortcut for 'test-unit'
ti: test-integration ## Shortcut for 'test-integration'
ts: test-smoke ## Shortcut for 'test-smoke'
c: coverage ## Shortcut for 'coverage'
l: lint ## Shortcut for 'lint'
f: format ## Shortcut for 'format'