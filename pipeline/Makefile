.PHONY: help install test lint clean docker-build docker-up docker-down docker-logs

help:
	@echo "Available commands:"
	@echo "  make install       - Install dependencies"
	@echo "  make test          - Run tests"
	@echo "  make lint          - Run linter"
	@echo "  make clean         - Clean up generated files"
	@echo "  make docker-build  - Build Docker images"
	@echo "  make docker-up     - Start all services with Docker Compose"
	@echo "  make docker-down   - Stop all services"
	@echo "  make docker-logs   - View logs from all services"
	@echo "  make run-api       - Run API service locally"
	@echo "  make run-video     - Run video generator service locally"
	@echo "  make run-model     - Run model converter service locally"

install:
	pip install -r requirements.txt

test:
	pytest

test-coverage:
	pytest --cov=. --cov-report=html --cov-report=term

lint:
	pylint common/ api/ video_generator/ model_converter/ orchestrator/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf storage/videos/*
	rm -rf storage/models/*
	rm -rf storage/temp/*

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-restart:
	docker-compose restart

run-api:
	python -m api.app

run-video:
	python -m video_generator.service

run-model:
	python -m model_converter.service

run-orchestrator:
	python -m orchestrator.service

setup-dirs:
	mkdir -p storage/videos storage/models storage/temp logs