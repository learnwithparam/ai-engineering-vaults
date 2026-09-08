"""Every notebook is valid JSON and a valid notebook."""
from __future__ import annotations

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from nbcommon import ROOT


def main() -> int:
    paths = sorted(p for p in ROOT.glob("[0-9][0-9]-*/*.ipynb")
                   if ".ipynb_checkpoints" not in p.parts)
    if not paths:
        print("check-notebooks: no notebooks yet")
        return 0

    bad = []
    for path in paths:
        rel = path.relative_to(ROOT)
        try:
            doc = json.loads(path.read_text())
        except json.JSONDecodeError as exc:
            bad.append(f"{rel}: invalid JSON at line {exc.lineno}")
            continue
        if "cells" not in doc:
            bad.append(f"{rel}: no cells key")
            continue
        for i, cell in enumerate(doc["cells"]):
            if cell.get("cell_type") not in ("markdown", "code", "raw"):
                bad.append(f"{rel}: cell {i} has an unknown cell_type")

    for line in bad:
        print(f"  {line}")
    print(f"check-notebooks: {len(paths)} notebooks, {len(bad)} problems")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
