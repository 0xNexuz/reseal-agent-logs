"""Checks on ReSeal itself. These tests assert properties of the harness,
never findings about a tool: a tool being fixed must not break them."""

import filecmp
import json

import pytest

from reseal import adapters
from reseal.adapters import ACCEPTED, NotApplicable
from reseal.attacks import ATTACKS, Ctx, coverage_sweep, index_for, leaf_paths, perturb
from reseal.controls import CONTROLS
from reseal.runner import run_matrix
from reseal.workload import generate

TOOLS = [c.name for c in adapters.ALL]
N = 24


def test_workload_is_deterministic():
    assert generate(50, 3) == generate(50, 3)
    assert generate(50, 3) != generate(50, 4)
    ev = generate(200, 0)
    assert [e["i"] for e in ev] == list(range(200))
    assert all(a["ts"] < b["ts"] for a, b in zip(ev, ev[1:]))  # strictly increasing
    assert {e["verdict"] for e in ev} == {"allowed", "blocked"}


def test_positions():
    assert [index_for(p, 10) for p in ("first", "middle", "penultimate", "final")] == [0, 5, 8, 9]


def test_perturb_always_changes_the_value():
    for v in ["", "a", "abcdef", "0000", 0, 7, True, False, None, 1.5]:
        assert perturb(v) != v


def test_leaf_paths():
    rec = {"a": 1, "b": {"c": [1, {"d": 2}]}}
    assert list(leaf_paths(rec)) == [("a",), ("b", "c", 0), ("b", "c", 1, "d")]


@pytest.mark.parametrize("tool", TOOLS)
@pytest.mark.parametrize("strong", [False, True])
def test_clean_log_is_accepted_and_one_record_per_event(tool, strong, tmp_path):
    a = adapters.get(tool)
    events = generate(N, 1)
    run = a.record(events, tmp_path / "log", strong=strong)
    assert a.verify(run.logdir, run.external, strong=strong).status == ACCEPTED
    records, _ = a.load(run.logdir)
    assert len(records) == len(events)


@pytest.mark.parametrize("tool", TOOLS)
@pytest.mark.parametrize("strong", [False, True])
def test_controls_never_raise_false_alarms_from_the_harness(tool, strong, tmp_path):
    """C0 (load and re-save) must pass, or every 'detected' would be suspect."""
    a = adapters.get(tool)
    run = a.record(generate(N, 1), tmp_path / "orig" / "log", strong=strong)
    c0 = next(c for c in CONTROLS if c.id == "C0")
    work = tmp_path / "c0"
    work.mkdir()
    presented = c0.fn(a, run, work)
    assert a.verify(presented, run.external, strong=strong).status == ACCEPTED


@pytest.mark.parametrize("tool", TOOLS)
def test_every_attack_really_changes_the_log(tool, tmp_path):
    """An attack that leaves the bytes untouched would be scored as a miss."""
    a = adapters.get(tool)
    events = generate(N, 1)
    run = a.record(events, tmp_path / "orig" / "log", strong=False)
    orig = a.log_file(run.logdir)
    for k, atk in enumerate(ATTACKS):
        for variant in atk.variants:
            work = tmp_path / f"t{k}{variant}"
            work.mkdir()
            ctx = Ctx(a, events, run, work, position="middle", variant=variant)
            try:
                presented, _ = atk.fn(ctx)
            except NotApplicable:
                continue
            assert not filecmp.cmp(orig, a.log_file(presented), shallow=False), atk.id


@pytest.mark.parametrize("tool", TOOLS)
def test_runner_does_not_score_an_attack_that_changed_nothing(tool, tmp_path):
    """Sprint fix: at some positions an attack can be a no-op for a tool (its
    first record may have no integrity field to strip). Such a trial must be
    recorded as not applicable, never as a miss."""
    from reseal.runner import run_matrix

    rows, _ = run_matrix(tools=[tool], seeds=(1,), n=N, setups=("default",),
                         out_dir=tmp_path / "out", log=lambda *_: None)
    a = adapters.get(tool)
    run = a.record(generate(N, 1), tmp_path / "orig" / "log", strong=False)
    original, _ = a.load(run.logdir)
    for k, atk in enumerate(ATTACKS):
        if not atk.positional or atk.id in ("A11", "A12", "A13", "A14"):
            continue
        for pos in ("first", "middle", "penultimate", "final"):
            work = tmp_path / f"p{k}{pos}"
            work.mkdir()
            try:
                presented, _ = atk.fn(Ctx(a, generate(N, 1), run, work, position=pos))
            except NotApplicable:
                continue
            noop = a.load(presented)[0] == original
            scored = [r for r in rows if r["id"] == atk.id and r["position"] == pos]
            assert all(r["applicable"] is (not noop) for r in scored), (atk.id, pos)


@pytest.mark.parametrize("tool", TOOLS)
def test_attacks_do_not_touch_the_original_or_external_state(tool, tmp_path):
    a = adapters.get(tool)
    events = generate(N, 1)
    run = a.record(events, tmp_path / "orig" / "log", strong=True)
    before = a.log_file(run.logdir).read_bytes()
    ext_before = json.dumps(run.external, sort_keys=True)
    for k, atk in enumerate(ATTACKS):
        work = tmp_path / f"t{k}"
        work.mkdir()
        ctx = Ctx(a, events, run, work, position="middle", variant=atk.variants[0])
        try:
            atk.fn(ctx)
        except NotApplicable:
            pass
    assert a.log_file(run.logdir).read_bytes() == before
    assert json.dumps(run.external, sort_keys=True) == ext_before
    assert a.verify(run.logdir, run.external, strong=True).status == ACCEPTED


@pytest.mark.parametrize("tool", TOOLS)
def test_coverage_sweep_changes_exactly_one_field(tool, tmp_path):
    a = adapters.get(tool)
    run = a.record(generate(N, 1), tmp_path / "orig" / "log", strong=False)
    orig, _ = a.load(run.logdir)
    sweep = tmp_path / "sweep"
    sweep.mkdir()
    trials = coverage_sweep(a, run, sweep, "middle")
    assert trials
    i = index_for("middle", N)
    for _path, presented in trials:
        recs, _ = a.load(presented)
        assert [k for k, (x, y) in enumerate(zip(orig, recs)) if x != y] == [i]
        diff = [p for p in leaf_paths(orig[i])
                if _get(orig[i], p) != _get(recs[i], p)]
        assert len(diff) == 1


def _get(node, path):
    for p in path:
        node = node[p]
    return node


def test_run_matrix_is_reproducible(tmp_path):
    """Same inputs give the same verdicts (ids and signatures differ, verdicts must not)."""
    key = lambda r: (r["tool"], r["setup"], r["kind"], r["id"], r["variant"], r["position"],
                     r["applicable"], r["status"])
    a, _ = run_matrix(tools=["halo-record", "witnesskit"], n=N, out_dir=tmp_path / "a", log=lambda *_: None)
    b, _ = run_matrix(tools=["halo-record", "witnesskit"], n=N, out_dir=tmp_path / "b", log=lambda *_: None)
    assert [key(r) for r in a] == [key(r) for r in b]
    assert (tmp_path / "a" / "trials.csv").exists()
