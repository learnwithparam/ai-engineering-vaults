# The contract

What a vault must be. `scripts/score.py`, `check-structure` and the other `check-*` gates enforce
every rule here, and each rule says what fails when it is broken. Decision 009 records why the
contract took this shape.

---

## Shape

A **vault** is one short course: one topic, one scenario, one notebook, and about thirty minutes of
screencast. The folder holds a `README.md` that lists the notebook, the notebook itself, and its own
`diagrams/`, `images/` and `fixtures/`. `check-structure` fails a vault with more than one notebook.

The notebook is built the way a good tutorial is. It shows the finished system first, then builds
it one step at a time on the same example, so each step adds one piece to what the reader already
has.

| Part | What it holds | Fails when |
|---|---|---|
| Title | `# <course title>`: exactly this vault's title in `config/courses.yml`, and the same string as `metadata.vault.title` | missing, different from the catalogue, or naming a vendor from `vendor_words` |
| Overview | one `## What you will build` section before Step 0: in plain words, what the course builds and the problem it solves, over one diagram of that problem | a different heading, not exactly one diagram, a step frame, or code in the prose. The design belongs in the steps |
| Steps | `## Step 0: <what this step builds>` to `## Step N`, numbered with no gaps | fewer than 4, or a gap |
| Frames | the design, grown one frame per step in the step that builds it | fewer than 3 frames after Step 0, or out of order |
| Closing | `## Concepts`: a table of the concept, where it lives in the code, and what it does | missing |

Every diagram in a course fits 800 by 860 pixels with its labels at 70% or more. At 1920 by 1080
the notebook column is about 800 pixels wide, and it clips anything wider rather than scaling it.
`check-diagrams` measures every SVG.

## Writing

Plain technical English, in the register of a good tutorial. A reader should follow it without
fatigue, and the author should be able to read it aloud on a screencast without stumbling.

| Rule | Limit |
|---|---|
| Headings and step titles | at least 4 words, saying what the step builds. Never a label from `vague_headings` |
| First sentence of each step | at least 8 words, saying what we do and why |
| Mean sentence length | 12 to 22 words |
| Sentences under 6 words | at most 15%, and never two in a row in a paragraph |
| Words over three syllables | at most 15% |
| `words` and `teaching_words` in `config/banned.yml` | none |
| Em dashes | none |
| Terms in `config/glossary.yml` | explained in the sentence that first uses them |

There is no word cap. Say what the step needs, in full sentences, and stop.

## Code

The code is read aloud on a screencast, so it must read as the clearest version of the idea.

| Rule | Limit |
|---|---|
| Lines in one code cell | at most 25 |
| Two code cells in a row | not allowed, a sentence goes between them |
| Function names | at least two words, verb then object, like `issue_refund` or `run_agent`. Never one word, and never a first word from `vague_function_words` |
| `except:` with no exception named | not allowed |
| Outbound HTTP | always with a timeout |

## Checking

Every rule is pass or fail. `make score` lists each finding with the notebook, the cell and the fix,
and passes only when there are none. Estimated screencast minutes are printed as advice, with 30 as
the target.

`make score` checks every vault. `uv run python scripts/score.py 05` checks one vault while you
work on it.

## Provider honesty

No price, context length, cache minimum, TTL, discount ratio or token limit is ever written into
prose or code as a literal. Those are provider facts that differ per model and change without notice.

Notebooks read `provider-truth.json`, written by `make probe` from the live API. A number that
appears in a lesson must have been printed by a real response.

`check-prose` carries the known-wrong constants as banned literals, because the source material this
course was built from teaches a different provider's numbers.

## Secrets

No key, token or credential appears in a notebook, an output, a fixture or a committed file.
`check-prose` scans committed cell outputs for key-shaped strings, because notebook outputs are
committed here and are a real leak path.

## Notebook metadata

Every notebook carries this under `metadata.vault`, with a domain drawn from `config/domains.yml`:

```json
{
  "vault": 1,
  "title": "Building Stateful Agent Runtimes for AI Developers",
  "domain": "ecommerce-support",
  "framework": "none"
}
```
