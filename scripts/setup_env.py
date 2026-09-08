"""Create .env, reusing a key that already exists on this machine.

Secrets are copied, never displayed. Nothing here prints a value, and nothing
returns one to a caller. The only output is whether a variable is set and how
long it is, which is enough to debug and not enough to leak.
"""
from __future__ import annotations

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
FLEET = ROOT.parent
WANTED = ("OPENROUTER_API_KEY", "GOOGLE_API_KEY")


def read_env_file(path: pathlib.Path) -> dict[str, str]:
    """Parse KEY=value pairs. Values stay inside this process."""
    out: dict[str, str] = {}
    if not path.is_file():
        return out
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        out[key.strip()] = value.strip().strip('"').strip("'")
    return out


def find_in_fleet(name: str) -> str:
    """Search sibling repos for a usable value. Returns it without printing."""
    for env_path in sorted(FLEET.glob("*/.env")):
        value = read_env_file(env_path).get(name, "")
        if value and not value.startswith("your-"):
            return value
    return ""


def is_placeholder(value: str) -> bool:
    return not value or value.startswith("your-") or value.endswith("-here")


def build_env_text(template: str, found: dict[str, str]) -> str:
    """Substitute real values into the template, leaving everything else intact."""
    lines = []
    for line in template.splitlines():
        match = re.match(r"^([A-Z_]+)=(.*)$", line)
        if match and match.group(1) in found:
            lines.append(f"{match.group(1)}={found[match.group(1)]}")
        else:
            lines.append(line)
    return "\n".join(lines) + "\n"


def describe(name: str, value: str) -> str:
    """A safe one line status. Never the value."""
    if is_placeholder(value):
        return f"  {name:22} not set"
    return f"  {name:22} set, {len(value)} chars"


def main() -> int:
    target = ROOT / ".env"
    if target.exists():
        current = read_env_file(target)
        print(".env already exists, leaving it alone")
        for name in WANTED:
            print(describe(name, current.get(name, "")))
        return 0

    found = {n: v for n in WANTED if (v := find_in_fleet(n))}
    text = build_env_text((ROOT / "env.example").read_text(), found)
    target.write_text(text)
    target.chmod(0o600)

    print(".env created from env.example, mode 600")
    for name in WANTED:
        print(describe(name, found.get(name, "")))
    if "OPENROUTER_API_KEY" not in found:
        print("\n  No key found in sibling repos. Add OPENROUTER_API_KEY to .env by hand.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
