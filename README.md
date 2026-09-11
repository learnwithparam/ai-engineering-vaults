# AI Engineering Vaults

![AI Bootcamp Open Graph preview](https://www.learnwithparam.com/ai-bootcamp/opengraph-image)

Production AI engineering, taught as short practical courses. Each vault is one course in one
notebook. It opens with the problem you are about to solve, then builds the solution step by step on
one real scenario, runs every failure for real, fixes it, and ends with tests that keep it fixed.

## Run it

```bash
make setup
make run
```

That installs everything and opens JupyterLab. Start with `00-setup/01-start-here.ipynb`, then take
the courses in order.

**You do not need an API key.** Every response was recorded from the real API and committed, so the
notebooks run from those recordings and cost nothing. Add a key when you want to change a prompt and
watch the answer change, which is the point.

## The one idea underneath all of it

**The model decides, your code executes.** A model never does anything. It returns a decision as
data, and your code chooses whether to act on it. Almost every incident in these courses comes from
forgetting that.

## The courses

| Course | What goes wrong without it |
|---|---|
| Building Stateful Agent Runtimes for AI Developers | A refund over the limit, a cut-off answer trusted, a retry that pays twice |
| Multi-Agent Systems for Production AI Engineering | A worker that never ran reported as a clean lane |
| Token Economics Optimization for AI System Architects | Handoffs resending the same history, and a pruned log that took a fact with it |
| Context Engineering for AI Coding Agent Infrastructure | A rule every task pays for, and a glob that never matches |
| Autonomous Subagent Workflows for Senior Developers | Logs that drown the session they were meant to keep clean |
| Headless AI Automation for CI/CD Pipelines | A green build hiding an unsafe query |
| Defensive Prompt Engineering for Enterprise AI Security | A resume that rewrites its own evaluation |
| Deterministic Response Engineering for Production APIs | Valid JSON posting the wrong invoice |
| Programmatic Guardrails for High-Reliability AI | Valid JSON carrying an impossible payment |
| Low-Entropy Tool Design for Reliable AI Agents | Too many tools, and the wrong one chosen |
| Model Context Protocol for Enterprise System Integration | A stray log line that corrupts the protocol stream |
| Human-in-the-Loop Governance for High-Risk AI Actions | An irreversible action taken unattended |
| Cost and Latency Engineering for AI Systems at Volume | A cache saving that never arrives, and fast calls that add up slowly |

## How a course works

Every course follows the same path. It shows what you will build and what goes wrong without it.
Then it builds that system one step at a time on a single scenario. Each production concern is seen
failing in a recorded run before it is fixed, with the numbers printed before and after. The last
step tests every safeguard without calling the model, and a concepts table closes the course.

## If it does not run

`00-setup/01-start-here.ipynb` checks your setup and names what is missing. If it still fails, open
an issue.

The course, with regional pricing for eligible learners:
https://www.learnwithparam.com/ai-bootcamp
