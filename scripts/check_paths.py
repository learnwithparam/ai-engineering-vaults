"""Every repo path named in a doc has to resolve.

Docs drift when files move. This repo shipped three files and one make target
still pointing at build/provider-truth.json weeks after it moved to the root,
and nothing noticed, because a path in prose is not executed by anything.

Scope is deliberately narrow: inline code spans in markdown, fenced blocks
skipped, gitignored paths skipped. A false alarm here costs more than a miss.
"""
from __future__ import annotations

import pathlib
import re
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from nbcommon import ROOT

FENCE = re.compile(r"^```.*?^```", re.S | re.M)
SPAN = re.compile(r"`([^`\n]+)`")
SKIP_DIRS = {".git", ".venv", "node_modules", ".ipynb_checkpoints"}


def markdown_files() -> list[pathlib.Path]:
    return sorted(p for p in ROOT.rglob("*.md")
                  if not SKIP_DIRS & set(p.parts))


def ignored(rel: str) -> bool:
    result = subprocess.run(["git", "check-ignore", "--quiet", rel],
                            cwd=ROOT, capture_output=True)
    return result.returncode == 0


def candidates(text: str) -> list[str]:
    """A path is a code span with a slash, no spaces and no URL scheme."""
    out = []
    for span in SPAN.findall(FENCE.sub("", text)):
        token = span.strip().rstrip(".,;:)")
        if "/" not in token or " " in token or "://" in token:
            continue
        if any(c in token for c in "*?<>|$"):
            continue
        out.append(token)
    return out


def main() -> int:
    problems = []
    git = (ROOT / ".git").exists()
    for doc in markdown_files():
        rel = doc.relative_to(ROOT).as_posix()
        for token in candidates(doc.read_text()):
            if token.startswith("/"):
                problems.append(f"{rel}: {token} is an absolute path, "
                                f"useless to anyone who clones this")
                continue
            # Only a token whose first segment names something real is a repo
            # path. Without this, a model id and a sibling repo's file read as
            # broken links.
            head = token.split("/")[0]
            if not (ROOT / head).exists() and not (doc.parent / head).exists():
                continue
            if git and ignored(token):
                continue
            if (doc.parent / token).exists() or (ROOT / token).exists():
                continue
            problems.append(f"{rel}: {token} does not exist")

    for line in problems:
        print(f"  {line}")
    print(f"check-paths: {len(markdown_files())} docs, {len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
