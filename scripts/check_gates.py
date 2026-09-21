"""Prove the gates bite.

A gate that has never failed is not known to gate anything. This plants a
deliberately broken vault, asserts each gate rejects it, then removes it.

It runs inside `make check`, so the checks are themselves checked on every run
and in CI, rather than being verified once by hand and trusted forever.
"""
from __future__ import annotations

import json
import pathlib
import re
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
    ("score.py", "two fragments in a row", "staccato writing"),
    ("score.py", "unclear word 'pin it'", "an invented metaphor"),
    ("score.py", "is used before it is explained", "a term used before its definition"),
    ("check_diagrams.py", "'Z', which is not in the graph", "a step naming a missing node"),
    ("check_diagrams.py", "no source renders it", "an SVG no source renders"),
    ("check_diagrams.py", "fits the box only at", "a frame too tall to keep readable labels"),
    ("check_diagrams.py", "not written at", "an SVG whose declared size is not the fitted size"),
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


def glossary_window_bites() -> str:
    """A term may be defined in its first-use sentence or the next one, and no later."""
    import types
    import score
    glossary = {"finish_reason": "the field on a response that says why the model stopped"}
    next_sentence = "The field on a response says why the model stopped."
    filler = "The loop reads it before it trusts the reply."

    def findings(*sentences: str) -> list:
        stub = types.SimpleNamespace(rel="stub", prose=" ".join(sentences), markdown_cells=[])
        return [f for f in score._flow(stub, glossary, {}) if "before it is explained" in f.problem]

    if findings("Read the finish_reason first, before anything else.", next_sentence):
        return "glossary: a definition in the next sentence was rejected"
    if not findings("Read the finish_reason first, before anything else.", filler, next_sentence):
        return "glossary: a definition two sentences later was accepted"
    if not findings("A cut-off reply is refused by finish_reason.", filler, filler):
        return "glossary: a term with no definition was accepted"
    return ""


def speakable_bites() -> str:
    """The ceilings sit exactly at 28 words and 4 sentences, and money is judged by how it sounds."""
    import types
    import score
    banned = {"max_words": 28, "max_sentences": 4}

    def found(text: str, needle: str) -> bool:
        stub = types.SimpleNamespace(rel="stub", markdown_cells=[text])
        return any(needle in f.problem for f in score._speakable(stub, banned))

    sentence = lambda n: " ".join(["word"] * (n - 1)) + " end."
    paragraph = lambda n: " ".join(["The run stops."] * n)
    cases = [
        (sentence(29), "the ceiling is 28", True), (sentence(28), "the ceiling is 28", False),
        (paragraph(5), "the ceiling is 4", True), (paragraph(4), "the ceiling is 4", False),
        ("It cost $0.0000479 a claim.", "cannot be said aloud", True),
        ("It cost $1,234,567 a night.", "cannot be said aloud", True),
        ("It cost $4.32 a night, or $86.50 a month, or $1,250 a year.", "cannot be said aloud", False),
    ]
    for text, needle, expected in cases:
        if found(text, needle) != expected:
            return f"speakable: {text[:40]!r} {'was accepted' if expected else 'was rejected'}"
    print("  speakable  bit as expected (a 29-word sentence, a 5-sentence paragraph, $0.0000479)")
    return ""


def ceiling_drift_bites() -> str:
    """Edit a ceiling out of step with house-rules.md, confirm check-prose notices, put it back."""
    if not (pathlib.Path.home() / ".claude/skills/lwp-shared/scripts/house_rules.py").exists():
        print("  ceilings   not compared with the house rules, none on this machine")
        return ""
    banned = CONFIG / "banned.yml"
    original = banned.read_text()
    banned.write_text(original.replace("max_words: 28", "max_words: 40"))
    try:
        rc, output = run_gate("check_prose.py")
    finally:
        banned.write_text(original)
    if rc == 0 or "max_words is out of date" not in output:
        return "ceilings: check-prose did NOT notice max_words edited out of step with the house rules"
    print("  ceilings   bit as expected (max_words edited out of step with house-rules.md)")
    if run_gate("check_prose.py")[0] != 0:
        return "ceilings: check-prose still failing after banned.yml was restored"
    return ""


def frame_size_bites() -> str:
    """Put one real frame back at its natural size, confirm check-diagrams notices, restore it."""
    frame = ROOT / "01-stateful-agent-runtime" / "images" / "agent-loop-step-1.svg"
    original = frame.read_text()
    natural = re.search(r'viewBox="[-\d.]+ [-\d.]+ ([\d.]+) ([\d.]+)"', original)
    fitted = re.search(r'<svg[^>]* width="(\d+)" height="(\d+)"', original)
    frame.write_text(original.replace(f'width="{fitted[1]}" height="{fitted[2]}"',
                                      f'width="{round(float(natural[1]))}" height="{round(float(natural[2]))}"', 1))
    try:
        rc, output = run_gate("check_diagrams.py")
    finally:
        frame.write_text(original)
    if rc == 0 or "not written at" not in output:
        return "frame size: check-diagrams did NOT notice a frame written at its natural size"
    print("  frame size bit as expected (a real frame put back at its natural size)")
    if run_gate("check_diagrams.py")[0] != 0:
        return "frame size: check-diagrams still failing after the frame was restored"
    return ""


def css_box_bites() -> str:
    """Edit the step-frame cap in custom.css out of step with theme.json, confirm check-theme notices."""
    css = ROOT / ".jupyter" / "custom" / "custom.css"
    original = css.read_text()
    css.write_text(original.replace("max-width: min(900px", "max-width: min(800px", 1))
    try:
        rc, output = run_gate("check_theme.py")
    finally:
        css.write_text(original)
    if rc == 0 or "frames.maxFrameWidth" not in output:
        return "css box: check-theme did NOT notice custom.css out of step with theme.json"
    print("  css box    bit as expected (custom.css cap edited out of step with theme.json)")
    if run_gate("check_theme.py")[0] != 0:
        return "css box: check-theme still failing after custom.css was restored"
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

    # These plant at the root, in docs/, in config/ and on a real frame, so they run before the broken
    # vault exists. Their restore check cannot pass while it does.
    failures = [p for p in (root_inventory_bites(), path_truth_bites(), ceiling_drift_bites(),
                                    frame_size_bites(), css_box_bites()) if p]

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
        for problem in (theme_gate_bites(), glossary_window_bites(), speakable_bites()):
            if problem:
                failures.append(problem)
    finally:
        # Restore even when a check above raises, or the planted promise stays in the syllabus.
        backup = PLANT / "syllabus.backup"
        if backup.is_file():
            (CONFIG / "syllabus.yml").write_text(backup.read_text())
        shutil.rmtree(PLANT)

    restored = [n for n, _, _ in EXPECTED if run_gate(n)[0] != 0]
    if restored:
        failures.append(f"after cleanup these still fail: {restored}")

    for line in failures:
        print(f"  {line}")
    tested = len(EXPECTED) + len(RULES) + 8
    print(f"check-gates: {tested} gates tested, {len(failures)} problems")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
