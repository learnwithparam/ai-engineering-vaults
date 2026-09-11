# Context Engineering for AI Coding Agent Infrastructure

One course in one notebook: `01-assemble-agent-context.ipynb`.

You build the code that decides what a coding agent reads before it changes a full-stack monorepo,
with a React frontend in `src/ui` and an Express backend in `src/api`. An instruction file,
`AGENTS.md`, holds the build settings for every task, and a rule file scoped to `src/api/**/*.ts`
adds database safety checks only when backend code changes.

The notebook starts by sending every rule on every task, and measures what the backend rule costs
on a frontend task. It then grows the assembler one step at a time: it reads each rule's glob,
matches globs across folders the way the rule author meant, writes each instruction in exactly one
file, refuses a context over its budget, and summarises a long session without ever summarising the
rules.

## Before you start

Run `00-setup/01-start-here.ipynb` first. The notebook runs without an API key, from committed
recordings of real responses, so you can follow the whole course for free. It writes its monorepo
to a temporary folder and removes it in the last cell.

## What you will have built

A context assembler for a coding agent, with a test for each of its safeguards, all of which run
without calling the model.
