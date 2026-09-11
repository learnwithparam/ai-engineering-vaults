# Low-Entropy Tool Design for Reliable AI Agents

One course in one notebook: `01-design-low-entropy-tools.ipynb`.

You build the tool suite for an agent on a customer account portal. Customers ask about their plan,
their invoices and their contact email, and report problems that need a person. The portal grew 25
generic tools over the years, and the model has to guess which one a request belongs to.

The notebook measures how often the model picks the right tool, with real runs, and how spread out
its picks are in bits. It then replaces the 25 tools with four tightly scoped ones, writes each
description as the conditions for calling the tool, locks every schema, and adds middleware that
checks every argument before a tool runs.

## Before you start

Run `00-setup/01-start-here.ipynb` first. The notebook runs without an API key, from committed
recordings of real responses, so you can follow the whole course for free.

## What you will have built

A suite of four scoped tools with locked schemas, a selection eval that scores any tool suite, and
middleware that refuses a bad call before it reaches the portal, with tests that run without calling
the model.
