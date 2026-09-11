"""Diagrams are fresh, step series are well formed, and every SVG is shown.

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
from render_diagrams import MANIFEST, digest, directive_problems, sources, svgs_for


def main() -> int:
    mmds = sources()
    problems = []
    manifest = json.loads(MANIFEST.read_text()) if MANIFEST.is_file() else {}
    produced = {svg for mmd in mmds for svg in svgs_for(mmd)}

    for mmd in mmds:
        rel = mmd.relative_to(ROOT).as_posix()
        problems += [f"{rel}: {p}" for p in directive_problems(mmd.read_text())]
        missing = [svg for svg in svgs_for(mmd) if not svg.is_file()]
        if missing:
            problems.append(f"{rel}: {len(missing)} SVG not rendered. Run: make diagrams")
            continue
        if manifest.get(rel) != digest(mmd):
            problems.append(f"{rel}: source changed since the SVG was rendered. Run: make diagrams")

    # The edge label rule arrives through --cssFile. Passing it as a themeCSS
    # config key is silently ignored, which leaves edge labels unstyled and
    # invisible on a dark background. Assert it actually landed.
    theme = json.loads((ROOT / "diagrams" / "theme.json").read_text())
    marker = theme["themeCSS"].split("{")[0].strip()
    for svg in sorted(produced):
        if svg.is_file() and marker not in svg.read_text():
            problems.append(
                f"{svg.relative_to(ROOT)}: the edge label stylesheet is missing. "
                f"mermaid-cli dropped it. Re-render with make diagrams")

    # A frame shrinks to fit one screen. Shrunk too far, its labels are lost on video.
    box = theme["frames"]
    for svg in sorted(produced):
        if not (svg.is_file() and "-step-" in svg.name):
            continue
        match = re.search(r"viewBox=[\"'][-\d.]+ [-\d.]+ ([\d.]+) ([\d.]+)", svg.read_text())
        if not match:
            continue
        w, h = float(match.group(1)), float(match.group(2))
        scale = min(1.0, box["maxFrameWidth"] / w, box["maxFrameHeight"] / h)
        if scale < box["minLabelScale"]:
            problems.append(
                f"{svg.relative_to(ROOT)}: {w:.0f} by {h:.0f} shrinks labels to {scale:.0%}, "
                f"unreadable on video. Change the layout direction, or cut a node")

    for stale in sorted(set(manifest) - {m.relative_to(ROOT).as_posix() for m in mmds}):
        problems.append(f"{stale}: in the manifest but the source is gone. Run: make diagrams")

    shown = set()
    for n in nb.every_notebook():
        for ref in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", n.prose):
            if ref.startswith(("http://", "https://", "data:")):
                continue
            target = (n.path.parent / ref).resolve()
            shown.add(target)
            if not target.is_file():
                problems.append(f"{n.rel}: image reference {ref!r} does not resolve")

    # A frame nobody shows is a step the lesson skipped. An SVG no source
    # renders is a leftover from a renamed or shortened series.
    for svg in sorted(ROOT.glob("[0-9][0-9]-*/images/*.svg")):
        rel = svg.relative_to(ROOT)
        if svg not in produced:
            problems.append(f"{rel}: no source renders it. Delete it or restore its .mmd")
        elif svg.resolve() not in shown:
            problems.append(f"{rel}: rendered but no notebook shows it")

    for line in problems:
        print(f"  {line}")
    print(f"check-diagrams: {len(mmds)} sources, {len(produced)} SVG, {len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
