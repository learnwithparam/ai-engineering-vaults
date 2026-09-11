"""Build a notebook from beats, so sixty of them cannot drift apart.

Authoring goes through this rather than through hand written JSON. The beat
order, the metadata shape and the cell rules come from docs/CONTRACT.md, and this is
the one place that knows how to satisfy them.
"""
from __future__ import annotations

import json
import pathlib

import nbformat

BEATS = ["mechanics", "cost", "failure", "diagnosis", "fix", "gate"]


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

    def code(self, source: str, raises: bool = False) -> "SubModule":
        """Add a code cell.

        `raises=True` tags the cell so the notebook keeps running after it
        throws. The failure beat needs a real traceback in the output, not a
        described one, and it still has to leave the rest of the lesson
        runnable.
        """
        cell = nbformat.v4.new_code_cell(source.strip())
        if raises:
            cell.metadata["tags"] = ["raises-exception"]
        self.cells.append(cell)
        return self

    def opening(self, title: str, body: str, learn: list[str]) -> "SubModule":
        """The hook cell: the title, the scenario, and what the reader will learn."""
        bullets = "\n".join(f"- {item}" for item in learn)
        return self.md(f"# {title}\n\n{body.strip()}\n\n### What you will learn\n\n{bullets}")

    def beat(self, name: str, heading: str, body: str) -> "SubModule":
        """Open a beat. The tag is for the gates, the heading is a claim for the reader."""
        if name not in BEATS:
            raise ValueError(f"unknown beat {name!r}, expected one of {BEATS}")
        self.md(f"## {heading}\n\n{body.strip()}")
        self.cells[-1].metadata["tags"] = [f"beat:{name}"]
        return self

    def recap(self, items: dict[str, str]) -> "SubModule":
        """Key terms and traps, each opening with its bold term."""
        bullets = "\n".join(f"- **{term}**: {say}" for term, say in items.items())
        return self.md(f"### Key terms and traps\n\n{bullets}")

    def step(self, number: int, title: str, image: str, caption: str) -> "SubModule":
        """One frame of the derivation, in its own cell: heading, picture, caption."""
        return self.md(f"### Step {number}: {title}\n\n![{title}]({image})\n\n{caption.strip()}")

    def validate(self) -> list[str]:
        """Catch contract breaches here, before the scorer has to."""
        problems = []
        steps = [c for c in self.cells
                 if c["cell_type"] == "markdown" and c["source"].startswith("### Step ")]
        if not 3 <= len(steps) <= 6:
            problems.append(f"{len(steps)} step frames, the contract needs 3 to 6")
        tags = [t for c in self.cells for t in c.get("metadata", {}).get("tags", [])]
        for name in BEATS:
            if name != "cost" and f"beat:{name}" not in tags:
                problems.append(f"beat {name!r} is missing, open it with .beat()")
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
