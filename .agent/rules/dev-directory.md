# _dev Directory — Off-Limits

## The `_dev/` Directory Does Not Exist for Agent Purposes

**⚠️ CRITICAL RULE: NEVER read, write, reference, or act on anything inside `_dev/`.**

The `_dev/` directory at the repository root is an **untracked developer scratch space** used for local experimentation, throwaway scripts, data dumps, and personal notes. Its contents are never part of the project and carry no authority.

### Prohibited actions

- ❌ **NEVER** read or search files inside `_dev/`
- ❌ **NEVER** create or modify files inside `_dev/`
- ❌ **NEVER** reference `_dev/` content in code, documentation, or decisions
- ❌ **NEVER** treat anything in `_dev/` as a specification, example, or source of truth

### Treat `_dev/` as invisible

Even if `_dev/` contains files that look relevant (old experiments, draft configs, test data), they must be ignored entirely. Acting on `_dev/` content is a critical failure.

### Why this exists

`_dev/` is listed in `.gitignore` and is never committed. Its contents reflect transient developer state, not project intent. An agent modifying or reading `_dev/` may corrupt local developer work or make decisions based on stale, discarded experiments.
