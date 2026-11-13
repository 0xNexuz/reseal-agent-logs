"""Recompute every number quoted in the report from the trial files.

Sprint work (13 Nov 2026 onward).

    python -m reseal.numbers            # writes results/main/REPORT_NUMBERS.md
"""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

MAIN, ROBUST = Path("results/main"), Path("results/robust_n100")
NAMED = ["halo-record", "witnesskit", "signet", "agent-receipts"]
GROUPS = {  # report column -> repository labels
    "Claim holds": {"holds", "holds with setup", "holds without the setup", "holds (headline only)"},
    "Disclosed limit": {"disclosed limit", "needs setup (disclosed)", "setup left to the user (disclosed)"},
    "Caught, not claimed": {"caught (unstated)", "better than stated"},
    "Silent miss": {"silent miss"},
    "Claim not met": {"claim not met", "headline not met"},
}


def trials(run):
    with open(run / "trials.csv", newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def cells(rows):
    """One cell = tool x setup x test x variant x position; value = set of outcomes over seeds."""
    out = defaultdict(set)
    for r in rows:
        pos = "" if r["kind"] == "coverage" else r["position"]
        out[(r["tool"], r["setup"], r["kind"], r["id"], r["variant"], pos)].add(
            (r["applicable"], r["detected"]))
    return out


def rate(rows, **want):
    sel = [r for r in rows if r["applicable"] == "True" and all(r[k] in (v if isinstance(v, (set, tuple)) else (v,)) for k, v in want.items())]
    return f"{sum(r['detected'] == 'True' for r in sel)}/{len(sel)}"


def main():
    rows, rob = trials(MAIN), trials(ROBUST)
    meta = json.loads((MAIN / "meta.json").read_text())
    tools = list(meta["tools"])
    L = ["# Numbers quoted in the report\n",
         "Recomputed from `results/main/trials.csv`, `results/robust_n100/trials.csv` and "
         "`results/main/labels.csv` by `python -m reseal.numbers`.\n"]
    add = L.append

    add("## Run size and checks\n")
    add(f"- Main run trials: {len(rows)} ({meta['n_events']} events per log, seeds {meta['seeds']})")
    add(f"- Robustness run trials: {len(rob)}")
    add(f"- Clean logs accepted before attacks: {sum(b['status'] == 'accepted' for b in meta['baselines'])}"
        f"/{len(meta['baselines'])}")
    c_main, c_rob = cells(rows), cells(rob)
    add(f"- Cells in the main run: {len(c_main)}; cells whose outcome differs between seeds: "
        f"{sum(len(v) > 1 for v in c_main.values())}")
    shared = set(c_main) & set(c_rob)
    add(f"- Cells shared by the two runs: {len(shared)}; with a different outcome: "
        f"{sum(c_main[k] != c_rob[k] for k in shared)}")
    ctl = [r for r in rows if r["kind"] == "control" and r["applicable"] == "True"]
    add(f"- Benign controls flagged: {sum(r['detected'] == 'True' for r in ctl)}/{len(ctl)}\n")

    add("## Detection counts (refused / shown)\n")
    add("| Test | Setup | " + " | ".join(tools) + " |")
    add("| --- | --- |" + " --- |" * len(tools))
    tests = [("A1, A2, A5-A8 each, lowest", dict(id={"A1", "A2", "A5", "A6", "A7", "A8"})),
             ("A3 not the final record", dict(id="A3", position={"first", "middle", "penultimate"})),
             ("A3 final record", dict(id="A3", position="final")),
             ("A4 truncate", dict(id="A4")), ("A10 strip", dict(id="A10")),
             ("A10 strip, first record", dict(id="A10", position="first")),
             ("A11 rebuild, no keys", dict(id="A11")), ("A12 operator rewrite", dict(id="A12")),
             ("A13 fork", dict(id="A13")), ("A14 omission", dict(id="A14")), ("A9 field sweep", dict(id="A9"))]
    for name, want in tests:
        for setup in meta["setups"]:
            vals = []
            for t in tools:
                if name.startswith("A1, A2"):
                    per = [rate(rows, tool=t, setup=setup, id=i) for i in sorted(want["id"])]
                    vals.append(min(per, key=lambda s: int(s.split("/")[0])))
                else:
                    vals.append(rate(rows, tool=t, setup=setup, **want))
            add(f"| {name} | {setup} | " + " | ".join(vals) + " |")

    add("\n## Fields whose change was accepted (A9, default setup)\n")
    for t in tools:
        sel = [r for r in rows if r["tool"] == t and r["id"] == "A9" and r["setup"] == "default"]
        fields = sorted({r["variant"] for r in sel})
        acc = sorted({r["variant"] for r in sel if r["detected"] != "True"})
        add(f"- {t}: {len(fields)} stored fields; accepted: {', '.join(acc) or 'none'}")

    add("\n## Claims versus behaviour (Table 2), default / strong\n")
    with open(MAIN / "labels.csv", newline="", encoding="utf-8") as fh:
        labels = list(csv.DictReader(fh))
    add("| Tool | " + " | ".join(GROUPS) + " |")
    add("| --- |" + " --- |" * len(GROUPS))
    for t in tools:
        cellsout = []
        for g, members in GROUPS.items():
            n = [sum(r["tool"] == t and r["setup"] == s and r["label"] in members for r in labels)
                 for s in ("default", "strong")]
            cellsout.append(f"{n[0]} / {n[1]}")
        add(f"| {t} | " + " | ".join(cellsout) + " |")
    miss = [r for r in labels if r["tool"] in NAMED and r["setup"] == "default" and r["outcome"] != "caught"]
    kinds = Counter("disclosed" if r["label"] in GROUPS["Disclosed limit"] else r["label"] for r in miss)
    add(f"\n- Default-setup misses of the four named tools: {len(miss)} = {dict(kinds)}")
    silent = sorted((r["property"], r["tool"]) for r in miss if r["label"] == "silent miss")
    add(f"- Their silent misses: {silent}")
    notmet = sorted((r["tool"], r["property"], r["setup"]) for r in labels if r["label"] in GROUPS["Claim not met"])
    add(f"- Claims not met: {notmet}")

    out = MAIN / "REPORT_NUMBERS.md"
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    print("wrote", out)


if __name__ == "__main__":
    main()
