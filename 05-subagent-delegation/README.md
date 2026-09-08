# Subagent delegation

**One video, about thirty minutes.** Why you hand work to a second agent, how two frameworks draw the
line, and what has to come back across it.

One idea holds the vault together: **the parent grows by the summary, not by the work.** A subagent is
a second agent run with its own list of messages. It reads everything, and the only thing that
survives it is the line you copy back.

| Sub-module | What breaks | Domain |
|---|---|---|
| `01-why-delegate-at-all.ipynb` | Three applicant packets read inline, and the parent turn costs 2583 tokens instead of 104 | Candidate screening |
| `02-two-ways-to-delegate.ipynb` | A shared LangGraph state means the worker writes its log into the parent, and an undeclared CrewAI task output hands a truncated log across | Genomics pipeline |
| `03-capstone-a-delegated-migration.ipynb` | A worker replies with a summary a person could read and a commander cannot parse | Warehouse robotics |

## Before you start

Run `00-setup/01-start-here.ipynb` first. Every notebook here runs without an API key, from committed
recordings, so the whole vault executes for free.

LangGraph and CrewAI both make their own calls, which the recordings do not capture. Both notebooks
route every call through the vault client instead, so a crew and a graph replay offline exactly like
any other lesson. The CrewAI cell also switches off first run consent, telemetry and tracing, which
otherwise phone home and can stop to ask a question.

## What you will have built

A delegation boundary you can point at. A worker state that holds the noise, a parent state with no
channel for it, a typed result contract the parent can branch on without reading anything, and a test
for each of those properties that needs no model and runs in milliseconds.
