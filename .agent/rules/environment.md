# Environment Guidelines

## Strictly No Local `.venv`

**⚠️ CRITICAL RULE: NEVER create a local `.venv` directory inside the repository.**

All dependency management and execution must be isolated from the repository path to ensure a clean experience and prevent state pollution. 

### Enforcing the Rule
Whenever you use `uv` to install dependencies, run scripts, or execute tests, you **MUST** prefix the command with environment variables that point the virtual environment to `${HOME}/.local/venvs/hibp-download` and the cache to the `/tmp/` directory, and explicitly use copy linking.

> [!TIP]
> **Recommended Alternative:** To avoid formatting-sensitive command prefix checks and prevent accidental local `.venv` creation, use the provided `Makefile`:
> ```bash
> make <target>
> ```
> For example: `make test` or `make lint`. The `Makefile` automatically exports the required environment variables.

If running `uv` directly, you must use this exact multiline prefix structure:
```bash
UV_PROJECT_ENVIRONMENT=${HOME}/.local/venvs/hibp-download \
UV_CACHE_DIR=/tmp/.uv-cache-hibp-download \
UV_LINK_MODE=copy \
uv <command>
```

Failure to use this prefix may result in a `.venv` being created in the workspace, which is strictly prohibited.
