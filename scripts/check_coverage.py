"""Every vault still teaches what it promised.

A one-off audit found two topics promised in the course specs and missing from
the built notebooks. This turns that audit into a check, so the next gap fails
the build instead of surviving to recording day.
"""
from __future__ import annotations

import pathlib
import re
import sys

import yaml

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import nbcommon as nb
from nbcommon import ROOT, CONFIG


def searchable(notebooks) -> dict[int, str]:
    """Everything a vault says, in prose, code and committed output."""
    blob: dict[int, str] = {}
    for n in notebooks:
        vault = n.meta.get("vault")
        blob.setdefault(vault, "")
        blob[vault] += f"{n.prose}\n{chr(10).join(n.code_cells)}\n{n.outputs_text()}\n"
    return blob


def main() -> int:
    syllabus = yaml.safe_load((CONFIG / "syllabus.yml").read_text())
    notebooks = nb.all_notebooks()
    if not notebooks:
        print("check-coverage: no notebooks yet")
        return 0

    blob = searchable(notebooks)
    problems = []
    checked = 0
    for vault, promises in sorted(syllabus.items()):
        text = blob.get(vault)
        if text is None:
            problems.append(f"vault {vault}: promised in config/syllabus.yml but no notebooks found")
            continue
        for concept, pattern in promises.items():
            checked += 1
            if not re.search(pattern, text, re.I):
                problems.append(
                    f"vault {vault}: promised {concept!r} and never teaches it. "
                    f"Add it, or remove the promise from config/syllabus.yml")

    for line in problems:
        print(f"  {line}")
    print(f"check-coverage: {checked} promises across {len(syllabus)} vaults, "
          f"{len(problems)} unmet")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
