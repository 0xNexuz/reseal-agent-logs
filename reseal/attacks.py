"""ReSeal attack library v0.

Every attack takes a clean recorded log and returns a tampered copy for the
tool's own verifier to judge. Attacks never touch ``Run.external`` (trusted
state held outside the attacker's reach).

Attacker tiers
--------------
T1  outside editor      edits stored bytes; does not repair integrity fields
T1+ public re-seal      rebuilds the log with the tool's own library but
                        without the original keys (fresh keys if needed)
T2  operator            rebuilds the log with the real signing keys
T3  equivocating        operator who shows a different history (a fork)
--  boundary            the action never reached the recorder at all

T1+ and T2 are implemented as "re-record": the edited event list is written
again through the tool's public recording API. That keeps the attack free of
tool-specific tricks: it is what any operator can do with the SDK.
"""

from __future__ import annotations

import copy
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from .adapters import Adapter, NotApplicable, Run
from .workload import generate

POSITIONS = ("first", "middle", "penultimate", "final")


def index_for(position: str, n: int) -> int:
    return {"first": 0, "middle": n // 2, "penultimate": n - 2, "final": n - 1}[position]


@dataclass
class Ctx:
    adapter: Adapter
    events: list[dict]
    run: Run
    work: Path          # fresh directory for this trial
    position: str = "middle"
    variant: str = ""

    @property
    def idx(self) -> int:
        return index_for(self.position, len(self.events))


@dataclass
class Attack:
    id: str
    name: str
    tier: str
    fn: Callable[[Ctx], tuple[Path, dict | None]]
    positional: bool = True
    variants: tuple[str, ...] = ("",)
    expect_undetectable: bool = False  # boundary control


def _copy(ctx: Ctx) -> Path:
    dst = ctx.work / "log"
    shutil.copytree(ctx.run.logdir, dst)
    return dst


def _mutate(ctx: Ctx, change: Callable[[list[dict], int], None]) -> tuple[Path, None]:
    dst = _copy(ctx)
    records, aux = ctx.adapter.load(dst)
    change(records, ctx.idx)
    ctx.adapter.dump(records, aux, dst)
    return dst, None


# -- T1: naive edits -------------------------------------------------------

def a1_edit_arg(ctx):
    return _mutate(ctx, lambda r, i: ctx.adapter.edit_arg(r[i]))


def a2_flip_verdict(ctx):
    return _mutate(ctx, lambda r, i: ctx.adapter.flip_verdict(r[i]))


def a3_delete(ctx):
    return _mutate(ctx, lambda r, i: r.pop(i))


def a4_truncate(ctx):
    k = int(ctx.variant)

    def cut(r, _i):
        del r[len(r) - k:]

    return _mutate(ctx, cut)


def a5_swap(ctx):
    def swap(r, i):
        j = i + 1 if i + 1 < len(r) else i - 1
        r[i], r[j] = r[j], r[i]

    return _mutate(ctx, swap)


def a6_insert(ctx):
    def ins(r, i):
        forged = copy.deepcopy(r[i])
        ctx.adapter.edit_arg(forged)
        try:
            ctx.adapter.fresh_identity(forged)
        except NotApplicable:
            pass
        r.insert(i + 1, forged)

    return _mutate(ctx, ins)


def a7_replay(ctx):
    return _mutate(ctx, lambda r, i: r.insert(i + 1, copy.deepcopy(r[i])))


def a8_backdate(ctx):
    return _mutate(ctx, lambda r, i: ctx.adapter.backdate(r[i]))


def a10_downgrade(ctx):
    return _mutate(ctx, lambda r, i: ctx.adapter.strip_integrity(r[i]))


# -- T1+ / T2: rebuild with the tool's own recorder --------------------------

def _edited_events(ctx: Ctx) -> list[dict]:
    ev = copy.deepcopy(ctx.events)
    i = ctx.idx
    if ctx.variant == "edit":
        ev[i]["args"]["_edited"] = 1
    elif ctx.variant == "delete":
        ev.pop(i)
    else:
        raise ValueError(ctx.variant)
    return ev


def a11_public_reseal(ctx):
    dst = ctx.work / "log"
    ctx.adapter.record(_edited_events(ctx), dst, strong=False, secrets=None)
    return dst, None


def a12_operator_rewrite(ctx):
    dst = ctx.work / "log"
    ctx.adapter.record(_edited_events(ctx), dst, strong=False, secrets=ctx.run.secrets or None)
    return dst, None


def a13_fork(ctx):
    """Same prefix, different suffix, signed with the real keys."""
    i = ctx.idx
    n = len(ctx.events)
    alt = generate(n, seed=10_007)[i:]
    ev = copy.deepcopy(ctx.events[:i]) + alt
    for k, e in enumerate(ev):
        e["i"] = k
        e["ts"] = ctx.events[k]["ts"]
    dst = ctx.work / "log"
    ctx.adapter.record(ev, dst, strong=False, secrets=ctx.run.secrets or None)
    return dst, None


# -- boundary: capture omission ---------------------------------------------

def a14_omission(ctx):
    """The action never reached the recorder. The log is recorded honestly
    from the remaining events, and the verifier's external state is taken
    from that log - there is nothing for any hash to disagree with."""
    ev = copy.deepcopy(ctx.events)
    ev.pop(ctx.idx)
    dst = ctx.work / "log"
    strong = bool(ctx.run.external.get("_strong"))
    run2 = ctx.adapter.record(ev, dst, strong=strong, secrets=None)
    return dst, run2.external


ATTACKS: list[Attack] = [
    Attack("A1", "edit a tool argument", "T1", a1_edit_arg),
    Attack("A2", "flip a policy verdict", "T1", a2_flip_verdict),
    Attack("A3", "delete one record", "T1", a3_delete),
    Attack("A4", "truncate the tail", "T1", a4_truncate, positional=False, variants=("1", "10")),
    Attack("A5", "swap two adjacent records", "T1", a5_swap),
    Attack("A6", "insert a forged record", "T1", a6_insert),
    Attack("A7", "replay a duplicate record", "T1", a7_replay),
    Attack("A8", "backdate a timestamp", "T1", a8_backdate),
    Attack("A10", "strip integrity fields (downgrade)", "T1", a10_downgrade),
    Attack("A11", "rebuild without the original keys", "T1+", a11_public_reseal, variants=("edit", "delete")),
    Attack("A12", "operator rewrite with real keys", "T2", a12_operator_rewrite, variants=("edit", "delete")),
    Attack("A13", "fork: same prefix, different suffix", "T3", a13_fork),
    Attack("A14", "capture omission (boundary control)", "boundary", a14_omission,
           expect_undetectable=True),
]


# -- A9: field-coverage sweep -------------------------------------------------

def leaf_paths(node, prefix=()):
    """Yield every leaf path in a JSON-like record."""
    if isinstance(node, dict):
        for k, v in node.items():
            yield from leaf_paths(v, prefix + (k,))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from leaf_paths(v, prefix + (i,))
    else:
        yield prefix


def _get(node, path):
    for p in path:
        node = node[p]
    return node


def _set(node, path, value):
    for p in path[:-1]:
        node = node[p]
    node[path[-1]] = value


def perturb(value):
    """Smallest type-preserving change to one stored value."""
    if isinstance(value, bool):
        return not value
    if isinstance(value, int):
        return value + 1
    if isinstance(value, float):
        return value + 1.0
    if isinstance(value, str):
        if not value:
            return "x"
        # Change a middle character, not the last one: the final character of
        # a base64 string carries padding bits, so changing it can decode to
        # the same bytes and would look like a miss when nothing changed.
        k = len(value) // 2
        swap = "0" if value[k] != "0" else "1"
        return value[:k] + swap + value[k + 1:]
    if value is None:
        return "x"
    return value


def coverage_sweep(adapter: Adapter, run: Run, work: Path, position: str = "middle"):
    """A9: change each stored field of one record, one at a time.

    Returns a list of (path, new_logdir). A field whose change the verifier
    accepts is outside the tool's integrity coverage.
    """
    records, _aux = adapter.load(run.logdir)
    i = index_for(position, len(records))
    out = []
    for n, path in enumerate(leaf_paths(records[i])):
        dst = work / f"f{n:03d}" / "log"
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(run.logdir, dst)
        recs, aux = adapter.load(dst)
        _set(recs[i], path, perturb(_get(recs[i], path)))
        adapter.dump(recs, aux, dst)
        out.append((".".join(str(p) for p in path), dst))
    return out
