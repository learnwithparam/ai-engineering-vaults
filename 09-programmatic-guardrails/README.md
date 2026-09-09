# Programmatic guardrails

A schema tells you the shape is right. It says nothing about whether the answer is possible, and
production is full of possible-looking answers that are not.

Everything here rests on one idea: **checking is a job for your code, and it has three parts.** Is
the shape right, is the meaning right, and what do you do when it is not. A retry answers only the
last one, and only if it terminates.

| Sub-module | What breaks | Domain |
|---|---|---|
| `01-valid-json-wrong-answer.ipynb` | Six schema-valid records, a risk score of 118, a negative amount and a period that runs backwards | Anti money laundering case work |
| `02-the-error-taxonomy.ipynb` | One retry wrapper sends the same illegal grid command three times and pays three times for an empty answer | Grid load and EV charging |
| `03-capstone-a-retry-loop-that-terminates.ipynb` | A repair loop invents the value that was blocking it, and the record passes | Clinical trial safety reporting |

## Before you start

Run `00-setup/01-start-here.ipynb` first. Every notebook here runs without an API key, from
committed recordings, so you can read and execute the whole vault for free.

## What you will have built

A validation layer that separates shape from meaning, a classifier that sends each of the four
failure tiers to its own handler, a bounded repair loop that feeds the validator's own words back to
the model, a dead letter shelf for records no reply can fix, and a test for each of those
properties.
