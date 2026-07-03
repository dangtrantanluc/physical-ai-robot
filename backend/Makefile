.PHONY: help install dev run test lint fmt typecheck migrate revision up down logs clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

install: ## Install runtime deps
	pip install -r requirements.txt

dev: ## Install dev + runtime deps
	pip install -r requirements-dev.txt

run: ## Run the API with autoreload (needs local Postgres + Redis)
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test: ## Run the test suite
	pytest

lint: ## Lint with ruff
	ruff check app tests

fmt: ## Auto-format with ruff
	ruff check --fix app tests
	ruff format app tests

typecheck: ## Static type check
	mypy app

migrate: ## Apply migrations to head
	alembic upgrade head

revision: ## Autogenerate a migration: make revision m="message"
	alembic revision --autogenerate -m "$(m)"

up: ## Start the full stack (db + redis + api)
	docker compose up --build

down: ## Stop the stack
	docker compose down

logs: ## Tail api logs
	docker compose logs -f api

clean: ## Remove caches
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .mypy_cache .ruff_cache
