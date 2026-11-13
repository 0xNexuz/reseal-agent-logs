"""Merge runs made one tool at a time into one results folder.

Sprint work (13 Nov 2026 onward).

    python -m reseal.merge results/layer_parts/* --out results/layer
    python -m reseal.merge results/rerun_parts/main --splice-into results/main

The second form replaces one tool's rows in an existing run with rows from a
re-run of that tool (used once, on 13 Nov, after the no-op fix in the runner).
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from . import report


def splice(part, target):
    part, target = Path(part), Path(target)
    with open(part / "trials.csv", newline="", encoding="utf-8") as fh:
        new = list(csv.DictReader(fh))
    with open(target / "trials.csv", newline="", encoding="utf-8") as fh:
        old = list(csv.DictReader(fh))
    tools = {r["tool"] for r in new}
    setups = {r["setup"] for r in new}
    keep_before, keep_after, seen = [], [], False
    for r in old:
        if r["tool"] in tools and r["setup"] in setups:
            seen = True
        elif seen:
            keep_after.append(r)
        else:
            keep_before.append(r)
    rows = keep_before + new + keep_after
    with open(target / "trials.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(old[0]))
        w.writeheader()
        w.writerows(rows)
    meta = json.loads((target / "meta.json").read_text(encoding="utf-8"))
    pm = json.loads((part / "meta.json").read_text(encoding="utf-8"))
    meta["baselines"] = [b for b in meta["baselines"]
                         if not (b["tool"] in tools and b["setup"] in setups)] + pm["baselines"]
    meta["trials"] = len(rows)
    (target / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print("wrote", report.write(target), f"({len(rows)} trials; replaced {sorted(tools)} in {sorted(setups)})")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("parts", nargs="+")
    ap.add_argument("--out")
    ap.add_argument("--splice-into")
    a = ap.parse_args(argv)
    if a.splice_into:
        for part in a.parts:
            splice(part, a.splice_into)
        return
    rows, meta = [], None
    for part in a.parts:
        with open(Path(part) / "trials.csv", newline="", encoding="utf-8") as fh:
            rows += list(csv.DictReader(fh))
        m = json.loads((Path(part) / "meta.json").read_text(encoding="utf-8"))
        if meta is None:
            meta = m
            continue
        meta["tools"].update(m["tools"])
        meta["setups"] += [s for s in m["setups"] if s not in meta["setups"]]
        meta.setdefault("setup_notes", {}).update(m.get("setup_notes", {}))
        meta["baselines"] += m["baselines"]
    meta["trials"] = len(rows)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "trials.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    (out / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print("wrote", report.write(out), f"({len(rows)} trials)")


if __name__ == "__main__":
    main()
