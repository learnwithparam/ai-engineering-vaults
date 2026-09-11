# Autonomous Subagent Workflows for Senior Developers

One course in one notebook: `01-delegate-a-migration-to-a-subagent.ipynb`.

You build the migrate command of a coding assistant that works on a web shop's customer database.
A developer types the command, and the assistant hands the whole migration to a subagent: a second
agent run with its own message history. The subagent reads every line of the migration log, and
only a short typed summary comes back to the developer's main session.

The notebook starts with a real database and its migrations. Then it adds custom commands for
manual actions, packages the migration as a skill with a fork flag, and measures what the log costs
when the skill runs in the main session. From there it forks the skill into a subagent, returns a
typed summary instead of prose, lets the model choose the skill from a plain request, and checks
every summary against the database before anyone trusts it.

## Before you start

Run `00-setup/01-start-here.ipynb` first. The notebook runs without an API key, from committed
recordings of real responses, so you can follow the whole course for free.

## What you will have built

A command registry, a skill that runs in a forked subagent, and a typed summary checked against the
migration table, with a test for each safeguard that runs without calling the model.
