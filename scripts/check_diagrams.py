"""Diagrams are fresh and every reference resolves.

Freshness is a hash comparison against diagrams/manifest.json, so this needs no
node and runs anywhere.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import nbcommon as nb
from nbcommon import ROOT
from render_diagrams import MANIFEST, digest, sources, svg_for


def main() -> int:
    mmds = sources()
    problems = []
    manifest = json.loads(MANIFEST.read_text()) if MANIFEST.is_file() else {}

    for mmd in mmds:
        rel = mmd.relative_to(ROOT).as_posix()
        svg = svg_for(mmd)
        if not svg.is_file():
            problems.append(f"{rel}: no rendered SVG. Run: make diagrams")
            continue
        if manifest.get(rel) != digest(mmd):
            problems.append(f"{rel}: source changed since the SVG was rendered. Run: make diagrams")

    # The edge label rule arrives through --cssFile. Passing it as a themeCSS
    # config key is silently ignored, which leaves edge labels unstyled and
    # invisible on a dark background. Assert it actually landed.
    theme = json.loads((ROOT / "diagrams" / "theme.json").read_text())
    marker = theme["themeCSS"].split("{")[0].strip()
    for mmd in mmds:
        svg = svg_for(mmd)
        if svg.is_file() and marker not in svg.read_text():
            problems.append(
                f"{svg.relative_to(ROOT)}: the edge label stylesheet is missing. "
                f"mermaid-cli dropped it. Re-render with make diagrams")

    for stale in sorted(set(manifest) - {m.relative_to(ROOT).as_posix() for m in mmds}):
        problems.append(f"{stale}: in the manifest but the source is gone. Run: make diagrams")

    for n in nb.all_notebooks():
        for ref in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", n.prose):
            if ref.startswith(("http://", "https://", "data:")):
                continue
            if not (n.path.parent / ref).resolve().is_file():
                problems.append(f"{n.rel}: image reference {ref!r} does not resolve")

    for line in problems:
        print(f"  {line}")
    print(f"check-diagrams: {len(mmds)} sources, {len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
