# AI Engineering Vaults

![AI Bootcamp Open Graph preview](https://www.learnwithparam.com/ai-bootcamp/opengraph-image)

Production AI engineering, taught as vaults. Each vault takes one topic. Each notebook inside it
takes one idea, breaks it on purpose, fixes it, measures the difference, and leaves you with the
check that stops it breaking again.

## Run it

```bash
make setup
make run
```

That installs everything and opens JupyterLab. Start with `00-setup/01-start-here.ipynb`, then take
the vaults in order.

**You do not need an API key.** Every response was recorded from the real API and committed, so the
notebooks run from those recordings and cost nothing. Add a key when you want to change a prompt and
watch the answer change, which is the point.

## The one idea underneath all of it

**The model decides, your code executes.** A model never does anything. It returns a decision as
data, and your harness chooses whether to act on it. Almost every incident in this course comes from
forgetting that.

## The vaults

| Vault | What breaks in production |
|---|---|
| Stateful agent runtimes | Loops that never end, retries that charge twice, restarts that lose the thread |
| Multi-agent orchestration | Workers flooding the parent context, synthesis that averages away disagreement |
| Token economics | Caches that never hit, handoffs paying for the same context repeatedly |
| Context engineering | The one identifier a summariser threw away |
| Subagent delegation | Logs that drown the session they were meant to keep clean |
| Headless automation | A green build hiding a red finding |
| Prompt injection defense | A document that rewrites its own evaluation |
| Deterministic outputs | Prose where the pipeline expected JSON |
| Programmatic guardrails | Valid JSON carrying an impossible number |
| Low-entropy tool design | Twenty five tools and the wrong one chosen |
| Model context protocol | A `print()` that corrupts the protocol stream |
| Human in the loop governance | An irreversible action taken unattended |
| Cost and latency at volume | A cache saving that never arrives, five fast calls that take as long as their total |

## How a vault works

Most agent material shows you the happy path. Every notebook here shows the failure first: the
mechanics, a diagram, what it costs, a failure you can run, the diagnosis, the fix with the
difference measured, the production build, and the test that keeps it fixed.

## If it does not run

`00-setup/01-start-here.ipynb` checks your setup and names what is missing. If it still fails, open
an issue.

The course, with regional pricing for eligible learners:
https://www.learnwithparam.com/ai-bootcamp
