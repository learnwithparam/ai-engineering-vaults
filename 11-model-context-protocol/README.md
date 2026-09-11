# Model Context Protocol for Enterprise System Integration

One course in one notebook: `01-connect-an-mcp-client-to-a-database.ipynb`.

You connect an assistant to a finance team's reporting database. A small MCP server sits in front of
the database and offers read only queries as tools, the schema and customer records as resources,
and a summary request as a prompt. Your client starts that server, speaks JSON-RPC 2.0 to it, and
carries each tool call from the model to the server and back. The database is a SQLite file standing
in for the company's PostgreSQL server, so the course needs no install.

The notebook starts with one handshake over stdio, then grows the client one step at a time. It
translates the server's tools for the model, reads failed calls correctly, keeps every log line on
stderr so the reply stream stays clean, and reaches the same server over HTTP.

## Before you start

Run `00-setup/01-start-here.ipynb` first. The notebook runs without an API key, from committed
recordings of real responses, so you can follow the whole course for free. The MCP server runs for
real on your machine either way.

## What you will have built

A small MCP client and a read only MCP server, with a test for each safeguard, all of which run
without calling the model.
