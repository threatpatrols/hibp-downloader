# Development Workflow

Guidelines and examples for running common development tasks on this codebase.

## Make Targets (Recommended)

To avoid accidentally creating a local `.venv` in the repository, you should use the provided [Makefile](file:///home/ndejong/cyberco/projects/hibp-downloader/Makefile) for most tasks. The `Makefile` automatically exports the required sandboxed environment variables.

### Common Commands

- **Format**: Format python code using `ruff`.
  ```bash
  make format
  ```
- **Lint**: Lint and check types using `ruff` and `mypy`.
  ```bash
  make lint
  ```
- **Test**: Run all unit and integration tests using `pytest`.
  ```bash
  make test
  ```
- **Clean**: Remove python and test cache directories.
  ```bash
  make clean
  ```
- **Build**: Compile package into sdist and wheel packages.
  ```bash
  make build
  ```
- **All**: Run format, lint, test, and build in sequence.
  ```bash
  make all
  ```

### Running the App Locally

To run the local development build of the application, use `make run` and supply any CLI arguments.
> [!NOTE]
> The Makefile converts trailing `help` arguments into `--help`.

Examples:
- **Show App Help**:
  ```bash
  make run --help
  ```
- **Show Command Help (e.g., download)**:
  ```bash
  make run download --help
  ```
- **Execute Download**:
  ```bash
  make run download --hash-type sha1 --local-db /path/to/db
  ```

---

## Direct UV Commands (Manual)

If you must run `uv` commands directly, you **must** prefix them with the environment overrides to enforce sandboxing. Failing to do so will result in a local `.venv` directory, which is strictly prohibited.

```bash
UV_PROJECT_ENVIRONMENT=${HOME}/.local/venvs/hibp-download \
UV_CACHE_DIR=/tmp/.uv-cache-hibp-download \
UV_LINK_MODE=copy \
uv <command>
```

### Examples

- **Direct test run**:
  ```bash
  UV_PROJECT_ENVIRONMENT=${HOME}/.local/venvs/hibp-download \
  UV_CACHE_DIR=/tmp/.uv-cache-hibp-download \
  UV_LINK_MODE=copy \
  uv run pytest tests/ -vv
  ```
- **Direct single test run**:
  ```bash
  UV_PROJECT_ENVIRONMENT=${HOME}/.local/venvs/hibp-download \
  UV_CACHE_DIR=/tmp/.uv-cache-hibp-download \
  UV_LINK_MODE=copy \
  uv run pytest tests/test_http.py::test_http_fetch
  ```
