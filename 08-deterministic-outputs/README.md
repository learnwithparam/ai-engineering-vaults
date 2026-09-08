# Deterministic outputs

**One video, about thirty minutes.** How a model is made to answer in a shape your code can rely on,
and the two ways that still is not enough.

One idea runs through the vault: **a shape is not an answer.** Forcing a reply into a fixed shape
removes the parse failures and nothing else. A value can pass every type, every enum and every
required list and still be wrong, and knowing where that line sits is the whole point of the vault.

| Sub-module | What breaks | Domain |
|---|---|---|
| `01-forcing-a-shape.ipynb` | "Reply with JSON only" comes back wrapped in a markdown fence, and four notes file nothing | Insurance claims |
| `02-schema-design-for-reliability.ipynb` | A loose schema returns `10+` kills and a role that is not a role | Esports analytics |
| `03-capstone-a-typed-extractor.ipynb` | A corrupt log line becomes a valid crew swap for a real flight | Airline crew scheduling |

The first two use raw tool calls, because the setting being taught is the setting itself. The capstone
uses Pydantic AI, where the Python type is the contract for the whole call.

## Before you start

Run `00-setup/01-start-here.ipynb` first. Every notebook here runs without an API key, from committed
recordings, so you can read and execute the whole vault for free. The capstone runs its Pydantic AI
agent through `FunctionModel`, driven by the recorded provider answers, so it needs no key either.

## What you will have built

An extractor with a typed contract: forced through a named tool, held to a schema whose closed sets
are closed and whose blanks are honest, able to return a refusal as a first class shape, and carrying
a test for each of those properties that runs with no network.

## Where this vault stops

Every check here asks whether an answer has the right shape. Nothing here asks whether it is true.
Rejecting a value that is the right shape and the wrong answer is a validator, and that is vault 9.
