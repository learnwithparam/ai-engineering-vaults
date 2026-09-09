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

Working targets per sub-module: about 550 words of prose, about 60 lines of code across six or seven
cells, four or five outputs.

## The eight beats

Every sub-module notebook carries these seven, in this order. Each is a markdown heading the scorer
looks for.

| Beat | Heading | What it must contain |
|---|---|---|
| 1 | `## Mechanics` | Exact parameters, states and enums, as a table |
| 2 | `## The picture` | An image reference to a rendered SVG |
| 3 | `## The cost` | A formula or a measurement. Omitted honestly if none applies |
| 4 | `## The failure` | A code cell that runs and visibly breaks |
| 5 | `## The diagnosis` | Why, naming a mechanic from beat 1 |
| 6 | `## The fix` | The production build. One function per cell, in learning order, prose between, and a printed before and after number. See `docs/decisions/004-merge-fix-and-build.md` |
| 7 | `## The gate` | A runnable check, then `### Enterprise exploration` |

Beat 3 may be absent when there is no honest cost model. Every other beat is required.

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
