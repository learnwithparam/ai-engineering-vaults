"""Score every notebook and vault. Threshold 95.

Deterministic. Every deduction names the notebook, the cell and the fix, because
a finding you cannot act on is noise. Rules live in docs/CONTRACT.md.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

import yaml

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import nbcommon as nb
from nbcommon import ROOT, CONFIG, BUILD

THRESHOLD = 95.0
WEIGHTS = {
    "structure": 20,
    "language": 20,
    "production": 20,
    "domains": 15,
    "enterprise": 15,
    "recording": 10,
}
MAX_CODE_LINES = 25
MIN_CODE_CELLS = 6
MIN_STEPS, MAX_STEPS = 3, 6
MAX_CAPTION_WORDS = 35
MAX_PROSE_WORDS = 600

# Reading rules, calibrated in decision 008: the user's four examples average
# 14.8 words a sentence with 13.7% under six words; the rejected vault 1, 9.0 and 23%.
MIN_MEAN_SENTENCE = 12
SHORT_SENTENCE, MAX_SHORT_SHARE = 6, 0.15
MIN_OPENING_WORDS = 8
MIN_HEADING_WORDS = 4
TITLE_WORDS, TITLE_CHARS = (6, 12), 70
FIXED_HEADINGS = {"What you will learn", "Enterprise exploration", "Key terms and traps"}
STOPWORDS = {"that", "this", "with", "from", "into", "what", "when", "your", "they", "them",
             "then", "than", "does", "have", "each", "every", "before", "after", "only"}

# Vaults still in the shape of the contract before decisions 007 and 008: one
# picture and label headings. The set only shrinks: a vault leaves it when its
# notebooks are rewritten, and the constant goes when it is empty.
LEGACY_VAULTS = {
    "02-multi-agent-orchestration", "03-token-economics", "04-context-engineering",
    "05-subagent-delegation", "06-headless-automation", "07-prompt-injection-defense",
    "08-deterministic-outputs", "09-programmatic-guardrails", "10-low-entropy-tool-design",
    "11-model-context-protocol", "12-human-in-the-loop-governance",
    "13-cost-and-latency-at-volume",
}


class Finding:
    def __init__(self, notebook: str, dimension: str, cell: str, problem: str, fix: str) -> None:
        self.notebook, self.dimension = notebook, dimension
        self.cell, self.problem, self.fix = cell, problem, fix

    def as_dict(self) -> dict:
        return {"notebook": self.notebook, "dimension": self.dimension,
                "cell": self.cell, "problem": self.problem, "fix": self.fix}

    def __str__(self) -> str:
        return f"  [{self.dimension}] {self.cell}: {self.problem}\n      fix: {self.fix}"


def score_structure(n: nb.Notebook) -> tuple[float, list[Finding]]:
    """Beats present and ordered, metadata complete."""
    out: list[Finding] = []
    found = n.beats_present()
    required = [name for name in nb.BEATS if name not in nb.OPTIONAL_BEATS]

    for name in required:
        if name not in found:
            out.append(Finding(n.rel, "structure", "notebook",
                               f"beat {name!r} is missing",
                               f"tag the markdown cell that opens it 'beat:{name}'"))

    ordered = [found[k] for k in nb.BEATS if k in found]
    if ordered != sorted(ordered):
        out.append(Finding(n.rel, "structure", "notebook", "beats are out of order",
                           "reorder cells to match the beat order in docs/CONTRACT.md"))

    for field in ("vault", "submodule", "title", "domain", "framework", "analogy"):
        if not n.meta.get(field) and n.meta.get(field) != 0:
            out.append(Finding(n.rel, "structure", "metadata.vault",
                               f"metadata field {field!r} is missing",
                               f"set metadata.vault.{field} in the notebook JSON"))

    penalty = min(len(out) * 4.0, 100.0)
    return max(0.0, 100.0 - penalty), out


def score_visual(n: nb.Notebook) -> list[Finding]:
    """The fix is derived in frames, not handed over. Pass or fail, never averaged."""
    if n.vault_dir in LEGACY_VAULTS:
        return []
    out: list[Finding] = []
    steps = n.steps()
    numbers = [s["number"] for s in steps]
    if not MIN_STEPS <= len(steps) <= MAX_STEPS:
        out.append(Finding(n.rel, "visual", "notebook",
                           f"{len(steps)} step frames, the contract needs {MIN_STEPS} to {MAX_STEPS}",
                           "derive it: the naive build, the break, the why, each piece the fix adds"))
    if numbers != list(range(1, len(steps) + 1)):
        out.append(Finding(n.rel, "visual", "notebook", f"steps are numbered {numbers}",
                           "number the steps 1, 2, 3 in reading order"))
    for s in steps:
        cell = f"markdown cell {s['cell']}"
        if len(s["images"]) != 1:
            out.append(Finding(n.rel, "visual", cell,
                               f"step {s['number']} holds {len(s['images'])} images",
                               "one picture per step, in its own cell"))
        if s["caption_words"] > MAX_CAPTION_WORDS:
            out.append(Finding(n.rel, "visual", cell,
                               f"step {s['number']} caption is {s['caption_words']} words, "
                               f"limit is {MAX_CAPTION_WORDS}",
                               "say what lit up and why, in two sentences"))

    found = n.beats_present()
    if "fix" in found:
        end = found.get("gate", len(n.cells))
        if not any(s["cell"] < found["fix"] for s in steps):
            out.append(Finding(n.rel, "visual", "The fix", "no step frame before the fix",
                               "show the naive build and where it breaks first"))
        if not any(found["fix"] < s["cell"] < end for s in steps):
            out.append(Finding(n.rel, "visual", "The fix", "no step frame inside the fix",
                               "add a frame for each piece the fix adds"))

    prose_words = len(nb.words(nb.strip_code_and_media(n.prose)))
    if prose_words > MAX_PROSE_WORDS:
        out.append(Finding(n.rel, "visual", "prose",
                           f"{prose_words} words of prose, limit is {MAX_PROSE_WORDS}",
                           "cut what the frames already show"))
    return out


def _content_words(text: str) -> set[str]:
    return {w.lower().rstrip("s") for w in nb.words(text)
            if len(w) >= 4 and w.lower() not in STOPWORDS}


def _bullets_after(text: str, heading: str) -> list[str]:
    """The list items directly under a heading, up to the next heading."""
    body = text.split(heading, 1)[1] if heading in text else ""
    body = re.split(r"^#{1,6}\s", body, maxsplit=1, flags=re.MULTILINE)[0]
    return [nb.LIST_ITEM.sub("", l).strip() for l in body.splitlines() if nb.LIST_ITEM.match(l)]


def score_reading(n: nb.Notebook, glossary: dict, banned: dict) -> list[Finding]:
    """Reads like a book a junior can learn from. Pass or fail, never averaged."""
    if n.vault_dir in LEGACY_VAULTS:
        return []
    out: list[Finding] = []
    add = lambda cell, problem, fix: out.append(Finding(n.rel, "reading", cell, problem, fix))
    first = n.markdown_cells[0] if n.markdown_cells else ""
    teaches = [t for t in n.meta.get("teaches", []) if t]

    title = next((t for _, level, t in n.headings() if level == 1), "")
    if not 2 <= len(teaches) <= 4:
        add("metadata.vault.teaches", f"{len(teaches)} teaches terms, the contract needs 2 to 4",
            "list the concepts a reader leaves with, the headline one first")
    elif teaches[0].lower() not in title.lower():
        add("title", f"title {title!r} does not name {teaches[0]!r}",
            "open the title with the concept, then say what it stops or makes possible")
    count = len(title.split())
    if not TITLE_WORDS[0] <= count <= TITLE_WORDS[1] or len(title) > TITLE_CHARS:
        add("title", f"title {title!r} is {count} words and {len(title)} characters",
            f"{TITLE_WORDS[0]} to {TITLE_WORDS[1]} words, at most {TITLE_CHARS} characters")
    for word in banned.get("vague_titles", []):
        if re.search(rf"\b{re.escape(word)}\b", title, re.IGNORECASE):
            add("title", f"title uses the vague word {word!r}",
                "say what the reader learns, not where the notebook sits in the course")
    if title and title != n.meta.get("title"):
        add("metadata.vault.title", "the title heading and metadata.vault.title differ",
            "make them the same string")

    learn = _bullets_after(first, "### What you will learn")
    if not 2 <= len(learn) <= 4:
        add("opening", f"no 'What you will learn' list of 2 to 4 bullets in the opening cell",
            "tell the reader what they will be able to do by the end")
    missing = [t for t in teaches if t.lower() not in " ".join(learn).lower()]
    if learn and missing:
        add("opening", f"the learn list never mentions {missing}", "name each teaches term in it")
    return _reading_headings(n, banned, _content_words(first + " " + " ".join(teaches)), out) \
        + _reading_flow(n, glossary, banned)


def _reading_headings(n: nb.Notebook, banned: dict, scenario: set[str],
                      out: list[Finding]) -> list[Finding]:
    """Every heading makes a claim with a subject, and every section opens with a sentence."""
    vague = {v.lower() for v in banned.get("vague_headings", [])}
    for index, level, text in n.headings():
        if level == 1 or text in FIXED_HEADINGS:
            continue
        step = nb.STEP.match(f"{'#' * level} {text}")
        subject = step.group(2) if step else text
        cell = f"markdown cell {index}"
        if subject.lower().strip(" .") in vague or len(subject.split()) < MIN_HEADING_WORDS:
            what = "step title" if step else "heading"
            out.append(Finding(n.rel, "reading", cell,
                               f"{what} {subject!r} does not say what it teaches",
                               f"write a claim of at least {MIN_HEADING_WORDS} words with a subject, "
                               f"like 'Check a running total before any money moves'"))
        elif step and not _content_words(subject) & scenario:
            out.append(Finding(n.rel, "reading", cell,
                               f"step title {subject!r} names nothing from the scenario",
                               "use the scenario's own nouns, the refund, the booking, the plan"))

    for name, index in n.beats_present().items():
        body = nb.HEADING.sub("", n.source_of(index), count=1)
        sents = nb.flow_sentences(body)
        if not sents or len(nb.words(sents[0])) < MIN_OPENING_WORDS:
            opening = sents[0] if sents else ""
            out.append(Finding(n.rel, "reading", f"markdown cell {index}",
                               f"section {name!r} opens with a fragment: {opening[:50]!r}",
                               f"open with a full sentence of at least {MIN_OPENING_WORDS} words "
                               f"saying what this section shows"))
    return out


def _reading_flow(n: nb.Notebook, glossary: dict, banned: dict) -> list[Finding]:
    """Sentences long enough to carry a thought, plain words, terms explained where used."""
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
        if len(short) / len(lens) > MAX_SHORT_SHARE:
            add("prose", f"{len(short) / len(lens):.0%} of sentences are under {SHORT_SENTENCE} words, "
                f"limit is {MAX_SHORT_SHARE:.0%}", f"rewrite fragments such as {short[0]!r}")
    for is_item, parts in blocks:
        pairs = [(a, b) for a, b in zip(parts, parts[1:])
                 if max(len(nb.words(a)), len(nb.words(b))) < SHORT_SENTENCE]
        if pairs and not is_item:
            add("prose", f"two fragments in a row: {pairs[0][0]!r} {pairs[0][1]!r}",
                "say it as one sentence with a subject and a verb")

    lower = " ".join(sents).lower()
    for phrase in banned.get("teaching_words", []):
        if re.search(rf"\b{re.escape(phrase)}\b", lower):
            add("prose", f"unclear word {phrase!r}", "use the plain word a reader already knows")

    for term, definition in glossary.items():
        pattern = re.compile(rf"\b{re.escape(term.lower())}\b")
        first_use = next((s for s in sents if pattern.search(s.lower())), None)
        anchors = [w for w in nb.words(definition.lower()) if len(w) > 4][:3]
        if first_use and anchors and not any(a in first_use.lower() for a in anchors):
            add("prose", f"{term!r} is used before it is explained: {first_use[:60]!r}",
                f"define it in that sentence: {definition}")

    recap = _bullets_after(n.prose, "### Key terms and traps")
    if not 3 <= len(recap) <= 5 or not all(b.startswith("**") for b in recap):
        add("recap", "no 'Key terms and traps' recap of 3 to 5 bullets, each opening with a bold term",
            "close with the terms and the traps a reader should remember")
    return out


def score_language(n: nb.Notebook, glossary: dict, banned: dict) -> tuple[float, list[Finding]]:
    """Plain enough for a junior, clean enough for the house rules."""
    out: list[Finding] = []
    prose = nb.strip_code_and_media(n.prose)

    sents = nb.sentences(prose)
    if sents:
        mean_len = sum(len(nb.words(s)) for s in sents) / len(sents)
        if mean_len > 20:
            longest = max(sents, key=lambda s: len(nb.words(s)))
            out.append(Finding(n.rel, "language", "prose",
                               f"mean sentence length is {mean_len:.1f} words, limit is 20",
                               f"split long sentences, starting with: {longest[:70]!r}"))

    ws = nb.words(prose)
    if ws:
        long_share = sum(nb.syllables(w) > 3 for w in ws) / len(ws)
        if long_share > 0.15:
            out.append(Finding(n.rel, "language", "prose",
                               f"{long_share:.0%} of words are long, limit is 15%",
                               "replace long words with plain ones"))

    for cell_index, text in enumerate(n.markdown_cells):
        if "—" in text or "–" in text:
            out.append(Finding(n.rel, "language", f"markdown cell {cell_index}",
                               "contains an em dash or en dash",
                               "restructure the sentence, do not swap in a hyphen"))
        for word in banned.get("words", []):
            if re.search(rf"\b{re.escape(word)}\b", text, re.IGNORECASE):
                out.append(Finding(n.rel, "language", f"markdown cell {cell_index}",
                                   f"banned word {word!r}",
                                   "rewrite without it, per the house rules"))
    return _language_tail(n, glossary, out)


def _language_tail(n: nb.Notebook, glossary: dict, out: list[Finding]) -> tuple[float, list[Finding]]:
    """Headings, the analogy, and glossary terms used without a definition."""
    for cell_index, text in enumerate(n.markdown_cells):
        for heading in re.findall(r"^#{1,6}\s+(.+)$", text, re.MULTILINE):
            body = re.sub(r"[`*_]", "", heading).strip()
            words_after_first = body.split()[1:]
            shouty = [w for w in words_after_first
                      if w[:1].isupper() and w.lower() in glossary]
            if shouty:
                out.append(Finding(n.rel, "language", f"markdown cell {cell_index}",
                                   f"heading is not sentence case: {body[:50]!r}",
                                   "lower case everything but the first word and proper nouns"))
                break

    analogy = (n.meta.get("analogy") or "").strip()
    # Prose is hard wrapped, so an analogy can span a line break and still be
    # present. Compare on collapsed whitespace or the check fires on formatting.
    flat = " ".join(n.prose.lower().split())
    if not analogy:
        out.append(Finding(n.rel, "language", "metadata.vault.analogy",
                           "no plain English analogy declared",
                           "add one, and use it in the prose"))
    elif " ".join(analogy.lower().split()) not in flat:
        out.append(Finding(n.rel, "language", "prose",
                           f"the declared analogy {analogy!r} never appears in the prose",
                           "use the analogy in the lesson or change the metadata"))

    prose_lower = nb.strip_code_and_media(n.prose).lower()
    for term, definition in glossary.items():
        if re.search(rf"\b{re.escape(term)}\b", prose_lower) and definition.split()[0] not in prose_lower:
            pass  # a loose signal only, handled by check_prose across a whole vault

    penalty = min(len(out) * 5.0, 100.0)
    return max(0.0, 100.0 - penalty), out


def score_production(n: nb.Notebook) -> tuple[float, list[Finding]]:
    """Real failures, measured fixes, granular code, no unsafe habits."""
    out: list[Finding] = []
    code = n.code_cells

    if len(code) < MIN_CODE_CELLS:
        out.append(Finding(n.rel, "production", "notebook",
                           f"only {len(code)} code cells, minimum is {MIN_CODE_CELLS}",
                           "split the build into one function per cell"))

    for i, src in enumerate(code):
        lines = [l for l in src.splitlines() if l.strip()]
        if len(lines) > MAX_CODE_LINES:
            out.append(Finding(n.rel, "production", f"code cell {i}",
                               f"{len(lines)} lines, limit is {MAX_CODE_LINES}",
                               "split it, one function or one idea per cell"))
        tops = len(re.findall(r"^(?:def|class)\s", src, re.MULTILINE))
        if tops > 1:
            out.append(Finding(n.rel, "production", f"code cell {i}",
                               f"defines {tops} top level functions or classes",
                               "move each into its own cell with prose between"))
        if re.search(r"^\s*except\s*:", src, re.MULTILINE):
            out.append(Finding(n.rel, "production", f"code cell {i}", "bare except",
                               "catch the specific exception you expect"))
        if re.search(r"requests\.(get|post|put|delete)\((?![^)]*timeout)", src):
            out.append(Finding(n.rel, "production", f"code cell {i}",
                               "outbound call with no timeout",
                               "pass timeout= to every outbound call"))
    return _production_tail(n, out)


def _cells_between(n: nb.Notebook, start_beat: str, end_beat: str) -> list[int]:
    """Indexes of code cells sitting under one beat."""
    found = n.beats_present()
    if start_beat not in found:
        return []
    start = found[start_beat]
    later = [i for name, i in found.items() if i > start]
    end = min(later) if later else len(n.cells)
    return [i for i in range(start, end) if n.cells[i].get("cell_type") == "code"]


def _production_tail(n: nb.Notebook, out: list[Finding]) -> tuple[float, list[Finding]]:
    """The failure must really fail, the fix must really measure."""
    src_of = lambda i: "".join(n.cells[i].get("source", []))

    failure_cells = _cells_between(n, "failure", "diagnosis")
    if not failure_cells:
        out.append(Finding(n.rel, "production", "The failure",
                           "no code cell under the failure beat",
                           "add a cell that runs and visibly breaks"))
    elif not any(re.search(r"\b(raise|assert|traceback|Error|except)\b", src_of(i))
                 for i in failure_cells):
        out.append(Finding(n.rel, "production", "The failure",
                           "the failure cell never raises or asserts",
                           "make the break real, not described in a comment"))

    fix_cells = _cells_between(n, "fix", "gate")
    if not fix_cells:
        out.append(Finding(n.rel, "production", "The fix",
                           "no code cell under the fix beat",
                           "add a cell that runs and prints the improvement"))
    elif not any("print" in src_of(i) for i in fix_cells):
        out.append(Finding(n.rel, "production", "The fix",
                           "the fix prints no before and after number",
                           "print the measurement that proves the fix worked"))

    order = n.cell_order()
    for i in range(len(order) - 1):
        if order[i] == "code" and order[i + 1] == "code":
            out.append(Finding(n.rel, "production", f"code cell after index {i}",
                               "two code cells with no prose between them",
                               "add a markdown cell explaining the next piece"))
            break

    penalty = min(len(out) * 5.0, 100.0)
    return max(0.0, 100.0 - penalty), out


def score_enterprise(n: nb.Notebook) -> tuple[float, list[Finding]]:
    """Questions a principal engineer would actually ask."""
    out: list[Finding] = []
    section = ""
    for text in n.markdown_cells:
        if "### Enterprise exploration" in text:
            section = text.split("### Enterprise exploration", 1)[1]
            break

    if not section:
        out.append(Finding(n.rel, "enterprise", "The gate",
                           "no Enterprise exploration section",
                           "add '### Enterprise exploration' with open questions"))
        return 0.0, out

    questions = [l for l in section.splitlines() if l.strip().endswith("?")]
    if len(questions) < 3:
        out.append(Finding(n.rel, "enterprise", "Enterprise exploration",
                           f"only {len(questions)} questions, minimum is 3",
                           "add open questions about running this for real"))

    angles = ("scale", "cost", "complian", "audit", "blast radius", "failure",
              "trade off", "trade-off", "latency", "throughput", "regulat")
    if not any(a in section.lower() for a in angles):
        out.append(Finding(n.rel, "enterprise", "Enterprise exploration",
                           "no scale, cost, compliance, failure or trade off angle",
                           "name at least one of those explicitly"))

    penalty = min(len(out) * 25.0, 100.0)
    return max(0.0, 100.0 - penalty), out


def estimate_minutes(n: nb.Notebook, config: dict) -> float:
    """Speaking time. An estimate, calibrated once, never a stopwatch."""
    prose_words = len(nb.words(nb.strip_code_and_media(n.prose)))
    code_cells = n.code_cells
    code_lines = sum(len([l for l in c.splitlines() if l.strip()]) for c in code_cells)
    outputs = sum(1 for c in n.cells if c.get("outputs"))
    seconds = (prose_words / config["words_per_minute"] * 60
               + len(code_cells) * config["seconds_per_code_cell"]
               + code_lines * config["seconds_per_code_line"]
               + outputs * config["seconds_per_output_block"]
               + len(n.steps()) * config["seconds_per_step_frame"])
    return seconds / 60.0


def score_domains(notebooks: list[nb.Notebook], register: dict) -> tuple[float, list[Finding]]:
    """A repo wide property: spread, and the mix of pull and credibility."""
    out: list[Finding] = []
    high, ent = set(register["high_pull"]), set(register["enterprise_credible"])
    known = high | ent

    used: dict[str, int] = {}
    by_vault: dict[str, set[str]] = {}
    for n in notebooks:
        domain = n.meta.get("domain", "")
        if domain not in known:
            out.append(Finding(n.rel, "domains", "metadata.vault.domain",
                               f"domain {domain!r} is not in config/domains.yml",
                               f"use one of the {len(known)} registered domains"))
            continue
        used[domain] = used.get(domain, 0) + 1
        by_vault.setdefault(n.vault_dir, set()).add(domain)

    # Spread is only meaningful against how much content exists. One vault
    # cannot show twenty domains, so the floor rises as vaults land and tops
    # out at twenty once the course is complete.
    expected = min(20, 3 * max(len(by_vault), 1))
    if len(used) < expected:
        out.append(Finding("repo", "domains", "config/domains.yml",
                           f"only {len(used)} distinct domains across {len(by_vault)} vaults, "
                           f"expected at least {expected}",
                           "give each sub-module its own scenario"))
    for domain, count in sorted(used.items()):
        if count > 3:
            out.append(Finding("repo", "domains", domain,
                               f"used {count} times, limit is 3",
                               "swap some uses for an unused domain"))

    for vault, domains in sorted(by_vault.items()):
        if len(domains) < 3:
            out.append(Finding(vault, "domains", "vault",
                               f"only {len(domains)} distinct domains, minimum is 3",
                               "give each sub-module its own scenario"))
        if not domains & high:
            out.append(Finding(vault, "domains", "vault", "no high pull domain",
                               f"use one of: {', '.join(sorted(high)[:4])}"))
        if not domains & ent:
            out.append(Finding(vault, "domains", "vault", "no enterprise credible domain",
                               f"use one of: {', '.join(sorted(ent)[:4])}"))

    penalty = min(len(out) * 10.0, 100.0)
    return max(0.0, 100.0 - penalty), out


def load_banned() -> dict:
    return yaml.safe_load((CONFIG / "banned.yml").read_text())


def main() -> int:
    notebooks = nb.all_notebooks()
    if not notebooks:
        print("No notebooks yet. Nothing to score.")
        return 0

    glossary = yaml.safe_load((CONFIG / "glossary.yml").read_text())
    register = yaml.safe_load((CONFIG / "domains.yml").read_text())
    banned = load_banned()
    config = json.loads((CONFIG / "recording.json").read_text())

    domain_score, domain_findings = score_domains(notebooks, register)

    per_notebook: dict[str, dict] = {}
    per_vault: dict[str, list[float]] = {}
    minutes: dict[str, float] = {}
    all_findings = list(domain_findings)

    for n in notebooks:
        parts = {}
        for name, fn in (("structure", lambda: score_structure(n)),
                         ("language", lambda: score_language(n, glossary, banned)),
                         ("production", lambda: score_production(n)),
                         ("enterprise", lambda: score_enterprise(n))):
            value, findings = fn()
            parts[name] = value
            all_findings.extend(findings)
        all_findings.extend(score_visual(n))
        all_findings.extend(score_reading(n, glossary, banned))
        parts["domains"] = domain_score
        minutes[n.vault_dir] = minutes.get(n.vault_dir, 0.0) + estimate_minutes(n, config)
        per_notebook[n.rel] = parts
        per_vault.setdefault(n.vault_dir, [])

    return _finish(notebooks, per_notebook, per_vault, minutes, config, all_findings)


def _recording_score(vault: str, used: float, config: dict,
                     findings: list[Finding]) -> float:
    """A band, not a stopwatch.

    The estimate models speaking time from prose, code and outputs. It is
    accurate enough to catch a vault that is running long and nowhere near
    accurate enough to defend a tenth of a minute, so only leaving the band
    fails. Inside it, the target is printed and nothing is deducted.
    """
    low, high = config["hard_min_minutes"], config["hard_max_minutes"]
    if low <= used <= high:
        return 100.0
    if used > high:
        findings.append(Finding(vault, "recording", "vault",
                                f"estimated {used:.1f} minutes, the ceiling is {high:.0f}",
                                "cut prose or move a sub-module out, this vault runs long"))
        return max(0.0, 100.0 - (used - high) / high * 300.0)
    findings.append(Finding(vault, "recording", "vault",
                            f"estimated {used:.1f} minutes, the floor is {low:.0f}",
                            "this vault is too thin for a session, add depth or merge it"))
    return max(0.0, 100.0 - (low - used) / low * 300.0)


def _finish(notebooks, per_notebook, per_vault, minutes, config, findings) -> int:
    budget = config["vault_budget_minutes"]
    rec = {v: _recording_score(v, m, config, findings) for v, m in minutes.items()}

    totals = {}
    for n in notebooks:
        parts = dict(per_notebook[n.rel])
        parts["recording"] = rec[n.vault_dir]
        total = sum(parts[k] * w for k, w in WEIGHTS.items()) / sum(WEIGHTS.values())
        totals[n.rel] = total
        per_notebook[n.rel] = {"parts": parts, "total": round(total, 1)}
        per_vault[n.vault_dir].append(total)

    vault_totals = {v: sum(s) / len(s) for v, s in per_vault.items() if s}
    failing = ({k: v for k, v in totals.items() if v < THRESHOLD}
               | {k: v for k, v in vault_totals.items() if v < THRESHOLD})

    # Domain spread, the recording budget, the visual derivation and the reading
    # rules are contract requirements, not opinions. A weighted average must not
    # be able to outvote them: it carried writing the user rejected to 100.
    hard = [f for f in findings if f.dimension in ("domains", "recording", "visual", "reading")]
    for finding in hard:
        failing.setdefault(f"{finding.notebook} ({finding.dimension})", 0.0)

    report = {
        "threshold": THRESHOLD,
        "notebooks": per_notebook,
        "vaults": {v: round(s, 1) for v, s in vault_totals.items()},
        "vault_minutes": {v: round(m, 1) for v, m in minutes.items()},
        "findings": [f.as_dict() for f in findings],
        "passing": not failing,
    }
    out = BUILD / "scores.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")

    return _print_report(vault_totals, totals, minutes, config, findings, failing)


def _print_report(vault_totals, totals, minutes, config, findings, failing) -> int:
    target = config["vault_budget_minutes"]
    low, high = config["hard_min_minutes"], config["hard_max_minutes"]
    print(f"{'vault':36} {'score':>6} {'minutes':>8}")
    print("-" * 54)
    for vault in sorted(vault_totals):
        used = minutes[vault]
        # Off the target is worth seeing. Only off the band is worth failing.
        flag = "" if low <= used <= high else "  OUT OF BAND"
        if not flag and abs(used - target) > 5:
            flag = "  long" if used > target else "  short"
        print(f"{vault:36} {vault_totals[vault]:6.1f} {used:7.1f}m{flag}")

    print()
    print(f"{'notebook':56} {'score':>6}")
    print("-" * 64)
    for name in sorted(totals):
        mark = " " if totals[name] >= THRESHOLD else "!"
        print(f"{mark}{name:55} {totals[name]:6.1f}")

    if findings:
        print(f"\n{len(findings)} findings:\n")
        by_nb: dict[str, list[Finding]] = {}
        for f in findings:
            by_nb.setdefault(f.notebook, []).append(f)
        for name in sorted(by_nb):
            print(name)
            for f in by_nb[name][:12]:
                print(f)
            if len(by_nb[name]) > 12:
                print(f"  ... {len(by_nb[name]) - 12} more")
            print()

    print(f"wrote build/scores.json")
    if failing:
        print(f"\nFAIL: {len(failing)} below the threshold of {THRESHOLD:.0f}")
        return 1
    print(f"\nPASS: everything at or above {THRESHOLD:.0f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
