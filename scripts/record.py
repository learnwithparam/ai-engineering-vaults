"""Refresh fixtures against the real API, with a budget guard.

Runs every notebook in record mode, so each committed fixture is a response the
provider really gave. Checks credit before and after, and refuses to start if
the remaining balance is below a floor.
"""
from __future__ import annotations

import os
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from nbcommon import ROOT
from probe_provider import _key, budget

MINIMUM_REMAINING_USD = 1.00
MAXIMUM_SPEND_PER_RUN_USD = 2.00


def remaining(snapshot: dict) -> float:
    value = snapshot.get("limit_remaining_usd")
    return float(value) if value is not None else float("inf")


def main() -> int:
    key = _key()
    before = budget(key)
    start = remaining(before)
    print(f"budget before: {start} USD remaining of {before.get('limit_usd')}")

    if start < MINIMUM_REMAINING_USD:
        print(f"Refusing to record. Remaining credit is below {MINIMUM_REMAINING_USD} USD.")
        return 1

    os.environ["VAULT_MODE"] = "record"
    from run_notebooks import main as run_all
    result = run_all()

    after = budget(key)
    end = remaining(after)
    spent = start - end
    print(f"budget after:  {end} USD remaining")
    print(f"spent this run: {spent:.4f} USD")

    if spent > MAXIMUM_SPEND_PER_RUN_USD:
        print(f"WARNING: spend exceeded the {MAXIMUM_SPEND_PER_RUN_USD} USD cap for one run")
        return 1
    return result


if __name__ == "__main__":
    raise SystemExit(main())
