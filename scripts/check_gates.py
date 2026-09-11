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
from nbcommon import ROOT, CONFIG, BUILD

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
    """A vault of two notebooks that breaks every rule at least once."""
    PLANT.mkdir(parents=True, exist_ok=True)
    (PLANT / "README.md").write_text("# Gate self test\n")

    cells = [
        md("# Broken on purpose for Claude developers\n\nThis notebook exists so the gates can be "
           "proven to bite."),
        md("## Mechanics\n\nWe leverage a robust paradigm here."),
        md("A cache needs 1,024 tokens, which is a provider constant written as prose."),
        code("import os\nkey = 'sk-or-v1-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'"),
        md("The function below does something, but its name never says what."),
        code("def approve():\n    pass"),
        code("from vault.client import get_client\nclient = get_client('99-gate-selftest/01-broken')"),
        md("![missing](images/never-rendered.svg)"),
    ]
    # syllabus.yml gains a vault that has no notebooks, so coverage has a gap.
    syllabus = CONFIG / "syllabus.yml"
    original = syllabus.read_text()
    syllabus.write_text(original + "\n98:\n  a promise nothing keeps: this-phrase-appears-nowhere\n")
    (PLANT / "syllabus.backup").write_text(original)

    meta = {"vault": 99, "title": "Broken", "domain": "not-a-real-domain", "framework": "none"}
    (PLANT / "01-broken.ipynb").write_text(json.dumps(notebook(cells, meta), indent=1))

    # A diagram source with no rendered SVG, so check-diagrams has something to catch.
    (PLANT / "diagrams").mkdir(exist_ok=True)
    (PLANT / "diagrams" / "unrendered.mmd").write_text("graph LR\n  A[in] --> B[out]\n")

    # The writing the user rejected on 2026-09-11, verbatim where it can be.
    bad_reading = [
        md("# Capstone, actions that survive"),
        md("## Mechanics\n\nIn the prompt. The harness runs first in this example here today, "
           "reading `finish_reason`."),
        md("## Step 1: the naive build\n\n![x](images/series-step-1.svg)\n\n"
           "Ask six times and count. Not a better prompt. Now pin it."),
        code("print('before 1, after 0')"),
    ]
    meta = dict(meta, title="Capstone, actions that survive")
    (PLANT / "02-bad-reading.ipynb").write_text(json.dumps(notebook(bad_reading, meta), indent=1))

    # A series naming a node that does not exist, and an SVG nothing renders.
    (PLANT / "diagrams" / "series.mmd").write_text(
        "graph LR\n  A[in] --> B[out]\n%% step 1: A Z\n")
    (PLANT / "images").mkdir(exist_ok=True)
    (PLANT / "images" / "orphan.svg").write_text("<svg xmlns='http://www.w3.org/2000/svg'/>\n")
    (PLANT / "images" / "series-step-1.svg").write_text(
        "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 3000 400'/>\n")


EXPECTED = [
    ("check_structure.py", "structure", "two notebooks in one vault, README gaps"),
    ("check_prose.py", "prose", "banned words, a provider constant, and a planted key"),
    ("check_diagrams.py", "diagrams", "a .mmd with no SVG and a dead image reference"),
    ("check_fixtures.py", "fixtures", "a notebook calling the model with no fixtures"),
    ("score.py", "score", "no overview, bad domain, label headings, a vague function name"),
    ("check_coverage.py", "coverage", "a vault in the syllabus with no notebooks"),
]

# Exit codes alone cannot prove these: the planted vault fails most gates for
# several reasons at once. So each rule must name itself.
RULES = [
    ("check_structure.py", "the contract says one course notebook", "two notebooks in one vault"),
    ("score.py", "function name 'approve' does not say", "a function named approve"),
    ("score.py", "vague word 'capstone'", "a title that names no concept"),
    ("score.py", "heading 'Mechanics' does not say", "a label heading"),
    ("score.py", "step title 'the naive build' does not say", "a step title with no subject"),
    ("score.py", "steps are numbered [1]", "steps that do not start at 0"),
    ("score.py", "the overview heading is 'Mechanics'", "an opening that is not the overview"),
    ("score.py", "the overview has 0 diagrams", "an overview with no problem diagram"),
    ("score.py", "the overview names code", "an overview that explains the design"),
    ("score.py", "has no title in config/courses.yml", "a course missing from the catalogue"),
    ("score.py", "names the vendor 'claude'", "a vendor name in a title"),
    ("score.py", "no closing '## Concepts' table", "no concepts table"),
    ("score.py", "step frames after Step 0", "a course shown in one frame"),
    ("score.py", "opens with a fragment", "a step opening on a fragment"),
    ("score.py", "the floor is 12", "clipped sentences"),
    ("score.py", "sentences are under 6 words", "too many fragments"),
    ("score.py", "two fragments in a row", "staccato writing"),
    ("score.py", "unclear word 'pin it'", "an invented metaphor"),
    ("score.py", "is used before it is explained", "a term used before its definition"),
    ("check_diagrams.py", "'Z', which is not in the graph", "a step naming a missing node"),
    ("check_diagrams.py", "no source renders it", "an SVG no source renders"),
    ("check_diagrams.py", "unreadable on video", "a frame too wide to read"),
]


def root_inventory_bites() -> str:
    """Drop a file at the root, confirm check-structure rejects it, remove it."""
    stray = ROOT / "stray-note.md"
    stray.write_text("# planted by check-gates\n")
    try:
        rc, output = run_gate("check_structure.py")
    finally:
        stray.unlink()
    if rc == 0:
        return "root inventory: did NOT bite on a stray file at the repo root"
    if "stray-note.md" not in output:
        return "root inventory: failed without naming the file it rejected"
    print("  root       bit as expected (a file at the root that is not on the allow-list)")
    if run_gate("check_structure.py")[0] != 0:
        return "root inventory: still failing after the stray file was removed"
    return ""


def path_truth_bites() -> str:
    """Write a doc naming a path that does not exist, confirm check-paths says so."""
    doc = ROOT / "docs" / "gate-selftest.md"
    doc.write_text("# planted\n\nThis names `config/does-not-exist.json`, which is not there.\n")
    try:
        rc, output = run_gate("check_paths.py")
    finally:
        doc.unlink()
    if rc == 0:
        return "path truth: did NOT bite on a doc naming a path that does not exist"
    if "does-not-exist.json" not in output:
        return "path truth: failed without naming the dead path"
    print("  paths      bit as expected (a doc naming a path that does not exist)")
    if run_gate("check_paths.py")[0] != 0:
        return "path truth: still failing after the planted doc was removed"
    return ""


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

    # These two plant at the root and in docs/, so they run before the broken
    # vault exists. Their restore check cannot pass while it does.
    failures = [p for p in (root_inventory_bites(), path_truth_bites()) if p]

    plant_broken()
    outputs = {}
    try:
        for script, label, why in EXPECTED:
            rc, output = run_gate(script)
            if script == "score.py" and (BUILD / "scores.json").is_file():
                output += (BUILD / "scores.json").read_text()
            outputs[script] = output
            if rc == 0:
                failures.append(f"{label}: did NOT bite. Expected it to catch {why}")
            else:
                print(f"  {label:10} bit as expected ({why})")
            if "sk-or-v1-aaaa" in output:
                failures.append(f"{label}: printed the planted key in its own output")
        for script, needle, why in RULES:
            if needle in outputs.get(script, ""):
                print(f"  {'rule':10} bit as expected ({why})")
            else:
                failures.append(f"rule: {script} did NOT name {why}")
        problem = theme_gate_bites()
        if problem:
            failures.append(problem)
        backup = PLANT / "syllabus.backup"
        if backup.is_file():
            (CONFIG / "syllabus.yml").write_text(backup.read_text())
    finally:
        shutil.rmtree(PLANT)

    restored = [n for n, _, _ in EXPECTED if run_gate(n)[0] != 0]
    if restored:
        failures.append(f"after cleanup these still fail: {restored}")

    for line in failures:
        print(f"  {line}")
    tested = len(EXPECTED) + len(RULES) + 3
    print(f"check-gates: {tested} gates tested, {len(failures)} problems")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
