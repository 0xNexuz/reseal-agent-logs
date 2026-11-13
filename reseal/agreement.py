"""Agreement between two independent codings of the tools' documentation.

Sprint work (13 Nov 2026 onward).

    python -m reseal.agreement claims/claims_coder1.csv claims/claims_coder2.csv

The unit is one tool x property cell (11 properties per tool). For each cell
the governing statement is picked exactly as the analysis does
(``analyze.claim_for``), giving one of four categories: claims,
claims_with_setup, disclaims, or silent (no statement). Cohen's kappa is
computed on those categories.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from .analyze import PROPERTIES, claim_for, load_claims

CATS = ["claims", "claims_with_setup", "disclaims", "silent"]


def governing(claims, tools):
    out = {}
    for tool in tools:
        for prop, _ids, tier, _pos, _desc in PROPERTIES:
            strength, kind, _row = claim_for(claims, tool, prop, tier)
            # a general slogan is a headline, not a statement about this property
            out[(tool, prop)] = strength if kind != "slogan" else "claims"
    return out


def kappa(a: dict, b: dict) -> tuple[float, float, int]:
    keys = sorted(a)
    n = len(keys)
    agree = sum(a[k] == b[k] for k in keys) / n
    ca, cb = Counter(a.values()), Counter(b.values())
    expected = sum(ca[c] * cb[c] for c in CATS) / (n * n)
    k = 1.0 if expected == 1 else (agree - expected) / (1 - expected)
    return k, agree, n


def compare(path1, path2, tools=None):
    c1, c2 = load_claims(path1), load_claims(path2)
    tools = tools or sorted({t for t, _ in c1} | {t for t, _ in c2})
    g1, g2 = governing(c1, tools), governing(c2, tools)
    k, agree, n = kappa(g1, g2)
    diffs = [{"tool": t, "property": p, "coder1": g1[(t, p)], "coder2": g2[(t, p)]}
             for (t, p) in sorted(g1) if g1[(t, p)] != g2[(t, p)]]
    per_tool = {t: kappa({key: v for key, v in g1.items() if key[0] == t},
                         {key: v for key, v in g2.items() if key[0] == t})[1] for t in tools}
    return {"cells": n, "raw_agreement": round(agree, 3), "cohens_kappa": round(k, 3),
            "agreement_by_tool": {t: round(v, 3) for t, v in per_tool.items()},
            "disagreements": diffs}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("coder1")
    ap.add_argument("coder2")
    ap.add_argument("--out", default="claims/agreement.json")
    a = ap.parse_args(argv)
    res = compare(a.coder1, a.coder2)
    Path(a.out).write_text(json.dumps(res, indent=2), encoding="utf-8")
    print(f"cells {res['cells']}  raw agreement {res['raw_agreement']}  Cohen's kappa {res['cohens_kappa']}")
    for d in res["disagreements"]:
        print(f"  {d['tool']:16s} {d['property']:10s} coder1={d['coder1']:18s} coder2={d['coder2']}")


if __name__ == "__main__":
    main()
