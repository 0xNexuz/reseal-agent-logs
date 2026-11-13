"""A minimal outside checkpoint, and a wrapper that adds it to any tool.

Sprint work (13 Nov 2026 onward).

The checkpoint is two values that someone other than the operator keeps:

    count   how many records the log had when the checkpoint was taken
    digest  a running SHA-256 over those records, in order

``digest`` is a prefix digest: d_0 = 32 zero bytes,
d_k = SHA-256(d_{k-1} || SHA-256(canonical JSON of record k)). A later, longer
log can therefore still be checked: its first ``count`` records must give the
same digest. Nothing here needs keys, and nothing depends on the tool.

What it catches: any change to, removal of, or insertion among the first
``count`` records, a log shorter than ``count``, and a different history for
that prefix. What it cannot catch: changes after the last checkpoint, and
actions that were never recorded.
"""

from __future__ import annotations

import hashlib
import json

from .adapters.base import ACCEPTED, REJECTED, Run, Verdict


def _leaf(record) -> bytes:
    text = json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(text.encode("utf-8")).digest()


def prefix_digest(records, count: int) -> str:
    d = bytes(32)
    for rec in records[:count]:
        d = hashlib.sha256(d + _leaf(rec)).digest()
    return d.hex()


def take(records, count: int | None = None) -> dict:
    """What the outside party stores."""
    count = len(records) if count is None else count
    return {"count": count, "digest": prefix_digest(records, count)}


def check(records, cp: dict) -> tuple[bool, str]:
    if len(records) < cp["count"]:
        return False, f"log has {len(records)} records, checkpoint covers {cp['count']}"
    if prefix_digest(records, cp["count"]) != cp["digest"]:
        return False, f"first {cp['count']} records do not match the checkpoint"
    return True, f"first {cp['count']} records match the checkpoint"


SETUPS = {
    # setup name -> share of the log the checkpoint covers
    "checkpoint": 1.0,        # taken after the last record
    "checkpoint-stale": 0.9,  # taken earlier: the last tenth of the log is not covered
}


class Checkpointed:
    """Wrap an adapter: the tool's default verifier, then the outside checkpoint."""

    def __init__(self, inner, cover: float = 1.0):
        self._inner = inner
        self._cover = cover

    def __getattr__(self, name):  # hooks, load/dump, names: all from the wrapped tool
        return getattr(self._inner, name)

    def record(self, events, logdir, *, strong, secrets=None) -> Run:
        run = self._inner.record(events, logdir, strong=False, secrets=secrets)
        records, _ = self._inner.load(run.logdir)
        run.external["_cp"] = take(records, int(len(records) * self._cover))
        return run

    def verify(self, logdir, external, *, strong) -> Verdict:
        own = self._inner.verify(logdir, external, strong=False)
        if own.status != ACCEPTED:
            return own
        try:
            records, _ = self._inner.load(logdir)
        except Exception as exc:  # unreadable log: nothing to vouch for
            return Verdict(REJECTED, f"checkpoint: unreadable log ({type(exc).__name__})")
        ok, why = check(records, external["_cp"])
        return Verdict(ACCEPTED if ok else REJECTED, "checkpoint: " + why)


def wrap(adapter, setup: str):
    return Checkpointed(adapter, SETUPS[setup])


def describe(setup: str) -> str:
    share = SETUPS[setup]
    when = "after the last record" if share == 1.0 else f"after the first {share:.0%} of the log"
    return f"the tool's default check plus a ReSeal checkpoint (count and prefix digest) taken {when} and held outside the operator"
