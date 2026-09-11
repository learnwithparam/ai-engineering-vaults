# Token Economics Optimization for AI System Architects

One course in one notebook: `01-classify-tickets-on-a-token-budget.ipynb`.

You build a classifier for a support desk that handles a high volume of tickets. Each ticket
arrives with a long history, and most of that history is the logs of sub-tasks that already
finished. An orchestrator reads the ticket once, three workers each decide one thing about it, and
a synthesis step writes the routing line.

The notebook starts with a chain that hands the whole history to every worker, measures what each
handoff costs, then grows it one step at a time into a pipeline that prunes finished logs, keeps
their results as a small key-value state, refuses to run a worker on missing state, and runs the
workers in parallel.

## Before you start

Run `00-setup/01-start-here.ipynb` first. The notebook runs without an API key, from committed
recordings of real responses, so you can follow the whole course for free. Every price it prints
comes from `provider-truth.json`, never from memory.

## What you will have built

A ticket triage pipeline whose cost per ticket and wall clock you can predict, with tests for its
pruning, its state check and its latency math, all of which run without calling the model.
