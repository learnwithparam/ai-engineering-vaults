"""Every notebook has the fixtures it needs, and no fixture rots unused.

Unused fixtures matter: a stale one means a prompt changed and nobody noticed
which recording the lesson is really running on.
"""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import nbcommon as nb
from nbcommon import ROOT


def fixture_dir_for(n: nb.Notebook) -> pathlib.Path:
    return n.path.parent / "fixtures" / n.path.stem


def calls_the_model(n: nb.Notebook) -> bool:
    return any("get_client" in c for c in n.code_cells)


def main() -> int:
    notebooks = nb.all_notebooks()
    if not notebooks:
        print("check-fixtures: no notebooks yet")
        return 0

    problems = []
    used_dirs = set()
    for n in notebooks:
        directory = fixture_dir_for(n)
        if not calls_the_model(n):
            continue
        used_dirs.add(directory.resolve())
        if not directory.is_dir() or not list(directory.glob("*.json")):
            problems.append(f"{n.rel}: calls the model but has no fixtures. Run: make record")

    for directory in sorted(ROOT.glob("[0-9][0-9]-*/fixtures/*")):
        if directory.is_dir() and directory.resolve() not in used_dirs:
            rel = directory.relative_to(ROOT)
            problems.append(f"{rel}: fixtures with no notebook using them. Delete them")

    for line in problems:
        print(f"  {line}")
    print(f"check-fixtures: {len(notebooks)} notebooks, {len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
