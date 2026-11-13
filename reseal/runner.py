"""Run the attack matrix: tools x setups x seeds x attacks x positions."""

from __future__ import annotations

import csv
import json
import shutil
import tempfile
import time
from importlib import metadata
from pathlib import Path

from . import adapters, checkpoint
from .adapters import ACCEPTED, ERROR, NotApplicable, Verdict
from .attacks import ATTACKS, POSITIONS, Ctx, coverage_sweep
from .controls import CONTROLS
from .workload import generate

FIELDS = ["tool", "version", "setup", "seed", "n", "kind", "id", "name", "tier",
          "variant", "position", "applicable", "status", "detected", "detail"]


def _version(adapter) -> str:
    if getattr(adapter, "withheld", False) or not adapter.package:
        return ""
    try:
        return metadata.version(adapter.package)
    except metadata.PackageNotFoundError:
        return "unknown"


def _unchanged(adapter, original, presented) -> bool:
    """True if the tampered log holds exactly the records of the original."""
    try:
        return adapter.load(presented)[0] == adapter.load(original)[0]
    except Exception:
        return False


def _safe_verify(adapter, logdir, external, strong) -> Verdict:
    try:
        return adapter.verify(logdir, external, strong=strong)
    except Exception as exc:  # a crashing verifier is its own finding
        return Verdict(ERROR, f"{type(exc).__name__}: {exc}"[:200])


def run_matrix(tools=None, seeds=(0,), n=200, setups=("default", "strong"),
               positions=POSITIONS, out_dir="results/run", keep=False, log=print):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []
    baselines: list[dict] = []
    tools = tools or [c.name for c in adapters.ALL]
    t0 = time.time()

    for tool in tools:
        adapter = adapters.get(tool)
        version = _version(adapter)
        base_adapter = adapter
        for setup in setups:
            strong = setup == "strong"
            # sprint work: the checkpoint setups wrap the tool's default verifier
            adapter = checkpoint.wrap(base_adapter, setup) if setup in checkpoint.SETUPS else base_adapter
            for seed in seeds:
                events = generate(n, seed)
                root = Path(tempfile.mkdtemp(prefix=f"reseal_{tool}_{setup}_{seed}_"))
                run = adapter.record(events, root / "orig" / "log", strong=strong)
                run.external["_strong"] = strong
                base = dict(tool=tool, version=version, setup=setup, seed=seed, n=n)

                # 0. Sanity: the untouched log must verify.
                v = _safe_verify(adapter, run.logdir, run.external, strong)
                hide = getattr(adapter, "withheld", False)  # keep an unnamed tool unnamed
                baselines.append({**base, "status": v.status, "detail": "" if hide else v.detail[:200]})
                if v.status != ACCEPTED:
                    log(f"!! {tool}/{setup}/seed{seed}: clean log not accepted ({v.status}); skipping")
                    continue

                def add(kind, id_, name, tier, variant, position, verdict, applicable=True):
                    rows.append({**base, "kind": kind, "id": id_, "name": name, "tier": tier,
                                 "variant": variant, "position": position, "applicable": applicable,
                                 "status": verdict.status if verdict else "",
                                 "detected": verdict.detected if verdict else "",
                                 "detail": "" if hide else (verdict.detail if verdict else "")[:200]})

                # 1. Attacks.
                trial = 0
                for atk in ATTACKS:
                    for variant in atk.variants:
                        for pos in (positions if atk.positional else ("-",)):
                            trial += 1
                            work = root / f"t{trial:04d}"
                            work.mkdir()
                            ctx = Ctx(adapter, events, run, work,
                                      position=pos if atk.positional else "middle", variant=variant)
                            try:
                                presented, ext = atk.fn(ctx)
                            except NotApplicable:
                                add("attack", atk.id, atk.name, atk.tier, variant, pos, None, False)
                                continue
                            # sprint fix: an attack that leaves the log unchanged is not an
                            # attack (e.g. stripping a proof from a record that has none)
                            if _unchanged(adapter, run.logdir, presented):
                                add("attack", atk.id, atk.name, atk.tier, variant, pos, None, False)
                                continue
                            verdict = _safe_verify(adapter, presented, ext or run.external, strong)
                            add("attack", atk.id, atk.name, atk.tier, variant, pos, verdict)

                # 2. A9 field-coverage sweep (one record, every stored field).
                sweep = root / "sweep"
                sweep.mkdir()
                for path, presented in coverage_sweep(adapter, run, sweep, "middle"):
                    verdict = _safe_verify(adapter, presented, run.external, strong)
                    add("coverage", "A9", "change one stored field", "T1", path, "middle", verdict)

                # 3. Benign controls.
                for ctl in CONTROLS:
                    work = root / f"c_{ctl.id}"
                    work.mkdir()
                    try:
                        presented = ctl.fn(adapter, run, work)
                    except NotApplicable:
                        add("control", ctl.id, ctl.name, "benign", "", "-", None, False)
                        continue
                    verdict = _safe_verify(adapter, presented, run.external, strong)
                    add("control", ctl.id, ctl.name, "benign", "", "-", verdict)

                if not keep:
                    shutil.rmtree(root, ignore_errors=True)
                log(f"{tool:16s} {setup:8s} seed={seed} done ({time.time() - t0:.0f}s)")

    with open(out / "trials.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    meta = {
        "n_events": n, "seeds": list(seeds), "setups": list(setups), "positions": list(positions),
        "tools": {t: {"version": _version(adapters.get(t)),
                      "default_setup": adapters.get(t).default_setup,
                      "strong_setup": adapters.get(t).strong_setup} for t in tools},
        "setup_notes": {s: checkpoint.describe(s) for s in setups if s in checkpoint.SETUPS},
        "baselines": baselines, "trials": len(rows),
    }
    (out / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return rows, meta
