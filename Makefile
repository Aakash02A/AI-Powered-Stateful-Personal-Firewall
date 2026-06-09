# ============================================================
# SentinelX AI-SOC — Root Makefile
# ============================================================
.DEFAULT_GOAL := help
SHELL := /bin/bash

# ── Colors ──────────────────────────────────────────────────
CYAN  := \033[0;36m
GREEN := \033[0;32m
RESET := \033[0m

.PHONY: help dev down build test lint format seed

help: ## Show this help
	@awk 'BEGIN {FS = ":.*##"; printf "\n${CYAN}SentinelX AI-SOC${RESET}\n\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  ${GREEN}%-20s${RESET} %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

# ── Development ──────────────────────────────────────────────
dev: ## Start full local stack (all services + infra)
	docker compose up --build -d
	@echo "$(GREEN)✅  Stack is up. Dashboard → http://localhost:3000$(RESET)"

down: ## Stop local stack
	docker compose down -v

logs: ## Tail all container logs
	docker compose logs -f

restart: ## Restart a specific service (make restart s=auth)
	docker compose restart $(s)

# ── Build ────────────────────────────────────────────────────
build: ## Build all Docker images
	docker compose build

build-service: ## Build a single service (make build-service s=auth)
	docker compose build $(s)

# ── Testing ──────────────────────────────────────────────────
test: ## Run all backend tests
	@for svc in auth telemetry rule-engine ml-engine threat-intel alert-engine response-engine ai-analyst; do \
		echo "$(CYAN)▶ Testing $$svc...$(RESET)"; \
		docker compose run --rm $$svc pytest tests/ -v --tb=short || exit 1; \
	done

test-service: ## Test a single service (make test-service s=auth)
	docker compose run --rm $(s) pytest tests/ -v --tb=short

test-host: ## Run tests on the host system using virtual environment
	PYTHONPATH=backend/services/auth SECRET_KEY="test-secret-key-at-least-32-characters" DATABASE_URL="sqlite+aiosqlite:///:memory:" test_env/Scripts/pytest backend/services/auth/tests/ -v
	PYTHONPATH=backend/services/telemetry SECRET_KEY="test-secret-key-at-least-32-characters" DATABASE_URL="sqlite+aiosqlite:///:memory:" test_env/Scripts/pytest backend/services/telemetry/tests/ -v


test-frontend: ## Run frontend tests
	cd frontend && npm test

# ── Linting & Formatting ─────────────────────────────────────
lint: ## Lint all Python services
	@for svc in backend/services/*/; do \
		echo "$(CYAN)▶ Linting $$svc$(RESET)"; \
		cd $$svc && ruff check . && mypy app/ --ignore-missing-imports && cd -; \
	done

format: ## Auto-format all Python services
	@for svc in backend/services/*/; do \
		cd $$svc && ruff format . && cd -; \
	done

# ── Database ─────────────────────────────────────────────────
migrate: ## Run Alembic migrations for auth service
	docker compose run --rm auth alembic upgrade head

migrate-service: ## Run migrations for a specific service (make migrate-service s=auth)
	docker compose run --rm $(s) alembic upgrade head

seed: ## Seed the database with test data
	docker compose run --rm auth python scripts/seed_db.py

# ── Infrastructure ───────────────────────────────────────────
tf-plan: ## Terraform plan (env=dev|prod)
	cd infra/terraform/environments/$(env) && terraform init && terraform plan

tf-apply: ## Terraform apply (env=dev|prod)
	cd infra/terraform/environments/$(env) && terraform apply -auto-approve

# ── Utilities ────────────────────────────────────────────────
gen-events: ## Generate synthetic test events for the agent
	python scripts/generate_test_events.py

setup: ## First-time local setup (copy .env, install tools)
	cp .env.example .env
	@echo "$(GREEN)✅  .env created. Edit it with your API keys before running 'make dev'.$(RESET)"
