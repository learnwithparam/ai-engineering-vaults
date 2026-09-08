# 006: Replay must accept a finish reason the SDK does not list

Date: 2026-09-09
Status: accepted

## What happened

Forcing extraction through `tool_choice` on `google/gemini-2.5-flash-lite` made the model emit
repeated tool calls until it hit the token cap. OpenRouter reported that as
`finish_reason: "error"`.

The OpenAI SDK's `ChatCompletion` type allows only `stop`, `length` and `tool_calls`, so
`model_validate` raised on the recorded response. The lesson had been recorded from a real call and
could not be replayed from it.

## Why this matters beyond one fixture

A gateway in front of many upstream providers will surface values the client library does not
enumerate. If replay is stricter than the live path, a recording stops being a faithful record of
what happened, which is the only thing it is for.

## Decision

`vault.client.parse_completion` validates strictly first, then falls back to a widened model that
accepts any string as a finish reason. The value is preserved rather than coerced, so a lesson can
show `error` if that is what the provider said.

## What this does not do

It does not hide the problem. Vault 2 and vault 10 both carry fixtures with `finish_reason: "error"`,
and those notebooks show it. A model that loops on forced tool choice until it dies is worth seeing,
not worth smoothing over.

Vaults using forced `tool_choice` should expect this on some models.
