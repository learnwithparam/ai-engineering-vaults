"""Execute every notebook. Replay by default, so CI needs no key.

Executes a copy, so a run never rewrites the committed outputs. Refreshing
those is the recorder's job, not the test's.
"""
from __future__ import annotations

import os
import pathlib
import sys
import time

import nbformat
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import nbcommon as nb
from nbcommon import ROOT

TIMEOUT_SECONDS = 300


def run_one(path: pathlib.Path) -> tuple[bool, str]:
    doc = nbformat.read(path, as_version=4)
    client = NotebookClient(doc, timeout=TIMEOUT_SECONDS, kernel_name="python3",
                            resources={"metadata": {"path": str(path.parent)}})
    try:
        client.execute()
        return True, ""
    except CellExecutionError as exc:
        return False, str(exc)[-700:]
    except Exception as exc:  # noqa: BLE001 - report anything, do not hide it
        return False, f"{type(exc).__name__}: {exc}"


def main() -> int:
    mode = os.environ.get("VAULT_MODE", "replay")
    # VAULT=01 runs one vault, so recording a lesson spends nothing on the others.
    only = os.environ.get("VAULT", "")
    paths = sorted(p for p in ROOT.glob("[0-9][0-9]-*/*.ipynb")
                   if ".ipynb_checkpoints" not in p.parts and p.parent.name.startswith(only))
    if not paths:
        print("run-notebooks: no notebooks yet")
        return 0

    print(f"Executing {len(paths)} notebooks in {mode} mode")
    failures = []
    for path in paths:
        rel = path.relative_to(ROOT)
        started = time.monotonic()
        ok, detail = run_one(path)
        took = time.monotonic() - started
        print(f"  {'ok  ' if ok else 'FAIL'} {rel}  {took:.1f}s")
        if not ok:
            failures.append((rel, detail))

    if failures:
        print(f"\n{len(failures)} notebooks failed:\n")
        for rel, detail in failures:
            print(f"{rel}\n{detail}\n")
        return 1
    print(f"\nAll {len(paths)} notebooks executed in {mode} mode")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
