# 003: Four sub-modules per vault, not five

Date: 2026-09-08
Status: accepted

## What the measurement said

The first sub-module was written to the depth the course promises: a real failure measured over six
attempts, a diagnosis, a measured fix, and a production build. It came out at 947 words of prose and
104 lines of code, which the estimator puts at 11.2 minutes of video.

Five of those is 56 minutes. The budget is 30.

## The two ways out

Cut each sub-module to six minutes, or cut the count. Trimming a dense lesson by 45% removes the
measurement and the production build, which are the parts that make it worth more than a blog post.
The count is the cheaper thing to lose.

## Decision

**Four sub-modules per vault: three teaching, one capstone.** Target roughly 7 minutes each, so a
vault lands near 28 minutes with headroom.

Working shape per sub-module, which the scorer now enforces as a budget rather than as a rule:

| | Target |
|---|---|
| Prose | about 550 words |
| Code | about 60 lines across 6 or 7 cells |
| Outputs | 4 or 5 |

Twelve vaults, forty eight notebooks.

## Why this is the better answer

"Concise yet full coverage" is a real constraint, and three sharp lessons plus a capstone cover a
topic better than five thin ones. The cut falls on repetition, not on depth.

## What changes

`docs/CONTRACT.md` says four, and `check_structure.py` asserts four. The estimator gains a per cell term,
because introducing a cell costs time whatever its length, and a fifteen line schema is not read out
line by line.
