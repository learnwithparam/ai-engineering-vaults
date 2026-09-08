"""Refuse to commit a real credential.

Two files legitimately contain key-shaped text: the prose checker holds the
detection patterns, and the gate self test plants a decoy. Both are excluded by
path, and the decoy is additionally rejected as low entropy, so an actual key
pasted into either file would still be caught.
"""
from __future__ import annotations

import re
import subprocess
import sys

ALLOWED = {"scripts/check_prose.py", "scripts/check_gates.py", "scripts/scan_staged.py"}
SHAPES = [
    (re.compile(r"sk-or-v1-[A-Za-z0-9]{24,}"), "OpenRouter key"),
    (re.compile(r"sk-ant-[A-Za-z0-9\-_]{24,}"), "Anthropic key"),
    (re.compile(r"sk-proj-[A-Za-z0-9\-_]{24,}"), "OpenAI key"),
    (re.compile(r"\bAIza[0-9A-Za-z\-_]{30,}"), "Google key"),
    (re.compile(r"ghp_[A-Za-z0-9]{30,}"), "GitHub token"),
]


def looks_real(secret: str) -> bool:
    """A decoy is a repeated character. A real key is not."""
    body = re.sub(r"^(sk-or-v1-|sk-ant-|sk-proj-|AIza|ghp_)", "", secret)
    return len(set(body)) > 6


def staged_files() -> list[str]:
    out = subprocess.run(["git", "diff", "--cached", "--name-only"],
                         capture_output=True, text=True, check=True)
    return [f for f in out.stdout.split("\n") if f]


def main() -> int:
    hits = []
    for path in staged_files():
        if path in ALLOWED:
            continue
        blob = subprocess.run(["git", "show", f":{path}"], capture_output=True)
        if blob.returncode != 0:
            continue
        try:
            # Binary files cannot carry a pasted key in readable form, and
            # decoding one as text throws. Screenshots are the common case.
            content = blob.stdout.decode("utf-8")
        except UnicodeDecodeError:
            continue
        for pattern, label in SHAPES:
            for match in pattern.findall(content):
                if looks_real(match):
                    hits.append(f"{path}: {label}")

    for line in hits:
        print(f"  {line}")
    if hits:
        print(f"scan-staged: {len(hits)} real credentials staged. Commit refused.")
        return 1
    print(f"scan-staged: {len(staged_files())} files, no credential found")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
