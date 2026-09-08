"""A berth wait server, used to show what a stray write to stdout does.

One line decides where its trace goes, set by BERTH_LOG:

    stderr          the trace lands out of band, the protocol is untouched
    stdout-line     a whole line of text on stdout, between two messages
    stdout-partial  the same text with no newline, glued to the next message
"""
import os
import sys

from mcp.server.fastmcp import FastMCP

WAITS = {"NLRTM": 6.5, "SGSIN": 3.0, "USLAX": 19.5}
MODE = os.environ.get("BERTH_LOG", "stderr")

srv = FastMCP("berths", log_level="WARNING")


def trace(message: str) -> None:
    """Where a diagnostic goes. This is the whole lesson."""
    if MODE == "stdout-line":
        print(message, flush=True)
    elif MODE == "stdout-partial":
        print(message, end="", flush=True)
    else:
        print(message, file=sys.stderr, flush=True)


@srv.tool()
def berth_wait_hours(terminal: str) -> float:
    """Median hours a ship waits before a berth frees up."""
    trace(f"[berths] wait lookup for {terminal}")
    return WAITS.get(terminal, 0.0)


if __name__ == "__main__":
    srv.run()
