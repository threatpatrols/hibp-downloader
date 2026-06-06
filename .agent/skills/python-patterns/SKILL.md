---
name: python-patterns
description: Python development principles and decision-making. Framework selection, async patterns, type hints, project structure. Teaches thinking, not copying.
allowed-tools: Read, Write, Edit, Glob, Grep
---

# Python Patterns

> Python development principles and decision-making for 2026.
> **Learn to THINK, not memorize patterns.**

---

## ⚠️ How to Use This Skill

This skill teaches **decision-making principles**, not fixed code to copy.

- ASK user for framework preference when unclear
- Choose async vs sync based on CONTEXT
- Don't default to same framework every time

---

## 1. Framework & Core Tooling Selection (2026)

### Core Developer Toolchain (Modern Standards)

In 2026, the modern Python workflow is unified and extremely fast:
- **Environment & Dependency Management**: **`uv`** is the standard. Replace `pip`, `venv`, `pipenv`, and `poetry`. Run workspaces, install packages, and manage Python versions via `uv`.
- **Linting & Formatting**: **`Ruff`** is the consolidated de facto linter and formatter. Replace `black`, `isort`, `flake8`, and `pyupgrade`. Configure it in `pyproject.toml`.
- **Performance Workloads**: Use **`Polars`** instead of `Pandas` for performance-critical data analysis (Rust-powered, lazy evaluation, Arrow-backed). Use **`DuckDB`** for serverless, embedded SQL analytical queries.

### Framework Decision Tree

```
What are you building?
│
├── API-first / Microservices
│   ├── FastAPI (async, modern, standard validation via Pydantic v2)
│   └── Litestar (async, high-performance, strictly typed alternative)
│
├── Full-stack web / CMS / Admin
│   └── Django 5.2/6.0+ (batteries-included, async-capable)
│
├── Simple / Script / Utility
│   └── Single-file Python script + PEP 723 inline metadata (run via `uv run`)
│
├── AI/ML API serving / GenAI Agents
│   └── FastAPI / Pydantic-AI (type-safe structured outputs)
│
└── Background workers
    └── Taskiq / ARQ (async-first) or Celery (enterprise legacy)
```

### Comparison Principles

| Factor | FastAPI / Litestar | Django 5.2+ | PEP 723 Single-File |
|--------|---------|--------|-------|
| **Best for** | APIs, microservices, GenAI | Full-stack monoliths, CMS | Scripts, utilities, tooling |
| **Package Manager** | `uv` | `uv` | `uv run` (ephemeral env) |
| **Async Support** | Native, async-first | Native async views & ORM queries | Synchronous or async |
| **Admin Panel** | Manual | Built-in (highly extensible) | N/A |
| **ORM** | Choose your own (SQLAlchemy, SQLModel) | Django ORM (async-capable) | N/A / SQLObject / Peewee |
| **Learning Curve** | Low to Medium | Medium | Low |

### Selection Questions to Ask:
1. Is this API-only or full-stack?
2. Do you need a built-in admin panel or user-auth batteries included (Django)?
3. Are the background operations I/O-bound (async-first) or CPU-bound?
4. Are you writing a quick utility or a structured application?

---

## 2. Concurrency: Async, Sync, and Parallelism (Python 3.13 / PEP 703)

### The Concurrency Matrix

How to select the right tool based on your runtime and workload:

| Workload Type | GIL-Enabled Python (Standard) | Free-Threaded Python 3.13 (`python3.13t`) |
| :--- | :--- | :--- |
| **I/O-bound** (APIs, DBs, Net) | Use `async` (`asyncio`, `httpx`, `asyncpg`) | Use `async` or multi-threaded `ThreadPoolExecutor` |
| **CPU-bound** (Heavy math, parsing) | Use `multiprocessing` (bypasses GIL overhead) | Use standard `threading` / `ThreadPoolExecutor` (true parallelism) |

---

### Python 3.13 Free-Threaded Concurrency (PEP 703)

In Python 3.13, you can run Python without the Global Interpreter Lock (GIL) via experimental free-threaded builds (`python3.13t`). 

#### Implications for CPU-bound Code:
*   **Without GIL**: You no longer need the high-overhead `multiprocessing` module (and complex IPC serialization) to scale CPU work across multiple cores. You can use standard `threading.Thread` or `concurrent.futures.ThreadPoolExecutor`.
*   **Thread Safety is Crucial**: Without the GIL, data races can happen at the application level. Standard types (`list`, `dict`, `set`) have internal lock protection, but compound operations (e.g. `if key not in d: d[key] = val`) are NOT atomic. You MUST use synchronization primitives (`threading.Lock`) to safeguard shared mutable state.

---

### When to Use Async (`async def`)

```
async def is better when:
├── High-concurrency I/O (handling thousands of connections)
├── WebSockets / Real-time event streaming
├── Microservice aggregation/mesh (frequent external HTTP calls)
└── Modern frameworks (FastAPI, Litestar, Django ASGI)

def (sync) is better when:
├── CPU-bound computing (if on standard GIL build)
├── Legacy sync codebases / Single-run scripts
├── Synchronous CLI tools and simple utilities
└── Blocking client libraries that have no robust async version
```

### Modern Async Library Selection

| Need | Standard Async Library (2026) | Notes |
|------|---------------|---|
| **HTTP Client** | `httpx` | Support for HTTP/2, replaces `requests` and `aiohttp` |
| **PostgreSQL** | `asyncpg` or `psycopg` (v3 async) | `psycopg` v3 has native async and connection pooling |
| **Redis** | `redis.asyncio` | Built into the official `redis` package (no separate `aioredis` needed) |
| **File I/O** | `aiofiles` or `anyio` | Bypasses local disk blocking in event loops |
| **Database ORM** | `SQLAlchemy 2.x async` or `SQLModel` | Standardized async session wrappers |

---

## 3. Modern Type Hints & Domain Modeling (Python 3.13)

### When to Type

```
Always type:
├── Function parameters and return values
├── Domain models & Data Transfer Objects (DTOs)
├── Public interface signatures (APIs, library entry points)
└── Class attributes

Can skip:
├── Local variables (let type inference do the work)
├── Ephemeral internal helper variables
└── Simple test scripts
```

### Modern Generic Syntax & Defaults (PEP 695 & 696)

Python 3.12+ introduced the new `type` statement and simplified generic syntax, and Python 3.13 added Type Parameter Defaults:

```python
# Modern Type Aliases (PEP 695)
type JsonValue = str | int | float | bool | None | dict[str, 'JsonValue'] | list['JsonValue']

# Modern Generics syntax (PEP 695)
# No need to import TypeVar manually!
class Box[T]:
    def __init__(self, content: T):
        self.content = content

# Generic Functions
def first[T](items: list[T]) -> T:
    return items[0]

# Generic Type Defaults (PEP 696 - Python 3.13)
# Specify a default fallback type directly in the generic signature
class Stack[T = int]:
    def __init__(self) -> None:
        self.items: list[T] = []
```

### Type Narrowing and Immutable Dictionaries (PEP 742 & 705)

Use the latest typing constructs to provide richer data safety checks:

```python
from typing import TypeIs, TypedDict, ReadOnly

# 1. Type Narrowing with TypeIs (PEP 742 - Python 3.13)
# Prefer TypeIs over TypeGuard. TypeIs narrows in BOTH branches (True/False):
def is_str_list(val: list[object]) -> TypeIs[list[str]]:
    return all(isinstance(x, str) for x in val)

def process(items: list[object]) -> None:
    if is_str_list(items):
        # type checker knows items is list[str] here
        print(", ".join(items))
    else:
        # type checker knows items is NOT list[str] here
        pass

# 2. Read-Only TypedDict Keys (PEP 705 - Python 3.13)
# Enforce read-only rules for dictionaries at static analysis time:
class UserConfig(TypedDict):
    id: int
    username: ReadOnly[str]  # username cannot be reassigned/mutated
    email: str
```

### API Deprecation Warnings (PEP 702 - Python 3.13)

Use `@warnings.deprecated` to flag deprecated code. Static checkers (like Pyright/Mypy) will warn developers, and runtime calls will raise deprecation warnings.

```python
from warnings import deprecated

@deprecated("Use fetch_user_by_uuid() instead.")
def get_user_old(user_id: int) -> dict:
    ...
```

### Data Modeling: Dataclasses & Pydantic v2

Avoid raw, untyped dictionaries (`dict`) for business logic payloads. Instead, use static DTOs:

*   **Pydantic v2**: Standard for external-facing boundary models, APIs, and settings. Offers Rust-powered validation speed and rich runtime enforcement.
*   **Dataclasses**: Standard for internal domain modeling, services logic, and lightweight containers. Use `frozen=True` to create immutable domain structures.

---

## 4. Modern Project Structure & Inline Metadata

### Structure Selection

#### 1. Small Utility / Single-File Script (PEP 723)
For standalone scripts, do not use `requirements.txt`. Define dependencies inline using **PEP 723** metadata, and run it with `uv run`:

```python
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "httpx",
#     "rich",
# ]
# ///

import httpx
from rich import print

response = httpx.get("https://api.github.com")
print(response.json())
```
*Run via:* `uv run script.py`

---

#### 2. Medium API (Feature-Based / Modular Monolith)
Prefer organizing by domain feature/bounded context rather than technical layers. This keeps relevant code together and improves modularity:

```
my_app/
├── core/                   # Shared config, logging, telemetry, DB connection
├── users/                  # Users feature module
│   ├── routes.py           # HTTP endpoints
│   ├── services.py         # Business domain logic
│   ├── repository.py       # Data access implementation
│   └── models.py           # Dataclasses/Pydantic schemas
├── products/               # Products feature module
│   ├── routes.py
│   ├── services.py
│   └── ...
├── tests/                  # Integration and unit tests
├── pyproject.toml          # Workspace configuration
└── uv.lock                 # Managed dependency lockfile
```

---

### Clean Architecture & DDD Layout (Large Application)
For larger domain-driven apps, keep the business domain pure, isolating infrastructure details behind interface/protocol boundaries:

```
src/myapp/
├── domain/                 # Pure domain business logic (no DB / framework dependencies)
│   ├── models.py           # Core dataclasses / value objects
│   └── interfaces.py       # Protocols (e.g. UserRepository interface)
├── services/               # Application coordination (use-cases)
├── infrastructure/         # External tools implementation
│   ├── database/           # SQLAlchemy models / connection code
│   └── repositories/       # Database implementations of interfaces
├── api/                    # API delivery layer (FastAPI routes)
└── main.py                 # Application bootstrap and DI container wiring
```

#### The Dependency Rule:
Outer circles (Infrastructure, API) can depend on inner circles (Services, Domain). Core Domain must have **zero** dependencies on outer layers (e.g. domain models should not import SQLAlchemy or FastAPI).

---

## 5. Django Principles (2026)

### Django Async (Django 5.2/6.0+)

```
Django supports async:
├── Async views
├── Async middleware
├── Async ORM (limited)
└── ASGI deployment

When to use async in Django:
├── External API calls
├── WebSocket (Channels)
├── High-concurrency views
└── Background task triggering
```

### Django Best Practices

```
Model design:
├── Fat models, thin views
├── Use managers for common queries
├── Abstract base classes for shared fields

Views:
├── Class-based for complex CRUD
├── Function-based for simple endpoints
├── Use viewsets with DRF

Queries:
├── select_related() for FKs
├── prefetch_related() for M2M
├── Avoid N+1 queries
└── Use .only() for specific fields
```

---

## 6. FastAPI Principles

### async def vs def in FastAPI

```
Use async def when:
├── Using async database drivers
├── Making async HTTP calls
├── I/O-bound operations
└── Want to handle concurrency

Use def when:
├── Blocking operations
├── Sync database drivers
├── CPU-bound work
└── FastAPI runs in threadpool automatically
```

### Dependency Injection

```
Use dependencies for:
├── Database sessions
├── Current user / Auth
├── Configuration
├── Shared resources

Benefits:
├── Testability (mock dependencies)
├── Clean separation
├── Automatic cleanup (yield)
```

### Pydantic v2 Integration

```python
# FastAPI + Pydantic are tightly integrated:

# Request validation
@app.post("/users")
async def create(user: UserCreate) -> UserResponse:
    # user is already validated
    ...

# Response serialization
# Return type becomes response schema
```

---

## 7. Background Tasks & Orchestration (2026)

### Selection Guide

| Solution | Async Support | Best For | Pros & Cons |
| :--- | :--- | :--- | :--- |
| **FastAPI BackgroundTasks** | Native | In-process, simple notifications, fire-and-forget | 🟢 No external broker needed<br>🔴 Runs in the app process (blocking/failures lose task) |
| **Taskiq** | Native | Greenfield async-first projects, type-safe APIs | 🟢 Native async, type-safe, clean Pydantic integration<br>🔴 Smaller ecosystem than Celery |
| **ARQ** | Native | Lightweight async-first jobs, Redis-backed | 🟢 Very low overhead, easy to configure<br>🔴 Redis-only, lacks complex workflow tooling |
| **Celery** | Limited | Complex DAGs, multi-language/enterprise stacks | 🟢 Massive ecosystem, robust monitoring (Flower), rich workflows<br>🔴 Extremely complex configuration, sync/async bridging friction |

### When to Use Which

```
FastAPI BackgroundTasks:
├── Quick, non-critical operations (e.g. sending a single welcome email)
├── No persistence or task recovery needed
└── Same-process thread execution

Taskiq or ARQ:
├── Modern async-first architectures (e.g. FastAPI / Litestar APIs)
├── Tasks that are primarily I/O-bound (scraping, API integrations)
├── Requires type-safe signatures and native async/await
└── Redis Streams / Redis Queue infrastructure

Celery:
├── Complex distributed tasks and pipeline structures (DAGs, chords, chains)
├── Heavy multi-process workloads (CPU or memory intensive tasks)
├── Needs robust task scheduling and dashboard monitoring (Flower)
└── Legacy applications / Synchronous web frameworks
```

---

## 8. Error Handling Principles

### Exception Strategy

```
In FastAPI:
├── Create custom exception classes
├── Register exception handlers
├── Return consistent error format
└── Log without exposing internals

Pattern:
├── Raise domain exceptions in services
├── Catch and transform in handlers
└── Client gets clean error response
```

### Error Response Philosophy

```
Include:
├── Error code (programmatic)
├── Message (human readable)
├── Details (field-level when applicable)
└── NOT stack traces (security)
```

---

## 9. Testing Principles

### Testing Strategy

| Type | Purpose | Tools |
|------|---------|-------|
| **Unit** | Business logic & Pure domain functions | `pytest` |
| **Integration** | API endpoints & Database repositories | `pytest` + `httpx.ASGITransport` + Test Database |
| **E2E / System** | Full multi-component flows | `pytest` + `Testcontainers` (for ephemeral DBs/Redis) |

### Modern Async API Testing

In 2026, passing the `app` directly to `httpx.AsyncClient` is deprecated/removed. You must explicitly use `httpx.ASGITransport(app=app)`. Additionally, modern `pytest-asyncio` configurations run in `auto` mode, meaning `@pytest.mark.asyncio` can often be inferred, but explicitly declaring it on async tests remains standard practice.

```python
import pytest
import httpx
from myapp.main import app

@pytest.mark.asyncio
async def test_endpoint():
    # Pass app via ASGITransport
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/users")
        assert response.status_code == 200
```

### Testcontainers for Integration Testing
Avoid mocking database calls wherever possible. In 2026, the standard pattern for integration testing is to spin up real lightweight database instances using **`testcontainers`**:

```python
import pytest
from testcontainers.postgres import PostgresContainer

@pytest.fixture(scope="session")
def postgres_db():
    with PostgresContainer("postgres:16-alpine") as postgres:
        # Use postgres.get_connection_url() with asyncpg driver
        yield postgres.get_connection_url(driver="asyncpg")
```

---

## 10. Decision Checklist

Before implementing:

- [ ] **Asked user about framework preference?**
- [ ] **Chosen framework for THIS context?** (not just default)
- [ ] **Decided async vs sync?**
- [ ] **Planned type hint strategy?**
- [ ] **Defined project structure?**
- [ ] **Planned error handling?**
- [ ] **Considered background tasks?**

---

## 11. Anti-Patterns to Avoid

### ❌ DON'T:
- Default to Django for simple APIs (FastAPI may be better)
- Use sync libraries in async code
- Skip type hints for public APIs
- Put business logic in routes/views
- Ignore N+1 queries
- Mix async and sync carelessly

### ✅ DO:
- Choose framework based on context
- Ask about async requirements
- Use Pydantic for validation
- Separate concerns (routes → services → repos)
- Test critical paths

---

> **Remember**: Python patterns are about decision-making for YOUR specific context. Don't copy code—think about what serves your application best.
