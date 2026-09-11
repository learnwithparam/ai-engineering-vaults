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

HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)
# A course is one notebook: an overview, then "## Step 0: ..." to "## Step N: ...".
STEP = re.compile(r"^## Step (\d+): (.+?)\s*$", re.MULTILINE)
IMAGE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
FRAME = re.compile(r"([^/]+)-step-(\d+)\.svg$")


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

    def title(self) -> str:
        return next((t for _, level, t in self.headings() if level == 1), "")

    def source_of(self, index: int) -> str:
        return self._source(self.cells[index])

    def headings(self) -> list[tuple[int, int, str]]:
        """Every heading as (cell index, level, text), in reading order."""
        out = []
        for index, cell in enumerate(self.cells):
            if cell.get("cell_type") == "markdown":
                for hashes, text in HEADING.findall(self._source(cell)):
                    out.append((index, len(hashes), text))
        return out

    def steps(self) -> list[dict]:
        """Every '## Step N: title' heading, in reading order."""
        return [{"cell": index, "number": int(m.group(1)), "title": m.group(2)}
                for index, level, text in self.headings() if level == 2
                for m in [STEP.match(f"## {text}")] if m]

    def frames(self) -> list[tuple[int, str, int]]:
        """Every diagram frame shown, as (cell index, series, frame number), in reading order."""
        out = []
        for index, cell in enumerate(self.cells):
            if cell.get("cell_type") == "markdown":
                for ref in IMAGE.findall(self._source(cell)):
                    match = FRAME.search(ref)
                    if match:
                        out.append((index, match.group(1), int(match.group(2))))
        return out


def all_notebooks() -> list[Notebook]:
    """Course notebooks, one per vault, in vault order.

    00-setup is excluded. It explains how to run the repo and is not a lesson,
    so forcing it through the course shape would be theatre. It is still parsed,
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


LIST_ITEM = re.compile(r"^\s*(?:[-*]|\d+\.)\s+")


def prose_blocks(markdown: str) -> list[tuple[bool, list[str]]]:
    """Paragraphs and list items as (is_list_item, sentences), headings dropped.

    A list item is its own block, so a bullet with no full stop never merges
    into the next one, and a label list is never read as a run of fragments.
    """
    text = re.sub(r"\$\$.*?\$\$", " ", markdown, flags=re.DOTALL)
    text = strip_code_and_media(re.sub(r"\$[^$\n]+\$", " x ", text))
    blocks: list[tuple[bool, str]] = []
    joining = False
    for line in text.splitlines():
        s = line.strip()
        if not s or HEADING.match(s) or s == "---":
            joining = False
            continue
        if LIST_ITEM.match(line):
            blocks.append((True, LIST_ITEM.sub("", line).strip()))
            joining = True
        elif joining:
            blocks[-1] = (blocks[-1][0], blocks[-1][1] + " " + s)
        else:
            blocks.append((False, s))
            joining = True
    out = []
    for is_item, body in blocks:
        parts = [p.strip() for p in re.split(r"(?<=[.!?])\s+", body.rstrip(":")) if words(p)]
        if parts:
            out.append((is_item, parts))
    return out


def flow_sentences(markdown: str) -> list[str]:
    return [s for _, parts in prose_blocks(markdown) for s in parts]


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
