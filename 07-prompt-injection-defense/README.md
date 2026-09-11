# Defensive Prompt Engineering for Enterprise AI Security

One course in one notebook: `01-defend-a-resume-screener.ipynb`.

You build a resume screener for a hiring team. Each resume arrives inside `resume_content` tags, and
the screener's instructions tell the model to judge skills only from the text inside those tags and
to ignore any instructions written there. The resume and the candidate's portfolio page are both
written by the candidate, so either one can try to give the model orders.

The notebook starts with a single screening call, shows real resumes ordering their own advance,
then adds one defense at a time: tags and an instruction hierarchy, tags a candidate cannot close,
wrapped tool results, and finally a rubric in code that no text can reach. Every layer is scored
against the same small corpus of attack resumes.

## Before you start

Run `00-setup/01-start-here.ipynb` first. The notebook runs without an API key, from committed
recordings of real responses, so you can follow the whole course for free.

## What you will have built

A screener whose advance decision lives in code, an attack corpus that puts a number on each
defense, and tests for the tag handling and the rubric that run without calling the model.
