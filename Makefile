# Makefile — local CI replication for tech-cheat-sheets-and-notes
#
# All Python work runs inside a local .venv so nothing touches the system
# Python. The venv is created automatically the first time any Python target
# is invoked.
#
# Targets:
#   make venv              Create .venv and install dev deps (idempotent)
#   make install           Alias for venv + npm ci
#   make markdownlint      Lint Markdown files
#   make mermaid-check     Validate all Mermaid diagrams via mmdc
#   make python-lint       ruff check + ruff format --check
#   make python-lint-fix   Auto-fix safe ruff violations
#   make python-test       pytest with coverage (default venv Python)
#   make python-test-all   pytest across Python 3.11, 3.12, 3.13
#   make link-check        Dead-link check (requires lychee on PATH)
#   make docs-serve        Serve the MkDocs site locally (hot-reload)
#   make docs-build        Build the static MkDocs site into site/
#   make update-docs-reqs  Regenerate requirements-docs.txt from uv.lock
#   make check-docs-deps   Verify requirements-docs.txt matches uv.lock
#   make ci                Full pipeline — no link-check (makes live HTTP calls)
#   make ci-full           Full pipeline including link-check
#   make clean             Remove .venv, node_modules, site/, and build artefacts

# ── Configuration ──────────────────────────────────────────────────────────────
# Override on the command line: make python-test PYTHON=python3.12
PYTHON   ?= python3

VENV     := .venv
VENV_BIN := $(VENV)/bin
PY       := $(VENV_BIN)/python
PIP      := $(VENV_BIN)/pip
UV       := $(VENV_BIN)/uv

PUPPETEER_CONFIG_FILE ?= /tmp/puppeteer-config.json
LYCHEE_VERSION        ?= lychee-v0.24.2
LYCHEE_DIR            := .tools/lychee/$(LYCHEE_VERSION)
LYCHEE_BIN            := $(LYCHEE_DIR)/lychee

MD_GLOBS         = "docs/**/*.md" "README.md" "AGENTS.md" "CONTRIBUTING.md"
LINT_TARGETS     = scripts/ tests/
# Validate all Markdown files that contain Mermaid fences or snippet references to .mmd files.
# This includes both cheat sheets and the section snippet files under docs/<section>/.
MD_FILES_VALIDATE := $(shell $(PY) scripts/validate_mermaid.py --discover-md)
# All standalone .mmd diagram files
MMD_FILES_VALIDATE := $(shell $(PY) scripts/validate_mermaid.py --discover-mmd)

# ── Phony declarations ─────────────────────────────────────────────────────────
.PHONY: help venv install ensure-uv \
        markdownlint \
		puppeteer-config npm-deps npm-audit mermaid-check \
        python-lint python-lint-fix \
        python-audit \
        python-test python-test-311 python-test-312 python-test-313 python-test-all \
		ensure-lychee link-check \
        start docs-build \
        update-docs-reqs check-docs-deps \
        ci ci-full \
        clean

# ── Default target ─────────────────────────────────────────────────────────────
help: ## List documented Make targets
	@grep -E '^[a-zA-Z0-9_-]+:.*?## ' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS=":.*?## "} {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ── Venv bootstrap ────────────────────────────────────────────────────────────
# The sentinel file $(VENV_BIN)/activate is recreated only when pyproject.toml
# changes, keeping re-installs fast during day-to-day work.
$(VENV_BIN)/activate: pyproject.toml
	@echo "--- creating .venv ---"
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip --quiet
	$(PIP) install -e '.[dev]' --quiet
	@touch $(VENV_BIN)/activate

venv: $(VENV_BIN)/activate ## Create .venv and install development dependencies

# ── Install (Python + Node) ────────────────────────────────────────────────────
install: venv ## Install Python and Node development dependencies
	npm ci

ensure-uv: venv ## Install uv in the project venv when absent
	@if [ ! -x "$(UV)" ]; then $(PIP) install uv; fi

# ── markdownlint ──────────────────────────────────────────────────────────────
markdownlint: ## Lint Markdown files
	@echo "--- markdownlint ---"
	npx markdownlint-cli2 $(MD_GLOBS)

# ── Mermaid check ─────────────────────────────────────────────────────────────
puppeteer-config: ## Configure Puppeteer for sandboxed environments
	@echo '{"args":["--no-sandbox","--disable-setuid-sandbox"]}' > $(PUPPETEER_CONFIG_FILE)

npm-deps: ## Install Node dependencies
	npm ci

mermaid-check: venv puppeteer-config npm-deps ## Validate Mermaid diagrams in Markdown and .mmd files
	@echo "--- mermaid-check ---"
	PUPPETEER_CONFIG_FILE=$(PUPPETEER_CONFIG_FILE) \
	  PATH="$(CURDIR)/node_modules/.bin:$(PATH)" \
	  $(PY) scripts/validate_mermaid.py

npm-audit: npm-deps ## Audit Node dependencies for high-severity vulnerabilities
	@echo "--- npm-audit ---"
	npm audit --audit-level=high

# ── Python lint ───────────────────────────────────────────────────────────────
python-lint: venv ## Run Ruff checks and formatting verification
	@echo "--- python-lint ---"
	$(VENV_BIN)/ruff check $(LINT_TARGETS)
	$(VENV_BIN)/ruff format --check $(LINT_TARGETS)

python-lint-fix: venv ## Automatically fix safe Ruff violations and formatting
	@echo "--- python-lint-fix ---"
	$(VENV_BIN)/ruff check --fix $(LINT_TARGETS)
	$(VENV_BIN)/ruff format $(LINT_TARGETS)

# ── Python audit ──────────────────────────────────────────────────────────────
# Mirrors: Audit Python dependencies step in the python-lint CI job.
python-audit: venv ## Scan Python dependencies for known vulnerabilities
	@echo "--- python-audit ---"
	$(VENV_BIN)/pip-audit --skip-editable

# ── Python test ───────────────────────────────────────────────────────────────
# Default: uses the venv created from $(PYTHON) (python3 unless overridden).
python-test: venv ## Run tests with coverage using the default Python version
	@echo "--- python-test ($(PY)) ---"
	$(VENV_BIN)/pytest tests/ -v \
	  --cov=scripts --cov-report=term-missing --cov-fail-under=90

# Per-version targets — each builds its own isolated venv in .venv-<ver>.
# Requires the named interpreter to be installed on the host.
.venv-311/bin/activate: pyproject.toml
	python3.11 -m venv .venv-311
	.venv-311/bin/pip install --upgrade pip --quiet
	.venv-311/bin/pip install -e '.[dev]' --quiet
	@touch .venv-311/bin/activate

.venv-312/bin/activate: pyproject.toml
	python3.12 -m venv .venv-312
	.venv-312/bin/pip install --upgrade pip --quiet
	.venv-312/bin/pip install -e '.[dev]' --quiet
	@touch .venv-312/bin/activate

.venv-313/bin/activate: pyproject.toml
	python3.13 -m venv .venv-313
	.venv-313/bin/pip install --upgrade pip --quiet
	.venv-313/bin/pip install -e '.[dev]' --quiet
	@touch .venv-313/bin/activate

python-test-311: .venv-311/bin/activate ## Run tests with Python 3.11
	@echo "--- python-test (3.11) ---"
	.venv-311/bin/pytest tests/ -v \
	  --cov=scripts --cov-report=term-missing --cov-fail-under=90

python-test-312: .venv-312/bin/activate ## Run tests with Python 3.12
	@echo "--- python-test (3.12) ---"
	.venv-312/bin/pytest tests/ -v \
	  --cov=scripts --cov-report=term-missing --cov-fail-under=90

python-test-313: .venv-313/bin/activate ## Run tests with Python 3.13
	@echo "--- python-test (3.13) ---"
	.venv-313/bin/pytest tests/ -v \
	  --cov=scripts --cov-report=term-missing --cov-fail-under=90

# Aggregates the per-version targets above. Keep this list in sync with the
# supported Python versions exercised by the required PR/release CI matrices.
# Note: the help text cannot live on the target line itself — the documented
# local parity set (python-test-311/312/313) is asserted verbatim by
# tests/test_dependencies.py, so any trailing token would break that guard.
python-test-all: python-test-311 python-test-312 python-test-313

# ── Link check ────────────────────────────────────────────────────────────────
$(LYCHEE_BIN):
	@echo "--- installing lychee ($(LYCHEE_VERSION)) ---"
	@set -e; \
	mkdir -p "$(LYCHEE_DIR)"; \
	tmp_dir=$$(mktemp -d); \
	asset="lychee-x86_64-unknown-linux-gnu.tar.gz"; \
	url="https://github.com/lycheeverse/lychee/releases/download/$(LYCHEE_VERSION)/$$asset"; \
	curl -fsSL "$$url" -o "$$tmp_dir/$$asset"; \
	tar -xzf "$$tmp_dir/$$asset" -C "$$tmp_dir"; \
	binary_path=$$(find "$$tmp_dir" -type f -name lychee | head -n 1); \
	if [ -z "$$binary_path" ]; then \
		echo "Could not locate lychee binary in downloaded archive"; \
		rm -rf "$$tmp_dir"; \
		exit 1; \
	fi; \
	install -m 0755 "$$binary_path" "$(LYCHEE_BIN)"; \
	rm -rf "$$tmp_dir"

ensure-lychee: $(LYCHEE_BIN) ## Install lychee if its local binary is absent

link-check: ensure-lychee ## Check documentation links using lychee
	@echo "--- link-check ---"
	$(LYCHEE_BIN) --verbose --no-progress \
	  --retry-wait-time 5 --max-retries 3 --timeout 30 \
	  docs/**/*.md README.md CONTRIBUTING.md AGENTS.md

# ── Docs — MkDocs Material ────────────────────────────────────────────────────
# Diagrams are stored as standalone .mmd files in docs/diagrams/ and referenced
# from the cheat-sheet Markdown files via PyMdown Snippets directives.
# MkDocs+Material renders Mermaid in-browser; no pre-compilation is required.

start: venv ## Serve the documentation site locally with hot reload
	@echo "--- docs-serve (http://127.0.0.1:8000) ---"
	$(VENV_BIN)/mkdocs serve --dev-addr 127.0.0.1:8000

docs-build: venv ## Build the documentation site in strict mode
	@echo "--- docs-build ---"
	$(VENV_BIN)/mkdocs build --strict

# ── Documentation dependency management ───────────────────────────────────────
# requirements-docs.txt is the single locked, hashed dependency file for
# documentation builds. It is generated from uv.lock via `uv export` and is
# the authoritative source consumed by CI (lint.yml docs-build job) and
# Vercel (vercel.json buildCommand). Local `make venv` installs the full
# `[dev]` extra which also includes the docs deps, so local and remote
# builds resolve from the same locked set.
#
# To add or update a documentation dependency:
#   1. Add or edit the package in pyproject.toml [project.optional-dependencies] docs
#   2. Run `make update-docs-reqs` to regenerate requirements-docs.txt
#   3. Run `make check-docs-deps` to verify the file is in sync

update-docs-reqs: ensure-uv ## Regenerate requirements-docs.txt from uv.lock
	@echo "--- update-docs-reqs ---"
	@rm -f requirements-docs.txt.tmp
	@( \
		echo "# Minimal Python dependencies for building the MkDocs documentation site." > requirements-docs.txt.tmp && \
		echo "#" >> requirements-docs.txt.tmp && \
		echo "# This file is auto-generated from uv.lock via:" >> requirements-docs.txt.tmp && \
		echo "#   uv export --format requirements.txt --output-file requirements-docs.txt --extra docs --no-dev --no-header --python 3.12" >> requirements-docs.txt.tmp && \
		echo "#" >> requirements-docs.txt.tmp && \
		echo "# Do not edit manually. To add or update documentation dependencies, edit" >> requirements-docs.txt.tmp && \
		echo "# pyproject.toml [project.optional-dependencies] docs, then run" >> requirements-docs.txt.tmp && \
		echo "# \`make update-docs-reqs\` to regenerate this file." >> requirements-docs.txt.tmp && \
		echo "#" >> requirements-docs.txt.tmp && \
		echo "# All three build environments consume this file:" >> requirements-docs.txt.tmp && \
		echo "#   - Local:   \`make venv\` installs the full \`[dev]\` extra (includes docs deps)" >> requirements-docs.txt.tmp && \
		echo "#   - CI:      \`pip install -r requirements-docs.txt\` in the docs-build job" >> requirements-docs.txt.tmp && \
		echo "#   - Vercel:  \`python -m pip install -r requirements-docs.txt\` in vercel.json" >> requirements-docs.txt.tmp && \
		echo "#" >> requirements-docs.txt.tmp && \
		$(UV) export --format requirements.txt --extra docs --no-dev --no-header --python 3.12 >> requirements-docs.txt.tmp 2>/dev/null && \
		mv requirements-docs.txt.tmp requirements-docs.txt \
	) || (rm -f requirements-docs.txt.tmp; exit 1)

check-docs-deps: ensure-uv ## Verify requirements-docs.txt matches uv.lock
	@echo "--- check-docs-deps ---"
	@$(UV) export --format requirements.txt --extra docs --no-dev --no-header --python 3.12 > /tmp/requirements-docs-generated.txt 2>/dev/null && \
	(grep -v '^[[:space:]]*#' requirements-docs.txt | grep -v '^[[:space:]]*$$' > /tmp/docs-committed.txt && \
	 grep -v '^[[:space:]]*#' /tmp/requirements-docs-generated.txt | grep -v '^[[:space:]]*$$' > /tmp/docs-generated.txt && \
	 diff /tmp/docs-committed.txt /tmp/docs-generated.txt >/dev/null && \
	 rm -f /tmp/requirements-docs-generated.txt /tmp/docs-committed.txt /tmp/docs-generated.txt && \
	 echo "requirements-docs.txt matches uv export output") || \
	(echo "MISMATCH: requirements-docs.txt differs from uv export output" >&2; \
	 echo "Run: make update-docs-reqs" >&2; \
	 rm -f /tmp/requirements-docs-generated.txt /tmp/docs-committed.txt /tmp/docs-generated.txt; \
	 exit 1)

# ── Full CI pipeline ──────────────────────────────────────────────────────────
ci: markdownlint npm-audit mermaid-check python-lint python-audit python-test check-docs-deps docs-build ## Run the full local verification pipeline
	@echo ""
	@echo "=== CI passed ==="

ci-full: ci link-check ## Run the full pipeline including link checks
	@echo ""
	@echo "=== Full CI including link-check passed ==="

# ── Clean ─────────────────────────────────────────────────────────────────────
clean: ## Remove virtual environments, dependencies, and build artifacts
	rm -rf $(VENV) .venv-311 .venv-312 .venv-313
	rm -rf .tools/
	rm -rf node_modules
	rm -rf site/
	rm -rf .coverage .coverage.* htmlcov/ .pytest_cache/ .ruff_cache/
	rm -rf *.egg-info dist build
	@echo "--- clean done ---"
