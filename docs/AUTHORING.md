# Authoring a vault

Read `docs/CONTRACT.md` first. This is the recipe; the contract is the law.

Vault 1 is the worked reference. Read its notebook, `01-build-an-agent-runtime.ipynb`, before
writing anything.

## The one rule that matters most

**Never write a failure you have not seen happen.**

Before writing a step that shows something breaking, run it against the real API and read the
output. If it does not fail, or fails differently than expected, the step changes to match reality.
Every number in a lesson must have been printed by a real response.

## How to write it

Write it the way a good tutorial reads, for an engineer who has never built this before and is
watching you build it.

- **Open with the problem, not the design.** `## What you will build` says in plain words what the
  course builds and what goes wrong without it, above one small diagram of that problem. It names
  no code. The detailed diagrams appear in the steps that build them.
- **The title is the catalogue's.** Each vault's title and scenario live in `config/courses.yml`.
  Build the whole course on that one scenario.
- **One scenario, grown step by step.** Every step adds one piece to the same example. Never switch
  to a new scenario to make a new point.
- **Every heading says what the step builds.** "Run the tool and send the result back" tells the
  reader what is coming. "The fix" does not.
- **Open each step with what we are doing and why,** in one or two full sentences. Then the code.
- **Every sentence carries a whole thought.** "In the prompt. Ask six times and count." is two
  fragments. Say it as one sentence with a subject and a verb.
- **Use the plain technical word.** Write "the call timed out", not "the timeout is honest".
- **Introduce a term by contrast.** Show the problem first, then bold the term and define it in that
  sentence or the next. "Asking for a shape in words is only a request. **tool_choice** names the one
  tool the model may answer through." A definition pasted into the middle of a sentence pushes the
  verb away from its object.
- **Hand over between steps by repeating the noun.** A step opens on the noun the last step ended on,
  not on "however" or "next".
- **Say money at a scale a person can hear.** The cell output keeps the exact figure. The prose says
  "about 5 cents a claim" or "about $87 a night", never `$0.0000479`.
- **Show the numbers.** When a step fixes something, print the result before and after.

`~/.claude/skills/lwp-shared/voice.md` and `house-rules.md` are the language standard. Their
ceilings are 28 words to a sentence and 4 sentences to a paragraph, and nothing else: no floor, no
target average. Check with `python3 ~/.claude/skills/lwp-shared/scripts/house_rules.py --voice`.

## How to name code

You read every name aloud on a screencast. If you cannot say what a name does in one breath, rename
it.

- Functions are verb then object: `get_order_status`, `issue_refund`, `run_agent`,
  `execute_tool_call`. Never one word like `approve` or `dispatch`.
- Constants are nouns in capitals that say what they hold: `ORDERS`, `REFUNDS_ISSUED`,
  `TOOL_REGISTRY`, `MAX_TURNS`.
- A function whose job changes gets a name that says the new job: `issue_refund_within_limit`,
  `issue_refund_once`.
- Each code cell ends by printing what just happened, so the output narrates the step.
- Comments are for the numbered moves inside a longer cell, and nothing else.

## How to build one

Author with a scratch Python script that uses `scripts/nbbuild.py`, never hand written notebook JSON.
Keep the script in your scratch directory, because the notebook is the deliverable.

```python
import pathlib, sys
ROOT = pathlib.Path("path/to/ai-engineering-vaults")
sys.path.insert(0, str(ROOT / "scripts"))
from nbbuild import Course

c = Course(vault=2, title="Multi-Agent Systems for Production AI Engineering",  # courses.yml
           domain="code-review")
c.overview("What the course builds and what goes wrong without it, in plain words.",
           "images/audit-overview.svg")
c.step("Set up the client and the model", "What we do and why, in full sentences.")
c.code("...")
c.step("Describe the tools to the model", "...", image="images/router-step-1.svg")
c.code("...")
c.md("A sentence on what the next cell does.")
c.code("...")
c.concepts([("Tool call", "`choice.message.tool_calls`", "The model's request to run a function")])

print(c.validate() or "valid")
c.write(ROOT / "02-multi-agent-orchestration" / "01-build-a-router.ipynb")
```

## Calling the model

```python
from vault import get_client, load_env, model_for
load_env()
client = get_client("02-multi-agent-orchestration/01-build-a-router")
```

`model_for("default")`, `model_for("reasoning")` or `model_for("small")`. Never a literal model id,
price, context length or token limit.

## Diagrams

Write `<vault>/diagrams/<name>.mmd` holding the **finished** system. Label every node with the plain
words the notebook uses, such as "Call the model", "Inspect finish_reason" or "Append the tool
result". Never use a slogan. Tag nodes with the six roles, so colour means something: `input`, `store`,
`model`, `decision`, `risk`, `output`.

Then say which ids appear at each frame, as Mermaid comments:

```
%% step 1: U H C F T    the first request
%% step 2: B R          running the tool and sending the result back
%% retire 5: K-B        an edge that a later piece replaces
```

Every frame is the same render restyled, so nodes never move between frames. Render one vault with
`make diagrams VAULT=01`. Each step shows the frame it builds.

The overview is its own small diagram of the problem, in `diagrams/<name>-overview.mmd` with no
step directives. Draw the people and systems involved and what goes wrong, never the design.

`make diagrams` shrinks every SVG to fit 900 by 700 pixels and never enlarges one. A long chain
drawn top to bottom runs too tall, so it shrinks until its labels fall under 11px and the check
fails. Merge nodes or split the design into two series. `uv run python scripts/check_diagrams.py`
measures every SVG.

## Recording and finishing

```bash
make record VAULT=01               # real API, budget guarded, this vault only
uv run python scripts/score.py 01  # this vault, no findings
make check                          # every gate
```

Do not run git commands. Do not run `make diagrams` or `make record` without a `VAULT`.
