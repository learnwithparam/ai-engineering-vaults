#!/usr/bin/env python3
"""Audit a diff with a model and block the pipeline when it finds something.

Usage:
    python audit.py --diff pr.diff --schema audit-schema.json --max-seconds 120

Channels:
    stdout   the validated JSON report, and nothing else
    stderr   narration, timings and errors
    exit 0   nothing found, the merge may proceed
    exit 1   the audit itself broke, which is not the same as clean
    exit 2   a finding, the merge is blocked

The key is read from the environment, never from a flag, because argv shows up
in the process list and in the job log. In CI it comes from the secret store.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import sys
import time

from openai import APIError

from vault import get_client, load_env, model_for

NOTEBOOK = "06-headless-automation/03-capstone-a-pr-audit-that-blocks"
SYSTEM = ("You review a diff from a card payments service that handles chargebacks. "
          "Report only what the diff shows. Set verdict to block if any finding is high.")

SECRET_SHAPES = [
    re.compile(r"sk-[a-z0-9\-]{2,10}-[A-Za-z0-9\-_]{20,}"),
    re.compile(r"gh[pousr]_[A-Za-z0-9]{30,}"),
    re.compile(r"\bAIza[0-9A-Za-z\-_]{30,}"),
]
BLOCKING = {"high"}


def narrate(message: str) -> None:
    """Everything a person needs later goes to stderr, never to stdout."""
    print(f"[audit] {message}", file=sys.stderr, flush=True)


def redact(text: str) -> str:
    """Nothing leaves this process with a credential still in it."""
    for shape in SECRET_SHAPES:
        text = shape.sub("[redacted]", text)
    return text


def refuse_credentials_on_argv(argv: list[str]) -> None:
    """A key passed as a flag is already in the process list and the log."""
    for shape in SECRET_SHAPES:
        if any(shape.search(arg) for arg in argv):
            raise SystemExit("a credential was passed on the command line. "
                             "Use the CI secret store and the environment instead.")


def validate(report: dict, schema: dict) -> dict:
    """Reject a reply that is the right shape but the wrong answer."""
    for field in schema["required"]:
        if field not in report:
            raise ValueError(f"report is missing {field!r}")
    allowed = schema["properties"]["verdict"]["enum"]
    if report["verdict"] not in allowed:
        raise ValueError(f"verdict {report['verdict']!r} is not one of {allowed}")
    item = schema["properties"]["findings"]["items"]["properties"]
    for finding in report["findings"]:
        for field, rule in item.items():
            if "enum" in rule and finding.get(field) not in rule["enum"]:
                raise ValueError(f"{field} {finding.get(field)!r} is not one of {rule['enum']}")
    return report


def review(diff: str, schema: dict, seconds: int) -> dict:
    """One model call, answered in the shape the pipeline branches on.

    The bound is on the request, and it is per attempt. The SDK retries, so a
    one second bound was measured taking 1.35 seconds of wall clock in total.
    A signal alarm looks like it bounds this and does not: measured here, the
    call ran to completion with the alarm already past due.
    """
    client = get_client(NOTEBOOK)
    reply = client.chat.completions.create(
        model=model_for("default"), max_tokens=800, timeout=seconds,
        response_format={"type": "json_schema",
                         "json_schema": {"name": "audit", "strict": True, "schema": schema}},
        messages=[{"role": "system", "content": SYSTEM},
                  {"role": "user", "content": diff}])
    return json.loads(reply.choices[0].message.content)


def exit_code_for(report: dict) -> int:
    """0 clean, 2 blocked. 1 is reserved for the audit breaking."""
    worst = {f["severity"] for f in report["findings"]}
    return 2 if report["verdict"] == "block" or worst & BLOCKING else 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit a diff and block on a finding.")
    parser.add_argument("--diff", required=True)
    parser.add_argument("--schema", required=True)
    parser.add_argument("--max-seconds", type=int, default=120)
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    refuse_credentials_on_argv(argv)
    args = parse_args(argv)
    load_env()
    if not os.environ.get("OPENROUTER_API_KEY") and os.environ.get("VAULT_MODE") != "replay":
        narrate("OPENROUTER_API_KEY is not set. In CI it comes from the secret store.")
        return 1

    started = time.monotonic()
    try:
        schema = json.loads(pathlib.Path(args.schema).read_text())
        diff = pathlib.Path(args.diff).read_text()
        report = validate(review(diff, schema, args.max_seconds), schema)
    except (APIError, ValueError, OSError, json.JSONDecodeError) as broke:
        narrate(f"the audit failed: {type(broke).__name__}: {redact(str(broke))}")
        return 1

    narrate(f"reviewed in {time.monotonic() - started:.2f}s, "
            f"{len(report['findings'])} findings, verdict {report['verdict']}")
    print(redact(json.dumps(report, indent=2)))
    return exit_code_for(report)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
