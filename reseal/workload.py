"""Seeded synthetic agent workload.

One neutral event stream is fed to every tool through that tool's own
recording API, so all tools are attacked on the same history.

Event shape (plain JSON-safe dict):

    {
      "i":       0,                      # position in the run
      "ts":      "2026-11-13T09:00:00Z", # deterministic, strictly increasing
      "kind":    "tool_call",            # model_call | tool_call | file_write |
                                         # approval | delegation
      "tool":    "payments.refund",
      "args":    {"amount": 120, ...},
      "verdict": "allowed",              # allowed | blocked (policy gate)
      "actor":   "agent-7",
      "outcome": "success",              # success | error
    }
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone

KINDS = [
    ("tool_call", 0.45),
    ("model_call", 0.25),
    ("file_write", 0.15),
    ("approval", 0.08),
    ("delegation", 0.07),
]

TOOLS = {
    "tool_call": ["crm.lookup", "payments.refund", "email.send", "db.query", "search.web"],
    "model_call": ["model.generate"],
    "file_write": ["fs.write", "fs.delete"],
    "approval": ["human.approve"],
    "delegation": ["agent.delegate"],
}

START = datetime(2026, 11, 13, 9, 0, 0, tzinfo=timezone.utc)


def _args(rng: random.Random, tool: str, i: int) -> dict:
    if tool == "payments.refund":
        return {"amount": rng.randint(5, 500), "currency": "USD", "account": f"acct-{rng.randint(1, 40)}"}
    if tool == "email.send":
        return {"to": f"user{rng.randint(1, 90)}@example.com", "template": rng.choice(["receipt", "notice", "reset"])}
    if tool == "db.query":
        return {"table": rng.choice(["orders", "customers", "tickets"]), "limit": rng.choice([10, 50, 100])}
    if tool == "crm.lookup":
        return {"account": f"acct-{rng.randint(1, 40)}"}
    if tool == "search.web":
        return {"query": f"topic {rng.randint(1, 300)}"}
    if tool == "model.generate":
        return {"model": "example-model-1", "messages": rng.randint(1, 12)}
    if tool in ("fs.write", "fs.delete"):
        return {"path": f"/srv/data/file_{rng.randint(1, 200)}.txt", "bytes": rng.randint(10, 9000)}
    if tool == "human.approve":
        return {"approver": f"staff-{rng.randint(1, 6)}", "request": f"req-{i}"}
    return {"to_agent": f"agent-{rng.randint(8, 12)}", "scope": rng.choice(["read", "write"])}


def generate(n: int = 1000, seed: int = 0) -> list[dict]:
    """Return ``n`` events. Same (n, seed) always returns the same list."""
    rng = random.Random(seed)
    kinds = [k for k, _ in KINDS]
    weights = [w for _, w in KINDS]
    events = []
    ts = START
    for i in range(n):
        kind = rng.choices(kinds, weights)[0]
        tool = rng.choice(TOOLS[kind])
        ts = ts + timedelta(seconds=rng.randint(1, 5))
        events.append(
            {
                "i": i,
                "ts": ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "kind": kind,
                "tool": tool,
                "args": _args(rng, tool, i),
                # ~12% of gated actions are blocked by policy.
                "verdict": "blocked" if rng.random() < 0.12 else "allowed",
                "actor": "agent-7",
                "outcome": "error" if rng.random() < 0.05 else "success",
            }
        )
    return events
