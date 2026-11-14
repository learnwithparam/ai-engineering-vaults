# Test one agent contract with a framework-free loop

One course in one notebook: `01-test-an-agent-contract.ipynb`.

A team rewrote its agent on a new framework. The rewrite passed every demo and then assigned a pilot
past the duty hours limit, because the old behaviour lived in a prompt and a loop that nobody had
written down. Here you build the crew-rebooking agent for an airline operations desk and write down
what it must do as six plain checks, so any runner can be tested against them.

The notebook runs the same six cases through your own plain loop and through a second runner whose
result has the shape an agent framework gives you. It then plants a broken runner that skips the duty
check and shows the failure naming the clause it broke.

## Before you start

Run `00-setup/01-start-here.ipynb` first. The notebook runs without an API key, from committed
recordings of real responses, so you can follow the whole course for free.

## What you will have built

An agent contract of six conformance cases, one runner interface that both runners satisfy, a
comparison of the two runners, and tests for the contract that run without calling the model.
