# Multi-Agent Systems for Production AI Engineering

One course in one notebook: `01-build-a-code-audit-pipeline.ipynb`.

You build the audit pipeline an enterprise team runs on every pull request before it merges. An
orchestrator splits the audit into security, performance and style tasks, three workers review the
change at the same time in isolated contexts, and a synthesizer merges their findings into one
report. A router sends a small request to the one specialist it needs instead.

The notebook starts with one reviewer call as the number to beat, then grows it one step at a time
into a pipeline that keeps each worker's context separate, fans the workers out in parallel, merges
their findings, blocks the merge when a worker never ran, and routes small requests to a single
worker.

## Before you start

Run `00-setup/01-start-here.ipynb` first, and read `01-stateful-agent-runtime/` before this vault.
The notebook runs without an API key, from committed recordings of real responses, so you can
follow the whole course for free.

## What you will have built

A small code audit pipeline with a test for each of its safeguards, all of which run without
calling the model.
