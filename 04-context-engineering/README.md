# Context engineering

**One video, about thirty minutes.** What goes into a request, in what order, and what happens to
the parts you left out.

Everything in this vault rests on one idea: **the request is built, not accumulated.** A prompt that
grows by appending is a prompt nobody owns. The three sub-modules take the three things that get
appended without thought, and give each of them a decision and a check.

| Sub-module | What breaks | Domain |
|---|---|---|
| `01-rules-that-only-load-when-they-apply.ipynb` | Every rule loaded for every task, so the model follows one written for a file nobody touched | Visa and residency casework |
| `02-what-a-summary-throws-away.ipynb` | A summary keeps the story and loses the lot id, and the next step answers anyway | Semiconductor yield |
| `03-capstone-a-context-assembler.ipynb` | A budget filled newest first, so the learner record never made it into the request | Learner progress |

## Before you start

Run `00-setup/01-start-here.ipynb` first. Every notebook here runs without an API key, from
committed recordings, so you can read and execute the whole vault for free.

The rule files in the first sub-module are written to a temporary folder by the notebook itself and
are not committed. Nothing in this vault edits the repository.

## What you will have built

A resolver that turns a list of changed paths into the rules that apply and what each one costs, a
compaction step that pins exact identifiers outside the part a summary is allowed to rewrite, and an
assembler that puts all four blocks in a deliberate order under a budget it refuses to exceed.
