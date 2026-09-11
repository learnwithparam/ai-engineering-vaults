# 009: One notebook per course, built step by step

Supersedes 005, which set three sub-modules per vault, and the count rules in 007 and 008.

## Why

On 2026-09-11 the vault 1 pilot passed every gate and was rejected again, for three reasons.

- **The shape.** Three notebooks taught three unrelated scenarios, a card chargeback, a race
  strategy and a hospital booking, for one small course. The user asked for one example taught
  incrementally.
- **The language.** It was clipped and robotic in the prose and in the diagram labels, for example
  "Your code. The only thing that can execute." and "Lives with the scheduler, not the agent".
- **The names.** `approve`, `dispatch`, `ask`, `stops_naive` and `book_durable` do not say what they
  do, and the author reads every name aloud on a screencast.

The gates caused much of this. A 600-word cap, 35-word captions, six fixed beats, three domains per
vault and a required analogy all pushed the text toward fragments.

The reference is a Gemini notebook on the same topic. It shows the whole runtime first, then builds
it through numbered steps on one e-commerce example, with a heading that says what each step builds,
names like `TOOL_REGISTRY` and `get_order_status`, and a closing concepts table.

## Decision

- A vault is one notebook: title, an overview with the finished diagram, `## Step 0` to `## Step N`,
  and a closing `## Concepts` table. `check-structure` enforces one notebook per vault.
- Every rule in `score.py` is pass or fail. The weighted average, the word and caption caps, the six
  beats, enterprise questions, the analogy, the recap and the domain spread rules are gone.
- A new rule says function names are at least two words, verb then object.
- The reading rules from 008 that measure flow stay. Those are claim headings, full opening
  sentences, the sentence length floor, the fragment limits, plain vocabulary and glossary terms
  defined where first used.
- Vaults 2 to 13 were rewritten to this contract the same day, each on its catalogue scenario. The
  legacy exemption that covered them during the rewrite is deleted, so every gate reads every vault.

## Amended after review

The first vault 1 rewrite opened with the full runtime diagram. The user found that confusing
before any code, so the opening now shows the problem instead:

- The opening is `## What you will build`, with one problem diagram, no step frame, and no code.
- Each title is the catalogue title from `config/courses.yml`, with vendor names dropped, because
  every course is taught on a generic API.
- Every diagram fits the real notebook column. The old 1200 pixel limit let a wider image pass the
  check while the cell clipped it.

## Enforcement

`scripts/score.py`, `scripts/check_structure.py`, and `scripts/check_gates.py`. The last plants a
vault that breaks each rule and requires every rule to name itself.
