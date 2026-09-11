"""Vault shape: one course notebook per vault, a README that lists it, a clean root."""
from __future__ import annotations

import pathlib
import re
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import nbcommon as nb
from nbcommon import ROOT

# What a learner is allowed to see at the root. Everything else is authoring
# machinery and belongs in config/ or docs/. A vault folder matches NN-name.
ROOT_ALLOWED = {
    ".github", ".gitignore", ".jupyter", ".python-version",
    "AGENTS.md", "CLAUDE.md", "Makefile", "README.md",
    "build", "config", "diagrams", "docs", "scripts", "vault",
    "env.example", "provider-truth.json", "pyproject.toml", "uv.lock",
}
VAULT_DIR = re.compile(r"^\d\d-[a-z0-9-]+$")


def ignored(entry: pathlib.Path) -> bool:
    """Ask git, so .env and a lesson's own runtime files never trip this."""
    result = subprocess.run(["git", "check-ignore", "--quiet", entry.name],
                            cwd=ROOT, capture_output=True)
    return result.returncode == 0


def root_problems() -> list[str]:
    if not (ROOT / ".git").exists():
        print("  root inventory skipped: not a git checkout")
        return []
    out = []
    for entry in sorted(ROOT.iterdir()):
        name = entry.name
        if name == ".git" or name in ROOT_ALLOWED or VAULT_DIR.match(name):
            continue
        if ignored(entry):
            continue
        out.append(f"root: {name} is not on the root allow-list. "
                   f"Authoring config belongs in config/, authoring docs in docs/")
    return out


def main() -> int:
    vaults = nb.vault_dirs()
    if not vaults:
        print("check-structure: no vaults yet")
        return 0

    problems = root_problems()
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
        elif len(notebooks) != 1:
            problems.append(f"{rel}: {len(notebooks)} notebooks, the contract says one course "
                            f"notebook per vault")

    for line in problems:
        print(f"  {line}")
    print(f"check-structure: {len(vaults)} vaults, {len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
