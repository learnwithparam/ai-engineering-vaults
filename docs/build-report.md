# Build report

Generated 11 September 2026. Check it rather than trust it: `make check && make test`.

## Where it landed

Every vault is one course in one notebook, titled from `config/courses.yml`.

| Vault | Course | Estimated video |
|---|---|---|
| `01-stateful-agent-runtime` | Building Stateful Agent Runtimes for AI Developers | 23.9 min |
| `02-multi-agent-orchestration` | Multi-Agent Systems for Production AI Engineering | 24.7 min |
| `03-token-economics` | Token Economics Optimization for AI System Architects | 25.7 min |
| `04-context-engineering` | Context Engineering for AI Coding Agent Infrastructure | 28.2 min |
| `05-subagent-delegation` | Autonomous Subagent Workflows for Senior Developers | 33.3 min |
| `06-headless-automation` | Headless AI Automation for CI/CD Pipelines | 31.0 min |
| `07-prompt-injection-defense` | Defensive Prompt Engineering for Enterprise AI Security | 24.3 min |
| `08-deterministic-outputs` | Deterministic Response Engineering for Production APIs | 28.3 min |
| `09-programmatic-guardrails` | Programmatic Guardrails for High-Reliability AI | 27.1 min |
| `10-low-entropy-tool-design` | Low-Entropy Tool Design for Reliable AI Agents | 30.1 min |
| `11-model-context-protocol` | Model Context Protocol for Enterprise System Integration | 30.8 min |
| `12-human-in-the-loop-governance` | Human-in-the-Loop Governance for High-Risk AI Actions | 31.5 min |
| `13-cost-and-latency-at-volume` | Cost and Latency Engineering for AI Systems at Volume | 26.1 min |

The total estimated recording time is 365 minutes, and every course passes `score.py` with no
findings. The estimate is advice, not a gate.

## What was verified, by running it

| Check | Result |
|---|---|
| `score` | 13 course notebooks, no findings |
| `check-structure` | 13 vaults, 0 problems |
| `check-notebooks` | 14 notebooks, 0 problems |
| `check-diagrams` | 35 sources, 96 SVG, 0 problems, every diagram inside 800 by 860 |
| `check-prose` | 14 notebooks, 0 problems |
| `check-fixtures` | 13 notebooks, 0 problems |
| `check-coverage` | 63 promises across 13 vaults, all kept |
| `check-gates` | 31 gates planted against and rejected |
| `run_notebooks` in replay | 14 of 14 executed with no API key |

## The failure each course is built on

Every failure below was seen in a recorded run before its fix was written.

| Course | What the recording showed |
|---|---|
| 01 | With the refund limit only in the prompt, 3 of 3 attempts paid 47500 cents as three refunds. With the limit in code, each paid 20000 |
| 02 | A security worker that failed left an empty lane that the report read as clean, until the merge reported it as not run |
| 03 | In a long history the orchestrator lost the customer's plan and dropped the ticket from p1 to p2. Keeping finished results fixed it on 133 tokens |
| 04 | `fnmatch` never matched `src/api/db.ts` against `src/api/**/*.ts`, so the database rule was missing on backend changes |
| 05 | Migration logs in the main session sent follow-up questions at 1554 and 1589 prompt tokens, against 89 and 135 with a forked subagent |
| 06 | Plan mode stated only in the prompt let the audit write to the branch in 4 of 6 runs. A tool allowlist made it 0 |
| 07 | With no defense, 11 of 15 attack resumes advanced a candidate. Tags left 3 of 15, and a decision in code left 0 |
| 08 | A locked schema gave 5 of 5 valid replies and only 2 of 5 correct ones, including francs posted as euros |
| 09 | 5 of 5 quotes came back negative, and the feedback loop changed a 41% loan to 36% to pass the validator |
| 10 | 25 generic tools sent 6 of 16 requests to the tool that could answer. Four scoped tools sent 13 of 16 |
| 11 | A client that ignored `isError` let the model invent totals in 2 of 3 attempts |
| 12 | With approval asked for only in the prompt, the agent deleted a production database in 5 of 5 attempts. A pre-execution hook made it 0 |
| 13 | The same cached prefix was billed in full for 9 calls before the cache appeared on the 10th |

## What is deliberately not here

- **A provider batch price.** The repo's client calls only the chat endpoint, so the course 13 batch
  lane is built in code and does not measure a provider's batch discount.
- **Authentication over HTTP.** Course 11 mentions the header and does not build it, because its
  scenario does not need it.
- **A calibrated recording estimate.** The model in `config/recording.json` has never been timed
  against a recording, so the minutes above are advice.
