# Multi-agent orchestration

When splitting one agent into several helps, when it hurts, and how to tell the difference with a
number rather than an opinion.

Everything here rests on one idea: **a second agent is a second bill and a second blind spot.** Fan
out buys isolation, and isolation is not free. Each sub-module measures what it bought.

| Sub-module | What breaks | Domain |
|---|---|---|
| `01-router-or-one-agent.ipynb` | One agent with five playbooks names the right one and runs nothing | Security operations |
| `02-workers-and-context-isolation.ipynb` | Worker analyses flood the parent, measured in tokens | Content moderation |
| `03-capstone-a-review-pipeline.ipynb` | The pipeline costs more, runs slower and is less correct than one call | Legal ediscovery |

## Before you start

Run `00-setup/01-start-here.ipynb` first, and read `01-stateful-agent-runtime/` before this vault.
Every notebook here runs without an API key, from committed recordings, so you can read and execute
the whole vault for free.

## What you will have built

A LangGraph router that classifies with no tools and acts with one, an orchestrator that fans out
with `Send` and bounds what each worker returns, and a review pipeline that was measured against a
single call and rebuilt around what the measurement said.
