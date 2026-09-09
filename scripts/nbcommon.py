"""Shared notebook reading for every gate.

One parser, so the scorer and the checks can never disagree about what a
notebook contains.
"""
from __future__ import annotations

import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
# Every gate input lives here, so the root stays the learner surface.
CONFIG = ROOT / "config"
DOCS = ROOT / "docs"
BUILD = ROOT / "build"

BEATS = [
    ("mechanics", "## Mechanics"),
    ("picture", "## The picture"),
    ("cost", "## The cost"),
    ("failure", "## The failure"),
    ("diagnosis", "## The diagnosis"),
    ("fix", "## The fix"),
    ("gate", "## The gate"),
]
OPTIONAL_BEATS = {"cost"}


class Notebook:
    def __init__(self, path: pathlib.Path) -> None:
        self.path = path
        self.rel = path.relative_to(ROOT).as_posix()
        self.raw = json.loads(path.read_text())
        self.cells = self.raw.get("cells", [])
        self.meta = self.raw.get("metadata", {}).get("vault", {})

    @property
    def vault_dir(self) -> str:
        return self.path.parent.name

    def _source(self, cell) -> str:
        src = cell.get("source", "")
        return "".join(src) if isinstance(src, list) else src

    @property
    def markdown_cells(self) -> list[str]:
        return [self._source(c) for c in self.cells if c.get("cell_type") == "markdown"]

    @property
    def code_cells(self) -> list[str]:
        return [self._source(c) for c in self.cells if c.get("cell_type") == "code"]

    @property
    def prose(self) -> str:
        return "\n\n".join(self.markdown_cells)

    def outputs_text(self) -> str:
        """Everything committed as output, which is a real leak path."""
        chunks = []
        for cell in self.cells:
            for out in cell.get("outputs", []) or []:
                for key in ("text",):
                    val = out.get(key)
                    if val:
                        chunks.append("".join(val) if isinstance(val, list) else str(val))
                data = out.get("data", {})
                for val in data.values():
                    chunks.append("".join(val) if isinstance(val, list) else str(val))
        return "\n".join(chunks)

    def cell_order(self) -> list[str]:
        """The cell types in order, for the prose-between-code rule."""
        return [c.get("cell_type", "") for c in self.cells]

    def beats_present(self) -> dict[str, int]:
        """Beat name to the index of the markdown cell that opens it."""
        found = {}
        for index, cell in enumerate(self.cells):
            if cell.get("cell_type") != "markdown":
                continue
            text = self._source(cell)
            for name, heading in BEATS:
                if name not in found and re.search(rf"^{re.escape(heading)}\s*$",
                                                   text, re.MULTILINE):
                    found[name] = index
        return found


def all_notebooks() -> list[Notebook]:
    """Teaching notebooks, in vault then sub-module order.

    00-setup is excluded. It explains how to run the repo and is not a lesson,
    so forcing it through the eight beats would be theatre. It is still parsed,
    and still scanned for prose and for secrets.
    """
    paths = sorted(
        p for p in ROOT.glob("[0-9][0-9]-*/[0-9][0-9]-*.ipynb")
        if ".ipynb_checkpoints" not in p.parts and p.parent.name != "00-setup"
    )
    return [Notebook(p) for p in paths]


def every_notebook() -> list[Notebook]:
    """Everything, including 00-setup. Used by the prose and secret scans."""
    paths = sorted(
        p for p in ROOT.glob("[0-9][0-9]-*/*.ipynb")
        if ".ipynb_checkpoints" not in p.parts
    )
    return [Notebook(p) for p in paths]


def vault_dirs() -> list[pathlib.Path]:
    return sorted(
        p for p in ROOT.glob("[0-9][0-9]-*")
        if p.is_dir() and p.name != "00-setup"
    )


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z']+", text)


def strip_code_and_media(markdown: str) -> str:
    """Prose only. Fenced code, inline code, images and links are not prose."""
    text = re.sub(r"```.*?```", " ", markdown, flags=re.DOTALL)
    text = re.sub(r"`[^`]*`", " ", text)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"^\s*\|.*\|\s*$", " ", text, flags=re.MULTILINE)
    return text


def sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [p.strip() for p in parts if len(words(p)) >= 3]


def syllables(word: str) -> int:
    word = word.lower()
    groups = re.findall(r"[aeiouy]+", word)
    count = len(groups)
    if word.endswith("e") and count > 1:
        count -= 1
    return max(count, 1)
