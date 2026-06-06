export UV_PROJECT_ENVIRONMENT=$(HOME)/.local/venvs/hibp-download
export UV_CACHE_DIR=/tmp/.uv-cache-hibp-download
export UV_LINK_MODE=copy

# Capture trailing arguments for make run (maps exactly "help" to "--help")
ifeq (run,$(firstword $(MAKECMDGOALS)))
  RUN_ARGS := $(foreach word,$(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS)),$(if $(filter help,$(word)),--help,$(word)))
  EVAL_ARGS := $(filter-out help run,$(MAKECMDGOALS))
  $(eval $(EVAL_ARGS):;@:)
endif

.PHONY: help format lint test build clean all run

help:
ifeq (,$(findstring run,$(MAKECMDGOALS)))
	@echo "Available targets:"
	@echo "  make format - Format code with ruff"
	@echo "  make lint   - Lint code with ruff and mypy"
	@echo "  make test   - Run tests using pytest"
	@echo "  make build  - Build sdist and wheel using uv"
	@echo "  make run    - Run development version of hibp-downloader (use help, query help, etc.)"
	@echo "  make clean  - Clean build directories and cache files"
	@echo "  make all    - Run format, lint, test, and build"
endif

format:
	uv run ruff format .

lint:
	uv run ruff check .
	uv run mypy src

test:
	uv run pytest tests/ -vv

build:
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
