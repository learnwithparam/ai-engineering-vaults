# Low entropy tool design

**One video, about thirty minutes.** How a tool suite grows until the model can no longer tell your
tools apart, what that costs at the backend, and how to score a suite instead of arguing about it.

One idea runs through all three: **a tool suite is a design decision you can measure.** Names and
descriptions are read by the model as words. Only a schema and your own code are checked by anything.

| Sub-module | What breaks | Domain |
|---|---|---|
| `01-too-many-tools.ipynb` | Nine questions cost 123 backend calls once the suite reaches 24 tools | Customer success |
| `02-descriptions-are-not-guardrails.ipynb` | A rule in a description holds for the state it names and fails for the next one | Satellite operations |
| `03-capstone-a-scored-tool-suite.ipynb` | One instruction to cut bids turns three different dials | Real time bidding |

## Before you start

Run `00-setup/01-start-here.ipynb` first. Every notebook here runs without an API key, from committed
recordings, so you can read and execute the whole vault for free.

## What you will have built

A tool catalogue with one owner per answer, a harness cap on how many calls one turn may run, an
activation check that compares a claim against telemetry before anything executes, and an eval that
scores a suite and fails the build when the score drops.
