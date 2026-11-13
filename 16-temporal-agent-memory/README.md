# Serve Current Facts with a Temporal Memory Store

One course in one notebook: `01-serve-current-facts-with-a-temporal-memory-store.ipynb`.

You build the memory for a support assistant at a B2B software company. The assistant remembers
facts about each customer account, such as the plan, the renewal owner and the support tier. Those
facts change, so the course stores each one with the dates it was true, and then answers what was
true on the day a question asks about. Other vaults in this repository keep a chat log short or keep
a paused run on disk. None of them keep facts that change over time, and this one never trims or
summarises history. It only ever closes a fact and adds the one that replaces it.

## Before you start

No API key is needed. The notebook makes no model call, so every cell runs on your own machine.

## What you will have built

A dated fact store for three customer accounts, an as-of lookup that answers what was true on a given
day, a context builder that gives the assistant only the facts that are true, and tests that show the
dated store serves no stale answers while a plain list of notes serves some.
