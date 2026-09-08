# Stateful agent runtimes

**One video, about thirty minutes.** The loop you write by hand, and the three ways it goes wrong in
production.

Everything in this vault rests on one idea: **the model decides, your code executes.** A model never
does anything. It returns a decision as data, and your harness chooses whether to act on it. Most
production incidents in this course come from forgetting that.

| Sub-module | What breaks | Domain |
|---|---|---|
| `01-the-harness-and-the-model.ipynb` | A policy written in the prompt, obeyed to the letter, for 47500 cents | Card chargebacks |
| `02-finish-reason-as-a-state-machine.ipynb` | A truncated answer read as a finished one | Formula 1 race strategy |
| `03-tool-results-and-idempotency.ipynb` | A retry that orders the same scan twice | Medical imaging triage |
| `04-capstone-a-runtime-that-survives.ipynb` | All three, in one runtime that can be restarted | Port logistics |

## Before you start

Run `00-setup/01-start-here.ipynb` first. Every notebook here runs without an API key, from
committed recordings, so you can read and execute the whole vault for free.

## What you will have built

A small agent runtime that parses what the model asked for, checks it against state you control,
executes only what passes, survives a restart without repeating an action, and carries a test for
each of those properties.
