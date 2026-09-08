# 001: The dependency set resolves as one lockfile

Date: 2026-09-08
Status: accepted

## The question

The plan named one risk above all others: CrewAI pins hard, and might not sit beside LangGraph and
Pydantic AI in a single environment. If it did not, vault 5 would lose its CrewAI contrast and the
plan would change.

## What was actually run

    uv lock     # resolved 232 packages
    uv sync
    uv run python -c "import each module"

## Result

It resolves and it imports. No conflict.

| Package | Resolved |
|---|---|
| openai | 2.54.0 |
| pydantic | 2.12.5 |
| pydantic_ai (via pydantic-ai-slim) | 2.41.0 |
| langchain_openai | 1.6.1 |
| langchain_core | 1.6.2 |
| crewai | 1.15.20 |
| langgraph, mcp, dotenv | installed, no `__version__` attribute exposed |

Python 3.11.14.

## Decision

Keep the full framework spread. Vault 5 ships both the LangGraph subgraph and the CrewAI contrast as
planned. No optional dependency group, so `make setup` installs everything a learner needs in one
command and the first run cannot half work.

`pydantic-ai-slim` is used rather than `pydantic-ai`, because the full package pulls every model
provider and this repo only needs the OpenAI-compatible path for OpenRouter.

## What would reopen this

A future bump where CrewAI and LangChain disagree on a shared pin. The lockfile is committed, so that
surfaces as a failed `uv lock`, not as a broken clone.
