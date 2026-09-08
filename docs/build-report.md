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
| `13-cost-and-latency-at-volume` | 100.0 | 27.3 min |

Thirteen vaults, 39 teaching notebooks plus a setup guide. Total estimated recording time 377 minutes. Lowest score 100.0 against a threshold of 95. Longest vault 29.8 minutes against a budget of 30.

## What was verified, by running it

| Check | Result |
|---|---|
| `check-structure` | 13 vaults, 0 problems |
| `check-notebooks` | 40 notebooks, 0 problems |
| `check-diagrams` | 39 sources, 0 problems |
| `check-prose` | 40 notebooks, 0 problems |
| `check-fixtures` | 39 notebooks, 0 problems |
| `check-theme` | 0 problems, structural only |
| `check-gates` | 5 gates planted against and rejected |
| `score` | every notebook and vault at or above 95 |
| `run_notebooks` in replay | 40 of 40 executed with no API key |

A clean clone carries no credential. Recording the whole course against the live
API cost well under a dollar.

## Coverage against the original twelve course specs

Audited by matching the mechanics and vocabulary of each spec against the built
notebooks. Two gaps were found after the first twelve vaults were complete:
**the parallel latency formula** and **prompt caching**, both named in the
Course 3 spec and in the Domain 5 material. Vault 13 was built to close them.

Everything else in the twelve specs was already covered.

## The rule that shaped the content

Never write a failure you have not seen happen. Several planned lessons did not
survive contact with a real model, and every replacement is stronger.

| Planned | What actually happened |
|---|---|
| A model blows past a refund limit written in the prompt | It refused. Asked six times it breached four, by splitting the refund into pieces that each obeyed the rule |
| Tool accuracy decays as the tool count grows | Accuracy held. At 24 tools the model stopped choosing at all and returned a malformed function call |
| A `print()` corrupts a stdio MCP stream | A full line survives. Only a partial line, with the reply glued to it, breaks the host |
| Multi-agent beats a single call | It measured worse on cost, latency and accuracy, because isolation stripped the comparison set |
| Negative framing in a tool description fails | It held. Enumeration failed: a state the rule never named fired 5 of 6 times |
| Lost in the middle costs you retrieval | Retrieval held 15 of 15. The loss is in the summary |
| A model either caches or it does not | The default model reported 0% cached cold and 88.9% warm. A cold measurement is worthless |
| A shape cannot rescue a slow model | Overlapping took a 22.7 second run to 6.3 seconds for no extra money |

## What is deliberately not here

- **Deployment, evaluation and observability.** Modules 6 to 8 of the source are
  syllabus stubs with no teaching content, deferred by agreement.
- **A working batch submission.** The lane exists at roughly half price and the
  endpoint returned 404 on this account. Vault 13 shows the shape and says it did
  not run it.
- **A pushed remote.** Every commit is local.
- **A calibrated recording estimate.** The model is documented in
  `config/recording.json` and has never been checked against a real recording.
