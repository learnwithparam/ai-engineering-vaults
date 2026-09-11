# Building Stateful Agent Runtimes for AI Developers

One course in one notebook: `01-build-an-agent-runtime.ipynb`.

You build the runtime for a support agent at an online electronics store. The agent looks up orders
and issues refunds, so every mistake in the runtime costs real money. The model never runs anything
itself: it asks for a tool, and your runtime decides what actually happens.

The notebook starts with a single request, then grows it one step at a time into a loop that runs
tools, stops cleanly, enforces the refund limit in code, refuses a cut-off answer, and pays each
refund only once across retries and restarts.

## Before you start

Run `00-setup/01-start-here.ipynb` first. The notebook runs without an API key, from committed
recordings of real responses, so you can follow the whole course for free.

## What you will have built

A small agent runtime with a test for each of its safeguards, all of which run without calling the
model.
