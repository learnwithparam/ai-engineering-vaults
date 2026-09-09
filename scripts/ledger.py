"""Build progress, on disk.

The point of this file is recovery. If the run is interrupted, or context is
lost, the next step is read from here rather than remembered. `make status`
prints it.
"""
from __future__ import annotations

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from nbcommon import BUILD

LEDGER = BUILD / "ledger.json"

STATES = ("planned", "drafted", "scored", "fixtures", "diagrams", "accepted")


def load() -> dict:
    if LEDGER.is_file():
        return json.loads(LEDGER.read_text())
    return {"vaults": {}, "baseline": None, "contract_frozen": False}


def save(data: dict) -> None:
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    LEDGER.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def set_state(vault: str, submodule: str, state: str, score: float | None = None,
              failures: list[str] | None = None) -> None:
    if state not in STATES:
        raise ValueError(f"unknown state {state!r}, expected one of {STATES}")
    data = load()
    entry = data["vaults"].setdefault(vault, {})
    entry[submodule] = {"state": state, "score": score, "failures": failures or []}
    save(data)


def show() -> int:
    data = load()
    vaults = data.get("vaults", {})
    if not vaults:
        print("Nothing recorded yet. Phase 1 is still building the machine.")
        return 0

    done = 0
    total = 0
    print(f"{'vault':34} {'sub-module':30} {'state':10} {'score':>6}")
    print("-" * 84)
    for vault in sorted(vaults):
        for sub in sorted(vaults[vault]):
            e = vaults[vault][sub]
            total += 1
            done += e["state"] == "accepted"
            score = f"{e['score']:.1f}" if e.get("score") is not None else "-"
            print(f"{vault:34} {sub:30} {e['state']:10} {score:>6}")
            for f in e.get("failures", []):
                print(f"{'':66} ! {f}")

    print("-" * 84)
    print(f"accepted {done} of {total}")
    if data.get("baseline") is not None:
        print(f"baseline {data['baseline']:.1f}   contract frozen: {data.get('contract_frozen')}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "show":
        raise SystemExit(show())
    raise SystemExit(show())
