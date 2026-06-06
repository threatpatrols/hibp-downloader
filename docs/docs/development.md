# Development

This project uses **[uv](https://github.com/astral-sh/uv)** for development, testing, packaging, and release management.

> [!IMPORTANT]
> To comply with environment guidelines and ensure no local `.venv` is created in the repository, prefix all local `uv` commands with:
> ```shell
> UV_PROJECT_ENVIRONMENT=${HOME}/.local/venvs/hibp-download \
> UV_CACHE_DIR=/tmp/.uv-cache-hibp-download \
> UV_LINK_MODE=copy
> ```

## Commands

```shell
# Update code formatting
uv run ruff format .

# Run linter
uv run ruff check .

# Run type checker
uv run mypy src

# Run tests
uv run pytest tests/ -vv

# Build a package (wheel and sdist)
uv build --out-dir dist

# Publish a package
uv publish dist/*
```

