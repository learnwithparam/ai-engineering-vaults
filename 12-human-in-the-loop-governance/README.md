# Human-in-the-Loop Governance for High-Risk AI Actions

One course in one notebook: `01-build-an-approval-gate.ipynb`.

You build the runtime for an infrastructure automation agent that manages a company's databases.
Engineers ask it to take backups and remove databases nobody uses. The model decides what to do,
but your runtime decides what actually runs, so a request to delete a production database stops
and waits for an administrator before anything happens.

The notebook starts with an agent that deletes whatever the model asks for, then grows it one step
at a time: a risk tier for every tool call, a hook that intercepts high-risk calls before they run,
refusals the model can read, a pause that is saved to disk and resumed by its thread id after a
restart, a check that stops a model repeating the same call, and an audit trail that names who
allowed each change.

## Before you start

Run `00-setup/01-start-here.ipynb` first. The notebook runs without an API key, from committed
recordings of real responses, so you can follow the whole course for free.

## What you will have built

An approval gate for high-risk agent actions, with a test for each of its safeguards, all of which
run without calling the model.
