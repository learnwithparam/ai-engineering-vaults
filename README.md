# AI Engineering Vaults

![AI Bootcamp Open Graph preview](https://www.learnwithparam.com/ai-bootcamp/opengraph-image)

Production AI engineering, taught as vaults. Each vault is one topic and one video. Each notebook
inside it takes one idea, breaks it on purpose, fixes it, measures the difference, and leaves you
with the check that stops it breaking again.

> Regional pricing is available for eligible learners, with discounts of up to 60% in supported regions. Start here: https://www.learnwithparam.com/ai-bootcamp

## Quick start

```bash
make setup
make run
```

Open `00-setup/01-start-here.ipynb` and read it. It takes five minutes and saves you an hour.

**You can run every lesson without an API key.** Responses are recorded from the real API and
committed, so `make test` executes all of it for free. Add a key when you want to change a prompt
and watch the answer change, which is the point.

## What makes this different from a tutorial

Most agent material shows you the happy path. This shows you the failure first.

Every sub-module runs the same eight beats: the exact mechanics, a diagram, the cost model, a
**runnable failure**, the diagnosis traced to a specific mechanic, a **measured fix**, the
production build one function at a time, and the gate that prevents a regression.

The one idea underneath all of it: **the model decides, your code executes.** A model never does
anything. It returns a decision as data, and your harness chooses whether to act on it. Almost every
production incident in this course comes from forgetting that.

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

## How it stays honest

- **`make check` runs every gate**, and plants a deliberately broken vault to prove the gates still
  catch things. A check that has never failed is not known to check anything.
- **Notebooks are scored, not reviewed.** `scripts/score.py` is deterministic and the bar is 95.
  `CONTRACT.md` defines exactly what it measures.
- **No provider number is hardcoded.** Prices, context limits and cache rules are probed from the
  live API by `make probe`. A number in a lesson was printed by a real response.
- **Secrets never appear.** Keys are copied without being displayed, and every committed output is
  scanned for key shaped text.

## Where the theme applies

`make run` launches JupyterLab with a dark theme built for screen recording, scoped to this repo so
nothing global is touched. That theme does **not** apply on GitHub, in VS Code or in Colab, which
render notebooks their own way. Committed outputs and transparent SVG diagrams keep those readable.

## License

MIT. Use it, teach from it, fork it.
