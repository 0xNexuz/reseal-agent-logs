"""Recompute every number quoted in the report from the trial files.

Sprint work (13 Nov 2026 onward).

    python -m reseal.numbers     # writes results/REPORT_NUMBERS.md and results/APPENDIX_C.md
"""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

from . import agreement
from .analyze import build, cards, load_claims, strict_violations
from .attacks import ATTACKS
from .figure import ROWS

MAIN, ROBUST, LAYER = Path("results/main"), Path("results/robust_n100"), Path("results/layer")
C1, C2 = Path("claims/claims_coder1.csv"), Path("claims/claims_coder2.csv")
NAMED = ["halo-record", "witnesskit", "signet", "agent-receipts"]
GROUPS = {  # report column -> repository labels
    "Claim holds": {"holds", "holds with setup", "holds without the setup", "holds (headline only)"},
    "Disclosed limit": {"disclosed limit", "needs setup (disclosed)", "setup left to the user (disclosed)"},
    "Caught, not claimed": {"caught (unstated)", "better than stated"},
    "Silent miss": {"silent miss"},
    "Claim not met": {"claim not met", "headline not met"},
}


def group(label: str) -> str:
    return next((g for g, members in GROUPS.items() if label in members), label)


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
    sel = [r for r in rows if r["applicable"] == "True"
           and all(r[k] in (v if isinstance(v, (set, tuple)) else (v,)) for k, v in want.items())]
    return f"{sum(r['detected'] == 'True' for r in sel)}/{len(sel)}"


TESTS = [("A1, A2, A5-A8 each, lowest", dict(id={"A1", "A2", "A5", "A6", "A7", "A8"})),
         ("A3 not the final record", dict(id="A3", position={"first", "middle", "penultimate"})),
         ("A3 final record", dict(id="A3", position="final")),
         ("A4 truncate", dict(id="A4")), ("A10 strip", dict(id="A10")),
         ("A10 strip, first record", dict(id="A10", position="first")),
         ("A11 rebuild, no keys", dict(id="A11")), ("A12 operator rewrite", dict(id="A12")),
         ("A13 fork", dict(id="A13")), ("A14 omission", dict(id="A14")), ("A9 field sweep", dict(id="A9"))]


def detection_table(rows, tools, setups, add):
    add("| Test | Setup | " + " | ".join(tools) + " |")
    add("| --- | --- |" + " --- |" * len(tools))
    for name, want in TESTS:
        for setup in setups:
            vals = []
            for t in tools:
                if name.startswith("A1, A2"):
                    per = [rate(rows, tool=t, setup=setup, id=i) for i in sorted(want["id"])]
                    vals.append(min(per, key=lambda s: int(s.split("/")[0])))
                else:
                    vals.append(rate(rows, tool=t, setup=setup, **want))
            add(f"| {name} | {setup} | " + " | ".join(vals) + " |")


def run_checks(rows, meta, add, name):
    c = cells(rows)
    ctl = [r for r in rows if r["kind"] == "control" and r["applicable"] == "True"]
    add(f"- {name}: {len(rows)} trials; {len(c)} cells; cells whose outcome differs between seeds: "
        f"{sum(len(v) > 1 for v in c.values())}; clean logs accepted "
        f"{sum(b['status'] == 'accepted' for b in meta['baselines'])}/{len(meta['baselines'])}; "
        f"benign controls flagged {sum(r['detected'] == 'True' for r in ctl)}/{len(ctl)}; "
        f"control rows that do not apply: {sum(r['kind'] == 'control' and r['applicable'] != 'True' for r in rows)}")
    return c


def numbers() -> str:
    rows, rob, lay = trials(MAIN), trials(ROBUST), trials(LAYER)
    meta = json.loads((MAIN / "meta.json").read_text())
    lmeta = json.loads((LAYER / "meta.json").read_text())
    rmeta = json.loads((ROBUST / "meta.json").read_text())
    tools = list(meta["tools"])
    L = ["# Numbers quoted in the report\n",
         "Recomputed from the trial files in `results/main`, `results/robust_n100` and "
         "`results/layer`, and from the two claims sheets, by `python -m reseal.numbers`.\n"]
    add = L.append

    add("## Run size and checks\n")
    c_main = run_checks(rows, meta, add, "Main run (default, strong; 1,000 events; seeds 0-4)")
    c_rob = run_checks(rob, rmeta, add, "Robustness run (default, strong; 100 events; seeds 5-9)")
    run_checks(lay, lmeta, add, "Checkpoint run (checkpoint, checkpoint-stale, baseline default; 1,000 events; seeds 0-4)")
    shared = set(c_main) & set(c_rob)
    add(f"- Cells shared by the main and robustness runs: {len(shared)}; with a different outcome: "
        f"{sum(c_main[k] != c_rob[k] for k in shared)}\n")

    add("## Detection counts, main run (refused / shown)\n")
    detection_table(rows, tools, meta["setups"], add)

    add("\n## Detection counts, checkpoint run (refused / shown)\n")
    ltools = list(lmeta["tools"])
    detection_table(lay, ltools, [s for s in lmeta["setups"]], add)
    for setup in ("checkpoint", "checkpoint-stale"):
        sel = [r for r in lay if r["setup"] == setup and r["kind"] in ("attack", "coverage")
               and r["applicable"] == "True" and r["id"] != "A14"]
        miss = [r for r in sel if r["detected"] != "True"]
        add(f"\n- `{setup}`, all tools, every attack except the control: "
            f"{len(sel) - len(miss)}/{len(sel)} refused")
        if miss:
            where = Counter((r["id"], r["variant"] if r["id"] in ("A4", "A11", "A12") else "", r["position"])
                            for r in miss)
            tools_by = defaultdict(set)
            for r in miss:
                tools_by[(r["id"], r["variant"] if r["id"] in ("A4", "A11", "A12") else "", r["position"])].add(r["tool"])
            for k in sorted(where):
                add(f"  - accepted: {k[0]} {k[1]} at {k[2]}: {where[k]} trials, tools {sorted(tools_by[k])}")
            early = [r for r in miss if r["position"] in ("first", "middle")]
            add(f"  - accepted at the first or middle record: {len(early)}")

    add("\n## Fields whose change was accepted (A9, default setup)\n")
    for t in tools:
        sel = [r for r in rows if r["tool"] == t and r["id"] == "A9" and r["setup"] == "default"]
        fields = sorted({r["variant"] for r in sel})
        acc = sorted({r["variant"] for r in sel if r["detected"] != "True"})
        add(f"- {t}: {len(fields)} stored fields; accepted: {', '.join(acc) or 'none'}")

    add("\n## Agreement between the two claim codings\n")
    res = agreement.compare(C1, C2)
    add(f"- Cells: {res['cells']}; agreeing: {round(res['raw_agreement'] * res['cells'])}; "
        f"raw agreement {res['raw_agreement']}; Cohen's kappa {res['cohens_kappa']}")
    add(f"- Agreement by tool: {res['agreement_by_tool']}")

    add("\n## Claims versus behaviour, by coder (default / strong)\n")
    tables = {}
    for coder, path in (("coder 1", C1), ("coder 2", C2)):
        table, _, raw = build(MAIN, path)
        tables[coder] = table
        add(f"\n{coder}:\n")
        add("| Tool | " + " | ".join(GROUPS) + " |")
        add("| --- |" + " --- |" * len(GROUPS))
        for t in tools:
            out = []
            for g in GROUPS:
                n = [sum(r["tool"] == t and r["setup"] == s and group(r["label"]) == g for r in table)
                     for s in ("default", "strong")]
                out.append(f"{n[0]} / {n[1]}")
            add(f"| {t} | " + " | ".join(out) + " |")
        miss = [r for r in table if r["tool"] in NAMED and r["setup"] == "default" and r["outcome"] != "caught"]
        add(f"\n- Default-setup misses of the four named tools: {len(miss)} = "
            f"{dict(Counter(group(r['label']) for r in miss))}")
        add(f"- Their silent misses: {sorted((r['property'], r['tool']) for r in miss if group(r['label']) == 'Silent miss')}")
        add(f"- Claims not met: {sorted((r['tool'], r['property'], r['setup']) for r in table if group(r['label']) == 'Claim not met')}")
        strict = strict_violations(raw, load_claims(path), tools, meta["setups"])
        add(f"- Strict reading, claims not met: {[(t, p, s, f'{d}/{n}') for t, p, s, d, n in strict]}")
    a = {(r["tool"], r["property"], r["setup"]): group(r["label"]) for r in tables["coder 1"]}
    b = {(r["tool"], r["property"], r["setup"]): group(r["label"]) for r in tables["coder 2"]}
    diff = sorted(k for k in a if a[k] != b[k])
    add(f"\n- Label cells that differ between coders: {len(diff)} of {len(a)}; of these, cells where "
        f"one coder says the tampering was missed and the labels differ: "
        f"{sum(1 for k in diff if {a[k], b[k]} & {'Disclosed limit', 'Silent miss', 'Claim not met'})}")
    return "\n".join(L) + "\n", res, tables


def appendix_c(res, tables) -> str:
    table1, meta, _ = build(MAIN, C1)
    L = ["## Appendix C: Attacks, Claims Cards and coder disagreements\n",
         "**Attacks and Figure 1.** Figure 1 pools the fourteen attacks into ten rows.\n",
         "| ID | Attack | Attacker | Row in Figure 1 |", "| --- | --- | --- | --- |"]
    row_of = {}
    for label, ids, pos in ROWS:
        for i in ids:
            row_of.setdefault(i, []).append(label)
    tier = {"T1": "outside editor", "T1+": "re-sealer (no keys)", "T2": "operator (real keys)",
            "T3": "forking operator", "boundary": "control"}
    for atk in ATTACKS[:8]:
        L.append(f"| {atk.id} | {atk.name} | {tier[atk.tier]} | {'; '.join(row_of[atk.id])} |")
    L.append(f"| A9 | change each stored field of one record, one at a time | outside editor | {row_of['A9'][0]} |")
    for atk in ATTACKS[8:]:
        L.append(f"| {atk.id} | {atk.name} | {tier[atk.tier]} | {'; '.join(row_of[atk.id])} |")
    L.append("\n**Claims Cards (coder 1).** Counts are tampered logs refused / shown, default and strong "
             "setup. The verdict column gives the repository's finer label for default / strong.\n")
    body = cards(table1, meta, load_claims(C1))
    body = body.split("\n## ", 1)[1]
    L.append("### " + body.replace("\n## ", "\n### "))
    L.append("\n**Where coder 2 differs.** Governing statement per tool and kind of tampering "
             f"({res['cells']} cells, {len(res['disagreements'])} differ, Cohen's kappa {res['cohens_kappa']}). "
             "The last two columns give the default-setup label under each coding.\n")
    L.append("| Tool | Tampering | Coder 1 reads | Coder 2 reads | Label, coder 1 | Label, coder 2 |")
    L.append("| --- | --- | --- | --- | --- | --- |")
    lab = {c: {(r["tool"], r["property"]): group(r["label"]) for r in t if r["setup"] == "default"}
           for c, t in tables.items()}
    for d in res["disagreements"]:
        k = (d["tool"], d["property"])
        L.append(f"| {d['tool']} | {d['property']} | {d['coder1'].replace('_', ' ')} | "
                 f"{d['coder2'].replace('_', ' ')} | {lab['coder 1'][k]} | {lab['coder 2'][k]} |")
    return "\n".join(L) + "\n"


def main():
    text, res, tables = numbers()
    Path("results/REPORT_NUMBERS.md").write_text(text, encoding="utf-8")
    Path("results/APPENDIX_C.md").write_text(appendix_c(res, tables), encoding="utf-8")
    Path("claims/agreement.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
    print("wrote results/REPORT_NUMBERS.md, results/APPENDIX_C.md, claims/agreement.json")


if __name__ == "__main__":
    main()
