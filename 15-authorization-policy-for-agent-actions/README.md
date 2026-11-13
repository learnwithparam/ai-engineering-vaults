# Authorize Agent Actions with a Policy Evaluator

One course in one notebook: `01-authorize-agent-actions-with-policies.ipynb`.

A data agent for a company's staff acts through one shared service credential, so it can do whatever that credential can do. An intern's session asked it to export the salary table and email it out, and it did. This course builds an authorization policy that the code checks before every tool runs, and a small policy evaluator that decides each request and gives a reason for every denial.

The notebook counts the wrong answers of the shared credential. It then adds permit rules, forbid rules, a refund limit and default deny, and checks the whole recorded log against the answers a careful manager would give. It ends with tests that run without calling a model.

## Before you start

Run `make setup` once. The notebook calls no model, so it needs no API key and costs nothing to run.

## What you will have built

A policy evaluator that answers every recorded request the way the policy says, gives a reason for every denial, and passes tests that run without a model.
