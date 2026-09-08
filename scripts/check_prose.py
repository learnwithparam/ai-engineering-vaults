"""Prose rules, provider honesty, and secrets.

The secrets scan covers committed cell outputs as well as source, because this
repo commits outputs so a learner sees expected results. That makes an output a
real leak path, not a theoretical one.
"""
from __future__ import annotations

import pathlib
import re
import sys

import yaml

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import nbcommon as nb
from nbcommon import ROOT

KEY_SHAPES = [
    (re.compile(r"sk-or-v1-[A-Za-z0-9]{20,}"), "OpenRouter key"),
    (re.compile(r"sk-ant-[A-Za-z0-9\-_]{20,}"), "Anthropic key"),
    (re.compile(r"sk-proj-[A-Za-z0-9\-_]{20,}"), "OpenAI project key"),
    (re.compile(r"\bAIza[0-9A-Za-z\-_]{30,}"), "Google API key"),
    (re.compile(r"ghp_[A-Za-z0-9]{30,}"), "GitHub token"),
]


def scan_secrets(notebooks: list[nb.Notebook]) -> list[str]:
    problems = []
    for n in notebooks:
        haystacks = {"source": n.prose + "\n".join(n.code_cells),
                     "committed output": n.outputs_text()}
        for where, text in haystacks.items():
            for pattern, label in KEY_SHAPES:
                if pattern.search(text):
                    problems.append(f"{n.rel}: {label} found in {where}")
    return problems


def scan_prose(notebooks: list[nb.Notebook], banned: dict) -> list[str]:
    problems = []
    for n in notebooks:
        for i, text in enumerate(n.markdown_cells):
            prose = nb.strip_code_and_media(text)
            lower = prose.lower()
            if "—" in prose or "–" in prose:
                problems.append(f"{n.rel} cell {i}: em dash or en dash")
            for word in banned["words"]:
                if re.search(rf"\b{re.escape(word)}\b", lower):
                    problems.append(f"{n.rel} cell {i}: banned word {word!r}")
            for phrase in banned["phrases"]:
                if phrase in lower:
                    problems.append(f"{n.rel} cell {i}: banned phrase {phrase!r}")
            for constant in banned["provider_constants"]:
                if constant.lower() in lower:
                    problems.append(
                        f"{n.rel} cell {i}: provider constant {constant!r} written as prose. "
                        f"Print it from a live response instead")
    return problems


def scan_glossary(notebooks: list[nb.Notebook], glossary: dict) -> list[str]:
    """A term must be explained somewhere in the vault that uses it."""
    by_vault: dict[str, list[nb.Notebook]] = {}
    for n in notebooks:
        by_vault.setdefault(n.vault_dir, []).append(n)

    problems = []
    for vault, group in sorted(by_vault.items()):
        text = " ".join(nb.strip_code_and_media(n.prose) for n in group).lower()
        for term, definition in glossary.items():
            if not re.search(rf"\b{re.escape(term)}\b", text):
                continue
            anchor = [w for w in nb.words(definition.lower()) if len(w) > 4][:3]
            if anchor and not any(a in text for a in anchor):
                problems.append(
                    f"{vault}: uses {term!r} but never explains it. "
                    f"Say something like: {definition}")
    return problems


def main() -> int:
    notebooks = nb.every_notebook()
    if not notebooks:
        print("check-prose: no notebooks yet")
        return 0

    banned = yaml.safe_load((ROOT / "banned.yml").read_text())
    glossary = yaml.safe_load((ROOT / "glossary.yml").read_text())

    secrets = scan_secrets(notebooks)
    prose = scan_prose(notebooks, banned)
    terms = scan_glossary(notebooks, glossary)

    for line in secrets:
        print(f"  SECRET  {line}")
    for line in prose + terms:
        print(f"  {line}")

    total = len(secrets) + len(prose) + len(terms)
    print(f"check-prose: {len(notebooks)} notebooks, {total} problems"
          + (f", {len(secrets)} of them secrets" if secrets else ""))
    return 1 if total else 0


if __name__ == "__main__":
    raise SystemExit(main())
