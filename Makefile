export UV_PROJECT_ENVIRONMENT=$(HOME)/.local/venvs/hibp-download
export UV_CACHE_DIR=/tmp/.uv-cache-hibp-download
export UV_LINK_MODE=copy

# Capture trailing arguments for make run (maps exactly "help" to "--help")
ifeq (run,$(firstword $(MAKECMDGOALS)))
  RUN_ARGS := $(foreach word,$(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS)),$(if $(filter help,$(word)),--help,$(word)))
  EVAL_ARGS := $(filter-out help run,$(MAKECMDGOALS))
  $(eval $(EVAL_ARGS):;@:)
endif

.PHONY: help format lint test build clean all run release

help:
ifeq (,$(findstring run,$(MAKECMDGOALS)))
	@echo "Available targets:"
	@echo "  make format  - Format code with ruff"
	@echo "  make lint    - Lint code with ruff and mypy"
	@echo "  make test    - Run tests using pytest"
	@echo "  make build   - Build sdist and wheel using uv"
	@echo "  make run     - Run development version of hibp-downloader (use help, query help, etc.)"
	@echo "  make clean   - Clean build directories and cache files"
	@echo "  make release - Release the current version built packages only to PyPI"
	@echo "  make all     - Run format, lint, test, and build"
endif

format:
	uv run ruff format .

lint:
	uv run ruff check .
	uv run mypy src

test:
	uv run pytest tests/ -vv

build:
	uv run python .agent/workflows/scripts/bump_semver_patch.py
	uv lock --project docs
	uv build --out-dir dist

# clean: NB > do not remove dist/ or build/
clean:
	rm -rf .pdm-build/ .mypy_cache/ .pytest_cache/ .ruff_cache/

run:
	@echo "--------------------------------------------------------"
	@echo "Hint: To pass double-dash options via make, use:"
	@echo "make -- run --data-path <path> <hibp-command>"
	@echo "--------------------------------------------------------"
	@echo ""
	uv run hibp-downloader $(ARGS) $(RUN_ARGS) || true

all: format lint test build

release:
	@if [ -z "$(UV_PUBLISH_TOKEN)" ]; then \
		echo "Error: UV_PUBLISH_TOKEN environment variable is not set." >&2; \
		exit 1; \
	fi
	@VERSION=$$(grep -m 1 -E '^version' pyproject.toml | cut -d '"' -f 2); \
	if [ -z "$$VERSION" ]; then \
		echo "Error: Could not determine version from pyproject.toml" >&2; \
		exit 1; \
	fi; \
	WHL_FILE="dist/hibp_downloader-$$VERSION-py3-none-any.whl"; \
	TAR_FILE="dist/hibp_downloader-$$VERSION.tar.gz"; \
	if [ ! -f "$$WHL_FILE" ] || [ ! -f "$$TAR_FILE" ]; then \
		echo "Error: Release files for version $$VERSION not found. Please run 'make build' first." >&2; \
		exit 1; \
	fi; \
	echo "Releasing version $$VERSION to PyPI..."; \
	uv publish $$WHL_FILE $$TAR_FILE
