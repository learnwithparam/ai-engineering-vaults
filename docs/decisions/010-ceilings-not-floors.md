# 010: Ceilings, a definition may follow its term, and money is said aloud

Reverses two rules from 008 and 009.

## Why

The vault notebooks passed every gate and still read badly. Three defects were measured:

- 29 of 43 sentences that introduce a bold term ran over 28 words, because `score.py` required the
  definition in the same sentence, so the glossary text was pasted in as an appositive.
- 18 currency figures, such as `$0.0000479`, could not be said on a screencast.
- 23 of 126 steps opened with no word connecting them to the step before.

`voice.md` says to introduce a term by contrast, problem first. The gate forbade that. And
`MIN_MEAN_SENTENCE` and `MAX_SHORT_SHARE` were a floor and a target average, which
`voice.md` bans, because a floor is what made the earlier text robotic.

## Decision

- The glossary definition may sit in the first-use sentence or the one right after it.
- The mean-sentence floor and the short-sentence share are removed. Two fragments in a row still
  fail, and a single short beat after an explanation is allowed.
- `score.py` enforces 28 words a sentence and 4 sentences a paragraph, read from `config/banned.yml`.
  The numbers are a copy of `house-rules.md`, and `check-prose` fails when they drift.
- A dollar figure in prose fails with more than two decimal places or three significant digits.
  The cell output still prints the exact figure.
- The rewrite of all 14 notebooks changed markdown cells only, so the recorded fixtures still replay.

## Enforcement

`scripts/score.py` (`_flow`, `_speakable`), `scripts/check_prose.py` (`rules_stale`) and
`scripts/check_gates.py`, which plants a 29-word sentence, a 5-sentence paragraph, `$0.0000479`, a
ceiling edited out of step with `house-rules.md` and a definition two sentences late.
