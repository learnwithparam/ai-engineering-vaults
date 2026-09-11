.PHONY: help setup install dev run probe status score check test test-live record diagrams clean \
        check-structure check-notebooks check-diagrams check-prose check-paths check-fixtures check-theme check-coverage check-gates
.DEFAULT_GOAL := help

BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m

UV := uv
PY := $(UV) run python
ROOT := $(shell pwd)

help: ## Show this help
	@echo "$(BLUE)AI Engineering Vaults$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-17s$(NC) %s\n", $$1, $$2}'

# ============================================================================
# Setup
# ============================================================================

setup: ## Create .env from an existing key, install everything
	@if ! command -v uv >/dev/null 2>&1; then \
		echo "$(BLUE)Installing uv...$(NC)"; \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
	fi
	@$(UV) sync
	@$(UV) run python scripts/setup_env.py
	@echo "$(GREEN)Ready. Next: make run$(NC)"

install: ## Sync dependencies
	@$(UV) sync

# ============================================================================
# Development
# ============================================================================

dev: setup run ## Set up then launch

run: ## Launch JupyterLab with the recording theme
	@echo "$(BLUE)JupyterLab on http://localhost:8888$(NC)"
	@JUPYTER_CONFIG_DIR=$(ROOT)/.jupyter \
	 JUPYTERLAB_SETTINGS_DIR=$(ROOT)/.jupyter/lab/user-settings \
	 $(UV) run jupyter lab --custom-css --port=8888

probe: ## Ask the provider what is actually true, write build/provider-truth.json
	@$(PY) scripts/probe_provider.py

status: ## Show build progress from the ledger
	@$(PY) scripts/ledger.py show

# ============================================================================
# Quality
# ============================================================================

score: ## Score every notebook and vault. Threshold 95
	@$(PY) scripts/score.py

check-structure: ## Beats, metadata, capstones, README coverage
	@$(PY) scripts/check_structure.py

check-notebooks: ## Every notebook parses
	@$(PY) scripts/check_notebooks.py

check-diagrams: ## Every diagram has a fresh SVG, every reference resolves
	@$(PY) scripts/check_diagrams.py

check-prose: ## Em dashes, banned words, provider constants, key-shaped strings
	@$(PY) scripts/check_prose.py

check-paths: ## Every repo path named in a doc resolves
	@$(PY) scripts/check_paths.py

check-fixtures: ## Every notebook has fixtures and every fixture is used
	@$(PY) scripts/check_fixtures.py

check-theme: ## Theme files exist, parse, and agree on fonts
	@$(PY) scripts/check_theme.py

check-coverage: ## Every vault still teaches what its course spec promised
	@$(PY) scripts/check_coverage.py

check-gates: ## Prove the gates bite, by planting a broken vault and removing it
	@$(PY) scripts/check_gates.py

check: check-structure check-notebooks check-diagrams check-prose check-paths check-fixtures check-theme check-coverage check-gates score ## Run every gate
	@echo "$(GREEN)All gates passed$(NC)"

# ============================================================================
# Tests
# ============================================================================

test: ## Execute every notebook in replay. No key, no spend
	@VAULT_MODE=replay $(PY) scripts/run_notebooks.py

test-live: ## Execute every notebook against the real API. Costs money
	@VAULT_MODE=live $(PY) scripts/run_notebooks.py

record: ## Refresh fixtures from the real API, budget guarded
	@$(PY) scripts/record.py

diagrams: ## Render every .mmd to SVG and refresh the manifest. VAULT=01 renders one vault
	@$(PY) scripts/render_diagrams.py $(VAULT)

# ============================================================================
# Cleanup
# ============================================================================

# provider-truth.json is committed, because a clone with no key still has to
# print a real cost. Nothing here removes it.
clean: ## Remove venv, caches and build artefacts
	@rm -rf .venv build/scores.json build/budget.json
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".ipynb_checkpoints" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)Cleaned$(NC)"
