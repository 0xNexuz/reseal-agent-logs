"""Checks on the outside checkpoint and the unprotected baseline (sprint work)."""

import copy

from reseal import adapters, checkpoint
from reseal.workload import generate


def records(n=30):
    return [dict(e) for e in generate(n, seed=3)]


def test_same_log_passes_and_a_log_that_only_grew_passes():
    recs = records()
    cp = checkpoint.take(recs, 20)
    assert checkpoint.check(recs, cp)[0]
    assert checkpoint.check(recs[:20], cp)[0]
    assert checkpoint.check(recs + records(5), cp)[0]


def test_any_change_before_the_checkpoint_is_refused():
    recs = records()
    cp = checkpoint.take(recs)
    edited = copy.deepcopy(recs)
    edited[7]["verdict"] = "changed"
    swapped = recs[:3] + [recs[4], recs[3]] + recs[5:]
    for bad in (edited, recs[:-1], recs[:5] + recs[6:], swapped, recs[:9] + [recs[9]] + recs[9:]):
        assert not checkpoint.check(bad, cp)[0]


def test_changes_after_a_stale_checkpoint_are_not_seen():
    recs = records()
    cp = checkpoint.take(recs, 20)
    tail_edit = copy.deepcopy(recs)
    tail_edit[25]["verdict"] = "changed"
    assert checkpoint.check(tail_edit, cp)[0]      # the stated limit
    assert checkpoint.check(recs[:22], cp)[0]      # truncation inside the uncovered tail
    assert not checkpoint.check(recs[:19], cp)[0]  # truncation below the checkpoint


def test_key_order_and_spacing_do_not_matter():
    recs = records()
    cp = checkpoint.take(recs)
    reordered = [dict(reversed(list(r.items()))) for r in recs]
    assert checkpoint.check(reordered, cp)[0]


def test_baseline_accepts_tampering_and_the_wrapper_refuses_it(tmp_path):
    plain = adapters.get("plain-jsonl")
    events = generate(20, seed=1)
    wrapped = checkpoint.wrap(plain, "checkpoint")
    run = wrapped.record(events, tmp_path / "log", strong=False)
    assert wrapped.verify(run.logdir, run.external, strong=False).status == adapters.ACCEPTED
    recs, aux = plain.load(run.logdir)
    plain.flip_verdict(recs[4])
    plain.dump(recs, aux, run.logdir)
    assert plain.verify(run.logdir, {}, strong=False).status == adapters.ACCEPTED
    assert wrapped.verify(run.logdir, run.external, strong=False).status == adapters.REJECTED
