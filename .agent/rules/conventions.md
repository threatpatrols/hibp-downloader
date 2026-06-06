# Code Style & Conventions

These are strict, non-negotiable guidelines for writing code in this repository.

## Python Conventions

- **Formatting**: Adhere to `ruff` configuration defined in `pyproject.toml` (target line-length: 120).
- **Type Hints**: Strict typing is required and verified via `mypy`. Use modern, native Python typing constructs where possible. Use `Annotated` for Typer options.
- **Imports**: Group imports into three sections (standard library, third-party, local package) and remove unused imports.
- **CLI Commands**: CLI commands are built using the `typer` library and are dynamically loaded from [commands](file:///home/ndejong/cyberco/projects/hibp-downloader/src/hibp_downloader/commands/). Do not statically register or import commands in `main.py`.
- **Async I/O**: Use `aiofiles` and `httpx` for all network/disk I/O bound tasks to prevent blocking the event loop.
- **Logging**: Do not use `print()` or raw `logging.getLogger()`. Always use `logger_get` from [logger.py](file:///home/ndejong/cyberco/projects/hibp-downloader/src/hibp_downloader/lib/logger.py).
- **Error Handling**: Custom exceptions must inherit from `HibpDownloaderException` (defined in [exceptions.py](file:///home/ndejong/cyberco/projects/hibp-downloader/src/hibp_downloader/exceptions.py)). Raise this exception for application-level failures.
- **Configuration**: Respect `pyproject.toml` settings. Do not modify configuration configurations unless explicitly instructed.
