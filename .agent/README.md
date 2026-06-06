# Agent Instructions

**Welcome!** This directory contains guidance for AI coding agents (Claude Code, Google Antigravity, etc.) working with this project.

## Critical Rules

Read every rule file before starting any task. Violating any of these is a critical failure.

| Rule | Summary |
|:-----|:--------|
| **[environment.md](rules/environment.md)** | Never create a local `.venv`. Always prefix `uv` commands with virtual environment and cache path overrides or use the `Makefile`. |
| **[dev-directory.md](rules/dev-directory.md)** | Treat `_dev/` as invisible. Never read, write, or reference anything inside it. |
| **[conventions.md](rules/conventions.md)** | Strict coding conventions regarding formatting, type hints, imports, CLI loading, logging, and exceptions. |

## Quick Start

When starting a task on this repository, orient yourself by reading in this order:

1. **`rules/`** — All rule files (see table above). Read these first, every session.
2. **`context/architecture-decisions.md`** — Architectural choice records (ADRs).
3. **`workflows/development.md`** — CLI usage commands for the development environment.

## Instruction Files

### Development Guidelines
- **[Coding Standards](rules/conventions.md)**: Rules for logging, type annotations, Typer CLI structure, and async design.
- **[Development Workflow](workflows/development.md)**: Guidelines for testing, linting, formatting, and running using the `Makefile` or direct sandboxed `uv` commands.
- **[Release & Versioning Workflow](workflows/release-process.md)**: Guidelines for version bumping and compiling packages.

## Documentation Hierarchy

The `.agent` directory is logically separated by concern:
- `README.md` (this file): Index and entry point. Rules are in `rules/`, not here.
- `context/`: System architectures, technical decision records (ADRs).
- `rules/`: Strict, non-negotiable constraints. Each rule has ONE authoritative file.
- `workflows/`: Actionable workflows and CLI command examples.
- `skills/`: Agent-specific persona definitions and advanced capabilities.

## Technical Documentation
- **[Architecture Decisions](context/architecture-decisions.md)**: Historical decision records (ADRs).

## Active Skills

These skills define personas and specialized expertise available to agents:

| Skill | Purpose |
|:------|:--------|
| **[architect-review](skills/architect-review/SKILL.md)** | Master software architect specializing in modern architecture patterns, clean architecture, and DDD. |
| **[caveman](skills/caveman/SKILL.md)** | Ultra-compressed communication mode. Cuts token usage ~75%. |
| **[code-reviewer](skills/code-reviewer/SKILL.md)** | Elite code review expert for quality, performance, and security. |
| **[karpathy-guidelines](skills/karpathy-guidelines/SKILL.md)** | Behavioral guidelines to reduce common LLM coding mistakes. |
| **[python-patterns](skills/python-patterns/SKILL.md)** | Python development principles and decision-making guidance. |
| **[python-pro](skills/python-pro/SKILL.md)** | Master Python 3.13+ features, async, and performance optimization. |
| **[vulnerability-scanner](skills/vulnerability-scanner/SKILL.md)** | Advanced vulnerability analysis (OWASP, supply chain, risk). |

## Key Principles

- **No duplication** — Each concept has ONE authoritative location.
- **Cross-reference** — Link to details instead of copying content.
- **Modern Tooling**: Use `uv` with `pdm-backend` for packaging, `ruff` for formatting/linting, and `pytest` for unit testing.
- **Sandboxed Environment**: Do not create or poll workspace `.venv` files. Use the `Makefile` wrappers.
