"""Render every .mmd to a committed SVG, and record a hash manifest.

Rendering needs node, via npx mmdc. Checking freshness does not, which is why
CI can verify diagrams without installing a browser toolchain.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from nbcommon import ROOT

THEME = ROOT / "diagrams" / "theme.json"
MANIFEST = ROOT / "diagrams" / "manifest.json"


def sources() -> list[pathlib.Path]:
    return sorted(ROOT.glob("[0-9][0-9]-*/diagrams/*.mmd"))


def digest(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def svg_for(mmd: pathlib.Path) -> pathlib.Path:
    return mmd.parent.parent / "images" / f"{mmd.stem}.svg"


def with_roles(mmd: pathlib.Path, theme: dict) -> str:
    """Append the six role classDefs unless the diagram already defines them."""
    text = mmd.read_text().rstrip()
    if "classDef" in text:
        return text
    return text + "\n  " + "\n  ".join(theme["roleClasses"]) + "\n"


def render(mmd: pathlib.Path, theme: dict) -> None:
    svg = svg_for(mmd)
    svg.parent.mkdir(parents=True, exist_ok=True)

    config = {
        "theme": theme["theme"],
        "themeVariables": theme["themeVariables"],
        "themeCSS": theme["themeCSS"],
    }
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = pathlib.Path(tmp)
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps(config))
        source_file = tmp_path / mmd.name
        source_file.write_text(with_roles(mmd, theme))

        result = subprocess.run(
            ["npx", "-y", "-p", "@mermaid-js/mermaid-cli", "mmdc",
             "-i", str(source_file), "-o", str(svg),
             "-c", str(config_file), "-b", "transparent"],
            capture_output=True, text=True, timeout=300,
        )
    if result.returncode != 0:
        raise RuntimeError(f"{mmd.name}: mmdc failed\n{result.stderr[-800:]}")


def main() -> int:
    mmds = sources()
    if not mmds:
        print("render-diagrams: no .mmd sources yet")
        MANIFEST.write_text(json.dumps({}, indent=2) + "\n")
        return 0

    theme = json.loads(THEME.read_text())
    manifest = {}
    for mmd in mmds:
        rel = mmd.relative_to(ROOT).as_posix()
        print(f"  rendering {rel}")
        render(mmd, theme)
        manifest[rel] = digest(mmd)

    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(f"render-diagrams: {len(mmds)} rendered, manifest updated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
