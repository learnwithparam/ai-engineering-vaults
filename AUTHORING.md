# Authoring a vault

Read `CONTRACT.md` first. This is the recipe; the contract is the law.

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
ROOT = pathlib.Path("/Users/param/learn/learnwithparam/lwp-repos/ai-engineering-vaults")
sys.path.insert(0, str(ROOT / "scripts"))
from nbbuild import SubModule

s = SubModule(vault=2, submodule=1, title="...", domain="threat-hunting",
              framework="langgraph", analogy="a plain English comparison")

s.md("# Title\n\n**Scenario:** ...")
s.beat("mechanics", "| Field | Meaning |\n|---|---|\n| ... | ... |")
s.beat("picture", "![alt](images/name.svg)")
s.beat("cost", "```\nformula\n```")          # omit honestly if there is none
s.beat("failure", "prose")
s.code("code that breaks", raises=True)       # a real traceback, notebook keeps running
s.beat("diagnosis", "why, naming a mechanic from beat 1")
s.beat("fix", "prose")
s.code("...")                                  # production shape, one function per cell
s.beat("gate", "prose")
s.code("def test_...():\n    ...")
s.md("### Enterprise exploration\n\n- ...\n\n### Key takeaways\n\n- ...")

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
Never a hardcoded price, context length or token limit; read `build/provider-truth.json` instead.

## Budget, which is the constraint that bites

A vault is **30 minutes total**, and the scorer fails the build over that. Measured from vault 1, a
sub-module lands near 9 minutes at this depth, so **three sub-modules per vault**.

Per sub-module, aim for about 600 words of prose, 70 lines of code, 7 or 8 code cells. Check with
`uv run python scripts/score.py` and cut prose first.

## Rules the scorer enforces

- Seven beats, in order. `cost` may be omitted.
- No code cell over 25 lines. At least six code cells. One `def` or `class` per cell.
- Prose between consecutive code cells, always.
- The failure cell really raises. The fix cell really prints a before and after number.
- At least three questions under `### Enterprise exploration`, naming scale, cost, compliance,
  failure or a trade off.
- The declared analogy appears in the prose.
- Sentence case headings, no em dashes, no banned words from `banned.yml`.

## Diagrams

Write `<vault>/diagrams/<name>.mmd`. Tag nodes with the six roles so colour means something:
`input`, `store`, `model`, `decision`, `risk`, `output`. Do not render; that is done centrally.

## Finishing

```bash
uv run python scripts/score.py     # your vault at or above 95
make check                          # every gate
```

Do not run git commands. Do not run `make diagrams` or `make record` across the whole repo.
