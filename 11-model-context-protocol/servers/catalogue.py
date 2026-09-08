"""A tiny catalogue server, used to show the protocol on the wire.

One of each primitive: a tool that runs, a resource that only reads, and a
prompt that is wording the host can borrow. Nothing here knows about a model.
"""
import json

from mcp.server.fastmcp import FastMCP

TRACKS = {
    "T-1042": {"title": "Blue Monday", "artist": "New Order", "bpm": 130},
    "T-2277": {"title": "Teardrop", "artist": "Massive Attack", "bpm": 78},
}

srv = FastMCP("catalogue", log_level="WARNING")


@srv.tool()
def similar_tracks(track_id: str, limit: int = 3) -> list[str]:
    """Track ids a listener of this one usually plays next."""
    if track_id not in TRACKS:
        raise ValueError(f"unknown track {track_id}")
    return [f"{track_id}-near-{n}" for n in range(limit)]


@srv.resource("catalogue://track/{track_id}")
def track_record(track_id: str) -> str:
    """One catalogue row. Reading it changes nothing."""
    return json.dumps(TRACKS.get(track_id, {}))


@srv.prompt()
def explain_pick(track_id: str) -> str:
    """Wording the host can borrow when it explains a pick."""
    return f"In one sentence, say why {track_id} follows what is playing now."


if __name__ == "__main__":
    srv.run()
