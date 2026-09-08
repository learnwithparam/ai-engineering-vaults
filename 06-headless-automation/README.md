# Headless automation for CI

**One video, about thirty minutes.** What changes about an agent when nobody is watching it run,
and how to make a pipeline able to stop because of what it found.

Everything here rests on one idea: **the exit code is the interface.** A job runner never reads your
report. It reads one integer and decides whether the next step happens. Most of the failures in this
vault are cases where that integer was never wired to anything real.

| Sub-module | What breaks | Domain |
|---|---|---|
| `01-the-non-interactive-contract.ipynb` | A confirmation prompt hangs the job, and a paging finding still exits 0 | Incident response |
| `02-a-schema-is-the-interface.ipynb` | Every reply arrives in a code fence, and one queue arrives under three spellings | Public services |
| `03-capstone-a-pr-audit-that-blocks.ipynb` | An audit that found three real problems and blocked nothing | Card chargebacks |

## Files in this folder

| File | What it is |
|---|---|
| `audit.py` | The entrypoint the capstone builds. Runnable on its own |
| `audit-schema.json` | The shape the audit answers in |
| `sample-diff.txt` | A chargeback refund change with three problems in it |
| `clean-diff.txt` | The same file, changed harmlessly, so the audit can pass |
| `example-workflow.yml` | A GitHub Actions workflow to copy. Deliberately not in `.github/workflows/` here |

## Before you start

Run `00-setup/01-start-here.ipynb` first. Every notebook here runs without an API key, from
committed recordings, so you can execute the whole vault for free.

Run the entrypoint on its own:

```bash
uv run python audit.py --diff sample-diff.txt --schema audit-schema.json --max-seconds 60
echo $?      # 2, because the diff has a blocking finding
```

## What you will have built

A step that cannot be asked a question and cannot run forever, an answer shaped so a pipeline can
branch on it, a tool allowlist that holds when an instruction does not, and an entrypoint plus a
workflow that turns a finding into a blocked merge without ever writing a key to a log.
