"""Prove the gates bite.

A gate that has never failed is not known to gate anything. This plants a
deliberately broken vault, asserts each gate rejects it, then removes it.

It runs inside `make check`, so the checks are themselves checked on every run
and in CI, rather than being verified once by hand and trusted forever.
"""
from __future__ import annotations

import json
import pathlib
import shutil
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from nbcommon import ROOT

PLANT = ROOT / "99-gate-selftest"
SCRIPTS = ROOT / "scripts"


def run_gate(script: str) -> tuple[int, str]:
    result = subprocess.run([sys.executable, str(SCRIPTS / script)],
                            capture_output=True, text=True, cwd=ROOT, timeout=180)
    return result.returncode, result.stdout + result.stderr


def notebook(cells: list[dict], meta: dict) -> dict:
    return {
        "cells": cells,
        "metadata": {"vault": meta,
                     "kernelspec": {"display_name": "Python 3", "language": "python",
                                    "name": "python3"},
                     "language_info": {"name": "python", "version": "3.11"}},
        "nbformat": 4, "nbformat_minor": 5,
    }


def md(text: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": text}


def code(text: str) -> dict:
    return {"cell_type": "code", "metadata": {}, "source": text,
            "execution_count": None, "outputs": []}


def plant_broken() -> None:
    """One notebook that breaks something in every dimension at once."""
    PLANT.mkdir(parents=True, exist_ok=True)
    (PLANT / "README.md").write_text("# Gate self test\n")

    cells = [
        md("# Broken on purpose\n\nThis notebook exists so the gates can be proven to bite."),
        md("## Mechanics\n\nWe leverage a robust paradigm here."),
        md("A cache needs 1,024 tokens, which is a provider constant written as prose."),
        code("import os\nkey = 'sk-or-v1-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'"),
        code("def one():\n    pass\n\ndef two():\n    pass"),
        md("It also references a picture that was never rendered."),
        code("from vault.client import get_client\nclient = get_client('99-gate-selftest/01-broken')"),
        md("![missing](images/never-rendered.svg)"),
    ]
    # syllabus.yml gains a vault that has no notebooks, so coverage has a gap.
    syllabus = ROOT / "syllabus.yml"
    original = syllabus.read_text()
    syllabus.write_text(original + "\n98:\n  a promise nothing keeps: this-phrase-appears-nowhere\n")
    (PLANT / "syllabus.backup").write_text(original)

    doc = notebook(cells, {"vault": 99, "submodule": 1, "title": "Broken",
                           "domain": "not-a-real-domain", "framework": "none",
                           "analogy": ""})
    (PLANT / "01-broken.ipynb").write_text(json.dumps(doc, indent=1))

    # A diagram source with no rendered SVG, so check-diagrams has something to catch.
    (PLANT / "diagrams").mkdir(exist_ok=True)
    (PLANT / "diagrams" / "unrendered.mmd").write_text("graph LR\n  A[in] --> B[out]\n")


EXPECTED = [
    ("check_structure.py", "structure", "no capstone, wrong notebook count, README gaps"),
    ("check_prose.py", "prose", "banned words, a provider constant, and a planted key"),
    ("check_diagrams.py", "diagrams", "a .mmd with no SVG and a dead image reference"),
    ("check_fixtures.py", "fixtures", "a notebook calling the model with no fixtures"),
    ("score.py", "score", "missing beats, bad domain, no analogy, two defs in one cell"),
    ("check_coverage.py", "coverage", "a vault in the syllabus with no notebooks"),
]


def theme_gate_bites() -> str:
    """Hide one theme file, confirm check-theme notices, put it back."""
    css = ROOT / ".jupyter" / "custom" / "custom.css"
    hidden = css.with_suffix(".css.hidden")
    css.rename(hidden)
    try:
        rc, _ = run_gate("check_theme.py")
    finally:
        hidden.rename(css)
    if rc == 0:
        return "theme: did NOT bite when custom.css was removed"
    print("  theme      bit as expected (custom.css missing)")
    if run_gate("check_theme.py")[0] != 0:
        return "theme: still failing after custom.css was restored"
    return ""


def main() -> int:
    if PLANT.exists():
        shutil.rmtree(PLANT)

    baseline = {name: run_gate(name)[0] for name, _, _ in EXPECTED}
    dirty = [n for n, rc in baseline.items() if rc != 0]
    if dirty:
        print(f"  cannot self test: these already fail before planting: {dirty}")
        return 1

    plant_broken()
    try:
        failures = []
        for script, label, why in EXPECTED:
            rc, output = run_gate(script)
            if rc == 0:
                failures.append(f"{label}: did NOT bite. Expected it to catch {why}")
            else:
                print(f"  {label:10} bit as expected ({why})")
            if "sk-or-v1-aaaa" in output:
                failures.append(f"{label}: printed the planted key in its own output")
        problem = theme_gate_bites()
        if problem:
            failures.append(problem)
        backup = PLANT / "syllabus.backup"
        if backup.is_file():
            (ROOT / "syllabus.yml").write_text(backup.read_text())
    finally:
        shutil.rmtree(PLANT)

    restored = [n for n, _, _ in EXPECTED if run_gate(n)[0] != 0]
    if restored:
        failures.append(f"after cleanup these still fail: {restored}")

    for line in failures:
        print(f"  {line}")
    print(f"check-gates: {len(EXPECTED)} gates tested, {len(failures)} problems")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
