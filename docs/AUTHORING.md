# Authoring a vault

Read `docs/CONTRACT.md` first. This is the recipe; the contract is the law.

Vault 1 is the worked reference. Read all three of its notebooks before writing anything.

## The one rule that matters most

**Never write a failure you have not seen happen.**

Before writing a sub-module, run the failing case against the real API and look at the output. If it
does not fail, or fails differently than expected, the lesson changes to match reality. Every number
in a lesson must have been printed by a real response.

This is not a style preference. Vault 1 was going to teach that a model blows past a prompt limit.
The first live test showed it correctly refusing. The real failure turned out to be more interesting:
asked six times, it breached four times, by splitting the refund into pieces that each obeyed the
rule. That measurement is now the lesson, and it only exists because the failure was checked.

## How to build one

Author with a Python script that uses `scripts/nbbuild.py`. Do not hand write notebook JSON. Put the
script in your scratch directory, not in the repo: the notebook is the deliverable, and a committed
generator would be a second source of truth.

```python
import pathlib, sys
ROOT = pathlib.Path("path/to/ai-engineering-vaults")   # your clone
sys.path.insert(0, str(ROOT / "scripts"))
from nbbuild import SubModule

TITLE = "Tool calls and the harness: enforce a refund limit in code"
s = SubModule(vault=2, submodule=1, title=TITLE, domain="threat-hunting",
              framework="langgraph", analogy="a plain English comparison")
s.meta["teaches"] = ["tool calls", "harness", "running total"]

s.opening(TITLE, "**Scenario:** a card issuer's assistant refunds 47500 cents ...",
          ["Read a tool call as a request your code can refuse", "..."])
s.beat("mechanics", "How the model asks your code to run a function",
       "A full opening sentence.\n\n| Field | Meaning |\n|---|---|\n| ... | ... |")
s.step(1, "Run every refund the model asks for", "images/name-step-1.svg", "One or two sentences.")
s.beat("cost", "What one over-limit refund costs", "...")   # omit if there is no cost model
s.beat("failure", "The model splits one refund into three", "...")
s.code("code that breaks", raises=True)       # a real traceback, notebook keeps running
s.step(2, "Three small refunds add up to 47500 cents", "images/name-step-2.svg", "...")
s.beat("diagnosis", "Why the limit in the prompt did not hold", "naming a mechanic from beat 1")
s.step(3, "The limit is in the prompt, the risk is in the list", "images/name-step-3.svg", "...")
s.beat("fix", "Check a running total in code before any money moves", "...")
s.step(4, "Check each refund against the case total", "images/name-step-4.svg", "...")
s.code("...")                                  # production shape, one function per cell
s.beat("gate", "A test that fails if the limit check breaks", "...")
s.code("def test_...():\n    ...")
s.md("### Enterprise exploration\n\n- ...?")
s.recap({"harness": "the ordinary code around the model that decides what runs", "...": "..."})

print(s.validate() or "none")
s.write(ROOT / "02-multi-agent-orchestration" / "01-name.ipynb")
```

## Calling the model

```python
from vault import get_client, load_env, model_for
load_env()
client = get_client("02-multi-agent-orchestration/01-name")   # vault/notebook, no extension
```

`model_for("default")`, `model_for("reasoning")` or `model_for("small")`. Never a literal model id.
Never a hardcoded price, context length or token limit; read `provider-truth.json` instead.

## Budget, which is the constraint that bites

A vault targets **30 minutes**, and the scorer fails only outside 20 to 40. The estimate models
speaking time from prose, code and outputs; it has never been timed against a recording, so it is
there to catch a vault running long, not to defend a tenth of a minute. At this depth a sub-module
lands near 9 minutes, so **three sub-modules per vault**.

Per sub-module, at most 500 words of prose, 70 lines of code, 7 or 8 code cells, and 3 to 6 step
frames. Each frame adds about 20 seconds of narration. Check with `uv run python scripts/score.py`
and cut prose first.

## How to write it

Write it the way a good book chapter reads, for an engineer who has never seen the idea before.

- **The title says what you learn.** Put the concept first, then what it stops or makes possible:
  "Idempotency keys: stop a retry from booking the same scan twice". Never "Capstone, actions that
  survive".
- **Every heading is a claim.** "Why the limit in the prompt did not hold" teaches something before
  the paragraph starts. "The diagnosis" does not.
- **Every sentence carries a whole thought.** Join "In the prompt. Ask six times and count." into one
  sentence with a subject and a verb.
- **Use the plain word.** Write "the first version", not "the naive road". Write "the call timed
  out", not "the timeout is honest". A metaphor is allowed only as the declared analogy.
- **Define a term where you first use it,** and bold it there.
- **Show the numbers before and after the fix,** as printed by a real run.

## Rules the scorer enforces

- Six beats, in order, each opened with `.beat(name, heading, body)`. `cost` may be omitted.
- The reading rules in `docs/CONTRACT.md`, pass or fail: the title, the learn list, claim headings,
  full opening sentences, sentence flow, plain words, terms defined where used, and the recap.
- 3 to 6 step frames, one image each, captions of at most 35 words, at least one before the fix and
  one inside it. Pass or fail.
- No code cell over 25 lines. At least six code cells. One `def` or `class` per cell.
- Prose between consecutive code cells, always.
- The failure cell really raises. The fix cell really prints a before and after number.
- At least three questions under `### Enterprise exploration`, naming scale, cost, compliance,
  failure or a trade off.
- The declared analogy appears in the prose.
- Sentence case headings, no em dashes, no banned words from `config/banned.yml`.

## Diagrams

Write `<vault>/diagrams/<name>.mmd` holding the **final** graph. Tag nodes with the six roles so colour
means something: `input`, `store`, `model`, `decision`, `risk`, `output`.

Then say which ids light up at each step, as Mermaid comments:

```
%% step 1: U M T X      the naive build
%% step 2: B            where it breaks
%% step 3: M T          naming an id again puts the focus back on it
%% step 4: P G HARNESS  a subgraph id lights its box
%% retire 4: T-X B      the naive edge and the breach vanish once the fix lands
```

Every frame is the same render restyled, so nodes never move between steps. A later id is a dashed
ghost, and this step's ids glow in their role colour. An edge appears once both ends are lit. Node
ids are letters and digits only.

Render one vault with `make diagrams VAULT=01`. Frames land in `images/<name>-step-N.svg`.

## Finishing

```bash
uv run python scripts/score.py     # your vault at or above 95
make check                          # every gate
```

Do not run git commands. Do not run `make diagrams` or `make record` across the whole repo.
