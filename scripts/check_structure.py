"""Vault shape: README coverage, capstones, sub-module count."""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import nbcommon as nb
from nbcommon import ROOT


def main() -> int:
    vaults = nb.vault_dirs()
    if not vaults:
        print("check-structure: no vaults yet")
        return 0

    problems = []
    for vault in vaults:
        rel = vault.relative_to(ROOT)
        notebooks = sorted(p for p in vault.glob("[0-9][0-9]-*.ipynb")
                           if ".ipynb_checkpoints" not in p.parts)
        readme = vault / "README.md"

        if not readme.is_file():
            problems.append(f"{rel}: no README.md")
        else:
            text = readme.read_text()
            for path in notebooks:
                if path.name not in text:
                    problems.append(f"{rel}: README does not list {path.name}")

        if not notebooks:
            problems.append(f"{rel}: no notebooks")
            continue
        if "capstone" not in notebooks[-1].stem:
            problems.append(
                f"{rel}: the last notebook is not a capstone, it is {notebooks[-1].name}")
        if not 3 <= len(notebooks) <= 4:
            problems.append(
                f"{rel}: {len(notebooks)} notebooks, the contract says three or four")

    for line in problems:
        print(f"  {line}")
    print(f"check-structure: {len(vaults)} vaults, {len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
