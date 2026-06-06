# Release & Versioning Workflow

Guidelines for updating the package version and building release distributions.

## Versioning Scheme

This project uses **Semantic Versioning (SemVer)**: `MAJOR.MINOR.PATCH`.
Version strings are defined authoritatively in:
1. `pyproject.toml` (`[project]` and `[tool.poetry]` tables)
2. `src/hibp_downloader/__init__.py` (`__version__` string)

To prevent clobbering existing packages in the build destination (`dist/`), the version's **patch** number must be bumped before compiling a new build.

---

## Bumping the Version

A helper script is provided at `.agent/workflows/scripts/bump_semver_patch.py` to automate version incrementing.

### 1. Automatic Bumping (Recommended)
Running the `make build` target automatically runs the version bump script before calling `uv build`.
```bash
make build
```

### 2. Manual Bumping
If you need to bump the version without compiling a package immediately, run the script directly:
```bash
make run -- .agent/workflows/scripts/bump_semver_patch.py
```
Or use the direct sandboxed `uv` command:
```bash
UV_PROJECT_ENVIRONMENT=${HOME}/.local/venvs/hibp-download \
UV_CACHE_DIR=/tmp/.uv-cache-hibp-download \
UV_LINK_MODE=copy \
uv run python .agent/workflows/scripts/bump_semver_patch.py
```

---

## How the Script Works

The `bump_semver_patch.py` script:
1. Locates `pyproject.toml` and `src/hibp_downloader/__init__.py`.
2. Parses the `version` field in `pyproject.toml`.
3. Parses the version into `major`, `minor`, and `patch` integers.
4. Increments the `patch` digit by 1.
5. Performs regular expression replacements on both metadata files to write the updated version string.
