# Build report

Generated 9 September 2026. Check it rather than trust it: `make check && make test`.

## Where it landed

| Vault | Score | Estimated video |
|---|---|---|
| `01-stateful-agent-runtime` | 100.0 | 29.5 min |
| `02-multi-agent-orchestration` | 100.0 | 28.2 min |
| `03-token-economics` | 100.0 | 28.0 min |
| `04-context-engineering` | 100.0 | 29.5 min |
| `05-subagent-delegation` | 100.0 | 29.7 min |
| `06-headless-automation` | 100.0 | 28.7 min |
| `07-prompt-injection-defense` | 100.0 | 28.7 min |
| `08-deterministic-outputs` | 100.0 | 29.6 min |
| `09-programmatic-guardrails` | 100.0 | 29.5 min |
| `10-low-entropy-tool-design` | 100.0 | 29.8 min |
| `11-model-context-protocol` | 100.0 | 29.3 min |
| `12-human-in-the-loop-governance` | 100.0 | 29.5 min |

Twelve vaults, 36 teaching notebooks plus a setup guide. Total estimated recording time 350 minutes. Lowest score 100.0, threshold 95. Longest vault 29.8 minutes, budget 30.

## What was verified, by running it

| Check | Result |
|---|---|
| `check-structure` | 12 vaults, 0 problems |
| `check-notebooks` | 37 notebooks, 0 problems |
| `check-diagrams` | 36 sources, 0 problems |
| `check-prose` | 37 notebooks, 0 problems |
| `check-fixtures` | 36 notebooks, 0 problems |
| `check-theme` | 0 problems, structural only |
| `check-gates` | 5 gates planted against and rejected |
| `score` | every notebook and vault at or above 95 |
| `run_notebooks` in replay | 37 of 37 executed with no API key |

A clean clone carries 37 notebooks, 36 rendered diagrams and 470 recorded
responses, and no credential. Recording the entire course against the live API
cost **$0.0874**.

## The rule that shaped the content

Never write a failure you have not seen happen. Several planned lessons did not
survive contact with a real model, and every replacement is stronger.

| Planned | What actually happened |
|---|---|
| A model blows past a refund limit written in the prompt | It refused. Asked six times it breached four, by splitting the refund into pieces that each obeyed the rule |
| Tool accuracy decays as the tool count grows | Accuracy held. At 24 tools the model stopped choosing at all, asked for every tool it had, and returned a malformed function call |
| A `print()` corrupts a stdio MCP stream | A full line survives; the client logs a parse failure and continues. Only a partial line, with the reply glued to it, breaks the host. Framing is the mechanic |
| Multi-agent beats a single call | It measured worse on cost, latency and accuracy, because isolation stripped the comparison set |
| Negative framing in a tool description fails | It held. Enumeration failed: a state the rule never named fired 5 of 6 times |
| Lost in the middle costs you retrieval | Retrieval held 15 of 15. The loss is in the summary, and position moves between runs |

Two of those reversals are now the strongest lessons in the course.

## What is deliberately not here

- **Deployment, evaluation and observability.** Modules 6 to 8 of the source
  material are syllabus stubs with no teaching content, and were deferred by
  agreement. A light observability thread runs through the capstones.
- **A pushed remote.** Every commit is local. Creating a public repository is a
  decision for a person, not for an unattended run.
- **A calibrated recording estimate.** The budget model is defensible and
  documented in `config/recording.json`, but it has never been checked against a
  real recording. Confirm it against vault 1 and adjust once.
- **Proof that the theme renders on every machine.** `check-theme` is structural.
  The render is evidenced by `docs/theme.png` and the DOM values beside it.
