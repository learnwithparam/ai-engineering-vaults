# AI Engineering Vaults

Notebooks teaching production AI engineering: where an agent pattern breaks under real load, what
that costs, and the check that stops it breaking again.

**This is teaching material, not a product.** The bar is that a learner can clone it and run it.
Optimise for a working first command and a clear error when something is missing, not for
architecture.

## Running it

```bash
make help
make setup
make run
make check
make test
```

All targets: `help`, `setup`, `install`, `dev`, `run`, `probe`, `status`, `score`, `check`, `test`,
`test-live`, `record`, `diagrams`, `clean`, and the eight `check-*` gates.

Python project (`pyproject.toml`). Use the repo's own virtualenv; never install into the system
interpreter.

## Rules

- **Never break the first-run path.** A learner hitting an error in step one abandons the workshop.
  If you change setup, run it from a clean clone before calling it done.
- **Explanations belong in the README and in notebook prose**, not in long code comments. The code is
  the lesson; it should read as the clearest version of the idea.
- **No em dashes** in prose. `check-prose` fails the build on one.
- **Pin what you can.** `uv.lock` is committed.

## Where this repo deliberately differs from its siblings

`engineering.md` asks that a departure be stated out loud, so:

- **This repo has `make check` and CI.** No other repo in `lwp-repos` has either. Every gate here is
  wired into a command and into `.github/workflows/check.yml` in the same change that created it.
- **Notebooks are scored, not reviewed.** `scripts/score.py` is deterministic and the threshold is
  95 for every notebook and every vault. `docs/CONTRACT.md` defines what it measures.
- **Nothing hardcodes a provider number.** Prices, context lengths and limits are read from
  `provider-truth.json` at the root, written by `make probe` from the live API and committed,
  because a clone with no key still has to print a real cost. `check-prose` fails on a
  provider constant typed into prose.
- **Fixtures, not live calls, are the test path.** `make test` replays committed responses, so CI
  needs no key and spends nothing. `make test-live` is the one that costs money. Replay also waits
  as long as the recorded call did, so a lesson that measures wall clock reads the same either way.
- **The syllabus is a gate.** `config/syllabus.yml` records what each vault promised to teach and
  `check-coverage` fails if a promise stops being kept. It exists because an audit found two topics
  promised in the course specs and missing from the notebooks.

## Where things live

The root is the learner's surface: the numbered vaults, `README.md`, `Makefile` and the packaging
files. Everything the gates read lives in `config/`, everything about authoring lives in `docs/`.
`check-structure` fails on a new root entry that is not on its allow-list.

## The contract

`docs/CONTRACT.md` is the frozen definition of the seven beats, the cell limits, the score thresholds and
the domain register. Changing it forces a re-score of everything already accepted. Read it before
authoring or editing any notebook.
