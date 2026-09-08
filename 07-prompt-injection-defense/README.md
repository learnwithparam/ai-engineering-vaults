# Prompt injection defense

**One video, about thirty minutes.** Why untrusted text becomes an instruction, why the obvious fix
only partly works, and what you put behind it.

Everything in this vault rests on one idea: **a prompt level defence has a pass rate, not a
guarantee.** Every number below was printed by a live model, not asserted.

| Sub-module | What breaks | Domain |
|---|---|---|
| `01-untrusted-text-becomes-instruction.ipynb` | A CV that sounds like the platform moves its own score from 3 to 10 | Recruiting screening |
| `02-injection-through-tools-and-retrieval.ipynb` | A public label clears a sanctioned address, through a tool result nobody typed | Onchain analytics |
| `03-capstone-a-screener-with-a-suite.ipynb` | A defended screener, scored against a corpus, blocking 11 attack runs of 18 | Legal ediscovery |

## Before you start

Run `00-setup/01-start-here.ipynb` first. Every notebook here runs without an API key, from
committed recordings, so you can read and execute the whole vault for free.

## What you will have built

A screener that keeps the decision in code rather than in the prompt, a guard that refuses any
verdict the verified fields do not support, and an attack corpus that puts a number on your defence
instead of a claim.
