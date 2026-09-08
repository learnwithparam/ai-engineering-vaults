# 005: Three sub-modules per vault, and the budget decides

Date: 2026-09-08
Status: accepted, supersedes the count in 003

## What three trim passes established

Vault 1 was written to seven beats and trimmed three times. It measured 37.3, then 35.3 minutes
against a 30 minute budget. Prose trimming had clearly stopped paying: the remaining time is code,
and the code is the lesson.

The arithmetic is stable. Four sub-modules at this depth is 35 minutes. Three is 27.

| | Four sub-modules | Three sub-modules |
|---|---|---|
| Measured | 35.3 min | about 26.5 min |
| Verdict | over budget | fits, with headroom |

## Decision

**A vault is three sub-modules: two teaching and one capstone.** Twelve vaults, thirty six notebooks.

`check_structure.py` accepts three or four, because the real constraint is the thirty minute budget
and the scorer already enforces that. A vault of four genuinely short sub-modules is fine. A vault of
four at this density is not, and the gate says so.

## What this cost

Vault 1's idempotency and durability lessons merge into one capstone, "actions that survive". They
were always the same argument: an action must survive a retry, and it must survive a restart. Holding
them apart was a structure decision, not a teaching one.

## Why not raise the budget instead

Thirty minutes was an explicit requirement, not a guess. A course that quietly ships 35 minute videos
against a 30 minute promise has broken the promise, and the gate exists to stop exactly that.
