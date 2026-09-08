# Token economics

**One video, about thirty minutes.** What a call costs, what a handoff costs, and how to hold a
budget without dropping work on the floor.

One idea runs through all three: **you cannot control a bill you have never read.** Every number
here is printed from a real response. Nothing in this vault quotes a price from memory, and the
rates come from `build/provider-truth.json`, which `make probe` writes from the live API.

| Sub-module | What breaks | Domain |
|---|---|---|
| `01-measuring-the-bill.ipynb` | The model that is cheaper per token costs more per fault | Telecom faults |
| `02-the-token-tax-of-handoffs.ipynb` | A six step chain pays for the same log six times | Climate modelling |
| `03-capstone-a-classifier-under-budget.ipynb` | A batch goes over its ceiling and returns fewer labels | Retail demand |

## Before you start

Run `00-setup/01-start-here.ipynb` first. Every notebook here runs without an API key, from
committed recordings, so you can read and execute the whole vault for free.

Vault 1 is worth doing first. The capstone leans on `finish_reason`, which is taught there.

## What you will have built

A meter that reports cost per unit of work rather than cost per call, a chain that pays for its
evidence once and proves the digest kept what later steps need, and a batch that holds a hard
budget by degrading to cheaper answers rather than by stopping.

## Where this continues

`13-cost-and-latency-at-volume/` picks up where the counting stops: whether your model
caches, whether your work is shaped to overlap, and which lane a workload belongs in.

