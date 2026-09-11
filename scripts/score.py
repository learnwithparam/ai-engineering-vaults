"""Check every course notebook against docs/CONTRACT.md. Pass or fail.

Deterministic, and every finding names the notebook, the cell and the fix. There
is no weighted score: an average once carried writing a reader rejected to 100.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

import yaml

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import nbcommon as nb
from nbcommon import CONFIG, BUILD

MAX_CODE_LINES = 25
MIN_STEPS, MIN_FRAMES = 4, 3
MIN_TITLE_WORDS, MIN_HEADING_WORDS, MIN_OPENING_WORDS = 4, 4, 8
# Measured in decision 008: the writing the user asked for averages 14.6 words a
# sentence with 14% under six words; the writing they rejected, about 9 and 22%.
MIN_MEAN_SENTENCE, MAX_MEAN_SENTENCE = 12, 22
SHORT_SENTENCE, MAX_SHORT_SHARE = 6, 0.15
MAX_LONG_WORD_SHARE = 0.15
CLOSING = "Concepts"
OVERVIEW = "What you will build"


class Finding:
    def __init__(self, notebook: str, rule: str, cell: str, problem: str, fix: str) -> None:
        self.notebook, self.rule = notebook, rule
        self.cell, self.problem, self.fix = cell, problem, fix

    def as_dict(self) -> dict:
        return {"notebook": self.notebook, "rule": self.rule,
                "cell": self.cell, "problem": self.problem, "fix": self.fix}

    def __str__(self) -> str:
        return f"  [{self.rule}] {self.cell}: {self.problem}\n      fix: {self.fix}"


def check_shape(n: nb.Notebook, register: dict, courses: dict) -> list[Finding]:
    """Title, overview, numbered steps, frames in order, a closing concepts table."""
    out: list[Finding] = []
    add = lambda cell, problem, fix: out.append(Finding(n.rel, "shape", cell, problem, fix))

    title = n.title()
    expected = (courses.get(n.meta.get("vault")) or {}).get("title")
    if not title:
        add("notebook", "no title heading", "open with '# <the course title>'")
    elif title != n.meta.get("title"):
        add("metadata.vault.title", "the title heading and metadata.vault.title differ",
            "make them the same string")
    if not expected:
        add("title", f"vault {n.meta.get('vault')} has no title in config/courses.yml",
            "add the course to the catalogue before writing it")
    elif title != expected:
        add("title", f"title {title!r} is not the catalogue title {expected!r}",
            "use the title from config/courses.yml, exactly")
    for field in ("vault", "title", "domain", "framework"):
        if n.meta.get(field) in (None, ""):
            add("metadata.vault", f"metadata field {field!r} is missing",
                f"set metadata.vault.{field} in the notebook JSON")
    known = set(register["high_pull"]) | set(register["enterprise_credible"])
    if n.meta.get("domain") not in known:
        add("metadata.vault.domain", f"domain {n.meta.get('domain')!r} is not in config/domains.yml",
            "use one of the registered domains")

    steps = n.steps()
    numbers = [s["number"] for s in steps]
    if len(steps) < MIN_STEPS:
        add("notebook", f"{len(steps)} steps, a course needs at least {MIN_STEPS}",
            "build it up in '## Step N: <what this step builds>' sections")
    if numbers != list(range(len(steps))):
        add("notebook", f"steps are numbered {numbers}", "number them 0, 1, 2 in reading order")

    first_step = steps[0]["cell"] if steps else len(n.cells)
    sections = [(i, t) for i, level, t in n.headings() if level == 2]
    overview = [(i, t) for i, t in sections if i < first_step]
    if len(overview) != 1:
        add("overview", f"{len(overview)} sections before Step 0, the contract needs one overview",
            f"open with one '## {OVERVIEW}' section")
    else:
        # The opening shows the problem, not the design: detail there confuses a
        # reader who has not built anything yet (user feedback, decision 009).
        start, heading = overview[0]
        body = "\n".join(n.source_of(i) for i in range(start, first_step)
                         if n.cells[i].get("cell_type") == "markdown")
        images = nb.IMAGE.findall(body)
        if heading != OVERVIEW:
            add("overview", f"the overview heading is {heading!r}, the contract says {OVERVIEW!r}",
                "say what the course builds and the problem it solves")
        if len(images) != 1:
            add("overview", f"the overview has {len(images)} diagrams, the contract needs one",
                "show one top-level picture of the problem")
        elif nb.FRAME.search(images[0]):
            add("overview", "the overview shows a step frame of the design",
                "draw the problem at the top level; the design belongs in the steps")
        if re.search(r"`[^`]+`", nb.IMAGE.sub("", body)):
            add("overview", "the overview names code",
                "describe the problem in plain words; fields and functions belong in the steps")
    if not sections or sections[-1][1] != CLOSING or "|" not in n.source_of(sections[-1][0]):
        add("closing", f"no closing '## {CLOSING}' table",
            "end with a table: the concept, where it lives in the code, what it does")

    shown = [(series, frame) for cell, series, frame in n.frames() if cell > first_step]
    if len(set(shown)) < MIN_FRAMES:
        add("frames", f"{len(set(shown))} step frames after Step 0, the contract needs at least "
            f"{MIN_FRAMES}", "grow the overview diagram one frame per step")
    for series in {s for s, _ in shown}:
        order = [frame for s, frame in shown if s == series]
        if order != sorted(order):
            add("frames", f"{series} frames appear in the order {order}",
                "show each frame at the step it builds")
    return out


def check_reading(n: nb.Notebook, glossary: dict, banned: dict) -> list[Finding]:
    """Headings that say what gets built, and steps that open with a real sentence."""
    out: list[Finding] = []
    add = lambda cell, problem, fix: out.append(Finding(n.rel, "reading", cell, problem, fix))

    title = n.title()
    if title and len(title.split()) < MIN_TITLE_WORDS:
        add("title", f"title {title!r} is {len(title.split())} words",
            "say what the course builds, like 'Build a stateful agent runtime that issues refunds safely'")
    for word in banned.get("vague_titles", []):
        if re.search(rf"\b{re.escape(word)}\b", title, re.IGNORECASE):
            add("title", f"title uses the vague word {word!r}",
                "say what the reader builds, not where the notebook sits in the course")

    for index, level, text in n.headings():
        for word in banned.get("vendor_words", []):
            if re.search(rf"\b{re.escape(word)}\b", text, re.IGNORECASE):
                add(f"markdown cell {index}", f"heading {text!r} names the vendor {word!r}",
                    "every course is taught on a generic API, so drop the vendor name")

    vague = {v.lower() for v in banned.get("vague_headings", [])}
    for index, level, text in n.headings():
        if level not in (2, 3) or text == CLOSING:
            continue
        step = nb.STEP.match(f"## {text}") if level == 2 else None
        subject = step.group(2) if step else text
        what = "step title" if step else "heading"
        if subject.lower().strip(" .") in vague or len(subject.split()) < MIN_HEADING_WORDS:
            add(f"markdown cell {index}", f"{what} {subject!r} does not say what it teaches",
                f"say what gets built in at least {MIN_HEADING_WORDS} words, "
                f"like 'Run the tool and send the result back'")
        shouty = [w for w in re.sub(r"[`*]", "", subject).split()[1:]
                  if w[:1].isupper() and w.lower() in glossary]
        if shouty:
            add(f"markdown cell {index}", f"{what} {subject!r} is not sentence case",
                "lower case everything but the first word and proper nouns")

    for s in n.steps():
        body = nb.HEADING.sub("", n.source_of(s["cell"]), count=1)
        sents = nb.flow_sentences(body)
        if not sents or len(nb.words(sents[0])) < MIN_OPENING_WORDS:
            opening = sents[0] if sents else ""
            add(f"markdown cell {s['cell']}", f"step {s['number']} opens with a fragment: {opening[:50]!r}",
                f"open with a full sentence of at least {MIN_OPENING_WORDS} words on what we do and why")
    return out + _flow(n, glossary, banned)


def _flow(n: nb.Notebook, glossary: dict, banned: dict) -> list[Finding]:
    """Sentences that carry a whole thought, plain words, terms explained where used."""
    out: list[Finding] = []
    add = lambda cell, problem, fix: out.append(Finding(n.rel, "reading", cell, problem, fix))
    blocks = nb.prose_blocks(n.prose)
    sents = [s for _, parts in blocks for s in parts]
    lens = [len(nb.words(s)) for s in sents]
    if lens:
        mean = sum(lens) / len(lens)
        short = [s for s, l in zip(sents, lens) if l < SHORT_SENTENCE]
        if mean < MIN_MEAN_SENTENCE:
            add("prose", f"mean sentence length is {mean:.1f} words, the floor is {MIN_MEAN_SENTENCE}",
                "join clipped sentences into ones that carry a whole thought")
        if mean > MAX_MEAN_SENTENCE:
            add("prose", f"mean sentence length is {mean:.1f} words, the ceiling is {MAX_MEAN_SENTENCE}",
                f"split the longest, starting with {max(sents, key=lambda s: len(nb.words(s)))[:60]!r}")
        if len(short) / len(lens) > MAX_SHORT_SHARE:
            add("prose", f"{len(short) / len(lens):.0%} of sentences are under {SHORT_SENTENCE} words, "
                f"limit is {MAX_SHORT_SHARE:.0%}", f"rewrite fragments such as {short[0]!r}")
    for is_item, parts in blocks:
        pairs = [(a, b) for a, b in zip(parts, parts[1:])
                 if max(len(nb.words(a)), len(nb.words(b))) < SHORT_SENTENCE]
        if pairs and not is_item:
            add("prose", f"two fragments in a row: {pairs[0][0]!r} {pairs[0][1]!r}",
                "say it as one sentence with a subject and a verb")

    ws = [w for s in sents for w in nb.words(s)]
    if ws and sum(nb.syllables(w) > 3 for w in ws) / len(ws) > MAX_LONG_WORD_SHARE:
        add("prose", f"more than {MAX_LONG_WORD_SHARE:.0%} of words are long", "use the plain word")

    lower = " ".join(sents).lower()
    for phrase in banned.get("teaching_words", []) + banned.get("words", []):
        if re.search(rf"\b{re.escape(phrase)}\b", lower):
            add("prose", f"unclear word {phrase!r}", "use the plain word a reader already knows")
    if any("—" in t or "–" in t for t in n.markdown_cells):
        add("prose", "an em dash or en dash", "restructure the sentence, do not swap in a hyphen")

    for term, definition in glossary.items():
        pattern = re.compile(rf"\b{re.escape(term.lower())}\b")
        first_use = next((s for s in sents if pattern.search(s.lower())), None)
        anchors = [w for w in nb.words(definition.lower()) if len(w) > 4][:3]
        if first_use and anchors and not any(a in first_use.lower() for a in anchors):
            add("prose", f"{term!r} is used before it is explained: {first_use[:60]!r}",
                f"define it in that sentence: {definition}")
    return out


def check_code(n: nb.Notebook, banned: dict) -> list[Finding]:
    """Short cells, prose between them, and names you can read aloud."""
    out: list[Finding] = []
    add = lambda cell, problem, fix: out.append(Finding(n.rel, "code", cell, problem, fix))
    vague = set(banned.get("vague_function_words", []))
    for i, src in enumerate(n.code_cells):
        lines = [l for l in src.splitlines() if l.strip()]
        if len(lines) > MAX_CODE_LINES:
            add(f"code cell {i}", f"{len(lines)} lines, limit is {MAX_CODE_LINES}",
                "split it at the next idea, with a sentence between")
        if re.search(r"^\s*except\s*:", src, re.MULTILINE):
            add(f"code cell {i}", "bare except", "catch the specific exception you expect")
        if re.search(r"requests\.(get|post|put|delete)\((?![^)]*timeout)", src):
            add(f"code cell {i}", "outbound call with no timeout", "pass timeout= to every call")
        for name in re.findall(r"^def\s+(\w+)", src, re.MULTILINE):
            parts = name.strip("_").split("_")
            if len(parts) < 2 or parts[0] in vague:
                add(f"code cell {i}", f"function name {name!r} does not say what it does",
                    "name it verb then object, like issue_refund or run_agent")

    order = n.cell_order()
    if any(a == b == "code" for a, b in zip(order, order[1:])):
        add("notebook", "two code cells with no prose between them",
            "add a sentence saying what the next cell does")
    return out


def estimate_minutes(n: nb.Notebook, config: dict) -> float:
    """Screencast time. An estimate, calibrated once, never a stopwatch."""
    code = n.code_cells
    seconds = (len(nb.words(nb.strip_code_and_media(n.prose))) / config["words_per_minute"] * 60
               + len(code) * config["seconds_per_code_cell"]
               + sum(len([l for l in c.splitlines() if l.strip()]) for c in code)
               * config["seconds_per_code_line"]
               + sum(1 for c in n.cells if c.get("outputs")) * config["seconds_per_output_block"]
               + len({(s, f) for _, s, f in n.frames()}) * config["seconds_per_step_frame"])
    return seconds / 60.0


def main() -> int:
    # `score.py 05` checks one vault, so an author can work on it alone.
    only = sys.argv[1] if len(sys.argv) > 1 else ""
    notebooks = [n for n in nb.all_notebooks() if n.vault_dir.startswith(only)]
    glossary = yaml.safe_load((CONFIG / "glossary.yml").read_text())
    register = yaml.safe_load((CONFIG / "domains.yml").read_text())
    courses = yaml.safe_load((CONFIG / "courses.yml").read_text())
    banned = yaml.safe_load((CONFIG / "banned.yml").read_text())
    config = json.loads((CONFIG / "recording.json").read_text())

    findings: list[Finding] = []
    minutes: dict[str, float] = {}
    for n in notebooks:
        findings += (check_shape(n, register, courses) + check_reading(n, glossary, banned)
                     + check_code(n, banned))
        minutes[n.vault_dir] = minutes.get(n.vault_dir, 0.0) + estimate_minutes(n, config)

    report = {"notebooks": [n.rel for n in notebooks],
              "vault_minutes": {v: round(m, 1) for v, m in minutes.items()},
              "findings": [f.as_dict() for f in findings], "passing": not findings}
    BUILD.mkdir(parents=True, exist_ok=True)
    (BUILD / "scores.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")

    target = config["vault_budget_minutes"]
    print(f"{'vault':36} {'minutes':>8}   (advice: about {target:.0f})")
    for vault, used in sorted(minutes.items()):
        print(f"{vault:36} {used:7.1f}m")
    by_notebook: dict[str, list[Finding]] = {}
    for f in findings:
        by_notebook.setdefault(f.notebook, []).append(f)
    for name, group in sorted(by_notebook.items()):
        print(f"\n{name}")
        for f in group:
            print(f)
    print("\nwrote build/scores.json")
    if findings:
        print(f"FAIL: {len(findings)} findings in {len(by_notebook)} notebooks")
        return 1
    print(f"PASS: {len(notebooks)} course notebooks, no findings")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
