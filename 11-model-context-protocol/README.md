# Model Context Protocol

How a model reaches your systems without a connector per pair, and the two ways a server built on
that protocol goes wrong in production.

Everything here rests on one idea: **the protocol carries claims, and your code carries controls.**
A description, an annotation and a schema all travel on the wire. None of them stops anything.

| Sub-module | What breaks | Domain |
|---|---|---|
| `01-the-protocol-and-its-primitives.ipynb` | Two failed tool calls counted as successes, one underscore apart | Catalogue and listening recommendation |
| `02-stdio-and-the-stderr-rule.ipynb` | One trace on stdout eats the reply, and the host freezes rather than errors | Container terminal flow |
| `03-capstone-a-read-only-server.ipynb` | A tool marked read only in two places deletes rows and returns a credential | Industrial asset failure prediction |

## Before you start

Run `00-setup/01-start-here.ipynb` first. Nothing in this vault calls a model, so every notebook runs
with no API key and no spend. The servers it talks to are in `servers/`, and they are real MCP servers
started as child processes.

## What you will have built

A host adapter that translates the wire shape once and refuses anything else, a check that proves a
server writes nothing but the protocol on stdout, and a read only MCP server whose read only claim is
enforced by a connection mode and an allowlist rather than by its own description.
