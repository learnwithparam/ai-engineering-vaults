# The contract

The single definition of what a vault and a sub-module must be. `scripts/score.py` and the six
`check-*` gates read this document's rules. Nothing else decides whether a notebook is good enough.

**Frozen once vault 1 is signed off.** After that, changing any threshold here forces a re-score of
every accepted notebook, which `make score` does automatically. A late idea cannot quietly invalidate
earlier work.

---

## Shape

A **vault** is one topic and one recorded video of about thirty minutes. It is a folder holding a
`README.md`, three or four notebooks, and its own `diagrams/`, `images/` and `fixtures/`.

A **sub-module** is one notebook. Normally two teach and a third is a capstone that integrates them.
The thirty minute vault target is the real constraint, so four short sub-modules are fine and four
dense ones are not. See `docs/decisions/005-three-submodules-per-vault.md`.

Working targets per sub-module: at most 600 words of prose, 3 to 6 step frames, about 60 lines of
code across six or seven cells, four or five outputs.

## The six beats

Every sub-module notebook carries these six, in this order. A beat is a role, found by the tag on
the markdown cell that opens it. The heading on that cell belongs to the reader and says what the
section teaches, as a claim. See `docs/decisions/008-headings-teach.md`.

| Beat | Tag | What it must contain | Example heading |
|---|---|---|---|
| 1 | `beat:mechanics` | Exact parameters, states and enums, as a table | How the model asks your code to run a function |
| 2 | `beat:cost` | A formula or a measurement. Omitted if none applies | What one over-limit refund costs |
| 3 | `beat:failure` | A code cell that runs and visibly breaks | The model splits one refund into three |
| 4 | `beat:diagnosis` | Why, naming a mechanic from beat 1 | Why the limit in the prompt did not hold |
| 5 | `beat:fix` | The production build. One function per cell, in learning order, prose between, and a printed before and after number. See `docs/decisions/004-merge-fix-and-build.md` | Check a running total in code before any money moves |
| 6 | `beat:gate` | A runnable check, then `### Enterprise exploration` | A test that fails if the limit check breaks |

Beat 2 may be absent when there is no cost model to show. Every other beat is required.

## Reading

A notebook reads like a chapter of a book: the title says what you learn, every heading makes a
claim, and every sentence carries a whole thought. These are pass or fail, like the step frames.
The thresholds were measured, not guessed, and decision 008 records the numbers.

| Rule | Limit |
|---|---|
| Title | 6 to 12 words, at most 70 characters, naming the first `metadata.vault.teaches` term. No word from `vague_titles` in `config/banned.yml` |
| `metadata.vault.teaches` | 2 to 4 concepts the reader leaves with, the headline one first |
| Opening cell | the title, a scenario with its number, then `### What you will learn` with 2 to 4 bullets naming every `teaches` term |
| Headings and step titles | at least 4 words, never on `vague_headings`. A step title uses a noun from the scenario |
| First sentence of each beat | at least 8 words |
| Mean sentence length | 12 to 20 words |
| Sentences under 6 words | at most 15% |
| Two fragments in a row in a paragraph | not allowed |
| `teaching_words` in `config/banned.yml` | none |
| Glossary terms | explained in the sentence that first uses them, in every notebook |
| Closing | `### Key terms and traps`, 3 to 5 bullets, each opening with a bold term |

## Step frames

The fix is derived, never handed over. A notebook reaches it in frames, the way a maths derivation
reaches an answer: the naive build, where it breaks, why, each piece the fix adds, and the test that
pins it. See `docs/decisions/007-steps-replace-the-picture.md`.

| Rule | Limit |
|---|---|
| Step frames per notebook | 3 to 6, numbered from 1 with no gaps |
| A step | its own markdown cell: `### Step N: <title>`, exactly one image, then the caption |
| Caption | at most 35 words |
| Placement | at least one frame before `## The fix`, and at least one inside it |
| Prose per notebook | at most 600 words |
| Frames | from one `.mmd` with `%% step` directives. Every node lit by the last step |

These are pass or fail, like domain spread and the recording budget. A weighted average cannot
carry a notebook that breaks one.

## Cell rules

These exist so the notebook reads well on video. A wall of code is skipped, not watched.

| Rule | Limit |
|---|---|
| Lines in one code cell | at most 25 |
| Code cells per notebook | at least 6 |
| Top level `def` or `class` per cell | at most 1 |
| Consecutive code cells with no prose between | not allowed |
| Estimated speaking time per vault | 30 minutes is the target, 20 to 40 is the band that fails |

## Scoring

Deterministic, 0 to 100. **Every notebook must reach 95 and every vault must reach 95.**

| Dimension | Weight |
|---|---|
| Structure | 20 |
| Plain language | 20 |
| Production grade | 20 |
| Domain spread | 15 |
| Enterprise depth | 15 |
| Recording budget | 10 |

Every deduction names the notebook, the cell and the fix. A deduction that cannot name a fix is a
bug in the scorer, not a finding.

**The threshold never moves to make a notebook pass.** If a notebook cannot reach 95, the notebook is
rewritten. The only reason to change a rule here is that the rule is wrong or impossible to satisfy,
and that change is recorded in `docs/decisions/` with its reason.

## Plain language

Written for a junior to follow and a principal to respect.

| Rule | Limit |
|---|---|
| Mean sentence length | at most 20 words |
| Words over three syllables | at most 15% |
| Em dashes | none |
| Banned words | none, per the house rules list |
| Headings | sentence case |
| Plain English analogy | at least one per sub-module |
| Glossary terms | defined on first use in the vault |

## Provider honesty

No price, context length, cache minimum, TTL, discount ratio or token limit is ever written into
prose or code as a literal. Those are provider facts that differ per model and change without notice.

Notebooks read `build/provider-truth.json`, written by `make probe` from the live API. A number that
appears in a lesson must have been printed by a real response.

`check-prose` carries the known-wrong constants as banned literals, because the source material this
course was built from teaches a different provider's numbers.

## Secrets

No key, token or credential appears in a notebook, an output, a fixture or a committed file.
`check-prose` scans committed cell outputs for key-shaped strings, because notebook outputs are
committed here and are a real leak path.

## Domains

Every sub-module declares one domain in its notebook metadata, drawn from `config/domains.yml`.

| Rule | Limit |
|---|---|
| Distinct domains across the repo | at least 20 |
| Uses of any one domain | at most 3 |
| Distinct domains within a vault | at least 3 |
| High pull domains per vault | at least 1 |
| Enterprise credible domains per vault | at least 1 |

Fascination earns the click, credibility earns the subscription. A vault made only of racing cars
fails, and so does a vault made only of insurance claims.

## Notebook metadata

Every notebook carries this under `metadata.vault`:

```json
{
  "vault": 1,
  "submodule": 2,
  "title": "Stop reason as a state machine",
  "domain": "medical-imaging-triage",
  "framework": "none",
  "analogy": "a radar sweep"
}
```
