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
from render_diagrams import MANIFEST, digest, directive_problems, fitted_size, sources, svgs_for


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

    # The renderer writes every SVG at the size that fits the box, because VS Code and
    # GitHub load no stylesheet. So the declared size is asserted, and the labels it leaves.
    box = theme["frames"]
    for svg in sorted(produced):
        if not svg.is_file():
            continue
        text = svg.read_text()
        match = re.search(r"viewBox=[\"'][-\d.]+ [-\d.]+ ([\d.]+) ([\d.]+)", text)
        if not match:
            continue
        rel = svg.relative_to(ROOT)
        w, h = float(match.group(1)), float(match.group(2))
        fit_w, fit_h = fitted_size(w, h, box)
        declared = re.search(r'<svg[^>]* width="([\d.]+)" height="([\d.]+)"', text)
        spread = re.search(r"<svg[^>]* style=\"[^\"]*max-width:\s*([\d.]+)px", text)
        if not declared or (float(declared.group(1)), float(declared.group(2))) != (fit_w, fit_h):
            problems.append(f"{rel}: not written at {fit_w} by {fit_h}, so it can overflow the window. "
                            f"Run: make diagrams")
        elif spread and float(spread.group(1)) != fit_w:
            problems.append(f"{rel}: inline max-width {spread.group(1)}px lets it spread past {fit_w}. "
                            f"Run: make diagrams")
        label_px = box["baseLabelPx"] * fit_w / w
        if label_px < box["minLabelPx"]:
            problems.append(f"{rel}: {w:.0f} by {h:.0f} fits the box only at {label_px:.1f}px labels, "
                            f"under {box['minLabelPx']}. Cut a node or shorten the chain")

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
