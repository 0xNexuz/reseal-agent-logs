"""Merge runs made one tool at a time into one results folder.

Sprint work (13 Nov 2026 onward).

    python -m reseal.merge results/layer_parts/* --out results/layer
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from . import report


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("parts", nargs="+")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
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
