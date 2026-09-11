# Headless AI Automation for CI/CD Pipelines

One course in one notebook: `01-audit-sql-in-a-ci-pipeline.ipynb`.

You build the SQL audit a CI pipeline runs on every pull request. A script sends the changed code to
a model with nobody watching, the model reviews every SQL query in it, and the pipeline blocks the
merge when the model finds a query an attacker could abuse.

The notebook starts with a reply the pipeline cannot parse, then grows it one step at a time into an
audit whose report is locked to a JSON schema, whose tools are limited to reading by an allowlist,
whose step can never wait for a person, whose exit code decides the merge, and whose log and report
never carry a password or an API key.

## Before you start

Run `00-setup/01-start-here.ipynb` first, and read `01-stateful-agent-runtime/` before this vault.
The notebook runs without an API key, from committed recordings of real responses, so you can
follow the whole course for free.

## What you will have built

A headless SQL audit step with a test for each of its safeguards, all of which run without calling
the model.
