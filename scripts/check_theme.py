"""The theme files exist, parse, and agree with each other.

Structural only. This cannot prove the theme renders, and does not claim to.
The render is confirmed by eye against docs/theme.png.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from nbcommon import ROOT

CSS = ROOT / ".jupyter" / "custom" / "custom.css"
SETTINGS = ROOT / ".jupyter" / "lab" / "user-settings" / "@jupyterlab"
THEMES = SETTINGS / "apputils-extension" / "themes.jupyterlab-settings"
TRACKER = SETTINGS / "notebook-extension" / "tracker.jupyterlab-settings"


def strip_json_comments(text: str) -> str:
    text = re.sub(r"^\s*//.*$", "", text, flags=re.MULTILINE)
    return re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)


def main() -> int:
    problems = []
    for path in (CSS, THEMES, TRACKER):
        if not path.is_file():
            problems.append(f"missing {path.relative_to(ROOT)}")

    if problems:
        for line in problems:
            print(f"  {line}")
        print(f"check-theme: {len(problems)} problems")
        return 1

    settings = {}
    for path in (THEMES, TRACKER):
        try:
            settings[path.name] = json.loads(strip_json_comments(path.read_text()))
        except json.JSONDecodeError as exc:
            problems.append(f"{path.relative_to(ROOT)}: invalid JSON, {exc.msg}")

    css = CSS.read_text()
    if "--jp-layout-color0" not in css:
        problems.append("custom.css never sets --jp-layout-color0, so the canvas is untouched")

    tracker = settings.get(TRACKER.name, {})
    fonts = {tracker.get("codeCellConfig", {}).get("fontFamily", ""),
             tracker.get("markdownCellConfig", {}).get("fontFamily", "")}
    declared = {f for f in fonts if f}
    if not declared:
        problems.append("tracker settings declare no fontFamily")
    for family in declared:
        head = family.split(",")[0].strip().strip("'\"")
        if head and head not in css:
            problems.append(
                f"tracker uses font {head!r} but custom.css never mentions it. "
                f"The two must agree or the notebook and the chrome will not match")

    if settings.get(THEMES.name, {}).get("theme") != "JupyterLab Dark":
        problems.append("themes settings do not select JupyterLab Dark as the base")

    for line in problems:
        print(f"  {line}")
    print(f"check-theme: {len(problems)} problems (structural only, does not prove a render)")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
