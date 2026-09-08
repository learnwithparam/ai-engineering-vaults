"""Score every notebook and vault. Threshold 95.

Deterministic. Every deduction names the notebook, the cell and the fix, because
a finding you cannot act on is noise. Rules live in CONTRACT.md.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

import yaml

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import nbcommon as nb
from nbcommon import ROOT

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
    required = [name for name, _ in nb.BEATS if name not in nb.OPTIONAL_BEATS]

    for name in required:
        if name not in found:
            heading = dict(nb.BEATS)[name]
            out.append(Finding(n.rel, "structure", "notebook",
                               f"beat {name!r} is missing",
                               f"add a markdown cell with the heading {heading!r}"))

    ordered = [found[k] for k, _ in nb.BEATS if k in found]
    if ordered != sorted(ordered):
        out.append(Finding(n.rel, "structure", "notebook", "beats are out of order",
                           "reorder cells to match the beat order in CONTRACT.md"))

    for field in ("vault", "submodule", "title", "domain", "framework", "analogy"):
        if not n.meta.get(field) and n.meta.get(field) != 0:
            out.append(Finding(n.rel, "structure", "metadata.vault",
                               f"metadata field {field!r} is missing",
                               f"set metadata.vault.{field} in the notebook JSON"))

    penalty = min(len(out) * 4.0, 100.0)
    return max(0.0, 100.0 - penalty), out


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
    if not analogy:
        out.append(Finding(n.rel, "language", "metadata.vault.analogy",
                           "no plain English analogy declared",
                           "add one, and use it in the prose"))
    elif analogy.lower() not in n.prose.lower():
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

    fix_cells = _cells_between(n, "fix", "build")
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
               + outputs * config["seconds_per_output_block"])
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
                               f"domain {domain!r} is not in domains.yml",
                               f"use one of the {len(known)} registered domains"))
            continue
        used[domain] = used.get(domain, 0) + 1
        by_vault.setdefault(n.vault_dir, set()).add(domain)

    if len(used) < 20:
        out.append(Finding("repo", "domains", "domains.yml",
                           f"only {len(used)} distinct domains used, minimum is 20",
                           "vary the scenarios across sub-modules"))
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
    return yaml.safe_load((ROOT / "banned.yml").read_text())


def main() -> int:
    notebooks = nb.all_notebooks()
    if not notebooks:
        print("No notebooks yet. Nothing to score.")
        return 0

    glossary = yaml.safe_load((ROOT / "glossary.yml").read_text())
    register = yaml.safe_load((ROOT / "domains.yml").read_text())
    banned = load_banned()
    config = json.loads((ROOT / "config" / "recording.json").read_text())

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
        parts["domains"] = domain_score
        minutes[n.vault_dir] = minutes.get(n.vault_dir, 0.0) + estimate_minutes(n, config)
        per_notebook[n.rel] = parts
        per_vault.setdefault(n.vault_dir, [])

    return _finish(notebooks, per_notebook, per_vault, minutes, config, all_findings)


def _recording_score(vault: str, used: float, budget: float,
                     findings: list[Finding]) -> float:
    """Over budget is a hard fail, because concise was the requirement."""
    if used <= budget:
        return 100.0
    findings.append(Finding(vault, "recording", "vault",
                            f"estimated {used:.1f} minutes, budget is {budget:.0f}",
                            "cut prose or move a sub-module out, this vault runs long"))
    over = (used - budget) / budget
    return max(0.0, 100.0 - over * 300.0)


def _finish(notebooks, per_notebook, per_vault, minutes, config, findings) -> int:
    budget = config["vault_budget_minutes"]
    rec = {v: _recording_score(v, m, budget, findings) for v, m in minutes.items()}

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

    # Domain spread and the recording budget are contract requirements, not
    # opinions. A weighted average must not be able to outvote them, or a
    # strong notebook could carry a vault that breaks a rule outright.
    hard = [f for f in findings if f.dimension in ("domains", "recording")]
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
    out = ROOT / "build" / "scores.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")

    return _print_report(vault_totals, totals, minutes, budget, findings, failing)


def _print_report(vault_totals, totals, minutes, budget, findings, failing) -> int:
    print(f"{'vault':36} {'score':>6} {'minutes':>8}")
    print("-" * 54)
    for vault in sorted(vault_totals):
        used = minutes[vault]
        flag = "" if used <= budget else "  OVER"
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
