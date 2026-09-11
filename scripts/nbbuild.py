"""Build a course notebook, so the shape in docs/CONTRACT.md is written once.

A scratch authoring script uses this rather than hand written JSON. The script
itself is never committed: the notebook is the deliverable.
"""
from __future__ import annotations

import pathlib

import nbformat


class Course:
    """One vault, one notebook: an overview, numbered steps, a concepts table."""

    def __init__(self, vault: int, title: str, domain: str, framework: str = "none") -> None:
        self.meta = {"vault": vault, "title": title, "domain": domain, "framework": framework}
        self.cells: list = [nbformat.v4.new_markdown_cell(f"# {title}")]
        self.next_step = 0

    def md(self, text: str) -> "Course":
        self.cells.append(nbformat.v4.new_markdown_cell(text.strip()))
        return self

    def code(self, source: str, raises: bool = False) -> "Course":
        """Add a code cell. `raises=True` lets the notebook run on past a cell that throws."""
        cell = nbformat.v4.new_code_cell(source.strip())
        if raises:
            cell.metadata["tags"] = ["raises-exception"]
        self.cells.append(cell)
        return self

    def overview(self, body: str, image: str) -> "Course":
        """What the course builds and the problem it solves, over one problem diagram."""
        return self.md(f"## What you will build\n\n{body.strip()}\n\n![What you will build]({image})")

    def step(self, title: str, body: str, image: str = "") -> "Course":
        """Open the next step. Numbering is automatic, so it can never skip."""
        text = f"## Step {self.next_step}: {title}\n\n{body.strip()}"
        if image:
            text += f"\n\n![{title}]({image})"
        self.next_step += 1
        return self.md(text)

    def concepts(self, rows: list[tuple[str, str, str]]) -> "Course":
        """The closing table: the concept, where it lives in the code, what it does."""
        lines = ["| Concept | Where it lives | What it does |", "|---|---|---|"]
        lines += [f"| **{a}** | {b} | {c} |" for a, b, c in rows]
        return self.md("## Concepts\n\n" + "\n".join(lines))

    def validate(self) -> list[str]:
        """Catch contract breaches here, before the scorer has to."""
        problems = []
        if self.next_step < 4:
            problems.append(f"{self.next_step} steps, the contract needs at least 4")
        kinds = [c["cell_type"] for c in self.cells]
        for i in range(len(kinds) - 1):
            if kinds[i] == kinds[i + 1] == "code":
                problems.append(f"cells {i} and {i + 1} are both code with no prose between")
        for i, cell in enumerate(c for c in self.cells if c["cell_type"] == "code"):
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
