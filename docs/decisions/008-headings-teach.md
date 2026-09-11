# 008: Headings teach, and sentences carry a whole thought

## Why

On 2026-09-11 the vault 1 pilot scored 100 and was rejected as unfit for teaching. These were the
reasons given:

- "Capstone, actions that survive, what does that even mean." The title named neither the concept
  (idempotency) nor the problem (a retry books the same scan twice).
- "Mechanics, what was it?" Every section heading was a label for the author: `## Mechanics`,
  `## The fix`, `## The gate`. The contract required those exact strings, because beats were found
  by heading.
- "Step 1: the naive build, about what?" Step titles had no subject: "why", "pin it", "where it
  breaks".
- "Read like a book without fatigue." The prose was staccato: "In the prompt." "Ask six times and
  count." "Not a better prompt." It also used invented metaphors in place of plain words: "the naive
  road is gone", "the timeout is honest".

The scorer measured none of this. Its language rules were a sentence length ceiling, a long-word
share, banned words and sentence case, and short fragments pass every one of them.

The reference is the four examples the user supplied and the viraloop shorts engine
(`internal-apps/studio/engines/viraloop`). Both use headings that make a claim, a hook before the
mechanics, one full sentence per idea, terms defined where they appear, and a closing recap.

## Decision

- A beat is found by the cell tag `beat:<name>`, not by its heading, so the heading can teach.
- A new hard dimension, `reading`, in `scripts/score.py`. A weighted average cannot outvote it.
  `docs/CONTRACT.md` lists its rules.
- Prose per notebook rises from 500 to 600 words, because full sentences, claim headings, the learn
  list and the recap cost about 100 words. That is still well under the 800 before decision 007.

## Calibration

Measured with `nbcommon.prose_blocks`, which drops headings, code, tables and images, and splits
list items into their own blocks.

| Sample | Sentences | Mean words | Under 6 words | Fragment pairs in a paragraph |
|---|---|---|---|---|
| The user's four examples | 214 | 14.6 | 14.0% | 0 |
| Vault 1 notebook 01, rejected | 48 | 9.5 | 21% | 1 |
| Vault 1 notebook 02, rejected | 52 | 8.6 | 24% | 2 |
| Vault 1 notebook 03, rejected | 49 | 9.4 | 21% | 2 |

So the floor is a mean of 12 words, and at most 15% of sentences may be under 6 words.

Flesch reading ease was measured and dropped. The examples score 29.9 because they are dense with
API vocabulary, and the rejected notebooks score about 77, so the measure rewards the wrong one.
The existing limit of 15% long words already covers vocabulary density.

## Enforcement

- `score.py` `score_reading`, with its word lists in `config/banned.yml`: `vague_titles`,
  `vague_headings` and `teaching_words`.
- `check_gates.py` plants `03-bad-reading.ipynb`, which carries the rejected title, headings and
  fragments. Each rule must name itself in the output.
- Vaults 2 to 13 sit in `LEGACY_VAULTS` until they are rewritten. The set only shrinks.
