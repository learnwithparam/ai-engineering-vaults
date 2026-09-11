"""Render every .mmd to committed SVGs, and record a hash manifest.

A source carrying `%% step N: ids` directives renders once and is cut into one
frame per step by restyling that same SVG, so every frame shares one layout.
Rendering needs node, via npx mmdc. Checking freshness does not, which is why
CI can verify diagrams without installing a browser toolchain.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import re
import subprocess
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from nbcommon import ROOT

THEME = ROOT / "diagrams" / "theme.json"
MANIFEST = ROOT / "diagrams" / "manifest.json"

DIRECTIVE = re.compile(r"^\s*%%\s*(step|retire)\s+(\d+)\s*:\s*(.+?)\s*$", re.MULTILINE)
DECLARED = re.compile(r"^\s*([A-Za-z]\w*)\s*[\[\{\(]", re.MULTILINE)
ROLE = re.compile(r"^\s*([A-Za-z]\w*)\s*[\[\{\(].*?:::(\w+)\s*$", re.MULTILINE)
SUBGRAPH = re.compile(r"^\s*subgraph\s+([A-Za-z]\w*)", re.MULTILINE)
ARROW = re.compile(r"\s*(?:-\.->|-->|==>|---|-\.-)\s*")
NOT_EDGES = re.compile(r"^(%%|classDef\s|class\s|subgraph\s|linkStyle\s|style\s|graph\s|flowchart\s|end$)")


def sources(prefix: str = "") -> list[pathlib.Path]:
    found = sorted(ROOT.glob("[0-9][0-9]-*/diagrams/*.mmd"))
    return [p for p in found if p.relative_to(ROOT).as_posix().startswith(prefix)]


def digest(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def edges(text: str) -> list[tuple[str, str, str]]:
    """(source, target, Mermaid's edge id) in source order, chains included."""
    out, seen = [], {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or NOT_EDGES.match(stripped):
            continue
        bare = re.sub(r'"[^"]*"', "", stripped)
        bare = re.sub(r"\|[^|]*\||:::\w+|\[[^\]]*\]|\{[^}]*\}|\([^)]*\)", "", bare)
        ids = [t.strip() for t in ARROW.split(bare)]
        for a, b in zip(ids, ids[1:]):
            if a and b:
                k = seen.get((a, b), 0)
                seen[(a, b)] = k + 1
                out.append((a, b, f"L_{a}_{b}_{k}"))
    return out


def series(text: str) -> tuple[dict[int, list[str]], dict[int, list[str]]]:
    """The step and retire directives, keyed by step number."""
    steps: dict[int, list[str]] = {}
    retire: dict[int, list[str]] = {}
    for kind, n, ids in DIRECTIVE.findall(text):
        (steps if kind == "step" else retire).setdefault(int(n), []).extend(ids.split())
    return steps, retire


def directive_problems(text: str) -> list[str]:
    """Everything a series can get wrong, found without rendering it."""
    steps, retire = series(text)
    if not steps:
        return []
    links = edges(text)
    nodes = set(DECLARED.findall(text)) | {e[0] for e in links} | {e[1] for e in links}
    known = nodes | set(SUBGRAPH.findall(text))
    pairs = {f"{a}-{b}" for a, b, _ in links}
    problems = []
    if sorted(steps) != list(range(1, len(steps) + 1)):
        problems.append(f"steps are numbered {sorted(steps)}, expected 1 to {len(steps)} with no gaps")
    if len(steps) < 3:
        problems.append(f"{len(steps)} steps, a series needs at least 3")
    for n, ids in sorted(steps.items()):
        problems += [f"step {n} names {i!r}, which is not in the graph" for i in ids if i not in known]
    for n, ids in sorted(retire.items()):
        problems += [f"retire {n} names {i!r}, which is not a node or an edge like A-B"
                     for i in ids if i not in known and i not in pairs]
    lit = {i for ids in steps.values() for i in ids} | {i for ids in retire.values() for i in ids}
    problems += [f"{i!r} is never lit, so the last frame is still a ghost" for i in sorted(nodes - lit)]
    problems += [f"node id {i!r} has an underscore, which breaks Mermaid's edge ids"
                 for i in sorted(known) if "_" in i]
    return problems


def svgs_for(mmd: pathlib.Path) -> list[pathlib.Path]:
    """What a source renders to: one SVG, or one frame per step."""
    steps, _ = series(mmd.read_text())
    images = mmd.parent.parent / "images"
    if not steps:
        return [images / f"{mmd.stem}.svg"]
    return [images / f"{mmd.stem}-step-{n}.svg" for n in sorted(steps)]


def with_roles(mmd: pathlib.Path, theme: dict) -> str:
    """Append the six role classDefs unless the diagram already defines them."""
    text = mmd.read_text().rstrip()
    if "classDef" in text:
        return text
    return text + "\n  " + "\n  ".join(theme["roleClasses"]) + "\n"


def _state_at(steps: dict, retire: dict, links: list, n: int) -> tuple[set, set, set]:
    """Lit nodes, retired ids and visible edge ids after step n."""
    gone = {i for k, ids in retire.items() if k <= n for i in ids}
    lit = {i for k, ids in steps.items() if k <= n for i in ids} - gone
    shown = {eid for a, b, eid in links
             if a in lit and b in lit and f"{a}-{b}" not in gone}
    return lit, gone, shown


def frame_css(text: str, theme: dict, n: int) -> str:
    """The stylesheet that turns the full render into frame n."""
    steps, retire = series(text)
    links = edges(text)
    style = theme["frames"]
    glow = {line.split()[1]: re.search(r"stroke:(#[0-9A-Fa-f]{6})", line).group(1)
            for line in theme["roleClasses"]}
    roles = dict(ROLE.findall(text))
    lit, gone, shown = _state_at(steps, retire, links, n)
    _, _, shown_before = _state_at(steps, retire, links, n - 1)
    shapes = ":is(rect,polygon,circle,ellipse,path)"

    def node(i: str) -> str:
        return f'[id="my-svg-{i}"], [id^="my-svg-flowchart-{i}-"]'

    rules = []
    for i in sorted(set(DECLARED.findall(text)) | set(SUBGRAPH.findall(text))):
        sel = node(i)
        if i in gone:
            rules.append(f"{sel} {{ opacity: 0 !important; }}")
        elif i not in lit:
            rules.append(f"{sel} {{ opacity: {style['ghostOpacity']} !important; }}")
            rules.append(f":is({sel}) {shapes} {{ stroke-dasharray: {style['ghostDash']} !important; }}")
        elif i in steps.get(n, []):
            colour = glow.get(roles.get(i, ""), style["nowEdgeColour"])
            rules.append(f":is({sel}) {shapes} {{ stroke-width: {style['nowStroke']} !important; "
                         f"filter: drop-shadow(0 0 6px {colour}); }}")
            # Brighter, never bolder: Mermaid sized the box for regular weight.
            rules.append(f":is({sel}) :is(span,p) {{ color: #FFFFFF !important; }}")
    for a, b, eid in links:
        sel = f'[id="my-svg-{eid}"], [data-id="{eid}"]'
        if f"{a}-{b}" in gone or a in gone or b in gone:
            rules.append(f"{sel} {{ opacity: 0 !important; }}")
        elif eid not in shown:
            rules.append(f"{sel} {{ opacity: {style['ghostOpacity']} !important; "
                         f"stroke-dasharray: {style['ghostDash']} !important; }}")
        elif eid not in shown_before:
            rules.append(f'[id="my-svg-{eid}"] {{ stroke-width: {style["nowStroke"]} !important; '
                         f'stroke: {style["nowEdgeColour"]} !important; }}')
    return "\n".join(rules)


def _mmdc(source: str, name: str, theme: dict, out: pathlib.Path) -> None:
    config = {"theme": theme["theme"], "themeVariables": theme["themeVariables"]}
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = pathlib.Path(tmp)
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps(config))
        source_file = tmp_path / name
        source_file.write_text(source)

        # themeCSS in the config file is silently ignored by mermaid-cli, which
        # is how edge labels end up unstyled and invisible on a dark ground.
        # It has to arrive as a real stylesheet via --cssFile.
        css_file = tmp_path / "theme.css"
        css_file.write_text(theme["themeCSS"])

        result = subprocess.run(
            ["npx", "-y", "-p", "@mermaid-js/mermaid-cli", "mmdc",
             "-i", str(source_file), "-o", str(out),
             "-c", str(config_file), "-C", str(css_file), "-b", "transparent"],
            capture_output=True, text=True, timeout=300,
        )
    if result.returncode != 0:
        raise RuntimeError(f"{name}: mmdc failed\n{result.stderr[-800:]}")
    _real_size(out)


def _real_size(svg: pathlib.Path) -> None:
    """Swap width="100%" for the viewBox size. Without it an <img> has no
    natural width and shrinks to the prose column, which made labels 6px."""
    text = svg.read_text()
    match = re.search(r'viewBox="[-\d.]+ [-\d.]+ ([\d.]+) ([\d.]+)"', text)
    if match:
        w, h = (round(float(v)) for v in match.groups())
        svg.write_text(text.replace('width="100%"', f'width="{w}" height="{h}"', 1))


def render(mmd: pathlib.Path, theme: dict) -> None:
    text = mmd.read_text()
    frames = svgs_for(mmd)
    images = frames[0].parent
    images.mkdir(parents=True, exist_ok=True)
    steps, _ = series(text)
    if not steps:
        _mmdc(with_roles(mmd, theme), mmd.name, theme, frames[0])
        return

    with tempfile.TemporaryDirectory() as tmp:
        full = pathlib.Path(tmp) / "full.svg"
        _mmdc(with_roles(mmd, theme), mmd.name, theme, full)
        svg = full.read_text()
    head, tail = svg.rsplit("</svg>", 1)
    # A series replaces the single picture and any frames from a longer version.
    for stale in [images / f"{mmd.stem}.svg", *images.glob(f"{mmd.stem}-step-*.svg")]:
        stale.unlink(missing_ok=True)
    for n, frame in zip(sorted(steps), frames):
        frame.write_text(f"{head}<style>{frame_css(text, theme, n)}</style></svg>{tail}")


def main() -> int:
    prefix = sys.argv[1] if len(sys.argv) > 1 else ""
    mmds = sources(prefix)
    if not mmds:
        print(f"render-diagrams: no .mmd sources match {prefix!r}")
        if not prefix:
            MANIFEST.write_text(json.dumps({}, indent=2) + "\n")
        return 0

    theme = json.loads(THEME.read_text())
    # One render at a time: parallel authors share the manifest, and each render
    # starts a headless browser. The lock is released when the process exits.
    import fcntl
    (ROOT / "build").mkdir(exist_ok=True)
    lock = open(ROOT / "build" / "render.lock", "w")
    fcntl.flock(lock, fcntl.LOCK_EX)
    # A filtered run keeps every other vault's entries, a full run rebuilds.
    # Either way an entry whose source was deleted goes, or check-diagrams flags it.
    manifest = json.loads(MANIFEST.read_text()) if prefix and MANIFEST.is_file() else {}
    manifest = {rel: sha for rel, sha in manifest.items() if (ROOT / rel).is_file()}
    for mmd in mmds:
        rel = mmd.relative_to(ROOT).as_posix()
        problems = directive_problems(mmd.read_text())
        if problems:
            print(f"  {rel}:\n    " + "\n    ".join(problems))
            return 1
        print(f"  rendering {rel} ({len(svgs_for(mmd))} SVG)")
        render(mmd, theme)
        manifest[rel] = digest(mmd)

    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(f"render-diagrams: {len(mmds)} rendered, manifest updated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
