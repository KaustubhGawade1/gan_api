# Makefile for common development tasks

.PHONY: help install dev prod test lint format clean run

help:
	@echo "GAN Backend API - Available Commands"
	@echo "===================================="
	@echo ""
	@echo "make install    - Install dependencies"
	@echo "make dev        - Run in development mode (with reload)"
	@echo "make prod       - Run in production mode"
	@echo "make test       - Run test suite"
	@echo "make lint       - Run code linting (flake8)"
	@echo "make format     - Format code with black"
	@echo "make clean      - Clean up cache and build files"
	@echo "make docker     - Build Docker image"
	@echo "make weights    - Generate dummy weights for testing"
	@echo ""

install:
	pip install -r requirements.txt

dev:
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

prod:
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

test:
	pytest tests/ -v

lint:
	flake8 app/ --max-line-length=120
	mypy app/ --ignore-missing-imports

format:
	black app/ tests/
	isort app/ tests/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info

docker:
	docker build -t gan-backend:latest .

docker-run:
	docker run --gpus all -p 8000:8000 gan-backend:latest

weights:
	python init_weights.py

install-dev:
	pip install -r requirements.txt
	pip install pytest black flake8 mypy isort

check:
	@echo "Running checks..."
	format
	lint
	test
	@echo "All checks passed! ✅"

.DEFAULT_GOAL := help
