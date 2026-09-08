"""Build a notebook from beats, so sixty of them cannot drift apart.

Authoring goes through this rather than through hand written JSON. The beat
order, the metadata shape and the cell rules come from CONTRACT.md, and this is
the one place that knows how to satisfy them.
"""
from __future__ import annotations

import json
import pathlib

import nbformat

BEAT_HEADINGS = {
    "mechanics": "## Mechanics",
    "picture": "## The picture",
    "cost": "## The cost",
    "failure": "## The failure",
    "diagnosis": "## The diagnosis",
    "fix": "## The fix",
    "build": "## The build",
    "gate": "## The gate",
}


class SubModule:
    """One notebook, assembled beat by beat."""

    def __init__(self, vault: int, submodule: int, title: str, domain: str,
                 framework: str, analogy: str) -> None:
        self.meta = {"vault": vault, "submodule": submodule, "title": title,
                     "domain": domain, "framework": framework, "analogy": analogy}
        self.cells: list = []

    def md(self, text: str) -> "SubModule":
        self.cells.append(nbformat.v4.new_markdown_cell(text.strip()))
        return self

    def code(self, source: str) -> "SubModule":
        self.cells.append(nbformat.v4.new_code_cell(source.strip()))
        return self

    def beat(self, name: str, body: str = "") -> "SubModule":
        """Open a beat. The heading must match the contract exactly."""
        if name not in BEAT_HEADINGS:
            raise ValueError(f"unknown beat {name!r}, expected one of {sorted(BEAT_HEADINGS)}")
        text = BEAT_HEADINGS[name]
        if body:
            text += "\n\n" + body.strip()
        return self.md(text)

    def validate(self) -> list[str]:
        """Catch contract breaches here, before the scorer has to."""
        problems = []
        kinds = [c["cell_type"] for c in self.cells]
        for i in range(len(kinds) - 1):
            if kinds[i] == "code" and kinds[i + 1] == "code":
                problems.append(f"cells {i} and {i+1} are both code with no prose between")
        code_cells = [c for c in self.cells if c["cell_type"] == "code"]
        if len(code_cells) < 6:
            problems.append(f"{len(code_cells)} code cells, the contract needs at least 6")
        for i, cell in enumerate(code_cells):
            lines = [l for l in cell["source"].splitlines() if l.strip()]
            if len(lines) > 25:
                problems.append(f"code cell {i} has {len(lines)} lines, limit is 25")
        return problems

    def write(self, path: pathlib.Path) -> pathlib.Path:
        problems = self.validate()
        if problems:
            raise ValueError(f"{path.name} breaks the contract:\n  " + "\n  ".join(problems))
        doc = nbformat.v4.new_notebook(cells=self.cells)
        doc.metadata["vault"] = self.meta
        doc.metadata["kernelspec"] = {"display_name": "Python 3", "language": "python",
                                      "name": "python3"}
        doc.metadata["language_info"] = {"name": "python", "version": "3.11"}
        path.parent.mkdir(parents=True, exist_ok=True)
        nbformat.write(doc, path)
        return path
